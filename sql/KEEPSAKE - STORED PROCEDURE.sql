-- ================================================
-- Template generated from Template Explorer using:
-- Create Procedure (New Menu).SQL
--
-- Use the Specify Values for Template Parameters 
-- command (Ctrl-Shift-M) to fill in the parameter 
-- values below.
--
-- This block of comments will not be included in
-- the definition of the procedure.
-- ================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

USE KEEPSAKE;
GO
-- =============================================
-- Author:		GROUP 10
-- Create date: 7/11/24
-- Description:	KEEPSAKE STORED PROCEDURE
-- =============================================

CREATE PROCEDURE SP_PT_INFORMATION
    @PT_ID INT = NULL,
    @PT_LNAME VARCHAR(30),
    @PT_FNAME VARCHAR(20),
    @PT_MNAME VARCHAR(20) = NULL, 
    @DT_OF_BIRTH DATE,          
    @MT_NAME VARCHAR(60),
    @FT_NAME VARCHAR(60),
    @CON_NUM VARCHAR(60),
    @EMAIL_ADD VARCHAR(60)
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM PATIENT_INFORMATION WHERE PT_ID = @PT_ID)
    BEGIN
        -- Update existing record
        UPDATE PATIENT_INFORMATION
        SET PT_LNAME = UPPER(@PT_LNAME),
            PT_FNAME = UPPER(@PT_FNAME),
            PT_MNAME = CASE WHEN @PT_MNAME IS NULL THEN PT_MNAME ELSE UPPER(@PT_MNAME) END,
            DT_OF_BIRTH = CONVERT(DATE, @DT_OF_BIRTH), 
            MT_NAME = UPPER(@MT_NAME),
            FT_NAME = UPPER(@FT_NAME),
            CON_NUM = UPPER(@CON_NUM),
            EMAIL_ADD = UPPER(@EMAIL_ADD)
        WHERE PT_ID = @PT_ID;
		SELECT SCOPE_IDENTITY() AS PT_ID;
    END
    ELSE
    BEGIN
        -- Insert new record
        INSERT INTO PATIENT_INFORMATION (PT_LNAME, PT_FNAME, PT_MNAME, DT_OF_BIRTH, MT_NAME, FT_NAME, CON_NUM, EMAIL_ADD)
        VALUES (
            UPPER(@PT_LNAME),
            UPPER(@PT_FNAME),
            UPPER(@PT_MNAME), 
            CONVERT(DATE, @DT_OF_BIRTH), 
            UPPER(@MT_NAME),
            UPPER(@FT_NAME),
            UPPER(@CON_NUM),
            UPPER(@EMAIL_ADD)
        );
		SELECT SCOPE_IDENTITY() AS PT_ID;
    END
END;
GO



CREATE PROCEDURE SP_DOCTOR
	@DR_ID INT = NULL,
	@DR_NAME VARCHAR(60),
	@DEPPT VARCHAR(60),
	@SPLTY VARCHAR(30),
	@CONTACT VARCHAR(15)

AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM DOCTOR WHERE DR_ID = @DR_ID)
    BEGIN
        UPDATE DOCTOR
        SET DR_ID = @DR_ID,
            DR_NAME = UPPER(@DR_NAME),
            DEPPT = UPPER(@DEPPT),
			SPLTY = UPPER(@SPLTY),
			CONTACT = UPPER(@CONTACT)

            
        WHERE DR_ID = @DR_ID;
    END
    ELSE
    BEGIN
        INSERT INTO DOCTOR (DR_ID, DR_NAME, DEPPT, SPLTY, CONTACT)
        VALUES (@DR_ID, UPPER(@DR_NAME),UPPER(@DEPPT), UPPER(@SPLTY), UPPER(@CONTACT));
    END
END
GO

CREATE PROCEDURE SP_ACCOUNTS
    @USER_ID INT = NULL,
    @USERTYPE BIT,
    @PASSWORD VARCHAR(15),
    @EMP_ID CHAR(15) = NULL,
    @USER_LNAME VARCHAR(60),
    @USER_FNAME VARCHAR(60)
