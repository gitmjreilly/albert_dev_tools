(*
 * This include file provides basic console i/o.
 * It does not require an OS.  It runs on bare h/w
 * The included files are only for string and color handling.
 *
 * Handle input like Unix terminal driver.
 * An incoming CR is translated into NL (ASCII_LF) 
 * with stty this is the "icrnl" option.
 *
 *)

#ifndef K_USERIO_INC
#define K_USERIO_INC

#include <strings.inc>
#include  <term_colors.inc>


(*
 * Code to provide direct serial i/o.
 * Should only be used for debugging.
 *)

#define UART_0_STATUS_ADDRESS ($F001)
#define UART_0_DATA_ADDRESS   ($F000)
 
(*=================================================================*)
(*
 * Is a char available from the console serial port?
 *) 
function console_char_is_available() : integer; 
VAR
   DataPtr: t_word_ptr, StatusPtr: t_word_ptr;
begin
   StatusPtr := UART_0_STATUS_ADDRESS;
   DataPtr   := UART_0_DATA_ADDRESS;

   if ((StatusPtr^ AND $0002) =  $0002) then
      retval(1)
   else
      retval(0)

end;
(*=================================================================*)

 
(*=================================================================*)
(*
 * Handle input like Unix terminal driver.
 * An incoming CR is translated into NL (ASCII_LF) 
 * with stty this is the "icrnl" option.
 *
 *)
procedure BIOS_GetChFromUART(UARTNum : integer, ChPtr : t_word_ptr);
VAR
   DataPtr: t_word_ptr, StatusPtr: t_word_ptr;
begin
   if UARTNum = 0  then begin
      StatusPtr := UART_0_STATUS_ADDRESS;
      DataPtr   := UART_0_DATA_ADDRESS
   end;

   while (StatusPtr^ AND $0002) <> $0002 do ChPtr := ChPtr;
   ChPtr^ := DataPtr^;

   if ChPtr^ = 13 then ChPtr^ := 10
end;
(*=================================================================*)


(*=================================================================*)
(*
 * Handle output like Unix terminal driver.
 * An outgoing NL(ASCII_LF) is translated into  CR NL (ASCII_LF) 
 * with stty this is the "onlcr" option.
 *
 *)
procedure k_pr_ch(Ch : integer);
VAR
   DataPtr: t_word_ptr, StatusPtr: t_word_ptr;


begin
    StatusPtr := UART_0_STATUS_ADDRESS;
    DataPtr   := UART_0_DATA_ADDRESS;

    (*
    * If the output is NL, output CR first.
    *)
    if ch = 10 then begin
        while (StatusPtr^ AND 1) <> 1  do 
        Ch := Ch; 

        DataPtr^ := 13
    end;

    while (StatusPtr^ AND 1) <> 1  do 
    Ch := Ch; 

    DataPtr^ := Ch
end;
#####################################################################


(*=================================================================*)
(*
 * Handle output like Unix terminal driver.
 * An outgoing NL(ASCII_LF) is translated into  CR NL (ASCII_LF) 
 * with stty this is the "onlcr" option.
 *
 *)
procedure BIOS_PrintChToUART(UARTNum : integer, Ch : integer);
VAR
   DataPtr: t_word_ptr, StatusPtr: t_word_ptr;


begin
   if UARTNum = 0 then begin
      StatusPtr := UART_0_STATUS_ADDRESS;
      DataPtr   := UART_0_DATA_ADDRESS
   end;

   (*
    * If the output is NL, output CR first.
    *)
   if ch = 10 then begin
      while (StatusPtr^ AND 1) <> 1  do 
         Ch := Ch; 

      DataPtr^ := 13
   end;

   while (StatusPtr^ AND 1) <> 1  do 
      Ch := Ch; 

   DataPtr^ := Ch
end;
#####################################################################


#####################################################################
procedure BIOS_GetLineFromUART(UARTNum : integer, StrPtr : t_word_ptr);
var
   Ch: integer;
begin
   while 1=1 do begin
      BIOS_GetChFromUART(UARTNum, StrPtr);
      if StrPtr^ = 10 then begin
         StrPtr^ := 0;
         return
      end;
      StrPtr := StrPtr + 1
   end
end;
#####################################################################



#####################################################################
(*
 * This should be cooked input.  For now all it does is echo.
 *)
procedure ConsoleGetStr(StrPtr : t_word_ptr);
begin
   while 1=1 do begin
      BIOS_GetChFromUART(0, StrPtr);
      BIOS_PrintChToUART(0, StrPtr^);
      if StrPtr^ = ASCII_LF then begin
         StrPtr^ := 0;
         return
      end;
      StrPtr := StrPtr + 1
   end
end;
#####################################################################



#####################################################################
procedure BIOS_PrintStrToUART(
   UARTNum : integer, 
   StrPtr : t_word_ptr, 
   DoCr : integer);

begin
   while StrPtr^ <> 0 do begin
      BIOS_PrintChToUART(UARTNum, StrPtr^);
      StrPtr := StrPtr + 1
   end;
   if DoCR = 1 then
      BIOS_PrintChToUART(UARTNum, ASCII_LF)
end;
#####################################################################


(*===================================================================*)
procedure ConsolePrintStr(StrPtr : t_word_ptr, DoCR : integer);
begin
   BIOS_PrintStrToUART(0, StrPtr, DoCr)
end;

(*===================================================================*)

 
(*=================================================================*)
(* Handle input like Unix terminal driver.
 * An incoming CR is translated into NL (ASCII_LF) 
 * with stty this is the "icrnl" option. *)
function k_getc() : integer;
VAR
    c : integer,
   DataPtr: t_word_ptr, StatusPtr: t_word_ptr;
