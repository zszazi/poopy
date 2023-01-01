from core.runtime import RTResult
from core.context import Context
from core.error import RTError, NotDefined, ValError
from core.types.string import String
from core.types.number import Number
from core.types.procedure import Procedure
from core.types.list import List
import core.constant as cc

import os
import math


class BuiltIn:
    def __init__(self, name):
        self.set_pos()
        self.set_context()
        self.name = name

    def __repr__(self):
        return f"<Built-in {self.name}>"

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
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent_context.symbol_table)
        
        built_in_name = f'execute_{self.name}'

        built_in_handler = getattr(self, built_in_name, self.no_execute_method)

        if len(args) > len(built_in_handler.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(built_in_handler.arg_names)} : too many args passed into '{self.name}'",
                    self.context,
                )
            )

        if len(args) < len(built_in_handler.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(built_in_handler.arg_names) - len(args)} : too few args passed into '{self.name}'",
                    self.context,
                )
            )

        for i in range(len(args)):
            arg_name = built_in_handler.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set_val(arg_name, arg_value)

        value = res.register(built_in_handler(new_context))
        if res.error:
            return res
        return res.success(value)

    def no_execute_method(self):
        NotDefined(None, None, f"{self.name} built-in is not defined")

    def copy(self):
        copy = BuiltIn(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute_poop_run(self, new_ctx):
        """
        Execute filename.poop from poop terminal
        """
        from core.run import Run

        filename = str(new_ctx.symbol_table.get("filename"))
        filename_to_run, filename_to_run_extension = os.path.splitext(filename)
        
        if not isinstance(filename_to_run, str):
            return RTResult().failure(
                RTError(self.pos_start, self.pos_end, "Filename must be a String", new_ctx)
            )
        
        if filename_to_run_extension not in (cc.POOPY_FILE_EXT, cc.POOPY_FILE_EXT_EMOJI):
            return RTResult().failure(
                RTError(self.pos_start, self.pos_end, "Filename Extension must end with .poop or \U0001F4A9", new_ctx)
            )

        try:
            with open(filename, "r") as f:
                file_content = f.read()
        except Exception as e:
            return RTResult().failure(
                RTError(self.pos_start, self.pos_end, f"Failed to load Poop File {filename_to_run + filename_to_run_extension}\n {str(e)}", new_ctx)
            )
        
        value, error = Run().run(filename_to_run, file_content, mode="Terminal")
        
        if error:
            return RTResult().failure(
                RTError(self.pos_start, self.pos_end, f"Failed executing script {filename_to_run + filename_to_run_extension}\n, {error}", new_ctx)
            )

        return RTResult().success(None)

    execute_poop_run.arg_names = ["filename"]

    def execute_poop_out(self, new_ctx):
        """
        output the value passed
        """        
        print(str(new_ctx.symbol_table.get("value")))
        return RTResult().success(String("NULL"))
    execute_poop_out.arg_names = ["value"]

    def execute_poop_out_ret(self, new_ctx):
        """
        Returns the output
        """
        return RTResult().success(String((str(new_ctx.symbol_table.get("value")))))
    execute_poop_out_ret.arg_names = ["value"]
    
    def execute_poop_in(self, new_ctx):
        """
        Get user input
        """
        ip = input()
        return RTResult().success(String(ip))
    execute_poop_in.arg_names = []  #No Arguments

    def execute_poop_in_int(self, new_ctx):
        """
        Get user input
        """
        try:
            ip = input()
            num = int(ip)
        except ValueError: 
            ValError(self.pos_start, self.pos_end, f"{ip} must be an integer" )
        return RTResult().success(Number(num))
    execute_poop_in_int.arg_names = []

    def execute_clear(self, new_ctx):
        """
        clear the poop terminal
        """
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        return RTResult().success(String("NULLa"))
    execute_clear.arg_names = []

    def execute_is_number(self, new_ctx):
        """
        Check if the value is a Number
        """
        is_num = isinstance(new_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number(1) if is_num else Number(0))
    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, new_ctx):
        """
        Check if the value is a String
        """
        is_string = isinstance(new_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number(1) if is_string else Number(0))
    execute_is_string.arg_names = ["value"]

    def execute_is_proc(self, new_ctx):
        """
        Check if the values is a Procedure
        """
        print("is proc")
        is_proc = isinstance(new_ctx.symbol_table.get("value"), Procedure)
        return RTResult().success(Number(1) if is_proc else Number(0))
    execute_is_proc.arg_names = ["value"]

    def execute_is_builtin(self, new_ctx):
        """
        Check if the values is a Built-in
        """
        is_builtin = isinstance(new_ctx.symbol_table.get("value"), BuiltIn)
        return RTResult().success(Number(1) if is_builtin else Number(0))
    execute_is_proc.arg_names = ["value"]

    def execute_is_list(self, new_ctx):
        """
        Check if the value is a list
        """
        print("is list")
        is_list = isinstance(new_ctx.symbol_table.get("value"), List)
        return RTResult().success(Number(1) if is_list else Number(0))
    execute_is_number.arg_names = ["value"]

    def execute_math_sqrt(self, new_ctx):
        """
        Get square root of a value
        """
        num = new_ctx.symbol_table.get("value")
        
        if isinstance(num, Number):
            if str(num).count("."):
                return RTResult().success(Number(math.sqrt(float(str(num)))))
            else:
                return RTResult().success(Number(math.sqrt(int(str(num)))))
        else:
            ValError(self.pos_start, self.pos_end, f"{num} must be an integer or float" )
    execute_math_sqrt.arg_names = ["value"]

poop_run = BuiltIn("poop_run")
poop_out = BuiltIn("poop_out")
poop_out_ret = BuiltIn("poop_out_ret")
poop_in = BuiltIn("poop_in")
poop_in_int = BuiltIn("poop_in_int")
clear = BuiltIn("clear")
is_number = BuiltIn("is_number")
is_string = BuiltIn("is_string")
is_proc = BuiltIn("is_proc")
is_builtin = BuiltIn("is_builtin")
is_list = BuiltIn("is_list")
math_sqrt = BuiltIn("math_sqrt")
poop_poop = BuiltIn("poop_poop")