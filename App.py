import streamlit as st
import hashlib
import time
from datetime import date
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from hashlib import sha256
import os
from datetime import datetime, date, timedelta

st.set_page_config(layout="wide")

# Path for the Excel file
EXCEL_FILE = "users.xlsx"

def load_users():
    try:
        # Load the Excel file
        df = pd.read_excel(EXCEL_FILE)

        # Ensure column names are stripped of whitespace
        df.columns = df.columns.str.strip()

        # Check if "Username" column exists
        if "Username" not in df.columns:
            raise KeyError("The 'Username' column is missing from the Excel file!")

        return df.set_index("Username").to_dict(orient="index")

    except (FileNotFoundError, KeyError):
        # If file is missing or "Username" column is missing, create a new file
        df = pd.DataFrame(columns=[
            "Username", "Password", "Name", "DOB", 
            "Security_Question", "Security_Answer", "Last_Attendance"
        ])
        df.to_excel(EXCEL_FILE, index=False)
        return {}

# Example usage
users = load_users()
print(users)  # Debugging: Print loaded users


# Function to save user data to Excel
def save_users(users_dict):
    df = pd.DataFrame.from_dict(users_dict, orient="index").reset_index()
    if len(df.columns) == 7:  # Ensure correct column count before renaming
        df.columns = ["Username", "Password", "Name", "DOB", "Security_Question", "Security_Answer", "Last_Attendance"]
    else:
        print("Column mismatch! Found columns:", df.columns)  # Debugging step

    df.to_excel(EXCEL_FILE, index=False)

# Function to hash passwords
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Function to check login credentials
def check_login(username, password, users):
    if username in users and users[username]["Password"] == hash_password(password):
        return True
    return False

# Function to add new users
def add_user(username, password, name, dob, question, answer, users):
    if username not in users:
        users[username] = {
            "Password": hash_password(password),
            "Name": name,
            "DOB": dob,
            "Security_Question": question,
            "Security_Answer": hash_password(answer),
            "Last_Attendance": None
        }
        save_users(users)

# Function to reset password
def reset_password(username, question, answer, new_password, users):
    if username in users:
        if users[username]["Security_Question"] == question and users[username]["Security_Answer"] == hash_password(answer):
            users[username]["Password"] = hash_password(new_password)
            save_users(users)
            return True
    return False

# Function to mark attendance
def mark_attendance(username, users):
    today = str(date.today())
    if users[username]["Last_Attendance"] != today:
        users[username]["Last_Attendance"] = today
        save_users(users)
        return True  # Attendance marked successfully
    return False  # Attendance already marked today

# Initialize the app
users = load_users()

if 'login' not in st.session_state:
    st.session_state.login = False
    st.session_state.current_user = None

if not st.session_state.login:
    st.title("Login/Registration")
    option = st.radio("Select an option", ["Login", "Registration"])

    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_login(username, password, users):
                st.session_state.login = True
                st.session_state.current_user = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
        
        # Forgot Password Section
        if st.checkbox("Forgot Password"):
            st.subheader("Forgot Password")
            reset_user = st.text_input("Enter your username for password reset")
            selected_question = st.selectbox("Select your Security Question", [
                "What is your favorite subject?",
                "What is your favorite colour?",
                "What is your favorite place?",
                "Where do you live?",
                "What is your favorite movie?",
                "What is your favorite food?",
                "What is your childhood nickname?"
            ])
            answer = st.text_input("Your Answer", type="password")
            new_password = st.text_input("New Password", type="password")
            if st.button("Reset Password"):
                if reset_password(reset_user, selected_question, answer, new_password, users):
                    st.success("Password reset successfully! Please login.")
                else:
                    st.error("Invalid security question or answer!")

    elif option == "Registration":
        username = st.text_input("Username")
        name = st.text_input("Full Name")
        dob = st.date_input(
            "Date of Birth",
            value=datetime.now() - timedelta(days=30 * 365),  # Default: 30 years ago
            min_value=datetime.now() - timedelta(days=80 * 365),  # Minimum: 80 years ago
            max_value=datetime.now()  # Maximum: Today
        )
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        question = st.selectbox("Select a Security Question", [
            "What is your favorite subject?",
            "What is your favorite colour?",
            "What is your favorite place?",
            "Where do you live?",
            "What is your favorite movie?",
            "What is your favorite food?",
            "What is your childhood nickname?"
        ])
        answer = st.text_input("Answer to Security Question")
        if st.button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif username in users:
                st.error("Username already exists!")
            else:
                add_user(username, password, name, dob, question, answer, users)
                st.success("Registration successful! Please login.")

