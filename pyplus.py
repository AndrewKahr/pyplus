import os
from modules import pytranslator


def convert(script_path, output_path):
    """
    The entry point of the translator. Call this function to translate a
    python script to C++

    Parameters
    ----------
    script_path : str
        The relative path to the script to convert
    output_path : str
        The relative path to the directory to output to
    """

    # Reference for getting absolute path of relative path file
    # so relative paths work in jupyter notebooks
    # https://stackoverflow.com/questions/7165749/
    #         open-file-in-a-relative-location-in-python
    full_path = os.path.dirname(__file__)
    translator = pytranslator.PyTranslator(os.path.join(full_path, script_path),
                                           os.path.join(full_path, output_path))
    translator.run()


if __name__ == "__main__":
    convert("examples/example_assignment.py", "output/")
