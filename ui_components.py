# ui_components.py
import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: #f0f2f5; }
        .main-header {
            background: linear-gradient(135deg, #1e5f6b 0%, #2c7a8a 100%);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            margin-bottom: 32px;
            color: white;
        }
        .main-header h1 { font-size: 2rem; margin-bottom: 8px; }
        .main-header p { opacity: 0.9; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e0e4e8;
        }
        .doctor-card {
            background: white;
            border-radius: 20px;
            padding: 24px;
            margin: 20px 0;
            border: 1px solid #e0e4e8;
            transition: all 0.3s ease;
        }
        .doctor-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .doctor-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e8f4f0;
        }
        .doctor-avatar {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #2c7a8a 0%, #1e5f6b 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: white;
        }
        .doctor-info h3 { color: #1e5f6b; margin: 0 0 5px 0; }
        .doctor-specialty { color: #2c7a8a; font-weight: 600; }
        .rating { color: #ffc107; font-size: 14px; }
        .grid-2 {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .grid-col { flex: 1; min-width: 200px; }
        .grid-col p { margin: 8px 0; color: #4a5568; }
        .grid-col strong { color: #1e5f6b; }
        .availability {
            background: #e8f4f0;
            padding: 12px 16px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-green { background: #d4edda; color: #155724; }
        .badge-red { background: #f8d7da; color: #721c24; }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a3a4a 0%, #1e4a5e 100%);
        }
        .stButton > button {
            background: linear-gradient(135deg, #2c7a8a 0%, #1e5f6b 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 500;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(44,122,138,0.3);
        }
        .stChatMessage {
            background: white !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin: 8px 0 !important;
            border: 1px solid #e0e4e8 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def show_about_page():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Welcome to Dr. Well</h1>
        <p>Your AI-Powered Medical Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h2 style="color: #1e5f6b;">🌟 About Dr. Well</h2>
            <p>Dr. Well is an AI Medical Assistant that can:</p>
            <ul>
                <li>🤖 <strong>Analyze Symptoms</strong> - Get instant diagnosis</li>
                <li>💊 <strong>Recommend Medications</strong> - Auto-add to your list</li>
                <li>👨‍⚕️ <strong>Refer to Specialists</strong> - Find the right doctor</li>
                <li>📅 <strong>Book Appointments</strong> - Schedule consultations</li>
                <li>🍎 <strong>Nutrition Advice</strong> - Personalized tips</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h2 style="color: #1e5f6b; text-align: center;">🎯 What Dr. Well Can Do</h2>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 20px; margin: 12px 0; text-align: center;">
                <h3 style="color: #1e5f6b;">🤖 Symptom Analysis</h3>
                <p>Instant diagnosis from symptoms</p>
            </div>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 20px; margin: 12px 0; text-align: center;">
                <h3 style="color: #1e5f6b;">💊 Medication Prescriber</h3>
                <p>Auto-adds prescriptions to your list</p>
            </div>
            <div style="background: #e8f4f0; border-radius: 12px; padding: 20px; margin: 12px 0; text-align: center;">
                <h3 style="color: #1e5f6b;">👨‍⚕️ Doctor Referral</h3>
                <p>Connects you with specialists</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_login_ui():
    st.markdown('<div class="card" style="max-width: 450px; margin: 0 auto;"><div style="text-align: center;"><h2 style="color: #1e5f6b;">Welcome Back!</h2><p>Login to continue</p></div>', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login", use_container_width=True):
            if username and password:
                return {"username": username, "password": password}
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def show_signup_ui():
    st.markdown('<div class="card" style="max-width: 450px; margin: 0 auto;"><div style="text-align: center;"><h2 style="color: #1e5f6b;">Create Account</h2><p>Join Dr. Well today</p></div>', unsafe_allow_html=True)
    with st.form("signup_form"):
        user_type = st.radio("I am a:", ["Patient", "Doctor"], horizontal=True)
        full_name = st.text_input("Full Name*")
        email = st.text_input("Email*")
        username = st.text_input("Username*")
        password = st.text_input("Password*", type="password")
        confirm = st.text_input("Confirm Password*", type="password")
        phone = st.text_input("Phone Number")
        
        if st.form_submit_button("Sign Up", use_container_width=True):
            if all([full_name, email, username, password, confirm]):
                if password == confirm and len(password) >= 6:
                    return {"full_name": full_name, "email": email, "username": username, 
                            "password": password, "user_type": user_type.lower(), "phone": phone}
                else:
                    st.error("Passwords must match and be at least 6 characters")
            else:
                st.error("Please fill all required fields")
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def show_patient_info_form():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1e5f6b;'>👤 Complete Your Profile</h2>", unsafe_allow_html=True)
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, value=70.0)
            height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, step=0.1, value=170.0)
        with col2:
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            allergies = st.text_input("Allergies", placeholder="e.g., Penicillin, Peanuts")
        about = st.text_area("About Yourself", placeholder="Tell us about yourself...")
        if st.form_submit_button("Save Profile", use_container_width=True):
            return {"weight": weight, "height": height, "blood_group": blood_group, "allergies": allergies, "about": about}
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def show_doctor_info_form():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1e5f6b;'>👨‍⚕️ Complete Your Profile</h2>", unsafe_allow_html=True)
    with st.form("doctor_form"):
        col1, col2 = st.columns(2)
        with col1:
            specialty = st.selectbox("Specialty*", [
                "Cardiologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon",
                "Pediatrician", "General Physician", "ENT Specialist", "Ophthalmologist", "Gynecologist"
            ])
            qualification = st.text_input("Qualification*", placeholder="e.g., MBBS, MD")
            experience = st.number_input("Years of Experience*", min_value=0, max_value=50, step=1, value=10)
            fee = st.number_input("Consultation Fee ($)*", min_value=0, step=10, value=100)
        with col2:
            clinic_name = st.text_input("Clinic Name*", placeholder="e.g., City Hospital")
            clinic_address = st.text_input("Clinic Address*", placeholder="Street, Area")
            city = st.text_input("City*")
            state = st.text_input("State*")
            zip_code = st.text_input("ZIP Code*")
            phone = st.text_input("Clinic Phone*")
        
        days = st.multiselect("Available Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        col3, col4 = st.columns(2)
        with col3:
            start = st.time_input("From")
        with col4:
            end = st.time_input("To")
        about = st.text_area("About Yourself", placeholder="Your experience, achievements, etc.")
        
        if st.form_submit_button("Save Profile", use_container_width=True):
            if all([specialty, qualification, clinic_name, clinic_address, city, state, zip_code, phone, days]):
                return {"specialty": specialty, "qualification": qualification, "experience": experience, "fee": fee,
                        "clinic_name": clinic_name, "clinic_address": clinic_address, "city": city, "state": state,
                        "zip_code": zip_code, "phone": phone, "days": ",".join(days), 
                        "start": start.strftime("%H:%M"), "end": end.strftime("%H:%M"), "about": about}
            else:
                st.error("Please fill all required fields")
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def show_doctor_card(doctor):
    def safe_get(value, default='N/A'):
        if value is None:
            return default
        return str(value) if value else default
    
    rating_value = doctor.get('rating')
    try:
        rating_float = float(rating_value) if rating_value else 4.5
        rating_int = int(rating_float)
    except (ValueError, TypeError):
        rating_int = 4
        rating_float = 4.5
    
    rating_stars = "⭐" * rating_int + "☆" * (5 - rating_int)
    
    with st.container():
        st.markdown(f"""
        <div class="doctor-card">
            <div class="doctor-header">
                <div class="doctor-avatar">👨‍⚕️</div>
                <div class="doctor-info">
                    <h3>{safe_get(doctor.get('full_name'))}</h3>
                    <div class="doctor-specialty">{safe_get(doctor.get('specialty'))}</div>
                    <div class="rating">{rating_stars} {rating_float} ({safe_get(doctor.get('total_reviews'), 0)} reviews)</div>
                </div>
            </div>
            <div class="grid-2">
                <div class="grid-col">
                    <p><strong>📚 Qualification:</strong> {safe_get(doctor.get('qualification'))}</p>
                    <p><strong>📅 Experience:</strong> {safe_get(doctor.get('experience_years'), 0)} years</p>
                    <p><strong>💰 Fee:</strong> ${safe_get(doctor.get('consultation_fee'), 0)}</p>
                    <p><strong>📞 Phone:</strong> {safe_get(doctor.get('phone'))}</p>
                </div>
                <div class="grid-col">
                    <p><strong>🏥 Clinic:</strong> {safe_get(doctor.get('clinic_name'))}</p>
                    <p><strong>📍 Address:</strong> {safe_get(doctor.get('clinic_address'))}</p>
                    <p><strong>🌆 City:</strong> {safe_get(doctor.get('city'))}, {safe_get(doctor.get('state'))} {safe_get(doctor.get('zip_code'))}</p>
                    <p><strong>📧 Email:</strong> {safe_get(doctor.get('email'))}</p>
                </div>
            </div>
            <div class="availability">
                <p><strong>🕒 Available:</strong> {safe_get(doctor.get('available_days'))} | {safe_get(doctor.get('available_time_start'))} - {safe_get(doctor.get('available_time_end'))}</p>
            </div>
            <p><strong>📝 About:</strong> {safe_get(doctor.get('about'))[:200] if doctor.get('about') else 'Experienced medical professional.'}</p>
            <div class="badge badge-green">✓ Available for Consultation</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"📅 Book Appointment with {safe_get(doctor.get('full_name'))}", key=f"book_{doctor['id']}"):
            return doctor
    return None
