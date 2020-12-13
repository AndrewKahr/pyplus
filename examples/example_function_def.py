# Example script demonstration function declaration and usage

def add(val_a, val_b):
    """
    Adds a and b together and returns the result

    :param val_a: First value to add
    :param val_b: Second value to add
    :return: The sum of a and b
    """

    return val_a + val_b


def sub(val_a, val_b):
    """
    Subtracts b from a and returns the result

    :param val_a: First value to add
    :param val_b: Second value to add
    :return: The difference of a and b
    """

    return val_a - val_b


# Function calls supported for functions declared in the same file
x = add(1.1, 2.4)
print(x)

a = 3.2
b = 5
# Function calls also support variables as parameters
y = add(a, b)
print(y)

# Can also use function calls as parameters of function calls
z = add(sub(a, b), sub(b, a))
print(z)
