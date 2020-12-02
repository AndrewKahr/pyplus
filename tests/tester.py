# Hello!
print("hello")

# Useful Comment Test
print("hello2")

x = 5.21234234435435345345345345
m = x
q = 1 < 3
v = 3 + x
t = (3 + 5) + v + ((3 + 2) + x) # (((3+5)+v)+((3+2)+x))
x = b = 3

if x < 6 and 3 > 5:
    if x == b:
        print("True")
    print("Both")
elif x > 8:
    print("Else")
else:
    print("None")


def print_test():
    """
    Test Doc String
    :return: none
    """
    print("Test")
    y = 3
    y = 8
    y = 3 + 9
    z = 3 - 9


def abc(a, y, z):
    print("3342")
    y = 6


class Tester():
    name = "test"

    def __init__(self, input_var):
        self.input_var = input_var
