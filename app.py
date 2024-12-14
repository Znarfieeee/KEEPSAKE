from flask import Flask, render_template, redirect, session, url_for, request, flash, jsonify
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

    vaccines = get_vaccines_for_patient(patient_id)  # Fetch vaccines for the patient
    print("Vaccines:", vaccines)  # Debugging line
    return render_template("pat_info.html", patient=patient, age=age, 
                           dr_name=dr_name, spclty=spclty, 
                           test_data=test_data, htest=htest,
                           ptest=ptest, vaccines=vaccines)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        empid = request.form.get('EMP_ID')
        password = request.form.get('PASSWORD')
        
        if not empid or not password:
            flash("Please fill in both username and password.", "error")
            return redirect(url_for('login'))
        
        sql = """
            SELECT a.USERTYPE, a.USER_FNAME, a.USER_LNAME, a.EMP_ID, a.PASSWORD, 
                   d.DR_NAME, d.SPLTY, d.DR_ID 
            FROM ACCOUNTS a
            LEFT JOIN DOCTOR d ON a.EMP_ID = d.DR_ID
            WHERE a.EMP_ID = ? AND a.PASSWORD = ?
        """
        user = getallprocess(sql, (empid, password))
        
        if user:  # Check if the query returned any data
            user_data = user[0]  # Safely access the first row
            
            session['logged_in'] = True
            session['user'] = user_data
            session['user_type'] = user_data.get('USERTYPE')  # Determine if staff or doctor

            # Combine USER_FNAME and USER_LNAME for staff users
            user_fname = user_data.get('USER_FNAME', '').strip()
            user_lname = user_data.get('USER_LNAME', '').strip()
            session['staff_name'] = f"{user_fname} {user_lname}".upper()
            
            # Safely handle doctor-specific fields
            session['dr_name'] = (user_data.get('DR_NAME') or '').upper()
            session['spclty'] = (user_data.get('SPLTY') or '').upper()
            session['dr_id'] = user_data.get('DR_ID')

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
    staff_name = session.get('staff_name', '')
    
    return render_template("index.html", patients=patients, dr_name=dr_name, spclty=spclty, staff_name=staff_name)
    
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
    
@app.route('/dashboard/details')
def dashboard_details():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get detailed statistics
    sql_immunizations = """
    SELECT 
        VAX,
        COUNT(*) as count
    FROM IMMUNIZATION_RECORD
    GROUP BY VAX
    ORDER BY count DESC
    """
    
    sql_age_groups = """
    SELECT 
        CASE 
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 12 THEN 'Under 1 year'
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 24 THEN '1-2 years'
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 60 THEN '2-5 years'
            ELSE 'Over 5 years'
        END as age_group,
        COUNT(*) as count
    FROM PATIENT_INFORMATION
    GROUP BY 
        CASE 
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 12 THEN 'Under 1 year'
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 24 THEN '1-2 years'
            WHEN DATEDIFF(month, DT_OF_BIRTH, GETDATE()) < 60 THEN '2-5 years'
            ELSE 'Over 5 years'
        END
    ORDER BY age_group
    """
    
    immunization_stats = getallprocess(sql_immunizations)
    age_groups = getallprocess(sql_age_groups)
    
    return render_template('dashboard_details.html',
                         immunization_stats=immunization_stats,
                         age_groups=age_groups,
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))


