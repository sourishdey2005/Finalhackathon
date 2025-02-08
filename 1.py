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
        body {
            font-family: 'Helvetica Neue', sans-serif;
            background-color: #f4f4f4;
            color: #333;
            line-height: 1.6;
        }

        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #007bff; /* Bootstrap primary color */
            margin-bottom: 15px;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1); /* Subtle text shadow */
        }

        a {
            color: #007bff;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        a:hover {
            color: #0056b3; /* Darker shade on hover */
        }

        /* Sidebar Styles */
        .sidebar .sidebar-content {
            background-color: #2c3e50; /* Darker background */
            color: #fff;
        }

        .sidebar h1, .sidebar h2, .sidebar h3, .sidebar h4, .sidebar h5, .sidebar h6 {
            color: #fff;
            text-shadow: none;
        }

        /* Input and Button Styles */
        input[type="text"], input[type="password"], input[type="number"], input[type="date"], input[type="time"],
        select, textarea {
            width: 100%;
            padding: 10px;
            margin: 5px 0 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 16px;
        }

        button {
            background-color: #007bff;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            transition: background-color 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: block; /* Make buttons full width */
            margin-bottom: 10px;
        }

        button:hover {
            background-color: #0056b3;
        }

        /* Success and Error Messages */
        .stSuccess {
            color: #155724;
            background-color: #d4edda;
            border-color: #c3e6cb;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
        }

        .stError {
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid transparent;
            border-radius: 4px;
        }

        /* Health Cards (Example for displaying health information) */
        .health-card {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #eee;
            transition: transform 0.2s ease-in-out;
        }

        .health-card:hover {
            transform: translateY(-5px); /* Slightly lift card on hover */
        }

        /* Add Glowing Effect to the title */
        .main-title {
            font-size: 2.5em;
            color: #4CAF50;
            text-shadow: 0 0 10px #4CAF50, 0 0 20px #4CAF50;
            text-align: center;
            animation: glow 2s infinite alternate;
            margin-bottom: 30px;
        }

        @keyframes glow {
            from {
                text-shadow: 0 0 5px #4CAF50, 0 0 10px #4CAF50;
            }
            to {
                text-shadow: 0 0 10px #4CAF50, 0 0 20px #4CAF50, 0 0 30px #388E3C;
            }
        }

        /* Animated Submit Button */
        .animated-button {
            background-color: #008CBA;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.16);
            transition: all 0.3s ease 0s;
        }

        .animated-button:hover {
            background-color: #0056b3;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
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
        if st.button("Register"):
            if register_user(username, password, aadhaar_number, address):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Please choose a different username.")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
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
            if st.button("Confirm Booking"):
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
            if st.button("Predict Health Risk"):
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
            if st.button("View Health Trends"):
                display_health_trends()

            st.header("More Wellness Tools")
            if st.button("Nearby Pharmacies"):
                user_location = "Placeholder User Location"
                suggest_nearby_pharmacies(user_location)
            if st.button("Mental Wellness Tips"):
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
        if st.button("Submit Referral"):
            refer_friend(username, referred_username)

        # Community Forum
        st.subheader("Community Forum")
        post = st.text_area("Share your thoughts or experiences:")
        if st.button("Post to Community"):
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
            if st.button("Export Health Data"):
                export_user_data(username)

        # Feedback Section
        if choice == "Feedback":
            st.subheader("Feedback")
            feedback = st.text_area("Please provide your feedback:")
            if st.button("Submit Feedback"):
                submit_feedback(username, feedback)

        # Health Articles and Resources
        if choice == "Health Articles":
            display_health_articles()

# Launch App
if __name__ == "__main__":
    init_db()  # Initialize the database once
    populate_doctors_and_hospitals()  # Populate doctors and hospitals
    main()