begin
    StatusPtr := UART_0_STATUS_ADDRESS;
    DataPtr   := UART_0_DATA_ADDRESS;

    while (StatusPtr^ AND $0002) <> $0002 do c := c;
    c := DataPtr^;

    if c = 13 then c := 10;
    retval(c)
end;
(*=================================================================*)

(*=================================================================
 * Print a str (no newline; must be done separately)
(*=================================================================*)
procedure k_pr(StrPtr : t_word_ptr);
begin
   (* ConsolePrintStr(s, 0) *)
   while StrPtr^ <> 0 do begin
      BIOS_PrintChToUART(0, StrPtr^);
      StrPtr := StrPtr + 1
   end
end;
(*=================================================================*)



(*===================================================================*)
procedure TextColor(ANSIColorCode : integer);
begin
      BIOS_PrintChToUART(0, ASCII_ESCAPE);
      k_pr("[0;");
      (* Set the color... *)
      if (AnsiColorCode = ANSI_RED) then
          k_pr("31")
      else if (AnsiColorCode = ANSI_GREEN) then
          k_pr("32") 
      else if (AnsiColorCode = ANSI_YELLOW) then
          k_pr("33") 
      else if (AnsiColorCode = ANSI_BLUE) then
          k_pr("34") 
      else if (AnsiColorCode = ANSI_MAGENTA) then
          k_pr("35") 
      else if (AnsiColorCode = ANSI_CYAN) then
          k_pr("36") 
      else if (AnsiColorCode = ANSI_WHITE) then
          k_pr("37"); 

      k_pr("m")
end;
(*===================================================================*)




(*=================================================================
 * Print a bunch(n) of blanks
(*=================================================================*)
procedure k_prtab(n : integer);
var
   tmp_array : array[80] of integer,
   s : ^integer;

begin
   if n >79 then n := 79;

   s := adr(tmp_array);
   while (n > 0) do begin
      s^ := ASCII_SPACE;
      n := n - 1;
      s := s + 1
   end;
   s^ := 0;
   k_pr(adr(tmp_array))
end;
(*=================================================================*)


(*=================================================================
 * Print a bunch(n) of newlines
(*=================================================================*)
procedure k_prln(n : integer);
var
   tmp_array : array[10] of integer,
   s : ^integer;

begin
   s := adr(tmp_array);
   while (n > 0) do begin
      s^ := 13;
      s := s + 1;

      s^ := ASCII_LF;
      s := s + 1;

      n := n - 1
   end;
   s^ := 0;
   k_pr(adr(tmp_array))
end;
(*=================================================================*)


(*=================================================================
 * Print a decimal number
(*=================================================================*)
procedure k_prnum(n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_str(n , adr(tmp_array));

   k_pr(adr(tmp_array))
end;
(*=================================================================*)


 
(*=================================================================*)
procedure k_gets(s : t_word_ptr );
var
    c : integer,
    orig_s : ^integer;
    
begin
    orig_s := s;
    while (1) do begin
        c := k_getc();
        if c = ASCII_LF then begin
            k_prln(1);
            s^ := 0;
            return
        end;
        
        if c = ASCII_DEL then c := ASCII_BS;
    
        if c = ASCII_BS then begin
            if s = orig_s then continue;
            (* We got backspace, we have to handle it in buffer and on screen *)
            k_pr_ch(ASCII_BS); k_pr(" "); k_pr_ch(ASCII_BS);
            s := s - 1;
            continue
        end;
        s^ := c;
        k_pr_ch(c);
        s := s + 1
    end
end;
(*=================================================================*)


(*=================================================================
 *  Get a number until it looks correct
(*=================================================================*)
procedure k_get_num(n_ptr : ^integer) ;
var
   s : array[20] of integer;

begin
   while (1) do begin
      k_gets(adr(s));
      if str_is_num(adr(s)) then begin
         str_to_num(adr(s) , n_ptr);
         return
      end;

      k_pr("BAD! Enter a number>")
   end
end;
(*=================================================================*)


(*=================================================================
 * Print a hex num
(*=================================================================*)
procedure k_pr_hex_num(n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_hex_str(n , adr(tmp_array));

   k_pr(adr(tmp_array))

end;
(*=================================================================*)


(*=================================================================
 *  Get a hex number until it looks correct
(*=================================================================*)
procedure k_get_hex_num(n_ptr : ^integer) ;
var
   s : array[20] of integer;

begin
   while (1) do begin
      k_gets(adr(s));
      if str_is_hex_num(adr(s)) then begin
         str_to_hex_num(adr(s) , n_ptr);
         return
      end;

      k_pr("BAD! Enter a number>")
   end
end;
(*=================================================================*)


(*=================================================================
 * Color print
(*=================================================================*)
procedure k_cpr(color : integer, StrPtr : t_word_ptr);
begin
   (* ConsolePrintStr(s, 0) *)
   TextColor(color);
   while StrPtr^ <> 0 do begin
      BIOS_PrintChToUART(0, StrPtr^);
      StrPtr := StrPtr + 1
   end
end;
(*=================================================================*)


(*=================================================================
 * Print a hex num in COLOR!
(*=================================================================*)
procedure k_cpr_hex_num(color : integer, n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_hex_str(n , adr(tmp_array));

   k_cpr(color, adr(tmp_array))
end;
(*=================================================================*)


(*=================================================================
 * Print a decimal number in COLOR
(*=================================================================*)
procedure k_cprnum(color : integer, n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_str(n , adr(tmp_array));

   k_cpr(color, adr(tmp_array))
end;
(*=================================================================*)

#endif
