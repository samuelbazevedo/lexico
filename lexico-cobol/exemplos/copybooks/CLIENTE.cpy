      *----------------------------------------------------------------*
      * COPYBOOK CLIENTE - LAYOUT DO REGISTRO DE CLIENTE (40 BYTES)    *
      *----------------------------------------------------------------*
       01  REG-CLIENTE.
           05 CLI-CODIGO       PIC 9(5).
           05 CLI-NOME         PIC X(20).
           05 CLI-UF           PIC XX.
           05 CLI-SALDO        PIC 9(6)V99.
           05 CLI-STATUS       PIC X.
              88 CLI-ATIVO               VALUE "A".
              88 CLI-INATIVO             VALUE "I".
           05 FILLER           PIC X(4).