AS
BEGIN
    SET NOCOUNT ON;

    -- Check if the record exists
    IF EXISTS (SELECT 1 FROM ACCOUNTS WHERE USER_ID = @USER_ID)
    BEGIN
        -- Update the existing record
        UPDATE ACCOUNTS
        SET 
            USERTYPE = @USERTYPE,
            PASSWORD = @PASSWORD,
            EMP_ID = @EMP_ID,
            USER_LNAME = UPPER(@USER_LNAME),
            USER_FNAME = UPPER(@USER_FNAME)
        WHERE USER_ID = @USER_ID;
    END
    ELSE
    BEGIN
        -- Insert a new record
        INSERT INTO ACCOUNTS (USERTYPE, PASSWORD, EMP_ID, USER_LNAME, USER_FNAME)
        VALUES (@USERTYPE, @PASSWORD, @EMP_ID, UPPER(@USER_LNAME), UPPER(@USER_FNAME));
    END
END
GO

ALTER PROCEDURE SP_PRESCRIPTIONS
    @RX_ID INT = NULL,
    @CU_TYPE TINYINT,
    @DATE DATETIME,
    @AGE INT,
    @FINDINGS NVARCHAR(MAX),
    @CONSULT NVARCHAR(MAX) = NULL,
    @DR_INS NVARCHAR(MAX),
    @RETURN_DT DATETIME = NULL,
    @PT_ID INT,
    @DR_ID INT
AS

BEGIN
    SET NOCOUNT ON;
    BEGIN
        INSERT INTO PRESCRIPTIONS (CU_TYPE, [DATE], AGE, FINDINGS, CONSULT, DR_INS, RETURN_DT, PT_ID, DR_ID)
        VALUES (@CU_TYPE, @DATE, @AGE, @FINDINGS, @CONSULT, @DR_INS, @RETURN_DT, @PT_ID, @DR_ID);
    END
END
GO

ALTER PROCEDURE SP_ATPMC_MSRMT
    @AM_ID INT = NULL,
    @WEIGHT FLOAT,
    @LENGTH FLOAT,
    @HEAD_CC FLOAT,
    @CHEST_CC FLOAT,
    @ABDML_GT FLOAT,
    @PT_ID INT,
    @RX_ID INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN
        INSERT INTO ATPMC_MSRMT (WEIGHT, LENGTH, HEAD_CC, CHEST_CC, ABDML_GT, PT_ID, RX_ID)
        VALUES (@WEIGHT, @LENGTH, @HEAD_CC, @CHEST_CC, @ABDML_GT, @PT_ID, @RX_ID);
    END
END
GO

ALTER PROCEDURE SP_SCREENING_TEST
    @ST_ID INT = NULL,
    @ENS_DATE DATE,
    @ENS_REMARKS BIT,
    @NHS_DATE DATE,
    @NHS_REAR BIT,
    @NHS_LEAR BIT,
    @POS_CCHD_DATE DATE = NULL,
    @POS_CCHD_RHAND BIT,
    @POS_CCHD_LHAND BIT,
    @ROR_DATE DATE = NULL,
    @ROR_REMARKS VARCHAR(60) = NULL,
    @PT_ID INT
AS
BEGIN
    SET NOCOUNT ON;

              
    BEGIN
        INSERT INTO SCREENING_TEST (ENS_DATE, ENS_REMARKS, NHS_DATE, NHS_REAR, NHS_LEAR, POS_CCHD_DATE, POS_CCHD_RHAND, POS_CCHD_LHAND, ROR_DATE, ROR_REMARKS, PT_ID)
        VALUES (@ENS_DATE, @ENS_REMARKS, @NHS_DATE, @NHS_REAR, @NHS_LEAR, @POS_CCHD_DATE, @POS_CCHD_RHAND, @POS_CCHD_LHAND, @ROR_DATE, @ROR_REMARKS, @PT_ID);
    END
END
GO

