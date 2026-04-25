# main.py
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import time
import uuid
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os

# Load environment variables
load_dotenv()

# Configure LangChain with Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.5,
    max_tokens=1024
)

from config import *
from database import *
from ui_components import *

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
    """Get response from LangChain Google Gemini with doctor database access"""
    
    # Get complete doctors database
    doctors_text = get_all_doctors_text()
    
    # Get patient medications
    patient_meds = get_medications(st.session_state.user_id)
    meds_text = "\n".join([f"- {m['name']}: {m['dosage']}, {m['frequency']}" for m in patient_meds]) if patient_meds else "No active medications"
    
    # Get conversation context
    memory_text = ""
    for msg in chat_history[-8:]:
        memory_text += f"{msg['role']}: {msg['content'][:150]}\n"
    
    # Create system prompt
    system_prompt = f"""You are Dr. Well, a smart and caring AI medical assistant. You have COMPLETE access to all doctors in our database.

🏥 COMPLETE DOCTORS DATABASE (You MUST use this to answer any doctor-related questions):
{doctors_text}

PATIENT INFO:
- Current medications: {meds_text}

CONVERSATION MEMORY:
{memory_text}

IMPORTANT RULES - FOLLOW STRICTLY:

1. TREATMENT FIRST APPROACH:
   - FIRST try to treat with medicine and home remedies
   - Give specific medicine names, dosage, timing, and food restrictions
   - ONLY refer to specialist if patient doesn't improve or symptoms are severe

2. WHEN TO REFER TO DOCTOR:
   - If patient says "no improvement", "still in pain", "medicine not working"
   - If symptoms are severe (chest pain radiating to arm/jaw, difficulty breathing)
   - If condition needs specialist care

3. DOCTOR INFORMATION (Use exact database info):
   - When patient asks about ANY doctor, give COMPLETE details from database
   - Include: Full name, Specialty, Clinic, City, Fee, Phone, Available days/timings

4. MEDICINE PRESCRIPTION:
   - Give: name, dosage, frequency, timing (before/after food)
   - Also give FOOD RESTRICTIONS (what to eat/avoid)
   - Tell how many days to take

5. RESPONSE STYLE:
   - Keep response UNDER 60 words
   - Be friendly and caring
   - End with "Take care! - Dr. Well"

Now respond to the patient's message:
"""
    
    # Create messages for LangChain
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    try:
        response = llm.invoke(messages)
        reply = response.content.strip()
        
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
    if "appointment" in msg_lower or "kab" in msg_lower:
        return "Please call the clinic directly to check appointment availability. Their phone number is in the doctor's details above. Take care! - Dr. Well"
    
    # Chest pain emergency
    if "chest" in msg_lower and "pain" in msg_lower:
        return "⚠️ Chest pain needs attention! If pain is sharp or spreading to arm/jaw, please see a Cardiologist immediately. Dr. Sarah Smith or Dr. Ahmed Khan can help. Take care! - Dr. Well"
    
    return "Please tell me more about your symptoms so I can help you better. Take care! - Dr. Well"

def extract_medication_from_response(response_text, user_message):
    """Extract medication info from AI response and auto-add to database"""
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
    st.markdown(f'<div class="main-header"><h1>🤖 Welcome, {user.get("full_name", "User")}!</h1><p>Your AI Medical Assistant</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="card"><h3>💊 My Medications</h3>', unsafe_allow_html=True)
        meds = get_medications(st.session_state.user_id)
        if meds:
            for m in meds[:3]:
                st.write(f"• {m['name']} - {m['dosage']}")
        else:
            st.info("No active medications")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3>📅 Upcoming Appointments</h3>', unsafe_allow_html=True)
        apts = get_appointments(st.session_state.user_id)
        if apts:
            for a in apts[:3]:
                st.write(f"• Dr. {a['doctor_name']} - {a['date']}")
        else:
            st.info("No upcoming appointments")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card"><h3>👨‍⚕️ Doctors Available</h3>', unsafe_allow_html=True)
        doctors = get_all_doctors()
        st.metric("Total Doctors", len(doctors))
        st.markdown('</div>', unsafe_allow_html=True)

