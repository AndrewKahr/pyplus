from modules import pytranslator
import os


def convert(script_path, output_path):
    """

    :param script_path:
    :param output_path:
    :return:
    """

    # Reference for getting absolute path of relative path file
    # so relative paths work in jupyter notebooks
    # https://stackoverflow.com/questions/7165749/
    #         open-file-in-a-relative-location-in-python
    full_path = os.path.dirname(__file__)
    # TODO: Error checking
    script = open(os.path.join(full_path, script_path), "r")

    translator = pytranslator.PyTranslator(script, os.path.join(full_path,
                                                                output_path))
    translator.run()
    script.close()


# convert("../tests/tester.py", "../tests/output/")
