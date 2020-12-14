class CPPVariable():
    """
    This class represents a variable, holding information about it to be used
    while outputting to the C++ file
    """

    # Using redundant mapping to allow for changes to mapped type
    types = {
             "int": "int ", "float": "double ", "str": "std::string ",
             "bool": "bool ", "None": "NULL", "char **": "char **",
             "void": "void ", "auto": "auto ", "NoneType": "void "
             }

    # Python uses capital letters while C++ uses lowercase
    bool_map = {"True": "true", "False": "false"}

    def __init__(self, name, line_num, py_var_type):
        """
        Constructs a C++ variable object representation converted from python

        Parameters
        ----------
        name : str
            The name of the variable
        line_num : int
            The line number this variable was declared on in python
        py_var_type : list of str
            The type of the variable in python
        """
        self.name = name

        self.line_num = line_num

        # We use a list here to get a mutable type so that a change to one
        # linked variable will reflect the change across all objects
        self.py_var_type = py_var_type
