from core.error import RTError, IllegalOperationError
from core.types.number import Number

class List:
    """
    List class = {}, {1,2,3,4}
    """
    def __init__(self, elements):
        self.set_context()
        self.set_pos() 
        self.elements = elements

    def __str__(self):
        return f"{', '.join([repr(x) for x in self.elements])}"

    def __repr__(self):
        return f"{{{', '.join([repr(x) for x in self.elements])}}}"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self
    
    def added_to(self, other):
        temp_list = self.copy()
        temp_list.elements.append(other)
        return temp_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    'index is out of bounds',
                    self.context
                )
        else:
            return None, IllegalOperationError(
                self.pos_start,
                self.pos_end,
                "Operation of incompatible types to List not allowed",
            )

    def copy(self):
        copy = List(self.elements[:])
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy