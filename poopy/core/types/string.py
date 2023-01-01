from core.error import IllegalOperationError
from core.types.number import Number


class String:
    """
    for string operating
    """

    def __init__(self, value):
        self.value = value
        self.set_context()
        self.set_pos()

    def __repr__(self):
        return f"{self.value}"
    
    def __str__(self):
        return self.value
        
    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, String):
            return (
                String(self.value + other.value).set_context(self.context),
                None,
            )
        else:
            return None, IllegalOperationError(
                self.pos_start,
                self.pos_end,
                "Adding of incompatible types to String not allowed",
            )

    def multed_by(self, other):
        if isinstance(other, Number):
            return (
                String(self.value * other.value).set_context(self.context),
                None,
            )
        else:
            return None, IllegalOperationError(
                self.pos_start,
                self.pos_end,
                "variodic concatenation of incompatible types not allowed",
            )

    def is_true(self):
        return len(self.value) > 0

    def get_comparison_eq(self, other):
        if isinstance(other, String):
            return (
                String(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, IllegalOperationError(
                self.pos_start, self.pos_end, "Comparing incompatible types with String"
            )

    def get_comparison_ne(self, other):
        if isinstance(other, String):
            return (
                String(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, IllegalOperationError(
                self.pos_start, self.pos_end, "Comparing incompatible types with String"
            )

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
