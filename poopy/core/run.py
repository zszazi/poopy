from core.lexer import Lexer
from core.parser import Parser
from core.interpreter import Interpreter
from core.context import Context
from core.symbol_table import GlobalSymbolTable

global_symbol_table = GlobalSymbolTable()

class Run:
    def __init__(self, fname=None, text=None):
        self.fname = fname
        self.text = text

    def run(self, fname, text, mode = "File"):
        lexers = Lexer(fname, text)
        tokens, error = lexers.make_tokens()
        if error:
            return None, error

        # generate AST
        parser = Parser(tokens)
        ast = parser.parse()

        if ast.error:
            return None, ast.error

        # Run Program
        interpreter = Interpreter()
        root_context = Context("<program>")
        root_context.symbol_table = global_symbol_table

        result = interpreter.visit(ast.node, root_context)
        if mode == "Terminal":
            result.value = str(result.value)
            if "NULL" in result.value: 
                result.value = result.value.replace("NULL", "")
            return result.value, result.error
        else:
            return " ", result.error
