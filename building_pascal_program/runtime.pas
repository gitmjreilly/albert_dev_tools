(* This is the runtime file! *)
VAR
   runtime : integer;

   
procedure GetUpper8(num  : integer, ans : ^integer);
var
   i : integer;

begin
   i := 1; 
   while i <= 8  do begin
      num := SRL(num);
      i := i + 1
   end;
   ans^ := num
end;

procedure GetLower8(num  : integer, ans : ^integer);
var
   i : integer;

begin
   ans^ := num AND $00FF
end;

   
   
(* *******************************************************************
 *
 * __is_negative
 * helper function to let compiler know if an integer is negative
 * meant for use by the compiler only
 *
 * ****************************************************************** *)
function __is_negative(a : integer) : integer;

begin
   if (a and $8000)
      then retval(1)
      else retval(0)
end;
(*===================================================================*)



(* *******************************************************************
 *
 * __unsigned_div_and_mod
 * helper procedure to give compiler division
 * __signed_div_and_mod will wrap this procedure
 * meant for use by the compiler
 *
 * ***************************************************************** *)
procedure __unsigned_div_and_mod(
   num : integer, 
   divisor : integer,
   ans_ptr : ^integer,
   rem_ptr : ^integer);

var
   result : integer,
   tmp : integer;

begin
   result := 0;
   tmp := divisor;

   (* Shift tmp over as far as possible
    * It is possible to shift too far, at which point,
    * tmp will go negative.  We check for this special case. *)
   while ( (tmp <= num) AND (tmp > 0)) do tmp := sll(tmp);
   if tmp < 0 then tmp := srl(tmp);
   
   while (tmp >= Divisor) do begin
      if num >= tmp then begin
         result := sll(result) + 1;
         num := num - tmp;
         tmp := srl(tmp)
      end
      else begin
         result := sll(result) ;
         tmp := srl(tmp)
      end
   end;

   ans_ptr^ := result;
   rem_ptr^ := num
end;
(*===================================================================*)


(* *******************************************************************
 *
 * __signed_div_and_mod
 * helper procedure to give compiler division
 * meant for use by the compiler
 *
 * ***************************************************************** *)
procedure __signed_div_and_mod(
   num : integer, 
   divisor : integer,
   ans_ptr : ^integer,
   rem_ptr : ^integer);

begin
   if ( (num >= 0) AND (divisor > 0) ) then begin
      __unsigned_div_and_mod(num, divisor, ans_ptr, rem_ptr);
      return
   end;

   if ( (num < 0) AND (divisor < 0) ) then begin
      num := -num;
      divisor := -divisor;
      __unsigned_div_and_mod(num, divisor, ans_ptr, rem_ptr);
      return
   end;

   if (num < 0) then num := -num;
   if (divisor < 0) then divisor := -divisor;

   __unsigned_div_and_mod(num, divisor, ans_ptr, rem_ptr);
   ans_ptr^ := -ans_ptr^

end;
(*===================================================================*)


(* *******************************************************************
 *
 * __signed_div
 * helper function to give compiler division
 * meant for use by the compiler
 *
 * ***************************************************************** *)
function __signed_div(
   num : integer, 
   divisor : integer) : integer;

var
   ans : integer,
   rem : integer;

begin
   __signed_div_and_mod(num, divisor, adr(ans), adr(rem));
   retval(ans)
end;
(*===================================================================*)



(* *******************************************************************
 *
 * __signed_mod
 * helper function to give compiler modulo
 * meant for use by the compiler
 *
 * ***************************************************************** *)
function __signed_mod(
   num : integer, 
   divisor : integer) : integer;

var
   ans : integer,
   rem : integer;

begin
   __signed_div_and_mod(num, divisor, adr(ans), adr(rem));
   retval(rem)
end;
(*===================================================================*)

(*===================================================================*)
procedure SetES(ESVal : integer);
begin
   ESVal := ESVal;

   ASM
      R_FETCH 1 - FETCH TO_ES
   END
end;
(*===================================================================*)

(*===================================================================*)
procedure LongStore(LongPtr : integer, Val : integer);
begin
   ASM
      R_FETCH 1 - FETCH
      R_FETCH 2 - FETCH
      LONG_STORE
   END
end;
(*===================================================================*)

(*===================================================================*)
procedure LongFetch(LongPtr : integer, ValPtr : ^integer);
begin
   LongPtr := LongPtr;
   ValPtr := ValPtr;

   ASM
      R_FETCH 2 - FETCH
      LONG_FETCH

      R_FETCH 1 - FETCH STORE
   END
end;
(*===================================================================*)


(*===================================================================*)
function __ul(a : integer, b : integer) : integer;
var
   a_is_positive : integer,
   b_is_positive : integer;

begin

   a_is_positive := (a AND $8000) = 0;
   b_is_positive := (b AND $8000) = 0;
   
   if (a_is_positive) then
      if (b_is_positive) then
         retval(a < b)
      else
         retval($FFFF)
   else (* a is negative ie large *)
      if (b_is_positive) then
         retval(0)
      else
         retval(a < b)
         
end;
(*===================================================================*)



(*===================================================================*)
(* a  -3
 * b  -2
 * c   0
 *)
function new__ul(a : integer, b : integer) : integer;
var
   c : integer;
   
begin
   a := a;
   b := b;
   c := 7;
   
   asm
      L_VAR -3 FETCH    # a FETCH
      L_VAR -2 FETCH    # b FETCH
      <                 # <
      L_VAR 0 STORE     # c STORE  (a < b)
   end;
   retval(c) 
end;
(*===================================================================*)



(*===================================================================*)
(*
 * Is a >= b?
 *)
function __uge(a : integer, b : integer) : integer;
begin
   if __ul(a, b) then
      retval(0)
   else
      retval(1)
end;
(*===================================================================*)


(*===================================================================*)
(*
 * Is a <= b?
 *)
function __ule(a : integer, b : integer) : integer;
begin
   if __ul(b, a) then
      retval(0)
   else
      retval(1)

end;
(*===================================================================*)


(*===================================================================*)
(*
 * Is a > b?
 *)
function __ug(a : integer, b : integer) : integer;
begin
   retval((__ul(b, a)))
end;
(*===================================================================*)

