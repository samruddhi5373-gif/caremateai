from flask import Flask, render_template, request, send_file, redirect
import sqlite3
import numpy as np
import joblib

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# =========================
# APP
# =========================

app = Flask(__name__)

# =========================
# GLOBAL VARIABLES
# =========================

patient_name = ""
age = ""
gender = ""
disease = ""
bmi = ""
bmi_status = ""
health_score = ""
risk = ""
medicines = ""
advice = ""

latest_report = {}

# =========================
# LOAD ML MODEL
# =========================

model = joblib.load('disease_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# =========================
# DATABASE
# =========================

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''

CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT

)

''')

conn.commit()
conn.close()

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():

    return render_template(

        'index.html',

        show_login=True

    )

# =========================
# SIGNUP
# =========================

@app.route('/signup', methods=['POST'])
def signup():

    username = request.form['signup_username']
    password = request.form['signup_password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(

        "SELECT * FROM users WHERE username=?",

        (username,)

    )

    existing_user = cursor.fetchone()

    if existing_user:

        conn.close()

        return render_template(

            'index.html',

            show_signup=True

        )

    cursor.execute(

        "INSERT INTO users(username,password) VALUES(?,?)",

        (username, password)

    )

    conn.commit()
    conn.close()

    return render_template(

        'index.html',

        show_login=True

    )

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['login_username']
    password = request.form['login_password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(

        "SELECT * FROM users WHERE username=? AND password=?",

        (username, password)

    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return render_template(

            'index.html',

            show_patient_page=True

        )

    else:

        return render_template(

            'index.html',

            show_login=True

        )

# =========================
# PREDICT
# =========================

@app.route('/predict', methods=['POST'])
def predict():

    global patient_name
    global age
    global gender
    global disease
    global bmi
    global bmi_status
    global health_score
    global risk
    global medicines
    global advice
    global latest_report

    # =========================
    # PATIENT DETAILS
    # =========================

    patient_name = request.form['patient_name']

    age = int(request.form['age'])

    gender = request.form['gender']

    weight = float(request.form['weight'])

    # =========================
    # HEIGHT
    # =========================

    height_cm = request.form.get('height_Centimeter')

    feet = request.form.get('feet')

    inches = request.form.get('inches')

    if height_cm:

        height_m = float(height_cm) / 100

    else:

        feet = float(feet or 0)

        inches = float(inches or 0)

        total_inches = (feet * 12) + inches

        height_m = total_inches * 0.0254

    # =========================
    # BMI
    # =========================

    bmi = round(weight / (height_m ** 2), 2)

    if bmi < 18.5:

        bmi_status = "Underweight"

    elif bmi < 25:

        bmi_status = "Normal"

    elif bmi < 30:

        bmi_status = "Overweight"

    else:

        bmi_status = "Obese"

    # =========================
    # BASIC SYMPTOMS
    # =========================

    fever = int(request.form['fever'])

    cough = int(request.form['cough'])

    headache = int(request.form['headache'])

    fatigue = int(request.form['fatigue'])

    vomiting = int(request.form['vomiting'])

    breathing = int(request.form['breathing'])

    body_pain = int(request.form['body_pain'])

    chest_pain = int(request.form['chest_pain'])

    # =========================
    # CHATBOT ANSWERS
    # =========================

    chatbot_text = request.form.get(

        "chatbot_answers",

        ""

    ).lower()

    # =========================
    # SYMPTOMS ARRAY
    # =========================

    symptoms = [0] * 11

    symptom_map = {

    "fever": 0,
    "cough": 1,
    "headache": 2,
    "vomiting": 3,
    "fatigue": 4,
    "breathing": 5,
    "body pain": 6,
    "chest pain": 7,
    "cold": 8,
    "stomach pain": 9,
    "diarrhea": 10

}

    # =========================
    # FILL SYMPTOMS
    # =========================

    for symptom, index in symptom_map.items():

        if symptom in chatbot_text:

            symptoms[index] = 1

    # =========================
    # BASIC FORM SYMPTOMS
    # =========================

    symptoms[0] = fever
    symptoms[1] = cough
    symptoms[2] = headache
    symptoms[3] = vomiting
    symptoms[4] = fatigue
    symptoms[5] = breathing
    symptoms[6] = body_pain
    symptoms[7] = chest_pain
    # =========================


    # =========================
    # ML PREDICTION
    # =========================

    prediction = model.predict([symptoms])

    disease = label_encoder.inverse_transform(

        prediction

    )[0]

    # =========================
    # HEALTH SCORE
    # =========================

    symptom_total = (

        fever +
        cough +
        headache +
        fatigue +
        vomiting +
        breathing +
        body_pain +
        chest_pain

    )

    health_score = max(

        100 - (symptom_total * 5),

        20

    )

    # =========================
    # RISK LEVEL
    # =========================

    if health_score > 80:

        risk = "Low"

    elif health_score > 50:

        risk = "Moderate"

    else:

        risk = "High"

    # =========================
    # EMERGENCY CHECK
    # =========================

    emergency = False

    if chest_pain >= 2 or breathing >= 3:

        emergency = True

    # =========================
    # MEDICINES
    # =========================

    medicine_map = {

        'Flu': 'Paracetamol, Vitamin C',

        'Covid': 'Isolation, Steam, Paracetamol',

        'Food Poisoning': 'ORS, Electrolytes',

        'Heart Disease': 'Consult Cardiologist',

        'Cold': 'Cough Syrup, Steam'

    }

    medicines = medicine_map.get(

        disease,

        'Consult Doctor'

    )

    # =========================
    # ADVICE
    # =========================

    advice_map = {

        'Flu': 'Take proper rest and drink warm fluids.',

        'Covid': 'Isolate yourself and monitor oxygen.',

        'Food Poisoning': 'Drink ORS and avoid outside food.',

        'Heart Disease': 'Seek medical attention immediately.',

        'Cold': 'Take steam and stay hydrated.'

    }

    advice = advice_map.get(

        disease,

        'Maintain healthy lifestyle.'

    )

    # =========================
    # AI TIPS
    # =========================

    tips = [

        "Drink plenty of water",

        "Take proper rest",

        "Avoid junk food",

        "Exercise regularly",

        "Sleep 7-8 hours daily"

    ]

    # =========================
    # SAVE REPORT
    # =========================

    latest_report = {

        'patient_name': patient_name,
        'age': age,
        'gender': gender,
        'prediction': disease,
        'bmi': bmi,
        'bmi_status': bmi_status,
        'health_score': health_score,
        'risk': risk,
        'medicines': medicines,
        'advice': advice

    }

    # =========================
    # FINAL REPORT
    # =========================

    return render_template(

    'chatbot.html',

    patient_name=patient_name,

    age=age,

    gender=gender

)
# =========================
# DOWNLOAD REPORT
# =========================

@app.route('/download_report')
def download_report():

    pdf_file = "medical_report.pdf"

    c = canvas.Canvas(

        pdf_file,

        pagesize=letter

    )

    y = 750

    c.setFont(

        "Helvetica-Bold",

        20

    )

    c.drawString(

        180,

        y,

        "CareMateAI Report"

    )

    y -= 50

    c.setFont(

        "Helvetica",

        14

    )

    for key, value in latest_report.items():

        c.drawString(

            80,

            y,

            f"{key}: {value}"

        )

        y -= 30

    c.save()

    return send_file(

        pdf_file,

        as_attachment=True

    )

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    return redirect('/')

# =========================
# RUN APP
# =========================
# =========================
# FINAL REPORT PAGE
# =========================

@app.route('/final_report', methods=['GET', 'POST'])
def final_report():

    return render_template(

        'index.html',

        show_result=True,

        patient_name=patient_name,

        age=age,

        gender=gender,

        prediction=disease,

        bmi=bmi,

        bmi_status=bmi_status,

        health_score=health_score,

        risk=risk,

        medicines=medicines,

        advice=advice
    )

if __name__ == '__main__':

    app.run(debug=True)