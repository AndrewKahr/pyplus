class CPPFile():

    def __init__(self, filename):
        """
        Represents a file to be exported
        Holds a list of includes to be written at the top of the file and a
        list of functions to be written after the includes

        :param filename: name to be given to the file
        """

        # Lines of Code stored as tuples consisting of (line, indent count)
        # of type (string, int)
        # Includes are just strings
        self.includes = []

        # Stored as a list of CPPFunction objects
        self.functions = []

        self.filename = filename
