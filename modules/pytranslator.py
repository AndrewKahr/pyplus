from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
from modules import pyanalyzer
import ast


class PyTranslator():
    def __init__(self, script_path, output_path):
        """
        Constructor of a python to C++ translator. This will automatically
        create a main.cpp and main function for code

        :param script_path: The string representation of the path to the file
                            to be converted
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
        main_function = cfun.CPPFunction("main", -1, -1, main_params)
        main_function.return_type[0] = "int"

        self.output_files[0].functions.append(main_function)

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
            try:
                f = open(self.output_path + file.filename + ".cpp", "w")
                f.write(file.get_formatted_file_text())
                f.close()
            except IOError:
                print("Error writing file: " + self.output_path
                      + file.filename + ".cpp")

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

    def ingest_comments(self):
        pass

    def apply_variable_types(self):
        """
        Goes through every variable in every function to apply types to them
        on declaration
        """
        for file in self.output_files:
            for cfunction in file.functions:
                for variable in cfunction.variables.values():
                    # Prepend line with variable type to apply type
                    cfunction.lines[variable.line_num].code_str \
                        = cvar.CPPVariable.types[variable.var_type[0]] \
                        + cfunction.lines[variable.line_num].code_str

    def run(self):
        """
        Entry point for parsing a python script. This will read the script
        line by line until it reaches the end, then it will call
        write_cpp_files to export the code into a cpp file
        """

        # Index for main file and main function
        file_index = 0
        function_index = 0

        # All the code will start with 1 tab indent
        indent = 1

        # Source: https://www.mattlayman.com/blog/2018/decipher-python-ast/
        with open(self.script_path, "r") as py_source:
            tree = ast.parse(py_source.read())
            py_source.seek(0)
            all_lines = py_source.read().splitlines()

        analyzer = pyanalyzer.PyAnalyzer(self.output_files, all_lines)
        analyzer.analyze_tree(tree, file_index, function_index, indent)

        self.apply_variable_types()
        self.ingest_comments()
        self.write_cpp_files()
