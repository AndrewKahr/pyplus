# PyPlus: A Python to C++ Transpiler

### Purpose
This is a tool designed to assist with porting Python code to C++, serving as the first step of a porting effort. 
The goal of this tool isn't necessarily to translate all Python perfectly to C++, rather, it's aimed at eliminating 
the boilerplate work that occurs during a software port. As much of Python is very similar to C++, translation is 
feasable for much of the code. Most importantly, the tool also brings over comments and docstrings thus eliminating 
much of the manual labor necessary during a port.

### Concept of Operation
This tool utilizes the Python interpreter to read a Python script or module and break it down into an Abstract 
Syntax Tree. Then, it recursively traverses the tree and converts the nodes into a line of code in C++. Code that 
cannot be directly translated is copied verbatim from the original python script and wrapped with C++ style comment 
symbols and preceded with a comment indicating why it wasn't translated. Once the whole tree is traversed, the 
translated code is written to C++ files and ready for use. 

The trickiest part of python to C++ code conversion is python not being strongly typed. To solve this, we use lists 
to store variable types. If variables are assigned to each other, they begin sharing the same list. Ideally, at a 
certain point in the Python script, a known type will be assigned to one of the variables. Since all variables that 
rely on that type share the same list, they will all reflect the type change without needing to recursively solve 
variable types every time a variable type is discovered or updated. Function parameters and return types also follow 
the same strategy.
 
## Usage
The translator can be used either from the Jupyter notebook or by editing the pyplus script located at the root 
directory of the tool to specify the file to convert and the location for outputting the conversion and run 
it. It is recommended to use the notebook for ease of use. This tool has been validated for **Python 3.8.5**. Use of 
a different version may have unexpected results. Code you want to translate must be valid python code.

## Limitations
As this tool was built in a very limited timeframe, there are several limitations to its translation abilities. 
Below are code constructs that the tool currently fully or partially supports.

#### Full Support
* BoolOp\*\*
* BinOp\*\*
* UnaryOp\*\*
* If\*
* While\*
* Break
* Continue
* Return\*\*
* Pass
* Assign\*\*
* Constant
* Name
* Comments

#### Partial Support
* Expr
* Call
* Compare
* FunctionDef


\*Construct is fully supported, however if the test field contains unsupported constructs, the entire construct 
won't be translated  
\*\*Construct is fully supported, however if it recursively depends on a construct with partial or no support, 
the entire construct won't be translated

## Future Plans
To further improve this tool, I'd like to add support for class conversion. As there is no support for classes 
as of this version, many python projects can't be easily converted. Adding support for class conversion will 
open the door to much more of the code base for translation. Originally, I had planned to implement class support, 
but time constraints forced me to scrap that portion. However, the project was structured in a way to allow for 
adding class support, so the complexity of adding it shouldn't require significant refactoring. After class support, 
recursively solving and translating imports would allow for far more code conversion to occur.