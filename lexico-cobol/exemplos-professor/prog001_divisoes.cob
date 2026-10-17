      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - DIVISOES DE UM PROGRAMA COBOL
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line:
      * cobc -x -o bin/prog001_divisoes -std=default prog001_divisoes.cob && ./bin/prog001_divisoes
      ******************************************************************

      *================================================================*
      ***** identifcata a documentacao do programa
      ***** nao contem SECTION
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PROG0001.

      ***** Itens abaixo sao opcionais
       AUTHOR. Enio Basso.
       INSTALLATION. ebasso(dot)net.
       DATE-WRITTEN. 2018-02-24.
       DATE-COMPILED. 2018-02-24.
       SECURITY. O programa usa criptografia XPTO.
       REMARKS. O programa recebe um valor e imprime na tela.

      ***** descreve o computador e perifericos
       ENVIRONMENT DIVISION.

       CONFIGURATION SECTION.

      ***** Informavam qual computador ia executar. DEPRECIADO.
      *SOURCE-COMPUTER. computador Usado Para Compilar.
      *OBJECT-COMPUTER. computador Usado Para Executar.

      *SPECIAL-NAMES. relacionaNomes Internos A Equipamentos.

       INPUT-OUTPUT SECTION.

      *      nomeia e associa arquivos e perifericos.
      *FILE-CONTROL.
      *         SELECT XPTO00005 ASSIGN to XMS70111

      *I-O-CONTROL. define tecnicas de controle do programa.


       DATA DIVISION.

      * FILE SECTION.  descricao dos arquivos e registros.
      * WORKING-STORAGE SECTION. aqui declara as variaveis.
      * LINKAGE SECTION. comunicaocao com outros programas.
      * SCREEN SECTION. definicao de telas

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
            DISPLAY "Hello world"
            display "Enio Basso - 2"
            STOP RUN.
       END PROGRAM PROG0001.
