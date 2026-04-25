# main.py
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import google.generativeai as genai
import time
import uuid
import re
from config import *
from database import *
from ui_components import *

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Dr. Well - AI Medical Assistant", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

def get_all_doctors_text():
    """Get all doctors information for AI context"""
    all_doctors = get_all_doctors()
    doctors_info = []
    for doc in all_doctors:
        doctors_info.append(f"Dr. {doc.get('full_name')}|Specialty:{doc.get('specialty')}|Clinic:{doc.get('clinic_name')}|City:{doc.get('city')}|Fee:${doc.get('consultation_fee')}|Phone:{doc.get('phone')}|Days:{doc.get('available_days')}|Time:{doc.get('available_time_start')}-{doc.get('available_time_end')}")
    return "\n".join(doctors_info) if doctors_info else "No doctors available"

def search_doctor_by_name(doctor_name):
    """Search doctor by name"""
    all_doctors = get_all_doctors()
    doctor_name_lower = doctor_name.lower()
    for doc in all_doctors:
        full_name = doc.get('full_name', '').lower()
        if doctor_name_lower in full_name or doctor_name_lower in doc.get('specialty', '').lower():
            return doc
    return None

def stream_response(response_text):
    """Stream response word by word"""
    words = response_text.split()
    for word in words:
        yield word + " "
        time.sleep(0.03)

def get_ai_medical_response(user_message, chat_history, session_id):
    """Get response from Gemini AI with complete doctor database and treatment-first approach"""
    
    # Get complete doctors database
    doctors_text = get_all_doctors_text()
    
    # Get patient medications
    patient_meds = get_medications(st.session_state.user_id)
    meds_text = "\n".join([f"- {m['name']}: {m['dosage']}, {m['frequency']}" for m in patient_meds]) if patient_meds else "No active medications"
    
    # Get conversation context
    memory_text = ""
    for msg in chat_history[-8:]:
        memory_text += f"{msg['role']}: {msg['content'][:150]}\n"
    
    context = f"""
    You are Dr. Well, a smart and caring AI medical assistant. You have COMPLETE access to all doctors in our database.

    🏥 COMPLETE DOCTORS DATABASE (You MUST use this to answer any doctor-related questions):
    {doctors_text}
    
    PATIENT INFO:
    - Current medications: {meds_text}
    
    CONVERSATION MEMORY:
    {memory_text}
    
    PATIENT'S LATEST MESSAGE: {user_message}
    
    ⚠️ IMPORTANT RULES - FOLLOW STRICTLY:
    
    1. TREATMENT FIRST APPROACH:
       - FIRST try to treat with medicine and home remedies
       - Give specific medicine names, dosage, timing, and food restrictions
       - ONLY refer to specialist if patient doesn't improve or symptoms are severe
    
    2. WHEN TO REFER TO DOCTOR:
       - If patient says "no improvement", "still in pain", "medicine not working"
       - If symptoms are severe (chest pain radiating to arm/jaw, difficulty breathing)
       - If condition needs specialist care
    
    3. DOCTOR INFORMATION (Use exact database info):
       - When patient asks about ANY doctor, give COMPLETE details from database:
         * Full name
         * Specialty 
         * Clinic name and address
         * City
         * Consultation fee
         * Phone number
         * Available days and timings
    
    4. MEDICINE PRESCRIPTION:
       - Give: name, dosage, frequency, timing (before/after food)
       - Also give FOOD RESTRICTIONS (what to eat/avoid)
       - Tell how many days to take
       - Tell when to come back if no improvement
    
    5. RESPONSE STYLE:
       - Keep response UNDER 60 words
       - Be friendly and caring
       - Ask follow-up questions if needed
       - End with "Take care! - Dr. Well"
    
    Now respond as Dr. Well:
    """
    
    try:
        response = model.generate_content(context)
        reply = response.text.strip()
        
        words = reply.split()
        if len(words) > 60:
            reply = ' '.join(words[:57]) + "... Take care! - Dr. Well"
        
        return reply
    except Exception as e:
        return get_fallback_response(user_message)

