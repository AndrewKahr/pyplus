#include <iostream>
#include <string>
#include <math.h>

void print_test();
int add(int a, int b);
void abc(auto a, auto y, auto z, int b, std::string c);

int main(int argc, char **argv)
{
    /*
    String
    */
    //TODO: Constant string not used
    /*"Hi"*/
    //TODO: Constant not used
    /*1*/
    //TODO: Value not assigned or used
    /*1 < 3*/
    std::cout << "hello" << std::endl;
    auto string_var = (std::to_string(1)+"2");
    std::cout << "hello2" << std::endl;
    bool boolean = true;
    bool boolean2 = false;
    int b = (int)(5.4);
    (int)(5.4);
    //TODO: Code not directly translatable, manual port required
    /*ls = [1,2,3]*/
    int x = 5;
    //TODO: Refactor for C++. Variable types cannot change or potential loss of precision occurred
    /*x=5.1*/
    int m = x;
    bool q = (1 < 3);
    int v = (3+x);
    double t = ((3+5)+((double)v / ((3+2)+x)));
    v = 8;
    x = v;
    t = (pow(3.2, 2));
    //TODO: Unable to translate chained assignment
    /*x = b = 3*/
    if (x)
    {
        /*
        abc
        */
        std::cout << "hi" << std::endl;
    }
    if ((!(x || m)))
    {
        std::cout << "hi" << std::endl;
    }
    if ((0 < 5) && (5 < 8))
    {
        std::cout << "in range" << std::endl;
    }
    if (((x < 4) && (m > 3)))
    {
        std::cout << "test" << std::endl;
    }
    if ((((x < 6) && (3 > 5) && (2 < 5)) || (3 > 5)))
    {
        if ((x == b))
        {
            std::cout << "True" << std::endl;
        }
        else
        {
            /*
            else:
            else:
            else:
            */
            std::cout << "not true" << std::endl;
        }
        std::cout << "Both" << std::endl;
    }
    else if ((x > 8))
    {
        std::cout << "Else" << std::endl;
    }
    else
    {
        std::cout << "None" << std::endl;
    }
    while (x)
    {
        std::cout << "hello" << std::endl;
        break;
        continue;
    }
    std::cout << 1 << std::endl;
    //TODO: Call to function not in scope
    /*tester = Tester(2)*/
    //TODO: Not a valid call
    /*tester.test()*/
    x = add(1, 2);
}

void print_test()
{
    /*
    Test Doc String
    :return: none
    */
    std::cout << "Test" << std::endl;
    int y = 3;
    y = 8;
    y = (3+9);
    int z = (3-9);
}

int add(int a, int b)
{
    return (a+b);
}

void abc(auto a, auto y, auto z, int b=3, std::string c="hi")
{
    std::cout << "3342" << std::endl;
    y = 6;
    return;
}

