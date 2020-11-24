from modules import cppfile as cfile


class PyTranslator():

    # Index of the main file in the output list
    main_index = 0

    def __init__(self, script, output_path):
        self.script = script

        self.output_path = output_path

        # Tracks if we are currently parsing a line within a doc comment
        self.in_doc_comment = False

        self.output_files = [cfile.CPPFile("main")]

        self.output_files[self.main_index].functions.append(
                                    [("int main(int argc, char **argv)", 0)])
        self.write_to_function(self.main_index, 0, ("{", 0))

        # Flags for inclusions
        self.iostream_included = False
        self.vector_included = False

    def write_cpp_files(self):
        for file in self.output_files:
            f = open(self.output_path + file.filename + ".cpp", "w")

            # TODO: Error checking
            for line in file.includes:
                f.write("\t" * line[1] + line[0] + "\n")

            # Add space between includes and functions
            f.write("\n")

            for function in file.functions:
                for line in function:
                    f.write("\t" * line[1] + line[0] + "\n")
            f.close()


    def write_to_function(self, file_index, function_index, line):
        self.output_files[file_index].functions[function_index].append(line)

    def write_to_include(self, file_index, function_index, line):
        self.output_files[file_index].includes.append(line)

    def function_parser(self):
        pass

    def for_parser(self):
        pass

    def print_parser(self, file_index, function_index, line, indent):
        """

        :param function_index:
        :param file_index:
        :param line: Line containing a print statement
        :param indent: How much to indent a line by
        :return: None
        """
        arg_start_index = (line.find("(") + 1)
        arg_end_index = line.rfind(")")
        line_tuple = ("std::cout << " + line[arg_start_index:arg_end_index]
                      + " << std::endl;", indent)
        self.write_to_function(file_index, function_index, line_tuple)
        if not self.iostream_included:
            self.write_to_include(file_index, function_index,
                                  ("#include <iostream>", 0))
            self.iostream_included = True

    def interpret_line(self, file_index, function_index, line, indent):
        if len(line) == 0:
            self.write_to_function(file_index, function_index, ("", indent))
            return

        # check if comment
        if line[0] == '#':
            self.write_to_function(file_index, function_index,
                                   ("//" + line[2:], indent))
            return

        elif self.in_doc_comment:
            self.write_to_function(file_index, function_index, (line, indent))
            return

        # Detect type of call
        print_check = line.split('(')
        if len(print_check) > 0 and print_check[0] == "print":
            self.print_parser(file_index, function_index, line, indent)
            return

        else:
            self.write_to_function(file_index, function_index,
                                   ("//TODO: Refactor for C++", indent))
            self.write_to_function(file_index, function_index,
                                   ("//" + line, indent))

    def run(self):
        """
        Reads the script line by line. At the end of the specified script,
        it will return.
        Each line will have leading and trailing whitespaces stripped.
        If the line begins with a comment, skip to the next line, otherwise
        pass the line to interpret_line
        :return:
        """

        line = ""
        while True:
            line = self.script.readline()
            if not line:
                break
            # cleanup whitespace
            line = line.strip()

            # Send to interpreter
            self.interpret_line(self.main_index, 0, line, 1)

        self.write_to_function(self.main_index, 0, ("}", 0))
        self.write_cpp_files()