def get_fallback_response(user_message):
    """Fallback response when API fails"""
    msg_lower = user_message.lower()
    
    # Check for doctor questions
    if "doctor" in msg_lower or "dr" in msg_lower:
        # Extract doctor name
        import re
        doctor_match = re.search(r'(?:Dr\.?\s*)([A-Za-z]+(?:\s+[A-Za-z]+)?)', user_message, re.IGNORECASE)
        if doctor_match:
            doctor_name = doctor_match.group(1)
            doctor = search_doctor_by_name(doctor_name)
            if doctor:
                return f"""**Dr. {doctor['full_name']}** 
- Specialty: {doctor['specialty']}
- Clinic: {doctor['clinic_name']}, {doctor['city']}
- Fee: ${doctor['consultation_fee']}
- Phone: {doctor['phone']}
- Available: {doctor['available_days']} {doctor['available_time_start']}-{doctor['available_time_end']}

Take care! - Dr. Well"""
    
    # Check for appointment questions
    if "appointment" in msg_lower or "kab" in msg_lower or "mile" in msg_lower:
        return "Please call the clinic directly to check appointment availability and book your visit. Their phone number is mentioned in the doctor's details above. Take care! - Dr. Well"
    
    # Chest pain emergency
    if "chest" in msg_lower and "pain" in msg_lower:
        return "⚠️ Chest pain needs attention! First, take rest. If pain is sharp or spreading to arm/jaw, please see a Cardiologist immediately. Dr. Sarah Smith (Heart Care Clinic, NY) or Dr. Ahmed Khan (City Heart Institute, Chicago) can help. Call them for emergency appointment. Take care! - Dr. Well"
    
    # General response
    return "Please tell me more about your symptoms so I can help you better. Take care! - Dr. Well"

def extract_medication_from_response(response_text, user_message):
    """Extract medication info from AI response and auto-add to database"""
    # Common medicine patterns
    med_patterns = [
        r'(\w+(?:\s+\w+)?)\s+(\d+\s*(?:mg|ml|g|tablet|capsule))',
        r'take\s+(\w+(?:\s+\w+)?)\s+(\d+\s*(?:mg|ml|g))',
        r'(\w+(?:\s+\w+)?)\s+tablet',
        r'(\w+(?:\s+\w+)?)\s+capsule'
    ]
    
    for pattern in med_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            med_name = match.group(1)
            med_dosage = match.group(2) if len(match.groups()) > 1 else "As prescribed"
            
            # Don't add if already exists
            existing_meds = get_medications(st.session_state.user_id)
            if not any(m['name'].lower() == med_name.lower() for m in existing_meds):
                save_medication(
                    st.session_state.user_id, med_name, med_dosage,
                    "As prescribed", "With food", 5, "Avoid spicy/oily food", "Dr. Well AI"
                )
                return med_name
    return None

# ========== PAGE FUNCTIONS ==========
def dashboard():
    user = get_user_by_id(st.session_state.user_id)
    show_hero_banner(user.get('full_name', 'User'))
    show_dashboard_stats()
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🩺 **Consultations**\nChat with AI Doctor", use_container_width=True):
            st.session_state.page = "Consultations"
            st.rerun()
    
    with col2:
        if st.button("🍎 **Nutrition**\nGet diet advice", use_container_width=True):
            st.session_state.page = "Nutrition"
            st.rerun()
    
    with col3:
        if st.button("💊 **Medications**\nView prescriptions", use_container_width=True):
            st.session_state.page = "Medications"
            st.rerun()
    
    with col4:
        if st.button("📅 **Appointments**\nSchedule visits", use_container_width=True):
            st.session_state.page = "Appointments"
            st.rerun()
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if st.button("👨‍⚕️ **Find Doctors**\nBrowse specialists", use_container_width=True):
            st.session_state.page = "Find Doctors"
            st.rerun()
    
    with col6:
        if st.button("👤 **My Profile**\nUpdate information", use_container_width=True):
            st.session_state.page = "Profile"
            st.rerun()
    
    with col7:
        if st.button("🚨 **Emergency**\nGet immediate help", use_container_width=True):
            st.error("🚨 **EMERGENCY!** Please call emergency services (911/1122) immediately!")
            st.info("📞 **Emergency Numbers:**\n- Ambulance: 911/1122\n- Poison Control: 1-800-222-1222")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card"><h3>💊 Recent Medications</h3>', unsafe_allow_html=True)
        meds = get_medications(st.session_state.user_id)
        if meds:
            for m in meds[:5]:
                st.write(f"• **{m['name']}** - {m['dosage']}")
        else:
            st.info("No active medications")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3>📅 Upcoming Appointments</h3>', unsafe_allow_html=True)
        apts = get_appointments(st.session_state.user_id)
        upcoming = [a for a in apts if a['status'] != 'Completed'][:5]
        if upcoming:
            for a in upcoming:
                st.write(f"• **Dr. {a['doctor_name']}** - {a['date']}")
        else:
            st.info("No upcoming appointments")
        st.markdown('</div>', unsafe_allow_html=True)

