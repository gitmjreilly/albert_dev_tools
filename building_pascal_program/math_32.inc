#ifndef MATH_32
#define MATH_32

#define MATH_COLOR ANSI_WHITE

type
   t_s32 = array[2] of integer;
   
function s16_carry(a : integer, b : integer) : integer;
var
   c : integer;
   
begin
   a := a;
   b := b;
   c := 7;
   
   asm
      L_VAR -3 FETCH    # a FETCH
      L_VAR -2 FETCH    # b FETCH
      UM+               # UM_PLUS
      L_VAR 0 STORE     # c STORE  (the carry)
      DROP              # throway the sum
   end;
   retval(c)
   
end;


procedure s32_set_zero(a : ^t_s32);
begin
   a^[0] := 0;
   a^[1] := 0
end;  


procedure s32_copy(src : ^t_s32, dst : ^t_s32);
begin
   dst^[0] := src^[0];
   dst^[1] := src^[1]
end;  



function s16_borrow(a : integer, b: integer) : integer;
begin
   if (__ul(a, b)) then begin
      retval(1)
   end
   else begin
      retval(0)
   end
end;

procedure s32_sll(a : ^t_s32);
var
   c : integer;
   
begin
   if a^[1] AND $8000 then c := 1 else c := 0;
   
   a^[1] := sll(a^[1]);
   a^[0] := sll(a^[0]) + c
end;


procedure s32_srl(a : ^t_s32);
var
   c : integer;
   
begin
   if a^[0] AND $0001 then c := $8000 else c := 0;
   
   a^[1] := srl(a^[1]) + c;
   a^[0] := srl(a^[0])
end;


procedure s32_add(a : ^t_s32, b : ^t_s32, c : ^t_s32);
var
   c_tmp : t_s32;
begin
   c_tmp[1] := a^[1] + b^[1];
   c_tmp[0] := a^[0] + b^[0] + s16_carry(a^[1], b^[1]);
   c^[1] := c_tmp[1];
   c^[0] := c_tmp[0]   
end;


procedure old_s32_sub(a : ^t_s32, b : ^t_s32, c : ^t_s32);
var
   c_tmp : t_s32;
   
begin
   c_tmp[1] := a^[1] - b^[1];
   c_tmp[0] := a^[0] - b^[0] - s16_borrow(a^[1], b^[1]);
   c^[1] := c_tmp[1];
   c^[0] := c_tmp[0]
end;


procedure s32_sub(a : ^t_s32, b : ^t_s32, c : ^t_s32);
var
   borrow : integer,
   c_tmp : t_s32;
   
begin
   c_tmp[1] := a^[1] - b^[1];
   
   borrow := s16_borrow(a^[1], b^[1]);
   
   c_tmp[0] := a^[0] - b^[0] - borrow;

   c^[1] := c_tmp[1];
   c^[0] := c_tmp[0]
end;


procedure s32_mul(a_in : ^t_s32, b_in : ^t_s32, c : ^t_s32);
var
   a : t_s32,
   b : t_s32,
   i : integer;
   
begin
   s32_copy(a_in, adr(a));
   s32_copy(b_in, adr(b));
   
   i := 0;
   c^[0] := 0;
   c^[1] := 0;
   while i < 32 do begin
      if b[1] AND $0001 then
         s32_add(adr(a), c, c);
      s32_sll(adr(a));
      s32_srl(adr(b));
      i := i + 1
   end
end;   

   
(* a < b *)   
function s32_l(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] < b^[0] then retval(1);
   if a^[0] > b^[0] then retval(0);
   (* Upper words are equal; check lower words *)
   if __ul(a^[1], b^[1]) then retval(1);
   retval(0)
end ;  


(* a <= b *)   
function s32_le(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] < b^[0] then retval(1);
   if a^[0] > b^[0] then retval(0);
   (* Upper words are equal; check lower words *)
   if __ule(a^[1], b^[1]) then retval(1);
   retval(0)
end ;  


(* a > b ? *)
function s32_g(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] > b^[0] then retval(1);
   if a^[0] < b^[0] then retval(0);
   (* Upper words are equal; check lower words *)
   if __ug(a^[1], b^[1]) then retval(1);
   retval(0)
end ;  


(* a >= b ? *)
function s32_ge(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] > b^[0] then retval(1);
   if a^[0] < b^[0] then retval(0);
   (* Upper words are equal; check lower words *)
   if __uge(a^[1], b^[1]) then retval(1);
   retval(0)
end ;  



(* 
 * 32 bit positive only div and mod calc.
 *)
procedure __s32_pos_div_and_mod(
   orig_num : ^t_s32,
   divisor: ^t_s32,
   ans : ^t_s32
   rem : ^t_s32);
   
var
   zero : t_s32,
   one : t_s32,
   internal_num : t_s32,
   num : ^t_s32,
   result : t_s32,
   tmp : t_s32;
   
begin
   num := adr(internal_num);
   s32_copy(orig_num, num);
  
   s32_set_zero(adr(zero));
   s32_set_zero(adr(result));
   s32_copy(divisor, adr(tmp));
   one[0] := 0; one[1] := 1;
   
   while ( s32_le(adr(tmp), num) AND s32_g(adr(tmp), adr(zero))     ) do begin
      s32_sll(adr(tmp))
   end;
   if s32_l(adr(tmp), adr(zero)) then begin
      s32_srl(adr(tmp))
   end;
   
  
   while s32_ge(adr(tmp), divisor) do begin
      if s32_ge(num, adr(tmp)) then begin
         s32_sll(adr(result));
         s32_add(adr(result), adr(one), adr(result));
         s32_sub(num, adr(tmp), num)
      end
      else begin
         s32_sll(adr(result))
      end;
      s32_srl(adr(tmp))
   end;
   
   s32_copy(adr(result), ans);
   s32_copy(num, rem)
end;
   
     
procedure s32_min(a : ^t_s32, b : ^t_s32, c : ^t_s32);
begin
   if s32_l(a, b) then begin
      s32_copy(a, c)
   end
   else begin
      s32_copy(b, c)
   end
end;


function s32_eq(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] <> b^[0] then retval(0);
   if a^[1] <> b^[1] then retval(0);
   retval(1)
end;
   
function s32_ne(a : ^t_s32, b : ^t_s32) : integer;
begin
   if a^[0] <> b^[0] then retval(1);
   if a^[1] <> b^[1] then retval(1);
   retval(0)
end;
   
#endif