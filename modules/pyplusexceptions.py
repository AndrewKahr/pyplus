class PyPlusException(Exception):
    """
    General Exception for pyplus exceptions
    """
    pass


class TranslationNotSupported(PyPlusException):
    """
    Exception to indicate python code cannot be translated to C++
    """
    pass


class VariableNotFound(PyPlusException):
    """
    Exception to indicate variable was not found in the current context
    """
    pass
