import core.constant as cc
from core.token import Token
from core.position import Position
from core.error import IllegalCharError, ExpectedCharError


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char == "@":
                self.comment()
            elif self.current_char in ";\n":
                tokens.append(Token(cc.TT_NEWLINE, pos_start = self.pos))
                self.advance()
            elif self.current_char in cc.DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in cc.LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == "+":
                tokens.append(Token(cc.TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(cc.TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(cc.TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(cc.TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(cc.TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(cc.TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(cc.TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(cc.TT_LCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(cc.TT_RCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == "!":
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == "~":
                tokens.append(self.make_xor())
            elif self.current_char == ",":
                tokens.append(Token(cc.TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == ":":
                tokens.append(Token(cc.TT_COLON, pos_start=self.pos))
                self.advance()
            elif self.current_char == '"':
                tokens.append(self.make_string())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(cc.TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in cc.DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(cc.TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(cc.TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()

        while (
            self.current_char is not None
            and self.current_char in cc.LETTERS_DIGITS + "_"
        ):
            id_str += self.current_char
            self.advance()

        tok_type = cc.TT_KEYWORD if id_str in cc.KEYWORDS else cc.TT_IDENTIFIER

        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(cc.TT_NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "expected '=' after '!'")

    def make_equals(self):
        """
        Checks for both = and == and returns TokenType accordingly
        """
        tok_type = cc.TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = cc.TT_EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        """
        Checks for both < and <= and returns TokenType accordingly
        """
        tok_type = cc.TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = cc.TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        """
        Checks for both > and >= and returns TokenType accordingly
        """
        tok_type = cc.TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = cc.TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self):
        _string = ""
        pos_start = self.pos.copy()
        self.advance()

        while self.current_char is not None and self.current_char != '"':
            _string += self.current_char
            self.advance()

        self.advance()

        return Token(cc.TT_STRING, _string, pos_start=pos_start, pos_end=self.pos)

    def comment(self):
        self.advance() #advance past the @ symbol

        while self.current_char != "\n": #skip till new line char is detected
            self.advance()

        self.advance() #advance past the new line too