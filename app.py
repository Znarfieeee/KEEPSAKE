from flask import Flask, render_template, redirect, session, url_for, request, flash
from dbhelper import *
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-development')
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    patients = getallrecords('PATIENT_INFORMATION')
    
    for patient in patients:
        pt_fname = patient.get('PT_FNAME', '')
        pt_mname = patient.get('PT_MNAME', '')
        pt_lname = patient.get('PT_LNAME', '')

        patient['PT_FULLNAME'] = f"{pt_fname} {pt_mname} {pt_lname}".strip() if pt_mname else f"{pt_fname} {pt_lname}".strip()

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')

    return render_template("index.html", pagetitle="Keepsake", patients=patients, dr_name=dr_name, spclty=spclty)

@app.route("/patient/<int:patient_id>")
def pat_info(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('index'))

    dob = patient.get('DT_OF_BIRTH')
    age = None
    if dob:
        try:
            dob = dob.date() if isinstance(dob, datetime) else dob
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception as e:
            age = None
            flash("Error calculating age", "error")

    prescriptions = getprescriptionsbypatientid(patient_id)

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')

    return render_template(
        "pat_info.html", 
        patient=patient, 
        age=age, 
        dr_name=dr_name, 
        spclty=spclty, 
        prescriptions=prescriptions
    )

@app.route("/addprescription/<int:patient_id>", methods=['POST'])
def add_prescription(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        prescription_date = request.form.get('prescription_date').strip()
        diagnosis = request.form.get('diagnosis').strip()
        
        if not prescription_date or not diagnosis:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('pat_info', patient_id=patient_id))
        
        success = addnewprescription(patient_id, prescription_date, diagnosis)
        if success:
            flash("Prescription added successfully.", "success")
        else:
            flash("Failed to add prescription.", "error")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect(url_for('pat_info', patient_id=patient_id))

@app.route("/prescriptions/<int:patient_id>")
def presc_info(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('index'))

    prescriptions = getprescriptionsbypatientid(patient_id)

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')

    return render_template(
        "presc_inf.html", 
        patient=patient, 
        prescriptions=prescriptions,
        dr_name=dr_name,
        spclty=spclty
    )

@app.route("/immunization/<int:patient_id>")
def immunization(patient_id):
    """Display immunization details for the patient."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('index'))

    # Fetch immunization records for the patient
    immunizations = getimmunizationsbypatientid(patient_id)

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')

    return render_template(
        "immunization.html",
        patient=patient,
        immunizations=immunizations,
        dr_name=dr_name,
        spclty=spclty
    )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        empid = request.form.get('EMP_ID')
        password = request.form.get('PASSWORD')
        
        if not empid or not password:
            flash("Please fill in both username and password.", "error")
            return redirect(url_for('login'))
        
        sql = """
            SELECT a.*, d.DR_NAME, d.SPLTY 
            FROM ACCOUNTS a
            LEFT JOIN DOCTOR d ON a.EMP_ID = d.DR_ID
            WHERE a.EMP_ID = ? AND a.PASSWORD = ?
        """
        user = getallprocess(sql, (empid, password))
        
        if user:
            session['logged_in'] = True
            session['user'] = user[0]
            session['dr_name'] = user[0].get('DR_NAME', '').upper()
            session['spclty'] = user[0].get('SPLTY', '').upper()
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

def getprescriptionsbypatientid(patient_id):
    """Fetch prescriptions based on patient ID."""
    sql = """
        SELECT RX_ID, [DATE] AS PRESCRIPTION_DATE, FINDINGS AS DIAGNOSIS
        FROM PRESCRIPTIONS
        WHERE PT_ID = ?
    """
    return getallprocess(sql, (patient_id,))

def addnewprescription(patient_id, prescription_date, diagnosis):
    """Add a new prescription to the database."""
    try:
        sql = """
            INSERT INTO PRESCRIPTIONS (PT_ID, [DATE], FINDINGS)
            VALUES (?, ?, ?)
        """
        success = postprocess(sql, (patient_id, prescription_date, diagnosis))
        return success
    except Exception as e:
        print(f"Error adding prescription: {e}")
        return False

def getimmunizationsbypatientid(patient_id):
    """Fetch immunization records based on patient ID."""
    sql = """
        SELECT IMMUNIZATION_ID, IMMUNIZATION_DATE, IMMUNIZATION_TYPE
        FROM IMMUNIZATIONS
        WHERE PT_ID = ?
    """
    return getallprocess(sql, (patient_id,))

if __name__ == '__main__':
    app.run(debug=True)
