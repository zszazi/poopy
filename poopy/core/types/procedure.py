from core.runtime import RTResult
from core.interpreter import Interpreter
from core.context import Context
from core.error import RTError
from core.types.number import Number

class Procedure:
    def __init__(self, name, body_node, arg_names, should_return_null):
        self.set_pos()
        self.set_context()
        self.name = name
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_return_null = should_return_null

    def __repr__(self):
        return f"<Procedure {self.name}>"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def execute(self, args):
        from core.symbol_table import SymbolTable
        res = RTResult()
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent_context.symbol_table)

        if len(args) > len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(self.arg_names)} too many args passed into '{self.name}'",
                    self.context,
                )
            )

        if len(args) < len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(self.arg_names) - len(args)} too few args passed into '{self.name}'",
                    self.context,
                )
            )

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set_val(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success((None if self.should_return_null else value))

    def copy(self):
        copy = Procedure(self.name, self.body_node, self.arg_names, self.should_return_null)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