else:
    st.set_page_config(page_title="Personal Fitness Tracker", layout="wide")  # MUST be the first Streamlit command
    st.markdown("""
    <style>
        .title {font-size:80px !important; text-align: center; font-style:bold; color:#00bfff; font-family: ink free;}
        .stButton>button { background-color: #87CEEB; color: white; }
    </style>
""", unsafe_allow_html=True)
    st.markdown('<b class="title">Personal Fitness Tracker</b>', unsafe_allow_html=True)
    username = st.session_state.current_user

    if st.button("Mark Attendance"):
        if mark_attendance(username, users):
            st.success("Attendance marked for today!")
        else:
            st.warning("You have already marked attendance for today.")
    st.write(f"Hello, {username}! Welcome to your personal fitness tracker.")
    st.write("---")
        # Categorized food list
    food_categories = {
            "Proteins & Meats": {
                "Chicken Breast": {"Calories": 165, "Protein": 31, "Fat": 3.6, "Vitamins": ["B6", "Niacin"]},
                "Turkey Breast": {"Calories": 135, "Protein": 29, "Fat": 1, "Vitamins": ["B6", "Niacin"]},
                "Salmon": {"Calories": 208, "Protein": 22, "Fat": 13, "Vitamins": ["Omega-3", "B12"]},
                "Tuna": {"Calories": 132, "Protein": 29, "Fat": 0.6, "Vitamins": ["Omega-3", "B12"]},
                "Eggs": {"Calories": 68, "Protein": 6, "Fat": 5, "Vitamins": ["B12", "Choline"]}
            },
            
            "Vegetables": {
                "Spinach": {"Calories": 23, "Protein": 2.9, "Fat": 0.4, "Vitamins": ["Iron", "Vitamin K"]},
                "Kale": {"Calories": 49, "Protein": 4.3, "Fat": 0.9, "Vitamins": ["Vitamin A", "Vitamin C"]},
                "Broccoli": {"Calories": 55, "Protein": 4.3, "Fat": 0.6, "Vitamins": ["Vitamin C", "Fiber"]},
                "Carrots": {"Calories": 41, "Protein": 0.9, "Fat": 0.2, "Vitamins": ["Vitamin A"]},
                "Sweet Potatoes": {"Calories": 86, "Protein": 2, "Fat": 0.1, "Vitamins": ["Vitamin A"]}
            },

            "Fruits": {
                "Apples": {"Calories": 52, "Protein": 0.3, "Fat": 0.2, "Vitamins": ["Vitamin C", "Fiber"]},
                "Bananas": {"Calories": 89, "Protein": 1.1, "Fat": 0.3, "Vitamins": ["Potassium"]},
                "Oranges": {"Calories": 47, "Protein": 0.9, "Fat": 0.1, "Vitamins": ["Vitamin C"]},
                "Blueberries": {"Calories": 57, "Protein": 0.7, "Fat": 0.3, "Vitamins": ["Antioxidants"]},
                "Strawberries": {"Calories": 32, "Protein": 0.7, "Fat": 0.3, "Vitamins": ["Vitamin C"]}
            },

            "Nuts & Seeds": {
                "Almonds": {"Calories": 579, "Protein": 21, "Fat": 50, "Vitamins": ["Vitamin E"]},
                "Walnuts": {"Calories": 654, "Protein": 15, "Fat": 65, "Vitamins": ["Omega-3"]},
                "Cashews": {"Calories": 553, "Protein": 18, "Fat": 44, "Vitamins": ["Magnesium"]},
                "Chia Seeds": {"Calories": 486, "Protein": 16, "Fat": 31, "Vitamins": ["Omega-3"]},
                "Pumpkin Seeds": {"Calories": 559, "Protein": 30, "Fat": 49, "Vitamins": ["Iron"]}
            },

            "Seafood": {
                "Mackerel": {"Calories": 205, "Protein": 19, "Fat": 13, "Vitamins": ["Omega-3"]},
                "Sardines": {"Calories": 208, "Protein": 25, "Fat": 11, "Vitamins": ["Calcium"]},
                "Trout": {"Calories": 168, "Protein": 22, "Fat": 10, "Vitamins": ["Omega-3"]},
                "Oysters": {"Calories": 81, "Protein": 9, "Fat": 2, "Vitamins": ["Zinc"]},
                "Crab": {"Calories": 97, "Protein": 20, "Fat": 1.5, "Vitamins": ["B12"]}
            },

            "Whole Grains & Legumes": {
                "Brown Rice": {"Calories": 111, "Protein": 2.6, "Fat": 0.9, "Vitamins": ["Fiber"]},
                "Quinoa": {"Calories": 120, "Protein": 4.1, "Fat": 1.9, "Vitamins": ["Magnesium"]},
                "Oats": {"Calories": 389, "Protein": 17, "Fat": 7, "Vitamins": ["Fiber"]},
                "Lentils": {"Calories": 116, "Protein": 9, "Fat": 0.4, "Vitamins": ["Iron"]},
                "Chickpeas": {"Calories": 164, "Protein": 9, "Fat": 2.6, "Vitamins": ["Folate"]}
            },

            "Dairy & Alternatives": {
                "Greek Yogurt": {"Calories": 97, "Protein": 10, "Fat": 5, "Vitamins": ["Probiotics"]},
                "Cottage Cheese": {"Calories": 98, "Protein": 11, "Fat": 4, "Vitamins": ["Calcium"]},
                "Cheddar Cheese": {"Calories": 403, "Protein": 25, "Fat": 33, "Vitamins": ["Calcium"]},
                "Milk": {"Calories": 42, "Protein": 3.4, "Fat": 1, "Vitamins": ["Calcium"]},
                "Tofu": {"Calories": 144, "Protein": 15, "Fat": 9, "Vitamins": ["Iron"]}
            },

            "Superfoods & Miscellaneous": {
                "Dark Chocolate": {"Calories": 546, "Protein": 7.9, "Fat": 31, "Vitamins": ["Iron"]},
                "Coconut": {"Calories": 354, "Protein": 3.3, "Fat": 33, "Vitamins": ["Manganese"]},
                "Kimchi": {"Calories": 15, "Protein": 1, "Fat": 0.5, "Vitamins": ["Probiotics"]},
                "Miso": {"Calories": 199, "Protein": 12, "Fat": 6, "Vitamins": ["Probiotics"]},
                "Seaweed": {"Calories": 45, "Protein": 5, "Fat": 1, "Vitamins": ["Iodine"]}
            }
        }

        # Sidebar UI
    st.sidebar.header("Food Nutritional Information")

        # Select category
    category = st.sidebar.selectbox("Select Category", list(food_categories.keys()))

        # Select food item within category
    if category:
        food_option = st.sidebar.selectbox("Select Food", list(food_categories[category].keys()))

            # Select quantity
        quantity_option = st.sidebar.selectbox("Select Quantity", ["250g", "500g", "750g", "1kg", "1.5kg", "2kg"])
        quantity_multiplier = {"250g": 0.25, "500g": 0.5, "750g": 0.75, "1kg": 1, "1.5kg": 1.5, "2kg": 2}

            # Display nutritional info
        if food_option:
            st.write(f"### {food_option} Nutritional Information ({quantity_option})")
            for nutrient, value in food_categories[category][food_option].items():
                if isinstance(value, list):
                    st.write(f"{nutrient}: {', '.join(value)}")
                else:
                    st.write(f"{nutrient}: {value * quantity_multiplier[quantity_option]}")
        st.write("---")


        fitness_juices = {
    "Muscle Recovery & Growth": {
        "Banana Almond Protein Shake": (
            "Rich in protein, almond milk and banana combine to promote muscle recovery and growth."
        ),
        "Chocolate Peanut Butter Smoothie": (
            "A tasty, protein-packed drink with antioxidants from cocoa and healthy fats from peanut butter."
        ),
        "Spinach Avocado Protein Juice": (
            "Loaded with amino acids and vitamins, this juice supports muscle regeneration and overall health."
        ),
        "Greek Yogurt Blueberry Smoothie": (
            "Packed with protein and antioxidants, this smoothie aids in muscle repair and reduces inflammation."
        ),
        "Mango Coconut Protein Shake": (
            "A tropical, nutrient-dense shake that blends mango and coconut for post-workout replenishment."
        ),
        "Pineapple Ginger Recovery Juice": (
            "An anti-inflammatory juice that helps soothe muscles and speed up recovery."
        ),
        "Beetroot Carrot Juice": (
            "Rich in nitrates, this juice boosts muscle oxygenation and supports recovery."
        ),
        "Watermelon Basil Juice": (
            "Provides hydration and amino acids for muscle repair and post-exercise recovery."
        ),
        "Papaya Honey Smoothie": (
            "A blend that supports digestion and provides nutrients for muscle growth."
        ),
        "Turmeric Golden Milk Shake": (
            "Infused with turmeric's anti-inflammatory properties to soothe post-workout soreness."
        )
    },
    "Fat Burning & Metabolism Boosting": {
        "Green Apple Celery Juice": (
            "A refreshing blend that’s low in calories and high in antioxidants to support fat burning."
        ),
        "Grapefruit Fat Burner Juice": (
            "Packed with vitamin C and enzymes that boost metabolism and support weight loss."
        ),
        "Lemon Ginger Detox Juice": (
            "A tangy and spicy combo that revs up your metabolism while aiding digestion."
        ),
        "Apple Cider Vinegar Drink": (
            "Famous for its fat-burning properties and ability to regulate blood sugar levels."
        ),
        "Cucumber Mint Fat Cutter": (
            "Cucumber keeps you hydrated while mint stimulates digestion and fat metabolism."
        ),
        "Carrot Beet Metabolism Booster": (
            "A nutrient-rich juice that improves metabolic rate and supports fat loss."
        ),
        "Orange Cinnamon Juice": (
            "A metabolism-enhancing juice with antioxidants and a burst of flavor."
        ),
        "Pineapple Chia Fat-Burner": (
            "Chia seeds add fiber and omega-3s while pineapple promotes fat loss."
        ),
        "Matcha Green Tea Smoothie": (
            "A metabolism-boosting drink rich in antioxidants and energy-boosting matcha."
        ),
        "Spinach Lemon Green Juice": (
            "Low-calorie juice loaded with iron and vitamin C to enhance fat burning."
        )
    },
    "Energy & Endurance Boosting": {
        "Banana Date Energy Smoothie": (
            "Rich in natural sugars and potassium, this smoothie is perfect for a pre-workout energy boost."
        ),
        "Sweet Potato Cinnamon Smoothie": (
            "A nutrient-packed blend providing long-lasting energy and vitamins for endurance."
        ),
        "Pomegranate Power Juice": (
            "Full of antioxidants, this juice aids in improving stamina and cardiovascular health."
        ),
        "Coconut Water Electrolyte Drink": (
            "An all-natural drink filled with electrolytes to keep you hydrated and energized."
        ),
        "Grape Honey Energy Juice": (
            "A sweet treat combining natural sugars from grapes and honey to keep your energy levels high."
        ),
        "Acai Berry Power Blend": (
            "Rich in antioxidants and natural sugars, it provides a quick energy boost."
        ),
        "Watermelon Coconut Juice": (
            "Packed with electrolytes and hydration to support endurance workouts."
        ),
        "Cherry Lemonade Energy Drink": (
            "Loaded with vitamin C and natural sugars to sustain energy levels."
        ),
        "Pineapple Papaya Juice": (
            "A tropical juice with a mix of nutrients to fuel your workouts."
        ),
        "Guava Strawberry Energizer": (
            "High in vitamins and minerals, this juice boosts energy and keeps you refreshed."
        )
    },
    "Hydration & Detoxification": {
        "Cucumber Aloe Hydration Juice": (
            "A cooling juice that hydrates deeply while supporting detoxification."
        ),
        "Lemon Cucumber Mint Detox Water": (
            "A classic blend that flushes toxins and keeps you hydrated."
        ),
        "Watermelon Coconut Hydrator": (
            "Combines watermelon and coconut water for a powerful hydrating drink."
        ),
        "Chia Seed Lime Drink": (
            "Packed with fiber and hydration, this drink aids in flushing out toxins."
        ),
        "Kiwi Cucumber Cooler": (
            "A refreshing and vitamin-rich juice that hydrates and detoxifies."
        ),
        "Aloe Vera Honey Detox Drink": (
            "A sweet and soothing drink that promotes digestion and detoxification."
        ),
        "Orange Basil Infused Water": (
            "A flavorful detox drink combining citrus and herbs for a refreshing touch."
        ),
        "Celery Lemon Hydration Juice": (
            "A hydrating juice rich in electrolytes and vitamins."
        ),
        "Blueberry Coconut Detox Drink": (
            "A delicious antioxidant-rich drink to cleanse your system."
        ),
        "Green Tea Lemon Detox Smoothie": (
            "A metabolism-boosting smoothie with detoxifying green tea."
        )
    },
    "Immunity & Overall Health": {
        "Carrot Ginger Turmeric Juice": (
            "Packed with immunity-boosting ingredients to fight inflammation."
        ),
        "Spinach Kale Super Juice": (
            "A superfood-rich juice that boosts immunity and overall wellness."
        ),
        "Citrus Honey Ginger Elixir": (
            "A vitamin C-rich elixir to keep your immune system strong."
        ),
        "Pineapple Orange Vitamin C Boost": (
            "A tangy drink loaded with vitamin C to support immunity."
        ),
        "Mixed Berry Antioxidant Juice": (
            "A blend of berries high in antioxidants to promote health."
        ),
        "Mango Carrot Vitamin A Juice": (
            "Rich in vitamin A and other nutrients to enhance immune function."
        ),
        "Apple Cinnamon Immunity Shot": (
            "A quick shot of nutrients and anti-inflammatory properties."
        ),
        "Strawberry Kiwi Vitamin C Drink": (
            "A sweet and tangy drink filled with immune-boosting vitamins."
        ),
        "Broccoli Spinach Health Juice": (
            "A nutrient-packed juice for overall health and immunity."
        ),
        "Ginger Lemon Wellness Shot": (
            "A quick and potent drink to fight inflammation and boost immunity."
        )
    }
        }

        # Streamlit Application
        st.sidebar.header("Fitness Juices")
        category = st.sidebar.selectbox("Select a Category", options=list(fitness_juices.keys()))
        juice_name = st.sidebar.selectbox("Select a Juice", options=list(fitness_juices[category].keys()))

        st.header("Fitness Juices Menu")
        st.subheader(category)
        st.markdown(f"{juice_name}")
        st.markdown(fitness_juices[category][juice_name])
        st.write("---")

        gym_equipment = {
    "Strength Training Equipment (Weights & Machines)": {
        "Dumbbells": "2 - 50 kg (based on strength level)",
        "Barbells": "10 - 20 kg (without plates)",
        "Weight Plates": "2.5 - 25 kg per plate",
        "Kettlebells": "4 - 40 kg",
        "Resistance Bands": "Light, Medium, Heavy, Extra Heavy",
        "Smith Machine": "20 - 60 kg bar & additional plates",
        "Cable Machine": "5 - 90 kg weight stack",
        "Leg Press Machine": "40 - 300 kg (adjustable)",
        "Chest Press Machine": "10 - 80 kg weight stack",
        "Shoulder Press Machine": "10 - 70 kg"
    },
    "Bodyweight & Functional Training Equipment": {
        "Pull-up Bar": "Bodyweight",
        "Parallel Dip Bars": "Bodyweight",
        "Power Rack": "Adjustable (holds up to 200+ kg)",
        "TRX Suspension Trainer": "NA",
        "Gymnastic Rings": "NA",
        "Plyometric Box": "30cm, 45cm, 60cm heights",
        "Medicine Ball": "2 - 15 kg",
        "Battle Ropes": "9 - 15 meters long",
        "Ab Roller": "NA",
        "Jump Rope": "Adjustable Length"
    },
    "Cardio Equipment": {
        "Treadmill": "User Weight: Up to 180 kg",
        "Stationary Bike": "Adjustable resistance",
        "Rowing Machine": "Adjustable resistance",
        "Stair Climber": "NA",
        "Elliptical Trainer": "NA",
        "Assault Bike": "NA",
        "Ski Erg": "NA",
        "Air Rower": "NA",
        "Battle Ropes": "9 - 15 meters",
        "Speed Ladder": "NA"
    },
    "Leg & Core Strength Equipment": {
        "Squat Rack": "Supports up to 300+ kg",
        "Calf Raise Machine": "10 - 80 kg",
        "Glute Ham Developer": "NA",
        "Leg Curl Machine": "10 - 100 kg",
        "Hack Squat Machine": "40 - 300 kg",
        "Hip Thrust Machine": "20 - 200 kg",
        "Seated Ab Crunch Machine": "10 - 80 kg",
        "Roman Chair": "NA",
        "Stability Ball": "55cm - 75cm",
        "Weighted Vest": "5 - 20 kg"
    },
    "Recovery & Mobility Equipment": {
        "Foam Roller": "NA",
        "Massage Gun": "NA",
        "Resistance Bands": "Light - Heavy",
        "Yoga Mat": "NA",
        "Balance Board": "NA",
        "Hand Grippers": "10 - 100 kg",
        "Wrist/Ankle Weights": "0.5 - 5 kg",
        "Stretching Strap": "NA",
        "Infrared Sauna": "NA",
        "Ice Bath Tub": "NA"
    }
}

