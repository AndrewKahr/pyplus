class CPPFile():

    def __init__(self, filename):
        """
        Represents a file to be exported
        Holds a list of includes to be written at the top of the file and a
        list of functions to be written after the includes

        :param filename: name to be given to the file
        """

        # Includes are just strings of name of include file
        self.includes = []

        # Stored as a list of CPPFunction objects
        self.functions = []

        self.filename = filename

    def add_include_file(self, file):
        """
        Adds the provided include file to the current cpp file if it doesn't
        already exist

        :param str file: Name of the include file to add
        """
        if file not in self.includes:
            self.includes.append(file)

    def get_formatted_file_text(self):
        """
        Generates the text representing the entire C++ file

        :return: A string holding all of the text of the C++ file
        """
        return_str = ""

        # We start with include files
        for file in self.includes:
            return_str += "#include <" + file + ">\n"

        # Now put in forward declarations
        # Skip main since it doesn't need a forward declaration
        for index in range(1, len(self.functions)):
            return_str += self.functions[index].get_signature() + ";\n"

        # Now we put in all of the functions for the file
        for function in self.functions:
            return_str += function.get_formatted_function_text() + "\n"

        return return_str
