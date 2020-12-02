from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
from modules import cppcodeline as cline
import ast


class PyAnalyzer():
    """
    This class inherits from the ast.NodeVisitor class to override functions
    for each type of call it parses from the python script. This allows for
    custom handlers for various types of calls
    """
    # Helps evaluate type when performing operations on different types
    type_precedence = {"string": 0, "float": 1, "int": 2, "bool": 3}

    # Python operators translated to C++ operators
    operator_map = {"Add": "+", "Sub": "-", "Mult": " * ", "Div": "/", "Mod": " % ",
                    "LShift": " << ", "RShift": " >> ", "BitOr": " | ", "BitAnd": " & ",
                    "BitXor": " ^ ", "FloorDiv": "/", "Pow": "Pow"}


    def __init__(self, output_files):

        # Saves a reference to the output_files list from the translator class
        self.output_files = output_files

        # Indices to track where to put parsed code
        # When they need to be changed, the function changing it will save
        # its current value, change the values, then once the recursion
        # completes, it will return the value to what it originally was
        # allowing traversal of the files in this recursive manner
        # self.file_index = 0
        # self.function_index = 0

        # Minimum indent will be one tab (4 spaces) since code will be inside
        # functions. Function definitions and other special lines that require
        # no indentation will handle it on their own
        # self.indent = 1

    def analyze_tree(self, tree, file_index, function_index, indent):
        """
        Accepts an AST node and parses through it recursively. It will
        look in the body field and call the respective functions
        to handle each type
        :param tree: An AST created from the python code to be converted
        :param file_index:
        :param function_index:
        :param indent:
        """
        for node in tree.body:
            print(node.__class__.__name__)
            # Using strategy found in ast.py built-in module
            handler_name = "parse_" + node.__class__.__name__
            # Will find if the function called handler_name exists, otherwise
            # it returns parse_unhandled
            handler = getattr(self, handler_name, self.parse_unhandled)
            handler(node, file_index, function_index, indent)

    def parse_unhandled(self, node, file_index, function_index, indent):
        pass

    # Imports
    def parse_Import(self, node, file_index, function_index, indent):
        """
        Overridden method to visit an Import node. In our usage, we can't
        translate this, so we will just ignore it and move to the next node
        :param node: The import node
        """
        print("import")

    def parse_ImportFrom(self, node, file_index, function_index, indent):
        """
        Overridden method to visit an ImportFrom node. In our usage, we can't
        translate this, so we will just ignore it and move to the next node
        :param node: The import node
        """
        print("importfrom")

    # Definitions
    def parse_ClassDef(self, node, file_index, function_index, indent):
        print("classdef")

    def parse_FunctionDef(self, node, file_index, function_index, indent):
        print("funcdef")

    # Control Statements
    def parse_If(self, node, file_index, function_index, indent):
        # Parse conditions and add in the code to the current function

        print("if")

    def parse_For(self, node, file_index, function_index, indent):
        print("for")

    def parse_While(self, node, file_index, function_index, indent):
        print("while")

    def parse_Try(self, node, file_index, function_index, indent):
        print("try")

    def parse_Pass(self, node, file_index, function_index, indent):
        print("pass")

    def parse_Break(self, node, file_index, function_index, indent):
        print("break")

    def parse_Continue(self, node, file_index, function_index, indent):
        print("continue")

    # Operators
    def parse_BoolOp(self, node, file_index, function_index, indent):
        print("boolop")

    def parse_And(self, node, file_index, function_index, indent):
        print("and")

    # Misc
    def parse_Expr(self, node, file_index, function_index, indent):
        print("expr")

    def parse_Assign(self, node, file_index, function_index, indent):
        function_ref = self.output_files[file_index].functions[function_index]

        var_name = node.targets[0].id
        # Determine Type being assigned to variable
        if node.value.__class__ is ast.Constant:
            assign_str = node.value.value
            assign_var_type = type(node.value.value).__name__

        elif node.value.__class__ is ast.Name:
            assign_var_type = self.find_var_type(node.value.id, file_index, function_index)
            if assign_var_type[0] is None:
                self.parse_unhandled(node, file_index, function_index, indent)
                return
            assign_str = node.value.id
        elif node.value.__class__ is ast.BinOp:
            assign_str, assign_var_type = self.parse_BinOp(node.value, file_index, function_index)
            if assign_str is None:
                self.parse_unhandled(node, file_index, function_index, indent)
                return

        else:
            self.parse_unhandled(node, file_index, function_index, indent)
            return

        # Find if name exists in context
        py_var_type = self.find_var_type(var_name, file_index, function_index)[0]

        if py_var_type is None:
            # Declaration
            c_var = cvar.CPPVariable(var_name, node.lineno, assign_var_type)
            function_ref.variables[var_name] = c_var
            code_str = var_name + " = " + str(assign_str) + ";"
            c_code_line = cline.CPPCodeLine(node.lineno, indent,
                                            "declaration", code_str)
            # print(c_code_line)
        else:
            # Verify types aren't changing
            if py_var_type != assign_var_type[0]:
                # Can't do changing types in C++
                self.parse_unhandled(node, file_index, function_index, indent)
                return
            else:
                code_str = var_name + " = " + str(assign_str) + ";"
                c_code_line = cline.CPPCodeLine(node.lineno, indent,
                                                "declaration", code_str)

        function_ref.lines[node.lineno] = c_code_line
        print("assign")

    def parse_BinOp(self, node, file_index, function_index):
        if node.left.__class__ is ast.BinOp:
            # Recursively solve the binary operation
            left_str, left_type = self.parse_BinOp(node.left, file_index, function_index)
        elif node.left.__class__ is ast.Name:
            # Variable should already exist if we're using it, so we just grab
            # it from the current context
            left_str = node.left.id
            left_type = self.find_var_type(node.left.id, file_index, function_index)[0]
        elif node.left.__class__ is ast.Constant:
            left_str = node.left.value
            left_type = type(node.left.value).__name__
        else:
            # Anything we don't handle
            left_str = None

        if node.right.__class__ is ast.BinOp:
            right_str, right_type = self.parse_BinOp(node.right, file_index, function_index)
        elif node.right.__class__ is ast.Name:
            right_str = node.right.id
            right_type = self.find_var_type(node.right.id, file_index, function_index)[0]
        elif node.right.__class__ is ast.Constant:
            right_str = node.right.value
            right_type = type(node.right.value).__name__
        else:
            right_str = None

        if left_str is None or right_str is None:
            return None, None
        left_str = str(left_str)
        right_str = str(right_str)
        operator = node.op.__class__.__name__
        if operator in PyAnalyzer.operator_map:
            if operator == "Pow":
                self.add_include_file("math.h", file_index)
                return_expr = "pow(" + left_str + ", " + right_str + ")"

            elif operator == "FloorDiv":
                return_expr = left_str + " / " + right_str
                # If they aren't both ints, we need to cast to int to truncate
                if left_type != "int" or right_type != "int":
                    return_expr = "(int)(" + return_expr + ")"
                return_type = "int"

            elif operator == "Div":
                return_expr = left_str + " / " + right_str
                # We need to cast one to a double or it will perform integer
                # math
                if left_type != "float" or right_type != "float":
                    return_expr = "(double)" + return_expr
                return_type = "float"

            else:
                return_expr = left_str + PyAnalyzer.operator_map[operator] + right_str
                if left_type in PyAnalyzer.type_precedence and right_type in PyAnalyzer.type_precedence:
                    if PyAnalyzer.type_precedence[left_type] < PyAnalyzer.type_precedence[right_type]:
                        return_type = left_type
                    else:
                        return_type = right_type
                else:
                    return_type = "auto"

        return "(" + return_expr + ")", return_type

    def find_var_type(self, name, file_index, function_index):
        function_ref = self.output_files[file_index].functions[function_index]
        if name in function_ref.parameters:
            return function_ref.parameters[name].var_type
        elif name in function_ref.variables:
            return function_ref.variables[name].var_type
        else:
            return [None]

    def add_include_file(self, name, file_index):
        if name not in self.output_files[file_index].includes:
            self.output_files[file_index].includes.append(name)

    def parse_Call(self, node, file_index, function_index, indent):

        # Reached a function, so we can just pull the name and args out
        print(node.func.id)
        print(node.args)
