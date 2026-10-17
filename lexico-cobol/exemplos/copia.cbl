      *================================================================*
      * DIRETIVA COPY: O LEXICO INTERROMPE ESTE ARQUIVO, LE O          *
      * COPYBOOK copybooks/CLIENTE.cpy E INSERE OS TOKENS DELE AQUI.   *
      *================================================================*
       IDENTIFICATION DIVISION.
       PROGRAM-ID. COPIA.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           COPY CLIENTE.
       77  WS-CONTADOR         PIC 9(3)  VALUE ZERO.
       PROCEDURE DIVISION.
           MOVE 12345 TO CLI-CODIGO.
           DISPLAY "CLIENTE: " CLI-CODIGO.
           STOP RUN.
