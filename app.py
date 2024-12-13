from flask import Flask, json, render_template, redirect, session, url_for, request, flash
from dbhelper import *
from datetime import datetime


app = Flask(__name__)
app.secret_key = "!@#$%tidert"

# @app.after_request
# def addheader(response):
#     response.headers['Content-Type'] = 'no-cache, no-store, must-revalidate, private'
#     response.headers["Pragma"] = 'no-cache'
#     response.header["Expires"] = "0"
#     return response

@app.route('/searchpatient', methods=['GET'])
def searchpatient():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    search_query = request.args.get('query', '').strip().lower()
    sql = """
        SELECT PT_ID, PT_FNAME, PT_MNAME, PT_LNAME, DT_OF_BIRTH
        FROM PATIENT_INFORMATION
    """
    params = []
    if search_query:
        sql += """
            WHERE LOWER(PT_FNAME) LIKE ? 
               OR LOWER(PT_MNAME) LIKE ? 
               OR LOWER(PT_LNAME) LIKE ? 
               OR CAST(PT_ID AS VARCHAR) LIKE ? 
               OR CONVERT(VARCHAR, DT_OF_BIRTH, 23) LIKE ?
        """
        like_query = f"%{search_query}%"
        params = [like_query, like_query, like_query, like_query, like_query]
    
    patients = getallprocess(sql, params)

    for patient in patients:
        pt_fname = patient.get('PT_FNAME', '')
        pt_mname = patient.get('PT_MNAME', '')
        pt_lname = patient.get('PT_LNAME', '')

        if pt_mname:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_mname} {pt_lname}".strip()
        else:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_lname}".strip()

        patient['DT_OF_BIRTH'] = str(patient.get('DT_OF_BIRTH', ''))

    return {'patients': patients}

@app.route("/deactivatepatient", methods=["POST"])
def deactivate_patient():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    pt_id = request.form.get("pt_id")
    if not pt_id:
        flash("Invalid patient ID.", "error")
        return redirect(url_for("index"))

    try:
        if deactivatepatient(pt_id):
            flash("Patient deactivated successfully.", "success")
        else:
            flash("Patient deactivation failed.", "error")
    except Exception as e:
        app.logger.error(f"Error deactivating patient: {e}")
        flash("An error occurred while deactivating the patient.", "error")

    return redirect(url_for("index"))

@app.route('/editpatient', methods=['POST'])
def editpatient():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        pt_id = request.form.get('pt_id') 
        pt_fname = request.form.get('pt_fname', '').strip().upper()
        pt_mname = request.form.get('pt_mname', '').strip().upper()
        pt_lname = request.form.get('pt_lname', '').strip().upper()
        dt_of_birth = request.form.get('dt_of_birth', '').strip()
        con_num = request.form.get('con_num', '').strip()
        email_add = request.form.get('email_add', '').strip()

        validation_errors = []

        if not pt_fname:
            validation_errors.append("First name cannot be empty.")
        if not pt_lname:
            validation_errors.append("Last name cannot be empty.")
        if not dt_of_birth:
            validation_errors.append("Date of birth cannot be empty.")
        if not con_num:
            validation_errors.append("Contact number cannot be empty.")

        # Flash all validation errors and stop further processing
        if validation_errors:
            for error in validation_errors:
                flash(error, "error")
            return redirect(url_for('pat_info', patient_id=pt_id))

        # Update patient information
        sql = """
            UPDATE PATIENT_INFORMATION
            SET PT_FNAME = ?, PT_MNAME = ?, PT_LNAME = ?, DT_OF_BIRTH = ?, CON_NUM = ?, EMAIL_ADD = ?
            WHERE PT_ID = ?
        """
        postprocess(sql, (pt_fname, pt_mname, pt_lname, dt_of_birth, con_num, email_add, pt_id))
        
        flash("Patient information updated successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while updating the patient: {e}", "error")

    return redirect(url_for('pat_info', patient_id=pt_id))

def get_fieldvalue(form, field_name):
    value = form.get(field_name)
    if value:
        return value.strip().upper()
    else: None
    
def get_bitvalue(form, field_name):
    value = form.get(field_name)
    if value and value.lower() in ['initial', 'passed', 'positive']:
        return 1
    return 0

