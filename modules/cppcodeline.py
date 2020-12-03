class CPPCodeLine():

    def __init__(self, start_line_num, end_line_num, end_char_index,
                 indent, code_str="", comment_str=""):
        # Line in the original python script
        self.start_line_num = start_line_num

        # Allows us to track if function is multiline
        self.end_line_num = end_line_num

        # Tells us where to start searching for inline comments, if any
        self.end_char_index = end_char_index

        # How much to indent the line in the C++ file
        self.indent = indent

        # String containing the converted C++ code
        self.code_str = code_str

        # String containing any inline comments
        # Also applicable if it is a comment only line, the code_str field
        # will just be an empty string
        self.comment_str = comment_str

    def get_formatted_code_line(self):
        return "    "*self.indent + self.code_str + "    //" + self.comment_str
