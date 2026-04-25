```markdown
# Dr. Well - AI Medical Assistant

[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Gemini AI](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlebard&logoColor=white)](https://deepmind.google/technologies/gemini/)

## 📋 Overview

**Dr. Well** is an advanced AI-powered Medical Assistant that provides instant healthcare guidance, symptom analysis, medication recommendations, and doctor referrals. Built with cutting-edge AI technology, it serves as a 24/7 virtual health companion for patients and a management platform for doctors.

## ✨ Features

### 🤖 AI Medical Consultation
- **Smart Symptom Analysis**: Real-time analysis of patient symptoms using Gemini AI
- **Instant Diagnosis**: Get immediate preliminary diagnosis
- **Treatment-First Approach**: AI first tries to treat with medicines before referring to specialists
- **Food Restrictions**: Each prescription includes dietary advice and restrictions
- **Emergency Detection**: Automatically detects critical conditions (chest pain, breathing difficulty)

### 💊 Smart Medication Management
- **Auto-Prescription**: AI-prescribed medications automatically added to patient's list
- **Dosage Tracking**: Track medicine dosage, frequency, and duration
- **Food Interactions**: Get food restrictions with each medication
- **Medication History**: Complete history of all prescribed medicines

### 👨‍⚕️ Complete Doctor Database
- **15+ Verified Specialists**: Cardiologists, Dermatologists, Neurologists, and more
- **Complete Doctor Profiles**: Includes name, specialty, clinic, address, timings, fees, phone, email
- **Search & Filter**: Find doctors by specialty, city, rating, experience, or fee
- **Direct Booking**: Book appointments directly through the platform

### 📅 Appointment System
- **Easy Scheduling**: Book appointments with preferred doctors
- **Status Tracking**: Track appointment status (Pending/Confirmed/Completed)
- **Symptom Recording**: Record symptoms when booking appointments
- **Appointment History**: Complete history of all appointments

### 🍎 Smart Nutrition
- **Condition-Based Advice**: Get food advice based on medical conditions
- **Dietary Restrictions**: For diabetes, blood pressure, heart disease, gastric issues, etc.
- **Quick Tips**: Healthy meal suggestions, weight management tips, immunity boosters

### 👤 User Management
- **Patient Registration**: Complete health profile (weight, height, blood group, allergies)
- **Doctor Registration**: Professional profile (specialty, qualification, experience, clinic, availability)
- **Secure Authentication**: Login/ Signup system with session management

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| AI Engine | Google Gemini 2.5 Flash |
| Database | SQLite3 |
| Language | Python 3.11+ |
| UI Framework | Custom CSS + Streamlit Components |

### Database Schema

```sql
users
├── id (PK)
├── username, email, password
├── user_type (patient/doctor)
├── full_name, phone, address
└── is_profile_complete

doctors_info
├── user_id (FK)
├── specialty, qualification
├── experience_years, consultation_fee
├── available_days, available_time
├── clinic_name, clinic_address, city, state
└── phone, email, rating

patients_info
├── user_id (FK)
├── weight, height
├── blood_group, allergies
└── medical_history

appointments
├── patient_id, doctor_id
├── doctor_name, specialty
├── date, time, status
└── symptoms, diagnosis

medications
├── user_id (FK)
├── name, dosage, frequency
├── duration_days, food_restrictions
└── prescribed_by

