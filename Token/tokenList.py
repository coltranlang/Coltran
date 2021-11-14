DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = '@$_'
NOT_ALLOWED_SYMBOLS = '!$%^&*()+-=[]{};\':"\\|,.<>/?`~'
LETTERS_SYMBOLS = LETTERS + SYMBOLS
LETTERS_DIGITS_SYMBOLS = LETTERS + DIGITS + SYMBOLS
TT_DATA_TYPE = ['int', 'float', 'char', 'void']
DATA_TYPE_SYMBOL ='DATA_TYPE_SYMBOL'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIVISION = 'DIVISION'
TT_MOD = 'MODULO'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POWER = 'POWER'
TT_EQ ='EQ'
TT_NEQ ='NEQ'
TT_EQEQ ='EQEQ'
TT_GT ='GT'
TT_LT ='LT'
TT_GTE ='GTE'
TT_LTE ='LTE'
TT_PLUS_EQ = 'PLUS_EQ'
TT_COLON = 'COLON'
TT_SEMICOLON ='SEMICOLON'
TT_IDENTIFIER = 'IDENTIFIER'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_DOT = 'DOT'
TT_STRING = 'STRING'
TT_SINGLE_STRING = 'SINGLE_STRING'
TT_RAW_STRING = 'RAW_STRING'
TT_BACKTICK = 'BACKTICK'
TT_STRING_INTERP = 'STRING_INTERP'
TT_FORMAT = 'FORMAT'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_LSQBRACKET = 'LSQBRACKET'
TT_RSQBRACKET = 'RSQBRACKET'
TT_KEYWORD = 'KEYWORD'
TT_NEWLINE = 'NEWLINE'
TT_WHITESPACE = 'WHITESPACE'
TT_ESCAPE = 'ESCAPE'
TT_RETURN = 'RETURN'
TT_EOF = 'EOF'
TT_WILDCARD = 'WILDCARD'
TT_START = 'START'
TT_END = 'END'
TT_STAR = 'STAR'
TT_DASH = 'DASH'
TT_QUESTION = 'QUESTION'
TT_PIPE = 'PIPE'





KEYWORDS = [
    'let',
    'final',
    'true',
    'false',
    'none',
    'and',
    'or',
    'not',
    'if',
    'endIf',
    'then',
    'elif',
    'else',
    'for',
    'endFor',
    'to',
    'get',
    'from',
    'step',
    'while',
    'endWhile',
    'task',
    'endTask',
    'object',
    'endObject',
    'class',
    'endClass',
    'def',
    'end',
    'return',
    'continue',
    'break',
    'fv'
]


BUILTIN = [
    'print',
    'len',
    'append',
    'pop',
    'del',
    'len',
    'clear',
    'exit',
    'input',
    'inputInt',
    'inputFloat',
    'str',
    'int',
    'float',
    'bool',
    'list',
    'object',
    'format'
]
