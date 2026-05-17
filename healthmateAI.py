from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

app.secret_key = "caremate_secret_key"

# ================= DATABASE =================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= USER TABLE =================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(db.String(100))

# ================= HISTORY TABLE =================

class History(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    disease = db.Column(db.String(100))

    bmi = db.Column(db.String(50))

    health_score = db.Column(db.String(50))

# ================= APPOINTMENT TABLE =================

class Appointment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    doctor = db.Column(db.String(100))

    date = db.Column(db.String(100))

    time = db.Column(db.String(100))

# ================= HOME =================

@app.route('/')
def home():

    return render_template('index.html')

# ================= SIGNUP =================

@app.route('/signup', methods=['POST'])
def signup():

    username = request.form['signup_username']

    password = request.form['signup_password']

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:

        return "Username already exists"

    new_user = User(
        username=username,
        password=password
    )

    db.session.add(new_user)

    db.session.commit()

    return redirect(url_for('home'))

# ================= LOGIN =================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['login_username']

    password = request.form['login_password']

    user = User.query.filter_by(
        username=username,
        password=password
    ).first()

    if user:

        session['user'] = username

        return render_template(
            'index.html',
            open_page='page3'
        )

    return "Invalid Username or Password"

# ================= PREDICT =================

@app.route('/predict', methods=['POST'])
def predict():

    # ================= PATIENT DETAILS =================

    patient_name = request.form['patient_name']

    age = request.form['age']

    gender = request.form['gender']

    weight = float(request.form['weight'])

    # ================= HEIGHT =================

    height = 1.6

    height_cm = request.form.get(
        'height_cm',
        ''
    ).strip()

    feet = request.form.get(
        'feet',
        ''
    ).strip()

    inches = request.form.get(
        'inches',
        ''
    ).strip()

    # HEIGHT FROM CM

    if height_cm != "":

        height = float(height_cm) / 100

    # HEIGHT FROM FEET + INCHES

    elif feet != "":

        feet_value = float(feet)

        inches_value = float(inches) if inches != "" else 0

        total_inches = (feet_value * 12) + inches_value

        height = total_inches * 0.0254

    # SAFETY

    if height <= 0:

        height = 1.6

    # ================= BMI =================

    bmi = round(

        weight / (height * height),

        2
    )

    # ================= BMI STATUS =================

    if bmi < 18.5:

        bmi_status = "Underweight"

    elif bmi < 25:

        bmi_status = "Normal"

    elif bmi < 30:

        bmi_status = "Overweight"

    else:

        bmi_status = "Obese"

    # ================= SYMPTOMS =================

    fever = int(request.form['fever'])

    cough = int(request.form['cough'])

    headache = int(request.form['headache'])

    fatigue = int(request.form['fatigue'])

    vomiting = int(request.form['vomiting'])

    breathing = int(request.form['breathing'])

    body_pain = int(request.form['body_pain'])

    chest_pain = int(request.form['chest_pain'])

    duration = int(request.form['duration'])

    # ================= TOTAL SCORE =================

    total_score = (

        fever +
        cough +
        headache +
        fatigue +
        vomiting +
        breathing +
        body_pain +
        chest_pain
    )

    # ================= DISEASE PREDICTION =================

    if fever >= 2 and cough >= 2:

        prediction = "Flu"

    elif breathing >= 2 and chest_pain >= 2:

        prediction = "Possible Lung Infection"

    elif vomiting >= 2 and fever >= 2:

        prediction = "Food Infection"

    elif headache >= 2 and fatigue >= 2:

        prediction = "Migraine / Stress"

    else:

        prediction = "General Viral Infection"

    # ================= HEALTH SCORE =================

    health_score = max(

        10,

        100 - (total_score * 5)
    )

    # ================= RISK LEVEL =================

    if total_score <= 5:

        risk = "Low"

    elif total_score <= 12:

        risk = "Moderate"

    else:

        risk = "High"

    # ================= MEDICINES + ADVICE =================

    if prediction == "Flu":

        medicines = "Paracetamol, Vitamin C, Warm Water"

        advice = "Take proper rest and drink warm fluids."

    elif prediction == "Food Infection":

        medicines = "ORS, Antacid, Probiotics"

        advice = "Avoid outside food and stay hydrated."

    elif prediction == "Migraine / Stress":

        medicines = "Pain Reliever, Proper Sleep"

        advice = "Reduce stress and avoid screen exposure."

    elif prediction == "Possible Lung Infection":

        medicines = "Steam Inhalation, Antibiotics (Doctor Advice)"

        advice = "Consult doctor immediately if breathing worsens."

    else:

        medicines = "Multivitamins, Healthy Diet"

        advice = "Maintain healthy lifestyle and hydration."

    # ================= EMERGENCY ALERT =================

    emergency = False

    if chest_pain >= 3 or breathing >= 3:

        emergency = True

    # ================= AI HEALTH TIPS =================

    if prediction == "Flu":

        tips = [

            "Drink warm water",

            "Take vitamin C",

            "Get proper rest"
        ]

    elif prediction == "Food Infection":

        tips = [

            "Avoid oily food",

            "Drink ORS",

            "Eat light meals"
        ]

    elif prediction == "Migraine / Stress":

        tips = [

            "Reduce screen time",

            "Sleep properly",

            "Stay hydrated"
        ]

    elif prediction == "Possible Lung Infection":

        tips = [

            "Avoid cold drinks",

            "Take steam inhalation",

            "Consult a doctor"
        ]

    else:

        tips = [

            "Exercise daily",

            "Eat healthy food",

            "Stay hydrated"
        ]

    # ================= SAVE HISTORY =================

    if 'user' in session:

        history = History(

            username=session['user'],

            disease=prediction,

            bmi=str(bmi),

            health_score=str(health_score)
        )

        db.session.add(history)

        db.session.commit()

    # ================= RESULT =================

    return render_template(

        'index.html',

        open_page='page5',

        patient_name=patient_name,
        age=age,
        gender=gender,
        prediction=prediction,
        bmi=bmi,
        bmi_status=bmi_status,
        health_score=health_score,
        advice=advice,
        risk=risk,
        medicines=medicines,
        emergency=emergency,
        tips=tips
    )

# ================= HISTORY PAGE =================

@app.route('/history')
def history():

    if 'user' not in session:

        return redirect(url_for('home'))

    records = History.query.filter_by(
        username=session['user']
    ).all()

    return render_template(
        'history.html',
        records=records
    )

# ================= APPOINTMENT PAGE =================

@app.route('/appointment')
def appointment():

    if 'user' not in session:

        return redirect(url_for('home'))

    return render_template(
        'appointment.html'
    )

# ================= BOOK APPOINTMENT =================

@app.route('/book_appointment', methods=['POST'])
def book_appointment():

    if 'user' not in session:

        return redirect(url_for('home'))

    doctor = request.form['doctor']

    date = request.form['date']

    time = request.form['time']

    appointment = Appointment(

        username=session['user'],

        doctor=doctor,

        date=date,

        time=time
    )

    db.session.add(appointment)

    db.session.commit()

    return """

    <h1 style='font-family:Arial;text-align:center;color:#0077ff;margin-top:100px;'>

    Appointment Booked Successfully

    </h1>

    <div style='text-align:center;margin-top:40px;'>

    <a href='/'>

    <button style='padding:15px 30px;background:#0077ff;color:white;border:none;border-radius:10px;'>

    Back To Home

    </button>

    </a>

    </div>

    """

# ================= DOWNLOAD REPORT =================

@app.route('/download_report')
def download_report():

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.drawString(
        200,
        800,
        "CareMateAI Medical Report"
    )

    pdf.drawString(
        100,
        760,
        "Generated by CareMateAI"
    )

    pdf.save()

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="CareMateAI_Report.pdf",

        mimetype='application/pdf'
    )

# ================= LOGOUT =================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect(url_for('home'))

# ================= MAIN =================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)