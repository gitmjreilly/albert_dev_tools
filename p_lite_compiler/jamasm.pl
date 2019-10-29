#!/usr/bin/perl

use strict;

###############################################################################
#
# External Modules:
#
use Getopt::Long;

#
# Use this module to handle tabs properly; It implicitly uses $tabstop.
#
use Text::Tabs;
$tabstop = 3;

use Text::ParseWords;
###############################################################################


###############################################################################
# Constants
my $SRC_LINE_LISTING_WIDTH = 120;
my $CODE_WORD = 0;
my $DATA_WORD = 1;
my $GUARD_WORD = 2;
###############################################################################


###############################################################################
#
# Global Variabes
#
my $TokenPointer;
my @FileBuffer;
my %SymbolTable;
my $LineNum;
my @TokenList;
my %PsuedoOpInfo;
my $PassNum;
my $LC;
my %InstructionInfo;
my @ObjectBuffer;
my @TypeBuffer;
my @ValToHex;
my %HexToVal;
my %SubroutineSymbolTables;
my $LoadAddress;
my $UseNewFormat;
my $GlobalError = 0;

#
# Placing the filenames here so they can be referenced
# by multiple subs
#
my $SrcFileName;
my $ObjFileName;
my $ErrorFileName;
my $ListFileName;

###############################################################################


###############################################################################
sub Usage {
	printf("$0 -srcfile SrcFile -objfile ObjFile -listfile ListFile -errorfile ErrorFile [-loadaddress n]\n");
}
###############################################################################