@app.route('/reports/patients')
def patients_tab():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        # Get all patients records (for all-patients tab)
        sql_all = """
        WITH LatestOperations AS (
            SELECT 
                PT_ID,
                LOG_ID,
                OPERATION,
                MODIFIED_DATE,
                PT_FNAME,
                PT_LNAME,
                ROW_NUMBER() OVER (PARTITION BY PT_ID ORDER BY MODIFIED_DATE DESC) as rn
            FROM (
                SELECT 
                    t.LOG_ID,
                    t.PT_ID,
                    CASE t.OPERATION 
                        WHEN 'INSERT' THEN 'INSERTED'
                        WHEN 'UPDATE' THEN 'UPDATED'
                        ELSE t.OPERATION 
                    END as OPERATION,
                    t.MODIFIED_DATE,
                    p.PT_FNAME,
                    p.PT_LNAME
                FROM 
                    TRANSACTION_LOG t
                    JOIN PATIENT_INFORMATION p ON t.PT_ID = p.PT_ID
                WHERE t.OPERATION IN ('INSERT', 'UPDATE')
                
                UNION ALL
                
                SELECT 
                    t.LOG_ID,
                    t.PT_ID,
                    CASE t.OPERATION 
                        WHEN 'CHECK-UP' THEN 'CHECK UP'
                        ELSE t.OPERATION 
                    END as OPERATION,
                    t.MODIFIED_DATE,
                    p.PT_FNAME,
                    p.PT_LNAME
                FROM 
                    TRANSACTION_LOG_OLD_PT t
                    JOIN PATIENT_INFORMATION p ON t.PT_ID = p.PT_ID
                WHERE t.OPERATION IN ('CHECK-UP', 'IMMUNIZATION')
            ) AS combined_results
        )
        SELECT *
        FROM LatestOperations
        WHERE rn = 1  -- Only get the latest operation for each patient
        ORDER BY PT_ID ASC
        """
        all_patients_records = getallprocess(sql_all)

        # Get patients records (for patients tab)
        sql_patients = """
        WITH LatestOperations AS (
            SELECT 
                PT_ID,
                OPERATION,
                MODIFIED_DATE,
                LOG_ID,
                ROW_NUMBER() OVER (PARTITION BY PT_ID ORDER BY MODIFIED_DATE DESC) as rn
            FROM (
                SELECT 
                    PT_ID,
                    'UPDATED' as OPERATION,
                    MODIFIED_DATE,
                    LOG_ID
                FROM TRANSACTION_LOG 
                WHERE OPERATION = 'UPDATE'
                
                UNION ALL
                
                SELECT 
                    PT_ID,
                    OPERATION,
                    MODIFIED_DATE,
                    LOG_ID
                FROM TRANSACTION_LOG_OLD_PT
                WHERE OPERATION IN ('CHECK UP', 'IMMUNIZATION')
            ) combined
        )
        SELECT DISTINCT 
            p.PT_ID,
            p.PT_FNAME,
            p.PT_LNAME,
            t.OPERATION,
            t.MODIFIED_DATE,
            t.LOG_ID
        FROM PATIENT_INFORMATION p
        INNER JOIN LatestOperations t ON p.PT_ID = t.PT_ID
        WHERE p.ISACTIVE = 1
            AND t.rn = 1
        ORDER BY p.PT_ID ASC
        """
        
        # Get new patients records (for new-patients tab)
        sql_new = """
        WITH LatestOperations AS (
            SELECT 
                PT_ID,
                OPERATION,
                MODIFIED_DATE,
                ROW_NUMBER() OVER (PARTITION BY PT_ID ORDER BY MODIFIED_DATE DESC) as rn
            FROM (
                SELECT PT_ID, OPERATION, MODIFIED_DATE
                FROM TRANSACTION_LOG
                UNION ALL
                SELECT PT_ID, OPERATION, MODIFIED_DATE
                FROM TRANSACTION_LOG_OLD_PT
            ) all_operations
        )
        SELECT DISTINCT
            p.PT_ID,
            p.PT_FNAME,
            p.PT_LNAME,
            'INSERT' as OPERATION,
            t.MODIFIED_DATE,
            t.LOG_ID
        FROM PATIENT_INFORMATION p
        INNER JOIN TRANSACTION_LOG t ON p.PT_ID = t.PT_ID
        LEFT JOIN LatestOperations lo ON p.PT_ID = lo.PT_ID AND lo.rn = 1
        WHERE t.OPERATION = 'INSERT'
            AND p.ISACTIVE = 1
            AND t.MODIFIED_DATE >= DATEADD(day, -30, GETDATE())
            AND (lo.OPERATION = 'INSERT' OR lo.OPERATION IS NULL)  -- Only show if latest operation is INSERT
        ORDER BY p.PT_ID ASC
        """
        
        patients_records = getallprocess(sql_patients)
        new_patients_records = getallprocess(sql_new)
        
        print(f"Found {len(patients_records)} patient records")
        print(f"Found {len(new_patients_records)} new patient records")
        
    except Exception as e:
        print(f"Error fetching patient records: {e}")
        all_patients_records = []
        patients_records = []
        new_patients_records = []
    
    return render_template('reports.html', 
                         all_patients=all_patients_records,    # For all patients tab
                         patients=patients_records,            # For patients tab
                         new_patients=new_patients_records,    # For new patients tab
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))

