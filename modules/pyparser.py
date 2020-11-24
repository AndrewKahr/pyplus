from modules import flagenums as fe
from modules import cppfile as cfile


class PyParser():

    # Index of the main file in the output list
    main_index = 0

    def __init__(self, script):
        self.script = script

        # Tracks the indentation of the current line
        self.indent = 1

        # Tracks if we are currently parsing a line within a doc comment
        self.in_doc_comment = False

        self.output_files = [cfile.CPPFile("main")]

        self.output_files[self.main_index].functions.append([("int main(int argc, char **argv) \n {", 0)])

    def function_parser(self, script):
        pass

    def for_parser(self, script):
        pass

    def interpret_line(self, line):
        pass

    def line_parser(self, script):
        """
        Reads the script line by line. At the end of the specified script, it will return.
        Each line will have leading and trailing whitespaces stripped.
        If the line begins with a comment, skip to the next line, otherwise pass the line to interpret_line
        :param script:
        :return:
        """

        line = ""
        while True:
            line = script.readline()
            if not line:
                break
            # cleanup whitespace
            line = line.strip()
            # check if comment
            if line[0] == '#':
                self.output_files[self.main_index].functions[self.main_index].append(("//" + line[1:], 1))

            elif self.in_doc_comment:
                self.output_files[self.main_index].functions[self.main_index].append((line[1:], 1))

            # send to interpreter
            self.interpret_line(line)
