class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.value is None:
            return f"Type : {self.type}"
        else:
            return f"{self.type} : {self.value}"

    def matches(self, type_, value):
        return self.type == type_ and self.value == value
