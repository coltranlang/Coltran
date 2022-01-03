DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = '@_'
NOT_ALLOWED_SYMBOLS = '!$%^&*()+-=[]{};\':"\\|,.<>/?`~'
LETTERS_SYMBOLS = LETTERS + SYMBOLS
LETTERS_DIGITS_SYMBOLS = LETTERS + DIGITS + SYMBOLS
TT_DATA_TYPE = ['int', 'float', 'char', 'void']
DATA_TYPE_SYMBOL = 'DATA_TYPE_SYMBOL'
TT_KEYWORD = 'KEYWORD'
TT_TYPE = 'TYPE'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_BINARY = 'BINARY'
TT_HEX = 'HEX'
TT_OCTAL = 'OCTAL'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_FLOOR_DIV = 'FLOOR_DIV'
TT_MOD = 'MODULO'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POWER = 'POWER'
TT_GETTER = 'GETTER'
TT_EQ = 'EQ'
TT_NEQ = 'NEQ'
TT_EQEQ = 'EQEQ'
TT_GT = 'GT'
TT_RSHIFT = 'RSHIFT'
TT_LSHIFT = 'LSHIFT'
TT_LT = 'LT'
TT_GTE = 'GTE'
TT_LTE = 'LTE'
TT_PLUS_PLUS = 'PLUS_PLUS'
TT_MINUS_MINUS = 'MINUS_MINUS'
TT_PLUS_EQ = 'PLUS_EQ'
TT_MINUS_EQ = 'MINUS_EQ'
TT_MUL_EQ = 'MUL_EQ'
TT_DIV_EQ = 'DIV_EQ'
TT_FLOOR_DIV_EQ = 'FLOOR_DIV_EQ'
TT_MOD_EQ = 'MOD_EQ'
TT_POWER_EQ = 'POWER_EQ'
TT_LSHIFT_EQ = 'LSHIFT_EQ'
TT_RSHIFT_EQ = 'RSHIFT_EQ'
TT_AND = 'AND'
TT_NOT_IN = 'NOT_IN'
TT_COLON = 'COLON'
TT_SEMICOLON = 'SEMICOLON'
TT_IDENTIFIER = 'IDENTIFIER'
TT_OBJECT_REF = 'OBJECT_REF'
TT_OBJECT_GETTER = 'OBJECT_GETTER'
TT_COMMA = 'COMMA'
TT_ARROW = 'ARROW'
TT_DOT = 'DOT'
TT_DOUBLE_STRING = 'STRING'
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
TT_DOLLAR = 'DOLLAR'
TT_PIPE = 'PIPE'
TT_SLASH = 'SLASH'
TT_SPREAD = 'SPREAD'
TT_MERGE = 'MERGE'
TT_DEL = 'DEL'
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
    'in',
    'notin',
    'is',
    'as',
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
    'match',
    'case',
    'attempt',
    'catch',
    'default',
    'return',
    'continue',
    'break',
    'fm',
    'raise'
]

NOT_ALLOWED_OBJECTS_VALUES = [
    'let',
    'final',
    'and',
    'or',
    'not',
    'if',
    'then',
    'elif',
    'else',
    'for',
    'to',
    'in',
    'notin',
    'is',
    'as',
    'step',
    'while',
    'end',
    'class',
    'def',
    'end',
    'match',
    'case',
    'default',
    'attempt',
    'catch',
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
    'in',
    'notin',
    'is',
    'as',
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
    'match',
    'case',
    'default',
    'attempt',
    'catch',
    'finally',
    'return',
    'continue',
    'break',
    'fm',
    'raise',
    'del'
]

TYPES = [
    'Number',
    'String',
    'Boolean',
    'NoneType',
    'List',
    'Pair',
    'Dict',
    'Object',
    'Class',
    'Function',
    'BuiltInFunction',
    'BuiltInMethod'
]

LET= 'let'
FINAL= 'final'
TRUE= 'true'
FALSE= 'false'
NONE= 'none'
AND= 'and'
OR= 'or'
NOT= 'not'
IF= 'if'
THEN= 'then'
ELIF= 'elif'
ELSE= 'else'
FOR= 'for'
TO= 'to'
GET= 'get'
FROM= 'from'
EXPORT = 'export'
MODULE= 'module'
REQUIRE= 'require'
STEP= 'step'
WHILE= 'while'
TASK= 'task'
OBJECT= 'object'
CLASS= 'class'
DEF= 'def'
END= 'end'
MATCH= 'match'
CASE= 'case'
ATTEMPT= 'attempt'
CATCH= 'catch'
DEFAULT= 'default'
RETURN= 'return'
CONTINUE= 'continue'
BREAK= 'break'
RAISE= 'raise'
FM= 'fm'
PRINT= 'print'
PRINTLN= 'println'



BUILTIN= [
    'print',
    'println',
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
    'format',
]
