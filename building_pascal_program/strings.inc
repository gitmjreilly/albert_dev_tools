#ifndef STRINGS_INC_INCLUDED
#define STRINGS_INC_INCLUDED

#include <math_32.inc>

const
   ASCII_ESCAPE = $001B,
   ASCII_A = 65, 
   ASCII_Z = 90, 
   ASCII_ZERO = 48, 
   ASCII_NINE = 57, 
   ASCII_MINUS = 45, 
   ASCII_SPACE = 32, 
   ASCII_LF = 10;
   
#define ASCII_SLASH 47
#define ASCII_BS 8
#define ASCII_DEL 127
   
type
   t_word_ptr = ^integer;
   
(* TODO *)
(* Never been clear where to put ArgV *)
var
   ArgVPtr : t_word_ptr,
   ArgV : array [32] of integer;

   
   
var

   (* ArgVPtr : t_word_ptr, *)
   NewBuffer :  array[128] of integer;


#####################################################################
procedure BIOS_StrLen(s : t_word_ptr , LenPtr : t_word_ptr);
begin
   LenPtr^ := 0;
   while s^ <> 0 do begin
      LenPtr^ := LenPtr^ + 1;
      s := s + 1
   end
end;
#####################################################################


#####################################################################
procedure BIOS_ChAppend(s : t_word_ptr, Ch : integer);
var
   Len: integer;

begin
   BIOS_StrLen(S, ADR(Len));
   s := s + Len;
   s^ := Ch;
   s := s + 1;
   s^ := 0
end;
#####################################################################


#####################################################################
procedure BIOS_StrAppend(OrigStrPtr : t_word_ptr, AddStrPtr : t_word_ptr);
var
   Len: integer;

begin
   BIOS_StrLen(OrigStrPtr, ADR(Len));
   OrigStrPtr := OrigStrPtr + Len;
   while AddStrPtr^ <> 0 do begin
      OrigStrPtr^ := AddStrPtr^;
      AddStrPtr := AddStrPtr + 1;
      OrigStrPtr := OrigStrPtr + 1
   end;
   OrigStrPtr^ := 0
end;
#####################################################################



#####################################################################
procedure BIOS_StrCmp(S1 : t_word_ptr, S2 : t_word_ptr, 
   AnsPtr : t_word_ptr);
var
   Len: integer;

begin
   while S1^ = S2^ do begin
      if S1^ = 0 then begin
         AnsPtr^ := 1;
         return
      end;
      S1 := S1 + 1;
      S2 := S2 + 1
   end;
   AnsPtr^ := 0
end;
#####################################################################


#####################################################################
procedure BIOS_NumToHexStr(Num : integer, StrPtr : t_word_ptr);
var
   i : integer,
   Tmp : integer;

begin
   (*
    * Trying to figure out how much time this is all taking...
    *)
   StrPtr^ := 0 ;

   Tmp := Num AND $F000;
   (* Pick off most significant hex digit *)
   i := 1; 
   while i <= 12 do begin
      Tmp := SRL(Tmp);
      i := i + 1
   end;
   if Tmp < 10 then
      Tmp := Tmp + 48
   else
      Tmp := Tmp + 55;
   StrPtr^ := Tmp;

   StrPtr := StrPtr + 1;
   Tmp := Num AND $0F00;
   (* Pick off 2nd most significant hex digit *)
   i := 1; 
   while i <= 8 do begin
      Tmp := SRL(Tmp);
      i := i + 1
   end;
   if Tmp < 10 then
      Tmp := Tmp + 48
   else
      Tmp := Tmp + 55;
   StrPtr^ := Tmp;
   
   StrPtr := StrPtr + 1;
   Tmp := Num AND $00F0;
   (* Pick off 3rd most significant hex digit *)
   i := 1; 
   while i <= 4 do begin
      Tmp := SRL(Tmp);
      i := i + 1
   end;
   if Tmp < 10 then
      Tmp := Tmp + 48
   else
      Tmp := Tmp + 55;
   StrPtr^ := Tmp;

   StrPtr := StrPtr + 1;
   Tmp := Num AND $000F;
   if Tmp < 10 then
      Tmp := Tmp + 48
   else
      Tmp := Tmp + 55;
   StrPtr^ := Tmp;

   StrPtr := StrPtr + 1;
   StrPtr^ := 0

end;
#####################################################################


#####################################################################
procedure BIOS_HexStrToNum(StrPtr : t_word_ptr, NumPtr : t_word_ptr);
var
   Increment: integer;

begin
   NumPtr^ := 0;
   while StrPtr^ <> 0 do begin
      if StrPtr^ < 58 
         then Increment := StrPtr^ - 48
         else Increment := StrPtr^ - 55;
      NumPtr^ := NumPtr^ * 16 + Increment;
      StrPtr := StrPtr + 1
   end
end;
#####################################################################



#####################################################################
procedure BIOS_DecStrToNum(StrPtr : t_word_ptr, AnsPtr : t_word_ptr);
begin
   AnsPtr^ := 0;
   while StrPtr^ <> 0 do begin
      AnsPtr^ := AnsPtr^ * 10 + (StrPtr^ - 48);
      StrPtr := StrPtr + 1
   end
