from modules import pyparser


def convert(path):
    """

    :param path:
    :return:
    """

    # TODO: Error checking
    script = open(path, "r")
    pyparser.line_parser(script)
    script.close()


convert("../tests/tester.py")