###############################################################################
sub Init {

$InstructionInfo{"&"}->{'Value'} = 27;
$InstructionInfo{"AND"}->{'Value'} = 27;
$InstructionInfo{"BRA"}->{'Value'} = 4;
$InstructionInfo{"JMP"}->{'Value'} = 4;
$InstructionInfo{"CS_FETCH"}->{'Value'} = 43;
$InstructionInfo{"DI"}->{'Value'} = 37;
$InstructionInfo{"JMPF"}->{'Value'} = 12;
$InstructionInfo{"PUSH"}->{'Value'} = 2;
$InstructionInfo{"DROP"}->{'Value'} = 7;
$InstructionInfo{"DS_FETCH"}->{'Value'} = 42;
$InstructionInfo{"DUP"}->{'Value'} = 19;
$InstructionInfo{"EI"}->{'Value'} = 35;
$InstructionInfo{"ES_FETCH"}->{'Value'} = 41;
$InstructionInfo{"=="}->{'Value'} = 31;
$InstructionInfo{"FETCH"}->{'Value'} = 9;
$InstructionInfo{"FROM_R"}->{'Value'} = 14;
$InstructionInfo{"HALT"}->{'Value'} = 3;
$InstructionInfo{"JSR"}->{'Value'} = 10;
$InstructionInfo{"JSRINT"}->{'Value'} = 33;
$InstructionInfo{"K_SP_STORE"}->{'Value'} = 47;
$InstructionInfo{"<"}->{'Value'} = 5;
$InstructionInfo{"LONG_FETCH"}->{'Value'} = 44;
$InstructionInfo{"LONG_STORE"}->{'Value'} = 45;
$InstructionInfo{"LONG_TYPE_STORE"}->{'Value'} = 53;
$InstructionInfo{"L_VAR"}->{'Value'} = 51;
$InstructionInfo{"MUL"}->{'Value'} = 30;
$InstructionInfo{'*'}->{'Value'} = 30;
$InstructionInfo{"NEG?"}->{'Value'} = 26;
$InstructionInfo{"NOP"}->{'Value'} = 1;
$InstructionInfo{"OR"}->{'Value'} = 28;
$InstructionInfo{"|"}->{'Value'} = 28;
$InstructionInfo{"OVER"}->{'Value'} = 22;
$InstructionInfo{"+"}->{'Value'} = 24;
$InstructionInfo{"++"}->{'Value'} = 6;
$InstructionInfo{"POPF"}->{'Value'} = 49;
$InstructionInfo{"PUSHF"}->{'Value'} = 48;
$InstructionInfo{"RESET"}->{'Value'} = 0;
$InstructionInfo{"RET"}->{'Value'} = 11;
$InstructionInfo{"RETI"}->{'Value'} = 34;
$InstructionInfo{"RP_FETCH"}->{'Value'} = 16;
$InstructionInfo{"RP_STORE"}->{'Value'} = 17;
$InstructionInfo{"R_FETCH"}->{'Value'} = 18;
$InstructionInfo{"S_LESS"}->{'Value'} = 50;
$InstructionInfo{"SLL"}->{'Value'} = 15;
$InstructionInfo{"SP_FETCH"}->{'Value'} = 20;
$InstructionInfo{"SP_STORE"}->{'Value'} = 23;
$InstructionInfo{"SRA"}->{'Value'} = 36;
$InstructionInfo{"SRL"}->{'Value'} = 38;
$InstructionInfo{"STORE"}->{'Value'} = 8;
$InstructionInfo{"STORE2"}->{'Value'} = 52;
$InstructionInfo{"-"}->{'Value'} = 25;
$InstructionInfo{"SWAP"}->{'Value'} = 21;
$InstructionInfo{"SYSCALL"}->{'Value'} = 46;
$InstructionInfo{"TO_DS"}->{'Value'} = 40;
$InstructionInfo{"TO_ES"}->{'Value'} = 39;
$InstructionInfo{"TO_R"}->{'Value'} = 13;
$InstructionInfo{"UM+"}->{'Value'} = 32;
$InstructionInfo{"XOR"}->{'Value'} = 29;


$PsuedoOpInfo{"CONST"} = 1;
$PsuedoOpInfo{"DS"} = 1;
$PsuedoOpInfo{"DG"} = 1;
$PsuedoOpInfo{"DW"} = 1;
$PsuedoOpInfo{"ENDDW"} = 1;
$PsuedoOpInfo{"DSTR"} = 1;


	$ValToHex[0]  = "0";
	$ValToHex[1]  = "1";
	$ValToHex[2]  = "2";
	$ValToHex[3]  = "3";
	$ValToHex[4]  = "4";
	$ValToHex[5]  = "5";
	$ValToHex[6]  = "6";
	$ValToHex[7]  = "7";
	$ValToHex[8]  = "8";
	$ValToHex[9]  = "9";
	$ValToHex[10] = "A";
	$ValToHex[11] = "B";
	$ValToHex[12] = "C";
	$ValToHex[13] = "D";
	$ValToHex[14] = "E";
	$ValToHex[15] = "F";

	$HexToVal{'0'} = 0;
	$HexToVal{'1'} = 1;
	$HexToVal{'2'} = 2;
	$HexToVal{'3'} = 3;
	$HexToVal{'4'} = 4;
	$HexToVal{'5'} = 5;
	$HexToVal{'6'} = 6;
	$HexToVal{'7'} = 7;
	$HexToVal{'8'} = 8;
	$HexToVal{'9'} = 9;
	$HexToVal{'A'} = 10;
	$HexToVal{'B'} = 11;
	$HexToVal{'C'} = 12;
	$HexToVal{'D'} = 13;
	$HexToVal{'E'} = 14;
	$HexToVal{'F'} = 15;

}
###############################################################################


###############################################################################
sub Error {
	my $Msg = $_[0];

	printf(ERRORFILE "ERROR : Line $LineNum $Msg\n");
    $GlobalError = 1;
}
###############################################################################


###############################################################################
sub ReadFile {
	my $FileName = $_[0];

	open (INPUT_FILE, "<$FileName") || die ("Could not open $FileName; exiting...\n");
	#
	# Push an empty first line. We do this because
	# we want linenums to start at 1 not 0, but array starts at zero.
	# 
	push (@FileBuffer, "");
	while (chop(my $Line = <INPUT_FILE>)) {
		$Line =~ s/\s+$//;
		push (@FileBuffer, $Line);
	}
	close(INPUT_FILE);
}
###############################################################################


###############################################################################
sub GetNextToken {
	my $Token = $TokenList[$TokenPointer];
	$TokenPointer++;
	return($Token);
}
###############################################################################