end;
#####################################################################


#####################################################################
procedure ParseLine(InputPtr : t_word_ptr);
var
   NumArgs: integer,
   ArgVPtr: t_word_ptr,
   NewBufPtr: t_word_ptr;

begin
   NewBufPtr := adr(NewBuffer);
   ArgVPtr := adr(ArgV);
   NumArgs := 0;

   (*
    * Special case code to handle string which is
    * spaces only
    *)
   NewBufPtr^ := 0;
   ArgVPtr^ := NewBufPtr;
 
   while  1 = 1 do begin
      while InputPtr^ = ASCII_SPACE do begin
         InputPtr := InputPtr + 1
      end;

      if InputPtr^ = 0 then begin
         if NumArgs = 0 then begin
            ArgVPtr^ := NewBufPtr
         end
         else begin
            ArgVPtr^ := 0;
            NewBufPtr^ := 0
         end;
         break
      end;

      (*
       * If we got this far, we are at the beginning of an arg
       *)
      NumArgs := NumArgs + 1;
      NewBufPtr^ := InputPtr^;
      ArgVPtr^ := NewBufPtr;
      NewBufPtr := NewBufPtr + 1;
      InputPtr := InputPtr + 1;
      ArgVPtr := ArgVPtr + 1;

      while 1 = 1 do begin
         if InputPtr^ = 32 then break;
         if InputPtr^ = 0 then break;

         NewBufPtr^ := InputPtr^;
         NewBufPtr := NewBufPtr + 1;
         InputPtr := InputPtr + 1
      end;

      NewBufPtr^ := 0;
      NewBufPtr := NewBufPtr + 1
   end


end;
(*=================================================================*)

(*=================================================================*)
procedure str_len(s : t_word_ptr , LenPtr : t_word_ptr);
begin
   LenPtr^ := 0;
   while s^ <> 0 do begin
      LenPtr^ := LenPtr^ + 1;
      s := s + 1
   end
end;
(*=================================================================*)


(*=================================================================*)
procedure str_to_num(StrPtr : t_word_ptr, AnsPtr : t_word_ptr);
var
   num_is_negative : integer,
   num : integer;

begin
   num := 0;
   if StrPtr^ = ASCII_MINUS then begin
      num_is_negative := 1;
      StrPtr := StrPtr + 1
   end
   else begin
      num_is_negative := 0
   end;


   while StrPtr^ <> 0 do begin
      num := num * 10 + (StrPtr^ - 48);
      StrPtr := StrPtr + 1
   end;
   if num_is_negative then
       num := 0 - num;

   AnsPtr^ := num
end;
(*=================================================================*)

(*=================================================================*)
procedure str_to_s32(StrPtr : t_word_ptr, AnsPtr : ^t_s32);
var
   tmp : t_s32,
   ten : t_s32,
   zero : t_s32,
   num_is_negative : integer,
   num : t_s32;

begin
   num[0] := 0;
   num[1] := 0;
   
   ten[0] := 0;
   ten[1] := 10;

   zero[0] := 0;
   zero[1] := 0;
   
   
   if StrPtr^ = ASCII_MINUS then begin
      num_is_negative := 1;
      StrPtr := StrPtr + 1
   end
   else begin
      num_is_negative := 0
   end;

   while StrPtr^ <> 0 do begin
      s32_mul(adr(num), adr(ten), adr(num));
      tmp[0] := 0;
      tmp[1] := StrPtr^ - ASCII_ZERO;
      s32_add(adr(num), adr(tmp), adr(num));
      StrPtr := StrPtr + 1
   end;
   if num_is_negative then
      s32_sub(adr(zero), adr(num), adr(num));

   AnsPtr^[0] := num[0];
   AnsPtr^[1] := num[1]
   
end;
(*=================================================================*)


(*=================================================================*)
procedure str_to_hex_num(StrPtr : t_word_ptr, NumPtr : t_word_ptr);
var
   Increment: integer;

begin
   NumPtr^ := 0;
   while StrPtr^ <> 0 do begin
      if StrPtr^ < 58 
         then Increment := StrPtr^ - 48
         else Increment := StrPtr^ - 55;
      NumPtr^ := NumPtr^ * 16 + Increment;
      StrPtr := StrPtr + 1
   end
end;
(*=================================================================*)


(*******************************************************************
 * Copy a string
 *******************************************************************)
procedure str_copy(src_ptr : t_word_ptr, dst_ptr : t_word_ptr);

begin
   while src_ptr^ <> 0 do begin
      dst_ptr^ := src_ptr^;
      src_ptr := src_ptr + 1;
      dst_ptr := dst_ptr + 1
   end;
   dst_ptr^ := 0
end;
(*******************************************************************)


(*=================================================================*)
procedure reverse_str(s : ^integer);
var
    front_p : ^integer,
    rear_p : ^integer,
    tmp : integer,
    i : integer,
    l : integer;