chat_history
├── user_id (FK)
├── role, content
├── diagnosis, session_id
└── created_at
```

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/dr-well.git
cd dr-well
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Step 5: Run the Application
```bash
streamlit run main.py
```

## 📁 Project Structure

```
dr-well/
├── main.py              # Main application entry point
├── database.py          # Database operations and schema
├── ui_components.py     # UI components and styling
├── config.py            # Configuration constants
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API keys)
├── runtime.txt          # Python version for deployment
└── README.md            # Project documentation
```

## 🎯 Usage Guide

### For Patients

1. **Sign Up / Login**
   - Create a patient account
   - Complete your health profile (weight, height, blood group, allergies)

2. **AI Consultation**
   - Go to "Consultations" from dashboard
   - Describe your symptoms in detail
   - Dr. Well will analyze and provide diagnosis, medicines, and food advice
   - Medicines are automatically added to your medications list

3. **Find Doctors**
   - Browse doctors by specialty, city, or rating
   - View complete doctor profiles including availability and fees
   - Book appointments directly

4. **Track Medications**
   - View all prescribed medicines with dosages and food restrictions
   - See active and completed medications

5. **Manage Appointments**
   - View upcoming and past appointments
   - Check appointment status

### For Doctors

1. **Sign Up / Login**
   - Create a doctor account
   - Complete professional profile (specialty, qualification, clinic, availability)

2. **Profile Management**
   - Update clinic information
   - Set consultation fees
   - Manage availability timings

## 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Patient | test_patient | test123 |
| Doctor | dr_smith | pass123 |
| Doctor | dr_johnson | pass123 |
| Doctor | dr_wilson | pass123 |
| Doctor | dr_patel | pass123 |
| Doctor | dr_garcia | pass123 |

## 🧪 AI Capabilities

### Symptoms Dr. Well Can Handle
- 🤒 **Fever** - Viral fever, high temperature
- 🤕 **Headache** - Migraine, tension headache
- 🤧 **Cold** - Common cold, runny nose
- 🫁 **Cough** - Dry cough, productive cough
- 🤢 **Stomach Issues** - Indigestion, gastric problems
- 💔 **Chest Pain** - Emergency detection (Cardiologist referral)
- 🫀 **Heart Issues** - Immediate specialist referral
- 🦴 **Body Pain** - General pain management

### Emergency Detection
Dr. Well automatically detects critical conditions:
- Chest pain radiating to arm/jaw
- Difficulty breathing
- Severe, unbearable pain
- "No improvement" after medication

## 📊 Sample Doctors Database

| Doctor | Specialty | City | Fee |
|--------|-----------|------|-----|
| Dr. Sarah Smith | Cardiologist | New York | $250 |
| Dr. Ahmed Khan | Cardiologist | Chicago | $200 |
| Dr. Michael Johnson | Dermatologist | Los Angeles | $180 |
| Dr. Emily Wilson | Neurologist | Chicago | $220 |
| Dr. Raj Patel | Orthopedic Surgeon | Houston | $300 |
| Dr. Maria Garcia | Pediatrician | Phoenix | $150 |

## 🛠️ Development

### Adding New Features
1. Update database schema in `database.py`
2. Add UI components in `ui_components.py`
3. Implement logic in `main.py`
4. Update configuration in `config.py`

### Customizing UI
- CSS styles are in `apply_custom_css()` function in `ui_components.py`
- Color scheme can be modified in the CSS styles

### Extending AI Capabilities
- Update `AI_RESPONSES` dictionary in `config.py`
- Modify `get_ai_medical_response()` function in `main.py`

## 🌐 Deployment

### Deploy on Streamlit Cloud

1. Push code to GitHub repository
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Set Python version to 3.11 in advanced settings
6. Add secret: `GOOGLE_API_KEY` = your_api_key
7. Deploy!

### Deploy Locally
```bash
streamlit run main.py --server.port 8501
```

## 📝 API Reference

### Google Gemini AI Integration
- **Model**: `gemini-2.5-flash`
- **Temperature**: 0.3
- **Max Tokens**: 1024
- **Response Length**: Under 60 words

### Database Connection
- **Type**: SQLite3
- **File**: `drwell.db` (auto-generated)
- **ORM**: Raw SQL with row_factory = sqlite3.Row

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**Dr. Well is an AI-powered informational tool only.** It does not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions, especially in emergencies.

## 🙏 Acknowledgments

- Google Gemini AI for powerful language model
- Streamlit for amazing web framework
- All doctors who contributed to the database
- Open source community

## 📞 Support

For issues, questions, or contributions:
- 📧 Email: support@drwell.com
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/yourusername/dr-well/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/dr-well/discussions)

## 🎯 Roadmap

- [ ] Video consultation integration
- [ ] Prescription PDF generation
- [ ] Medicine delivery integration
- [ ] Multi-language support (Urdu, Hindi)
- [ ] Mobile app version
- [ ] WhatsApp bot integration
- [ ] Voice input for symptoms
- [ ] Medical history tracking
- [ ] Lab test integration
- [ ] Insurance claim support

---

**Made with ❤️ for better healthcare** | Dr. Well Team 🚀
```
