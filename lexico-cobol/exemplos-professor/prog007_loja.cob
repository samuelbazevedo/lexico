      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - Progama Loja ou Cadastro de Produtos
      *          Le os produtos e faz o cadastro e consulta de produtos
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog007_loja.cob -std=default prog007_loja.cob.cob && ./bin/prog007_loja.cob
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PROG007_LOJA.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.

       FILE-CONTROL.
           SELECT FD-PRODUTOS ASSIGN TO WS-PROD-FILENAME 
                              ORGANIZATION INDEXED
                              ACCESS MODE DYNAMIC
                              RECORD KEY IS RP-PID
                              ALTERNATE RECORD KEY IS RP-NOME
                              FILE STATUS WS-FILE-STATUS-PROD.

      * ARMAZENA A ULTIMA CHAVE DO ARQUIVO DE DADOS.
           SELECT FD-PRODUTOS-KEY ASSIGN TO "PROG10-001.KEY" 
                              FILE STATUS WS-FILE-STATUS-PROD-KEY.

       DATA DIVISION.
       FILE SECTION.
       
      * FILE DESCRIPTOR 
       FD FD-PRODUTOS
          BLOCK CONTAINS 874 RECORDS
          RECORD CONTAINS 64 CHARACTERS.
      *   TAMANHO MAXIMO 27998 POSICOES(CARACTERES)
      *   1 CARACTERES = 8 BITS - 1 BYTE.
      *   TAMANHO DE REGISTRO 64 POSICOES
      *   TAMANHO DE BLOCO IDEAL -> TAMANHO MAXIMO/TAMANHO DO REGISTRO
      *                             27998/64 => 437.4675
      *                             437 X 64 = 27968
      *   BLOQUEIO OTIMO -> 27966 POSICIOES
      *   TRACK COMPLETO -> 2 * 27996 => 55,9992 POSICOES
      *   FATOR DE BLOQUEIO = 437 * 2 = 874 REGISTROS.
      
       01 REG-PRODUTO.
           02 RP-PID             PIC 9(10).
           02 RP-NOME            PIC X(10).
           02 RP-VALOR           PIC 9(10)V9(02).
           02 RP-QTD             PIC 9(10)V9(02).
           02 RP-DESCRICAO       PIC X(20).


       FD FD-PRODUTOS-KEY.
       01 REGISTRO-CHAVE        PIC 9(10).



       WORKING-STORAGE SECTION.       
      ************ VARIAVES PARA OS ARQUIVOS ************
      * EXEMPLO PARA NOMES DE ARQUIVO COMO VARIAVEL
       01 WS-PROD-FILENAME.
           02 NAME               PIC X(7) VALUES "PROG10-".
           02 NUM                PIC 9(3) VALUES 1.
           02 EXT                PIC X(4) VALUES ".DAT".

       77 WS-FILE-STATUS-PROD       PIC 9(02).
       77 WS-FILE-STATUS-PROD-KEY   PIC 9(02).

       01 WS-PRODUTO.
           02 WS-PID             PIC 9(10).
           02 WS-NOME            PIC X(10).
           02 WS-VALOR           PIC 9(10)V9(02).
           02 WS-QTD             PIC 9(10)V9(02).
           02 WS-DESCRICAO       PIC X(20).

      ************* VARIAVEIS PARA USO GERAL ************
       77 WS-OPCAO                        PIC 9(01).
       77 WS-ULTIMO-PID                   PIC 9(10).
       77 WS-EXIT                         PIC 9(01) VALUES ZERO.

      ************* VARIAVEIS PARA CONTADORES ************

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
        
           DISPLAY "PERFORM 00000-OPEN-FILE-PRODUTOS-KEY".
           PERFORM 00000-OPEN-FILE-PRODUTOS-KEY.

           IF WS-EXIT = 0
              DISPLAY "PERFORM 00000-OPEN-FILE-PRODUTOS"
              PERFORM 00000-OPEN-FILE-PRODUTOS 
           END-IF.
           
           PERFORM 00001-MENU-OPCOES UNTIL WS-EXIT = 1.

           WRITE REGISTRO-CHAVE FROM WS-ULTIMO-PID.
           CLOSE FD-PRODUTOS-KEY.
           CLOSE FD-PRODUTOS.
           DISPLAY "BYE"
           STOP RUN.

       00000-OPEN-FILE-PRODUTOS-KEY.
           
           MOVE 0 TO WS-FILE-STATUS-PROD-KEY.
           OPEN INPUT FD-PRODUTOS-KEY.
           IF WS-FILE-STATUS-PROD-KEY = 0
              DISPLAY "-- PROG10-001.KEY FOUND"     
              READ FD-PRODUTOS-KEY INTO WS-ULTIMO-PID   
           ELSE 
           IF WS-FILE-STATUS-PROD-KEY = 35 
              DISPLAY "-- PROG10-001.KEY NOT FOUND - CREATING NEW"
              OPEN OUTPUT FD-PRODUTOS-KEY
              IF WS-FILE-STATUS-PROD-KEY = 0
                 MOVE 0 TO WS-ULTIMO-PID
              ELSE
                 DISPLAY "-- ERRO AO CRIAR ARQUIVO DE CHAVES -->"
                         WS-FILE-STATUS-PROD-KEY
                 MOVE 1 TO WS-EXIT
           ELSE
              DISPLAY "-- ERRO AO ABRIR ARQUIVO DE CHAVES -->"
                    WS-FILE-STATUS-PROD-KEY
              MOVE 1 TO WS-EXIT.

       00000-OPEN-FILE-PRODUTOS.
           MOVE 0 TO WS-FILE-STATUS-PROD.
           OPEN I-O FD-PRODUTOS.

           IF WS-FILE-STATUS-PROD = 35 
              DISPLAY "-- PROG10-001.DAT NOT FOUND - CREATING NEW"
              OPEN OUTPUT FD-PRODUTOS
              IF WS-FILE-STATUS-PROD = 0
                 MOVE 0 TO WS-ULTIMO-PID
              ELSE
                 DISPLAY "-- ERRO AO CRIAR ARQUIVO DE DADOS -->"
                         WS-FILE-STATUS-PROD
                 MOVE 1 TO WS-EXIT
           ELSE
           IF WS-FILE-STATUS-PROD = 0 
              DISPLAY "-- PROG10-001.DAT FOUND"
              IF WS-ULTIMO-PID = 0
                 MOVE 0 TO WS-ULTIMO-PID
              ELSE
                 MOVE WS-ULTIMO-PID TO RP-PID
      *          POSICIONA NO REGISTRO DO ARQUIVO
                 START FD-PRODUTOS KEY EQUAL RP-PID 
                     INVALID KEY 
                        DISPLAY "ERRO AO REGISTRO"
           ELSE  
             DISPLAY "-- ERRO AO ABRIR ARQUIVO DE PRODUTOS"
                         WS-FILE-STATUS-PROD
             MOVE 1 TO WS-EXIT.


       00001-MENU-OPCOES.
           DISPLAY " ".
           DISPLAY "====00001-MENU-OPCOES====".
           DISPLAY "OPCOES:".    
           DISPLAY "1) ADICIONA PRODUTO". 
           DISPLAY "2) REMOVE PRODUTO - NOT IMPLEMENTED". 
           DISPLAY "3) ATUALIZA PRODUTO - NOT IMPLEMENTED". 
           DISPLAY "4) CONSULTA PRODUTO". 
           DISPLAY " ".
           DISPLAY "5) SAIR DO PROGRAMA".
           ACCEPT  WS-OPCAO.

           EVALUATE WS-OPCAO
              WHEN 1 PERFORM 00002-CREATE-PRODUTO
              WHEN 2
                 DISPLAY "DELETE"
              WHEN 3
                 DISPLAY "UPDATE"
              WHEN 4 PERFORM 00002-SELECT-PRODUTO
              WHEN 5 
                 MOVE 1 TO WS-EXIT
              WHEN OTHER
                 DISPLAY "OPCAO INVALIDA."
           END-EVALUATE.

       00002-CREATE-PRODUTO.
           DISPLAY "CRIA UM NOVO PRODUTO".
           DISPLAY "NOME: " WITH NO ADVANCING.
           ACCEPT WS-NOME.
           DISPLAY "VALOR: " WITH NO ADVANCING.
           ACCEPT WS-VALOR.
           DISPLAY "QUANTIDADE: " WITH NO ADVANCING.
           ACCEPT WS-QTD.
           DISPLAY "DESCRICAO: " WITH NO ADVANCING.
           ACCEPT WS-DESCRICAO.

           ADD 1 TO WS-ULTIMO-PID.
           MOVE WS-ULTIMO-PID TO WS-PID.

           DISPLAY "--------------"
           DISPLAY WS-PRODUTO.
           DISPLAY "--------------"

           WRITE REG-PRODUTO FROM WS-PRODUTO
              INVALID KEY
                 DISPLAY "CODIGO DE PRODUTO JAH EXISTE" WS-ULTIMO-PID
                 MOVE 1 TO WS-EXIT
              NOT INVALID KEY
                 DISPLAY "PRODUTO ARMAZENADO".

       00002-SELECT-PRODUTO.
           DISPLAY "CONSULTA PRODUTO".
           DISPLAY "WS-ULTIMO-PID --> " WS-ULTIMO-PID.
           DISPLAY "PID: ".
           ACCEPT WS-PID.

           MOVE WS-PID TO RP-PID.
      *          POSICIONA NO REGISTRO DO ARQUIVO
           READ FD-PRODUTOS RECORD KEY RP-PID 
                INVALID KEY 
                    DISPLAY "ERRO AO LOCALIZAR REGISTRO"
                NOT INVALID KEY
                    MOVE REG-PRODUTO TO WS-PRODUTO
                    DISPLAY " "
                    DISPLAY "NOME: " WITH NO ADVANCING
                    DISPLAY WS-NOME
                    DISPLAY "VALOR: " WITH NO ADVANCING
                    DISPLAY WS-VALOR
                    DISPLAY "QUANTIDADE: " WITH NO ADVANCING
                    DISPLAY WS-QTD
                    DISPLAY "DESCRICAO: " WITH NO ADVANCING
                    DISPLAY WS-DESCRICAO.

       END PROGRAM PROG007_LOJA.