begin

   str_len(s , adr(l));
   if (l = 0) then return;

   front_p := s;
   rear_p := s + l - 1;
   while (l > 0) do begin
      l := l - 2;
      tmp := rear_p^;
      rear_p^ := front_p^;
      front_p^ := tmp;
      rear_p := rear_p - 1;
      front_p := front_p + 1
   end

end;
(*=================================================================*)


(*=================================================================
 * Convert a num to str
(*=================================================================*)
procedure num_to_str(n : integer, s : ^integer);
var
   least_significant_digit : integer,
   tmp : ^integer,
   is_negative : integer;

begin

   if (n < 0) then begin
      tmp := s;
      tmp^ := ASCII_MINUS;
      tmp := tmp + 1;
      n := 0 - n;
      is_negative := 1
   end
   else begin
      tmp := s;
      is_negative := 0
   end;

   if (n = 0) then begin
      s^ := ASCII_ZERO;
      s := s + 1;
      s^ := 0;
      return
   end;

   while (n <> 0) do begin
      least_significant_digit := n MOD 10;
      tmp^ := least_significant_digit + ASCII_ZERO;
      tmp := tmp + 1;
      n := n / 10
   end;
   tmp^ := 0;


   if is_negative then
      reverse_str(s + 1)
   else
      reverse_str(s )

end;
(*=================================================================*)

(*=================================================================
 * Convert a s32 to str
(*=================================================================*)
procedure s32_to_str(orig_n : ^t_s32, s : ^integer);
var
   least_significant_digit : t_s32,
   tmp : ^integer,
   ascii_zero_32 : t_s32,
   zero : t_s32,
   ten : t_s32,
   n : t_s32,
   ans : t_s32,
   tmp_32 : t_s32,
   is_negative : integer;

   
begin
   n[0] := orig_n^[0];
   n[1] := orig_n^[1];

   zero[0] := 0;
   zero[1] := 0;

   ascii_zero_32[0] := 0;
   ascii_zero_32[1] := 48;

   ten[0] := 0;
   ten[1] := 10;
   
   if (s32_le(adr(n), adr(zero))) then begin
      tmp := s;
      tmp^ := ASCII_MINUS;
      tmp := tmp + 1;
      s32_sub(adr(zero), adr(n), adr(n));
      is_negative := 1
   end
   else begin
      tmp := s;
      is_negative := 0
   end;

   if (s32_eq(adr(n), adr(zero))) then begin
      s^ := ASCII_ZERO;
      s := s + 1;
      s^ := 0;
      return
   end;

   (*
   procedure __s32_pos_div_and_mod(
   orig_num : ^t_s32,
   divisor: ^t_s32,
   ans : ^t_s32
   rem : ^t_s32);
   *)
   
   while (s32_ne(adr(n), adr(zero))) do begin
      (* least_significant_digit := n MOD 10; *)
      __s32_pos_div_and_mod(adr(n), adr(ten), adr(ans), adr(least_significant_digit));
      s32_add(adr(least_significant_digit), adr(ascii_zero_32), adr(tmp_32));
      tmp^ := tmp_32[1];

      tmp := tmp + 1;
      s32_copy(adr(ans), adr(n))
   end;
   tmp^ := 0;


   if is_negative then
      reverse_str(s + 1)
   else
      reverse_str(s )

end;
(*=================================================================*)



(*=================================================================*)
procedure num_to_hex_str(
   n : integer,
   s : t_word_ptr);

begin
   BIOS_NumToHexStr(n, s)
end;
(*=================================================================*)


(*=================================================================
 * Check if a string looks like a num
(*=================================================================*)
function str_is_num(s : ^integer) : integer;

begin
   if (s^ = 0) then retval(0);

   if s^ = ASCII_MINUS then begin
      s := s + 1
   end;

   if (s^ = 0) then begin 
      retval(0)
   end;

   while (1) do begin
      if s^ = 0 then begin
         retval(1)
      end;

      if ((s^ < ASCII_ZERO) OR (s^ > ASCII_NINE)) then  begin
         retval(0)
      end;

       s := s + 1
   end
end;
(*=================================================================*)


(*=================================================================
 * Check if a string looks like a hex num
(*=================================================================*)
function str_is_hex_num(s : ^integer) : integer;

begin
   if (s^ = 0) then retval(0);

   while (1) do begin
      if s^ = 0 then begin
         retval(1)
      end;

      if ( (s^ < ASCII_ZERO) OR (s^ > ASCII_NINE) AND
           (s^ < ASCII_A) OR (s^ > ASCII_Z)          ) then begin
         retval(0)
      end;

       s := s + 1
   end
end;
(*=================================================================*)




(*=================================================================*)
procedure compare_strings(S1 : t_word_ptr, S2 : t_word_ptr, 
   AnsPtr : t_word_ptr);
var
   Len: integer;

begin
   while S1^ = S2^ do begin
      if S1^ = 0 then begin
         AnsPtr^ := 1;
         return
      end;
      S1 := S1 + 1;
      S2 := S2 + 1
   end;
   AnsPtr^ := 0
end;
(*=================================================================*)






#endif