ALTER PROCEDURE SP_IMMUNIZATION_RECORD
    @VAX_ID INT = NULL,
    @VAX VARCHAR(60),
    @DOSAGE FLOAT,
    @DATE DATE,
    @REMARKS NVARCHAR(MAX) = NULL,
    @PT_ID INT,
    @DR_ID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN
        INSERT INTO IMMUNIZATION_RECORD (VAX, DOSAGE, [DATE], REMARKS, PT_ID, DR_ID)
        VALUES (@VAX, @DOSAGE, @DATE, @REMARKS, @PT_ID, @DR_ID);
    END
END
GO

ALTER PROCEDURE SP_PATIENT_IMMUNIZATION
    @PI_ID INT = NULL,
    @PT_ID INT,
    @VAX_ID INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN
        INSERT INTO PATIENT_IMMUNIZATION (PT_ID, VAX_ID)
        VALUES (@PT_ID, @VAX_ID);
    END
END
GO

-- STORED PROCEDURE FOR REPORTS (NEW PATIENTS)
ALTER PROCEDURE SP_NEW_PATIENT
AS
BEGIN

    SET NOCOUNT ON;
   
    SELECT 
        L.LOG_ID,
        L.PT_ID,
        L.OPERATION,
        L.MODIFIED_DATE
    FROM
        TRANSACTION_LOG L
    WHERE
        L.OPERATION LIKE '%INSERT%'; 
END;
GO

-- STORED PROCEDURE FOR REPORTS (NEW PATIENTS)
ALTER PROCEDURE SP_NEW_PATIENT
AS
BEGIN

    SET NOCOUNT ON;
   
    SELECT 
        L.LOG_ID,
        L.PT_ID,
        L.OPERATION,
        L.MODIFIED_DATE
    FROM
        TRANSACTION_LOG L
    WHERE
        L.OPERATION LIKE '%INSERT%'; 
END;
GO


-- STORED PROCEDURE FOR REPORTS (RETURNING/OLD PATIENTS)

ALTER PROCEDURE SP_OLD_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('IMMUNIZATION', 'CHECK-UP') 
    
    UNION ALL

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION = 'UPDATE'; 
END;
GO


-- STORED PROCEDURE FOR REPORTS (ALL PATIENT)

ALTER PROCEDURE SP_ALL_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('CHECK-UP', 'IMMUNIZATION') 
    
    UNION ALL

    -- Select from TRANSACTION_LOG
    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION IN ('INSERT', 'UPDATE');
END;
GO

EXEC SP_NEW_PATIENT
EXEC SP_OLD_PATIENT
EXEC SP_ALL_PATIENT


-- STORED PROCEDURE FOR REPORTS (RETURNING/OLD PATIENTS)

ALTER PROCEDURE SP_OLD_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('IMMUNIZATION', 'CHECK-UP') 
    
    UNION ALL

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION = 'UPDATE'; 
END;
GO


-- STORED PROCEDURE FOR REPORTS (ALL PATIENT)

ALTER PROCEDURE SP_ALL_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('CHECK-UP', 'IMMUNIZATION')
    
    UNION ALL

    -- Select from TRANSACTION_LOG
    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION IN ('INSERT', 'UPDATE'); 
GO

EXEC SP_NEW_PATIENT
EXEC SP_OLD_PATIENT
EXEC SP_ALL_PATIENT

-- STORED PROCEDURE FOR REPORTS (RETURNING/OLD PATIENTS)

ALTER PROCEDURE SP_OLD_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('IMMUNIZATION', 'CHECK-UP') 
    
    UNION ALL

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION = 'UPDATE'; 
END;
GO


-- STORED PROCEDURE FOR REPORTS (ALL PATIENT)

ALTER PROCEDURE SP_ALL_PATIENT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG_OLD_PT
    WHERE 
        OPERATION IN ('CHECK-UP', 'IMMUNIZATION')
    
    UNION ALL

    -- Select from TRANSACTION_LOG
    SELECT 
        LOG_ID,
        PT_ID,
        OPERATION,
        MODIFIED_DATE
    FROM 
        TRANSACTION_LOG
    WHERE 
        OPERATION IN ('INSERT', 'UPDATE'); 
