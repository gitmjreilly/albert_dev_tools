""" This is the tokenizer module. """


from emitter import EmitSrc, EmitInit, FinishEmitter
import re

class FileNode(object):
    """ This class describes where we are in an open source file.
    It also notes if this file was included by another so once this
    file is read, reading can continue at the previous file. """

    def __init__(self, FileName):
        """ Initialize by opening FileName. """
        self.InputFile = open(FileName, "r")
        self.LineNum = 0
        self.Line = ""
        self.fname = FileName
        self.Index = 0
        self.LookAheadIsPresent = False
        self.LookAhead = ""
        self.char_list = list()

    def read_line(self):
        """ Read the next line from the file  """
        self.LineNum += 1
        self.Line = self.InputFile.readline()
        if len(self.Line) == 0:
            raise RuntimeError("Got length is 0")
        # Remove EOL
        self.Line = self.Line.rstrip("\n")
        self.Line = self.Line + " "
        self.Index = 0
        EmitSrc(self.Line, self.LineNum)
        self.char_list = list(self.Line)
        # We have to straighten line numbers and file names
        # now that we are using cpp and including files happens there
        # so this compiler only sees a single input file.
                # if re.match(r"[A-F]|[0-9]", ch):
        if re.match(r"^# [0-9]", self.Line):
            # print "LOG saw line inserted by CPP"
            # print "    [", self.Line, "]"
            Stuff = self.Line.split()
            self.LineNum = int(Stuff[1])
            self.fname = Stuff[2].strip()
            # print "    name is[", self.fname, "] num is [", self.LineNum, "]"
            print (f"    name is[{self.fname} num is [{self.LineNum}]")

    def IsAtEOL(self):
        """ Return boolean indicating if we have read to EOL. """
        return(self.Index == len(self.Line))

    def get_ch(self):
        """ Get the next char from the file. """
        ch = self.char_list[self.Index]
        self.Index += 1
        return(ch)

    def close(self):
        """ Close the file associated with this FileNode. """
        self.InputFile.close()