@app.route('/summary')
def summary():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get monthly statistics
    sql_monthly = """
    SELECT 
        FORMAT(px.DATE, 'yyyy-MM') as month,
        COUNT(DISTINCT p.PT_ID) as patient_count,
        COUNT(DISTINCT i.VAX_ID) as immunization_count,
        COUNT(DISTINCT px.RX_ID) as prescription_count
    FROM PATIENT_INFORMATION p
    LEFT JOIN IMMUNIZATION_RECORD i ON p.PT_ID = i.PT_ID
    LEFT JOIN PRESCRIPTIONS px ON p.PT_ID = px.PT_ID
    WHERE px.DATE IS NOT NULL
    GROUP BY FORMAT(px.DATE, 'yyyy-MM')
    ORDER BY month DESC
    """
    
    monthly_stats = getallprocess(sql_monthly)
    return render_template('summary.html', 
                         monthly_stats=monthly_stats,
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))

@app.route('/details')
def details():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get detailed patient records
    sql = """
    SELECT 
        p.PT_ID,
        p.PT_FNAME,
        p.PT_LNAME,
        p.PT_MNAME,
        p.DT_OF_BIRTH,
        p.MT_NAME,
        p.FT_NAME,
        p.CON_NUM,
        p.EMAIL_ADD
    FROM PATIENT_INFORMATION p
    ORDER BY p.PT_LNAME, p.PT_FNAME
    """
    
    try:
        patients = getallprocess(sql)
        
        # Format dates for display
        for patient in patients:
            if patient['DT_OF_BIRTH']:
                patient['DT_OF_BIRTH'] = patient['DT_OF_BIRTH'].strftime('%Y-%m-%d')
        
        return render_template('details.html', 
                             patients=patients,
                             dr_name=session.get('dr_name', ''),
                             spclty=session.get('spclty', ''))
    except Exception as e:
        print(f"Error fetching patient details: {e}")
        flash("Error loading patient details", "error")
        return redirect(url_for('index'))

@app.route('/print_report/<int:patient_id>')
def print_report(patient_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get patient details
    patient = getpatientbyid(patient_id)
    if not patient:
        flash("Patient not found!", "error")
        return redirect(url_for('reports'))
    
    # Get immunization records
    sql_immunizations = """
    SELECT VAX, DOSAGE, DATE, REMARKS
    FROM IMMUNIZATION_RECORD
    WHERE PT_ID = ?
    ORDER BY DATE DESC
    """
    immunizations = getallprocess(sql_immunizations, (patient_id,))
    
    # Get prescription records
    sql_prescriptions = """
    SELECT px.DATE, px.FINDINGS, px.CONSULT, px.DR_INS, d.DR_NAME
    FROM PRESCRIPTIONS px
    LEFT JOIN DOCTOR d ON px.DR_ID = d.DR_ID
    WHERE px.PT_ID = ?
    ORDER BY px.DATE DESC
    """
    prescriptions = getallprocess(sql_prescriptions, (patient_id,))
    
    return render_template('print_report.html',
                         patient=patient,
                         immunizations=immunizations,
                         prescriptions=prescriptions)

@app.route('/patient/<int:patient_id>/info')
def patient_info(patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    sql = """
    SELECT 
        PT_ID,
        PT_FNAME,
        PT_LNAME,
        DT_OF_BIRTH,
        MT_NAME,
        FT_NAME,
        CON_NUM,
        EMAIL_ADD
    FROM PATIENT_INFORMATION
    WHERE PT_ID = ?
    """
    
    try:
        patient_info = getallprocess(sql, (patient_id,))
        return jsonify(patient_info[0] if patient_info else {})
    except Exception as e:
        print(f"Error fetching patient info: {e}")
        return jsonify({'error': 'Failed to fetch patient info'}), 500

@app.route('/patient-records')
def patient_records():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    patients = getallrecords('PATIENT_INFORMATION')
    for patient in patients:
        pt_fname = patient.get('PT_FNAME', '')
        pt_mname = patient.get('PT_MNAME', '')
        pt_lname = patient.get('PT_LNAME', '')
        
        if pt_mname:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_mname} {pt_lname}".strip()
        else:
            patient['PT_FULLNAME'] = f"{pt_fname} {pt_lname}".strip()
    
    return render_template('patient_records.html', 
                         patients=patients,
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))

