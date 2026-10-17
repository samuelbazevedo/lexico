      ******************************************************************
      * Author: ENIO BASSO
      * Date: 2018-02-26
      * Purpose: COBOL STUDY - Strings
      * 
      * Para programar sugiro: o OpenCobolIDE para o Visual Studio Code
      *
      * Compilo com o gnu-cobol usando a seguinte command line: 
      * cobc -x -o bin/prog005_strings -std=default prog005_strings.cob && ./bin/prog005_strings
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PROG008_STRING.
       DATA DIVISION.
       FILE SECTION.
       WORKING-STORAGE SECTION.
       
       77 SAUX            PIC X(15).
       77 CONT            PIC 9(2).
       77 YESNO           PIC 9.
       
       77 IDX PIC 9(1).

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
            MOVE "HELLO WORLD 123!!" TO SAUX.

            DISPLAY " ".
            DISPLAY "==== EXEMPLO 1 ====".
            DISPLAY "SAUX='" SAUX "'".
            
            MOVE 0 TO CONT.
            INSPECT SAUX TALLYING CONT FOR CHARACTERS.
            DISPLAY "CONT=" CONT " - FOR CHARACTERS".

            MOVE 0 TO CONT.
            INSPECT SAUX TALLYING CONT FOR ALL "L".
            DISPLAY "CONT=" CONT " - FOR ALL 'L'".

            MOVE 0 TO CONT.
            INSPECT SAUX TALLYING CONT 
                    FOR CHARACTERS BEFORE INITIAL " ".
            DISPLAY "CONT=" CONT " - BEFORE INITIAL ' '".

            MOVE 0 TO CONT.
            INSPECT SAUX TALLYING CONT 
                    FOR CHARACTERS AFTER INITIAL " ".
            DISPLAY "CONT=" CONT " - AFTER INITIAL ' '".

            MOVE 0 TO YESNO.
            INSPECT SAUX TALLYING YESNO 
                    FOR LEADING "H".
            DISPLAY "YESNO=" YESNO " - FOR LEADING 'H' 0=N / 1=Y".

            INSPECT SAUX REPLACING FIRST "E" BY "A".
            DISPLAY "SAUX='" SAUX "' - REPLACING FIRST 'E' BY 'A'".

            INSPECT SAUX REPLACING ALL "LLO" BY "PPY".
            DISPLAY "SAUX='" SAUX "' - REPLACING ALL 'LLO' BY 'PPY'".

            MOVE " HOLA-DAY" TO SAUX.
            INSPECT SAUX REPLACING ALL "HOLA" BY "GOOD"
                    AFTER INITIAL " " BEFORE INITIAL "-".
            DISPLAY "SAUX='" SAUX "' - HOLA-DAY TO GOOD-DAY'".

            MOVE "HELLO WORLD" TO SAUX.
            INSPECT SAUX CONVERTING "ABCDEFGHIJKLMNOPQRSTUVWXZ" 
                TO "abcdefghijklmnopqrstuvwxz".
            DISPLAY "SAUX='" SAUX "' - CONVERTING'".

            INSPECT SAUX REPLACING CHARACTERS BY "F".
            DISPLAY "SAUX='" SAUX "' - REPLACING ".

           STOP RUN.

       END PROGRAM PROG008_STRING.
