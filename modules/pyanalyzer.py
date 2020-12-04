from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
from modules import cppcodeline as cline
from modules import pyplusexceptions as ppex
import ast


class PyAnalyzer(ast.NodeVisitor):
    """
    This class inherits from the ast.NodeVisitor class to override functions
    for each type of call it parses from the python script. This allows for
    custom handlers for various types of calls
    """
    # Helps evaluate type when performing operations on different types
    type_precedence = {"string": 0, "float": 1, "int": 2, "bool": 3}

    # Python operators translated to C++ operators
    operator_map = {"Add": "+", "Sub": "-", "Mult": " * ", "Div": "/",
                    "Mod": " % ", "LShift": " << ", "RShift": " >> ",
                    "BitOr": " | ", "BitAnd": " & ", "BitXor": " ^ ",
                    "FloorDiv": "/", "Pow": "Pow", "Not": "!",
                    "Invert": "~", "UAdd": "+", "USub": "-", "And": " && ",
                    "Or": " || "
                    }

    # Python Comparison operators translated to C++ operators
    # We aren't able to do in/is checks easily, so they are excluded from the
    # mapping
    comparison_map = {"Eq": " == ", "NotEq": " != ", "Lt": " < ",
                      "LtE": " <= ", "Gt": " > ", "GtE": " >= "
                      }

    def __init__(self, output_files, raw_lines):

        # Saves a reference to the output_files list from the translator class
        self.output_files = output_files

        self.raw_lines = raw_lines

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

    # Misc
    def parse_Expr(self, node, file_index, function_index, indent):
        print("expr")

    def parse_Call(self, node, file_index, function_index, indent):
        # Reached a function, so we can just pull the name and args out
        print(node.func.id)
        print(node.args)

    def parse_Assign(self, node, file_index, function_index, indent):
        function_ref = self.output_files[file_index].functions[function_index]

        if len(node.targets) > 1:
            self.parse_unhandled(node, file_index, function_index, indent)
            return
        var_name = node.targets[0].id
        try:
            assign_str, assign_type = self.recurse_operator(node.value,
                                                            file_index,
                                                            function_index)
        except ppex.TranslationNotSupported:
            self.parse_unhandled(node, file_index, function_index, indent)
            return

        # Find if name exists in context
        try:
            py_var_type = self.find_var_type(var_name,
                                             file_index,
                                             function_index)[0]
            # Verify types aren't changing
            if py_var_type != assign_type:
                # Can't do changing types in C++
                self.parse_unhandled(node, file_index, function_index, indent)
                return
            else:
                code_str = var_name + " = " + str(assign_str) + ";"
                c_code_line = cline.CPPCodeLine(node.lineno, node.end_lineno,
                                                node.end_col_offset, indent,
                                                code_str)
        except ppex.VariableNotFound:
            # Declaration
            c_var = cvar.CPPVariable(var_name, node.lineno, assign_type)
            function_ref.variables[var_name] = c_var
            code_str = var_name + " = " + str(assign_str) + ";"
            c_code_line = cline.CPPCodeLine(node.lineno, node.end_lineno,
                                            node.end_col_offset, indent,
                                            code_str)

        function_ref.lines[node.lineno] = c_code_line

    # Operators
    def parse_BoolOp(self, node, file_index, function_index):
        internal_return = []
        mixed_types = False
        # Multiple nodes can be chained, so we need to go through all of them
        for internal_node in node.values:
            internal_return.append(self.recurse_operator(internal_node,
                                                         file_index,
                                                         function_index))

        # This shouldn't be possible normally, but we check to be safe
        if len(internal_node) < 2:
            raise ppex.TranslationNotSupported()

        return_str = ""
        ret_var_type = internal_return[0][1]
        # Go through all but the last one and create a string separated by
        # the C++ version of the python operator
        for index in range(len(internal_return)-1):
            if internal_return[index][1] != ret_var_type:
                mixed_types = True
            return_str += (internal_return[index][0] +
                           PyAnalyzer.operator_map[node.op.__class__.__name__])

        if internal_return[len(internal_return)-1][1] != ret_var_type:
            mixed_types = True
        return_str += internal_return[len(internal_return)-1][0]

        # Short circuit operators complicate type determination, so if they
        # aren't all the same type, we'll use auto, otherwise these operators
        # keep they type if all items being compared are the same type
        if mixed_types:
            return_type = "auto"
        else:
            return_type = internal_return[0][1]

        return "(" + return_str + ")", return_type

    def parse_BinOp(self, node, file_index, function_index):
        left_str, left_type = self.recurse_operator(node.left,
                                                    file_index,
                                                    function_index)
        right_str, right_type = self.recurse_operator(node.right,
                                                      file_index,
                                                      function_index)

        left_str = str(left_str)
        right_str = str(right_str)
        operator = node.op.__class__.__name__
        if operator in PyAnalyzer.operator_map:
            if operator == "Pow":
                self.output_files[file_index].add_include_file("math.h")
                return_expr = "pow(" + left_str + ", " + right_str + ")"
                return_type = "float"

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
                return_expr = left_str \
                              + PyAnalyzer.operator_map[operator] \
                              + right_str
                # We determine which type takes precedent based on loss of
                # precision. So a float will take precedence over an int
                # If we can't figure it out, we'll default to auto
                if left_type in PyAnalyzer.type_precedence and right_type in PyAnalyzer.type_precedence:
                    if PyAnalyzer.type_precedence[left_type] < PyAnalyzer.type_precedence[right_type]:
                        return_type = left_type
                    else:
                        return_type = right_type
                else:
                    return_type = "auto"

        return "(" + return_expr + ")", return_type

    def parse_UnaryOp(self, node, file_index, function_index):
        operator = node.op.__class__
        if operator.__name__ not in PyAnalyzer.operator_map:
            raise ppex.TranslationNotSupported()

        return_str, return_type = self.recurse_operator(node.operand,
                                                        file_index,
                                                        function_index)
        if operator is ast.Not:
            return_type = "bool"
        else:
            return_type = "int"

        return "(" + PyAnalyzer.operator_map[operator] + return_str + ")", return_type

    def parse_Compare(self, node, file_index, function_index):
        # Ensure we can do all types of operations present in code line
        for op in node.ops:
            if op.__class__.__name__ not in PyAnalyzer.comparison_map:
                raise ppex.TranslationNotSupported()

        # Comparisons can be chained, so we use the left item as the
        # "last" item to be compared to start the chain
        last_comparator = self.recurse_operator(node.left,
                                                file_index,
                                                function_index)[0]
        return_str = ""
        for index in range(1, len(node.ops)-1):
            comparator = self.recurse_operator(node.comparators[index],
                                               file_index,
                                               function_index)[0]
            return_str += "(" + last_comparator \
                          + PyAnalyzer.comparison_map[node.ops[index-1]] \
                          + comparator + ") && "
            last_comparator = comparator

        comparator = self.recurse_operator(node.comparators[len(node.ops)-1],
                                           file_index,
                                           function_index)[0]

        return_str += "(" + last_comparator + \
                      PyAnalyzer.comparison_map[node.ops[len(node.ops)-1].__class__.__name__] \
                      + comparator + ")"
        return return_str, "bool"

    def recurse_operator(self, node, file_index, function_index):
        node_type = node.__class__
        if node_type is ast.BinOp:
            return self.parse_BinOp(node, file_index, function_index)

        elif node_type is ast.BoolOp:
            return self.parse_BoolOp(node, file_index, function_index)

        elif node_type is ast.UnaryOp:
            return self.parse_UnaryOp(node, file_index, function_index)

        elif node_type is ast.Compare:
            return self.parse_Compare(node, file_index, function_index)

        elif node_type is ast.Name:
            # Variable should already exist if we're using it, so we just grab
            # it from the current context
            try:
                return node.id, self.find_var_type(node.id,
                                                   file_index,
                                                   function_index)[0]
            except ppex.VariableNotFound:
                # Can't handle non declared variables being used
                raise ppex.TranslationNotSupported()

        elif node_type is ast.Constant:
            return str(node.value), type(node.value).__name__

        else:
            # Anything we don't handle
            raise ppex.TranslationNotSupported()

    # Helper methods
    def find_var_type(self, name, file_index, function_index):
        """
        Finds the type of a variable in a given context
        :param name: The name of the variable to identify
        :param file_index: Index of the file for context
        :param function_index: Index of the function for context
        :return: The list reference containing the variable type
        :raises VariableNotFound exception if the variable isn't in the context
        """
        function_ref = self.output_files[file_index].functions[function_index]
        if name in function_ref.parameters:
            return function_ref.parameters[name].var_type
        elif name in function_ref.variables:
            return function_ref.variables[name].var_type
        else:
            raise ppex.VariableNotFound()
