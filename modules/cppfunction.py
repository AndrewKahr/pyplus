class CPPFunction():

    def __init__(self, name, parameters={}):
        """
        Represents a C++ function
        :param name: The name of the function
        :param parameters: The parameters this function has passed in
        """
        self.name = name

        # Provides a lookup table for parameters, allowing for type updates
        # as file is parsed
        # Dictionary of {Variable Name : CPPVariable Object}
        self.parameters = parameters

        # Lines in a function stored as lists of tuples consisting of
        # (line, indent count) of type (string, int)
        self.lines = []

        # Provides a lookup table for variables declared in the scope,
        # allowing for type updates as the file is parsed
        # Dictionary of Variable Name : CPPVariable Object
        self.variables = {}

        self.return_type = "void"

        # List of strings consisting of the documentation for a function
        # where each item is a new line
        self.doc_string = []

        # A place to store the function signature during output phase
        self.signature = ""
