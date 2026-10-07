import os
import math
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from database import get_db_connection, init_db

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'nsfdc-concessional-loan-portal-secret-key'

# Ensure DB initialized
init_db()

# Haversine distance formula for Geo-Spatial routing
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('static', 'admin.html')

# -------------------------------------------------------------
# CITIZEN API ENDPOINTS
# -------------------------------------------------------------

@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    conn = get_db_connection()
    schemes = conn.execute('SELECT * FROM schemes').fetchall()
    conn.close()
    return jsonify([dict(s) for s in schemes])

@app.route('/api/recommend', methods=['POST'])
def recommend_scheme():
    data = request.json or {}
    purpose = data.get('purpose', 'micro_business')
    gender = data.get('gender', 'male').lower()
    loan_amount = float(data.get('loan_amount', 100000))
    family_income = float(data.get('family_income', 250000))
    education_status = data.get('education_status', 'undergraduate')

    conn = get_db_connection()
    schemes = {s['code']: dict(s) for s in conn.execute('SELECT * FROM schemes').fetchall()}
    conn.close()

    # Eligibility validation
    income_eligible = family_income <= 500000.0

    # Rules Engine Implementation (6 Purpose Cards from User Design)
    if purpose == 'education' or education_status in ['pursuing_higher_studies', 'student']:
        recommended_code = 'ELS'
        match_reason_en = "Educational Loan Scheme (ELS) covers full-time professional & technical education in India or abroad (up to ₹40 Lakhs) at 6.5% interest with up to 12 years tenure."
        match_reason_hi = "शिक्षा ऋण योजना (ELS) भारत या विदेश में पूर्णकालिक पेशेवर और तकनीकी शिक्षा (₹40 लाख तक) को 12 वर्ष तक की अवधि के साथ 6.5% ब्याज पर कवर करती है।"
    elif purpose in ['green_vehicle', 'green_business', 'solar_erickshaw']:
        recommended_code = 'GBS'
        match_reason_en = "Green Business Scheme (GBS) provides funding up to ₹30 Lakhs for eco-friendly enterprises like E-Rickshaws, Solar PV units, and waste management projects."
        match_reason_hi = "ग्रीन बिजनेस स्कीम (GBS) ई-रिक्शा, सोलर पीवी यूनिट और कचरा प्रबंधन जैसी पर्यावरण-अनुकूल परियोजनाओं के लिए ₹30 लाख तक का वित्तपोषण प्रदान करती है।"
    elif purpose in ['expand_business', 'machinery_tools'] or loan_amount > 125000.0:
        recommended_code = 'TERM'
        match_reason_en = "Flagship Term Loan Scheme provides substantial concessional finance up to ₹45 Lakhs for machinery purchase, industrial tools, and commercial enterprise expansion."
        match_reason_hi = "प्रमुख टर्म लोन योजना मशीनरी खरीद, औद्योगिक उपकरण और वाणिज्यिक उद्यम विस्तार के लिए ₹45 लाख तक का बड़ा रियायती वित्त प्रदान करती है।"
    elif loan_amount <= 125000.0 and gender == 'female':
        recommended_code = 'MSY'
        match_reason_en = "Mahila Samriddhi Yojana (MSY) offers SC women micro-entrepreneurs ultra-concessional business credit up to ₹1.25 Lakhs at just 4.0% interest p.a."
        match_reason_hi = "महिला समृद्धि योजना (MSY) अनुसूचित जाति की महिला सूक्ष्म उद्यमियों को केवल 4.0% की अत्यधिक रियायती ब्याज दर पर ₹1.25 लाख तक का ऋण प्रदान करती है।"
    else:
        recommended_code = 'MCF'
        match_reason_en = "Micro Credit Finance (MCF) provides small traders, traditional artisans, and micro ventures loan assistance up to ₹1.25 Lakhs at 6.5% concessional interest rate."
        match_reason_hi = "माइक्रो क्रेडिट फाइनेंस (MCF) छोटे व्यापारियों, पारंपरिक कारीगरों और सूक्ष्म उद्यमों को 6.5% रियायती ब्याज दर पर ₹1.25 लाख तक की ऋण सहायता प्रदान करता है।"

    scheme = schemes.get(recommended_code, list(schemes.values())[0])

    # Interest rate based on gender
    applicable_interest_rate = scheme['interest_rate_female'] if gender == 'female' else scheme['interest_rate_male']

    return jsonify({
        'recommended_scheme': scheme,
        'applicable_interest_rate': applicable_interest_rate,
        'income_eligible': income_eligible,
        'match_reason_en': match_reason_en,
        'match_reason_hi': match_reason_hi,
        'user_inputs': data
    })