@app.route('/immunization')
def immunization():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Modified SQL to get all patients with their immunization records
    sql = """
    SELECT DISTINCT
        p.PT_ID,
        p.PT_FNAME,
        p.PT_LNAME,
        p.DT_OF_BIRTH
    FROM PATIENT_INFORMATION p
    LEFT JOIN IMMUNIZATION_RECORD i ON p.PT_ID = i.PT_ID
    ORDER BY p.PT_LNAME, p.PT_FNAME
    """
    
    try:
        immunization_records = getallprocess(sql)
        
        # Format dates for display
        for record in immunization_records:
            if record['DT_OF_BIRTH']:
                record['DT_OF_BIRTH'] = record['DT_OF_BIRTH'].strftime('%Y-%m-%d')
        
        return render_template('immunization.html', 
                             immunization_records=immunization_records,
                             dr_name=session.get('dr_name', ''),
                             spclty=session.get('spclty', ''))
    except Exception as e:
        print(f"Error fetching immunization records: {e}")
        flash("Error loading immunization records", "error")
        return redirect(url_for('index'))

@app.route('/patient/<int:patient_id>/immunizations')
def patient_immunizations(patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    sql = """
    SELECT 
        VAX,
        DOSAGE,
        FORMAT([DATE], 'yyyy-MM-dd') as DATE,
        REMARKS
    FROM IMMUNIZATION_RECORD
    WHERE PT_ID = ?
    ORDER BY [DATE] DESC
    """
    
    try:
        immunizations = getallprocess(sql, (patient_id,))
        return jsonify(immunizations)
    except Exception as e:
        print(f"Error fetching immunization records: {e}")
        return jsonify({'error': 'Failed to fetch immunization records'}), 500

@app.route('/add_immunization', methods=['POST'])
def add_immunization():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.json
        print("Received data:", data)
        
        # Get the doctor's ID from the session
        dr_id = session.get('user', {}).get('EMP_ID')
        if not dr_id:
            return jsonify({'error': 'Doctor ID not found in session'}), 400
        
        # Convert dr_id to int if it's stored as string
        dr_id = int(dr_id)
        patient_id = int(data['patient_id'])
        
        # Validate patient exists
        check_patient_sql = "SELECT PT_ID FROM PATIENT_INFORMATION WHERE PT_ID = ?"
        patient_exists = getallprocess(check_patient_sql, (patient_id,))
        if not patient_exists:
            return jsonify({'error': 'Invalid patient ID'}), 400
            
        # Validate doctor exists
        check_doctor_sql = "SELECT DR_ID FROM DOCTOR WHERE DR_ID = ?"
        doctor_exists = getallprocess(check_doctor_sql, (dr_id,))
        if not doctor_exists:
            return jsonify({'error': 'Invalid doctor ID'}), 400
        
        # Insert the immunization record
        sql = """
        INSERT INTO IMMUNIZATION_RECORD 
        (VAX, DOSAGE, [DATE], REMARKS, PT_ID, DR_ID)
        VALUES 
        (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data['vaccine'],
            float(data['dosage']),
            data['date'],
            data['remarks'] if data['remarks'] else None,
            patient_id,
            dr_id
        )
        
        print("Executing SQL with params:", params)
        
        cursor = db.cursor()
        try:
            cursor.execute(sql, params)
            db.commit()
            print("Successfully inserted immunization record")
            return jsonify({'message': 'Immunization record added successfully'}), 200
            
        except Exception as e:
            db.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Error adding immunization record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/patient/<int:patient_id>/checkups')
def patient_checkups(patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    sql = """
    SELECT 
        FORMAT([DATE], 'yyyy-MM-dd') as DATE,
        FINDINGS
    FROM PRESCRIPTIONS
    WHERE PT_ID = ?
    ORDER BY [DATE] DESC
    """
    
    try:
        checkups = getallprocess(sql, (patient_id,))
        return jsonify(checkups)
    except Exception as e:
        print(f"Error fetching checkup records: {e}")
        return jsonify({'error': 'Failed to fetch checkup records'}), 500

@app.route('/patient/<int:patient_id>/list')
def patient_list(patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    sql = """
    SELECT 
        FORMAT(p.[DATE], 'yyyy-MM-dd') as DATE,
        p.FINDINGS,
        p.AGE,
        pi.PT_FNAME,
        pi.PT_LNAME,
        FORMAT(pi.DT_OF_BIRTH, 'yyyy-MM-dd') as DT_OF_BIRTH
    FROM PRESCRIPTIONS p
    JOIN PATIENT_INFORMATION pi ON p.PT_ID = pi.PT_ID
    WHERE p.PT_ID = ?
    ORDER BY p.[DATE] DESC
    """
    
    try:
        patient_list = getallprocess(sql, (patient_id,))
        return jsonify(patient_list)
    except Exception as e:
        print(f"Error fetching patient list: {e}")
        return jsonify({'error': 'Failed to fetch patient list'}), 500

@app.route('/patient/<int:patient_id>/operations')
def patient_operations(patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check if tables exist
        check_sql = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TRANSACTION_LOG')
        OR NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TRANSACTION_LOG_OLD_PT')
        BEGIN
            -- Return basic patient info if tables don't exist
            SELECT 
                'INSERTED' as OPERATION,
                GETDATE() as MODIFIED_DATE
            FROM PATIENT_INFORMATION
            WHERE PT_ID = ?
        END
        ELSE
        BEGIN
            -- Use the original query if tables exist
            SELECT 
                CASE t.OPERATION 
                    WHEN 'INSERT' THEN 'INSERTED'
                    WHEN 'UPDATE' THEN 'UPDATED'
                    WHEN 'CHECK-UP' THEN 'CHECK UP'
                    ELSE t.OPERATION 
                END as OPERATION,
                t.MODIFIED_DATE
            FROM (
                SELECT 
                    PT_ID,
                    OPERATION,
                    MODIFIED_DATE
                FROM TRANSACTION_LOG
                WHERE PT_ID = ?
                UNION ALL
                SELECT 
                    PT_ID,
                    OPERATION,
                    MODIFIED_DATE
                FROM TRANSACTION_LOG_OLD_PT
                WHERE PT_ID = ?
            ) t
            ORDER BY t.MODIFIED_DATE DESC
        END
        """
        
        operations = getallprocess(check_sql, (patient_id, patient_id, patient_id))
        
        # Ensure we have at least one record
        if not operations:
            operations = [{
                'OPERATION': 'INSERTED',
                'MODIFIED_DATE': datetime.now()
            }]
        
        return jsonify(operations)
    except Exception as e:
        print(f"Error fetching operations: {e}")
        return jsonify({'error': 'Failed to fetch operations'}), 500

@app.route('/reports/new-patients')
def new_patients_tab():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        # Check if TRANSACTION_LOG exists and get records accordingly
        sql_new = """
        IF EXISTS (SELECT * FROM sys.tables WHERE name = 'TRANSACTION_LOG')
        BEGIN
            SELECT 
                t.LOG_ID,
                t.PT_ID,
                t.OPERATION,
                t.MODIFIED_DATE,
                p.PT_FNAME,
                p.PT_LNAME,
                'INSERTED' as OPERATION
            FROM 
                TRANSACTION_LOG t
                JOIN PATIENT_INFORMATION p ON t.PT_ID = p.PT_ID
            WHERE 
                t.OPERATION = 'INSERT'
                AND t.MODIFIED_DATE >= DATEADD(day, -30, GETDATE())
            ORDER BY t.MODIFIED_DATE DESC
        END
        ELSE
        BEGIN
            -- Return empty result set with same structure
            SELECT TOP 0
                CAST(0 as INT) as LOG_ID,
                PT_ID,
                CAST('INSERT' as VARCHAR(50)) as OPERATION,
                GETDATE() as MODIFIED_DATE,
                PT_FNAME,
                PT_LNAME,
                CAST('INSERTED' as VARCHAR(50)) as OPERATION
            FROM PATIENT_INFORMATION
            WHERE 1 = 0
        END
        """
        new_patients_records = getallprocess(sql_new)
    except Exception as e:
        print(f"Error fetching new patients: {e}")
        new_patients_records = []
    
    return render_template('reports.html', 
                         all_patients=new_patients_records,
                         patients=new_patients_records,
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))

