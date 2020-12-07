class CPPCodeLine():
    tab_delimiter = "    "

    def __init__(self, start_line_num, end_line_num, end_char_index,
                 indent, code_str="", comment_str="", pre_comment_str=""):
        """
        Represents a line of C++ code

        :param int start_line_num: Line the code starts on in the python file
        :param int end_line_num: Line the code ends on in the python file
        :param int end_char_index: Index of the last character in this line
                                   in the python file
        :param int indent: Amount to indent the line by in the C++ file
        :param str code_str: The text for this line of C++ code
        :param str comment_str: The text for any inline comment
        :param str pre_comment_str: The text for any comment that should
                                    precede this line of code
        """
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

        # String containing a comment that should preceed a line of code
        # Used to help put comments about a line of code that couldn't be
        # converted
        self.pre_comment_str = pre_comment_str

    def get_formatted_code_line(self):
        """
        Generates a string representation of this C++ code line object

        :return: A string with the C++ code
        """
        return_str = ""
        if self.pre_comment_str != "":
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + "//" + self.pre_comment_str + "\n"
        if self.code_str != "":
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + self.code_str
            if self.comment_str != "":
                return_str += CPPCodeLine.tab_delimiter \
                              + "//" + self.comment_str
        elif self.comment_str != "":
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + "//" + self.comment_str
        else:
            return_str += CPPCodeLine.tab_delimiter * self.indent

        return return_str
