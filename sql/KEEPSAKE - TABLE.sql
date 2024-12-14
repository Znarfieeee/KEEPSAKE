CREATE DATABASE KEEPSAKE;
GO

USE KEEPSAKE;
GO

CREATE TABLE PATIENT_INFORMATION (
    PT_ID INT IDENTITY(1000,1) PRIMARY KEY,
    PT_LNAME VARCHAR(30) NOT NULL,
    PT_FNAME VARCHAR(20) NOT NULL,
    PT_MNAME VARCHAR(20) NULL,
    DT_OF_BIRTH DATE NOT NULL,
    MT_NAME VARCHAR(60) NULL,
    FT_NAME VARCHAR(60) NULL,
    CON_NUM VARCHAR(60) NULL,
    EMAIL_ADD VARCHAR(60) NULL,
	PT_FULLNAME AS PT_LNAME + ' ' + PT_LNAME,
	ISACTIVE BIT DEFAULT 1 NOT NULL
);


CREATE TABLE DOCTOR (
    DR_ID INT NOT NULL PRIMARY KEY,
    DR_NAME VARCHAR(60) NOT NULL,
    DEPPT VARCHAR(60) NOT NULL,
    SPLTY VARCHAR(30) NOT NULL,
    CONTACT VARCHAR(15) NULL
);

CREATE TABLE ACCOUNTS (
    USER_ID INT IDENTITY(1,1) PRIMARY KEY,
    USERTYPE BIT NOT NULL,
    PASSWORD VARCHAR(15) NOT NULL,
    EMP_ID CHAR(15) NULL,
    USER_LNAME VARCHAR(60) NOT NULL,
    USER_FNAME VARCHAR(60) NOT NULL
);

CREATE TABLE PRESCRIPTIONS (
    RX_ID INT IDENTITY(1,1) PRIMARY KEY,
    CU_TYPE TINYINT NOT NULL,
    [DATE] DATE NOT NULL,
    AGE INT NOT NULL,
    FINDINGS NVARCHAR(MAX) NOT NULL,
    CONSULT NVARCHAR(MAX) NULL,
    DR_INS NVARCHAR(MAX) NOT NULL,
    RETURN_DT DATE NULL,
    PT_ID INT REFERENCES PATIENT_INFORMATION(PT_ID),
    DR_ID INT REFERENCES DOCTOR(DR_ID)
);

CREATE TABLE ATPMC_MSRMT (
    AM_ID INT IDENTITY(1,1) PRIMARY KEY,
    WEIGHT FLOAT NOT NULL,
    LENGTH FLOAT NOT NULL,
    HEAD_CC FLOAT NOT NULL,
    CHEST_CC FLOAT NOT NULL,
    ABDML_GT FLOAT NOT NULL,
    PT_ID INT REFERENCES PATIENT_INFORMATION(PT_ID),
    RX_ID INT REFERENCES PRESCRIPTIONS(RX_ID)
);

CREATE TABLE SCREENING_TEST (
    ST_ID INT IDENTITY(1,1) PRIMARY KEY,
    ENS_DATE DATE NOT NULL,
    ENS_REMARKS BIT NOT NULL,
    NHS_DATE DATE NOT NULL,
    NHS_REAR BIT NOT NULL,
    NHS_LEAR BIT NOT NULL,
    POS_CCHD_DATE DATE NULL,
    POS_CCHD_RHAND BIT NOT NULL,
    POS_CCHD_LHAND BIT NOT NULL,
    ROR_DATE DATE NULL,
    ROR_REMARKS VARCHAR(60) NULL,
    PT_ID INT REFERENCES PATIENT_INFORMATION(PT_ID)
);

CREATE TABLE IMMUNIZATION_RECORD (
    VAX_ID INT IDENTITY(1,1) PRIMARY KEY,
    VAX VARCHAR(60) NOT NULL,
    DOSAGE FLOAT NOT NULL,
    [DATE] DATE NOT NULL,
    REMARKS NVARCHAR(MAX) NULL,
    PT_ID INT REFERENCES PATIENT_INFORMATION(PT_ID),
    DR_ID INT REFERENCES DOCTOR(DR_ID)
);

CREATE TABLE PATIENT_IMMUNIZATION (
    PI_ID INT IDENTITY(1,1) PRIMARY KEY,
    PT_ID INT REFERENCES PATIENT_INFORMATION(PT_ID),
    VAX_ID INT REFERENCES IMMUNIZATION_RECORD(VAX_ID)
);


INSERT INTO IMMUNIZATION_RECORD (VAX, DOSAGE, [DATE], REMARKS)
VALUES ('FLU VACCINE', 30, '10-22-2024', 'PATIENT IN GOOD CONDITION');

INSERT INTO PATIENT_IMMUNIZATION (PT_ID, VAX_ID)
VALUES (1000, 1);
	

---- TABLE PARA SA TRIGGERZZZZ -----
CREATE TABLE [TRANSACTION_LOG] (
	LOG_ID INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
	PT_ID INT NOT NULL,
	OPERATION NVARCHAR(15) NOT NULL,
	MODIFIED_DATE DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE TRANSACTION_LOG_OLD_PT (
	LOG_ID INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
	PT_ID INT NOT NULL,
	OPERATION NVARCHAR(15) NOT NULL,
	MODIFIED_DATE DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


---- TRIGGERZ FROM PT_INFORMATION TO TRANSACTION_LOG -------

-- INSERT --
CREATE TRIGGER TRIGGER_INSERT_PATIENT
ON PATIENT_INFORMATION
AFTER INSERT
AS
BEGIN
    INSERT INTO TRANSACTION_LOG (PT_ID, OPERATION, MODIFIED_DATE)
    SELECT PT_ID, 'INSERT', GETDATE()
    FROM INSERTED;
END;
GO

-- UPDATE --
CREATE TRIGGER TRIGGER_UPDATE_PATIENT
ON PATIENT_INFORMATION
AFTER UPDATE
AS
BEGIN
    -- Debug print to see what's in INSERTED table
    DECLARE @Debug TABLE (PT_ID INT, ISACTIVE BIT);
    INSERT INTO @Debug
    SELECT PT_ID, ISACTIVE FROM INSERTED;
    
    -- Log all updates with explicit CAST to ensure proper comparison
    INSERT INTO TRANSACTION_LOG (PT_ID, OPERATION, MODIFIED_DATE)
    SELECT PT_ID, 
           CASE 
               WHEN CAST(ISACTIVE AS BIT) = 0 THEN 'DEACTIVATED'
               ELSE 'UPDATE'
           END AS OPERATION,
           GETDATE()
    FROM INSERTED;

    -- Print debug info
    SELECT * FROM @Debug;
END;
GO

---- TRIGGERZ FROM PRESCRIPTION TO TRANSACTION_LOG -------

-- INSERT --
CREATE TRIGGER TRIGGER_ADD_PRESCRIPTION
ON PRESCRIPTIONS
AFTER INSERT
AS
BEGIN
    INSERT INTO TRANSACTION_LOG_OLD_PT (PT_ID, OPERATION, MODIFIED_DATE)
    SELECT PT_ID, 'CHECK-UP', GETDATE()
    FROM INSERTED;
END;
GO

CREATE TRIGGER TRIGGER_ADD_VAX
ON PATIENT_IMMUNIZATION
AFTER INSERT
AS
BEGIN
    INSERT INTO TRANSACTION_LOG_OLD_PT (PT_ID, OPERATION, MODIFIED_DATE)
    SELECT PT_ID, 'IMMUNIZATION', GETDATE()
    FROM INSERTED;
END;
GO
