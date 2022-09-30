#!/usr/bin/python
""" The pascal-lite compiler. """

import sys
import logger
import tokens
import emitter
import symtab
import typetab
from symtab import Constant_Variable, Procedure_Variable
from strutils import is_an_identifier, str_is_numeric, str_is_hex_numeric


import inspect

#---------------------------------------------------------------------
def usage():
   """ Print the Usage message.  """
   print(f"USAGE: {sys.argv[0]} infile outfile logfile")
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def begin_production(production):
    """ Log the start of a new production. """
    logger.begin_production(
        production.upper(),
        tokenizer.get_line_num(),
        tokenizer.get_look_ahead())
#---------------------------------------------------------------------
    

#---------------------------------------------------------------------
def end_production(production):
    """ Log the start of a new production. """
    logger.end_production(
        production.upper(),
        tokenizer.get_line_num(),
        tokenizer.get_look_ahead())
#---------------------------------------------------------------------
    


#---------------------------------------------------------------------
def get_function_name():
    """ Return the name of the current function! """
    return("FUNC")
    return(inspect.stack()[1][3])
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def get_next_label():
    """ Return a new assembly language label """
    global label_num
    
    s = "L" + str(label_num)
    label_num += 1
    return(s)
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def do_production_include():
    """ process an include directive"""
    begin_production (get_function_name())

    tokenizer.get_token() # get rid of the include
    file_name = tokenizer.get_token()

    if list(file_name)[0] != '"':
        logger.error("Expected quote after INCLUDE", file_name)

    file_name = file_name.lstrip('"').rstrip('"')
    tokenizer.IncludeFile(file_name)
    
    end_production (get_function_name())
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def do_production_if(return_label, external_break_label, external_continue_label):
    """ process an if statement"""
    begin_production (get_function_name())

    tokenizer.get_token() # Throw away the IF
    done_label = get_next_label()

    do_production_expression()

    after_then_label = get_next_label()
    emitter.Emit("JMPF " + after_then_label, tokenizer.get_line_num())

    throw_away = tokenizer.get_token() # Throw away the THEN
    if throw_away != "THEN":
        logger.error("Expected THEN ", throw_away)

    do_production_statement(return_label, external_break_label,external_continue_label)

    look_ahead = tokenizer.get_look_ahead()
    if ((look_ahead != "ELSE") and (look_ahead != "ELSIF")):
        emitter.EmitLabel(after_then_label, tokenizer.get_line_num())
    elif look_ahead == "ELSE":
        tokenizer.get_token()
        emitter.Emit("BRA " + done_label, tokenizer.get_line_num())
        emitter.EmitLabel(after_then_label, tokenizer.get_line_num())
        do_production_statement(return_label, external_break_label, external_continue_label)
    else:   # must be "ELSIF"
        while tokenizer.get_look_ahead() == "ELSIF":
            tokenizer.get_token() # throwaway the ELSIF
            emitter.Emit("BRA " + done_label, tokenizer.get_line_num())

            emitter.EmitLabel(after_then_label, tokenizer.get_line_num())

            do_production_expression()

            after_then_label = get_next_label()
            emitter.Emit("JMPF " + after_then_label, tokenizer.get_line_num())

            throw_away = tokenizer.get_token() # Throw away the THEN
            if throw_away != "THEN":
                logger.error("Expected THEN ", throw_away)

            do_production_statement(return_label, external_break_label,external_continue_label)

        if look_ahead == "ELSE":
            tokenizer.get_token() # throw away the ELSE
            emitter.Emit("BRA " + done_label)
            emitter.EmitLabel(after_then_label, tokenizer.get_line_num())
            do_production_statement(return_label, external_break_label,external_continue_label)
        else:
            emitter.EmitLabel(after_then_label, tokenizer.get_line_num())
            
    emitter.EmitLabel(done_label, tokenizer.get_line_num())

    end_production (get_function_name())
            
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def do_production_factor():
    """ process a factor"""
    begin_production (get_function_name())

    look_ahead = tokenizer.get_look_ahead()
    if look_ahead == "ADR":
        tokenizer.get_token() #  Throwaway the ADR
        
        throw_away = tokenizer.get_token()
        if throw_away != "(":
            logger.error("Expected '(' after ADR function", throw_away)

        do_production_variable_access()
        logger.general_log("About to look for an ) after var acc in ADR")

        throw_away = tokenizer.get_token()
        if throw_away != ")":
            logger.error("Expected ')' after ADR function", throw_away)


    elif ((look_ahead == "SLL") or (look_ahead == "SRL")):
        instruction = tokenizer.get_token()

        throw_away = tokenizer.get_token()
        if throw_away != "(":
            logger.error("Expected '(' after shift function", throw_away)

        do_production_expression()
        
        throw_away = tokenizer.get_token()
        if throw_away != ")":
            logger.error("Expected ')' after ADR function", throw_away)

        emitter.Emit(instruction, tokenizer.get_line_num())


        
    # Check for constants.            
    elif is_an_identifier(look_ahead):
        # First check for constants which can only be global
        variable_classification = global_symbol_table.get_data(look_ahead)
        logger.general_log("Checking to see if id : " + look_ahead + " is a const or func.")
        if isinstance(variable_classification, symtab.Constant_Variable):
            logger.general_log("  Found a const")
            constant_name = tokenizer.get_token()
            emitter.Emit(str(variable_classification.value), tokenizer.get_line_num())

        elif isinstance(variable_classification, symtab.Function_Variable):
            logger.general_log("Found a function")
            num_formal_params = variable_classification.num_params
            do_production_function_call()
        else:
            logger.general_log("  NOT a const")
            do_production_variable_access()
            emitter.Emit("FETCH", tokenizer.get_line_num())

    # TODO Still have to check for function calls
                          
                               
                               
    elif str_is_numeric(look_ahead):
        token = tokenizer.get_token()
        emitter.Emit(token, tokenizer.get_line_num())


    elif str_is_hex_numeric(look_ahead):
        token = tokenizer.get_token()
        token = "0x" + token.lstrip("$")
        emitter.Emit(token, tokenizer.get_line_num())

    elif look_ahead == "(":
        tokenizer.get_token()
        do_production_expression()
        token = tokenizer.get_token()
        if token != ")":
            logger.error("Expected ')'", token)

    elif list(look_ahead)[0] == '"':
        token = tokenizer.get_token()

        l2 = get_next_label()
        emitter.Emit("BRA " + l2, tokenizer.get_line_num())
        
        string_constant = token
        string_label = get_next_label()
        emitter.EmitLabel(string_label, tokenizer.get_line_num())
        emitter.Emit("DW", tokenizer.get_line_num())
        for i in range(1, len(token) - 1):
            emitter.Emit(str(ord(list(token)[i])), tokenizer.get_line_num())
        emitter.Emit("0", tokenizer.get_line_num())
        emitter.Emit("ENDDW", tokenizer.get_line_num())

        emitter.EmitLabel(l2, tokenizer.get_line_num())

        emitter.Emit(string_label, tokenizer.get_line_num())
        
    else:
        logger.error("Expected a FACTOR", look_ahead)


    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_term():
    """ process a term"""
    begin_production (get_function_name())

    do_production_factor()

    look_ahead = tokenizer.get_look_ahead()
    while ((look_ahead == "*") or
           (look_ahead == "/") or
           (look_ahead == "MOD") or
           (look_ahead == "AND") or
           (look_ahead == "OR") or
           (look_ahead == "XOR") or
           (look_ahead == "=") or
           (look_ahead == "<>") or
           (look_ahead == "<") or
           (look_ahead == "<=") or
           (look_ahead == ">") or
           (look_ahead == ">=")):

        token = tokenizer.get_token()

        do_production_factor()

        # Both values are on stack now

        if token == "<":
            # emitter.Emit("JSR __SIGNED_LESS TO_R DROP DROP FROM_R", tokenizer.get_line_num())
            emitter.Emit("S_LESS", tokenizer.get_line_num())
        elif token == "=":
            emitter.Emit("==", tokenizer.get_line_num())
        elif token == ">":
            emitter.Emit("SWAP S_LESS", tokenizer.get_line_num())
        elif token == ">=":
            l2 = get_next_label()
            l1 = get_next_label()
            # emitter.Emit("JSR __SIGNED_LESS TO_R DROP DROP FROM_R", tokenizer.get_line_num())
            emitter.Emit("S_LESS", tokenizer.get_line_num())
            emitter.Emit("JMPF " + l2, tokenizer.get_line_num())
            emitter.Emit("0 BRA " + l1, tokenizer.get_line_num())
            emitter.EmitLabel(l2, tokenizer.get_line_num())
            emitter.Emit("1", tokenizer.get_line_num())
            emitter.EmitLabel(l1, tokenizer.get_line_num())
        elif token == "<=":
            l2 = get_next_label()
            l1 = get_next_label()
            emitter.Emit("SWAP", tokenizer.get_line_num())
            # emitter.Emit("JSR __SIGNED_LESS TO_R DROP DROP FROM_R", tokenizer.get_line_num())
            emitter.Emit("S_LESS", tokenizer.get_line_num())
            emitter.Emit("JMPF " + l2, tokenizer.get_line_num())
            emitter.Emit("0 BRA " + l1, tokenizer.get_line_num())
            emitter.EmitLabel(l2, tokenizer.get_line_num())
            emitter.Emit("1", tokenizer.get_line_num())
            emitter.EmitLabel(l1, tokenizer.get_line_num())
        elif token == "<>":
            l2 = get_next_label()
            l1 = get_next_label()
            emitter.Emit("== ", tokenizer.get_line_num())
            emitter.Emit("JMPF " + l2, tokenizer.get_line_num())
            emitter.Emit("0 BRA " + l1, tokenizer.get_line_num())
            emitter.EmitLabel(l2, tokenizer.get_line_num())
            emitter.Emit("1", tokenizer.get_line_num())
            emitter.EmitLabel(l1, tokenizer.get_line_num())
        elif token == "/":
            emitter.Emit("JSR __SIGNED_DIV TO_R DROP DROP FROM_R", tokenizer.get_line_num())
        elif token == "MOD":
            emitter.Emit("JSR __SIGNED_MOD TO_R DROP DROP FROM_R", tokenizer.get_line_num())
        else:
            emitter.Emit(token, tokenizer.get_line_num())


        look_ahead = tokenizer.get_look_ahead()


    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_expression():
    """ process an expression"""
    begin_production (get_function_name())
    do_negative = False

    look_ahead = tokenizer.get_look_ahead()
    if (look_ahead == "+") or (look_ahead == "-"):
        if look_ahead == "-":
            emitter.Emit("0", tokenizer.get_line_num())
            do_negative = True
        tokenizer.get_token()

    do_production_term()

    if do_negative:
        emitter.Emit("-", tokenizer.get_line_num())

    look_ahead = tokenizer.get_look_ahead()
    while ((look_ahead == "+") or (look_ahead == "-")):
        throw_away = tokenizer.get_token()

        do_production_term()
        
        emitter.Emit(throw_away, tokenizer.get_line_num())

        look_ahead = tokenizer.get_look_ahead()

    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_record_section(record_definition):
    """ Process record_section production.  Next token should be a field name """
    begin_production (get_function_name())

    field_name = tokenizer.get_token()
    
    throw_away = tokenizer.get_token()
    if throw_away != ":":
        logger.error("Expected : in record section", throw_away)

    type_name = do_production_type()
    s = "*** field : " + field_name + " has type : " + type_name

    record_definition.add_field(field_name, type_name)

    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_field_list():
    """ Process field_list production.  Next token should be a field name
    return typetab.RecordBase """
    begin_production (get_function_name())

    record_definition = typetab.Record_Description()
    do_production_record_section(record_definition)
    while tokenizer.get_look_ahead() == ";":
        throw_away = tokenizer.get_token()
        do_production_record_section(record_definition)

    end_production (get_function_name())
    return(record_definition)
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_type_def():
    """ Process type def.  Next token should be a type name """
    begin_production (get_function_name())

    type_name = tokenizer.get_token()
    if not is_an_identifier(type_name):
        logger.error("Expected and ID (as type name)", type_name)
    
    logger.general_log("about to define a type whose programmer defined name will be : " + type_name)

    throw_away = tokenizer.get_token()
    if throw_away != "=":
        logger.error("Expected =", throw_away)

    auto_type_name = do_production_type()
    logger.general_log("created prog type : " + type_name + " as auto name : " + auto_type_name)
                            
    typetab.type_table.add(type_name, typetab.Alias_Description(auto_type_name))

    end_production (get_function_name())

