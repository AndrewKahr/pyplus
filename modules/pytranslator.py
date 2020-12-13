import ast
from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
from modules import cppcodeline as cline
from modules import pyanalyzer


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
        main_params = {"argc": cvar.CPPVariable("argc", -1, ["int"]),
                       "argv": cvar.CPPVariable("argv", -1, ["char **"])}
        # We name the function 0 because that is an invalid name in python
        # Otherwise theres a chance theres a function named main already
        # At file output, this will be changed to main
        main_function = cfun.CPPFunction("0", -1, -1, main_params)
        main_function.return_type[0] = "int"

        self.output_files[0].functions["0"] = main_function

    def write_cpp_files(self):
        """
        This goes through the process of converting the object representations
        of the code into usable strings and writes them to the appropriate
        output file
        """
        # Currently only one file, but this forms a basis to allow for multi-
        # file outputs from classes in C++
        for file in self.output_files:
            try:
                f = open(self.output_path + file.filename + ".cpp", "w")
                f.write(file.get_formatted_file_text())
                f.close()
            except IOError:
                print("Error writing file: " + self.output_path
                      + file.filename + ".cpp")
        print("Output written to " + self.output_path)

    def ingest_comments(self, raw_lines):
        # First get a dictionary with every existing line of code. That way
        # we know whether to look for an inline comment or a full line comment
        for file in self.output_files:
            all_lines_dict = {}
            for cfunction in file.functions.values():
                # Source: https://stackoverflow.com/questions/38987/how-do-i
                # -merge-two-dictionaries-in-a-single-expression-in-python
                # -taking-union-o
                all_lines_dict = {**all_lines_dict, **cfunction.lines}

            # Going through all lines in the script we are parsing
            for index in range(len(raw_lines)):
                if (index+1) in all_lines_dict:
                    # Looking for inline comment
                    code_line = all_lines_dict[index+1]
                    comment = raw_lines[index][code_line.end_char_index:].lstrip()

                    # Verify there is a comment present
                    if len(comment) > 0 and comment[0] == "#":
                        # Trim off the comment symbol as it will be changed
                        # to the C++ style comment
                        all_lines_dict[index+1].comment_str = comment[1:].lstrip()

                else:
                    # Determine which function the line belongs to
                    for function in file.functions.values():
                        if function.lineno < index + 1 < function.end_lineno:
                            line = raw_lines[index]
                            comment = line.lstrip()
                            if len(comment) > 0 and comment[0] == "#":
                                comment = line.replace("#", "//", 1)
                                function.lines[index + 1] = cline.CPPCodeLine(index + 1,
                                                                              index + 1,
                                                                              len(line),
                                                                              0,
                                                                              comment)
                                break
                    else:
                        line = raw_lines[index]
                        comment = line.lstrip()
                        if len(comment) > 0 and comment[0] == "#":
                            # We add an extra indent on code not in a function
                            # since it will go into a function in C++
                            comment = cline.CPPCodeLine.tab_delimiter + line.replace("#", "//", 1)
                            file.functions["0"].lines[index + 1] = cline.CPPCodeLine(index + 1,
                                                                                     index + 1,
                                                                                     len(line),
                                                                                     0,
                                                                                     comment)
        # Sort function line dictionaries so output is in proper order
        for function in file.functions.values():
            sorted_lines = {}
            for line in sorted(function.lines.keys()):
                sorted_lines[line] = function.lines[line]
            function.lines = sorted_lines

    def determine_indent(self, line):
        tab_count = 0
        space_count = 0
        for char in line:
            if char == " ":
                space_count += 1
            elif char == "\t":
                space_count += 1
            else:
                return tab_count + space_count // 4

    def apply_variable_types(self):
        """
        Goes through every variable in every function to apply types to them
        on declaration
        """
        for file in self.output_files:
            for cfunction in file.functions.values():
                for variable in cfunction.variables.values():
                    # Need to include string library for strings in C++
                    if variable.py_var_type[0] == "str":
                        file.add_include_file("string")

                    # Prepend line with variable type to apply type
                    cfunction.lines[variable.line_num].code_str \
                        = cvar.CPPVariable.types[variable.py_var_type[0]] \
                        + cfunction.lines[variable.line_num].code_str

    def run(self):
        """
        Entry point for parsing a python script. This will read the script
        line by line until it reaches the end, then it will call
        write_cpp_files to export the code into a cpp file
        """

        # Index for main file and key for main function
        file_index = 0
        function_key = "0"

        # All the code will start with 1 tab indent
        indent = 1

        # Source: https://www.mattlayman.com/blog/2018/decipher-python-ast/
        with open(self.script_path, "r") as py_source:
            tree = ast.parse(py_source.read())
            py_source.seek(0)
            all_lines = py_source.read().splitlines()

        analyzer = pyanalyzer.PyAnalyzer(self.output_files, all_lines)
        analyzer.analyze(tree.body, file_index, function_key, indent)

        self.apply_variable_types()
        self.ingest_comments(all_lines)
        self.write_cpp_files()
