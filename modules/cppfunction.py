from modules import cppvariable as cvar

class CPPFunction():

    def __init__(self, name, lineno, end_lineno, parameters={}):
        """
        Represents a C++ function

        :param str name: The name of the function
        :param int lineno: The line where the function is declared in the
                           python file
        :param int end_lineno: The line where the function ends in the python
                               file
        :param dict parameters: The parameters this function has passed in
        """
        self.name = name

        # We store these to help with performing the comment and blank line
        # pass on the script file to know where to put the lines
        # Note: doesn't apply for the main function which takes code from
        # anywhere in the file
        self.lineno = lineno
        self.end_lineno = end_lineno

        # Provides a lookup table for parameters, allowing for type updates
        # as file is parsed
        # Dictionary of {Variable Name : CPPVariable Object}
        self.parameters = parameters

        # Lines in a function stored as a dictionary of format
        # {LineNumber : CPPCodeLine} where line number is the line number
        # in the python script
        self.lines = {}

        # Provides a lookup table for variables declared in the scope,
        # allowing for type updates as the file is parsed
        # Dictionary of Variable Name : CPPVariable Object
        self.variables = {}

        # Using a list so type gets updated if more information is found about
        # a related variable
        self.return_type = ["void"]

        # String for the function documentation
        self.doc_string = ""

        # We cache the signature since it is requested twice during output
        self.signature = ""

    def get_signature(self):
        """
        Generates the string representation of this function's signature

        :return: String containing the function's signature
        """
        # Check if we've already cached the signature
        if self.signature == "":
            function_signature = cvar.CPPVariable.types[self.return_type[0]]
            function_signature += self.name + "("

            # Check if there are any parameters before attempting to add them
            if len(self.parameters.values()) > 0:
                for parameter in self.parameters.values():
                    # Prepend the param type in C++ style before the param name
                    function_signature += cvar.CPPVariable.types[parameter.var_type[0]]
                    function_signature += parameter.name + ", "
                # Remove the extra comma and space
                function_signature = function_signature[:-2]

            self.signature = function_signature + ")"

        return self.signature

    def get_formatted_function_text(self):
        """
        Generates a string with all of this function's code within it

        :return: String containing all of the function's C++ code
        """
        return_str = ""

        # First line is the function signature
        return_str += self.get_signature() + "\n{\n"

        # Go through all lines and get their formatted string version and
        # append to the string we will return
        for line in self.lines.values():
            return_str += line.get_formatted_code_line() + "\n"

        # Add a closing bracket for the end of the function
        return return_str + "}"