@app.route('/addpatient', methods=['POST'])
def addpatient():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        pt_id = get_fieldvalue(request.form, 'pt_id')
        pt_lname = get_fieldvalue(request.form, 'pt_lname')
        pt_mname = get_fieldvalue(request.form, 'pt_mname')
        pt_fname = get_fieldvalue(request.form, 'pt_fname')
        dt_of_birth = get_fieldvalue(request.form, 'dt_of_birth')
        mt_name = get_fieldvalue(request.form, 'mt_name')
        ft_name = get_fieldvalue(request.form, 'ft_name')
        con_num = get_fieldvalue(request.form, 'con_num')
        email_add = get_fieldvalue(request.form, 'email_add')
        ens_date = get_fieldvalue(request.form, 'ens_date')
        ens_remarks = get_bitvalue(request.form, 'ens_remarks')
        nhs_date = get_fieldvalue(request.form, 'nhs_date')
        nhs_rear = get_bitvalue(request.form, 'nhs_rear')
        nhs_lear = get_bitvalue(request.form, 'nhs_lear')
        pos_cchd_date = get_fieldvalue(request.form, 'pos_cchd_date')
        pos_cchd_rhand = get_bitvalue(request.form, 'pos_cchd_rhand')
        pos_cchd_lhand = get_bitvalue(request.form, 'pos_cchd_lhand')
        ror_date = get_fieldvalue(request.form, 'ror_date')
        ror_remarks = get_fieldvalue(request.form, 'ror_remarks')

        # Execute stored procedure to insert patient
        sql_patinf = """
            EXEC SP_PT_INFORMATION @PT_ID = ?, @PT_LNAME = ?, @PT_FNAME = ?, @PT_MNAME = ?, @DT_OF_BIRTH = ?, @MT_NAME = ?, @FT_NAME = ?, @CON_NUM = ?, @EMAIL_ADD = ?
        """
        patient_id_result = addprocess(sql_patinf, (pt_id, pt_lname, pt_fname, pt_mname, dt_of_birth, mt_name, ft_name, con_num, email_add))

        # Extract PT_ID from the result
        pt_id = patient_id_result[0] if patient_id_result else None
        if not pt_id:
            raise ValueError("Failed to retrieve PT_ID.")

        # Insert screening test if needed
        if any([ens_date, ens_remarks, nhs_date, nhs_rear, nhs_lear, pos_cchd_date, pos_cchd_rhand, pos_cchd_lhand, ror_date, ror_remarks]):
            sql_screentest = """
                EXEC SP_SCREENING_TEST @ENS_DATE = ?, @ENS_REMARKS = ?, @NHS_DATE = ?, @NHS_REAR = ?, @NHS_LEAR = ?, @POS_CCHD_DATE = ?, @POS_CCHD_RHAND = ?, 
                @POS_CCHD_LHAND = ?, @ROR_DATE = ?, @ROR_REMARKS = ?, @PT_ID = ?
            """
            postprocess(sql_screentest, (ens_date, ens_remarks, nhs_date, nhs_rear, nhs_lear, 
                                         pos_cchd_date, pos_cchd_rhand, pos_cchd_lhand, ror_date, 
                                         ror_remarks, pt_id))

        # Notify success
        flash("Patient added successfully!", "success")

    except Exception as e:
        app.logger.error(f"Error adding patient: {e}")
        flash("An error occurred while adding the patient.", "error")

    return redirect(url_for('index'))
    
@app.route("/patient/<int:patient_id>")
def pat_info(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('index'))

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')

    # pagkuha sa patient age
    dob = patient.get('DT_OF_BIRTH')
    if dob:
        if isinstance(dob, datetime):
            dob = dob.date()  
        today = datetime.today()
        age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age_years == 0:
            # If age is 0 years, calculate the months
            age_months = (today.year - dob.year) * 12 + today.month - dob.month - (today.day < dob.day)
            age = f"{age_months} months"
        else:
            age = age_years
        
    sql_stest = 'SELECT * FROM SCREENING_TEST WHERE PT_ID = ?' 
    stest = getallprocess(sql_stest, (patient_id,))
    
    descriptions = {
        'ENS_DATE': 'EXPANDED NEWBORN SCREENING',
        'ROR_DATE': 'RED ORANGE REFLEX',
    }
    
    test_data = []
    htest = []
    ptest = []
    
    
    if stest:
        for row in stest:
            # General test data
            for key, desc in descriptions.items():
                if row.get(key):
                    test_data.append({
                        'date': row.get(key),
                        'description': desc,
                        'remarks': row.get(f'{key.split("_")[0]}_REMARKS', 'N/A')
                    })

            # Hearing test data
            if row.get('NHS_DATE'):
                htest.append({
                    'date': row.get('NHS_DATE'),
                    'description': 'NEWBORN HEARING SCREENING',
                    'right_ear': "PASSED" if row.get('NHS_REAR', 0) == 1 else "REFER",
                    'left_ear': "PASSED" if row.get('NHS_LEAR', 0) == 1 else "REFER"
                })

            # Pulse oximetry data
            if row.get('POS_CCHD_DATE'):
                ptest.append({
                    'date': row.get('POS_CCHD_DATE'),
                    'description': 'PULSE OXIMETRY SCREENING',
                    'right_hand': "POSITIVE" if row.get('POS_CCHD_RHAND', 0) == 1 else "NEGATIVE",
                    'left_hand': "POSITIVE" if row.get('POS_CCHD_LHAND', 0) == 1 else "NEGATIVE"
                })

    return render_template("pat_info.html", patient=patient, age=age, 
                           dr_name=dr_name, spclty=spclty, 
                           test_data=test_data, htest=htest,
                           ptest=ptest)