@app.route('/reports/all-patients')
def all_patients_tab():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        # Check if tables exist and get all records
        sql_all = """
        IF EXISTS (SELECT * FROM sys.tables WHERE name = 'TRANSACTION_LOG')
        AND EXISTS (SELECT * FROM sys.tables WHERE name = 'TRANSACTION_LOG_OLD_PT')
        BEGIN
            SELECT * FROM (
                SELECT 
                    t.LOG_ID,
                    t.PT_ID,
                    CASE t.OPERATION 
                        WHEN 'INSERT' THEN 'INSERTED'
                        WHEN 'UPDATE' THEN 'UPDATED'
                        ELSE t.OPERATION 
                    END as OPERATION,
                    t.MODIFIED_DATE,
                    p.PT_FNAME,
                    p.PT_LNAME
                FROM 
                    TRANSACTION_LOG t
                    JOIN PATIENT_INFORMATION p ON t.PT_ID = p.PT_ID
                WHERE t.OPERATION IN ('INSERT', 'UPDATE')
                
                UNION ALL
                
                SELECT 
                    t.LOG_ID,
                    t.PT_ID,
                    CASE t.OPERATION 
                        WHEN 'CHECK-UP' THEN 'CHECK UP'
                        ELSE t.OPERATION 
                    END as OPERATION,
                    t.MODIFIED_DATE,
                    p.PT_FNAME,
                    p.PT_LNAME
                FROM 
                    TRANSACTION_LOG_OLD_PT t
                    JOIN PATIENT_INFORMATION p ON t.PT_ID = p.PT_ID
                WHERE t.OPERATION IN ('CHECK-UP', 'IMMUNIZATION')
            ) AS combined_results
            ORDER BY MODIFIED_DATE DESC
        END
        ELSE
        BEGIN
            -- Return basic patient info if tables don't exist
            SELECT 
                CAST(0 as INT) as LOG_ID,
                PT_ID,
                CAST('INSERTED' as VARCHAR(50)) as OPERATION,
                GETDATE() as MODIFIED_DATE,
                PT_FNAME,
                PT_LNAME
            FROM PATIENT_INFORMATION
        END
        """
        all_patients_records = getallprocess(sql_all)
    except Exception as e:
        print(f"Error fetching all patients: {e}")
        all_patients_records = []
    
    return render_template('reports.html', 
                         all_patients=all_patients_records,
                         patients=all_patients_records,
                         dr_name=session.get('dr_name', ''),
                         spclty=session.get('spclty', ''))

