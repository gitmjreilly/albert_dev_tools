#---------------------------------------------------------------------
hard_log_file_name = None
indent_level = 0
log_file = None
    
def init( log_filename):
    """ Initialize the Logger with StringIO. """
    global log_file
    global indent_level
    global hard_log_file_name
    hard_log_file_name = log_filename
    log_file = open(hard_log_file_name, "w")
    indent_level = 0

def begin_production(production, line_num, look_ahead):
    global log_file
    global indent_level
    indent_level += 1
    indent_str = indent_level * "  "
    
    log_file.writelines(indent_str)
    log_file.writelines("S PROD: " + indent_str + production)
    log_file.writelines("  line num: " + str(line_num))
    log_file.writelines("  lookahead: " + look_ahead + "\n")

def end_production(production, line_num, look_ahead):
    global log_file
    global indent_level
    indent_str = indent_level * "  "
    log_file.writelines(indent_str)
    log_file.writelines("E PROD: " + indent_str + production)
    log_file.writelines("  line num: " + str(line_num))
    log_file.writelines("  lookahead: " + look_ahead + "\n")
    indent_level -= 1

def general_log(message):
    global log_file
    global indent_level
    indent_str = ""
    for i in range(indent_level + 1):
        indent_str += "  "
    log_file.writelines(indent_str)
    log_file.writelines("LOG: " + message + "\n")

def error(message, token):
    """ Print message and terminate. """
    global log_file
    global indent_level

    log_file.writelines("ERROR: " + message + " Token : " + token)
    print ("in logger.error() about to call finish()")
    finish()
    raise RuntimeError("fatal error")

def finish():
    global log_file
    global indent_level
    log_file.close()

    print ("RUNNING logger.finish()")
    print (f"file name is  {hard_log_file_name}")
 
#---------------------------------------------------------------------      

