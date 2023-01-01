from core.types.number import Number
from core.types.string import String
import core.types.built_in as BultIns

import os
from enum import Enum
import math

class SymbolTable:
    """
    To keep track of all running variable name and their values
    """

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            self.parent.get(name)
        return value

    def set_val(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

    # TODO: Implement a nice looking table format here
    def __repr__(self):
        # return str(pprint.pprint(self.symbols))
        return str(self.symbols)


class GlobalSymbolTable(SymbolTable):
    def __init__(self):
        super().__init__()
        super().set_val("NULL", String("NULL"))
        super().set_val("TRUE", Number(1))
        super().set_val("FALSE", Number(0))

        # TODO: Make poop Clipart
        super().set_val("POOPY", String(list_poopy_available_commands()))
        super().set_val("POOPY_INFO", String(list_poopy_info()))
        super().set_val("POOPY_AUTHOR", String(PoopyInfo.AUTHOR.value))
        super().set_val("POOPY_VERSION", String(PoopyInfo.VERSION.value))
        super().set_val("POOPY_EXAMPLE", String(list_poopy_code_examples()))

        # TODO: Symbol table printer
        super().set_val("SYMBOL_TABLE", ("\U0001F4A9" * 10).center(50))

        #Math Constants
        super().set_val("MATH_PI", Math.MATH_PI)
        super().set_val("MATH_EULER", Math.MATH_EULER)
        super().set_val("MATH_TAU", Math.MATH_TAU)
        super().set_val("MATH_INF", Math.MATH_INF)

        #MATH Builtins
        super().set_val("MATH_SQRT", BultIns.math_sqrt)

        #Built-ins
        super().set_val("POOP_RUN", BultIns.poop_run)
        super().set_val("POOP_OUT", BultIns.poop_out)
        super().set_val("POOP_OUT_RET", BultIns.poop_out_ret)
        super().set_val("POOP_IN", BultIns.poop_in)
        super().set_val("POOP_IN_INT", BultIns.poop_in_int)
        super().set_val("CLEAR", BultIns.clear)
        super().set_val("IS_NUMBER", BultIns.is_number)
        super().set_val("IS_STRING", BultIns.is_string)
        super().set_val("IS_PROC", BultIns.is_proc)
        super().set_val("IS_BUILTIN", BultIns.is_builtin)
        super().set_val("IS_LIST", BultIns.is_list)


class HelpTable:
    pass

class PoopyInfo(Enum):
    AUTHOR = "Sai :@: zszazi"
    VERSION = os.getenv("POOPY_VERSION") or "0.0.1"
    EXAMPLE = " "
    INFO = " "

class Math():
    MATH_PI = Number(math.pi)
    MATH_EULER = Number(math.e)
    MATH_TAU = Number(math.tau)
    MATH_INF = Number(math.inf)

def list_poopy_available_commands():
    a = [e.name for e in PoopyInfo]
    return "Available PooPy commands -> " + " ".join(
        ["POOPY_" + e.name for e in PoopyInfo]
    )


def list_poopy_info():
    return "\n".join(
        [
            e.name + "\t->\t" + e.value
            for e in PoopyInfo
            if e.name not in ("INFO", "EXAMPLE")
        ]
    )


def list_poopy_code_examples():
    return "How to Poop Coming Soon"
