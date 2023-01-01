from core.error import RTError


class Number:
    """
    for storing numbers and operating on them
    """

    def __init__(self, value):
        self.value = value
        self.set_context()
        self.set_pos()

    def __repr__(self):
        return str(self.value)
    
    def __str__(self):
        return str(self.value)

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def is_noice_num(self):
        if hex(int(self.value)) == "0x10f2c":
            print("\U0001F609\x1B[3m noice \x1B[0m")
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return (
                Number(self.value + other.value)
                .is_noice_num()
                .set_context(self.context),
                None,
            )

    def subbed_by(self, other):
        if isinstance(other, Number):
            return (
                Number(self.value - other.value)
                .is_noice_num()
                .set_context(self.context),
                None,
            )

    def multed_by(self, other):
        if isinstance(other, Number):
            return (
                Number(self.value * other.value)
                .is_noice_num()
                .set_context(self.context),
                None,
            )

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Division by Zero", self.context
                )
            return (
                Number(self.value / other.value)
                .is_noice_num()
                .set_context(self.context),
                None,
            )

    def raised_to(self, other):
        if isinstance(other, Number):
            return (
                Number(self.value**other.value)
                .is_noice_num()
                .set_context(self.context),
                None,
            )

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value == other.value)).set_context(self.context),
                None,
            )

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value != other.value)).set_context(self.context),
                None,
            )

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value <= other.value)).set_context(self.context),
                None,
            )

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value >= other.value)).set_context(self.context),
                None,
            )

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def anded_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value and other.value)).set_context(self.context),
                None,
            )

    def ored_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value or other.value)).set_context(self.context),
                None,
            )

    def xored_by(self, other):
        """
        Bitwise XR
        """
        if isinstance(other, Number):
            return Number(int(self.value ^ other.value)).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0
