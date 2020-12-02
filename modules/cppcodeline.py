class CPPCodeLine():

    def __init__(self, line_num, indent, line_type, code_str="", comment_str=""):
        # Line in the original python script
        self.line_num = line_num

        # How much to indent the line in the C++ file
        self.indent = indent

        # String containing the converted C++ code
        self.code_str = code_str

        # String containing any inline comments
        # Also applicable if it is a comment only line, the code_str field
        # will just be an empty string
        self.comment_str = comment_str

        # Holds a string describing what kind of line it is to help
        # converting from objects to text
        self.line_type = line_type

    def get_formatted_code_line(self):
        return "    "*self.indent + self.code_str + "    //" + self.comment_str