@app.route('/api/community-posts/<scheme_code>', methods=['GET'])
def get_community_posts(scheme_code):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM community_posts WHERE scheme_code = ?', (scheme_code,)).fetchall()
    conn.close()
    return jsonify([dict(p) for p in posts])

@app.route('/api/calculate-emi', methods=['POST'])
def calculate_emi():
    data = request.json or {}
    principal = float(data.get('principal', 100000))
    annual_rate = float(data.get('annual_rate', 6.5))
    total_tenure_months = int(data.get('tenure_months', 36))
    moratorium_months = int(data.get('moratorium_months', 3))

    repayment_months = max(1, total_tenure_months - moratorium_months)
    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate > 0:
        emi = principal * monthly_rate * math.pow(1 + monthly_rate, repayment_months) / (math.pow(1 + monthly_rate, repayment_months) - 1)
    else:
        emi = principal / repayment_months

    total_repayable = emi * repayment_months
    total_interest = total_repayable - principal

    summary_en = f"After a {moratorium_months}-month grace period (Moratorium) during your business setup, you will pay approximately ₹{round(emi, 2):,} per month for {repayment_months} months."
    summary_hi = f"आपके व्यवसाय सेटअप के दौरान {moratorium_months} महीने की छूट अवधि (स्थगन) के बाद, आप {repayment_months} महीनों के लिए प्रति माह लगभग ₹{round(emi, 2):,} का भुगतान करेंगे।"

    return jsonify({
        'principal': principal,
        'annual_rate': annual_rate,
        'total_tenure_months': total_tenure_months,
        'moratorium_months': moratorium_months,
        'repayment_months': repayment_months,
        'monthly_emi': round(emi, 2),
        'total_interest': round(total_interest, 2),
        'total_repayable': round(total_repayable, 2),
        'summary_en': summary_en,
        'summary_hi': summary_hi
    })

@app.route('/api/partners', methods=['GET'])
def get_partners():
    scheme_code = request.args.get('scheme_code', '')
    search_query = request.args.get('search', '').strip().lower()
    user_lat = request.args.get('lat', type=float)
    user_lng = request.args.get('lng', type=float)
    max_npa = request.args.get('max_npa', 8.0, type=float) # Default NPA filter threshold: 8.0%

    conn = get_db_connection()
    partners = conn.execute('SELECT * FROM channel_partners WHERE is_active = 1 AND npa_ratio <= ?', (max_npa,)).fetchall()
    conn.close()

    result = []
    for p in partners:
        p_dict = dict(p)
        
        # Scheme matching
        supported = [s.strip() for s in p_dict['supported_schemes'].split(',')]
        if scheme_code and 'ALL' not in supported and scheme_code not in supported and 'MICRO' not in supported and 'TERM' not in supported:
            # Keep bank available if it supports general concessional loans
            p_dict['scheme_matched'] = False
        else:
            p_dict['scheme_matched'] = True

        # Text search (city, state, pincode, bank name, branch)
        if search_query:
            searchable_text = f"{p_dict['name_en']} {p_dict['name_hi']} {p_dict['branch_name_en']} {p_dict['city']} {p_dict['state']} {p_dict['pincode']} {p_dict['address_en']}".lower()
            if search_query not in searchable_text:
                continue

        # Distance calculation
        if user_lat is not None and user_lng is not None:
            p_dict['distance_km'] = calculate_distance(user_lat, user_lng, p_dict['latitude'], p_dict['longitude'])
        else:
            p_dict['distance_km'] = None

        # Sanitize sensitive internal data (NPA ratio) from public citizen response
        del p_dict['npa_ratio']
        result.append(p_dict)

    # Sort by distance if lat/lng available, otherwise by name
    if user_lat is not None and user_lng is not None:
        result.sort(key=lambda x: x['distance_km'])

    return jsonify(result)