# Age-Based Equipment Usage Guide
        age_guide = {
    "Kids (10-14)": "Bodyweight exercises only",
    "Teens (15-18)": "Light dumbbells (2-10kg), resistance bands",
    "Beginners (19-30)": "Dumbbells (5-15kg), barbell (20-40kg)",
    "Intermediate (30-50)": "Dumbbells (15-30kg), barbell (40-80kg)",
    "Advanced (50+)": "Adjust weights based on endurance & recovery"
        }

        # Streamlit Application
        st.sidebar.header("Gym Equipment & Usage Guide")
        category = st.sidebar.selectbox("Select a Category", options=list(gym_equipment.keys()))
        equipment_name = st.sidebar.selectbox("Select Equipment", options=list(gym_equipment[category].keys()))

        st.header("Gym Equipment List")
        st.subheader(category)
        st.markdown(f"{equipment_name}")
        st.markdown(gym_equipment[category][equipment_name])

        st.sidebar.header("Usage Guide")
        age_group = st.sidebar.selectbox("Select an Age Group", options=list(age_guide.keys()))

        st.subheader("Equipment Usage Based on Age")
        st.markdown(f"{age_group}: {age_guide[age_group]}")
        st.write("---")
    
        exercise_styles = {
    "Martial Arts-Based Exercises (Strength + Agility)": {
        "Karate": "Focuses on strikes, blocks, and katas to enhance strength, coordination, and reflexes.",
        "Taekwondo": "Emphasizes high kicks and fast movements to improve flexibility and agility.",
        "Muay Thai": "A full-body workout involving punches, kicks, elbows, and knees to build endurance.",
        "Judo": "A grappling sport that strengthens core muscles and improves balance.",
        "Boxing": "Boosts stamina, reflexes, and upper-body strength through intense training.",
        "Kickboxing": "Combines the agility of boxing and the strength of karate for a cardio-intensive workout.",
        "Brazilian Jiu-Jitsu (BJJ)": "Focuses on ground techniques that enhance flexibility and endurance.",
        "Krav Maga": "Real-world self-defense that integrates intense conditioning exercises.",
        "Wrestling": "Builds muscle control and body awareness through grappling techniques.",
        "Capoeira": "A Brazilian martial art blending dance and acrobatics for agility and fluid motion."
    },
    "Mindful & Flow-Based Exercises (Balance + Mobility)": {
        "Hatha Yoga": "Involves slow poses and deep breathing to promote relaxation and mindfulness.",
        "Vinyasa Yoga": "A flow-based practice that improves endurance, flexibility, and balance.",
        "Power Yoga": "Combines strength-building poses with dynamic movements for a full-body workout.",
        "Restorative Yoga": "Uses props for deep relaxation and physical recovery.",
        "Chair Yoga": "Adaptive poses designed for individuals with limited mobility.",
        "Pilates": "Focuses on core strength, flexibility, and posture through controlled movements.",
        "Tai Chi": "A gentle martial art that reduces stress and improves balance.",
        "Qigong": "Integrates breath control and slow movements to improve energy flow.",
        "Yin Yoga": "Holds passive stretches for extended periods to release deep tissue tension.",
        "Aerial Yoga": "Uses fabric hammocks to support strength-building and flexibility exercises."
    },
    "Traditional Eastern Flow Arts (Flexibility + Energy Control)": {
        "Ashtanga Yoga": "Follows a structured sequence of poses to develop discipline and strength.",
        "Bikram Yoga (Hot Yoga)": "Conducted in a heated room to promote detoxification and flexibility.",
        "Iyengar Yoga": "Focuses on alignment and posture with the use of props.",
        "Pranayama": "Breathing exercises aimed at increasing lung capacity and mental clarity.",
        "Kalaripayattu": "An ancient Indian martial art that combines weapon-based and body movements.",
        "Shaolin Kung Fu": "Incorporates intense training to improve body control and focus.",
        "Japanese Kenjutsu": "Sword techniques that build precision, balance, and agility.",
        "Indian Mallakhamb": "Traditional pole and rope exercises to enhance core strength.",
        "Baguazhang": "A martial art with flowing movements to improve energy flow and coordination.",
        "Zhan Zhuang (Standing Meditation)": "Builds endurance, stability, and focus by holding postures."
    },
    "Strength & Core-Based Disciplines (Control + Stamina)": {
        "Calisthenics": "A bodyweight training style focused on strength and mobility.",
        "Street Workout": "Includes pull-ups, dips, and dynamic exercises for overall body conditioning.",
        "CrossFit": "High-intensity workouts that enhance strength and functional fitness.",
        "Animal Flow": "Primal movement exercises to improve agility and body coordination.",
        "Parkour": "Involves overcoming obstacles to boost agility and functional strength.",
        "Hand Balancing": "Challenges core and wrist strength through balancing exercises.",
        "Plank Variations": "Strengthens the core and improves stability.",
        "Battle Ropes": "High-intensity ropes improve endurance and upper body strength.",
        "Kettlebell Training": "Focuses on power, strength, and coordination with kettlebell exercises.",
        "Farmer’s Walk": "Enhances grip strength and overall core stability by carrying weights."
    },
    "Combat & Strength-Based Functional Training": {
        "MMA (Mixed Martial Arts)": "Combines boxing, wrestling, and ground fighting for a full-body workout.",
        "Sandbag Training": "Develops raw power and grip strength using sand-filled bags.",
        "Tire Flipping": "Improves explosive strength through repetitive tire movements.",
        "Sledgehammer Workouts": "Targets endurance and coordination with sledgehammer swings.",
        "Bulgarian Bag Training": "Enhances rotational strength using sand-filled bags.",
        "Resistance Band Combat Drills": "Adds resistance to combat-specific movements.",
        "Speed Drills with Parachutes": "Increases sprint speed and explosive power.",
        "Agility Ladder Drills": "Improves quick footwork and coordination.",
        "Sled Push/Pull": "Boosts power and lower body endurance with resistance sleds.",
        "Olympic Lifting": "Focuses on explosive strength through powerlifting techniques."
    },
    "Explosive & Agility-Based Workouts": {
        "Sprint Drills": "Improves speed and endurance through high-intensity intervals.",
        "Box Jumps": "Develops explosive lower body power and coordination.",
        "Hurdle Drills": "Increases agility and reflexes with fast footwork exercises.",
        "Jump Rope": "Boosts cardiovascular endurance with rhythmic skipping.",
        "High-Knees": "Engages the core and improves leg endurance.",
        "Plyometric Push-Ups": "Enhances upper body explosiveness through dynamic push-ups.",
        "Depth Jumps": "Strengthens fast-twitch muscles for explosive movements.",
        "Single-Leg Hops": "Improves balance and power with hopping exercises.",
        "Cone Drills": "Focuses on quickness and multi-directional agility.",
        "Hill Sprints": "Builds lower body strength through resistance running."
    },
    "Holistic & Hybrid Practices": {
        "Dance-Based Workouts": "A fun way to stay fit with Zumba, Hip-Hop, and other dance styles.",
        "Barre Workouts": "Combines ballet, Pilates, and yoga for flexibility and strength.",
        "Functional Mobility Drills": "Improves joint health and movement efficiency.",
        "Foam Rolling & Myofascial Release": "Relieves muscle tension and improves recovery.",
        "Breathwork Exercises": "Strengthens lung capacity and mental focus.",
        "Stretch Therapy": "Enhances flexibility and helps prevent injuries.",
        "TRX Suspension Training": "Uses body weight for functional strength improvement.",
        "Aqua Workouts": "Low-impact exercises conducted in water for resistance training.",
        "Barefoot Training": "Strengthens foot mechanics and balance.",
        "Isometric Holds": "Builds endurance and stability by holding positions."
    },
    "Extreme Flexibility & Flow Training": {
        "Splits Training": "Improves flexibility for advanced movements.",
        "Bridge Training": "Strengthens the spine and core for backbends.",
        "Contortion Training": "Develops extreme flexibility and body control.",
        "Scorpion Pose": "An advanced pose to enhance balance and flexibility.",
        "Flagpole Hold": "Requires core and upper body strength for balance."
    }
    }

        # Streamlit Application
        st.sidebar.header("Exercise Styles")
        category = st.sidebar.selectbox("Select a Category", options=list(exercise_styles.keys()))
        exercise_name = st.sidebar.selectbox("Select an Exercise", options=list(exercise_styles[category].keys()))

        st.header("Exercise Styles Menu")
        st.subheader(category)
        st.markdown(f"{exercise_name}: {exercise_styles[category][exercise_name]}")
        st.write("---")

        FILE_PATH = "workout_data.xlsx"