#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_type_definition_part():
    """ Process type definition part production.
    "TYPE" is assumed to be the next token. """

    begin_production (get_function_name())

    # Get rid of the word TYPE
    throw_away = tokenizer.get_token()
    logger.general_log("DEBUG - this token should be TYPE : " + throw_away)
    
    do_production_type_def()
    look_ahead = tokenizer.get_look_ahead()
    while look_ahead == ",":
        tokenizer.get_token()
        do_production_type_def()
        look_ahead = tokenizer.get_look_ahead()

    token = tokenizer.get_token()
    if token != ";":
        logger.error("Expected ';'", token)


    end_production (get_function_name())

#---------------------------------------------------------------------



#---------------------------------------------------------------------
def do_production_type():
    """ Process type production.  Next token should be -
    ARRAY, RECORD, ^, NAME (pre - existing) 
    return type_name
    Dynamically parses the type definition and returns the name"""
    begin_production (get_function_name())

    throw_away = tokenizer.get_token()
    if throw_away == "ARRAY":
        type_name = typetab.get_next_type()
        logger.general_log("About to process and array; name will be :" + type_name)

        throw_away = tokenizer.get_token()
        if throw_away != "[":
            logger.error("Expected [ after ARRAY", throw_away)

        num_str = tokenizer.get_token()

        if str_is_numeric(num_str):
            num_elements = int(num_str)
        elif str_is_hex_numeric(num_str):
            num_elements = int(num_str.lstrip("$"), 16)
        else:
            logger.error("Expected dec or hex NUMBER - got ", "junk in type def")
            # logger.error("Expected dec or hex NUMBER - got ", token)

        throw_away = tokenizer.get_token()
        if throw_away != "]":
            logger.error("Expected ] in ARRAY declaration", throw_away)

        throw_away = tokenizer.get_token()
        if throw_away != "OF":
            logger.error("Expected 'OF' in ARRAY declaration", throw_away)

        element_type = do_production_type()

        typetab.type_table.add(type_name, typetab.Array_Description(num_elements, element_type))

        s = "DEBUG : " + type_name + " is an ARRAY of : " + str(num_elements) + " of " + element_type
        logger.general_log(s)

    elif throw_away == "RECORD":
        type_name = typetab.get_next_type()
        logger.general_log("About to process a rec; name will be :" + type_name)
        record_definition = do_production_field_list();
        throw_away = tokenizer.get_token()
        if throw_away != "END":
            logger.error("Expected END after record def", throw_away)

        typetab.type_table.add(type_name, record_definition)

    elif throw_away == "^":
        type_name = typetab.get_next_type()
        logger.general_log("About to process a pointer name will be :" + type_name)
        sub_type_name = do_production_type()
        logger.general_log("  It is a pointer to :" + sub_type_name)
        typetab.type_table.add(type_name, typetab.Pointer_Description(sub_type_name))

    elif is_an_identifier(throw_away):
        type_name = throw_away
    else:
        logger.error("Expected an ID as type name", throw_away)


    end_production (get_function_name())
    return(type_name)
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_constant_definition():
    """ Process constant_definition production.  Next token should be an id """
    begin_production (get_function_name())

    name = tokenizer.get_token()
    if not is_an_identifier(name):
        logger.error("Expected an identifier.", name)

    token = tokenizer.get_token()
    if token != "=":
        logger.error("Expected =", token)

    token = tokenizer.get_token()
    logger.general_log("in const def- token is [" + token + "]")
    if token == "-":
        token = tokenizer.get_token()
        if str_is_numeric(token):
            token = "-" + token
            global_symbol_table.add(name, Constant_Variable(int(token)))
        else:
            logger.error("Expected NUMBER after MINUS - got ", token)
    elif str_is_numeric(token):
        global_symbol_table.add(name, Constant_Variable(int(token)))
    elif str_is_hex_numeric(token):
        global_symbol_table.add(name, Constant_Variable(int(token.lstrip("$"), 16)))
    else:
        # logger.error("Expected dec or hex NUMBER - got ", token)
        logger.error("Expected dec or hex NUMBER - got ", "unknown")



    end_production(get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_const():
    """ Process const production.  Next token should be CONST """
    begin_production (get_function_name())

    tokenizer.get_token() # Get rid of CONST, present upon entry

    do_production_constant_definition()

    while tokenizer.get_look_ahead() == ",":
        tokenizer.get_token() # Throwaway the ,
        do_production_constant_definition()

    token = tokenizer.get_token()
    if token != ";":
        logger.error("Expected ;", token)
        

    end_production(get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_guard():
    """ Process guard production.  Next token should be GUARD """
    begin_production (get_function_name())

    tokenizer.get_token() # Get rid of GUARD, present upon entry

    asm_str = ' DG '
    emitter.Emit(asm_str, tokenizer.get_line_num())

    token = tokenizer.get_token()
    if token != ";":
        logger.error("Expected ;", token)
        

    end_production(get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_variable():
    """ Process variable production.  Next token should be VAR upon entry
    return num_variables, local_var_offset """
    begin_production (get_function_name())

    tokenizer.get_token() # Get rid of VAR, present upon entry

    num_variables = 0 # Remember to return this
    local_variable_stack_offset = 0 # remember to return this
    

    is_first_pass = True
    while (is_first_pass or (tokenizer.get_look_ahead() == ",")):
        if is_first_pass:
            is_first_pass = False
        else:
            tokenizer.get_token() # Throwaway the ','

        variable_name = tokenizer.get_token()
        if not is_an_identifier(variable_name):
            logger.error("Expected an identifier.", variable_name)

        throw_away = tokenizer.get_token()
        if throw_away != ":":
            logger.error("Expected : after var name", throw_away)

        type_name = do_production_type()
        type_size = typetab.type_table.get_type_storage(type_name)

        num_variables += 1
        logger.general_log("Declared var : " + variable_name + " type is : " + type_name);

        if is_compiling_subroutine:
            local_symbol_table.add(
                variable_name,
                symtab.Local_Variable(type_name, local_variable_stack_offset))
        else:
            global_symbol_table.add(
                variable_name,
                symtab.Global_Variable(type_name))
            asm_str = variable_name + ':' + ' DS '  + str(type_size)

            emitter.Emit(asm_str, tokenizer.get_line_num())

        local_variable_stack_offset += type_size

    throw_away = tokenizer.get_token()
    if throw_away != ";":
        logger.error("Expected ; after var declaration(s)", throw_away)
        
    end_production(get_function_name())

    return(num_variables, local_variable_stack_offset)
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def do_production_asm():
    """ compile an ASM section """

    begin_production (get_function_name())

    tokenizer.get_token() # throwaway ASM
    
    while tokenizer.get_asm_look_ahead() != "END":
        raw_token = tokenizer.get_asm_token()
        emitter.Emit(raw_token, tokenizer.get_line_num())
        
    tokenizer.get_token() # throwaway END
    
    end_production (get_function_name())

#---------------------------------------------------------------------
def do_production_variable_access():
    """ compile a variable_access
    The next token should be a variable name. """
    # TODO fix bad local_symbol table hack
    global local_symbol_table
    
    begin_production (get_function_name())

    # TODO fix bad hack which results in local_symbol_table not being empty!
    if not is_compiling_subroutine:
        local_symbol_table = symtab.Symbol_Table()

    variable_name = tokenizer.get_token()
    if not is_an_identifier(variable_name):
        logger.error("Expected and ID as variable access", variable_name)

    # Look up the variable_name in the local and global symbol tables
    # The local table will only have an entry, if we are compiling a
    # subroutine.
    #
    # Reminder the symbol table has keys -
    #    i.e variable, procedure, constant names
    #    and variable_description's
    #    The descriptions are instantiations of classes defined in symtab
    #
    variable_description = None
    variable_description = local_symbol_table.get_data(variable_name)
    if variable_description:
        logger.general_log("DEBUG " + variable_name + " is a local variable.")
        logger.general_log(str(variable_description))
        # emitter.Emit("R_FETCH", tokenizer.get_line_num())
        # emitter.Emit(str(variable_description.stack_offset), tokenizer.get_line_num())
        # emitter.Emit("+", tokenizer.get_line_num())

        emitter.Emit("L_VAR", tokenizer.get_line_num())
        emitter.Emit(str(variable_description.stack_offset), tokenizer.get_line_num())
    else:
        variable_description = global_symbol_table.get_data(variable_name)
        if not variable_description:
            logger.error("unknown var : ", variable_name)

        emitter.Emit(variable_name, tokenizer.get_line_num())


    # Now we have a variable description; it is either global
    # or local and the base address code was generated above.

    # Get the programmer_type e.g. INTEGER
    # Given the programmer_type, get the type's descriptive information
    if ( (isinstance(variable_description, symtab.Global_Variable)) or
         (isinstance(variable_description, symtab.Local_Variable))):
        programmer_type = variable_description.programmer_type
        type_description = typetab.type_table.get_data(programmer_type)
    else:
        return
    
    # Still have to emit offset to base address
    # By looking at the type, we can figure out what tokens can
    # come next.  For example, if the type_description is an
    # instance of a typetab.Array_Description, the we know a "["
    # can follow.
    while True:
        look_ahead = tokenizer.get_look_ahead()

        if isinstance(type_description, typetab.Array_Description):
            if look_ahead == "[":
                logger.general_log("Beginning production ARRAY_ACCESS - base type is " +
                                   str(type_description.base_type))

                tokenizer.get_token() # get rid of the '['

                do_production_expression() # Arbitrary expr inside []

                token = tokenizer.get_token()
                if token != "]":
                    logger.error("Expected ]", token)

                logger.general_log("Ending productin ARRAY Access")   

                array_element_storage_size = typetab.type_table.get_type_storage(type_description.base_type)
                emitter.Emit(str(array_element_storage_size) + " * +", tokenizer.get_line_num())

                # Now that we have compiled the offset calculation we are at the
                # point in the token stream where we are (potentially) compiling
                # a whole new type and thus we need a new type_description.
                # The new type would be the base type of the array.
                type_description = typetab.type_table.get_data(type_description.base_type)
            else:
                break
            
        elif isinstance(type_description, typetab.Record_Description):
            if look_ahead == ".":
                logger.general_log("Beginning production RECORD_ACCESS")
                tokenizer.get_token() # get rid of the '.'

                field_name = tokenizer.get_token()
                logger.general_log("programmer_type is : " + programmer_type +
                                   "field_name (w/i type) : " + field_name)

                tmp = type_description.get_field_info(field_name)
                if not tmp:
                    logger.error("Unknown record field : ", field_name)

                (field_type, field_offset) = tmp
                logger.general_log("Got field info field : " + field_name + " type : " + field_type)

                emitter.Emit(str(field_offset) + " +", tokenizer.get_line_num())

                # Now we are effectively looking at a new type - the field's type
                type_description = typetab.type_table.get_data(field_type)
                logger.general_log("The next field type is " + field_type)
                programmmer_type = field_type
            else:
                break
                    

        elif isinstance(type_description, typetab.Pointer_Description):
            # begin_production("POINTER_ACCESS")
            if look_ahead == "^":
#                begin_production("POINTER_ACCESS")
                tokenizer.get_token()

                logger.general_log(" The type is : " + programmer_type)
                emitter.Emit("FETCH", tokenizer.get_line_num())
                logger.general_log("  switching to base type")
                type_description = typetab.type_table.get_data(type_description.base_type)
            else:
                break
            # end_production("POINTER_ACCESS")
        else:
            break
                
    
    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_assignment():
    """ compile an assignment statement
    The next token should be a variable name. """
    begin_production (get_function_name())

    do_production_variable_access()

    throw_away = tokenizer.get_token()
    if throw_away != ":=":
        logger.error("Expected ':=' in assigment statement", throw_away)

    # do_production_expression()
    # TODO
    do_production_expression()

    emitter.Emit("STORE2", tokenizer.get_line_num())

    end_production (get_function_name())
#---------------------------------------------------------------------

#---------------------------------------------------------------------
def do_production_procedure_call():
    """ Process procedure call production.  Next token should be a proc name """
    
    begin_production (get_function_name())

    procedure_name = tokenizer.get_token()

    throw_away = tokenizer.get_token()
    if throw_away != "(":
        logger.error("Expected '(' after procedure name", throw_away)

    num_actual_params = 0
    look_ahead = tokenizer.get_look_ahead()
    while look_ahead != ")":
        num_actual_params += 1
        do_production_expression()
        look_ahead = tokenizer.get_look_ahead()
        if look_ahead == ",":
            tokenizer.get_token()

    tokenizer.get_token() # get rid of ")"

    emitter.Emit("JSR " + procedure_name, tokenizer.get_line_num())

    variable_classification = global_symbol_table.get_data(procedure_name)
    if not variable_classification:
        logger.error("Unknown procedure name ", procedure_name)

    if variable_classification.num_params != num_actual_params:
        logger.error("Expected " + str(variable_classification.num_params) +
                     " params.  Saw : " + str(num_actual_params), procedure_name)

    for i in range(num_actual_params):
        emitter.Emit("DROP", tokenizer.get_line_num())


    end_production (get_function_name())

#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_function_call():
    """ Process function call production.  Next token should be a func name """
    
    begin_production ("do_production_function_call")

    function_name = tokenizer.get_token()

    throw_away = tokenizer.get_token()
    if throw_away != "(":
        logger.error("Expected '(' after procedure name", throw_away)

    num_actual_params = 0
    look_ahead = tokenizer.get_look_ahead()
    while look_ahead != ")":
        num_actual_params += 1
        do_production_expression()
        look_ahead = tokenizer.get_look_ahead()
        if look_ahead == ",":
            tokenizer.get_token()

    tokenizer.get_token() # get rid of ")"

    emitter.Emit("JSR " + function_name, tokenizer.get_line_num())


    variable_classification = global_symbol_table.get_data(function_name)
    if not variable_classification:
        logger.error("Unknown function name ", function_name)

    if variable_classification.num_params != num_actual_params:
        logger.error("Expected " + str(variable_classification.num_params) +
                     " params.  Saw : " + str(num_actual_params), function_name)

    # The return value is assumed to be on top of parameter stack
    # We need to save it until we drop all of the original parameters
    emitter.Emit("TO_R" , tokenizer.get_line_num())

    for i in range(num_actual_params):
        emitter.Emit("DROP", tokenizer.get_line_num())


    emitter.Emit("FROM_R", tokenizer.get_line_num())


    end_production (get_function_name())

#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_procedure_declaration():
    """ Process procedure (definition) production.  Next token should be PROCEDURE upon entry
    return num_variables, local_var_offset """

    global is_compiling_subroutine
    global local_symbol_table

    local_symbol_table = symtab.Symbol_Table()
    
    begin_production (get_function_name())

    is_compiling_subroutine = True

    local_variable_stack_offset = 0

    return_label = get_next_label()

    tokenizer.get_token() # Get rid of PROCEDURE, present upon entry

    procedure_name = tokenizer.get_token() 
    emitter.EmitLabel(procedure_name, tokenizer.get_line_num())

    throw_away = tokenizer.get_token()
    if throw_away != "(":
        logger.error("Expected ( after procedure name", throw_away)

    # Parse all parameters.
    # Please note parameters are passed left to right i.e.
    # the left most parameter is pushed first and is therefore
    # lowest on the stack.
    # This means to calculate the stack offsets, we need to
    # know how many parameters we have and the size of each before we
    # can add their stack offsets to the LocalSymbolTable.
    num_parameters = 0

    parameter_list = list()

    # On entry to this look, we expect either a param name or ")"
    while True:
        look_ahead = tokenizer.get_look_ahead()

        if look_ahead == ")":
            break

        # If we got this far, we expect the next token
        # to be a parameter name
        parameter_name = tokenizer.get_token()
        num_parameters += 1

        throw_away = tokenizer.get_token()
        if throw_away != ":":
            logger.error("Expected ( after procedure name", throw_away)

        type_name = do_production_type()
        logger.general_log("Param : " + parameter_name + " is type : " + type_name)
        type_size = typetab.type_table.get_type_storage(type_name)

        tmp = dict()
        tmp["parameter_name"] = parameter_name
        tmp["type_size"] = type_size
        tmp["type_name"] = type_name
        parameter_list.append(tmp)

        # The lookahead must be either
        # "," meaning more params follow, or
        # ")" meaning we have hit the end of the parameter list
        look_ahead = tokenizer.get_look_ahead()
        if look_ahead == ",":
            tokenizer.get_token() # Throwaway the ","
            continue

    # Add the procedure name to the symbol table.        
    global_symbol_table.add(procedure_name, symtab.Procedure_Variable(num_parameters))

    # Add all of the parameters to the symbol table
    parameter_list.reverse()
    previous_offset = 0
    for entry in parameter_list:
        stack_offset = previous_offset - entry["type_size"]
        previous_offset = stack_offset
        local_symbol_table.add(
            entry["parameter_name"],
            symtab.Local_Variable(entry["type_name"], stack_offset))
    # All of the parameters have been added to the local symbol table

    # If we got this far, the look ahead should be the ")"
    # at the end of the parameter list.
    throw_away = tokenizer.get_token()
    if throw_away != ")":
        logger.error("Expected ')'", throw_away)

    throw_away = tokenizer.get_token()
    if throw_away != ";":
        logger.error("Expected ';'", throw_away)

    if tokenizer.get_look_ahead() == "VAR":
        (num_variables, local_variable_stack_offset) = do_production_variable()

    # Emit the procedure entry code
    # Emit a 0 so all parameters are pushed onto the pstack
    emitter.Emit("0", tokenizer.get_line_num())
    emitter.Emit("SP_FETCH", tokenizer.get_line_num())
    emitter.Emit("TO_R", tokenizer.get_line_num())
    emitter.Emit("SP_FETCH", tokenizer.get_line_num())
    emitter.Emit(str(local_variable_stack_offset), tokenizer.get_line_num())
    emitter.Emit("+", tokenizer.get_line_num())
    emitter.Emit("SP_STORE", tokenizer.get_line_num())

    do_production_statement(return_label, "", "")

    throw_away = tokenizer.get_token()
    if throw_away != ";":
        logger.error("Expected ';'", throw_away)

    is_compiling_subroutine = False
    emitter.EmitLabel(return_label, tokenizer.get_line_num())

    # Emit the procedure exit code
    emitter.Emit("FROM_R", tokenizer.get_line_num())
    emitter.Emit("SP_STORE", tokenizer.get_line_num())
    emitter.Emit("DROP", tokenizer.get_line_num())
    emitter.Emit("RET", tokenizer.get_line_num())

    # logger.general_log("The local symbol table is: ")
    # local_symbol_table.dump()
    
    end_production (get_function_name())
#---------------------------------------------------------------------




#---------------------------------------------------------------------
def do_production_function_declaration():
    """ Process procedure (definition) production.  Next token should be FUNCTION upon entry
    return num_variables, local_var_offset """

    global is_compiling_subroutine
    global local_symbol_table

    local_symbol_table = symtab.Symbol_Table()
    
    begin_production (get_function_name())

    is_compiling_subroutine = True

    num_variables = 0
    
    local_variable_stack_offset = 0

    return_label = get_next_label()

    tokenizer.get_token() # Get rid of FUNCTION, present upon entry

    function_name = tokenizer.get_token() 
    emitter.EmitLabel(function_name, tokenizer.get_line_num())

    throw_away = tokenizer.get_token()
    if throw_away != "(":
        logger.error("Expected ( after procedure name", throw_away)

    # Parse all parameters.
    # Please note parameters are passed left to right i.e.
    # the left most parameter is pushed first and is therefore
    # lowest on the stack.
    # This means to calculate the stack offsets, we need to
    # know how many parameters we have and the size of each before we
    # can add their stack offsets to the LocalSymbolTable.
    num_parameters = 0

    parameter_list = list()

    # On entry to this look, we expect either a param name or ")"
    while True:
        look_ahead = tokenizer.get_look_ahead()

        if look_ahead == ")":
            break

        # If we got this far, we expect the next token
        # to be a parameter name
        parameter_name = tokenizer.get_token()
        num_parameters += 1

        throw_away = tokenizer.get_token()
        if throw_away != ":":
            logger.error("Expected : after parameter name", throw_away)

        type_name = do_production_type()
        logger.general_log("Param : " + parameter_name + " is type : " + type_name)
        type_size = typetab.type_table.get_type_storage(type_name)

        tmp = dict()
        tmp["parameter_name"] = parameter_name
        tmp["type_size"] = type_size
        tmp["type_name"] = type_name
        parameter_list.append(tmp)

        # The lookahead must be either
        # "," meaning more params follow, or
        # ")" meaning we have hit the end of the parameter list
        look_ahead = tokenizer.get_look_ahead()
        if look_ahead == ",":
            tokenizer.get_token() # Throwaway the ","
            continue

    # Add the function name to the symbol table.        
    global_symbol_table.add(function_name, symtab.Function_Variable(num_parameters))

    # Add all of the parameters to the symbol table
    # Offset starts at -1 to acct for return val being treated like right most param
    parameter_list.reverse()
    previous_offset = -1
    for entry in parameter_list:
        stack_offset = previous_offset - entry["type_size"]
        previous_offset = stack_offset
        local_symbol_table.add(
            entry["parameter_name"],
            symtab.Local_Variable(entry["type_name"], stack_offset))
    # All of the parameters have been added to the local symbol table

    # If we got this far, the look ahead should be the ")"
    # at the end of the parameter list.
    throw_away = tokenizer.get_token()
    if throw_away != ")":
        logger.error("Expected ')'", throw_away)

    # Now we expect to see the type of the function
    throw_away = tokenizer.get_token()
    if throw_away != ":":
        logger.error("Expected ':'", throw_away)

    function_type = do_production_type()
    logger.general_log("declrd func is : " + function_name + " type is : " + function_type)


    throw_away = tokenizer.get_token()
    if throw_away != ";":
        logger.error("Expected ';'", throw_away)

    if tokenizer.get_look_ahead() == "VAR":
        (num_variables, local_variable_stack_offset) = do_production_variable()

    # Emit the function entry code
    # Push dummy param (used as space for return val)
    emitter.Emit("0x1111", tokenizer.get_line_num())
    # Push a val force all params into RAM
    emitter.Emit("0x9999", tokenizer.get_line_num())
    emitter.Emit("SP_FETCH", tokenizer.get_line_num())
    emitter.Emit("TO_R", tokenizer.get_line_num())
    emitter.Emit("SP_FETCH", tokenizer.get_line_num())
    emitter.Emit(str(local_variable_stack_offset + 1), tokenizer.get_line_num())
    emitter.Emit("+", tokenizer.get_line_num())
    emitter.Emit("SP_STORE", tokenizer.get_line_num())

    do_production_statement(return_label, "", "")

    throw_away = tokenizer.get_token()
    if throw_away != ";":
        logger.error("Expected ';'", throw_away)

    is_compiling_subroutine = False
    emitter.EmitLabel(return_label, tokenizer.get_line_num())

    # Emit the procedure exit code
    emitter.Emit("FROM_R", tokenizer.get_line_num())
    emitter.Emit("SP_STORE", tokenizer.get_line_num())
    emitter.Emit("DROP", tokenizer.get_line_num())
    emitter.Emit("RET", tokenizer.get_line_num())

    # logger.general_log("The local symbol table is: ")
    # local_symbol_table.dump()
    
    end_production (get_function_name())
#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_statement(return_label, external_break_label, external_continue_label):
    """ compile a statement """
    begin_production (get_function_name())

    look_ahead = tokenizer.get_look_ahead()

    if look_ahead == 'BEGIN':
        tokenizer.get_token()
        
        do_production_statement(return_label, external_break_label, external_continue_label)

        look_ahead = tokenizer.get_look_ahead()
        while look_ahead == ";":
            tokenizer.get_token()
            do_production_statement(return_label, external_break_label, external_continue_label)
            look_ahead = tokenizer.get_look_ahead()

        token = tokenizer.get_token()
        if token != "END":
            logger.error("Expected END", token)

    elif look_ahead == "ASM":
        do_production_asm()
    elif look_ahead == "WHILE":
        tokenizer.get_token()
        loop_label = get_next_label()
        emitter.EmitLabel(loop_label, tokenizer.get_line_num())
        do_production_expression()
        label = get_next_label()
        emitter.Emit("JMPF " + label, tokenizer.get_line_num())

        token = tokenizer.get_token()
        if token != "DO":
            logger.error("Expected DO ", token)

        do_production_statement(return_label, label, loop_label)
        emitter.Emit("BRA " + loop_label, tokenizer.get_line_num())

        emitter.EmitLabel(label, tokenizer.get_line_num())
    elif look_ahead == "BREAK":
        tokenizer.get_token()
        if external_break_label == "":
            logger.error("Tried to break but there is no loop!", tokenizer.get_look_ahead())

        emitter.Emit("BRA " + external_break_label, tokenizer.get_line_num())
    
    elif look_ahead == "CONTINUE":
        tokenizer.get_token()
        if external_continue_label == "":
            logger.error("Tried to CONTINUE but there is no loop!", tokenizer.get_look_ahead())

        emitter.Emit("BRA " + external_continue_label, tokenizer.get_line_num())
    
    elif look_ahead == "RETURN":
        tokenizer.get_token()
        if return_label == "":
            logger.error("Tried to RETURN outside a subroutine!", tokenizer.get_look_ahead())

        emitter.Emit("BRA " + return_label, tokenizer.get_line_num())

    elif look_ahead == "RETVAL":
        tokenizer.get_token() # throwaway retval
        if return_label == "":
            logger.error("Tried to issue RETVAL outside of a funct", tokenizer.get_look_ahead())
        throw_away = tokenizer.get_token()
        if throw_away != "(":
            logger.error("Expected '(' after RETVAL", throw_away)

        do_production_expression()

        throw_away = tokenizer.get_token()
        if throw_away != ")":
            logger.error("Expected ')' after RETVAL expr", throw_away)

        # The return val should be stored just as if it were the rightmost
        # param in the function call
        emitter.Emit("R_FETCH 1 - STORE", tokenizer.get_line_num())
        emitter.Emit("BRA " + return_label, tokenizer.get_line_num())


    elif look_ahead == "IF":
        do_production_if(return_label, external_break_label, external_continue_label)

    # If we have gotten this far, we assume it is an assignment
    # (and the LHS of the assignment can be to a local or global var)
    # or a procedure call.
    else:
        if is_compiling_subroutine:
            local_symbol_data = local_symbol_table.get_data(look_ahead)
        else:
            local_symbol_data = None


        if local_symbol_data:
            # Any data gotten from the local symbol table can ONLY be a local
            # variable NOT a procedure call
            do_production_assignment()
        else:
            # It was not a local symbol, so EITHER it is an assignment to
            # a global var OR it is a procedure call (remember all proc's are
            # global
            
            global_symbol_data = global_symbol_table.get_data(look_ahead)
            if (not global_symbol_data):
                # local_symbol_table.dump()
                logger.error("Unknown var or proc : ", look_ahead)

            if isinstance(global_symbol_data, symtab.Global_Variable):
                do_production_assignment()
            elif isinstance(global_symbol_data, symtab.Procedure_Variable):
                do_production_procedure_call()
            else:
                logger.error("Tried to call a non procedure!", look_ahead)
    

    end_production(get_function_name())

#---------------------------------------------------------------------


#---------------------------------------------------------------------
def do_production_declaration():
    """ compile a "block".  Next token must be the beginning of a block """
    begin_production (get_function_name())

    look_ahead = tokenizer.get_look_ahead()
    if look_ahead == "CONST":
        do_production_const()
    if look_ahead == "GUARD":
        do_production_guard()
    elif look_ahead == "VAR":
        do_production_variable()
    elif look_ahead == "PROCEDURE":
        do_production_procedure_declaration()
    elif look_ahead == "FUNCTION":
        do_production_function_declaration()
    elif look_ahead == "TYPE":
        do_production_type_definition_part()
    elif look_ahead == "INCLUDE":
        do_production_include()
    
    end_production(get_function_name())
#---------------------------------------------------------------------



#---------------------------------------------------------------------
def do_production_block():
    """ compile a "block".  Next token must be the beginning of a block """
    begin_production (get_function_name())

    while tokenizer.get_look_ahead() in ["CONST", "VAR", "PROCEDURE", "FUNCTION", "TYPE", "INCLUDE", "GUARD"]:
        do_production_declaration()

    emitter.EmitLabel("MAIN", tokenizer.LineNum())

    is_compiling_subroutine = False # This should have been cleared in proc decl
    do_production_statement("", "", "")
    
    end_production(get_function_name())
#---------------------------------------------------------------------



#---------------------------------------------------------------------
def do_production_program():
    """ Top level production for a program. """
    begin_production (get_function_name())

    do_production_block()

    token = tokenizer.get_token()
    if token != ".":
        logger.error("Expected [.]", token)

    end_production(get_function_name())
#---------------------------------------------------------------------


#
# Main Program
#

#
# Set up a global line num for production logging
# dummied up for now
# look_ahead = "dummy_lookahead"

label_num = 0
is_compiling_subroutine = False

if (len(sys.argv) != 4):
   print("Fatal Error! Expected 3 args!")
   usage()
   exit(1)

infile = sys.argv[1]
outfile = sys.argv[2]
logfile = sys.argv[3]

tokenizer = tokens.Tokenizer(infile)
# No including runtime here - switching to cpp
# tokenizer.IncludeFile('/usr/local/lib/runtime.pas')
emitter.EmitInit(outfile)

global_symbol_table = symtab.Symbol_Table()
logger.init(logfile)


do_production_program()

logger.general_log("Dumping type Table\n")
logger.general_log(str(typetab.type_table))
logger.general_log("Dumping symbol Table\n")
logger.general_log(str(global_symbol_table))

emitter.FinishEmitter()
logger.finish()

