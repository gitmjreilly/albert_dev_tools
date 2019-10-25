
#include "runtime.pas"
#include "strings.inc"
#include  "term_colors.inc"


(*
 * Code to provide direct serial i/o.
 * Should only be used for debugging.
 *)

#define UART_0_STATUS_ADDRESS ($F001)
#define UART_0_DATA_ADDRESS   ($F000)

var
   x : integer;
 
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
procedure print_ch(Ch : integer);
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
procedure print(StrPtr : t_word_ptr);
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
      print("[0;");
      (* Set the color... *)
      if (AnsiColorCode = ANSI_RED) then
          print("31")
      else if (AnsiColorCode = ANSI_GREEN) then
          print("32") 
      else if (AnsiColorCode = ANSI_YELLOW) then
          print("33") 
      else if (AnsiColorCode = ANSI_BLUE) then
          print("34") 
      else if (AnsiColorCode = ANSI_MAGENTA) then
          print("35") 
      else if (AnsiColorCode = ANSI_CYAN) then
          print("36") 
      else if (AnsiColorCode = ANSI_WHITE) then
          print("37"); 

      print("m")
end;
(*===================================================================*)




(*=================================================================
 * Print a bunch(n) of blanks
(*=================================================================*)
procedure printtab(n : integer);
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
   print(adr(tmp_array))
end;
(*=================================================================*)


(*=================================================================
 * Print a bunch(n) of newlines
(*=================================================================*)
procedure println(n : integer);
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
   print(adr(tmp_array))
end;
(*=================================================================*)


(*=================================================================
 * Print a decimal number
(*=================================================================*)
procedure print_num(n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_str(n , adr(tmp_array));

   print(adr(tmp_array))
end;
(*=================================================================*)


 
(*=================================================================*)
procedure gets(s : t_word_ptr );
var
    c : integer,
    orig_s : ^integer;
    
begin
    orig_s := s;
    while (1) do begin
        c := k_getc();
        if c = ASCII_LF then begin
            println(1);
            s^ := 0;
            return
        end;
        
        if c = ASCII_DEL then c := ASCII_BS;
    
        if c = ASCII_BS then begin
            if s = orig_s then continue;
            (* We got backspace, we have to handle it in buffer and on screen *)
            print_ch(ASCII_BS); print(" "); print_ch(ASCII_BS);
            s := s - 1;
            continue
        end;
        s^ := c;
        print_ch(c);
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
      gets(adr(s));
      if str_is_num(adr(s)) then begin
         str_to_num(adr(s) , n_ptr);
         return
      end;

      print("BAD! Enter a number>")
   end
end;
(*=================================================================*)


(*=================================================================
 * Print a hex num
(*=================================================================*)
procedure print_hex_num(n : integer);
var
   tmp_array : array[10] of integer;

begin
   num_to_hex_str(n , adr(tmp_array));

   print(adr(tmp_array))

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
      gets(adr(s));
      if str_is_hex_num(adr(s)) then begin
         str_to_hex_num(adr(s) , n_ptr);
         return
      end;

      print("BAD! Enter a number>")
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


var
   s : array[10] of integer,
   port_address : ^integer,
   debug_led_address : ^integer,
   value : integer,
   result : integer;

begin
   debug_led_address := $F027;

   print("Port Tester!");
   while (1 = 1) do begin
      print("Main Menu"); println(1);
      print("    A - PMOD B.1   SS Out   <= 1"); println(1);
      print("    a - PMOD B.1   SS Out   <= 0"); println(1);
      print("    B - PMOD B.2   MOSI Out <= 1"); println(1);
      print("    b - PMOD B.2   MOSI Out <= 0"); println(1);
      print("    C - PMOD B.4   SCLK Out <= 1"); println(1);
      print("    c - PMOD B.4   SCLK Out <= 0"); println(1);
      println(1);
      print("    D - PMOD C.1   SS Out   <= 1"); println(1);
      print("    d - PMOD C.1   SS Out   <= 0"); println(1);
      print("    E - PMOD C.2   MOSI Out <= 1"); println(1);
      print("    e - PMOD C.2   MOSI Out <= 0"); println(1);
      print("    F - PMOD C.4   SCLK Out <= 1"); println(1);
      print("    f - PMOD C.4   SCLK Out <= 0"); println(1);
      println(1);
      print("    g - PMOD B.3   Get MISO"); println(1);
      print("    h - PMOD C.3   Get MISO"); println(1);
      println(1);

      print(">"); gets(adr(s));
      println(1);

      BIOS_StrCmp(adr(s), "A", adr(result));
      if (result = 1) then begin
         port_address := $F025;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "a", adr(result));
      if (result = 1) then begin
         port_address := $F025;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "B", adr(result));
      if (result = 1) then begin
         port_address := $F024;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "b", adr(result));
      if (result = 1) then begin
         port_address := $F024;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "C", adr(result));
      if (result = 1) then begin
         port_address := $F023;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "c", adr(result));
      if (result = 1) then begin
         port_address := $F023;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "D", adr(result));
      if (result = 1) then begin
         port_address := $F022;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "d", adr(result));
      if (result = 1) then begin
         port_address := $F022;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "E", adr(result));
      if (result = 1) then begin
         port_address := $F021;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "e", adr(result));
      if (result = 1) then begin
         port_address := $F021;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "F", adr(result));
      if (result = 1) then begin
         port_address := $F020;
         value := 1
      end;

      BIOS_StrCmp(adr(s), "f", adr(result));
      if (result = 1) then begin
         port_address := $F020;
         value := 0
      end;

      BIOS_StrCmp(adr(s), "g", adr(result));
      if (result = 1) then begin
         port_address := $F040;
         value := port_address^;
         print("MISO PMOD B.3 : "); print_num(value); println(1);
         continue
      end;

      BIOS_StrCmp(adr(s), "h", adr(result));
      if (result = 1) then begin
         port_address := $F041;
         value := port_address^;
         print("MISO PMOD C.3 : "); print_num(value); println(1);
         continue
      end;

      port_address^ := value;
      debug_led_address^ := value;

      println(1)


   end

end.