# Define MET values globally
        MET_values = {
    "Cardio": {
        "Running": 9.8, "Jump Rope": 12, "Cycling": 8, "Rowing": 7, "Stair Climbing": 9
    },
    "Strength Training": {
        "Bench Press": 6, "Deadlifts": 6, "Bicep Curls": 5, "Shoulder Press": 5.5, "Squats": 7
    },
    "Leg Workouts": {
        "Lunges": 6.5, "Leg Press": 6, "Calf Raises": 4.5, "Step-Ups": 7, "Bulgarian Split Squats": 7.5
    },
    "Full-Body Workouts": {
        "Burpees": 10, "Kettlebell Swings": 9.5, "Mountain Climbers": 8, "Clean and Press": 10, "Medicine Ball Slams": 9
    },
    "Yoga Workouts": {
        "Downward Dog": 3, "Warrior Pose": 3.5, "Tree Pose": 3, "Cobra Pose": 2.5, "Child’s Pose": 2
    },
    "Pilates Workouts": {
        "Leg Circles": 4, "Hundred": 4.5, "Rolling Like a Ball": 4, "Single-Leg Stretch": 4.2, "Teaser": 4.3
    },
    "Core & Abs Workouts": {
        "Planks": 3, "Russian Twists": 5, "Bicycle Crunches": 5.5, "Hanging Leg Raises": 6, "Ab Rollouts": 6.5
    },
    "HIIT": {
        "Sprint Intervals": 12, "Jump Squats": 9.5, "Battle Ropes": 8.5, "Box Jumps": 9, "Kettlebell Snatches": 10
    },
    "Stretching & Mobility Workouts": {
        "Static Stretching": 2, "Dynamic Stretching": 2.5, "Foam Rolling": 2.2, "Hip Openers": 2.8, "Shoulder Mobility Drills": 2.6
    },
    "CrossFit Workouts": {
        "Wall Balls": 7, "Power Cleans": 8, "Box Step-Ups": 7.5, "Rope Climbs": 8.2, "Thrusters": 9
    },
    "Calisthenics": {
        "Pull-Ups": 6.5, "Muscle-Ups": 7.5, "Dips": 6.8, "L-Sits": 6, "Pistol Squats": 6.5
    },
    "Powerlifting": {
        "Back Squat": 7, "Deadlift": 7.5, "Bench Press": 6.5, "Overhead Press": 6, "Snatch": 7.8
    },
    "Functional Fitness": {
        "Farmer’s Walk": 5.5, "Sled Push": 6.5, "Medicine Ball Throws": 6, "Sandbag Carries": 6.8, "Battle Rope Slams": 7
    },
    "Bodyweight Workouts": {
        "Push-Ups": 5, "Sit-Ups": 4.5, "Triceps Dips": 5.2, "Wall Sits": 4.8, "Jump Lunges": 6
    },
    "Martial Arts Workouts": {
        "Kickboxing": 11, "Brazilian Jiu-Jitsu": 10, "Muay Thai": 11.5, "Boxing": 12, "Judo": 10.5
    },
    "Swimming Workouts": {
        "Freestyle": 9, "Butterfly": 10, "Backstroke": 8, "Breaststroke": 9, "Treading Water": 7
    },
    "Dance Workouts": {
        "Zumba": 6, "Hip-Hop Cardio": 7, "Salsa Workouts": 6.5, "Ballet Conditioning": 5, "Bollywood Dance Fitness": 6
    },
    "Endurance Training": {
        "Marathon Running": 10, "Long-Distance Cycling": 9, "Rowing Machine": 8, "Swimming Laps": 9, "Trail Running": 9.5
    },
    "Plyometrics": {
        "Box Jumps": 9, "Depth Jumps": 8, "Hurdle Hops": 8.5, "Plyo Push-Ups": 8, "Bounding Drills": 7.5
    },
    "Outdoor & Adventure Workouts": {
        "Hiking": 7, "Rock Climbing": 8.5, "Kayaking": 6, "Skiing": 9, "Trail Running": 9.5
    }        }

        def load_data():
            if os.path.exists(FILE_PATH):
                return pd.read_excel(FILE_PATH)
            else:
                return pd.DataFrame(columns=["Date", "Category", "Workout Type", "Duration (min)", "Weight (kg)", "Age", "Height (cm)", "Calories Burned", "Time"])

        def save_data(data):
            data.to_excel(FILE_PATH, index=False)

        def calculate_calories(workout_type, duration, weight):
            for category in MET_values.values():
                if workout_type in category:
                    MET = category[workout_type]
                    calories_burned = (MET * weight * 3.5) / 200 * duration
                    return round(calories_burned, 2)
            return round(6 * weight * 3.5 / 200 * duration, 2)

        st.header("Calories Burned Calculator")
        weight = st.number_input("Enter your weight (kg):", min_value=30, max_value=200, value=70)
        category = st.selectbox("Select Workout Category:", list(MET_values.keys()))
        activity = st.selectbox("Select an activity:", list(MET_values[category].keys()))
        duration = st.selectbox("Select duration (minutes):", [15, 30, 45, 60, 90, 120])

        if activity and duration:
            met_value = MET_values[category][activity]
            calories_burned = met_value * weight * (duration / 60)
            st.success(f"You burned approximately {calories_burned:.2f} calories.")

        # Workout History Section
        st.header("Workout History")
        workout_data = load_data()
        workout_data["Date"] = pd.to_datetime(workout_data["Date"], errors="coerce")
        workout_data["Date"] = workout_data["Date"].astype(str)

        selected_date = st.date_input("Select Date to View History", date.today())
        filtered_data = workout_data[workout_data["Date"] == str(selected_date)]

        if not filtered_data.empty:
            st.table(filtered_data)
        else:
            st.write("No workout recorded for this date.")

        if st.button("Save Workout"):
            workout_data = load_data()
            new_entry = pd.DataFrame([[str(date.today()), category, activity, duration, weight, "", "", calories_burned, datetime.now().strftime("%H:%M:%S")]], columns=workout_data.columns)
            workout_data = pd.concat([workout_data, new_entry], ignore_index=True)
            save_data(workout_data)
            st.success("Workout saved successfully!")


        # Existing Code: User Input Parameters
        st.header("INFORMATIONS:")
        st.sidebar.header("User Input Parameters: ")

        def user_input_features():
            age = st.sidebar.slider("Age: ", 10, 100, 30)
            bmi = st.sidebar.slider("BMI: ", 15, 40, 20)
            duration = st.sidebar.slider("Duration (min): ", 0, 360, 15)
            heart_rate = st.sidebar.slider("Heart Rate: ", 60, 130, 80)
            body_temp = st.sidebar.slider("Body Temperature (C): ", 36, 42, 38)
            sleep_time = st.sidebar.slider("Sleep Time (hours): ", 0, 12, 6)
            water_hydrate_level = st.sidebar.slider("Water Hydrate Level (liters): ", 0, 8, 5)
            gender_button = st.sidebar.radio("Gender: ", ("Male", "Female"))

            if sleep_time < 6:
                st.warning("Your sleep time is low. Consider getting more rest to maintain a healthy lifestyle.")
            if water_hydrate_level < 3:
                st.warning("Your water intake is low. Please stay hydrated!")

            if age < 10 or age > 100:
                st.error("Invalid age. Please enter an age between 10 and 100.")
                return None  # Return None to prevent further processing

            gender = 1 if gender_button == "Male" else 0

            data_model = {
                "Age": age,
                "BMI": bmi,
                "Duration": duration,
                "Heart_Rate": heart_rate,
                "Body_Temp": body_temp,
                "Sleep_Time": sleep_time,
                "Water_Hydrate_Level": water_hydrate_level,
                "Gender_male": gender
            }

            features = pd.DataFrame(data_model, index=[0])
            return features

        df = user_input_features()

        st.header("Your Parameters: ")
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
            bar.progress(i + 1)
            time.sleep(0.01)
        st.write(df)

        # Load and preprocess data
        calories = pd.read_csv("calories.csv")
        exercise = pd.read_csv("exercise.csv")

        exercise_df = exercise.merge(calories, on="User_ID")
        exercise_df.drop(columns="User_ID", inplace=True)

        exercise_train_data, exercise_test_data = train_test_split(exercise_df, test_size=0.2, random_state=1)

        for data in [exercise_train_data, exercise_test_data]:
            data["BMI"] = data["Weight"] / ((data["Height"] / 100) ** 2)
            data["BMI"] = round(data["BMI"], 2)

        exercise_train_data = exercise_train_data[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
        exercise_test_data = exercise_test_data[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
        exercise_train_data = pd.get_dummies(exercise_train_data, drop_first=True)
        exercise_test_data = pd.get_dummies(exercise_test_data, drop_first=True)

        X_train = exercise_train_data.drop("Calories", axis=1)
        y_train = exercise_train_data["Calories"]

        X_test = exercise_test_data.drop("Calories", axis=1)
        y_test = exercise_test_data["Calories"]

        random_reg = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6)
        random_reg.fit(X_train, y_train)

        df = df.reindex(columns=X_train.columns, fill_value=0)

        prediction = random_reg.predict(df)

        st.write("---")
        st.header("Prediction: ")
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
            bar.progress(i + 1)
            time.sleep(0.01)

        st.write(f"{round(prediction[0], 2)} kilocalories")

        st.write("---")
        st.header("Similar Results: ")
        latest_iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
            bar.progress(i + 1)
            time.sleep(0.01)

        calorie_range = [prediction[0] - 10, prediction[0] + 10]
        similar_data = exercise_df[(exercise_df["Calories"] >= calorie_range[0]) & (exercise_df["Calories"] <= calorie_range[1])]
        st.write(similar_data.sample(5))

        st.write("---")
        st.header("General Information: ")
        boolean_age = (exercise_df["Age"] < df["Age"].values[0]).tolist()
        boolean_duration = (exercise_df["Duration"] < df["Duration"].values[0]).tolist()
        boolean_body_temp = (exercise_df["Body_Temp"] < df["Body_Temp"].values[0]).tolist()
        boolean_heart_rate = (exercise_df["Heart_Rate"] < df["Heart_Rate"].values[0]).tolist()

        st.write("You are older than", round(sum(boolean_age) / len(boolean_age), 2) * 100, "% of other people.")
        st.write("Your exercise duration is higher than", round(sum(boolean_duration) / len(boolean_duration), 2) * 100, "% of other people.")
        st.write("You have a higher heart rate than", round(sum(boolean_heart_rate) / len(boolean_heart_rate), 2) * 100, "% of other people during exercise.")
        st.write("You have a higher body temperature than", round(sum(boolean_body_temp) / len(boolean_body_temp), 2) * 100, "% of other people during exercise.")

    if st.sidebar.button("Logout", key="logout_button", use_container_width=True): st.session_state.login = False; st.session_state.current_user = None; st.rerun()
