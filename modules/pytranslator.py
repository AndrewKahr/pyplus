from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
import ast


class PyTranslator():
    # Index of the main file in the output list
    main_index = 0

    def __init__(self, script_path, output_path):
        """
        Constructor of a python to C++ translator. This will automatically
        create a main.cpp and main function for code
        :param script: The file handle of the python file we are converting
        :param output_path: The string representation of the path to the
                            directory where the final file should be written
        """
        self.script_path = script_path

        self.output_path = output_path

        # Tracks if we are currently parsing a line within a doc comment
        self.in_doc_comment = False

        # Configuring Default Main Function code
        self.output_files = [cfile.CPPFile("main")]
        main_params = {"argc": cvar.CPPVariable("argc", 0, "int"),
                       "argv": cvar.CPPVariable("argv", 0, "char **")}
        main_function = cfun.CPPFunction("main", main_params)
        main_function.return_type = "int"

        self.output_files[self.main_index].functions.append(main_function)
        self.write_to_function(self.main_index, self.main_index, ("{", 0))

    def create_function_signature(self, function):
        """
        Uses information in a CPPFunction instance to generate and return a
        function signature
        :param function: CPPFunction object to create a function signature from
        :return: The function signature as a string
        """
        # Get the return type of the function and convert it to C++ style
        parameter_string = cvar.CPPVariable.types[function.return_type]
        parameter_string += function.name + "("

        # Check if there are any parameters before attempting to add them
        if len(function.parameters.values()) > 0:
            for parameter in function.parameters.values():
                # Prepend the param type in C++ style before the param name
                parameter_string += cvar.CPPVariable.types[parameter.var_type]
                parameter_string += parameter.name + ", "
            # Remove the extra comma and space
            parameter_string = parameter_string[:-2]
        return parameter_string + ")"

    def write_cpp_files(self):
        """
        This goes through the process of converting the object representations
        of the code into usable strings and writes them to the appropriate
        output file
        """
        # Currently only one file, but this forms a basis to allow for multi-
        # file outputs from classes in C++
        for file in self.output_files:
            # TODO: Error checking
            f = open(self.output_path + file.filename + ".cpp", "w")

            # Writes all libraries to include in C++ format at the top of the
            # file
            for line in file.includes:
                f.write("#include <" + line + ">\n")

            # Add empty line between includes and functions
            f.write("\n")

            # Write function forward declarations to avoid function order
            # issues in C++
            for function in file.functions:
                function.signature = self.create_function_signature(function)
                f.write(function.signature + ";\n")

            f.write("\n")

            # Writing functions generated from the current file
            for function in file.functions:
                f.write(function.signature + "\n")
                for line in function.lines:
                    f.write("    " * line[1] + line[0] + "\n")
                f.write("\n")

            f.close()

    def write_to_function(self, file_index, function_index, line):
        """
        Helper method to add line tuples to the corresponding function in the
        corresponding file
        :param file_index: Index of the file in output_files
        :param function_index: Index of the function in
                               output_files[file_index].functions
        :param line: A tuple containing the string of text and the amount of
                     indentation
        """
        self.output_files[file_index].functions[function_index].lines \
            .append(line)

    def write_to_include(self, file_index, include_line):
        """
        Helper method to add include files to the corresponding file
        :param file_index: Index of the file in output_files
        :param include_line: String of text representing the file to include
        """
        self.output_files[file_index].includes.append(include_line)

    def function_parser(self, file_index, line, original_pyindent):
        """
        Parser method to determine information about a python function. Stores
        this information in a CPPFunction object and adds it to the
        corresponding function list. Then it will go line by line and add code
        to this function until it finds the indentation in the python script
        has indicated the end of the function before breaking
        :param file_index: Index of the file in output_files
        :param line: String of text with the python function signature
        :param original_pyindent: Amount of indentation of the original
                                  function used to detect the end of a function
        """
        function_index = len(self.output_files[file_index].functions)
        # Splits the function name from the def and parameters that follow
        # This call splits the parameters from the def function_name
        function_name = line.split("(")[0]
        # This splits the name from the def portion
        function_name = function_name.split("def ")[1]

        parameter_string = line.split(function_name)[1]
        parameter_list = list(parameter_string.split(","))

        parameter_dict = {}
        # Now we generate the dictionary of parameters for this function
        # We check to make sure there are actually parameters present,
        # otherwise we can skip this step
        if len(parameter_list) > 0 and parameter_list[0].strip() != "():":
            # Cleanup First and Last Parameter
            parameter_list[0] = parameter_list[0][parameter_list[0].find("(")
                                                  + 1:]
            parameter_list[-1] = parameter_list[-1][:parameter_list[-1]
                                                    .rfind(")")]

            for parameter in parameter_list:
                cvar_name = parameter.strip()
                # This handles any default values that may be used
                cvar_name = cvar_name.split("=")[0]
                parameter_dict[cvar_name] = cvar.CPPVariable(cvar_name, 0)

        self.output_files[file_index].functions. \
            append(cfun.CPPFunction(function_name, parameter_dict))

        self.write_to_function(self.main_index, function_index, ("{", 0))

        # Start looping until we hit the end of the file or end of the function
        last_pyindent = 0
        while True:
            line, pyindent = self.get_line()
            if line is None or pyindent <= original_pyindent:
                break

            # Send to interpreter
            self.interpret_line(file_index, function_index, line, 1,
                                pyindent, last_pyindent)
            last_pyindent = pyindent

        self.write_to_function(self.main_index, function_index, ("}", 0))

    def variable_parser(self, file_index, function_index, line):
        pass

    def for_parser(self):
        pass

    def if_parser(self):
        pass

    def print_parser(self, file_index, function_index, line, indent):
        """
        Parses calls to print to convert to the C++ equivalent
        :param function_index: Index of the function this line should write to
        :param file_index: Index of the file this line should write to
        :param line: String representation of a line of code
                     containing a print statement
        :param indent: How much to indent a line by
        """
        arg_start_index = (line.find("(") + 1)
        arg_end_index = line.rfind(")")
        line_tuple = ("std::cout << " + line[arg_start_index:arg_end_index]
                      + " << std::endl;", indent)
        self.write_to_function(file_index, function_index, line_tuple)
        if "iostream" not in self.output_files[file_index].includes:
            self.write_to_include(file_index, "iostream")

    def interpret_line(self, file_index, function_index, line, cindent,
                       pyindent, last_pyindent):
        """
        This is the main function used to parse code from the python script.
        It will determine what type of call is on the provided line, then pass
        it to the appropriate handler to further parse it and turn it into
        C++ code
        :param file_index: Index of the file this line should write to
        :param function_index: Index of the function this line should write to
        :param line: String representing a line of python code
        :param cindent: Amount the code should be indented on the output C++
                        code
        :param pyindent: Amount the code was indented on the current line of
                         python code
        :param last_pyindent: Amount the code was indented on the previous line
                              of python code
        """
        # Blank line handler
        if len(line) == 0:
            self.write_to_function(file_index, function_index, ("", cindent))
            return

        # Check if comment
        if line[0] == '#':
            # Convert to C++ style comment
            self.write_to_function(file_index, function_index,
                                   ("//" + line[2:], cindent))
            return
        # Handle Docstring comments
        elif self.in_doc_comment:
            self.write_to_function(file_index, function_index, (line, cindent))
            return

        # Detect various types of calls
        # Function detection
        function_check = line.split(' ')
        if len(function_check) > 0 and function_check[0] == "def":
            self.function_parser(file_index, line, pyindent)
            return

        # Print Detection
        print_check = line.split('(')
        if len(print_check) > 0 and print_check[0] == "print":
            self.print_parser(file_index, function_index, line, cindent)
            return

        # Didn't match any known types, so we copy it across as a C++ comment
        # with a TODO to warn the user it needs to be refactored
        else:
            self.write_to_function(file_index, function_index,
                                   ("//TODO: Refactor for C++", cindent))
            self.write_to_function(file_index, function_index,
                                   ("//" + line, cindent))

    def get_line(self):
        """
        Gets the next line from the python file we are parsing and determines
        how much it was indented by
        :return: The line of code with whitespaces stripped and the amount the
                 code was indented by
        """
        line = self.script.readline()
        if not line:
            return None, 0

        clean_line = line.strip()
        py_indent = (len(line) - len(line.lstrip())) // 4
        return clean_line, py_indent

    def run(self):
        """
        Entry point for parsing a python script. This will read the script
        line by line until it reaches the end, then it will call
        write_cpp_files to export the code into a cpp file
        """

        # Source: https://www.mattlayman.com/blog/2018/decipher-python-ast/
        with open(self.script_path, "r") as py_source:
            tree = ast.parse(py_source.read())


        last_pyindent = 0
        while True:
            line, pyindent = self.get_line()
            if line is None:
                break

            # Send to interpreter
            self.interpret_line(self.main_index, self.main_index, line, 1,
                                pyindent, last_pyindent)
            last_pyindent = pyindent

        self.write_to_function(self.main_index, self.main_index, ("}", 0))
        self.write_cpp_files()
