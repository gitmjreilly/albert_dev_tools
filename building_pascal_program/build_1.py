#!/usr/bin/python3
#
import os
import sys

#####################################################################
def usage():
    print("%s BaseName (e.g. main not main.pas)" % (sys.argv[0]))
#####################################################################


#####################################################################
#
# Main Program
# 
if (len(sys.argv) != 2):
    usage()
    sys.exit(1)


pascal_include_dir = "~/albert_dev_tools/p_include"
pascal_include_dir = "."
output_dir = "./output"


base_name = sys.argv[1]
print ("The base_name is %s" % (base_name))


# Use the C preprocessor (on the Pascal source!) for things like:
#  #include 
#  #ifdef
#
cpp_command = "cpp -I %s %s.pas %s/%s.p" %  (pascal_include_dir, base_name, output_dir, base_name)
print("=========================================")
print("Running : %s" % (cpp_command))
status = os.system(cpp_command)
print("   Status from cpp is : %d" % (status))
if (status != 0):
    print("cpp failed!")
    sys.exit(1)


# Compile the output from the cpp run above.  Should still be valid Pascal for this compiler
#
logfile_name = "%s/%s.log" % (output_dir, base_name)
pcomp_command = "pcomp.py %s/%s.p %s/%s.jam %s" % (output_dir, base_name, output_dir, base_name, logfile_name)
print("Running : %s " % (pcomp_command))
status = os.system(pcomp_command)
print("   Status from pcomp is : %d " % (status))
if (status != 0):
    print("Compilation Failed!  Showing log below...")
    print("=========================================")
    tail_command = "tail -20 %s" % logfile_name
    status = os.system(tail_command)
    exit(1)


# Assemble  the output from the pcomp run above.  Should be valid assembly language for this assembler
#
jamasm_command = "jamasm.pl -srcfile %s/%s.jam -objfile %s/%s.hex -listfile %s/%s.lst -errorfile %s/%s.err  " % \
        (output_dir, base_name, output_dir, base_name, output_dir, base_name, output_dir, base_name)
print("Running : %s" % (jamasm_command))
status = os.system(jamasm_command)
print("   Status from assembler  is : %d " % (status))
if (status != 0):
    print("Assembly failed - see log")
    exit(1)


#####################################################################