@app.route("/add_vax", methods=["POST"])
def add_vax():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        pt_id = request.form.get('pt_id')
        vaccine = request.form.get('vaccine')
        total_doses = int(request.form.get('dosage', 0))
        date = request.form.get('date1')
        remarks = request.form.get('remarks', '')
        user = session.get('user', {})
        dr_id = user.get('EMP_ID')

        # First check if this record exists in the database
        check_sql = """
            SELECT COUNT(*) as count, MAX(DOSAGE) as current_doses
            FROM IMMUNIZATION_RECORD 
            WHERE PT_ID = ? AND VAX = ? AND [DATE] IS NOT NULL
        """
        result = getallprocess(check_sql, (pt_id, vaccine.strip().upper() if vaccine else ''))
        is_edit = result[0]['count'] > 0
        current_doses = result[0]['current_doses'] or 0

        if is_edit:
            # For editing, only validate the date field
            if not date:
                flash("Please enter the vaccination date.", "error")
                return redirect(url_for('pat_info', patient_id=pt_id))
                
            next_dose = current_doses + 1
            if next_dose <= total_doses:
                sql = """
                    INSERT INTO IMMUNIZATION_RECORD (VAX, DOSAGE, [DATE], REMARKS, PT_ID, DR_ID)
                    VALUES (?, ?, ?, ?, ?, ?);
                    DECLARE @VAX_ID INT = SCOPE_IDENTITY();
                    INSERT INTO PATIENT_IMMUNIZATION (PT_ID, VAX_ID) VALUES (?, @VAX_ID);
                """
                postprocess(sql, (vaccine.strip().upper(), next_dose, date, remarks or '', pt_id, dr_id, pt_id))
                flash("Additional vaccination date added successfully!", "success")
        else:
            # For new records, validate all required fields
            if not all([pt_id, vaccine, total_doses, date, dr_id]):
                flash("Please fill in all required fields.", "error")
                return redirect(url_for('pat_info', patient_id=pt_id))

            sql = """
                INSERT INTO IMMUNIZATION_RECORD (VAX, DOSAGE, [DATE], REMARKS, PT_ID, DR_ID)
                VALUES (?, ?, ?, ?, ?, ?);
                DECLARE @VAX_ID INT = SCOPE_IDENTITY();
                INSERT INTO PATIENT_IMMUNIZATION (PT_ID, VAX_ID) VALUES (?, @VAX_ID);
            """
            postprocess(sql, (vaccine.strip().upper(), total_doses, date, remarks or '', pt_id, dr_id, pt_id))
            flash("Vaccination record added successfully!", "success")

    except Exception as e:
        flash(f"Error processing vaccination record: {str(e)}", "error")
    
    return redirect(url_for('pat_info', patient_id=pt_id))
    

