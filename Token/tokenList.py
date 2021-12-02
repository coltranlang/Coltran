DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = '@_'
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
TT_GETTER = 'GETTER'
TT_EQ ='EQ'
TT_NEQ ='NEQ'
TT_EQEQ ='EQEQ'
TT_GT ='GT'
TT_RSHIFT ='RSHIFT'
TT_LSHIFT ='LSHIFT'
TT_LT ='LT'
TT_GTE ='GTE'
TT_LTE ='LTE'
TT_PLUS_EQ = 'PLUS_EQ'
TT_AND = 'AND'
TT_COLON = 'COLON'
TT_SEMICOLON ='SEMICOLON'
TT_IDENTIFIER = 'IDENTIFIER'
TT_OBJECT_REF = 'OBJECT_REF'
TT_OBJECT_GETTER = 'OBJECT_GETTER'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_DOT = 'DOT'
TT_STRING = 'STRING'
TT_SINGLE_STRING = 'SINGLE_STRING'
TT_BACKTICK_STRING = 'BACKTICK_STRING'
TT_RAW_STRING = 'RAW_STRING'
TT_BACKTICK = 'BACKTICK'
TT_STRING_INTERP = 'STRING_INTERP'
TT_FORMAT = 'FORMAT'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_LSQBRACKET = 'LSQBRACKET'
TT_RSQBRACKET = 'RSQBRACKET'
TT_SQBRACKET = 'SQBRACKET'
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
TT_SLASH = 'SLASH'

NOT_ALLOWED_OBJECTS_KEYS = [
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
    'export',
    'module',
    'require',
    'step',
    'while',
    'task',
    'object',
    'class',
    'def',
    'end',
    'return',
    'continue',
    'break',
    'fv'
]

NOT_ALLOWED_OBJECTS_VALUES = [
    'let',
    'final',
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
    'step',
    'while',
    'endWhile',
    'class',
    'def',
    'end',
    'return',
    'continue',
    'break',
    'raise'
]



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
    'export',
    'module',
    'require',
    'step',
    'while',
    'task',
    'object',
    'class',
    'def',
    'end',
    'return',
    'continue',
    'break',
    'fv',
    'raise'
]

LET = 'let'
FINAL = 'final'
TRUE = 'true'
FALSE = 'false'
NONE = 'none'
AND = 'and'
OR = 'or'
NOT = 'not'
IF = 'if'
THEN = 'then'
ELIF = 'elif'
ELSE = 'else'
FOR = 'for'
TO = 'to'
GET = 'get'
FROM = 'from'
EXPORT = 'export'   
MODULE = 'module'
REQUIRE = 'require'
STEP = 'step'
WHILE = 'while'
TASK = 'task'
OBJECT = 'object'
CLASS = 'class'
DEF = 'def'
END = 'end'
RETURN = 'return'
CONTINUE = 'continue'
BREAK = 'break'
RAISE = 'raise'
FV = 'fv'
PRINT = 'print'
PRINTLN = 'println'



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
