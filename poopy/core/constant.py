import string

PROMPT = "\U0001F4A9> "
INTRO = "\U0001F4A9 Poopy Lang \U0001F4A9 \nType POOPY to get started with pooping\n"
OUTRO = "\n\U0001F4A9 Thank you for using Poop Lang \U0001F4A9 \n"
OOPSIE_POOPSIE = "OoOpSiE PooPsIe : Got some error"
CHARS_TO_SKIP = " \t"
POOPY_FILE_EXT = ".poop"
POOPY_FILE_EXT_EMOJI = ".\U0001F4A9"

DIGITS = string.digits
LETTERS = string.ascii_letters
LETTERS_DIGITS = DIGITS + LETTERS

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_POW = "POWER"
TT_EQ = "EQ"
TT_EE = "EE"  # double equal - comparison
TT_NE = "NE"
TT_LT = "LT"
TT_LTE = "LTE"
TT_GT = "GT"
TT_GTE = "GTE"
TT_COMMA = "COMMA"
TT_COLON = "COLON"
TT_NEWLINE = "NEWLINE"
TT_EOF = "EOF"

KEYWORDS = [
    "BUCKET",
    "AND",
    "OR",
    "NOT",
    "XOR",
    "IF",
    "THEN",
    "ALTER",  # similar to elif
    "ELSE",
    "LOOP",
    "TILL",
    "STEP",
    "DO",
    "PROC",
    "END"
]  # TODO: support all logic gate operations

HELP_KEYWORDS = ["POOPY_AUTHOR", "POOPY_VERSION", "HELP", "SYMBOL_TABLE"]

WORK_IN_PROGRESS = ["AND", "OR", "XOR"]
