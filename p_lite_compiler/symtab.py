""" The symbol table """

import logger

class Global_Variable(object):
    """ An object meant to hold global variable attributes. """

    def __init__(self, programmer_type):
        """ programmer_type e.g. INTEGER or programmer defined type """
        self.programmer_type = programmer_type

    def __str__(self):
        tmp = "  GLOBAL VAR\n"
        tmp += "  programmer_type : " + self.programmer_type
        return(tmp)

class Local_Variable(object):
    """ An object meant to hold local variable and parameter attributes. """

    def __init__(self, programmer_type, stack_offset):
        """ programmer_type e.g. INTEGER """
        self.programmer_type = programmer_type
        self.stack_offset = stack_offset

    def __str__(self):
        tmp = "  LOCAL VAR\n"
        tmp += "  programmer_type : " + self.programmer_type + "\n" + \
        "  stack_offset : " + str(self.stack_offset)
        return(tmp)


class Procedure_Variable(object):
    """ An object meant to hold procedure attributes. """

    def __init__(self, num_params):
        """ Size in words and programmer_type e.g. integer """
        self.num_params = num_params

    def __str__(self):
        tmp = "  PROCEDURE \n"
        tmp += "  num_params : " + str(self.num_params) + "\n" 
        return(tmp)


class Function_Variable(object):
    """ An object meant to hold function attributes. """

    def __init__(self, num_params):
        """ Size in words and programmer_type e.g. integer """
        self.num_params = num_params

    def __str__(self):
        tmp = "  FUNCTION \n"
        tmp += "  num_params : " + str(self.num_params) + "\n" 
        return(tmp)


class Constant_Variable(object):
    """ An object meant to hold constant attributes. """

    def __init__(self, value):
        """ Initialize value of the constant. """
        self.value = value

    def __str__(self):
        tmp = "  CONSTANT \n"
        tmp += "  value : " + str(self.value)
        return(tmp)


class Symbol_Table(object):
    """ Create a new empty symbol table. """
    def __init__(self):
        """ No arguments. """
        self.__table__ = dict()

    def add(self, name, variable_classification):
        """ Add variable_classification to symbol table, keyed by name.
        variable_classification should be an instance of a supported class. """
        if self.__table__.has_key(name):
            logger.error("Tried to add duplicate key : " , name)
        
        if isinstance(variable_classification, Global_Variable):
            self.__table__[name] = variable_classification
        elif isinstance(variable_classification, Local_Variable):
            self.__table__[name] = variable_classification
        elif isinstance(variable_classification, Procedure_Variable):
            self.__table__[name] = variable_classification
        elif isinstance(variable_classification, Constant_Variable):
            self.__table__[name] = variable_classification
        elif isinstance(variable_classification, Function_Variable):
            self.__table__[name] = variable_classification

        else:
            raise RuntimeError, "Attempt to add bad value to symbol table"

    def get_data(self, name):
        """ return a variable_classification associated with name. """
        return(self.__table__.get(name))

    def dump(self):
        """ Display the symbol table. """
        for (name, value) in self.__table__.iteritems():
            print name
            print value
        
    def __str__(self):
        """ Return text rep of the symbol table. """
        tmp = ""
        for (name, value) in self.__table__.iteritems():
            tmp += str(name) + "\n" + str(value) + "\n"
        return(tmp)        

#
# Scripted Main
#
if __name__ == "__main__":
    print "Running main."
    s = Symbol_Table()
    v1 = Procedure_Variable(17)
    v2 = Local_Variable("integer", -2)
    v3 = Constant_Variable(17)
    v4 = Global_Variable("prog_type_2")
    s.add("p1", v1)
    s.add("l2", v2)
    s.add("l3", v3)
    s.add("l4", v4)
    s.dump()



        