###############################################################################
sub NumToHex {
	my $Num = $_[0];

	my $Str;
	for my $i (1..4) {
		my $NextVal = $Num % 16;
		$Num >>= 4;
		$Str = $ValToHex[$NextVal] . $Str;
	}
	return( $Str);
}
###############################################################################


###############################################################################
# Assume Hex str starts with "0x"
sub HexToNum {
	my $Hex = $_[0];
	my $Sum;

	my @Chars = (split(' *', $Hex));
	#
	# remove "0x" from beginning
	#
	shift(@Chars);
	shift(@Chars);
	foreach my $ch (@Chars) {
		$Sum = $Sum * 16 + $HexToVal{$ch};
	}
	return $Sum;

}
###############################################################################


###############################################################################
sub IsInstruction {
	my $Token = $_[0];

	return(defined($InstructionInfo{$Token}));
}
###############################################################################


###############################################################################
sub IsPsuedoOp {
	my $Token = $_[0];

	return(defined($PsuedoOpInfo{$Token}));
}
###############################################################################


###############################################################################
sub IsNumber {
	my $Token = $_[0];

	return ($Token =~ /^[0-9]+$|^-[0-9]+$/);
}
###############################################################################


###############################################################################
sub IsHexNumber {
	my $Token = $_[0];

	return ($Token =~ /^0(x|X).+/);
}
###############################################################################


