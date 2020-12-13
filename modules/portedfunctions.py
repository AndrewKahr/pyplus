def print_translation(args):
    """
    Parses calls to print to convert to the C++ equivalent

    :param list args: List of arguments to add to the print statement
    """
    return_str = "std::cout << "
    for arg in args[:-1]:
        return_str += arg + " + "
    return return_str + args[-1] + " << std::endl"


def sqrt_translation(args):

    return "sqrt(" + args[0] + ")"
