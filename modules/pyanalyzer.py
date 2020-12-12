import ast
from modules import cppfile as cfile
from modules import cppfunction as cfun
from modules import cppvariable as cvar
from modules import cppcodeline as cline
from modules import pyplusexceptions as ppex
from modules import portedfunctions as pf


class PyAnalyzer():
    # Helps evaluate type when performing operations on different types
    type_precedence_dict = {"string": 0, "float": 1, "int": 2, "bool": 3,
                            "auto": 8, "None": 9, "void": 9}

    # Python operators translated to C++ operators
    operator_map = {"Add": "+", "Sub": "-", "Mult": " * ", "Div": "/",
                    "Mod": " % ", "LShift": " << ", "RShift": " >> ",
                    "BitOr": " | ", "BitAnd": " & ", "BitXor": " ^ ",
                    "FloorDiv": "/", "Pow": "Pow", "Not": "!",
                    "Invert": "~", "UAdd": "+", "USub": "-", "And": " && ",
                    "Or": " || "
                    }

    # Tuple of all functions we have a special conversion from python to C++
    ported_functions = ("print", "input", "sqrt")

    # Python Comparison operators translated to C++ operators
    # We aren't able to do in/is checks easily, so they are excluded from the
    # mapping
    comparison_map = {"Eq": " == ", "NotEq": " != ", "Lt": " < ",
                      "LtE": " <= ", "Gt": " > ", "GtE": " >= "
                      }

    def __init__(self, output_files, raw_lines):
        """
        This initializes an object that will recurse through an AST to convert
        python code text to objects representing C++ code

        :param output_files: List of cppfiles where the analyzer should place
                             cppfile objects/data
        :param raw_lines: List of strings representing the entire python script
                          line by line, unmodified from the source
        """
        # Saves a reference to the output_files list from the translator class
        self.output_files = output_files

        self.raw_lines = raw_lines

    def analyze(self, tree, file_index, function_key, indent):
        self.pre_analysis(tree, file_index, indent)
        self.analyze_tree(tree, file_index, function_key, indent)

    def pre_analysis(self, tree, file_index, indent):
        # First work through function declarations so we know what calls go to
        # self written functions
        for node in tree:
            if node.__class__ is ast.FunctionDef:
                self.parse_function_header(node, file_index)

        # Now we'll parse the bodies of the functions
        for node in tree:
            if node.__class__ is ast.FunctionDef:
                self.analyze_tree(node.body, file_index, node.name, indent)

    def parse_function_header(self, node, file_index):
        func_ref = self.output_files[file_index].functions
        args = node.args
        # Verify the function can actually be converted to C++
        if len(args.kw_defaults) > 0 or len(args.kwonlyargs) > 0 \
            or len(args.posonlyargs) > 0 or args.kwarg is not None \
                or args.vararg is not None:
            return

        default_args_index = len(args.args) - len(args.defaults)
        params = {}
        for index in range(len(args.args)):
            name = args.args[index].arg
            if index >= default_args_index:
                default = args.defaults[index-default_args_index]
                default_type = [type(default.value).__name__]
                if default_type[0] == "str":
                    params[name] = cvar.CPPVariable(name + "=\"" + default.value + "\"",
                                                    -1, default_type)
                else:
                    params[name] = cvar.CPPVariable(name + "=" + str(default.value),
                                                    -1, default_type)
            else:
                params[name] = cvar.CPPVariable(name, -1)

        func_ref[node.name] = cfun.CPPFunction(node.name, node.lineno,
                                               node.end_lineno, params)

    def analyze_tree(self, tree, file_index, function_key, indent):
        """
        Accepts an AST node and parses through it recursively. It will
        look in the body field and call the respective functions
        to handle each type

        :param tree: An AST created from the python code to be converted
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :param int indent: Amount to indent code by
        """
        for node in tree:
            # Using strategy found in ast.py built-in module
            handler_name = "parse_" + node.__class__.__name__
            # Will find if the function called handler_name exists, otherwise
            # it returns parse_unhandled
            handler = getattr(self, handler_name, self.parse_unhandled)
            handler(node, file_index, function_key, indent)

    def parse_unhandled(self, node, file_index, function_key, indent):
        pass

    # Imports
    def parse_Import(self, node, file_index, function_key, indent):
        """
        Overridden method to visit an Import node. In our usage, we can't
        translate this, so we will just ignore it and move to the next node

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :param int indent: Amount to indent lines of code by
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        pass

    def parse_ImportFrom(self, node, file_index, function_key, indent):
        """
        Overridden method to visit an ImportFrom node. In our usage, we can't
        translate this, so we will just ignore it and move to the next node

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :param int indent: Amount to indent lines of code by
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        pass

    # Definitions
    def parse_ClassDef(self, node, file_index, function_key, indent):
        # We won't copy over a class definition as we aren't handling the
        # conversion
        pass

    # Control Statements
    def parse_If(self, node, file_index, function_key, indent, if_str="if"):
        # Parse conditions and add in the code to the current function
        func_ref = self.output_files[file_index].functions[function_key]
        test_str = self.recurse_operator(node.test, file_index, function_key)[0]
        func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                        node.end_lineno,
                                                        node.end_col_offset,
                                                        indent,
                                                        if_str + " (" + test_str + ")\n"
                                                        + indent*cline.CPPCodeLine.tab_delimiter
                                                        + "{")

        self.analyze_tree(node.body, file_index, function_key, indent+1)
        # Get the last codeline and add the closing bracket
        func_ref.lines[node.body[-1].lineno].code_str += "\n" + indent*cline.CPPCodeLine.tab_delimiter + "}"
        if len(node.orelse) == 1 and node.orelse[0].__class__ is ast.If:
            # Else if case
            self.parse_If(node.orelse[0], file_index, function_key, indent,
                          "else if")

        elif len(node.orelse) > 0:
            # Else case
            else_lineno, else_end_col_offset = self.find_else_lineno(node.orelse[0].lineno - 2)
            func_ref.lines[else_lineno] = cline.CPPCodeLine(else_lineno,
                                                            else_lineno,
                                                            else_end_col_offset,
                                                            indent,
                                                            "else\n"
                                                            + indent * cline.CPPCodeLine.tab_delimiter
                                                            + "{")
            self.analyze_tree(node.orelse, file_index, function_key, indent + 1)
            # Get the last codeline and add the closing bracket
            func_ref.lines[node.orelse[-1].lineno].code_str += "\n" + indent * cline.CPPCodeLine.tab_delimiter + "}"

    def find_else_lineno(self, search_index):
        while search_index > -1:
            # Check line isn't a comment
            if self.raw_lines[search_index].lstrip()[0] == "#":
                search_index -= 1
                continue
            else:
                end_col_offset = self.raw_lines[search_index].find("else:")
                if end_col_offset < 0:
                    raise ppex.TranslationNotSupported()
                else:
                    end_col_offset += 4

                # Line number is 1+index in list
                return search_index + 1, end_col_offset

    def parse_While(self, node, file_index, function_key, indent):
        func_ref = self.output_files[file_index].functions[function_key]
        test_str = self.recurse_operator(node.test, file_index, function_key)[0]
        func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                        node.end_lineno,
                                                        node.end_col_offset,
                                                        indent,
                                                        "while (" + test_str + ")\n"
                                                        + indent * cline.CPPCodeLine.tab_delimiter
                                                        + "{")
        self.analyze_tree(node.body, file_index, function_key, indent + 1)
        func_ref.lines[node.body[-1].lineno].code_str += "\n" + indent * cline.CPPCodeLine.tab_delimiter + "}"

    def parse_Pass(self, node, file_index, function_key, indent):
        # We have nothing to do for a pass call
        pass

    def parse_Break(self, node, file_index, function_key, indent):
        func_ref = self.output_files[file_index].functions[function_key]
        func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                        node.end_lineno,
                                                        node.end_col_offset,
                                                        indent,
                                                        "break;")

    def parse_Continue(self, node, file_index, function_key, indent):
        func_ref = self.output_files[file_index].functions[function_key]
        func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                        node.end_lineno,
                                                        node.end_col_offset,
                                                        indent,
                                                        "continue;")

    def parse_Return(self, node, file_index, function_key, indent):
        func_ref = self.output_files[file_index].functions[function_key]
        if node.value is None:
            func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                            node.end_lineno,
                                                            node.end_col_offset,
                                                            indent, "return;")
        else:
            return_str, return_type = self.recurse_operator(node.value,
                                                            file_index,
                                                            function_key)
            func_ref.return_type = self.type_precedence(return_type, func_ref.return_type)
            func_ref.lines[node.lineno] = cline.CPPCodeLine(node.lineno,
                                                            node.end_lineno,
                                                            node.end_col_offset,
                                                            indent,
                                                            "return " + return_str + ";")

    # Misc
    def parse_Expr(self, node, file_index, function_key, indent):
        func_ref = self.output_files[file_index].functions[function_key]

        # only worrying about docstrings and function calls
        if node.value.__class__ is ast.Constant:
            if type(node.value.value) is str:
                # Verify this is a docstring
                if self.raw_lines[node.value.lineno-1].strip()[0:3] == '"""':
                    return_str = self.convert_docstring(node.value.value, indent)
                else:
                    self.parse_unhandled(node, file_index, function_key, indent)
                    return
            else:
                self.parse_unhandled(node, file_index, function_key, indent)
                return

        elif node.value.__class__ is ast.Call:
            try:
                return_str, return_type = self.parse_Call(node.value, file_index, function_key)
            except ppex.TranslationNotSupported:
                self.parse_unhandled(node, file_index, function_key, indent)
                return
            return_str += ";"
        else:
            # Any other type doesn't matter as the work it does wouldn't be
            # saved
            self.parse_unhandled(node, file_index, function_key, indent)
            return

        func_ref.lines[node.value.lineno] = cline.CPPCodeLine(node.value.lineno,
                                                              node.value.end_lineno,
                                                              node.end_col_offset,
                                                              indent, return_str)

    def convert_docstring(self, doc_string, indent):
        doc_string = doc_string.strip()
        tab_char = cline.CPPCodeLine.tab_delimiter
        return_str = "/*\n"
        while doc_string.find("\n") > -1:
            doc_string = doc_string.lstrip()
            return_str += cline.CPPCodeLine.tab_delimiter*indent + doc_string[:doc_string.find("\n")] + "\n"
            doc_string = doc_string[doc_string.find("\n")+1:]

        doc_string = doc_string.lstrip()
        return_str += tab_char * indent + doc_string
        return return_str + "\n" + tab_char*indent + "*/"

    def parse_Assign(self, node, file_index, function_key, indent):
        """
        Function to parse ast.Assign nodes

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :param int indent: Amount to indent lines of code by
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        function_ref = self.output_files[file_index].functions[function_key]

        # Won't handle chained assignment
        if len(node.targets) > 1:
            self.parse_unhandled(node, file_index, function_key, indent)
            return
        var_name = node.targets[0].id
        try:
            assign_str, assign_type = self.recurse_operator(node.value,
                                                            file_index,
                                                            function_key)
        except ppex.TranslationNotSupported:
            self.parse_unhandled(node, file_index, function_key, indent)
            return

        # Find if name exists in context
        try:
            py_var_type = self.find_var_type(var_name,
                                             file_index,
                                             function_key)
            # Verify types aren't changing
            if py_var_type[0] != assign_type[0]:
                # Can't do changing types in C++
                self.parse_unhandled(node, file_index, function_key, indent)
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

    def parse_Call(self, node, file_index, function_key):
        # Should be a name to have a function call we can parse
        if node.func.__class__ is not ast.Name:
            raise ppex.TranslationNotSupported()

        # Get a reference to current function to shorten code width
        func_ref = self.output_files[file_index].functions
        func_name = node.func.id

        # Ensure this is a valid function call we can use
        if func_name not in cvar.CPPVariable.types \
            and func_name not in func_ref \
                and func_name not in self.ported_functions:
            raise ppex.TranslationNotSupported()

        # We track the types passed in to help update parameter types when
        # functions get called
        arg_types = []
        arg_list = []
        for arg in node.args:
            arg_str, arg_type = self.recurse_operator(arg,
                                                      file_index,
                                                      function_key)
            arg_list.append(arg_str)
            arg_types.append(arg_type)

        # Check if casting or normal function call
        if func_name in cvar.CPPVariable.types:
            # Trim the extra space since we are performing a cast rather than
            # a variable declaration
            return_str = "(" + cvar.CPPVariable.types[func_name][:-1] + ")("
            return_type = [func_name]
        elif func_name in func_ref:
            return_str = func_name + "("

            # Now we try to update the parameter types if applicable
            function = func_ref[func_name]
            for param, passed_type in zip(function.parameters.values(),
                                          arg_types):
                param.py_var_type[0] = self.type_precedence(param.py_var_type,
                                                         passed_type)[0]
            return_type = function.return_type
        elif func_name in self.ported_functions:
            return self.parse_ported_function(file_index, function_key, func_name, arg_list, arg_types)
        else:
            raise ppex.TranslationNotSupported()

        # Finish generating function call with parameters inserted
        for arg in arg_list:
            return_str += arg + ", "
        return_str = return_str[:-2] + ")"

        return return_str, return_type

    def parse_ported_function(self, file_index, function_key, function, args, arg_types):
        if function == "print":
            return_str = pf.print_translation(args)
            return_type = ["None"]
            self.output_files[file_index].add_include_file("iostream")

        elif function == "sqrt":
            if len(args) > 2:
                raise ppex.TranslationNotSupported()
            return_str = pf.sqrt_translation(args)
            return_type = ["float"]
            self.output_files[file_index].add_include_file("math.h")

        return return_str, return_type

    def parse_Constant(self, node, file_index, function_key):
        if type(node.value) is str:
            return ("\"" + node.value + "\""), [type(node.value).__name__]
        else:
            return str(node.value), [type(node.value).__name__]

    # Operators
    def parse_BoolOp(self, node, file_index, function_key):
        """
        Function to parse ast.BoolOp nodes

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        # List of tuples consisting of (string,[type_string])
        compare_nodes = []
        mixed_types = False
        # Multiple nodes can be chained, so we need to go through all of them
        for internal_node in node.values:
            compare_nodes.append(self.recurse_operator(internal_node,
                                                       file_index,
                                                       function_key))

        # This shouldn't be possible normally, but we check to be safe
        if len(compare_nodes) < 2:
            raise ppex.TranslationNotSupported()

        return_str = ""
        ret_var_type = compare_nodes[0][1][0]
        # Go through all but the last one and create a string separated by
        # the C++ version of the python operator
        for compare_node in compare_nodes[:-1]:
            if compare_node[1][0] != ret_var_type:
                mixed_types = True
            return_str += (compare_node[0] +
                           PyAnalyzer.operator_map[node.op.__class__.__name__])

        if compare_nodes[-1][1][0] != ret_var_type:
            mixed_types = True
        return_str += compare_nodes[-1][0]

        # Short circuit operators complicate type determination, so if they
        # aren't all the same type, we'll use auto, otherwise these operators
        # keep they type if all items being compared are the same type
        if mixed_types:
            return_type = ["auto"]
        else:
            return_type = compare_nodes[0][1]

        return "(" + return_str + ")", return_type

    def parse_BinOp(self, node, file_index, function_key):
        """
        Function to parse ast.BinOp nodes

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """

        left_str, left_type = self.recurse_operator(node.left,
                                                    file_index,
                                                    function_key)
        right_str, right_type = self.recurse_operator(node.right,
                                                      file_index,
                                                      function_key)

        left_str = str(left_str)
        right_str = str(right_str)
        operator = node.op.__class__.__name__
        if operator in PyAnalyzer.operator_map:
            if operator == "Pow":
                self.output_files[file_index].add_include_file("math.h")
                return_expr = "pow(" + left_str + ", " + right_str + ")"
                return_type = ["float"]

            elif operator == "FloorDiv":
                return_expr = left_str + " / " + right_str
                # If they aren't both ints, we need to cast to int to truncate
                if left_type[0] != "int" or right_type[0] != "int":
                    return_expr = "(int)(" + return_expr + ")"
                return_type = ["int"]

            elif operator == "Div":
                return_expr = left_str + " / " + right_str
                # We need to cast one to a double or it will perform integer
                # math
                if left_type[0] != "float" or right_type[0] != "float":
                    return_expr = "(double)" + return_expr
                return_type = ["float"]

            else:
                return_expr = left_str \
                              + PyAnalyzer.operator_map[operator] \
                              + right_str

                return_type = self.type_precedence(left_type, right_type)

        return "(" + return_expr + ")", return_type

    def type_precedence(self, type_a, type_b):
        """
        We determine which type takes precedent based on loss of
        precision. So a float will take precedence over an int
        If we can't figure it out, we'll default to auto

        :param list type_a: The first type to compare
        :param list type_b: The second type to compare
        :return list : The type that takes precedent, otherwise auto
        """

        if type_a[0] in PyAnalyzer.type_precedence_dict and type_b[0] in PyAnalyzer.type_precedence_dict:
            if PyAnalyzer.type_precedence_dict[type_a[0]] < PyAnalyzer.type_precedence_dict[type_b[0]]:
                return_type = type_a
            else:
                return_type = type_b
        else:
            return_type = ["auto"]
        return return_type

    def parse_UnaryOp(self, node, file_index, function_key):
        """
        Function to parse ast.UnaryOp nodes

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        operator = node.op.__class__
        if operator.__name__ not in PyAnalyzer.operator_map:
            raise ppex.TranslationNotSupported()

        return_str, return_type = self.recurse_operator(node.operand,
                                                        file_index,
                                                        function_key)
        if operator is ast.Not:
            return_type = "bool"
        else:
            return_type = "int"

        return "(" + PyAnalyzer.operator_map[operator.__name__] + return_str + ")", [return_type]

    def parse_Compare(self, node, file_index, function_key):
        """
        Function to parse ast.Compare nodes

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        """
        # Ensure we can do all types of operations present in code line
        for op in node.ops:
            if op.__class__.__name__ not in PyAnalyzer.comparison_map:
                raise ppex.TranslationNotSupported()

        # Comparisons can be chained, so we use the left item as the
        # "last" item to be compared to start the chain
        last_comparator = self.recurse_operator(node.left,
                                                file_index,
                                                function_key)[0]
        return_str = ""
        for index in range(1, len(node.ops)-1):
            comparator = self.recurse_operator(node.comparators[index],
                                               file_index,
                                               function_key)[0]
            return_str += "(" + last_comparator \
                          + PyAnalyzer.comparison_map[node.ops[index-1].__class__.__name__] \
                          + comparator + ") && "
            last_comparator = comparator

        comparator = self.recurse_operator(node.comparators[-1],
                                           file_index,
                                           function_key)[0]

        return_str += "(" + last_comparator + \
                      PyAnalyzer.comparison_map[node.ops[-1].__class__.__name__] \
                      + comparator + ")"
        return return_str, ["bool"]

    def recurse_operator(self, node, file_index, function_key):
        """
        Accepts a node and determines the appropriate handler function to use
        then passes the parameters to the correct handler function

        :param node: Node to parse
        :param int file_index: Index of the file this node should be written to
        :param int function_key: Key of the function this node should be
                                   written to
        :raises TranslationNotSupported: Raised if python code cannot be
                                         translated
        :returns Tuple: Tuple of (value, type)
        """
        node_type = node.__class__
        if node_type is ast.BinOp:
            return self.parse_BinOp(node, file_index, function_key)

        elif node_type is ast.BoolOp:
            return self.parse_BoolOp(node, file_index, function_key)

        elif node_type is ast.UnaryOp:
            return self.parse_UnaryOp(node, file_index, function_key)

        elif node_type is ast.Compare:
            return self.parse_Compare(node, file_index, function_key)

        elif node_type is ast.Call:
            return self.parse_Call(node, file_index, function_key)

        elif node_type is ast.Name:
            # Variable should already exist if we're using it, so we just grab
            # it from the current context
            try:
                return node.id, self.find_var_type(node.id,
                                                   file_index,
                                                   function_key)
            except ppex.VariableNotFound:
                # Can't handle non declared variables being used
                raise ppex.TranslationNotSupported()

        elif node_type is ast.Constant:
            return self.parse_Constant(node, file_index, function_key)

        else:
            # Anything we don't handle
            raise ppex.TranslationNotSupported()

    # Helper methods
    def find_var_type(self, name, file_index, function_key):
        """
        Finds the type of a variable in a given context

        :param string name: The name of the variable to identify
        :param int file_index: Index of the file for context
        :param int function_key: Key of the function for context
        :raises VariableNotFound:  Raised if the variable isn't in the context
        :return: The list reference containing the variable type
        """
        function_ref = self.output_files[file_index].functions[function_key]
        if name in function_ref.parameters:
            return function_ref.parameters[name].py_var_type
        elif name in function_ref.variables:
            return function_ref.variables[name].py_var_type
        else:
            raise ppex.VariableNotFound()
