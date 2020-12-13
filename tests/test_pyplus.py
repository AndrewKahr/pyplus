import modules


def test_print_translation():
    args = ["Hello World"]
    translated_print = modules.print_translation(args)

    assert translated_print == "std::cout << Hello World << std::endl"


def test_sqrt_translation():
    args = ["1", "2"]
    translated_sqrt = modules.sqrt_translation(args)

    assert translated_sqrt == "sqrt(1, 2)"


if __name__ == "__main__":
    test_print_translation()
    test_sqrt_translation()
