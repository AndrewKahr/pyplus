from modules import pytranslator


def convert(script_path, output_path):
    """

    :param script_path:
    :param output_path:
    :return:
    """

    # TODO: Error checking
    script = open(script_path, "r")

    translator = pytranslator.PyTranslator(script, output_path)
    translator.run()
    script.close()


convert("../tests/tester.py", "../tests/output/")