class Tokenizer(object):
    """ This class returns tokens from input files. """
    def __init__(self, InputFileName):
        """ Initialize with the name of the file to be tokenized. """
        self.FileNodeList = FileNode(InputFileName)
        self.returned_ch = ""

    def LineNum(self):
        """ Return the current line num in the current file. """
        return(self.FileNodeList.LineNum)

   
    def __GetCh__(self):
        """ Return the Ch and an EOF flag -
        (ch, is_at_eof) = GetCh() """

        if self.returned_ch != "":
            tmp = self.returned_ch
            self.returned_ch = ""
            return(tmp, False)

        if self.FileNodeList.IsAtEOL():
            try:
                self.FileNodeList.read_line()
            except RuntimeError:
                self.FileNodeList.close()
                print ("DEBUG closing file...")
                return("", True)
                # junk lines below...
                if self.FileNodeList is None:
                    print ("DEBUG returning...")
                    return("", True)

        ch = self.FileNodeList.char_list[self.FileNodeList.Index]
        self.FileNodeList.Index += 1
        return(ch, False)

    def __unget_ch__(self, ch):
        if self.returned_ch != "":
            raise RuntimeError("Tokenizer: tried to unget 2 chars in a row.")
        self.returned_ch = ch


    def get_token(self):
        """ Get the next token from the input stream. """
        if self.FileNodeList.LookAheadIsPresent:
            token = self.FileNodeList.LookAhead
            self.FileNodeList.LookAheadIsPresent = False
            return(token)
        
        self.FileNodeList.LookAheadIsPresent = False

        tmp = list()

        state_num = 0

        while state_num != 99:
            (ch, is_at_eof) = self.__GetCh__()
            if is_at_eof:
                return("")
        
            if state_num == 0:
                if ch.isspace():
                    state_num = 0
                    continue

                if (ch.isalpha()) or (ch == "_"):
                    tmp.append(ch)
                    state_num = 1
                    continue

                if ch.isdigit():
                    tmp.append(ch)
                    state_num = 2
                    continue

                if ch == ":":
                    tmp.append(ch)
                    state_num = 3
                    continue

                if ch == ";":
                    tmp.append(ch)
                    return(ch)

                if ch == "[":
                    return(ch)

                if ch == "]":
                    return(ch)

                if ch == "+":
                    return(ch)

                if ch == "-":
                    return(ch)

                if ch == "*":
                    return(ch)

                if ch == "/":
                    return(ch)

                if ch == ".":
                    return(ch)

                if ch == "(":
                    state_num = 9
                    continue

                if ch == ")":
                    return(ch)

                if ch == "=":
                     return(ch)

                if ch == ",":
                     return(ch)

                if ch == ">":
                    tmp.append(ch)
                    state_num = 4
                    continue

                if ch == "<":
                    tmp.append(ch)
                    state_num = 5
                    continue

                if ch == "^":
                    return(ch)

                if ch == '"':
                    tmp.append(ch)
                    state_num = 6
                    continue

                if ch == "#":
                    state_num = 7
                    continue

                if ch == "$":
                    tmp.append(ch)
                    state_num = 8
                    continue

            if state_num == 1:
                if ((ch.isalpha()) or (ch.isdigit()) or (ch == "_")):
                    tmp.append(ch)
                    state_num = 1
                    continue
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 2:
                if ch.isdigit():
                    tmp.append(ch)
                    state_num = 2
                    continue
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 3: # We got here because we saw ':'
                if ch == "=":
                    tmp.append(ch)
                    return("".join(tmp).upper())
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 4: # We got here because we saw '>'
                if ch == "=":
                    tmp.append(ch)
                    return("".join(tmp).upper())
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 5: # We got here because we saw '<'
                if ch == "=":
                    tmp.append(ch)
                    return("".join(tmp).upper())

                if ch == ">":
                    tmp.append(ch)
                    return("".join(tmp).upper())
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 6: # We got here because we saw '"'
                if ch == '"':
                    tmp.append(ch)
                    return("".join(tmp))

                tmp.append(ch)
                continue
 
            if state_num == 7:
                # We got here because we are tokenizing a comment to EOL
                if self.FileNodeList.IsAtEOL():
                    state_num = 0
                    continue
                else:
                    state_num = 7
                    continue

            if state_num == 8:
                # We got here because we saw a $
                if re.match(r"[A-F]|[0-9]", ch):
                    tmp.append(ch)
                    state_num = 8
                else:
                    self.__unget_ch__(ch)
                    return("".join(tmp).upper())

            if state_num == 9: 
                if ch != "*":
                    self.__unget_ch__(ch)
                    return("(")

                state_num = 10
                continue

            if state_num == 10:
                if ch != "*":
                    continue
                state_num = 11
                continue

            if state_num == 11:
                if ch == ")":
                    state_num = 0
                    continue
                
                state_num = 10
                continue

    def get_asm_token(self):
        """ Get the next asm token from the input stream. """
        if self.FileNodeList.LookAheadIsPresent:
            token = self.FileNodeList.LookAhead
            self.FileNodeList.LookAheadIsPresent = False
            return(token)
        
        self.FileNodeList.LookAheadIsPresent = False

        tmp = list()

        state_num = 0

        while True:
            (ch, is_at_eof) = self.__GetCh__()
            if is_at_eof:
                return("")
        
            if state_num == 0:
                if ch.isspace():
                    state_num = 0
                    continue

                if ch == ";":
                    tmp.append(ch)
                    print (f"token is {ch}")
                    return(ch)

                tmp.append(ch)
                state_num = 1
                continue

            if state_num == 1:
                if ch == ";":
                    self.__unget_ch__(ch)
                    state_num = 0
                    return("".join(tmp).upper())
                    
                if ch.isspace():
                    self.__unget_ch__(ch)
                    state_num = 0
                    return("".join(tmp).upper())

                tmp.append(ch)
                state_num = 1
                continue


    def get_look_ahead(self):
        """ Get the lookahead from the token stream. """
        if self.FileNodeList.LookAheadIsPresent:
            return(self.FileNodeList.LookAhead)

        token = self.get_token()
        if token == "":
            return("")
        
        self.FileNodeList.LookAhead = token
        self.FileNodeList.LookAheadIsPresent = True
        return(self.FileNodeList.LookAhead)

    def get_asm_look_ahead(self):
        """ Get the lookahead from the token stream. """
        if self.FileNodeList.LookAheadIsPresent:
            return(self.FileNodeList.LookAhead)

        token = self.get_asm_token()
        if token == "":
            return("")
        
        self.FileNodeList.LookAhead = token
        self.FileNodeList.LookAheadIsPresent = True
        return(self.FileNodeList.LookAhead)

    def get_line_num(self):
        """ Get the current source line num """
        s = self.FileNodeList.fname + "/" + str(self.FileNodeList.LineNum)
#        return(self.FileNodeList.LineNum)
        return(s)



                
# Main Program
def main():
    EmitInit("listfile")
    t = Tokenizer("sample.in")
    while True:
       token = t.get_token()
       if token == "":
           break
       print (token)

    print ("Done.")
    FinishEmitter()
