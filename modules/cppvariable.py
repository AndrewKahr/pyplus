class CPPVariable():

    # Using redundant mapping to allow for changes to mapped type
    types = {
             "int": "int ", "float": "double ", "str": "std::string ",
             "bool": "bool ", "None": "NULL", "char **": "char **",
             "void": "void ", "auto": "auto "
             }

    def __init__(self, name, line_num, var_type="auto", list_dims=0,
                 is_list=False, list_type=""):
        """
        Represents a C++ variable converted from python

        :param str name: Name of the variable
        :param int line_num: line number this variable was assigned on in
                             python
        :param str var_type: The type of the variable in python
        :param int list_dims: How many dimensions the list is, only applicable
                              if the variable is of a list type
        :param bool is_list: Flag to easily determine if this variable is a
                             list
        :param str list_type: The type of values held within the list
        """
        self.name = name

        self.line_num = line_num

        # We use a list here to get a mutable type so that a change to one
        # linked variable will reflect the change across all objects
        self.var_type = [var_type]

        self.is_list = is_list

        # To account for recursive lists made of lists
        self.list_dims = list_dims
        self.list_type = list_type
