      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - Operacoes em programas Cobol
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog002_operacoes.cob -std=default prog002_operacoes.cob.cob && ./bin/prog002_operacoes.cob
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. YOUR-PROGRAM-NAME.
       DATA DIVISION.
       FILE SECTION.
       WORKING-STORAGE SECTION.
           77 WRK-VALOR1       PIC 9(10) VALUES 10.
           77 WRK-VALOR2       PIC 9(10) VALUES ZEROS.
           77 WRK-A            PIC 9(2) VALUES 1.
           77 WRK-B            PIC 9(2) VALUES 1.
           77 WRK-C            PIC 9(2) VALUES ZEROS.

           01 WRK-TOTAIS.
              05 WRK-TOTAL     PIC 9(10) VALUE 19.

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "===== start =======".
           MOVE 20 TO WRK-VALOR2.
           DISPLAY "MOVE 20 TO WRK-VALOR2 -->" WRK-VALOR2.

           MOVE WRK-VALOR1 TO WRK-VALOR2.
           DISPLAY "MOVE WRK-VALOR1 TO WRK-VALOR2 -->" WRK-VALOR2.

           MOVE 70 TO WRK-VALOR1 WRK-VALOR2.
           DISPLAY "MOVE 70 TO WRK-VALOR1 WRK-VALOR2 -->" WRK-VALOR2.

           MOVE WRK-TOTAL OF WRK-TOTAIS TO WRK-VALOR2.
           DISPLAY "MOVE WRK-TOTAL OF WRK-TOTAIS TO WRK-VALOR2. -->"
      -              WRK-VALOR2.

           DISPLAY "--------".
           DISPLAY "A = 1, B = 1, C = 1".

           DISPLAY " ".
           ADD 1 1 TO WRK-A.
           DISPLAY "ADD B C TO A (A = B + C + A) -->" WRK-A.

           MOVE 1 TO WRK-A.
           ADD 1 TO WRK-A WRK-B.
           DISPLAY " ".
           DISPLAY "ADD 1 TO A B (A = A + 1; B = B + 1) -->" 
           DISPLAY "A= " WRK-A " , B= " WRK-B.

           DISPLAY " ".
           ADD 1 1 GIVING WRK-A.
           DISPLAY "ADD B C GIVING A (A = B + C) -->" WRK-A.

           DISPLAY "============ SUBTRACT ============= ".
           MOVE 99 TO WRK-A.
           MOVE 0 TO WRK-B.
           DISPLAY "A= 99, B= 0".
           SUBTRACT 30 23 FROM WRK-A 
                          GIVING WRK-B.
           DISPLAY "SUBTRACT 30 23 FROM A GIVING B.-->"
           DISPLAY "A= " WRK-A " , B= " WRK-B.

           DISPLAY "============ MULTIPLY ============= ".
           MOVE 40 TO WRK-A.
           MOVE 0 TO WRK-B.
           DISPLAY "A= 40, B= 0".
           MULTIPLY 2 BY WRK-A.
           DISPLAY "MULTIPLY A BY 2 -->"
           DISPLAY "A= " WRK-A " , B= " WRK-B.

           DISPLAY "============ MULTIPLY ============= ".
           MOVE 40 TO WRK-A.
           MOVE 0 TO WRK-B.
           DISPLAY "A= 40, B= 0".
           MULTIPLY 2 BY WRK-A GIVING WRK-B.
           DISPLAY "MULTIPLY A BY 2 GIVING B.-->"
           DISPLAY "A= " WRK-A " , B= " WRK-B.

           DISPLAY "============ DIVIDE =============".
           MOVE 81 TO WRK-A.
           MOVE 0 TO WRK-B.
           MOVE 0 TO WRK-C.
           DISPLAY "A= 80, B= 0".
           DIVIDE WRK-A BY 2 GIVING WRK-B REMAINDER WRK-C.
           DISPLAY "DIVIDE A BY 2 GIVING B REMAINDER C .-->"
           DISPLAY "A= " WRK-A " , B= " WRK-B " , C= " WRK-C.

      ****** Tive que tirar o ponto.
           DISPLAY " ".
           MOVE 99 TO WRK-A.
           ADD 1 TO WRK-A
           ON SIZE ERROR
              DISPLAY "ON SIZE ERROR -->" WRK-A.

            STOP RUN.
       END PROGRAM YOUR-PROGRAM-NAME.
