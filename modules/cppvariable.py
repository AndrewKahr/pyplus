class CPPVariable():

    # Using redundant mapping to allow for changes to mapped type
    types = {"int": "int ", "float": "double ", "None": "NULL",
             "char **": "char **", "void": "void ", "auto": "auto "}

    def __init__(self, name, line_index, var_type="auto", list_dims=0,
                 is_list=False, list_type=""):
        """
        Represents a C++ variable converted from python
        :param name: Name of the variable
        :param line_index: Index of the variable declaration in the lines list
                           from the owning function
        :param var_type: The type of the variable in python
        :param list_dims: How many dimensions the list is, only applicable if
                          the variable is of a list type
        :param is_list: Flag to easily determine if this variable is a list
        :param list_type: The type of values held within the list
        """
        self.name = name

        #
        # CPPFunction class
        self.line_index = line_index

        self.var_type = var_type

        self.is_list = is_list

        # To account for recursive lists made of lists
        self.list_dims = list_dims
        self.list_type = list_type
