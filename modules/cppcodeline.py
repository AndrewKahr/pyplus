class CPPCodeLine():
    """
    Class to represent a line of code in C++
    """

    # Using a variable in case we want to use tabs instead of spaces
    tab_delimiter = "    "

    def __init__(self, start_line_num, end_line_num, end_char_index,
                 indent, code_str="", comment_str="", pre_comment_str=""):
        """
        Constructs a CPPLine object

        Parameters
        ----------
        start_line_num : int
            Line number the code starts on in the python file
        end_line_num : int
            Line number the code ends on in the python file
        end_char_index : int
             Index of the last character in this line in the python file
        indent : int
            Amount to indent the line by in the C++ file
        code_str : str
            The text for this line of C++ code
        comment_str : str
            The text for any inline comments, if applicable
        pre_comment_str : str
            The text for any comment that should precede this line of code, if
            applicable
        """
        # Line in the original python script
        self.start_line_num = start_line_num

        # Allows us to handle multiline code lines
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

        # String containing a comment that should precede a line of code
        # Used to help put comments about a line of code that couldn't be
        # converted
        self.pre_comment_str = pre_comment_str

    def get_formatted_code_line(self):
        """
        Generates a string representation of this C++ code line object

        Returns
        -------
        str
            A string with the converted C++ code
        """
        return_str = ""
        # Goes through various permutations of how this object could be
        # populated. We need different handlers to ensure indentation is done
        # correctly
        if self.pre_comment_str != "":
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + "//" + self.pre_comment_str + "\n"

        if self.code_str != "":
            # Standard code line
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + self.code_str
            if self.comment_str != "":
                # Inline comment as well
                return_str += CPPCodeLine.tab_delimiter \
                              + "//" + self.comment_str

        elif self.comment_str != "":
            # Only a comment present
            return_str += CPPCodeLine.tab_delimiter * self.indent \
                          + "//" + self.comment_str

        else:
            # Empty line
            return_str += CPPCodeLine.tab_delimiter * self.indent

        return return_str
