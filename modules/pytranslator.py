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

        self.output_files[self.main_index].functions.append([("int main(int argc, char **argv)", 0)])
        self.output_files[self.main_index].functions[self.main_index].append(("{", 0))

    def write_cpp_files(self):
        for file in self.output_files:
            f = open(self.output_path + file.filename + ".cpp", "w")

            # TODO: Error checking
            for line in file.includes:
                f.write("\t" * line[1] + line[0] + "\n")

            for function in file.functions:
                for line in function:
                    f.write("\t" * line[1] + line[0] + "\n")

        f.close()

    def function_parser(self):
        pass

    def for_parser(self):
        pass

    def print_parser(self):
        pass

    def interpret_line(self, line, indent):
        if len(line) == 0:
            self.output_files[self.main_index].functions[self.main_index].append(("", indent))
            return

        # check if comment
        if line[0] == '#':
            self.output_files[self.main_index].functions[self.main_index].append(("//" + line[2:], indent))

        elif self.in_doc_comment:
            self.output_files[self.main_index].functions[self.main_index].append((line, indent))

        else:
            self.output_files[self.main_index].functions[self.main_index].append(("//TODO: Refactor for C++", indent))
            self.output_files[self.main_index].functions[self.main_index].append(("//" + line, indent))

    def run(self):
        """
        Reads the script line by line. At the end of the specified script, it will return.
        Each line will have leading and trailing whitespaces stripped.
        If the line begins with a comment, skip to the next line, otherwise pass the line to interpret_line
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
            self.interpret_line(line, 1)

        self.output_files[self.main_index].functions[self.main_index].append(("}", 0))
        self.write_cpp_files()
