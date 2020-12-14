def print_translation(args):
    """
    Parses calls to print to convert to the C++ equivalent

    Parameters
    ----------
    args : list of str
        List of arguments to add to the print statement

    Returns
    -------
    str
        The converted print statement
    """
    return_str = "std::cout << "

    for arg in args[:-1]:
        return_str += arg + " + "

    return return_str + args[-1] + " << std::endl"


def sqrt_translation(args):
    """
    Parses calls to sqrt to convert to the C++ equivalent

    Parameters
    ----------
    args : list of str
        List of arguments to add to the print statement

    Returns
    -------
    str
        The converted sqrt statement
    """
    return "sqrt(" + args[0] + ")"