def consultations():
    st.markdown('<div class="main-header"><h1>🩺 AI Medical Consultation</h1><p>Dr. Well will FIRST try to treat you, then refer to specialist if needed</p></div>', unsafe_allow_html=True)
    
    show_chat_welcome()
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
        st.session_state.chat_messages = []
    
    if 'chat_messages' not in st.session_state or len(st.session_state.chat_messages) == 0:
        saved_messages = get_chat_history(st.session_state.user_id, st.session_state.chat_session_id)
        st.session_state.chat_messages = [{"role": msg['role'], "content": msg['content']} for msg in saved_messages]
    
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        sessions = get_all_sessions(st.session_state.user_id)
        for sess in sessions[:5]:
            if st.button(f"📅 {sess['created_at'][:16]}", key=f"sess_{sess['id']}"):
                st.session_state.chat_session_id = sess['session_id']
                st.session_state.chat_messages = [{"role": msg['role'], "content": msg['content']} 
                                                   for msg in get_chat_history(st.session_state.user_id, sess['session_id'])]
                st.rerun()
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
            st.session_state.chat_messages = []
            st.rerun()
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🩺 Dr. Well is analyzing..."):
                response = get_ai_medical_response(prompt, st.session_state.chat_messages, st.session_state.chat_session_id)
                
                message_placeholder = st.empty()
                full_response = ""
                for chunk in stream_response(response):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
            save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "assistant", full_response)
            
            med_added = extract_medication_from_response(full_response, prompt)
            if med_added:
                st.success(f"💊 {med_added} added to your medications list!")
            
            if "cardiologist" in full_response.lower() or "heart" in prompt.lower():
                doctors = get_doctor_by_specialty('Cardiologist')
                if doctors:
                    st.warning("### 👨‍⚕️ Recommended Heart Specialists:")
                    for doc in doctors[:2]:
                        st.markdown(f"""
                        **Dr. {doc['full_name']}** - {doc['specialty']}
                        📍 {doc['clinic_name']}, {doc['city']}
                        💰 Fee: ${doc['consultation_fee']}
                        📞 Phone: {doc['phone']}
                        """)
                        if st.button(f"📅 Book with Dr. {doc['full_name']}", key=f"ref_doc_{doc['id']}"):
                            st.session_state.selected_doctor = doc
                            st.session_state.show_booking = True
                            st.rerun()
                        st.markdown("---")
            
            if "doctor" in prompt.lower() or "dr" in prompt.lower():
                doctor_match = re.search(r'(?:Dr\.?\s*)([A-Za-z]+(?:\s+[A-Za-z]+)?)', prompt, re.IGNORECASE)
                if doctor_match:
                    doctor_name = doctor_match.group(1)
                    doctor = search_doctor_by_name(doctor_name)
                    if doctor:
                        st.info(f"""
                        ### 📋 Complete Doctor Details:
                        **Name:** Dr. {doctor['full_name']}
                        **Specialty:** {doctor['specialty']}
                        **Clinic:** {doctor['clinic_name']}
                        **Address:** {doctor['clinic_address']}, {doctor['city']}
                        **Phone:** {doctor['phone']}
                        **Fee:** ${doctor['consultation_fee']}
                        **Available:** {doctor['available_days']} {doctor['available_time_start']}-{doctor['available_time_end']}
                        """)
                        if st.button(f"📅 Book with Dr. {doctor['full_name']}", key=f"doc_detail_{doctor['id']}"):
                            st.session_state.selected_doctor = doctor
                            st.session_state.show_booking = True
                            st.rerun()
        
        st.rerun()
    
    if st.session_state.get('show_booking') and st.session_state.get('selected_doctor'):
        show_booking_modal()

