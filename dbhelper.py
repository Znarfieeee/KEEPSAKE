import pyodbc as odbc

try:
    # Establish database connection
    db = odbc.connect(
        'DRIVER=ODBC Driver 11 for SQL Server;' 
        'SERVER=PRNSDAGREAT;'                  
        'DATABASE=KEEPSAKE;'           
        'Trusted_Connection=yes;'          
        'Encrypt=yes;'                       
        'TrustServerCertificate=yes;'        
    )
    print('Connected to database')
    
    def getallprocess(sql: str, params=()) -> list:
        """Fetch all rows from a query as a list of dictionaries."""
        cursor = db.cursor()
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return data
        
    def postprocess(sql: str, params=()) -> bool:
        """Execute an update/insert query and return success status."""
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        cursor.close()
        return cursor.rowcount > 0
    
    def addprocess(query: str, params) -> dict:
        """Execute an insert query and return the inserted row if available."""
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()  # Fetch result for generated keys or other output
        db.commit()
        cursor.close()
        return result
    
    def getallrecords(table: str) -> list:
        """Fetch all records from a specified table."""
        sql = f"SELECT * FROM [{table}]"
        return getallprocess(sql)
    
    def deactivatepatient(patient_id: str) -> bool:
        """Deactivate a patient by setting ISACTIVE to 0."""
        sql = "UPDATE PATIENT_INFORMATION SET ISACTIVE = 0 WHERE PT_ID = ?"
        return postprocess(sql, (patient_id,))
    
    def getpatientbyid(patient_id: str) -> dict:
        """Fetch a patient's details by their ID."""
        sql = "SELECT * FROM PATIENT_INFORMATION WHERE PT_ID = ?"
        result = getallprocess(sql, (patient_id,))
        return result[0] if result else None
    
    def getprescriptionsbypatientid(patient_id: str) -> list:
        """Fetch all prescriptions for a given patient ID."""
        sql = """
            SELECT RX_ID, [DATE] AS PRESCRIPTION_DATE, FINDINGS AS DIAGNOSIS
            FROM PRESCRIPTIONS
            WHERE PT_ID = ?
        """
        return getallprocess(sql, (patient_id,))
    
    def get_vaccines_for_patient(patient_id):
        sql = """
        SELECT VAX, DOSAGE, [DATE], REMARKS
        FROM IMMUNIZATION_RECORD
        WHERE PT_ID = ?
        ORDER BY [DATE] DESC
        """
        return getallprocess(sql, (patient_id,))
    
    def get_current_doses(patient_id, vaccine_name):
        sql = """
        SELECT MAX(DOSAGE) as current_doses
        FROM IMMUNIZATION_RECORD
        WHERE PT_ID = ? AND VAX = ?
        """
        result = getallprocess(sql, (patient_id, vaccine_name))
        return result[0]['current_doses'] if result and result[0]['current_doses'] else 0
    
except odbc.Error as ex:
    print('Connection Failed:', ex)
