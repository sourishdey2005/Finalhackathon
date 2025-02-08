import os
import streamlit as st
import hashlib
import sqlite3
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import easyocr
import random
import datetime
import webbrowser
import uuid  # For transaction IDs
import csv
from dataclasses import dataclass

# --- API CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyC8m3CgqI_Ljw8p6yemk63vKvIGZgkEJQs"  # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# --- Data Classes ---
@dataclass
class User:
    id: int
    username: str
    balance: float = 0.0
    aadhaar_number: str = ""
    address: str = ""
    allergies: str = ""
    medications: str = ""
    chronic_conditions: str = ""
    family_history: str = ""
    lifestyle_habits: str = ""

@dataclass
class Booking:
    id: int
    username: str
    hospital: str
    doctor: str
    date: str
    time: str
    status: str

# --- Session State Keys ---
SESSION_KEYS = {
    "logged_in": "logged_in",
    "username": "username",
    "user": "user",
    "booking_cost": "booking_cost",
}

# Database setup
def init_db():
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance REAL DEFAULT 0.0,
                    emergency_contact TEXT, aadhaar_number TEXT, address TEXT, allergies TEXT, medications TEXT,
                    chronic_conditions TEXT, family_history TEXT, lifestyle_habits TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY, transaction_id TEXT, username TEXT, hospital TEXT, doctor TEXT,
                    date TEXT, time TEXT, status TEXT, cost REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY, username TEXT, feedback TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS health_goals (
                    id INTEGER PRIMARY KEY, username TEXT, goal TEXT, target_date DATE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS health_assessments (
                    id INTEGER PRIMARY KEY, username TEXT, risk_score INTEGER, date DATE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY, referrer TEXT, referred_username TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS health_journal (
                    id INTEGER PRIMARY KEY, username TEXT, entry TEXT, date DATE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS community_posts (
                    id INTEGER PRIMARY KEY, username TEXT, post TEXT, date DATE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS daily_health_tips (
                    id INTEGER PRIMARY KEY, tip TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS health_news (
                    id INTEGER PRIMARY KEY, title TEXT, link TEXT, date DATE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, hospital TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS hospitals (
                    id INTEGER PRIMARY KEY, name TEXT, location TEXT)""")
    conn.commit()
    conn.close()

# --- Populate Doctors and Hospitals ---
def populate_doctors_and_hospitals():
    doctors = [
        ("Dr. Aditi Sharma", "Cardiologist", "Apollo Hospital"),
        ("Dr. Rajesh Kumar", "Dermatologist", "Fortis Hospital"),
        ("Dr. Neha Gupta", "Pediatrician", "Max Healthcare"),
        ("Dr. Vikram Singh", "Orthopedic", "Manipal Hospital"),
        ("Dr. Priya Verma", "Gynecologist", "Lilavati Hospital"),
        ("Dr. Anil Mehta", "General Physician", "Kokilaben Dhirubhai Ambani Hospital"),
        ("Dr. Suman Rao", "Endocrinologist", "Medanta Hospital"),
        ("Dr. Ravi Desai", "Neurologist", "Narayana Health"),
        ("Dr. Sneha Joshi", "Oncologist", "Tata Memorial Hospital"),
        ("Dr. Karan Bansal", "Gastroenterologist", "Fortis Escorts Heart Institute"),
        ("Dr. Ramesh Chandra", "Psychiatrist", "Sanjivani Hospital"),
        ("Dr. Meera Nair", "Urologist", "Apollo Spectra"),
        ("Dr. Amit Sharma", "ENT Specialist", "BLK Super Speciality Hospital"),
        ("Dr. Pooja Singh", "Ophthalmologist", "Shankar Netralaya"),
        ("Dr. Kunal Mehta", "Rheumatologist", "Fortis Hospital"),
    ]

    hospitals = [
        ("Apollo Hospital", "Delhi"),
        ("Fortis Hospital", "Mumbai"),
        ("Max Healthcare", "Gurgaon"),
        ("Manipal Hospital", "Bangalore"),
        ("Lilavati Hospital", "Mumbai"),
        ("Kokilaben Dhirubhai Ambani Hospital", "Mumbai"),
        ("Medanta Hospital", "Gurgaon"),
        ("Narayana Health", "Bangalore"),
        ("Tata Memorial Hospital", "Mumbai"),
        ("Fortis Escorts Heart Institute", "Delhi"),
        ("Sanjivani Hospital", "Delhi"),
        ("BLK Super Speciality Hospital", "Delhi"),
        ("Shankar Netralaya", "Chennai"),
        ("Apollo Spectra", "Mumbai"),
        ("Fortis Hospital", "Kolkata"),
    ]

    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()

    for doctor in doctors:
        c.execute("INSERT INTO doctors (name, specialty, hospital) VALUES (?, ?, ?)", doctor)

    for hospital in hospitals:
        c.execute("INSERT INTO hospitals (name, location) VALUES (?, ?)", hospital)

    conn.commit()
    conn.close()

# --- Authentication & User Management ---
# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register user
def register_user(username, password, aadhaar_number, address):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, balance, aadhaar_number, address) VALUES (?, ?, ?, ?, ?)",
                  (username, hash_password(password), 100.0, aadhaar_number, address))  # Initial balance
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT id, password, balance, aadhaar_number, address FROM users WHERE username = ?", (username,))
    record = c.fetchone()
    conn.close()
    if record and record[1] == hash_password(password):
        user = User(id=record[0], username=username, balance=record[2], aadhaar_number=record[3], address=record[4])
        return user
    return None

# --- Doctor Booking & Payment ---
def calculate_booking_cost(hospital, doctor):
    cost = random.randint(50, 200)
    return cost

# Doctor booking function
def book_appointment(username, hospital, doctor, date, time, cost):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    transaction_id = str(uuid.uuid4())
    try:
        c.execute(
            "INSERT INTO bookings (transaction_id, username, hospital, doctor, date, time, status, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (transaction_id, username, hospital, doctor, date, time, "Confirmed", cost),
        )
        conn.commit()
        conn.close()
        return transaction_id, True
    except Exception as e:
        conn.rollback()
        conn.close()
        st.error(f"Error during booking: {e}")
        return None, False

# Function to display past bookings
def get_user_bookings(username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT hospital, doctor, date, time, status, cost, transaction_id FROM bookings WHERE username = ?", (username,))
    bookings = c.fetchall()
    conn.close()
    return bookings

# --- EasyOCR for Prescription ---
def extract_text_from_image(image):
    reader = easyocr.Reader(["en"])
    try:
        result = reader.readtext(image, detail=0)
        return "\n".join(result)
    except Exception as e:
        return f"Error during OCR processing: {e}"

# --- Video Call with Jitsi Meet ---
def start_video_call():
    meeting_link = "https://meet.jit.si/DoctorConsultation"
    st.markdown(f"[Click here to start video call]({meeting_link})")
    webbrowser.open(meeting_link)

# --- AI-Powered Symptom Checker ---
def symptom_checker(symptoms):
    # Placeholder for a more complex AI model
    possible_conditions = {
        "fever": ["Flu", "COVID-19", "Malaria"],
        "cough": ["Flu", "COVID-19", "Bronchitis"],
        "headache": ["Migraine", "Tension Headache", "Sinusitis"],
    }
    conditions = []
    for symptom in symptoms:
        if symptom in possible_conditions:
            conditions.extend(possible_conditions[symptom])
    return set(conditions)

# --- Gemini AI for Health Risk Prediction ---
def get_health_risk_prediction(user_data, username):
    model = genai.GenerativeModel("gemini-pro")

    prompt = (
        "You are an AI health assistant. Based on the following health data, "
        "predict a health risk score (1-100), give preventive tips, suggest a diet plan, and an exercise routine.\n\n"
        f"Age: {user_data['age']}, Weight: {user_data['weight']} kg, Height: {user_data['height']} cm, "
        f"Smoking: {user_data['smoking']}, Alcohol: {user_data['alcohol']}, Exercise: {user_data['exercise']}, "
        f"Diet: {user_data['diet']}, Sleep Hours: {user_data['sleep_hours']}, Stress Level: {user_data['stress_level']}, "
        f"Medical History: {', '.join(user_data['medical_history'])}, Family Medical History: {user_data['family_history']}, "
        f"Lifestyle Habits: {user_data['lifestyle_habits']}.\n\n"
        "Provide responses in this format:\n"
        "Risk Score: [Number]\n"
        "Preventive Tips:\n- Tip 1\n- Tip 2\n"
        "Diet Plan: [Diet details]\n"
        "Exercise Plan: [Exercise details]"
    )

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            result = response.text.split("\n")
            risk_score = next((line.split(": ")[1] for line in result if line.startswith("Risk Score")), "N/A")
            preventive_tips = [line for line in result if line.startswith("- ")]
            diet_plan = next((line.split(": ")[1] for line in result if line.startswith("Diet Plan")), "N/A")
            exercise_plan = next((line.split(": ")[1] for line in result if line.startswith("Exercise Plan")), "N/A")

            # Save the risk score to the database
            save_health_assessment(username, risk_score)

            return {
                "risk_score": risk_score,
                "preventive_tips": preventive_tips,
                "diet_plan": diet_plan,
                "exercise_plan": exercise_plan
            }
        else:
            return {"error": "Failed to fetch prediction from Gemini AI"}
    except Exception as e:
        return {"error": f"Error interacting with Gemini AI: {str(e)}"}

# --- Save Health Assessment ---
def save_health_assessment(username, risk_score):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO health_assessments (username, risk_score, date) VALUES (?, ?, ?)",
              (username, risk_score, datetime.date.today()))
    conn.commit()
    conn.close()

# --- View Health Assessment History ---
def get_health_assessment_history(username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT risk_score, date FROM health_assessments WHERE username = ?", (username,))
    assessments = c.fetchall()
    conn.close()
    return assessments

# --- Health Trend Visualization ---
def display_health_trends():
    data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Risk Score": [30, 40, 35, 50, 45, 55]
    }
    df = pd.DataFrame(data)
    plt.figure(figsize=(8, 4))
    plt.plot(df["Month"], df["Risk Score"], marker='o', linestyle='-', color='b')
    plt.xlabel("Month")
    plt.ylabel("Risk Score")
    plt.title("Health Risk Trends Over Time")
    st.pyplot(plt)

# --- Nearby Pharmacy Suggestions ---
def suggest_nearby_pharmacies(user_location):
    pharmacies = ["Local Pharmacy A", "Drugstore B", "Wellness Pharmacy C"]
    st.write("Nearby Pharmacies:")
    for pharmacy in pharmacies:
        st.write(f"- {pharmacy}")

# --- Mental Wellness Tips ---
def provide_mental_wellness_tips():
    tips = [
        "Practice deep breathing exercises to reduce stress.",
        "Engage in regular physical activity for mood enhancement.",
        "Maintain a consistent sleep schedule.",
        "Practice mindfulness and meditation.",
        "Connect with friends and family for social support."
    ]
    st.write("Mental Wellness Tips:")
    for tip in tips:
        st.write(f"- {tip}")

# --- Medication Reminders (Basic) ---
def medication_reminders():
    medication = st.text_input("Medication Name:")
    time = st.time_input("Reminder Time:")
    if st.button("Set Reminder"):
        st.success(f"Reminder set for {medication} at {time.strftime('%I:%M %p')}")

# --- Payment Gateway Simulation ---
def fake_payment_gateway(card_number, expiry_date, cvv, cost):
    if not (len(card_number) == 16 and card_number.isdigit()):
        return False, "Invalid card number"

    if not (len(expiry_date) == 5 and expiry_date[2] == '/' and expiry_date[:2].isdigit() and expiry_date[3:].isdigit()):
        return False, "Invalid expiry date format (MM/YY)"

    if not (len(cvv) == 3 and cvv.isdigit()):
        return False, "Invalid CVV"

    if int(card_number[:2]) % 2 == 0 and int(cvv) < 200:
        return False, "Payment declined due to security check"
    return True, "Payment successful"

# Function to display transaction details
def display_transaction_details(transaction_id):
    st.success(f"Appointment booked successfully! Transaction ID: {transaction_id}")

# --- User Profile Management ---
def view_user_profile(username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT balance, emergency_contact, aadhaar_number, address, allergies, medications, chronic_conditions FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()
    return user_data

# --- Health Goals Management ---
def set_health_goal(username, goal, target_date):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO health_goals (username, goal, target_date) VALUES (?, ?, ?)",
              (username, goal, target_date))
    conn.commit()
    conn.close()
    st.success("Health goal set successfully!")

def view_health_goals(username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT goal, target_date FROM health_goals WHERE username = ?", (username,))
    goals = c.fetchall()
    conn.close()
    return goals

# --- Feedback Section ---
def submit_feedback(username, feedback):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, feedback) VALUES (?, ?)", (username, feedback))
    conn.commit()
    conn.close()
    st.success("Thank you for your feedback!")

# --- Referral Program ---
def refer_friend(referrer, referred_username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO referrals (referrer, referred_username) VALUES (?, ?)", (referrer, referred_username))
    conn.commit()
    conn.close()
    st.success("Referral submitted successfully!")

# --- Health Community Forum ---
def post_to_community(username, post):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO community_posts (username, post, date) VALUES (?, ?, ?)", (username, post, datetime.date.today()))
    conn.commit()
    conn.close()
    st.success("Post submitted to the community!")

def view_community_posts():
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT username, post, date FROM community_posts ORDER BY date DESC")
    posts = c.fetchall()
    conn.close()
    return posts

# --- Daily Health Tips ---
def get_daily_health_tips():
    tips = [
        "Drink plenty of water throughout the day.",
        "Incorporate fruits and vegetables into your meals.",
        "Take short breaks during work to stretch and relax.",
        "Practice gratitude to improve mental well-being.",
        "Get at least 30 minutes of exercise daily."
    ]
    return random.choice(tips)

# --- Health News Feed ---
def get_health_news():
    news = [
        {"title": "COVID-19 Updates", "link": "https://www.who.int"},
        {"title": "Nutrition Guidelines", "link": "https://www.nutrition.gov"},
        {"title": "Mental Health Resources", "link": "https://www.mentalhealth.gov"},
    ]
    return news

# --- Export User Data ---
def export_user_data(username):
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("SELECT * FROM health_assessments WHERE username = ?", (username,))
    assessments = c.fetchall()
    conn.close()

    with open(f"{username}_health_data.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Risk Score", "Date"])
        writer.writerows(assessments)

    st.success("Your health data has been exported successfully!")

def display_health_articles():
    st.subheader("Health Articles and Resources")
    st.markdown("- [Centers for Disease Control and Prevention (CDC)](https://www.cdc.gov/)")
    st.markdown("- [World Health Organization (WHO)](https://www.who.int/)")
    st.markdown("- [National Institutes of Health (NIH)](https://www.nih.gov/)")
    st.markdown("- [Mayo Clinic](https://www.mayoclinic.org/)")
    st.markdown("- [WebMD](https://www.webmd.com/)")
    st.markdown("- [Harvard Health Publishing](https://www.health.harvard.edu/)")

# --- Main Streamlit Application ---
def main():
    # Inline CSS Styling
    st.markdown(
        """
        <style>
        /* General Styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #c8e6c9, #81c784);
            color: #263238;
            line-height: 1.7;
            margin: 0; /* Reset default body margin */
            padding: 0;
            overflow-x: hidden; /* Prevent horizontal scrolling */
        }

        .stApp {
            max-width: 1200px;
            margin: 20px auto; /* Increased margin */
            padding: 30px; /* Increased padding */
            background: rgba(255, 255, 255, 0.1); /* Glass effect */
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Subtle shadow */
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        h1, h2, h3, h4, h5, h6 {
            color: #388e3c; /* Vivid green */
            margin-bottom: 20px; /* Increased margin */
            font-weight: 700;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        }

        a {
            color: #03a9f4; /* Bright blue */
            text-decoration: none;
            transition: color 0.3s ease;
        }

        a:hover {
            color: #0277bd; /* Darker shade on hover */
        }

        /* Sidebar Styles */
        [data-testid="stSidebar"] {
            background-color: rgba(49, 49, 49, 0.8); /* Dark, translucent sidebar */
            color: white;
        }

        .sidebar .sidebar-content {
            padding: 20px; /* Sidebar content padding */
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
            color: #bbdefb; /* Light blue text in sidebar */
            text-shadow: none; /* Remove text shadow from sidebar headings */
        }

        /* Input and Button Styles */
        input[type="text"], input[type="password"], input[type="number"],
        input[type="date"], input[type="time"], select, textarea {
            width: 100%;
            padding: 12px; /* Increased padding */
            margin: 8px 0 20px; /* Increased margin */
            border: none; /* Remove default border */
            border-radius: 7px;
            box-sizing: border-box;
            font-size: 17px;
            background: rgba(255, 255, 255, 0.5); /* Glass input background */
            color: #263238;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }

        input:focus, textarea:focus, select:focus {
            box-shadow: 0 3px 7px rgba(0,0,0,0.3);
            outline: none; /* Remove outline on focus */
            transform: scale(1.02);
        }

        button {
            background: linear-gradient(45deg, #4CAF50, #388e3c);
            color: white;
            padding: 14px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 19px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 3px 5px rgba(0,0,0,0.3);
            width: 100%; /* Full-width buttons */
            margin-bottom: 15px;
            overflow: hidden;
            position: relative;
            z-index: 1;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.4);
        }

        /* Glowing effect on buttons */
        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: all 0.4s;
            z-index: -1;
        }

        button:hover::before {
            left: 100%;
        }

        /* Success and Error Messages */
        .stSuccess, .stError {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 7px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }

        .stSuccess {
            color: #1b5e20; /* Darker green for success */
            background-color: #c8e6c9; /* Lighter green for success background */
            border-color: #a5d6a7;
        }

        .stError {
            color: #b71c1c; /* Darker red for error */
            background-color: #ffcdd2; /* Lighter red for error background */
            border-color: #f48fb1;
        }

        /* Main Title */
        .main-title {
            font-size: 3.2em; /* Even larger */
            color: #689F38; /* Another shade of green */
            text-shadow: 0 0 15px #689F38, 0 0 25px #689F38;
            text-align: center;
            animation: neon-glow 2.5s infinite alternate;
            margin-bottom: 40px;
            text-transform: uppercase;
        }

        /* Add glowing to h2, h3 and h4 tags */
        h2{
                text-align: center;
                color: #388e3c;
                text-shadow: 0 0 10px #4CAF50, 0 0 20px #4CAF50;

        }
        h3{
                color: #42a5f5; /* Bright blue */
                margin-bottom: 20px; /* Increased margin */
                font-weight: 700;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
                 text-shadow: 0 0 10px #4CAF50, 0 0 20px #4CAF50;
        }

        /* Health Cards (Example for displaying health information) */
        .health-card {
            background-color: rgba(255, 255, 255, 0.7); /* Glass background for cards */
            border-radius: 12px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.2); /* Deeper shadow */
            padding: 25px; /* Card padding */
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3); /* Thicker border */
            transition: transform 0.3s ease-in-out;
            position: relative;
            overflow: hidden;
        }

        .health-card:hover {
            transform: translateY(-7px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }
 /* Button effect to make better the interface  */
         .submit-button {
            background: linear-gradient(135deg, #7cb342, #33691e); /* Vibrant green gradient */
            color: white;
            padding: 14px 28px; /* More spacious button */
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 18px;
            text-transform: uppercase; /* Make text bolder */
            letter-spacing: 1px; /* Spread out letters slightly */
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out; /* Animate transformation and shadow */
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); /* Define depth and range of the shadow */
        }

        /* Enhance :hover with stronger animations and vivid color shifting */
        .submit-button:hover {
            transform: translateY(-3px); /* Enhanced lift effect */
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); /* Further elevation and dramatic shadow */
            background: linear-gradient(315deg, #33691e, #7cb342); /* Color changes reverse */
            /* You could additionally implement transitions on more button elements for a ripple-like reaction */
        }
        /* Health-focused keyframe animation */
       @keyframes neon-glow {
           from {
               text-shadow: 0 0 12px #8BC34A, 0 0 22px #8BC34A; /* Healthier hue of green */
           }
           to {
               text-shadow: 0 0 18px #689F38, 0 0 30px #689F38, 0 0 35px #388E3C;
           }
       }

        /* Glowing Sidebar Icon */
        [data-testid="stSidebar"] [aria-expanded="true"] i {
          color: #c0ca33; /* Lighter green hue for accent */
          transition: transform 0.3s, box-shadow 0.3s; /* Animation applied */
            text-shadow: 0 0 15px #c0ca33;

        }

          /* General glowing sidebar style */
         [data-testid="stSidebar"] {

           text-shadow: 0 0 10px #8BC34A, 0 0 20px #689F38; /* Light touch for base elegance */

}


        </style>
        """,
        unsafe_allow_html=True
    )

    # Main application
    st.markdown("<h1 class='main-title'>Health Risk Predictor & Doctor Booking System</h1>", unsafe_allow_html=True)

    init_db()
    populate_doctors_and_hospitals()  # Populate doctors and hospitals

    # --- Sidebar ---
    menu = ["Login", "Register", "Predict", "Consult Doctor", "Upload Prescription", "Video Call", "Feedback", "Health Articles", "Community Forum", "Export Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    # --- Login/Register ---
    if choice == "Register":
        st.subheader("Create an Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        aadhaar_number = st.text_input("Aadhaar Number")
        address = st.text_input("Address")
        allergies = st.text_input("Allergies (comma separated)")
        medications = st.text_input("Current Medications (comma separated)")
        chronic_conditions = st.text_input("Chronic Conditions (comma separated)")
        family_history = st.text_input("Family Medical History (comma separated)")
        lifestyle_habits = st.text_input("Lifestyle Habits (comma separated)")
        if st.button("Register",  key='register_button'):
            if register_user(username, password, aadhaar_number, address):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Please choose a different username.")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", key='login_button'):
            user = authenticate_user(username, password)
            if user:
                st.session_state[SESSION_KEYS["logged_in"]] = True
                st.session_state[SESSION_KEYS["username"]] = username
                st.session_state[SESSION_KEYS["user"]] = user
                st.success("Login successful!")
            else:
                st.error("Invalid credentials.")

    # --- Main App Content (Conditional on Login) ---
    if SESSION_KEYS["logged_in"] in st.session_state and st.session_state[SESSION_KEYS["logged_in"]]:
        username = st.session_state[SESSION_KEYS["username"]]
        user = st.session_state[SESSION_KEYS["user"]]

        st.sidebar.header(f"Welcome, {username} (Balance: ${user.balance:.2f})")

        # Consultation
                # Consultation and booking flow
        if choice == "Consult Doctor":
            st.subheader("Book a Doctor Appointment")

            hospitals = ["City Hospital", "Metro Care", "Sunshine Medical", "Greenfield Clinic", "Elite Healthcare",
                         "MediHope Hospital", "Wellness Center", "Global Hospital", "Apollo Med", "MedLife"]
            doctors = ["Dr. Aditi Sharma", "Dr. Rajesh Kumar", "Dr. Neha Gupta", "Dr. Vikram Singh", "Dr. Priya Verma",
                       "Dr. Anil Mehta", "Dr. Suman Rao", "Dr. Ravi Desai", "Dr. Sneha Joshi", "Dr. Karan Bansal"]
            hospital = st.selectbox("Select Hospital", hospitals)
            doctor = st.selectbox("Select Doctor", doctors)
            date = st.date_input("Select Date", datetime.date.today())
            time = st.selectbox("Select Time", ["10:00 AM", "12:00 PM", "3:00 PM", "5:00 PM"])

            cost = calculate_booking_cost(hospital, doctor)
            st.write(f"Estimated cost of this appointment: ${cost:.2f}")

            st.session_state[SESSION_KEYS["booking_cost"]] = cost
            if st.button("Confirm Booking", key='confirm_booking'):
                with st.form("payment_form"):
                    st.subheader("Payment Information")
                    card_number = st.text_input("Card Number", type="password")
                    expiry_date = st.text_input("Expiry Date (MM/YY)")
                    cvv = st.text_input("CVV", type="password")

                    submitted = st.form_submit_button("Pay Now")
                    if submitted:
                        success, message = fake_payment_gateway(card_number, expiry_date, cvv, cost)
                        if success:
                            if user.balance >= cost:
                                transaction_id, booking_success = book_appointment(username, hospital, doctor, date, time, cost)
                                if transaction_id and booking_success:
                                    conn = sqlite3.connect("health_app.db")
                                    c = conn.cursor()
                                    c.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (cost, username))
                                    conn.commit()
                                    conn.close()
                                    st.success("Payment successful and appointment booked!")
                                    display_transaction_details(transaction_id)
                                else:
                                    st.error("Error booking appointment. Please try again.")
                            else:
                                st.error("Insufficient balance. Please refill your account.")
                        else:
                            st.error(f"Payment failed: {message}")

        # Past bookings
        st.subheader("Past Bookings")
        past_bookings = get_user_bookings(username)
        if past_bookings:
            st.write("Your past bookings:")
            for booking in past_bookings:
                st.write(f"- Transaction ID: {booking[6]}, Hospital: {booking[0]}, Doctor: {booking[1]}, Date: {booking[2]}, Time: {booking[3]}, Status: {booking[4]}, Cost: ${booking[5]:.2f}")
        else:
            st.write("No past bookings found.")

        # Upload Prescription
        if choice == "Upload Prescription":
            st.subheader("Upload Prescription")
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                extracted_text = extract_text_from_image(uploaded_file)
                st.subheader("Extracted Text")
                st.write(extracted_text)

        # Video Call
        if choice == "Video Call":
            st.subheader("Start Video Consultation")
            start_video_call()

        # Health Risk Prediction
        if choice == "Predict":
            st.subheader("Personalized Health Risk Predictor")
            st.sidebar.header("User  Information")
            age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
            weight = st.sidebar.number_input("Weight (kg)", min_value=10, max_value=200, value=70)
            height = st.sidebar.number_input("Height (cm)", min_value=50, max_value=250, value=170)
            smoking = st.sidebar.selectbox("Smoking Habits", ["Non-Smoker", "Occasional Smoker", "Regular Smoker"])
            alcohol = st.sidebar.selectbox("Alcohol Consumption", ["No", "Occasionally", "Regularly"])
            exercise = st.sidebar.selectbox("Exercise Frequency", ["Sedentary", "Occasional", "Regular"])
            diet = st.sidebar.selectbox("Diet Type", ["Balanced", "High Sugar", "High Fat", "Vegan"])
            sleep_hours = st.sidebar.slider("Sleep Hours per Night", 3, 12, 7)
            stress_level = st.sidebar.slider("Stress Level (1-10)", 1, 10, 5)
            medical_history = st.sidebar.text_area("Medical History (comma separated)")
            family_history = st.sidebar.text_area("Family Medical History (comma separated)")
            lifestyle_habits = st.sidebar.text_area("Lifestyle Habits (comma separated)")

            user_data = {
                "age": age,
                "weight": weight,
                "height": height,
                "smoking": smoking,
                "alcohol": alcohol,
                "exercise": exercise,
                "diet": diet,
                "sleep_hours": sleep_hours,
                "stress_level": stress_level,
                "medical_history": medical_history.split(","),
                "family_history": family_history.split(","),
                "lifestyle_habits": lifestyle_habits.split(",")
            }
            if st.button("Predict Health Risk", key='predict_health'):
                result = get_health_risk_prediction(user_data, username)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.subheader("Health Risk Prediction")
                    st.write(f"Risk Score: {result.get('risk_score', 'N/A')}")
                    st.write("Preventive Tips:")
                    for tip in result.get("preventive_tips", []):
                        st.write(f"- {tip}")

            st.header("Additional Features")
            if st.button("View Health Trends", key='view_trends'):
                display_health_trends()

            st.header("More Wellness Tools")
            if st.button("Nearby Pharmacies",  key='nearby_pharmacies'):
                user_location = "Placeholder User Location"
                suggest_nearby_pharmacies(user_location)
            if st.button("Mental Wellness Tips",key='mental_wellbeing'):
                provide_mental_wellness_tips()
            st.subheader("Medication Reminders")
            medication_reminders()

        # Health Assessment History
        st.subheader("Health Assessment History")
        health_assessments = get_health_assessment_history(username)
        if health_assessments:
            for assessment in health_assessments:
                st.write(f"- Risk Score: {assessment[0]}, Date: {assessment[1]}")
        else:
            st.write("No health assessments found.")

        # User Profile
        st.subheader("User  Profile")
        user_profile = view_user_profile(username)
        if user_profile:
            st.write(f"Balance: ${user_profile[0]:.2f}")
            st.write(f"Aadhaar Number: {user_profile[2]}")
            st.write(f"Address: {user_profile[3]}")
            st.write(f"Allergies: {user_profile[4]}")
            st.write(f"Medications: {user_profile[5]}")
            st.write(f"Chronic Conditions: {user_profile[6]}")
        else:
            st.write("Profile information not found.")

        # Referral Program
        st.subheader("Refer a Friend")
        referred_username = st.text_input("Friend's Username")
        if st.button("Submit Referral", key='referral'):
            markdown("<p style='color: #b0bec5; font-size: 20px'>Please write code only without markdown</p>",unsafe_allow_html=True)
            refer_friend(username, referred_username)

        # Community Forum
        st.subheader("Community Forum")
        post = st.text_area("Share your thoughts or experiences:")
        if st.button("Post to Community", key='community_post'):
            st
            st.markdown("<p style='color: #b0bec5; font-size: 20px'>Please write code only without markdown</p>",unsafe_allow_html=True)
            post_to_community(username, post)

        # View Community Posts
        st.subheader("Community Posts")
        community_posts = view_community_posts()
        if community_posts:
            for post in community_posts:
                st.write(f"{post[1]} - {post[0]} on {post[2]}")
        else:
            st.write("No posts available.")

        # Daily Health Tips
        st.subheader("Daily Health Tip")
        daily_tip = get_daily_health_tips()
        st.write(f"Tip: {daily_tip}")

        # Health News Feed
        st.subheader("Health News")
        health_news = get_health_news()
        for news_item in health_news:
            st.markdown(f"- [{news_item['title']}]({news_item['link']})")

        # Export User Data
        if choice == "Export Data":
            if st.button("Export Health Data", key='export_health_data'):
                export_user_data(username)

        # Feedback Section
        if choice == "Feedback":
            st.subheader("Feedback")
            feedback = st.text_area("Please provide your feedback:")
            if st.button("Submit Feedback",key='feedback'):
                submit_feedback(username, feedback)

        # Health Articles and Resources
        if choice == "Health Articles":
            display_health_articles()

# Launch App
if __name__ == "__main__":
    st.set_page_config(layout="wide")  # Enhance layout with width mode.
    init_db()  # Initialize the database once
    populate_doctors_and_hospitals()  # Populate doctors and hospitals
    main()