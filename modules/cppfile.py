class CPPFile():
    """
    Class to represent a C++ file that will be exported
    """

    def __init__(self, filename):
        """
        Constructs a CPPFile object

        Parameters
        ----------
        filename : str
            Name for the file
        """
        # Includes are just strings of name of include file
        self.includes = []

        # Stored as a dictionary of {Function Name: CPPFunction object}
        self.functions = {}

        self.filename = filename

    def add_include_file(self, file):
        """
        Adds the provided include file to the current cpp file if it doesn't
        already exist

        Parameters
        ----------
        file : str
            Name of the include file to add
        """
        if file not in self.includes:
            self.includes.append(file)

    def get_formatted_file_text(self):
        """
        Generates the text representing the entire C++ file

        Returns
        -------
        return_str : str
            The text of the converted C++ file
        """
        return_str = ""

        # We start with include files
        for file in self.includes:
            return_str += "#include <" + file + ">\n"

        return_str += "\n"

        # Now put in forward declarations
        # Skip main since it doesn't need a forward declaration
        for function_key in list(self.functions.keys())[1:]:
            return_str += self.functions[function_key].get_forward_declaration() + ";\n"

        return_str += "\n"

        # Now we put in all of the functions for the file
        for function in self.functions.values():
            return_str += function.get_formatted_function_text() + "\n\n"

        return return_str