@app.route("/update_vaccine", methods=["POST"])
def update_vaccine():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        pt_id = request.form.get('pt_id')
        vaccine_name = request.form.get('vaccine_name')
        next_dose_date = request.form.get('next_dose_date')
        remarks = request.form.get('remarks')
        
        # Get the current doctor's ID from the session
        dr_id = session.get('user', {}).get('EMP_ID')
        
        if all([pt_id, vaccine_name, dr_id]):
            # Get current dose number
            current_doses = int(get_current_doses(pt_id, vaccine_name))
            
            # Insert remaining doses
            for i in range(current_doses + 1, 4):  # Max 3 doses
                dose_date = request.form.get(f'dose_date_{i}')
                dose_remarks = request.form.get(f'dose_remarks_{i}')
                
                if dose_date:  # Only insert if date is provided
                    sql = """
                        INSERT INTO IMMUNIZATION_RECORD (VAX, DOSAGE, [DATE], REMARKS, PT_ID, DR_ID)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    postprocess(sql, (vaccine_name, i, dose_date, dose_remarks, pt_id, dr_id))
            
            flash("Vaccine dose added successfully!", "success")
        else:
            flash("Missing required information.", "error")
            
    except Exception as e:
        flash(f"Error updating vaccine: {str(e)}", "error")
    
    return redirect(url_for('pat_info', patient_id=pt_id))

@app.route('/get_vaccine_dates/<vaccine_name>/<int:patient_id>')
def get_vaccine_dates(vaccine_name, patient_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    sql = """
    SELECT DOSAGE, [DATE], REMARKS
    FROM IMMUNIZATION_RECORD
    WHERE PT_ID = ? AND VAX = ?
    ORDER BY DOSAGE
    """
    
    try:
        doses = getallprocess(sql, (patient_id, vaccine_name))
        return jsonify(doses)
    except Exception as e:
        print(f"Error fetching vaccine dates: {e}")
        return jsonify({'error': 'Failed to fetch vaccine dates'}), 500

if __name__ == '__main__':
    app.run(debug=True)