def show_booking_modal():
    doctor = st.session_state.selected_doctor
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(f"📅 Book Appointment with {doctor['full_name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Select Date", min_value=datetime.now())
    with col2:
        time_slot = st.time_input("Select Time")
    
    symptoms = st.text_area("Describe your symptoms", height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Booking", use_container_width=True):
            save_appointment(
                st.session_state.user_id, doctor['id'], doctor['full_name'],
                doctor['specialty'], date.strftime("%Y-%m-%d"), time_slot.strftime("%H:%M"),
                symptoms, ""
            )
            st.success(f"✅ Appointment requested with {doctor['full_name']}")
            st.session_state.show_booking = False
            st.session_state.selected_doctor = None
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_booking = False
            st.session_state.selected_doctor = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def nutrition():
    st.markdown('<div class="main-header"><h1>🍎 Smart Nutrition</h1><p>Get food advice based on your condition</p></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    from config import FOOD_RESTRICTIONS
    condition = st.selectbox("Select your condition", list(FOOD_RESTRICTIONS.keys()))
    if st.button("Get Food Advice"):
        st.info(f"🍽️ **Food Advice for {condition.title()}:**\n\n{FOOD_RESTRICTIONS[condition]}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def medications_page():
    st.markdown('<div class="main-header"><h1>💊 My Medications</h1><p>Auto-added from Dr. Well consultations</p></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    meds = get_medications(st.session_state.user_id)
    if meds:
        for m in meds:
            st.markdown(f"""
            <div class="card">
                <h3 style="color: #1e5f6b;">💊 {m['name']}</h3>
                <p><strong>Dosage:</strong> {m['dosage']}<br>
                <strong>Frequency:</strong> {m['frequency']}<br>
                <strong>Timing:</strong> {m['timing']}<br>
                <strong>Duration:</strong> {m['duration_days']} days<br>
                <strong>Food Restrictions:</strong> {m.get('food_restrictions', 'None')}<br>
                <strong>Prescribed by:</strong> {m['prescribed_by']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No medications yet. Consult Dr. Well for prescription!")

def appointments_page():
    st.markdown('<div class="main-header"><h1>📅 My Appointments</h1><p>View your scheduled appointments</p></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    apts = get_appointments(st.session_state.user_id)
    if apts:
        for a in apts:
            st.markdown(f"""
            <div class="card">
                <h3 style="color: #1e5f6b;">🏥 {a['doctor_name']}</h3>
                <p><strong>Specialty:</strong> {a['specialty']}<br>
                <strong>Date:</strong> {a['date']} at {a['time']}<br>
                <strong>Status:</strong> {a['status']}<br>
                <strong>Symptoms:</strong> {a['symptoms'][:100] if a['symptoms'] else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No appointments scheduled")

def doctors_list_page():
    st.markdown('<div class="main-header"><h1>👨‍⚕️ Find a Doctor</h1><p>Browse our network of verified specialists</p></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        specialty_filter = st.selectbox("Filter by Specialty", ["All"] + MEDICAL_SPECIALTIES)
    with col2:
        city_filter = st.text_input("Filter by City", placeholder="Enter city name")
    with col3:
        sort_by = st.selectbox("Sort by", ["Rating", "Experience", "Fee"])
    
    doctors = get_all_doctors()
    if specialty_filter != "All":
        doctors = [d for d in doctors if d.get('specialty') == specialty_filter]
    if city_filter:
        doctors = [d for d in doctors if city_filter.lower() in d.get('city', '').lower()]
    
    if sort_by == "Rating":
        doctors.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "Experience":
        doctors.sort(key=lambda x: x.get('experience_years', 0), reverse=True)
    elif sort_by == "Fee":
        doctors.sort(key=lambda x: x.get('consultation_fee', 0))
    
    st.markdown(f"### Found {len(doctors)} Doctors")
    
    for doctor in doctors:
        result = show_doctor_card(doctor)
        if result:
            st.session_state.selected_doctor = result
            st.session_state.show_booking = True
            st.rerun()
    
    if st.session_state.get('show_booking') and st.session_state.get('selected_doctor'):
        show_booking_modal()

def profile_page():
    user = get_user_by_id(st.session_state.user_id)
    st.markdown('<div class="main-header"><h1>👤 My Profile</h1><p>Update your information</p></div>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", use_container_width=False):
        st.session_state.page = "Dashboard"
        st.rerun()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", user.get('full_name', ''))
        email = st.text_input("Email", user.get('email', ''))
        phone = st.text_input("Phone", user.get('phone', ''))
    with col2:
        address = st.text_area("Address", user.get('address', ''))
        about = st.text_area("About", user.get('about', ''))
    
    if st.button("Update Profile", use_container_width=True):
        update_user_profile(st.session_state.user_id, full_name, phone, address, about)
        st.success("Profile updated successfully!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN APP ==========
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_about' not in st.session_state:
        st.session_state.show_about = True
    if 'show_booking' not in st.session_state:
        st.session_state.show_booking = False
    if 'selected_doctor' not in st.session_state:
        st.session_state.selected_doctor = None
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    if not st.session_state.logged_in:
        if st.session_state.show_about:
            show_about_page()
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("Get Started", use_container_width=True):
                    st.session_state.show_about = False
                    st.rerun()
            return
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            result = show_login_ui()
            if result:
                user = authenticate_user(result['username'], result['password'])
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['id']
                    st.session_state.user_type = user['user_type']
                    st.session_state.username = user['username']
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try: test_patient / test123")
        
        with tab2:
            result = show_signup_ui()
            if result:
                uid = create_user(
                    result['username'], result['email'], result['password'],
                    result['user_type'], result['full_name'], result.get('phone', ''), '', ''
                )
                if uid:
                    st.success("Account created! Please login.")
                    st.rerun()
                else:
                    st.error("Username or email exists")
        return
    
    if not is_profile_complete(st.session_state.user_id):
        if st.session_state.user_type == 'doctor':
            result = show_doctor_info_form()
            if result:
                save_doctor_info(
                    st.session_state.user_id, result['specialty'], result['qualification'],
                    result['experience'], result['fee'], result['days'], result['start'],
                    result['end'], result['clinic_name'], result['clinic_address'],
                    result['city'], result['state'], result['zip_code'], result['phone'], 
                    st.session_state.username, result['about']
                )
                st.success("Profile completed!")
                st.rerun()
        else:
            result = show_patient_info_form()
            if result:
                save_patient_info(
                    st.session_state.user_id, result['weight'], result['height'],
                    result['allergies'], result['blood_group'], result['about']
                )
                st.success("Profile completed!")
                st.rerun()
        return
    
    # ========== SIDEBAR - YAHAN PE render_sidebar() LIKHNA HAI ==========
    with st.sidebar:
        render_sidebar()  # <-- YAHAN PE YE LINE LIKHNI HAI
    
    # Page navigation based on session state
    if st.session_state.page == "Dashboard":
        dashboard()
    elif st.session_state.page == "Consultations":
        consultations()
    elif st.session_state.page == "Nutrition":
        nutrition()
    elif st.session_state.page == "Medications":
        medications_page()
    elif st.session_state.page == "Appointments":
        appointments_page()
    elif st.session_state.page == "Find Doctors":
        doctors_list_page()
    elif st.session_state.page == "Profile":
        profile_page()

if __name__ == "__main__":
    main()