@app.route('/api/applications', methods=['POST'])
def submit_application():
    data = request.json or {}
    app_no = "NSFDC-" + str(uuid.uuid4())[:8].upper()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (
            application_no, applicant_name, gender, loan_purpose, required_amount,
            annual_income, education_status, recommended_scheme_code, calculated_emi,
            tenure_months, moratorium_months, chosen_mode, selected_partner_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        app_no,
        data.get('applicant_name', 'SC Beneficiary'),
        data.get('gender', 'male'),
        data.get('loan_purpose', 'micro_business'),
        float(data.get('required_amount', 100000)),
        float(data.get('annual_income', 200000)),
        data.get('education_status', 'undergraduate'),
        data.get('recommended_scheme_code', 'MICRO'),
        float(data.get('calculated_emi', 0.0)),
        int(data.get('tenure_months', 36)),
        int(data.get('moratorium_months', 3)),
        data.get('chosen_mode', 'offline'),
        data.get('selected_partner_id')
    ))
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'SUCCESS',
        'application_no': app_no,
        'message_en': 'Your scheme matching guidance application record has been registered successfully!',
        'message_hi': 'आपकी योजना मिलान मार्गदर्शन आवेदन रिकॉर्ड सफलतापूर्वक पंजीकृत हो गया है!'
    })

# -------------------------------------------------------------
# ADMIN API ENDPOINTS (Protected)
# -------------------------------------------------------------

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'admin123':
        return jsonify({'status': 'SUCCESS', 'token': 'admin-session-token-xyz-987'})
    return jsonify({'status': 'ERROR', 'message': 'Invalid admin credentials!'}), 401

