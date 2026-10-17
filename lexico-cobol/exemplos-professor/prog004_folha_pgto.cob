      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - TABLES 1 AND 2 DIMENSIONS
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog004_folha_pgto -std=default prog004_folha_pgto.cob && ./bin/prog004_folha_pgto
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. FOLHA-PGTO.
       DATA DIVISION.
       FILE SECTION.
       WORKING-STORAGE SECTION.
       
       01 TAB-TRABALHADOR.
          02 TRABALHADOR OCCURS 3 TIMES INDEXED BY TID. 
             03 NOME            PIC X(5).
             03 SALARIO         PIC 9(5)V99.
             03 DPTO            PIC X(2) VALUES SPACES OCCURS 2 TIMES.
       
       77 IDX PIC 9(1).

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
            MOVE "JOSEA1111111A1A4MARIA2222222A2  FABIO3333333A2A3" TO T
      -AB-TRABALHADOR.
            DISPLAY " ".
            DISPLAY "====TAB-TRABALHADOR====".
            DISPLAY "INITIAL VALUE".
            DISPLAY TAB-TRABALHADOR.

            MOVE 1 TO IDX.
            DISPLAY " ".
            DISPLAY "====00001-DISPLAY-TRABALHADOR====".
            PERFORM 00001-DISPLAY-TRABALHADOR UNTIL IDX > 3.

            DISPLAY " ".
            DISPLAY "====00002-DISPLAY-BY-SEARCH====".
            PERFORM 00002-DISPLAY-BY-SEARCH.

            DISPLAY " ".
            DISPLAY "====00003-REMOVE-TRABALHADOR====".
            PERFORM 00003-REMOVE-TRABALHADOR.

           STOP RUN.

       00001-DISPLAY-TRABALHADOR.
           DISPLAY " ".
           
           DISPLAY "IDX=" IDX.
           DISPLAY "TRABALHADOR(IDX)=" TRABALHADOR(IDX).
           DISPLAY "NOME(IDX)=" NOME(IDX).
           DISPLAY "SALARIO(IDX)=" SALARIO(IDX).
           DISPLAY "DPTO(IDX,1)=" DPTO(IDX,1).
           DISPLAY "DPTO(IDX,2)=" DPTO(IDX,2).
           ADD 1 TO IDX.

       00002-DISPLAY-BY-SEARCH.

           SET TID TO 1.
           SEARCH TRABALHADOR
              AT END DISPLAY "TRABALHADOR NOT FOUND"
              WHEN NOME(TID) = "MARIA"
                 DISPLAY "'WHEN NOME(TID) = MARIA'"
                 DISPLAY "TID=" TID
                 DISPLAY "TRABALHADOR(TID)=" TRABALHADOR(TID)
           END-SEARCH. 
           

       00003-REMOVE-TRABALHADOR.
           SET TID TO 2.
           MOVE LOW-VALUES TO TRABALHADOR(TID)
           DISPLAY TAB-TRABALHADOR.

       END PROGRAM FOLHA-PGTO.
