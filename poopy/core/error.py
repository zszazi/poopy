class Error:
    """
    This is the base class for defining Exceptions and Errors
    """

    ENDC = "\033[0m"
    SEV_1 = "\033[93m"  # Yellow
    SEV_2 = "\033[48;2;255;165;0m"  # Orange bg
    SEV_3 = "\033[91m"  # Red
    MAY_DAY = "\U0001F6A8"  # Siren

    def __init__(self, pos_start, pos_end, err_name, severity, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.err_name = err_name
        self.details = details
        self.severity = severity  # 3 - HIGH SEVE ( Red ), 2 - MEDIUM SEV ( Orange ), 1 - LOW SEV ( Yellow )

    def as_string(self):
        if self.severity == 1:
            return f"{self.SEV_1}{self.err_name}{self.ENDC} : {self.details} in File: {self.pos_start.fname} at Line {self.pos_start.ln + 1}"
        elif self.severity == 2:
            return f"{self.SEV_2}{self.err_name}{self.ENDC} : {self.details} in File: {self.pos_start.fname} at Line {self.pos_start.ln + 1}"
        elif self.severity == 3:
            return f"{self.SEV_3}{self.err_name}{self.ENDC} : {self.details} in File: {self.pos_start.fname} at Line {self.pos_start.ln + 1}"
        elif self.severity == 4:
            return f"{self.MAY_DAY}{self.SEV_3}{self.err_name}{self.MAY_DAY}{self.ENDC} : {self.details} in File: {self.pos_start.fname} at Line {self.pos_start.ln + 1}"


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", 1, details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Invalid Syntax", 3, details)


class NotDefined(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Not Defined", 2, details)


class ExpectedCharError:
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Unexpected Character", 3, details)


class FeatureInProgress(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Feature is Work in Progress", 2, details)


#FIXME : IllegalOperation Error to a Runtime error
class IllegalOperationError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Operation", 1, details)

class ValError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Value Error", 3, details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "RunTime Error", 3, details)
        self.context = context

    def as_string(self):
        tracer = self.generate_traceback()
        tracer += f"{self.SEV_3}{self.err_name}{self.ENDC} : {self.details} in File: {self.pos_start.fname} at Line {self.pos_start.ln + 1}"
        return tracer

    def generate_traceback(self):
        tracer = ""
        pos = self.pos_start
        ctx = self.context

        while ctx:
            tracer = (
                f" File {pos.fname}, line {str(pos.ln + 1)}, in {ctx.display_name}\n"
                + tracer
            )
            pos = ctx.parent_entry_pos
            ctx = ctx.parent_context

        return "Traceback (most recent call last):\n" + tracer
