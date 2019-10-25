""" Module for handling programmer type descriptions. """

import logger

##class __Field_Description__(object):
##    def __init__(self, field_name, field_type):
##        """ Init a record field description e.g. f1, integer - internal use only """
##        self.field_name = field_name
##        self.field_type = field_type
##
##    def __str__(self):
##        return("  field : " + self.field_name + " type : " + self.field_type + "\n")
##
##class Field_List(object):
##    def __init__(self):
##        """ Initialize and empty record field list. """
##        self.__table__ = dict()
##
##    def add_field(self, field_name, field_type):
##        """ Add a field to the list e.g. "f1", "integer" """
##        if self.__table__.has_key(field_name):
##            raise RuntimeError, "Tried to add a dup field to a rec : " + field_name
##
##        self.__table__[field_name] = __Field_Description__(field_name, field_type)
##        
        
class Alias_Description(object):

    def __init__(self, base_type):
        """ Initialize with the base_type """
        self.base_type = base_type

    def __str__(self):
        tmp =  "  ALIAS:\n"
        tmp += "    base : " + self.base_type + "\n"  
        return(tmp)

class Record_Description(object):
    def __init__(self):
        """ Initialize an empty record definition.  Use add to add fields. """

        # The field list elements are (field_name, programmer_type) tuples
        # This is not a dict because we do not want to alter the
        # programmer defined order of the fields
        self.field_list = list()

    def __str__(self):
        tmp =  "  RECORD:\n"
        for (key, val) in self.field_list:
            tmp +=  "    " + key + "  " + val + "\n"
        return(tmp)

    def add_field(self, field_name, programmer_type):
        """ Add a field to this record description. """
        for (existing_field_name, existing_programmer_type) in self.field_list:
            if field_name == existing_field_name:
                logger.error("Tried to add dup field to a rec. ", field_name)
        # If we got this far the field_name was not a duplicate
        self.field_list.append((field_name, programmer_type))

    def get_field_info(self, field_name):
        """ return programmer_type and field_offset for field_name of a given (input) programmer_type"""
        field_offset = 0
        is_found = False


        for (existing_field_name, existing_field_type) in self.field_list:
            if field_name == existing_field_name:
                return(existing_field_type, field_offset)
            field_offset += type_table.get_type_storage(existing_field_type)

            

class Array_Description(object):
    
    def __init__(self, num_elements, base_type):
        """ Initialize with number of elements and the base_type """
        self.num_elements = num_elements
        self.base_type = base_type

    def __str__(self):
        tmp =  "  ARRAY:\n"
        tmp += "    base : " + self.base_type + "\n"  
        tmp += "    num_elements : " + str(self.num_elements) + "\n"  
        return(tmp)


class Builtin_Description(object):

    def __init__(self, base_type):
        """ Initialize with the base_type """
        self.base_type = base_type
        self.size = 1

    def __str__(self):
        tmp =  "  BUILTIN:\n"
        tmp += "    base : " + self.base_type + "\n"  
        return(tmp)

class Pointer_Description(object):
    def __init__(self, base_type):
        """ Initialize with the pointer's base_type. """
        self.base_type = base_type
        self.size = 1
        
    def __str__(self):
        tmp =  "  POINTER:\n"
        tmp += "    base : " + self.base_type + "\n"  
        return(tmp)


class Type_Table(object):
    
    def __init__(self):
        """ No arguments. """
        self.__table__ = dict()

    def add(self, programmer_type_name, description):
        """ Add value to the type_table, programmer_type_nameed by programmer_type_name.  Value must be a
        supported base. """
        if self.__table__.has_key(programmer_type_name):
            logger.error("Tried to add duplicate programmer_type_name : ", programmer_type_name)

        if isinstance(description, Alias_Description):
            self.__table__[programmer_type_name] = description
        elif isinstance(description, Record_Description):
            self.__table__[programmer_type_name] = description
        elif isinstance(description, Array_Description):
            self.__table__[programmer_type_name] = description
        elif isinstance(description, Builtin_Description):
            self.__table__[programmer_type_name] = description
        elif isinstance(description, Pointer_Description):
            self.__table__[programmer_type_name] = description
        else:
            raise RuntimeError, "Attempt to add bad value to type table. """

    def get_data(self, programmer_type_name):
        """ return an description object associated with this programmer_type_name type """
        while True:        
            description = self.__table__.get(programmer_type_name)
            if isinstance(description, Alias_Description):
                programmer_type_name = description.base_type
            else:
                break
            
        return(self.__table__.get(programmer_type_name))

    def get_type_storage(self, programmer_type_name):
        """ return reqd storage by adding up all of the type's components. """
        
        try:
            type_description = self.__table__[programmer_type_name]
        except:
            logger.error("Could not find programmer defined type ", programmer_type_name)

        storage_amount = 0

        if isinstance(type_description, Alias_Description):
            storage_amount = self.get_type_storage(type_description.base_type)
        elif isinstance(type_description, Record_Description):
            storage_amount = 0
            for (field_name, programmer_type) in type_description.field_list:
                storage_amount += self.get_type_storage(programmer_type)

        elif isinstance(type_description, Array_Description):
            storage_amount = self.get_type_storage(type_description.base_type) * type_description.num_elements
        
        elif isinstance(type_description, Builtin_Description):
            storage_amount = type_description.size
        elif isinstance(type_description, Pointer_Description):
            storage_amount = 1

        return(storage_amount)

   
    def dump(self):
        """ Display the type table. """
        for (name, value) in self.__table__.iteritems():
            print name
            print value

    def __str__(self):
        """ Return a text representation of the type table """
        tmp = ""
        for (name, value) in self.__table__.iteritems():
            tmp += str(name) + "\n" + str(value) + "\n"
        return(tmp)


def get_next_type():
    global type_num
    
    type_num += 1
    return("TYPE_NUM_" + str(type_num))

#
# Module initialization
#
# Please note we initialize type_table here in the module so the type
# descriptions can make reference to it.
#
type_num = 0
type_table = Type_Table()
type_table.add('INTEGER', Builtin_Description('INTEGER'))



if __name__ == "__main__":
    print "Initializing typetab module..."
    logger.init("log.tmp")
    r1 = Record_Description()
    r1.add_field("f1", "INTEGER")
    type_table.add("A_TYPE", Array_Description(17, "INTEGER"))
    r1.add_field("f2", "A_TYPE")
    r1.add_field("f3", "INTEGER")
    type_table.add("REC_TYPE", r1)
    print "Type table is : "
    print type_table

    type_name = "REC_TYPE"
    print "Getting record description for : " + type_name
    record_description = type_table.get_data(type_name)
    
    (programmer_type, field_offset) = record_description.get_field_info("f3")
    print "programmer type  (f3): " + programmer_type
    print "field offset : " + str(field_offset)

    (programmer_type, field_offset) = record_description.get_field_info("f2")
    print "programmer type  (f2): " + programmer_type
    print "field offset : " + str(field_offset)

    (programmer_type, field_offset) = record_description.get_field_info("f1")
    print "programmer type  (f1): " + programmer_type
    print "field offset : " + str(field_offset)