@app.route("/addprescription/<int:patient_id>", methods=['POST'])
def add_prescription(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        prescription_date = request.form.get('prescription_date').strip()
        diagnosis = request.form.get('diagnosis').strip()
        
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
    # Ensure the user is logged in
    if not session.get('logged_in'):
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))

    # Fetch patient information
    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('index'))

    # Fetch prescriptions
    prescriptions = getprescriptionsbypatientid(patient_id)
    if not prescriptions:
        flash("No prescriptions found for this patient.", "info")

    # Add serialized JSON for prescription details to each prescription
    for prescription in prescriptions:
        prescription_details = prescription.get('PRESCRIPTION_DETAILS', {})
        prescription['PRESCRIPTION_DETAILS_JSON'] = json.dumps(prescription_details)

    # Fetch doctor information from session
    dr_name = session.get('dr_name', 'Unknown Doctor')
    spclty = session.get('spclty', 'General Practitioner')

    # Render the template
    return render_template(
        "presc_inf.html", 
        patient=patient, 
        prescriptions=prescriptions,
        dr_name=dr_name,
        spclty=spclty
    )

@app.route('/login', methods=['GET', 'POST'])
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
            print(user)
            session['logged_in'] = True
            session['user'] = user[0]
            
            session['dr_name'] = user[0].get('DR_NAME', '').upper()
            session['spclty'] = user[0].get('SPLTY', '').upper()
            session['dr_id'] = user[0].get('DR_ID')
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))
        
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    sql = "SELECT * FROM PATIENT_INFORMATION WHERE ISACTIVE = 1"    
    
    patients = getallprocess(sql)
    
    for patient in patients:
        pt_fname = patient.get('PT_FNAME', '')
        pt_mname = patient.get('PT_MNAME', '')
        pt_lname = patient.get('PT_LNAME', '')
        
        if pt_mname:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_mname} {pt_lname}".strip()
        else:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_lname}".strip()

    dr_name = session.get('dr_name', '')
    spclty = session.get('spclty', '')
    
    return render_template("index.html", patients=patients, dr_name=dr_name, spclty=spclty)
    
@app.route("/addprescription/<int:patient_id>", methods=['POST'])
def add_prescription(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        # Get form data
        dr_id = session.get('dr_id')
        
        date = get_fieldvalue(request.form, 'prescription_date')
        cutype = get_fieldvalue(request.form, 'checkup_type')
        age = get_fieldvalue(request.form, 'age')
        findings = get_fieldvalue(request.form, 'findings')
        consult = get_fieldvalue(request.form, 'consult')
        instruction = get_fieldvalue(request.form, 'instruction')
        returndate = get_fieldvalue(request.form, 'returndate')      
        length = get_fieldvalue(request.form, 'length')
        weight = get_fieldvalue(request.form, 'weight')
        headcc = get_fieldvalue(request.form, 'head_circumference')
        chestcc = get_fieldvalue(request.form, 'chest_circumference')
        abdogt = get_fieldvalue(request.form, 'abdominal_girth')
        
        sql_presc = """
            EXEC SP_PRESCRIPTIONS @CU_TYPE = ?, @DATE = ?, @AGE = ?, 
            @FINDINGS = ?, @CONSULT = ?, @DR_INS = ?, @RETURN_DT = ?, 
            @PT_ID = ?, @DR_ID = ?
        """
        success2 = addprocess(sql_presc, (cutype, date, age, findings, consult, instruction, returndate, patient_id, dr_id))
        if not success2 or len(success2) == 0:
            flash("Failed to add prescription. Database operation did not return an ID.", "error")
            return redirect(url_for('presc_info', patient_id=patient_id))

        rx_id = success2[0] if success2 else None
        if not rx_id:
            raise ValueError("Failed to retrieve PT_ID.")
        
        if any([length, weight, headcc, chestcc, abdogt]):
            sql_am = """
                EXEC SP_ATPMC_MSRMT @WEIGHT = ?, @LENGTH = ?, @HEAD_CC = ?, 
                @CHEST_CC = ?, @ABDML_GT = ?, @PT_ID = ?, @RX_ID = ?
            """
            result = postprocess(sql_am, (length, weight, headcc, chestcc, abdogt, patient_id, rx_id))
            if not result:
                flash("Failed to save anthropometric measurements.", "error")
        if success2:
            flash("Prescription added successfully.", "success")
        else:
            flash("Failed to add prescription.", "error")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect(url_for('presc_info', patient_id=patient_id))

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
    

    return render_template("index.html", pagetitle = "Keepsake", patients=patients, dr_name=dr_name, spclty=spclty)

if __name__ == '__main__':
    app.run(debug=True)