USE KEEPSAKE
GO

INSERT INTO ACCOUNTS(USERTYPE, [PASSWORD], EMP_ID, USER_LNAME, USER_FNAME)
VALUES(1, 'doctorsample', 22646525, 'ESPELITA', 'MARI FRANZ');


EXEC SP_DOCTOR @DR_ID = 22646525, @DR_NAME = 'MARI FRANZ ESPELITA', @DEPPT ='NEUROLOGY', @SPLTY ='NEUROLOGY', @CONTACT ='09223344556'


SELECT*FROM PATIENT_INFORMATION;