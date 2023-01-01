class Position:

    """
    To track position ( line number and col number of the exception position)
    """

    def __init__(self, idx, ln, col, fname, fcontent):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fname = fname
        self.fcontent = fcontent

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col += 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fname, self.fcontent)
