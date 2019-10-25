


def Emit(Line, LineNum):
    """ Emit Line to the annotated listing file. """

    global NewLineWasEmitted
    global OutputFile

    if NewLineWasEmitted:
        OutputFile.writelines('               ');
    OutputFile.writelines(Line + ' ');
    NewLineWasEmitted = False


def EmitLabel(AsmLabel, LineNum):
    """ Emit line to the annotated listing file. """

    global NewLineWasEmitted
    global OutputFile

    if not NewLineWasEmitted:
        OutputFile.writelines('\n')

    OutputFile.writelines('               ')
    OutputFile.writelines(AsmLabel + ':\n')
    NewLineWasEmitted = True


def EmitSrc(SrcLine, LineNum):
    """ Emit line to the annotated listing file. """

    global NewLineWasEmitted
    global OutputFile

    # SrcLine = SrcLine.rstrip()
    # SrcLine = SrcLine + " " # to get formatting compatibility with PASCAL version

    if not NewLineWasEmitted:
        OutputFile.writelines('\n')

    OutputFile.writelines((';SRC ', '%4d'%LineNum, '|', '%s'%SrcLine))
    OutputFile.writelines("\n")
    NewLineWasEmitted = True




def FinishEmitter():
    global OutputFile

    OutputFile.close()
    

def EmitInit(OutputFileName):
    """ Initialize the emitter, by opening OutputFileName. """

    global OutputFile
    global NewLineWasEmitted

    OutputFile = open(OutputFileName, 'w')
    NewLineWasEmitted = True
