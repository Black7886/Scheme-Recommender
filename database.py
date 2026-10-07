import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Schemes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name_en TEXT NOT NULL,
            name_hi TEXT NOT NULL,
            category TEXT NOT NULL, -- micro, term, education
            max_amount REAL NOT NULL,
            interest_rate_male REAL NOT NULL,
            interest_rate_female REAL NOT NULL,
            max_tenure_years REAL NOT NULL,
            moratorium_months INTEGER NOT NULL,
            income_limit REAL NOT NULL,
            description_en TEXT NOT NULL,
            description_hi TEXT NOT NULL,
            eligibility_en TEXT NOT NULL,
            eligibility_hi TEXT NOT NULL,
            documents_en TEXT NOT NULL,
            documents_hi TEXT NOT NULL,
            cost_sharing_rule TEXT NOT NULL,
            online_apply_url TEXT NOT NULL
        )
    ''')

    # 2. Community Success Posts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_code TEXT NOT NULL,
            beneficiary_name_en TEXT NOT NULL,
            beneficiary_name_hi TEXT NOT NULL,
            location_en TEXT NOT NULL,
            location_hi TEXT NOT NULL,
            business_type_en TEXT NOT NULL,
            business_type_hi TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            story_en TEXT NOT NULL,
            story_hi TEXT NOT NULL,
            image_url TEXT,
            impact_badge_en TEXT,
            impact_badge_hi TEXT
        )
    ''')

    # 3. Channel Partners / Banks Table (with NPA Ratio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_hi TEXT NOT NULL,
            partner_type TEXT NOT NULL,
            branch_name_en TEXT NOT NULL,
            branch_name_hi TEXT NOT NULL,
            address_en TEXT NOT NULL,
            address_hi TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            pincode TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            npa_ratio REAL NOT NULL,
            is_active INTEGER DEFAULT 1,
            supported_schemes TEXT NOT NULL,
            contact_number TEXT,
            email TEXT
        )
    ''')

    # 4. Citizen Applications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_no TEXT UNIQUE NOT NULL,
            applicant_name TEXT,
            gender TEXT NOT NULL,
            loan_purpose TEXT NOT NULL,
            required_amount REAL NOT NULL,
            annual_income REAL NOT NULL,
            education_status TEXT NOT NULL,
            recommended_scheme_code TEXT NOT NULL,
            calculated_emi REAL NOT NULL,
            tenure_months INTEGER NOT NULL,
            moratorium_months INTEGER NOT NULL,
            chosen_mode TEXT NOT NULL,
            selected_partner_id INTEGER,
            status TEXT DEFAULT 'SUBMITTED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Re-seed Schemes Data from PDF (6 Schemes)
    cursor.execute('DELETE FROM schemes')
    cursor.executemany('''
        INSERT INTO schemes (
            code, name_en, name_hi, category, max_amount, interest_rate_male, interest_rate_female, 
            max_tenure_years, moratorium_months, income_limit, description_en, description_hi, 
            eligibility_en, eligibility_hi, documents_en, documents_hi, cost_sharing_rule, online_apply_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        (
            'MCF',
            'Micro Credit Finance (MCF)',
            'माइक्रो क्रेडिट फाइनेंस योजना (MCF)',
            'micro',
            125000.0,
            6.5,
            6.5,
            3.0,
            3,
            500000.0,
            'Concessional micro-credit for small-scale traders, artisans, vegetable vendors, and micro-entrepreneurs to initiate or expand micro businesses.',
            'छोटे व्यापारियों, कारीगरों, सब्जी विक्रेताओं और सूक्ष्म उद्यमियों के लिए सूक्ष्म व्यवसाय शुरू करने या विस्तार करने हेतु रियायती सूक्ष्म ऋण।',
            'Scheduled Caste (SC) individuals with annual family income up to ₹5.00 Lakhs. Age 18 to 60 years.',
            'अनुसूचित जाति (SC) के व्यक्ति जिनकी वार्षिक पारिवारिक आय ₹5.00 लाख तक है। आयु 18 से 60 वर्ष।',
            'Caste Certificate, Family Income Certificate, Aadhaar Card, Bank Passbook, Project Cost Estimate',
            'जाति प्रमाण पत्र, पारिवारिक आय प्रमाण पत्र, आधार कार्ड, बैंक पासबुक, परियोजना लागत अनुमान',
            'Up to 90% Funded by NSFDC / 10% Channelizing Partner Contribution',
            'https://pmsuraj.dosje.gov.in'
        ),
        (
            'MSY',
            'Mahila Samriddhi Yojana (MSY)',
            'महिला समृद्धि योजना (MSY)',
            'micro',
            125000.0,
            4.0,
            4.0,
            3.5,
            3,
            500000.0,
            'Exclusive concessional business credit scheme for eligible SC women entrepreneurs at an ultra-low concessional interest rate of 4% p.a.',
            'पात्र अनुसूचित जाति की महिला उद्यमियों के लिए 4% वार्षिक की अत्यधिक रियायती ब्याज दर पर विशेष व्यापारिक ऋण योजना।',
            'Eligible Scheduled Caste (SC) female entrepreneurs with annual family income up to ₹5.00 Lakhs.',
            'अनुसूचित जाति (SC) की पात्र महिला उद्यमी जिनकी वार्षिक पारिवारिक आय ₹5.00 लाख तक है।',
            'Caste Certificate, Income Certificate, Woman Entrepreneur Self-Declaration, Aadhaar Card, Bank Details',
            'जाति प्रमाण पत्र, आय प्रमाण पत्र, महिला उद्यमी स्व-घोषणा, आधार कार्ड, बैंक विवरण',
            'Up to 90% Funded by NSFDC / 10% Borrower/Agency Share',
            'https://pmsuraj.dosje.gov.in'
        ),
        (
            'AMY',
            'Aajeevika Microfinance Yojana (AMY)',
            'जीविका माइक्रोफाइनेंस योजना (AMY)',
            'micro',
            125000.0,
            15.0,
            15.0,
            3.0,
            3,
            500000.0,
            'Quick grassroots micro-credit disbursed through selected NBFC-MFIs for instant working capital and small business activities.',
            'तत्काल कार्यशील पूंजी और लघु व्यावसायिक गतिविधियों के लिए चयनित एनबीएफसी-एमएफआई के माध्यम से त्वरित जमीनी स्तर का सूक्ष्म ऋण।',
            'SC individuals needing fast micro-credit through NBFC-MFI network. Annual family income up to ₹5.00 Lakhs.',
            'एनबीएफसी-एमएफआई नेटवर्क के माध्यम से त्वरित सूक्ष्म ऋण की आवश्यकता वाले एससी व्यक्ति। वार्षिक आय ₹5 लाख तक।',
            'SC Certificate, Income Verification, Aadhaar Card, MFI Member Passbook',
            'एससी प्रमाण पत्र, आय सत्यापन, आधार कार्ड, एमएफआई सदस्य पासबुक',
            'Disbursed through accredited NBFC-MFIs / NSFDC Channel',
            'https://pmsuraj.dosje.gov.in'
        ),
        (
            'TERM',
            'Flagship Term Loan Scheme',
            'प्रमुख टर्म लोन योजना (Flagship Term Loan)',
            'term',
            4500000.0,
            8.0,
            8.0,
            7.0,
            6,
            500000.0,
            'Provides substantial concessional finance up to ₹45 Lakhs for setting up larger income-generating, manufacturing, service, and commercial projects.',
            'बड़ी आय पैदा करने वाली, विनिर्माण, सेवा और वाणिज्यिक परियोजनाओं की स्थापना के लिए ₹45 लाख तक का बड़ा रियायती वित्त प्रदान करता है।',
            'SC entrepreneurs with viable commercial business projects up to ₹45 Lakhs. Family income up to ₹5.00 Lakhs.',
            '₹45 लाख तक की व्यावहारिक वाणिज्यिक व्यावसायिक परियोजनाओं वाले एससी उद्यमी। पारिवारिक आय ₹5.00 लाख तक।',
            'Detailed Project Report (DPR), Caste & Income Certificate, Trade License, Machinery Quotations, PAN & Aadhaar',
            'विस्तृत परियोजना रिपोर्ट (DPR), जाति एवं आय प्रमाण पत्र, व्यापार लाइसेंस, मशीनरी उद्धरण, पैन एवं आधार',
            'Up to 90% Loan Funded by NSFDC / 10% Promoter Share',
            'https://pmsuraj.dosje.gov.in'
        ),
        (
            'GBS',
            'Green Business Scheme (GBS)',
            'ग्रीन बिजनेस स्कीम (GBS)',
            'term',
            3000000.0,
            8.0,
            7.5,
            7.0,
            6,
            500000.0,
            'Concessional finance for eco-friendly business activities such as E-Rickshaws, Solar PV Energy Units, Poly-houses, and Waste Management projects.',
            'ई-रिक्शा, सोलर पीवी एनर्जी यूनिट, पॉली-हाउस और कचरा प्रबंधन परियोजनाओं जैसे पर्यावरण-अनुकूल व्यावसायिक गतिविधियों के लिए रियायती वित्त।',
            'SC entrepreneurs establishing eco-friendly business units or purchasing E-Rickshaws. Family income up to ₹5.00 Lakhs.',
            'पर्यावरण के अनुकूल व्यावसायिक इकाइयाँ स्थापित करने या ई-रिक्शा खरीदने वाले एससी उद्यमी। पारिवारिक आय ₹5.00 लाख तक।',
            'E-Vehicle Quotation / Solar Project Estimate, Caste & Income Certificate, Aadhaar & Driving License (for E-Rickshaw)',
            'ई-वाहन उद्धरण / सौर परियोजना अनुमान, जाति एवं आय प्रमाण पत्र, आधार एवं ड्राइविंग लाइसेंस (ई-रिक्शा के लिए)',
            '90% NSFDC Concessional Loan / 10% Channelizing Partner Share',
            'https://pmsuraj.dosje.gov.in'
        ),
        (
            'ELS',
            'Educational Loan Scheme (ELS)',
            'शिक्षा ऋण योजना (ELS)',
            'education',
            4000000.0,
            6.5,
            6.5,
            12.0,
            12,
            500000.0,
            'Concessional loan up to ₹40 Lakhs for full-time professional and technical education in India or Abroad with repayment up to 12 years.',
            'भारत या विदेशों में पूर्णकालिक पेशेवर और तकनीकी शिक्षा के लिए ₹40 लाख तक का रियायती ऋण, जिसकी पुनर्भुगतान अवधि 12 वर्ष तक है।',
            'SC students admitted to recognized technical/professional graduate or post-graduate courses in India or abroad. Family income up to ₹5.00 Lakhs.',
            'भारत या विदेश में मान्यता प्राप्त तकनीकी/पेशेवर स्नातक या स्नातकोत्तर पाठ्यक्रमों में प्रवेश प्राप्त एससी छात्र। पारिवारिक आय ₹5.00 लाख तक।',
            'Admission Confirmation Letter, Fee Structure, 10th/12th/Degree Marksheets, Caste & Income Certificate, Aadhaar Card',
            'प्रवेश पुष्टि पत्र, शुल्क संरचना, 10वीं/12वीं/डिग्री अंकपत्र, जाति एवं आय प्रमाण पत्र, आधार कार्ड',
            '90% Course Fee & Boarding Expenses Covered / 10% Student Contribution',
            'https://pmsuraj.dosje.gov.in'
        )
    ])

    # Re-seed Community Posts for the 6 Schemes
    cursor.execute('DELETE FROM community_posts')
    cursor.executemany('''
        INSERT INTO community_posts (
            scheme_code, beneficiary_name_en, beneficiary_name_hi, location_en, location_hi,
            business_type_en, business_type_hi, loan_amount, story_en, story_hi, image_url,
            impact_badge_en, impact_badge_hi
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        (
            'MCF',
            'Ramesh Kumar',
            'रमेश कुमार',
            'Nagpur, Maharashtra',
            'नागपुर, महाराष्ट्र',
            'Micro Hardware & Electrical Shop',
            'माइक्रो हार्डवेयर एवं इलेक्ट्रिकल शॉप',
            120000.0,
            'With a loan of ₹1.20 Lakh under Micro Credit Finance (MCF) at 6.5% interest, Ramesh set up a small electrical repair shop. He now supports his family and employs 2 local youths.',
            '6.5% ब्याज पर माइक्रो क्रेडिट फाइनेंस (MCF) के तहत ₹1.20 लाख के ऋण से रमेश ने एक छोटी इलेक्ट्रिकल मरम्मत की दुकान खोली। वे अब अपने परिवार का भरण-पोषण करते हैं और 2 युवाओं को रोजगार दिया है।',
            'https://images.unsplash.com/photo-1617886831575-b6d34b358580?auto=format&fit=crop&w=400&q=80',
            'Micro Entrepreneur',
            'सूक्ष्म उद्यमी'
        ),
        (
            'MSY',
            'Sunita Devi',
            'सुनीता देवी',
            'Jaipur, Rajasthan',
            'जयपुर, राजस्थान',
            'Garment Tailoring & Boutique Unit',
            'गारमेंट सिलाई एवं बुटीक इकाई',
            110000.0,
            'Sunita availed ₹1.10 Lakh under Mahila Samriddhi Yojana (MSY) at an ultra-low 4.0% interest rate to buy 3 stitching machines. She now supplies readymade dresses to local markets.',
            'सुनीता ने 3 सिलाई मशीनें खरीदने के लिए 4.0% की अत्यधिक कम ब्याज दर पर महिला समृद्धि योजना (MSY) के तहत ₹1.10 लाख का लाभ उठाया। वह अब स्थानीय बाजारों में रेडीमेड परिधानों की आपूर्ति करती हैं।',
            'https://images.unsplash.com/photo-1590736969955-71cc94801759?auto=format&fit=crop&w=400&q=80',
            'Women Empowerment',
            'महिला सशक्तिकरण'
        ),
        (
            'AMY',
            'Kavita Shinde',
            'कविता शिंदे',
            'Pune, Maharashtra',
            'पुणे, महाराष्ट्र',
            'Vegetable Vending & Grocery Supply',
            'सब्जी बिक्री एवं किराना आपूर्ति',
            80000.0,
            'Kavita received fast micro-credit of ₹80,000 via NBFC-MFI channel under Aajeevika Microfinance Yojana (AMY) for working capital. Her daily income increased by 50%.',
            'कविता को कार्यशील पूंजी के लिए जीविका माइक्रोफाइनेंस योजना (AMY) के तहत NBFC-MFI के माध्यम से ₹80,000 का त्वरित ऋण प्राप्त हुआ। उनकी दैनिक आय में 50% की वृद्धि हुई।',
            'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80',
            'Fast Micro-Credit',
            'त्वरित सूक्ष्म ऋण'
        ),
        (
            'TERM',
            'Rajesh Solanki',
            'राजेश सोलंकी',
            'Ahmedabad, Gujarat',
            'अहमदाबाद, गुजरात',
            'Cold Storage & Agro Processing Unit',
            'कोल्ड स्टोरेज एवं एग्रो प्रोसेसिंग यूनिट',
            1800000.0,
            'Rajesh established a mini cold storage unit with a Flagship Term Loan of ₹18 Lakhs at 8% interest. He helps 40+ local SC farmers preserve produce and prevent distress sales.',
            'राजेश ने 8% ब्याज पर ₹18 लाख के प्रमुख टर्म लोन के साथ एक मिनी कोल्ड स्टोरेज यूनिट की स्थापना की। वे 40+ स्थानीय एससी किसानों को उपज संरक्षित करने में मदद करते हैं।',
            'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=400&q=80',
            'Helps 40+ Farmers',
            '40+ किसानों की मदद'
        ),
        (
            'GBS',
            'Vijay Sonawane',
            'विजय सोनावणे',
            'Indore, Madhya Pradesh',
            'इंदौर, मध्य प्रदेश',
            'E-Rickshaw Fleet & Charging Station',
            'ई-रिक्शा बेड़ा एवं चार्जिंग स्टेशन',
            250000.0,
            'Vijay purchased 2 Battery E-Rickshaws under Green Business Scheme (GBS). He provides clean passenger transport in Indore and earns ₹40,000 monthly.',
            'विजय ने ग्रीन बिजनेस स्कीम (GBS) के तहत 2 बैटरी ई-रिक्शा खरीदे। वे इंदौर में स्वच्छ यात्री परिवहन प्रदान करते हैं और मासिक ₹40,000 कमाते हैं।',
            'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=400&q=80',
            'Eco-Friendly Transport',
            'पर्यावरण-अनुकूल परिवहन'
        ),
        (
            'ELS',
            'Priya Verma',
            'प्रिया वर्मा',
            'Bhopal, Madhya Pradesh',
            'भोपाल, मध्य प्रदेश',
            'M.Tech in Data Science & AI',
            'डेटा साइंस एवं एआई में एम.टेक',
            1200000.0,
            'Priya secured ₹12 Lakhs Educational Loan (ELS) at 6.5% interest. She completed her M.Tech degree and is now working as a Senior Software Engineer at an MNC.',
            'प्रिया ने 6.5% ब्याज पर ₹12 लाख का शिक्षा ऋण (ELS) प्राप्त किया। उन्होंने एम.टेक पूरा किया और अब एक बहुराष्ट्रीय कंपनी में सीनियर सॉफ्टवेयर इंजीनियर के रूप में कार्यरत हैं।',
            'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=400&q=80',
            'MNC Campus Placed',
            'एमएनसी कैंपस प्लेसमेंट'
        )
    ])

    # Re-seed Channel Partners to support the new scheme codes
    cursor.execute("UPDATE channel_partners SET supported_schemes = 'MCF,MSY,AMY,TERM,GBS,ELS'")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database updated successfully with 6 PDF schemes!")