def consultations():
    st.markdown('<div class="main-header"><h1>🤖 AI Medical Consultation</h1><p>Dr. Well will FIRST try to treat you, then refer to specialist if needed</p></div>', unsafe_allow_html=True)
    
    st.info("""
    💡 **How Dr. Well works:**
    1. 🩺 **Listens to your symptoms**
    2. 💊 **Prescribes medicine with food tips** 
    3. ✅ **If medicine works** - Continue treatment
    4. 🏥 **If no improvement** - Refers to specialist doctor
    5. 📋 **Answers any doctor questions** - Complete details from database
    """)
    
    # Initialize session
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = create_chat_session(st.session_state.user_id)
        st.session_state.chat_messages = []
    
    # Load chat history
    if 'chat_messages' not in st.session_state or len(st.session_state.chat_messages) == 0:
        saved_messages = get_chat_history(st.session_state.user_id, st.session_state.chat_session_id)
        st.session_state.chat_messages = [{"role": msg['role'], "content": msg['content']} for msg in saved_messages]
    
    # Sidebar for chat sessions
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
    
    # Display chat messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input with streaming
    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🩺 Dr. Well is analyzing..."):
                response = get_ai_medical_response(prompt, st.session_state.chat_messages, st.session_state.chat_session_id)
                
                # Stream response
                message_placeholder = st.empty()
                full_response = ""
                for chunk in stream_response(response):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            
            # Save to database
            st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
            save_chat_message(st.session_state.user_id, st.session_state.chat_session_id, "assistant", full_response)
            
            # Auto-add medication if detected
            med_added = extract_medication_from_response(full_response, prompt)
            if med_added:
                st.success(f"💊 {med_added} added to your medications list with food advice!")
            
            # Check for doctor recommendation
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
                        🕒 Available: {doc['available_days']} {doc['available_time_start']}-{doc['available_time_end']}
                        """)
                        if st.button(f"📅 Book with Dr. {doc['full_name']}", key=f"ref_doc_{doc['id']}"):
                            st.session_state.selected_doctor = doc
                            st.session_state.show_booking = True
                            st.rerun()
                        st.markdown("---")
            
            # Handle doctor questions
            if "doctor" in prompt.lower() or "dr" in prompt.lower():
                import re
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
                        **Address:** {doctor['clinic_address']}, {doctor['city']}, {doctor['state']}
                        **Phone:** {doctor['phone']}
                        **Email:** {doctor['email']}
                        **Fee:** ${doctor['consultation_fee']}
                        **Available Days:** {doctor['available_days']}
                        **Available Time:** {doctor['available_time_start']} - {doctor['available_time_end']}
                        **Experience:** {doctor['experience_years']} years
                        **Qualification:** {doctor['qualification']}
                        **Rating:** ⭐ {doctor['rating']} ({doctor['total_reviews']} reviews)
                        """)
                        if st.button(f"📅 Book Appointment with Dr. {doctor['full_name']}", key=f"doc_detail_{doctor['id']}"):
                            st.session_state.selected_doctor = doctor
                            st.session_state.show_booking = True
                            st.rerun()
            
            # Check for emergency
            emergency_keywords = ["chest", "heart", "difficulty breathing", "unbearable", "severe pain", "no improvement", "still in pain"]
            if any(kw in prompt.lower() for kw in emergency_keywords) and "no improvement" in full_response.lower():
                st.error("🚨 **Dr. Well recommends seeing a specialist immediately!** Please book an appointment with the recommended doctor above.")
        
        st.rerun()
    
    # Booking modal
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
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    from config import FOOD_RESTRICTIONS
    condition = st.selectbox("Select your condition", list(FOOD_RESTRICTIONS.keys()))
    if st.button("Get Food Advice"):
        st.info(f"🍽️ **Food Advice for {condition.title()}:**\n\n{FOOD_RESTRICTIONS[condition]}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def medications_page():
    st.markdown('<div class="main-header"><h1>💊 My Medications</h1><p>Auto-added from Dr. Well consultations</p></div>', unsafe_allow_html=True)
    
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
    
    with st.sidebar:
        user = get_user_by_id(st.session_state.user_id)
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 50px;">{'👨‍⚕️' if st.session_state.user_type == 'doctor' else '👤'}</div>
            <h3 style="color: white;">{user.get('full_name', 'User')}</h3>
            <p style="color: #90c9d9;">{st.session_state.user_type.title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        menu_options = ["Dashboard", "Consultations", "Nutrition", "Medications", "Appointments", "Find Doctors", "Profile"]
        
        selected = option_menu(
            None, menu_options,
            icons=["speedometer2", "chat-dots", "apple", "capsule", "calendar-check", "search", "person"],
            menu_icon="hospital", default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "#90c9d9", "font-size": "20px"},
                "nav-link": {"color": "white", "font-size": "14px", "padding": "10px 15px", "--hover-color": "rgba(255,255,255,0.1)"},
                "nav-link-selected": {"background": "#2c7a8a", "color": "white", "font-weight": "600"}
            }
        )
        
        st.markdown("---")
        db_status = check_database()
        st.caption(f"📊 {db_status['users']} users | {db_status['doctors']} doctors")
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if selected == "Dashboard":
        dashboard()
    elif selected == "Consultations":
        consultations()
    elif selected == "Nutrition":
        nutrition()
    elif selected == "Medications":
        medications_page()
    elif selected == "Appointments":
        appointments_page()
    elif selected == "Find Doctors":
        doctors_list_page()
    elif selected == "Profile":
        profile_page()

if __name__ == "__main__":
    main()