###############################################################################
sub IsCommentDelimiter {
	my $Token = $_[0];

	return ($Token =~ /^;|^#/);
}
###############################################################################


###############################################################################
sub IsLabel {
	my $Token = $_[0];

	return ($Token =~ /^.*:/);
}
###############################################################################


###############################################################################
sub IsGlobalVariable {
	my $Token = $_[0];

	my @Stuff = split('\'', $Token);
	#
	# Variable may or may not have attributes so we can't just look at the token.
	my $VarName = $Stuff[0];
	if (defined($SymbolTable{$VarName})) {
		return 1
	}

	return 0
}
###############################################################################


###############################################################################
sub AddLabelToSymbolTable {
	my $Label = $_[0];
	my $LC = $_[1];

	if (defined($SymbolTable{$Label})) {
		Error("Label [$Label] already in Symbol Table; dup def on line [$LineNum]\n");
		return;
	}

	$SymbolTable{$Label}->{'Value'} = $LC;
}
###############################################################################


###############################################################################
sub AssembleInstruction {
	my $Token = $_[0];

	if (! defined($InstructionInfo{$Token})) {
		Error("Internal error tried to assemble unknown instr $Token\n");
		return;
	}
	
	if ($PassNum == 1) {
		$LC++;
		if ($Token eq "JSR" || 
		    $Token eq "BRA" || 
		    $Token eq "JMP" || 
		    $Token eq "JMPF" || 
		    $Token eq "L_VAR") { 
			$LC++; 
			$TokenPointer++;	# Skip the label or numeric const associated w/these  instructions
		}
		return;
	}

	#
	# This is Pass 2; assemble the code.
	#
	EmitToObjectAndList($LC, $InstructionInfo{$Token}->{'Value'}, $CODE_WORD);
	$LC++;


	if ($Token eq "JSR" || $Token eq "BRA" || $Token eq "JMP" || $Token eq "JMPF" || $Token eq "L_VAR") {
		$Token = $TokenList[$TokenPointer];
		$TokenPointer++;

		if (defined($SymbolTable{$Token}) ) {
			EmitToObjectAndList($LC, $SymbolTable{$Token}->{'Value'}, $CODE_WORD);
		}
		elsif (IsNumber($Token)) {
			EmitToObjectAndList($LC, $Token, $CODE_WORD);
		}
		else {
			Error("Symbol [$Token] not found on line [$LineNum]\n");
		}


		$LC++;		
	}
}
###############################################################################


###############################################################################
sub AssembleNumber {
	my $Token = $_[0];

	#
	# Numbers require 2 words of mem: one for push; one for val
	#

	if ($PassNum == 1) {
		$LC += 2;
		return;
	}

	AssembleInstruction("PUSH");
	EmitToObjectAndList($LC, $Token, $CODE_WORD);
	$LC++;
}
###############################################################################


###############################################################################
sub AssembleGlobalVariable {
	my $Token = $_[0];
	
	my @Stuff = split('\'', $Token);
	my $VariableName = $Stuff[0];
	my $Attribute = $Stuff[1];
	
	my $LCOffset;
	
	if ($Attribute eq "") {
		$Attribute = "addr";
	}
	
	if ($Attribute eq "addr") {
		$LCOffset = 0;
	}
	elsif ($Attribute eq "val") {
		$LCOffset = 1;
	}
	elsif ($Attribute eq "ref") {
		$LCOffset = 2;
	}
	else {
		Error("Unknown attribute [$Attribute]\n");
		return;
	}	

	
	if ($PassNum == 1) {
		$LC += 2 + $LCOffset;
		return;
	}
		
	#
	# If we've gotten this far, we are in the 2nd pass
	#
	AssembleNumber($SymbolTable{$VariableName}->{'Value'});
	if ($Attribute eq "val") {
		AssembleInstruction("FETCH");
		return;
	}
	if ($Attribute eq "ref") {
		AssembleInstruction("FETCH");
		AssembleInstruction("FETCH");
		return;
	}

}
###############################################################################


###########################################################################
sub ProcessLabel {
	my $Token = $_[0];

	# Remove the ':'
	chop($Token);

	if ($PassNum == 2) { return; }

	AddLabelToSymbolTable($Token, $LC);
}
###############################################################################


###############################################################################
sub ProcessPsuedoOp {
	my $Token = $_[0];


	if ($Token eq "CONST") {
		if ($PassNum == 2) { 
			$TokenPointer += 2;
			return; 
		}

		my $Symbol = $TokenList[$TokenPointer];
		$TokenPointer++;

		my $Val = $TokenList[$TokenPointer];
		$TokenPointer++;

		if (IsHexNumber($Val)) {
			AddLabelToSymbolTable($Symbol, HexToNum($Val));
		}
		else {
			AddLabelToSymbolTable($Symbol, $Val);
		}

		return;
	}

	if ($Token eq "DG") {
		if ($PassNum == 1) {
			$LC += 1;
			return;
		}
		EmitToObjectAndList($LC, 0, $GUARD_WORD);
		$LC++;
		return;
	}

	if ($Token eq "DS") {
		my $StorageSize = $TokenList[$TokenPointer];
		$TokenPointer++;
		if ($PassNum == 1) {
			$LC += $StorageSize;
			return;
		}

		for my $i (1..$StorageSize) {
			EmitToObjectAndList($LC, 0, $DATA_WORD);
			$LC++;
		}
		return;
	}

	if ($Token eq "DW") {

		while (1) {
			my $NextToken = $TokenList[$TokenPointer];
			$TokenPointer++;

			if ($NextToken eq "ENDDW") { last; }

			if ($PassNum == 2) {
				if (IsHexNumber($NextToken)) {
					EmitToObjectAndList($LC, HexToNum($NextToken), $DATA_WORD);
				}
				else {
					EmitToObjectAndList($LC, $NextToken, $DATA_WORD);
				}
			}
			$LC++;
		}
		return;
	}
		
}
###############################################################################


###############################################################################
sub EmitToObjectAndList {
	my $LC = $_[0];
	my $Val = $_[1];
	my $ValType = $_[2];

	push(@ObjectBuffer, $Val);
	push(@TypeBuffer, $ValType);

	# Ignoring LC for now...

	SendObjectWordToList($Val);
}
###############################################################################


###############################################################################
sub SendObjectWordToList {
	my $ObjectWord = $_[0];
	printf(LISTFILE "%s ", NumToHex($ObjectWord));
}
###############################################################################


###############################################################################
sub SendLCToList {
	my $LC = $_[0];
	printf(LISTFILE "@%s ", NumToHex($LC));
}
###############################################################################


###############################################################################
sub SendSrcLineToList {
	my $SrcLine = $_[0];

	#
	# Expand tabs so listing looks pretty.
	#
	$SrcLine = expand($SrcLine);

	my $TruncatedLine = substr($SrcLine, 0, $SRC_LINE_LISTING_WIDTH);
	printf(LISTFILE "%-${SRC_LINE_LISTING_WIDTH}s ", $TruncatedLine);
}
###############################################################################


###############################################################################
sub SendLineNumToList {
	my $LineNum = $_[0];
	printf(LISTFILE "%4d ", $LineNum);
}
###############################################################################


###############################################################################
sub SendNLToList {
	printf(LISTFILE "\n");
}
###############################################################################


###############################################################################
sub OutputObject {
	my $Val = $_[0];

	if (! $UseNewFormat) { # Assume Pat's original loader format
		my $Size = $#ObjectBuffer + 1;
		printf(OBJFILE "%s", NumToHex($Size));
		printf(OBJFILE "%s", 	NumToHex($SymbolTable{'MAIN'}->{'Value'}));
		foreach my $ObjectWord (@ObjectBuffer) {
			printf(OBJFILE "%s", NumToHex($ObjectWord));
		}
	}
	else { # We are generating the new ASCII HEX loader format.
		my $Size = $#ObjectBuffer + 1;
		printf(OBJFILE "%s", NumToHex(0));
		printf(OBJFILE "%s", NumToHex(2));
		printf(OBJFILE "%s", NumToHex($Size));
		printf(OBJFILE "%s", NumToHex($LoadAddress));
		printf(OBJFILE "%s", 	NumToHex($SymbolTable{'MAIN'}->{'Value'}));
		foreach my $ObjectWord (@ObjectBuffer) {
			printf(OBJFILE "%s", NumToHex($ObjectWord));
		}
	}
	close(OBJFILE);

    #
    # Create another output file for use with the simulator
    # This is a BINARY format
    #
    my $SimulatorObjFileName = $ObjFileName . ".sim" ;

    open(OBJFILE, ">$SimulatorObjFileName") || 
        die("Could not open $ObjFileName\n");

	my $Size = $#ObjectBuffer + 1;

    # First 2 hex words are the MAGIC signature for use with the loader
#	printf(OBJFILE "%s\r", NumToHex(0));
#	printf(OBJFILE "%s\r", NumToHex(2));
#
#	printf(OBJFILE "%s\r", NumToHex($Size));
#	printf(OBJFILE "%s\r", NumToHex($LoadAddress));
#	printf(OBJFILE "%s\r", 	NumToHex($SymbolTable{'MAIN'}->{'Value'}));

	printf(OBJFILE "%s%s", chr(0), chr(0));
	printf(OBJFILE "%s%s", chr(0), chr(2));

	printf(OBJFILE "%s%s", 
        chr(($Size >>8) & 255), 
        chr($Size & 255)         );
	printf(OBJFILE "%s%s", 
        chr(($LoadAddress >>8) & 255), 
        chr($LoadAddress & 255)        );
	printf(OBJFILE "%s%s", 
        chr(($SymbolTable{'MAIN'}->{'Value'} >>8) & 255), 
        chr($SymbolTable{'MAIN'}->{'Value'}  & 255  )      );


    if ($#ObjectBuffer != $#TypeBuffer) {
        printf("FATAL Error ObjectBuffer and TypeBuffer are not the same length\n");
        exit(1);
    }

    my $i;
    for $i (0..$#ObjectBuffer) {
#		printf(OBJFILE "%s\r", NumToHex($TypeBuffer[$i]));
#		printf(OBJFILE "%s\r", NumToHex($ObjectBuffer[$i]));

        printf(OBJFILE "%s", chr($TypeBuffer[$i] & 255));
		printf(OBJFILE "%s%s", 
            chr(($ObjectBuffer[$i] >> 8) & 255), 
            chr($ObjectBuffer[$i]  & 255)        );
	}
	close(OBJFILE);

}
###############################################################################


###############################################################################
# 
# Main Program
#
{
$| = 1;

Init;

GetOptions(	
	"loadaddress=i" => \$LoadAddress,
	"srcfile=s"		=> \$SrcFileName,
	"objfile=s"		=> \$ObjFileName,
	"errorfile=s"		=> \$ErrorFileName,
	"listfile=s"	=> \$ListFileName);
	
#
# Note "usenewformat" is not required.  
# Without it, Pat's original loader format will be generated.
# With it, my new format will be generated.  The main difference
# is the explicit setting of a load address.
#	
if (defined($LoadAddress)) {
	$UseNewFormat = 1;
}
else {
	printf("DEBUG using OLD loader format\n");
	$UseNewFormat = 0;
}
	

if (! defined($SrcFileName) ) {
	printf(STDERR "ERROR: No source file specified.\n");
	Usage();
	exit(1);
}

if (! defined($ObjFileName) ) {
	printf(STDERR "ERROR: No object file specified.\n");
	Usage();
	exit(1);
}

if (! defined($ListFileName) ) {
	printf(STDERR "ERROR: No LISTFILE file specified.\n");
	Usage();
	exit(1);
}

if (! defined($ErrorFileName) ) {
	printf(STDERR "ERROR: No ERRORFILE file specified.\n");
	Usage();
	exit(1);
}

open(LISTFILE, ">$ListFileName") || die("Could not open $ListFileName\n");
open(OBJFILE, ">$ObjFileName") || die("Could not open $ObjFileName\n");
open(ERRORFILE, ">$ErrorFileName") || die("Could not open $ErrorFileName\n");


ReadFile($SrcFileName);

#
# Do 2 Pass Assembly
#	
$PassNum = 1;
while (1) {

if ($UseNewFormat) {
	$LC = $LoadAddress;
}
else {
	$LC = 256 * 4 + 3;
	$LoadAddress = $LC;
}

	printf("LC is %4x\n", $LC);


	if ($PassNum > 2) { last; }

	#
	# Iterate over all lines in the the FileBuffer
	#
	$LineNum = 1;
	while (1) {

		if ($LineNum > $#FileBuffer) { last; }

		my $Line = $FileBuffer[$LineNum];

		if ($PassNum == 2) {
			SendLineNumToList($LineNum);
			SendSrcLineToList($Line);
			SendLCToList($LC);
		}

		@TokenList = split(' ', $Line);

		#
		# Iterate over all tokens ON A LINE
		#
		$TokenPointer = 0;
		while (1) {
			if ($TokenPointer > $#TokenList) { last; };

			my $Token = $TokenList[$TokenPointer];
			$TokenPointer++;

			if (IsInstruction($Token)) {
				AssembleInstruction($Token);
				next; 
			}
   
  			if (IsPsuedoOp($Token)) {
  				ProcessPsuedoOp($Token);
  				next; 
	  		}

			if (IsNumber($Token)) {
				AssembleNumber($Token);
				next;
			}

			if (IsHexNumber($Token)) {
				my $Num = HexToNum($Token);
				AssembleNumber($Num);
				next;
			}

			if (IsLabel($Token)) {
				ProcessLabel($Token);
				next;
			}

			if (IsCommentDelimiter($Token)) {
				last;
			}

			if (IsGlobalVariable($Token)) {
				AssembleGlobalVariable($Token);
				next;
			}
				
			Error("Unknown token [$Token] on line [$LineNum]\n");
		}
		$LineNum++;

		if ($PassNum == 2) { SendNLToList; }

	}
	$PassNum++;
}

printf(LISTFILE "Global Symbol table:\n");
foreach my $Symbol (sort(keys(%SymbolTable))) {
	printf(LISTFILE "%-15s %4s\n", $Symbol, NumToHex($SymbolTable{$Symbol}->{'Value'}));
}

printf(LISTFILE "Subroutine Symbol tables:\n");
foreach my $SubroutineName (keys(%SubroutineSymbolTables)) {
	printf(LISTFILE "  Sub is $SubroutineName \n");
	my $LocalSymbolTablePtr = $SubroutineSymbolTables{$SubroutineName};
	foreach my $LocalVar (sort(keys(%{$LocalSymbolTablePtr}))) {
		printf(LISTFILE "    Local Var $LocalVar\n");
		printf(LISTFILE "      Size $LocalSymbolTablePtr->{$LocalVar}->{'Size'}\n");
		printf(LISTFILE "      LC   $LocalSymbolTablePtr->{$LocalVar}->{'LC'}\n");		
	}
}


OutputObject;
exit($GlobalError);

}
