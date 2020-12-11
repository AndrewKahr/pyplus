def print_translation(args):
    """
    Parses calls to print to convert to the C++ equivalent

    :param function_index: Index of the function this line should write to
    :param file_index: Index of the file this line should write to
    :param line: String representation of a line of code
                 containing a print statement
    :param indent: How much to indent a line by
    """
    return_str = "std::cout << "
    for arg in args[:-1]:
        return_str += arg + " + "
    return return_str + args[-1] + " << std::endl"


def sqrt_translation(args):

    return "sqrt(" + args[0] + ", " + args[1] + ")"