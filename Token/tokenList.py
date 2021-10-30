DIGITS = '0123456789'
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
TT_COLON = 'COLON'
TT_SEMICOLON ='SEMICOLON'
TT_IDENTIFIER = 'IDENTIFIER'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_STRING = 'STRING'
TT_SINGLE_STRING = 'SINGLE_STRING'
TT_FORMAT = 'FORMAT'
TT_LBRACES = 'LBRACES'
TT_RBRACES = 'RBRACES'
TT_LSQBRACKET = 'LSQBRACKET'
TT_RSQBRACKET = 'RSQBRACKET'
TT_KEYWORD = 'KEYWORD'
TT_NEWLINE = 'NEWLINE'
TT_WHITESPACE = 'WHITESPACE'
TT_EOF = 'EOF'

LETTERS = '@$ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
LETTERS_DIGITS = LETTERS + DIGITS

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
    'then',
    'elif',
    'else',
    'for',
    'to',
    'get',
    'from',
    'step',
    'while',
    'task',
    'endTask',
    'endFor',
    'return',
    'continue',
    'break'
]


BUILTINTASKS = [
    'print',
    'len',
    'append',
    'pop',
    'del',
    'len',
    'clear',
    'exit',
    'intInput',
    'floatInput',
    'format',
    'toString'
]