GO

EXEC SP_NEW_PATIENT
EXEC SP_OLD_PATIENT
EXEC SP_ALL_PATIENT

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'gaceta', 
    @PT_FNAME = 'ethan caleb', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '09-19-2019', 
    @MT_NAME = 'Yannah Gaceta', 
    @FT_NAME = 'Gerwen Gaceta', 
    @CON_NUM = '09123456789', 
    @EMAIL_ADD = 'gerwen@gmail.com';


EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'gaceta', 
    @PT_FNAME = 'gadiel caden', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '01-24-2024', 
    @MT_NAME = 'Yannah Gaceta', 
    @FT_NAME = 'Gerwen Gaceta', 
    @CON_NUM = '09123456789', 
    @EMAIL_ADD = 'gerwen@gmail.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'cabatingan', 
    @PT_FNAME = 'airoh malachi', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '04-14-2022', 
    @MT_NAME = 'ayen cabatingan', 
    @FT_NAME = 'ahmed cabatingan', 
    @CON_NUM = '0987654321', 
    @EMAIL_ADD = NULL;

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'prajes', 
    @PT_FNAME = 'xavier', 
    @PT_MNAME = 'gibson',
    @DT_OF_BIRTH = '10-24-2018', 
    @MT_NAME = 'dianne prajes', 
    @FT_NAME = 'clent prajes', 
    @CON_NUM = '924689753', 
    @EMAIL_ADD = 'clent@gmail.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'perez', 
    @PT_FNAME = 'hezekiah henzly', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '07-15-2017', 
    @MT_NAME = 'hannah perez', 
    @FT_NAME = 'leo perez', 
    @CON_NUM = '09657665356', 
    @EMAIL_ADD = 'leo@gmal.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'perez', 
    @PT_FNAME = 'selah hoseah', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '08-11-2021', 
    @MT_NAME = 'hannah perez', 
    @FT_NAME = 'leo perez', 
    @CON_NUM = '09657665356', 
    @EMAIL_ADD = 'leo@gmal.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'perez', 
    @PT_FNAME = 'yoana copeland', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '09-06-2023', 
    @MT_NAME = 'hannah perez', 
    @FT_NAME = 'leo perez', 
    @CON_NUM = '09657665356', 
    @EMAIL_ADD = 'leo@gmal.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'prajes', 
    @PT_FNAME = 'aica ', 
    @PT_MNAME = 'maeve',
    @DT_OF_BIRTH = '01-26-2014', 
    @MT_NAME = 'jamica prajes', 
    @FT_NAME = 'mark dave prajes', 
    @CON_NUM = '09642731783', 
    @EMAIL_ADD = 'davemark@gmal.com';

EXEC SP_PT_INFORMATION 
    @PT_LNAME = 'lumandas', 
    @PT_FNAME = 'zarianah', 
    @PT_MNAME = NULL,
    @DT_OF_BIRTH = '10-05-2022', 
    @MT_NAME = 'leyka lumandas', 
    @FT_NAME = 'mark lumandas', 
    @CON_NUM = '09657665356', 
    @EMAIL_ADD = null;



EXEC SP_PRESCRIPTIONS
    @CU_TYPE = 1,
    @DATE = '12-12-2024',
    @AGE = 3,
    @FINDINGS =  'LACERATION IN THE CHIN',
    @CONSULT = 'TAMBALL',
    @DR_INS = '3X A DAY',
    @RETURN_DT = '12-24-2024',
    @PT_ID = '1000',
    @DR_ID = 22646525


EXEC SP_PRESCRIPTIONS
    @CU_TYPE = 1,
    @DATE = '121212',
    @AGE = 3,
    @FINDINGS =  'ASTHMA',
    @CONSULT = 'TAMBALL',
    @DR_INS = '3X A DAY',
    @RETURN_DT = '12-24-2024',
    @PT_ID = '1000',
    @DR_ID = 22646525

SELECT*FROM PRESCRIPTIONS
SELECT*FROM TRANSACTION_LOG_OLD_PT


SELECT*FROM PATIENT_INFORMATION