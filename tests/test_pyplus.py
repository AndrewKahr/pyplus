import modules.pyanalyzer as pya
import modules.portedfunctions as pf


def test_print_translation():
    args = ["Hello World"]
    translated_print = pf.print_translation(args)

    assert translated_print == "std::cout << Hello World << std::endl"


def test_sqrt_translation():
    args = ["1"]
    translated_sqrt = pf.sqrt_translation(args)

    assert translated_sqrt == "sqrt(1)"


def test_type_precedence_a():
    type_a = ["int"]
    type_b = ["float"]

    analyzer = pya.PyAnalyzer([], [])
    returned_type = analyzer.type_precedence(type_a, type_b)

    assert returned_type == type_b


def test_type_precedence_b():
    type_a = ["float"]
    type_b = ["float"]

    analyzer = pya.PyAnalyzer([], [])
    returned_type = analyzer.type_precedence(type_a, type_b)

    assert returned_type[0] == "float"


def test_type_precedence_c():
    type_a = ["str"]
    type_b = ["float"]

    analyzer = pya.PyAnalyzer([], [])
    returned_type = analyzer.type_precedence(type_a, type_b)

    assert returned_type == type_a


def test_type_precedence_d():
    type_a = ["int"]
    type_b = ["bool"]

    analyzer = pya.PyAnalyzer([], [])
    returned_type = analyzer.type_precedence(type_a, type_b)

    assert returned_type == type_a