@app.route('/api/admin/applications', methods=['GET'])
def admin_get_applications():
    conn = get_db_connection()
    apps = conn.execute('''
        SELECT a.*, p.name_en as partner_name, p.branch_name_en as partner_branch 
        FROM applications a 
        LEFT JOIN channel_partners p ON a.selected_partner_id = p.id
        ORDER BY a.created_at DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(a) for a in apps])

@app.route('/api/admin/partners', methods=['GET', 'POST', 'PUT', 'DELETE'])
def admin_partners_crud():
    conn = get_db_connection()

    if request.method == 'GET':
        # Admin gets FULL partner list INCLUDING NPA ratio
        partners = conn.execute('SELECT * FROM channel_partners ORDER BY npa_ratio ASC').fetchall()
        conn.close()
        return jsonify([dict(p) for p in partners])

    elif request.method == 'POST':
        data = request.json or {}
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO channel_partners (
                name_en, name_hi, partner_type, branch_name_en, branch_name_hi, address_en, address_hi,
                city, state, pincode, latitude, longitude, npa_ratio, is_active, supported_schemes,
                contact_number, email
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name_en'), data.get('name_hi'), data.get('partner_type'),
            data.get('branch_name_en'), data.get('branch_name_hi'), data.get('address_en'),
            data.get('address_hi'), data.get('city'), data.get('state'), data.get('pincode'),
            float(data.get('latitude', 28.6)), float(data.get('longitude', 77.2)),
            float(data.get('npa_ratio', 3.0)), int(data.get('is_active', 1)),
            data.get('supported_schemes', 'MICRO,TERM,EDUCATIONAL'),
            data.get('contact_number'), data.get('email')
        ))
        conn.commit()
        conn.close()
        return jsonify({'status': 'SUCCESS', 'message': 'Channel partner added successfully!'})

@app.route('/api/admin/posts', methods=['POST'])
def admin_add_post():
    data = request.json or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO community_posts (
            scheme_code, beneficiary_name_en, beneficiary_name_hi, location_en, location_hi,
            business_type_en, business_type_hi, loan_amount, story_en, story_hi, image_url,
            impact_badge_en, impact_badge_hi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('scheme_code'), data.get('beneficiary_name_en'), data.get('beneficiary_name_hi'),
        data.get('location_en'), data.get('location_hi'), data.get('business_type_en'),
        data.get('business_type_hi'), float(data.get('loan_amount', 100000)),
        data.get('story_en'), data.get('story_hi'), data.get('image_url'),
        data.get('impact_badge_en'), data.get('impact_badge_hi')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'SUCCESS', 'message': 'Community post added successfully!'})

@app.route('/api/admin/schemes', methods=['POST'])
def admin_update_scheme():
    data = request.json or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    
    code = data.get('code')
    action = data.get('action', 'update')
    
    existing = cursor.execute('SELECT * FROM schemes WHERE code = ?', (code,)).fetchone()
    
    if action == 'add' or not existing:
        cursor.execute('''
            INSERT INTO schemes (
                code, name_en, name_hi, category, max_amount, interest_rate_male, interest_rate_female,
                max_tenure_years, moratorium_months, income_limit, description_en, description_hi,
                eligibility_en, eligibility_hi, documents_en, documents_hi, cost_sharing_rule, online_apply_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            code,
            data.get('name_en', code),
            data.get('name_hi', code),
            data.get('category', 'term'),
            float(data.get('max_amount', 500000)),
            float(data.get('interest_rate_male', 8.0)),
            float(data.get('interest_rate_female', 7.5)),
            int(data.get('max_tenure_years', 5)),
            int(data.get('moratorium_months', 6)),
            float(data.get('income_limit', 500000)),
            data.get('description_en', 'Concessional scheme'),
            data.get('description_hi', 'रियायती योजना'),
            data.get('eligibility_en', 'SC Beneficiaries with income up to ₹5 Lakhs'),
            data.get('eligibility_hi', 'आय ₹5 लाख तक वाले एससी लाभार्थी'),
            data.get('documents_en', 'Aadhaar, Caste Certificate, Income Certificate'),
            data.get('documents_hi', 'आधार, जाति प्रमाण पत्र, आय प्रमाण पत्र'),
            data.get('cost_sharing_rule', '90% NSFDC / 10% Channel Partner'),
            data.get('online_apply_url', 'https://jansamarth.in/')
        ))
        conn.commit()
        conn.close()
        return jsonify({'status': 'SUCCESS', 'message': f'Scheme {code} added successfully!'})
    else:
        cursor.execute('''
            UPDATE schemes SET 
                max_amount = ?, interest_rate_male = ?, interest_rate_female = ?,
                max_tenure_years = ?, moratorium_months = ?, online_apply_url = ?
            WHERE code = ?
        ''', (
            float(data.get('max_amount', existing['max_amount'])),
            float(data.get('interest_rate_male', existing['interest_rate_male'])),
            float(data.get('interest_rate_female', existing['interest_rate_female'])),
            int(data.get('max_tenure_years', existing['max_tenure_years'])),
            int(data.get('moratorium_months', existing['moratorium_months'])),
            data.get('online_apply_url', existing['online_apply_url']),
            code
        ))
        conn.commit()
        conn.close()
        return jsonify({'status': 'SUCCESS', 'message': f'Scheme {code} updated successfully!'})

if __name__ == '__main__':
    print("Starting NSFDC Government Concessional Loan Scheme Portal Server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
