class CPPFile():

    def __init__(self, filename):
        """

        :param filename:
        """

        # Lines of Code stored as tuples consisting of (line, indent count) of type (string, int)
        # Includes are just strings
        self.includes = []

        # Functions stored as lists of tuples consisting of (line, indent count) of type (string, int)
        self.functions = []

        self.filename = filename
