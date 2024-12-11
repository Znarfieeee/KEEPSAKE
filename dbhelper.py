import pyodbc as odbc

try:
    db = odbc.connect(
        'DRIVER=ODBC Driver 11 for SQL Server;' 
        'SERVER=DESKTOP-RPF16C9;'                  
        'DATABASE=KEEPSAKE;'           
        'Trusted_Connection=yes;'          
        'Encrypt=yes;'                       
        'TrustServerCertificate=yes;'        
    )
    print('Connected to database')
    
    def getallprocess(sql: str, params=()) -> list:
        cursor = db.cursor()
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return data
        
    def postprocess(sql: str, params=()) -> bool:
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        cursor.close()
        return cursor.rowcount > 0
    
    def getallrecords(table: str) -> list:
        sql = f"SELECT * FROM [{table}]"
        return getallprocess(sql)
    
    def getpatientbyid(patient_id: str) -> dict:
        sql = "SELECT * FROM PATIENT_INFORMATION WHERE PT_ID = ?"
        result = getallprocess(sql, (patient_id,))
        return result[0] if result else None

    def getprescriptionsbypatientid(patient_id: str) -> list:
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

except odbc.Error as ex:
    print('Connection Failed', ex)
