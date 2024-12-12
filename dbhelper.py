import pyodbc as odbc
from pyodbc import *


try:
    db = odbc.connect(
        'DRIVER=ODBC Driver 11 for SQL Server;' 
        'SERVER=PRNSDAGREAT;'                  
        'DATABASE=KEEPSAKE;'           
        'Trusted_Connection=yes;'          
        'Encrypt=yes;'                       
        'TrustServerCertificate=yes;'        
    )
    print('Connected to database')
    
    def getallprocess(sql:str, params=())-> list:
        cursor = db.cursor()
        cursor.execute(sql, params)
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return data
        
    def postprocess(sql:str, params=())->bool:
        cursor = db.cursor()
        cursor.execute(sql, params)
        db.commit()
        cursor.close()
        return cursor.rowcount > 0
    
    def addprocess(query, params)->bool:
        cursor = db.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def getallrecords(table:str) -> list:
        sql = f"SELECT * FROM [{table}]"
        return getallprocess(sql)
    
    def deactivatepatient(patient_id:str) -> bool:
        sql = "UPDATE PATIENT_INFORMATION SET ISACTIVE = 0 WHERE PT_ID =?"
        return postprocess(sql, (patient_id,))
    
    def getpatientbyid(patient_id: str) -> dict:
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

    def addnewprescription(patient_id: str, prescription_date: str, diagnosis: str) -> bool:
        """Add a new prescription to the database."""
        try:
            sql = """
                INSERT INTO PRESCRIPTIONS (PT_ID, [DATE], FINDINGS)
                VALUES (?, ?, ?)
            """
            success = postprocess(sql, (patient_id, prescription_date, diagnosis))
            return success
        except Exception as e:
            print(f"Database Error in addnewprescription: {e}")
            return False
    
    
except odbc.Error as ex:
    print('Connection Failed', ex) 

    


