      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - CALCULADORA.
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog003_calculadora -std=default prog003_calculadora.cob && ./bin/prog003_calculadora
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALCULADORA.
       DATA DIVISION.
       FILE SECTION.
       WORKING-STORAGE SECTION.
           77 WKS-NUM-1           PIC S9(05)V99    VALUES 0.
           77 WKS-NUM-2           PIC S9(05)V9(02) VALUES 0.
           77 WKS-RESULTADO       PIC S9(10)V99    VALUES ZEROS.
           77 WKS-RESTO           PIC 9(2)         VALUES ZEROS.
           77 WKS-OPCAO           PIC A(01).
           77 WKS-SAIR            PIC 9(1)         VALUES ZEROS.
           77 WKS-RESULT-FORMAT   PIC -ZZZZZZZZZ9.99.

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.

           PERFORM 00000-CALCULADORA UNTIL WKS-SAIR = 2.

           STOP RUN.
       
       00000-CALCULADORA.
           DISPLAY "============ CALCULADORA ============= ".
           DISPLAY "1-. USAR CALCULADORA, 2-. SAIR".
           ACCEPT WKS-SAIR.

           IF WKS-SAIR = 1
              PERFORM 00001-PEDIR-DADOS
              PERFORM 00002-EXECUTAR-OPERACOES
           END-IF.

       00001-PEDIR-DADOS.
           DISPLAY "OPERACAO: ".
           DISPLAY "(S)oma, s(U)btracao, (M)ultiplicacao e (D)ivisao".
           DISPLAY "(P)otencia".
           DISPLAY "==>".
           ACCEPT WKS-OPCAO.

           DISPLAY "VALOR 1:".
           ACCEPT WKS-NUM-1.

           DISPLAY "VALOR 2:".
           ACCEPT WKS-NUM-2.

       00002-EXECUTAR-OPERACOES.
           MOVE FUNCTION UPPER-CASE(WKS-OPCAO) TO WKS-OPCAO.
           IF WKS-OPCAO = "S" OR "s"
              ADD WKS-NUM-1 TO WKS-NUM-2 GIVING WKS-RESULTADO
           ELSE 
           IF WKS-OPCAO = "U"
              SUBTRACT WKS-NUM-1 FROM WKS-NUM-2 GIVING WKS-RESULTADO
           ELSE 
           IF WKS-OPCAO = "M"
              MULTIPLY WKS-NUM-1 BY WKS-NUM-2 GIVING WKS-RESULTADO
           ELSE 
           IF WKS-OPCAO = "D"
              DIVIDE WKS-NUM-1 BY WKS-NUM-2 GIVING WKS-RESULTADO
                                         REMAINDER WKS-RESTO
           ELSE
           IF WKS-OPCAO = "P"
              COMPUTE WKS-RESULTADO = WKS-NUM-1 ** WKS-NUM-2
           ELSE
              DISPLAY "OPCAO INVALIDA"
           END-IF
           END-IF
           END-IF
           END-IF
           END-IF.
           IF WKS-OPCAO = "S" OR "U" OR "M" OR "D" OR "P"
               MOVE WKS-RESULTADO TO WKS-RESULT-FORMAT
              DISPLAY "Resultado: " WKS-RESULT-FORMAT
           END-IF.
        
       END PROGRAM CALCULADORA.
