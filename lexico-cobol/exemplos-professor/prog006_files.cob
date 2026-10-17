      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - Manipulacao de arquivos
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog006_files -std=default prog006_files.cob && ./bin/prog006_files
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PROG006_FILES.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.

       FILE-CONTROL.
           SELECT MY-FILE ASSIGN TO "DADOS.TXT".

       DATA DIVISION.
       FILE SECTION.
       
      * FILE DESCRIPTOR 
       FD MY-FILE.
       01 RC-TRABALHADOR.
          02 RC-TID             PIC 9(5).
          02 RC-NOME            PIC X(10).
          02 RC-SALARIO         PIC 9(10)V99.
          02 RC-DPTO-1          PIC X(2).
          02 RC-DPTO-2          PIC X(2).

       WORKING-STORAGE SECTION.
       
       01 TAB-TRABALHADOR.
          02 TRABALHADOR OCCURS 3 TIMES INDEXED BY TID. 
             03 NOME            PIC X(5).
             03 SALARIO         PIC 9(5)V99.
             03 DPTO            PIC X(2) VALUES SPACES OCCURS 2 TIMES.

       77 SAUX            PIC X(15).
       77 CONT            PIC 9(2).
       77 YESNO           PIC 9.
       
       77 IDX PIC 9(1).

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.

            MOVE "JOSEA1111111A1A4MARIA2222222A2  FABIO3333333A2A3" TO T
      -AB-TRABALHADOR.
            
            DISPLAY " ".
            DISPLAY "====00001-DISPLAY-TRABALHADOR====".
            OPEN OUTPUT MY-FILE.

            MOVE 1 TO IDX.
            PERFORM 00001-WRITE-TO-FILE UNTIL IDX > 3.

            CLOSE MY-FILE.
            
           STOP RUN.

       00001-WRITE-TO-FILE.
           DISPLAY " ".
           
           MOVE LOW-VALUES TO RC-TRABALHADOR.
           DISPLAY "IDX=" IDX.
           DISPLAY "TRABALHADOR(IDX)=" TRABALHADOR(IDX).
           MOVE IDX TO RC-TID.
           MOVE NOME(IDX) TO RC-NOME.
           MOVE SALARIO(IDX) TO RC-SALARIO.
           MOVE DPTO(IDX,1) TO RC-DPTO-1.
           MOVE DPTO(IDX,2) TO RC-DPTO-2.
           WRITE RC-TRABALHADOR.
           ADD 1 TO IDX.

       END PROGRAM PROG006_FILES.
