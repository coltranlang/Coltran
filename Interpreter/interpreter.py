import os
from types import BuiltinMethodType, new_class
from Parser.parser import Parser
from Parser.stringsWithArrows import *
from Token.token import Token
import Token.tokenList as tokenList
from Lexer.lexer import Lexer
from Memory.memory import SymbolTable


import sys
import re
import time
import socket
import json


regex = '[+-]?[0-9]+\.[0-9]+'
string_methods = {
            'upperCase': 'upperCase',
            'lowerCase': 'lowerCase',
            'capitalize': 'capitalize',
            'split': 'split',
            'join': 'join',
            'substr': 'substr',
            'replace': 'replace',
            'slice': 'slice',
            'strip': 'strip',
            'length': 'length',
            'charAt': 'charAt',
            'includes': 'includes',
            'startsWith': 'startsWith',
            'find': 'find',
 }

list_methods = {
                'length': 'length',
                'append': 'append',
                'pop': 'pop',
                'remove': 'remove',
                'insert': 'insert',
                'empty': 'empty',
                'reverse': 'reverse',
                'getItem': 'getItem',
                'setItem': 'setItem',
                'slice': 'slice',
                'join': 'join',
                'sort': 'sort',
                'contains': 'contains',
                'includes': 'includes',
            }

number_methods = {
    'toInt': 'toInt',
    'toFloat': 'toFloat',
    'toString': 'toString',
}
def string_split(string, delimiter):
    res = []
    start = 0
    while True:
        index = string.find(delimiter, start)
        if index == -1:
            res.append(string[start:])
            break
        else:
            res.append(string[start:index])
            start = index + len(delimiter)
    return res

def getsubstr(string, start, end):
        return string[start:end]

def string_strip(text):
    split_text = text.split()
    new_text = ''
    for i in range(len(split_text)):
        if i == 0:
            new_text += split_text[i].strip()
        else:
            new_text += ' ' + split_text[i].strip()
    return new_text



class Regex:
        def __init__(self):
            self.value = None

        def parse(self, text, pos_start, pos_end):
            wildcard_token = Token(tokenList.TT_WILDCARD, None, pos_start, pos_end)
            start_token = Token(tokenList.TT_START, None, pos_start, pos_end)
            end_token = Token(tokenList.TT_END, None, pos_start, pos_end)
            comma_token = Token(tokenList.TT_COMMA, None, pos_start, pos_end)
            arrow_token = Token(tokenList.TT_ARROW, None, pos_start, pos_end)
            plus_token = Token(tokenList.TT_PLUS, None, pos_start, pos_end)
            star_token = Token(tokenList.TT_STAR, None, pos_start, pos_end)
            question_token = Token(tokenList.QUESTION, None, pos_start, pos_end)
            pipe_token = Token(tokenList.TT_PIPE, None, pos_start, pos_end)
            
        def compile(self, pattern):
            self.pattern = re.compile(pattern)
            return self
        def match(self, text):
            return self.pattern.findall(text)


def isEmptyString(value):
    return value == ""
 
            
class TypeOf:
    def __init__(self, type):
        self.type = type

    def getType(self):
        result = ''
        if self.type == 'str':
            result = 'string'
        elif self.type == 'tuple':
            result = 'pair'
        elif isinstance(self.type, Number) or type(self.type).__name__ == "NumberNode":
            if re.match(regex, str(self.type)):
                result = 'float'
            else:
                result = 'int'
        else:
            if isinstance(self.type, str) or isinstance(self.type, String):
                result = 'string'
            elif isinstance(self.type, tuple) or isinstance(self.type, Pair):
                result = 'pair'
            elif isinstance(self.type, Object):
                result = 'object'
            elif isinstance(self.type, bool) or isinstance(self.type, Boolean):
                result = 'boolean'
            elif isinstance(self.type, NoneType):
                result = 'NoneType'
            elif isinstance(self.type, list) or isinstance(self.type, List):
                result = 'list'
            elif isinstance(self.type, Class):
                result = 'class'
            elif isinstance(self.type, Types):
                result = 'type'
            elif isinstance(self.type, Function):
                result = 'function'
            elif isinstance(self.type, BuiltInFunction):
                result = 'builtin_function'
            elif isinstance(self.type, BuiltInMethod):
                result = 'builtin_method'
            elif isinstance(self.type, BuiltInMethod_String):
                result = 'builtin_method_string'
            elif isinstance(self.type, BuiltInMethod_List):
                result = 'builtin_method_list'
            elif isinstance(self.type, Dict) or isinstance(self.type, dict):
                result = 'dict'
            else:
                result = type(self.type).__name__
        return result


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbolTable = None


def setNumber(token):
    value = "none"
    if not token and token != 0:
        value = 0
    if token == 'true':
        value = 1
    elif token == 'false':
        value = 0
    elif token == 'none':
        value = 0
    else:
        value = token
    if hasattr(token, 'value'):
        if token.value == 'true':
            value = 1
        elif token.value == 'false':
            value = 0
        elif token.value == 'none':
            value = 0
        else:
            value = token.value
    return value


class Program:
    def error():
        def Default(detail):
            error = f"\n{detail['name']}: {detail['message']}\n"
            if detail['exit']:
                Program.printErrorExit(error)
            else:
                Program.printError(error)
                
        def Error(detail):
            isDetail = {
                'name': detail['name'],
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def IllegalCharacter(options):
            error = f'\nIllegal character: {options["originator"]}\n\nin File: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n'
            Program.printErrorExit(error)

        def Syntax(detail):
            isDetail = {
                'name': 'SyntaxError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def Runtime(detail):
            isDetail = {
                'name': 'RuntimeError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def ZeroDivisionError(detail):
            isDetail = {
                'name': 'ZeroDivisionError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def NameError(detail):
            isDetail = {
                'name': 'NameError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def TypeError(detail):
            isDetail = {
                'name': 'TypeError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                
        def KeyError(detail):
            isDetail = {
                'name': 'KeyError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                
        def ValueError(detail):
            isDetail = {
                'name': 'ValueError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
         
        def PropertyError(detail):
            isDetail = {
                'name': 'PropertyError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                          
        def IndexError(detail):
            isDetail = {
                'name': 'IndexError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
                
        def ModuleError(detail):
            isDetail = {
                'name': 'ModuleError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        methods = {
            'Default': Default,
            'Error': Error,
            'IllegalCharacter': IllegalCharacter,
            'Syntax': Syntax,
            'Runtime': Runtime,
            'ZeroDivisionError': ZeroDivisionError,
            'NameError': NameError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'ValueError': ValueError,
            'PropertyError': PropertyError,
            'IndexError': IndexError,
            'ModuleError': ModuleError
        }
        return methods

    def printWithType(*args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))

    def printError(arg):
        print(arg)

    def printErrorExit(arg):
        print(arg)
        sys.exit(1)

    def asString(detail):
        result = f'\n{detail["name"]}: {detail["message"]}\n'
        result += f'\nin File {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' + \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        return result

    def asStringTraceBack(detail):
        result = Program.generateTraceBack(detail)
        result += f'\n{detail["name"]}: {detail["message"]}\n'
        result += '\n\n' + \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        return result

    def generateTraceBack(detail):
        result = ''
        pos = detail['pos_start']
        context = detail['context']
        while context:
            result = f'\nFile {detail["pos_start"].fileName}, line {str(pos.line + 1)}, in {context.display_name if context.display_name != "none" else "anonymous"}\n' + result if hasattr(pos, 'line') else ''
            pos = context.parent_entry_pos
            context = context.parent
        return '\nStack trace (most recent call last):\n' + result
    
    def runFile(file):
        try:
            with open(file, 'r') as file_handle:
                code = file_handle.read()
                # check if file is ending with .alden
                if file[-6:] != ".alden":
                    print("File is not an alden file")
                    return
                else:
                    return code
        except FileNotFoundError:
            return None

    def createModule(module_name, module, context):
        res = RuntimeResult()
        lexer = Lexer(module_name, module)
        tokens, error = lexer.make_tokens()
        if error: return "", error
        parser = Parser(tokens, module_name)
        ast = parser.parse()
        if ast.error: return "", ast.error
        interpreter = Interpreter()
        new_context = Context('<module>', context)
        new_context.symbolTable = SymbolTable(context.symbolTable)
        
        result = interpreter.visit(ast.node, new_context)
        value = ""
        
        if hasattr(result, 'value') and hasattr(result, 'error'):
            if isinstance(result.value, List):
                for tok in result.value.elements:
                    # check if item has export defined
                    if hasattr(tok, 'name'):
                        if tok.name ==  "Export":
                            value = tok
                            context.symbolTable.set(module_name, value)
                            tok.context.symbolTable.set(module_name, value)
        return res.success(value)


class RuntimeResult:
    def __init__(self):
        self.reset()
        
    def reset(self, error=None):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_continue = False
        self.loop_break = False

    def register(self, res):
        if hasattr(res, 'value' and 'error' and 'func_return_value' and 'loop_break' and 'loop_continue'):
            self.error = res.error
            self.func_return_value = res.func_return_value
            self.loop_continue = res.loop_continue
            self.loop_break = res.loop_break
            return res.value
        else:
            return res
   
    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_break = True
        return self

    def failure(self, error):
        self.reset(True)
        self.error = True
        self.value = ''
        return self

    def noreturn(self):
        return str('')

    def should_return(self):
        return (
            self.error or
            self.func_return_value or
            self.loop_continue or
            self.loop_break
        )

    


class Value:
    def __init__(self):
        self.setPosition()
        self.setContext()

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self
    
    def setTrueorFalse(self, value):
        if value:
            return Boolean(True)
        else:
            return Boolean(False)

    def added_to(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'+' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def merge(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'|=' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })
    
    def increment(self):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'++' not supported on type '{TypeOf(self).getType()}'",
            'context': self.context
        })
        
    def decrement(self):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'--' not supported on type '{TypeOf(self).getType()}'",
            'context': self.context
        })

    def subtracted_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'-' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def multiplied_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'*' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def divided_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'/' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def powred_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'**' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def modulo(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'%' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_eq(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'==' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_ne(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'!=' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_lt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_gt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })
        
    def get_comparison_rshift(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>>' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_lshift(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<<' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_lte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<=' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_gte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>=' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context,
        })

    def and_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'&&' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def or_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'or' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def get_comparison_in(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'in' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })
        
    def get_comparison_not_in(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'notin' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        })

    def notted(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
            'context': self.context,
            'exit': False
        })

    def execute(self, args):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(args).getType()}",
            'context': self.context
        }
        return RuntimeResult().failure(self.illegal_operation_typerror(error))

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return Boolean(False)

    def illegal_operation(self, error, other=None):
        if not other:
            other = self
        if hasattr(other, 'value'):
            return Program.error()["Syntax"]({
                'message': error['message'] if error['message'] else f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit'] if 'exit' in error else True
            })
        else:
            return Program.error()["Syntax"]({
                'message': f"Illegal operation",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit']
            })
            
    def key_error(self, error, property):
            return Program.error()["Syntax"]({
                'message': error['message'],
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit'] if 'exit' in error else True
            })

    def none_value(self):
        return Program.NoneValue()

    def illegal_operation_typerror(self, error, other=None):
        errorDetail = {
            'pos_start': error['pos_start'],
            'pos_end': error['pos_end'],
            'message': error['message'],
            'context': error['context'],
            'exit': error['exit'] if 'exit' in error else False
        }
        if not other:
            other = self
        if not 'message' in error:
            if hasattr(other, 'value'):
                errorDetail['message'] = f'Illegal operation for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}'
                return Program.error()['Syntax'](errorDetail)
            else:
                errorDetail['message'] = f"illegal operation"
                return Program.error()['Syntax'](errorDetail)
        return Program.error()['TypeError'](errorDetail)

    def illegal_operation_indexError(self, error, other=None):
        errorDetail = {
            'pos_start': error['pos_start'],
            'pos_end': error['pos_end'],
            'message': error['message'],
            'context': error['context'],
            'exit': error['exit'] if 'exit' in error else False
        }
        if not other:
            other = self
        if not 'message' in error:
            if hasattr(other, 'value'):
                errorDetail['message'] = f'Illegal operation for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}'
                return Program.error()['Syntax'](errorDetail)
            else:
                errorDetail['message'] = f"illegal operation"
                return Program.error()['Syntax'](errorDetail)
        return Program.error()['IndexError'](errorDetail)


class Statement(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else []
        self.value = self.elements

    def copy(self):
        copy = Statement(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        for element in self.elements:
            if element == None:
                return ""
            else:
                return str(element)
        return ''


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.id = value
        self.value = value
        self.name = value
        
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        if value:
            return Boolean(True)
        else:
            return Boolean(False)

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't add {TypeOf(self.value).getType()} to {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def increment(self):
        return Number(setNumber(self.value) + 1).setContext(self.context), None
    
    def decrement(self):
        return Number(setNumber(self.value) - 1).setContext(self.context), None

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't subtract {TypeOf(self.value).getType()} from {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't multiply {TypeOf(self.value).getType()} with {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }

        if isinstance(other, Number):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def divided_by(self, other):
        if other.value == 0:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"division by zero",
                'context': self.context,
                'exit': False
            }
            return None, Program.error()['ZeroDivisionError'](error)
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't divide {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def powred_by(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't power {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def modulo(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't perform modulo on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            if other.value == 0 or setNumber(other.value) == 0:
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"modulo by zero",
                    'context': self.context,
                    'exit': False
                }
                return None, Program.error()['ZeroDivisionError'](error)
            else:
                return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            if other.value == 0 or setNumber(other.value) == 0:
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"modulo by zero",
                    'context': self.context,
                    'exit': False
                }
                return None, Program.error()['ZeroDivisionError'](error)
            else:
                return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def get_comparison_eq(self, other):
        return Boolean(setNumber(self.value) == setNumber(other.value)), None

    def get_comparison_ne(self, other):
        return Boolean(setNumber(self.value) != setNumber(other.value)), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'>' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return self.setTrueorFalse(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_in(self, other):
        new_list = []
        for el in other.value:
            if hasattr(el, 'value'):
                new_list.append(el.value) 
            elif hasattr(el, 'name'):
                new_list.append(el) 
            else:
                new_list.append(el)
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'in' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, List):
            return self.setTrueorFalse(setNumber(self.value) in new_list).setContext(self.context), None
        if isinstance(other, Pair):
            return self.setTrueorFalse(setNumber(self.value) in new_list).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_not_in(self, other):
        val = 'false'
        if self.get_comparison_in(other)[0].value == "false":
            val = "true"
        return Boolean(val), None
                          
    def get_comparison_notin(self, other):
        new_list = []
        for el in other.value:
            if hasattr(el, 'value'):
                new_list.append(el.value) 
            elif hasattr(el, 'name'):
                new_list.append(el) 
            else:
                new_list.append(el)
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'not in' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, List):
            return self.setTrueorFalse(setNumber(self.value) not in new_list).setContext(self.context), None
        if isinstance(other, Pair):
            return self.setTrueorFalse(setNumber(self.value) not in new_list).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)
    
    def get_comparison_rshift(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'>>' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        # get bitwise right shift
        if isinstance(other, Number):
            return Number(setNumber(self.value) >> setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) >> setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_lshift(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'<<' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        # get bitwise left shift
        if isinstance(other, Number):
            return Number(setNumber(self.value) << setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) << setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_lte(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'<=' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return self.setTrueorFalse(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_gte(self, other):
        error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"'>=' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context,
                    'exit': False
                }
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) >= setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return self.setTrueorFalse(setNumber(self.value) >= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def and_by(self, other): 
        error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform and on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                'context': self.context
        }
        if isinstance(other, String):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Boolean(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, NoneType):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def or_by(self, other):
        error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform or on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                'context': self.context
        }
        if isinstance(other, String):
            return Number(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, NoneType):
            return Number(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def notted(self):
        error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform not on {TypeOf(self.value).getType()}",
                'context': self.context
        }
        if isinstance(self, Number):
            return Number(self.setTrueorFalse(not setNumber(self.value))).setContext(self.context), None
        elif isinstance(self, Boolean):
            return Boolean(self.setTrueorFalse(not setNumber(self.value))).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)
    
    def copy(self):
        copy = Number(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return self.value == "true" if self.value else "false"

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value, arg=None):
        super().__init__()
        self.value = value
        self.id = value
         
            
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        if value:
            return Boolean(True)
        else:
            return Boolean(False)

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform concatenation on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}" if hasattr(other, 'value') and hasattr(self, 'value') else f"can't perform concatenation on type none",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return None, self.illegal_operation_typerror(error, other)
        if isinstance(other, String):
            return String(setNumber(str(self.value)) + setNumber(str(other.value))).setContext(self.context), None
        else:
            return "none", self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform multiplication on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if other.value == "true":
            return String(setNumber(str(self.value)) * setNumber(str(other.value))).setContext(self.context), None
        elif other.value == "false":
            return String(setNumber(str(self.value)) * setNumber(str(other.value))).setContext(self.context), None
        elif other.value == "none" or self.value == "none":
            return None, self.illegal_operation_typerror(error)
        if isinstance(other, String):

            return None, self.illegal_operation_typerror(error)

        if isinstance(other, Number):
            return String(setNumber(str(self.value)) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(self, error, other)

    def get_comparison_eq(self, other):
        return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_ne(self, other):
        return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_lt(self, other):
        return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_gt(self, other):
        return self.setTrueorFalse(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_lte(self, other):
        return self.setTrueorFalse(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_gte(self, other):
        return self.setTrueorFalse(setNumber(self.value) >= setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_in(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'in' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        }
        if isinstance(other, String):
            return self.setTrueorFalse(other.value in self.value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)
        
    def get_comparison_not_in(self, other):
        value = self.get_comparison_in(other)[0].value
        return self.setTrueorFalse(True if value == "false" else False), None
    
    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform indexing on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                return String(setNumber(str(self.value))[setNumber(other.value)]).setContext(self.context), None
            except IndexError:
                error['message'] = f"string index out of range"
                return None, self.illegal_operation_indexError(error)
        else:
            return None, self.illegal_operation(error, other)
    
    def notted(self):
        return self.setTrueorFalse(not setNumber(self.value)).setContext(self.context), None

    def and_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def or_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None

    def copy(self):
        copy = String(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    def is_true(self):
        return "true" if len(self.value) > 0 else "false"

    def __str__(self):
        return f"'{self.value}'"

    def __repr__(self):
        return f"'{self.value}'"


class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        if value == True or value == "true":
            self.value = "true"
            self.id = "true"
        elif value == False or value == "false":
            self.value = "false"
            self.id = "false"
        self.setPosition(0, 0)
        self.setContext(None)


    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = Boolean(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    
    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't add {TypeOf(self.value).getType()} to {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
    def increment(self):
        return Number(setNumber(self.value) + 1).setContext(self.context), None
    
    def decrement(self):
        return Number(setNumber(self.value) - 1).setContext(self.context), None
        
        
    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform multiplication on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't subtract {TypeOf(self.value).getType()} from {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
    
    
    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't divide {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
      
    def modulo_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform modulo on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
    def powred_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform powred on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
    def get_comparison_eq(self, other):
        return Boolean(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_ne(self, other):
        return Boolean(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
    
    def get_comparison_lt(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Boolean(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Boolean(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
    
    
    def get_comparison_gt(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Boolean(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Boolean(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
        
    def get_comparison_lte(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<=' operator can't be used on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Boolean(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Boolean(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
    def and_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform and on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Boolean(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            if self.value == "false":
                return Boolean(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
            return Number(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, String):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
        
    def or_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform or on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Boolean(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            if self.value == "true":
                return Boolean(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
            return Number(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, String):
            return String(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)
        
        
    def notted(self):
        if self.value == "true":
            return Boolean("false").setContext(self.context), None
        return Boolean("true").setContext(self.context), None

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


class NoneType(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.id = value
        self.setPosition(0, 0)
        self.setContext(None)

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = NoneType(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def get_comparison_eq(self, other):
        return self.setTrueorFalse(other.value == "none"), None
    
    def get_comparison_ne(self, other):
        return self.setTrueorFalse(other.value != "none"), None
    
    def and_by(self, other):
        return self.setTrueorFalse(other.value == "none"), None
    
    def or_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform or on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if other.value == "none":
            return None, None
        if isinstance(other, Boolean):
            return Boolean(setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, String):
            return String(setNumber(other.value)).setContext(self.context), None
        else:
            return String(other.value).setContext(self.context), None
        
    def notted(self):
        return Boolean("true").setContext(self.context), None
    
    def is_true(self):
        return self.value == "true" if self.value else "false"
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


Boolean.true = Boolean("true")
Boolean.false = Boolean("false")
NoneType.none = NoneType("none")





class List(Value):
    def __init__(self, elements=None, type=None):
        super().__init__()
        self.elements = elements if elements is not None else []
        self.value = self.elements
        self.type = type
        self.id = self.elements
        
    def added_to(self, other):
        if isinstance(other, List):
            return List(self.elements + other.elements), None
        elif isinstance(other, String):
            new_list = []
            for char in other.value:
                new_list.append(String(char).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return List(self.elements + new_list), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't add '{TypeOf(other.value).getType()}' to '{TypeOf(self.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation(error, other)

    
    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't subtract '{TypeOf(other.value).getType()}' from {TypeOf(self.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return List(new_list), None
            except:
                return None, "none"
        else:
            return None, self.illegal_operation(error, other)

    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"unsupported operation on 'list' and '{TypeOf(other.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't multiply {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            new_list = new_list.elements * other.value
            return List(new_list), None
        else:
            return None, self.illegal_operation(error, other)

    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None
    
    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, List):
            value = len(self.elements) < len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
    
    def get_comparison_gt(self, other):
        if isinstance(other, List):
            value = len(self.elements) > len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
     
    def get_comparison_lte(self, other):
        if isinstance(other, List):
            value = len(self.elements) <= len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'<=' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
    
    def get_comparison_gte(self, other):
        if isinstance(other, List):
            value = len(self.elements) >= len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>=' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
        
    def get_comparison_in(self, other):
        for element in self.elements:
            
            if other.isSame(element) if hasattr(other, "isSame") else other.value == element.value:
                return self.setTrueorFalse(True), None
        return self.setTrueorFalse(other.value in self.value), None
    
    def get_comparison_not_in(self, other):
        value = self.get_comparison_in(other)[0].value
        return self.setTrueorFalse(True if value == "false" else False), None
    
    def notted(self):
        value = self.value
        return self.setTrueorFalse(False if value == "true" else True), None

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't get index of {TypeOf(self.value).getType()}",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def get_element_at(self, index):
        return self.elements[index]

    def set_element_at(self, index, value):
        self.elements[index] = value
        return self

    def isSame(self, other):
        if isinstance(other, List):
            new_list = f'[{", ".join([str(x) for x in self.elements])}]'
            other_list = f'[{", ".join([str(x) for x in other.elements])}]'
            return new_list == other_list
        return False

    def length(self):
        return len(self.elements)

    def join(self, other):
        return List(self.elements + other.elements), None
   
    def copy(self):
        copy = List(self.elements)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy
    
    def __str__(self):
        try:
            if self.type == "split":
                return f'[{self.elements}]'
            else:
                return f'[{", ".join([str(x) for x in self.elements])}]'
        except:
            return f'{self.elements}'

    def __repr__(self):
        try:
            if self.type != None and self.type == "split":
                return f'{self.elements}'
            else:
                return f'[{", ".join([str(x) for x in self.elements])}]'
        except:
            return f'{self.elements}'


class Pair(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else ()
        self.value = self.elements
        self.id = self.elements

    def added_to(self, other):
        if isinstance(other, Pair):
            return Pair(self.elements + other.elements), None
        elif isinstance(other, String):
            new_pair = ()
            for char in other.value:
                new_pair += (String(char).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return Pair(self.elements + new_pair), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't add '{TypeOf(other.value).getType()}' to '{TypeOf(self.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation(error, other)

    def spread(self, other):
        if isinstance(other, Pair):
            return Pair(self.elements + other.elements), None
        elif isinstance(other, List):
            new_pair = ()
            for element in other.elements:
                new_pair += (element,)
            return Pair(self.elements + new_pair), None
        elif isinstance(other, String):
            new_pair = ()
            for char in other.value:
                new_pair += (String(char).setContext(self.context)
                             .setPosition(self.pos_start, self.pos_end))
            return Pair(self.elements + new_pair), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't add '{TypeOf(other.value).getType()}' to '{TypeOf(self.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation(error, other)
   
    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't subtract '{TypeOf(other.value).getType()}' from {TypeOf(self.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return List(new_list), None
            except:
                return None, "none"
        else:
            return None, self.illegal_operation(error, other)

    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"unsupported operation on 'pair' and '{TypeOf(other.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't multiply {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_pair = self.copy()
            new_pair = new_pair.elements * other.value
            return Pair(new_pair), None
        else:
            return None, self.illegal_operation(error, other)

    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None
    
    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None
    
    def get_comparison_lt(self, other):
        if isinstance(other, Pair):
            value = len(self.elements) < len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
    
    def get_comparison_gt(self, other):
        if isinstance(other, Pair):
            value = len(self.elements) > len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
     
    def get_comparison_lte(self, other):
        if isinstance(other, Pair):
            value = len(self.elements) <= len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'<=' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
    
    def get_comparison_gte(self, other):
        if isinstance(other, Pair):
            value = len(self.elements) >= len(other.elements)
            return self.setTrueorFalse(True if value else False), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"'>=' not supported between instances of '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
        
    def get_comparison_in(self, other):
        for element in self.elements:
            
            if other.isSame(element) if hasattr(other, "isSame") else other.value == element.value:
                return self.setTrueorFalse(True), None
        return self.setTrueorFalse(other.value in self.value), None
    
    def get_comparison_not_in(self, other):
        value = self.get_comparison_in(other)[0].value
        return self.setTrueorFalse(True if value == "false" else False), None
    
    def notted(self):
        value = self.value
        return self.setTrueorFalse(False if value == "true" else True), None

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't get index of {TypeOf(self.value).getType()}",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def get_element_at(self, index):
        return self.elements[index]

    def set_element_at(self, index, value):
        self.elements[index] = value
        return self
    
    def len(self):
        return Number(len(self.elements))

    def isSame(self, other):
        if isinstance(other, Pair):
            new_pair = f'[{", ".join([str(x) for x in self.elements])}]'
            other_pair = f'[{", ".join([str(x) for x in other.elements])}]'
            return new_pair == other_pair
        else:
            return False

    def copy(self):
        copy = Pair(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        try:
            return f'({", ".join([str(x) for x in self.elements])})'
        except:
            return "()"
        
        
class Dict(Value):
    def __init__(self, properties, keys=None, values=None):
        super().__init__()
        self.properties = properties
        self.keys = keys
        self.values = values
        self.value = self.properties
               
    def copy(self):
        copy = Dict(self.properties)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy
    
    def isSame(self, other):
        if isinstance(other, Dict):
            new_dict = f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
            other_dict = f"{{{', '.join([f'{k}: {v}' for k, v in other.properties.items()])}}}"
            return new_dict == other_dict
        return False
   
    def merge(self, other):
        if isinstance(other, Dict) or isinstance(other, Object):
            for key, value in other.properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        elif isinstance(other, Class):
            for key, value in other.methods_properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't merge '{TypeOf(self.value).getType()}' with '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
        
    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None
    
    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None
               
    def __repr__(self):
        try:
            return f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
        except:
            return f'{self.properties}'
    
   
class Object(Value):
    def __init__(self, name, properties, type=None):
        super().__init__()
        self.id = name
        self.name = name
        self.properties = properties if properties is not None else {}
        self.value = self.properties
        self.type = type
        self.get_property = self.get_property
       
    def set_property(self, key, value):
        self.properties[key] = value
        return self
    
    def get_property(self, obj, key):
        value = ""
        if type(key).__name__ == "String":
            if key.value in obj.properties:
                value = obj.properties[key.value]
                return value
            else:
                return NoneType.none
        return value
    
    def get_key(self, key):
        if key.value in self.properties:
            return self.properties[key.value]
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"Key '{key}' not found in {self.name}",
                'context': self.context,
                'exit': False
            }
        return None, self.key_error(error, key)
    
    def get_keys(self):
        keys = []
        for key in self.properties:
            keys.append(String(key))
        return keys
    
    def get_values(self):
        values = []
        for value in self.properties.values():
            values.append(value)
        return values
    
    def get_length(self):
        return len(self.properties)
    
    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on object",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                list_values = list(self.properties)
                return self.properties[list_values[other.value]], None
            except:
                return None, self.none_value()
        else:
            return None, self.illegal_operation(error, other)
            
    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None
    
    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None
         
    def isSame(self, other):
        if isinstance(other, Object):
            new_dict = f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
            other_dict = f"{{{', '.join([f'{k}: {v}' for k, v in other.properties.items()])}}}"
            return new_dict == other_dict
        return False

    def merge(self, other):
        if isinstance(other, Dict) or isinstance(other, Object):
            for key, value in other.properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        elif isinstance(other, Class):
            for key, value in other.methods_properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't merge '{TypeOf(self.value).getType()}' with '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
    
    def copy(self):
        copy = Object(self.name, self.properties)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    def __str__(self):
        try:
            if self.type == "module":
                return str(self.properties)
            return f"{{{','.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
        except:
            return "{}"
    
    def __repr__(self):
        return "<Object {}>".format(self.name)
        
        
class ObjectGet(Value):
    def __init__(self, obj, key):
        super().__init__()
        self.obj = obj
        self.key = key
        self.get_property = self.get_property
        self.value = self.get_property
        self.get_type = "ObjectGetNode"
        
    def get_property(self, obj, key):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Property '{key}' does not exist on object '{obj}'",
            'context': self.context,
            'exit': False
        }
        value  = ""
        if type(key).__name__ == "String":
            if hasattr(obj, "properties"):
                if key.value in obj.properties:
                    value = obj.properties[key.value]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
            
        elif type(key).__name__ == "Number":
            if hasattr(obj, "properties"):
                if str(key.value) in obj.properties:
                    value = obj.properties[str(key.value)]
                    return value
                else:
                    return NoneType.none
            else:
                return NoneType.none
        else:
            return None, self.illegal_operation(error, key)
  
    
class ObjectRefNode(Value):
    def __init__(self, value, arg=None):
        super().__init__()
        self.id = value
        self.value = value
        if arg:
            self.value = value + str(arg)

    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        if value:
            return Boolean(True)
        else:
            return Boolean(False)
    
    def copy(self):
        copy = ObjectRefNode(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"'{self.value}'"


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"
        self.value = self.name
        
  
    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbolTable = SymbolTable(new_context.parent.symbolTable)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()
        if len(args) > len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} argument(s) given, but {self.name if self.name != 'none' else 'anonymous'}() expects {len(arg_names)}",
                'context': self.context,
                'exit': False
            }))

        if len(args) < len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} few argument(s) given, but {self.name if self.name != 'none' else 'anonymous'}() expects {len(arg_names)}",
                'context': self.context,
                'exit': False
            }))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            exec_context.symbolTable.set(arg_name, arg_value)
            
    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)
   
    def isSame(self, other):
        if isinstance(other, BuiltInFunction):
            return self.name == other.name
        return False
   
        
class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, implicit_return, default_values, properties,context):
        super().__init__(name)
        self.id = name
        self.name = name
        self.body_node = body_node
        self.arg_names = arg_names
        self.implicit_return = implicit_return
        self.default_values = default_values
        self.properties = properties
        self.context = context
        
        
    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        self.args = args
        len_expected = None
        arg_giving = None
        if len(self.default_values) > 0:
            for i in range(len(self.default_values)):
                name = self.default_values[i]['name']
                value = res.register(interpreter.visit(self.default_values[i]['value'], exec_context))
                if res.should_return(): return res
                arg_giving = args
                if len(args) < len(self.arg_names):
                    if value not in args:
                        args.append(value)
                if len(args) <= i:
                    args.append(value)
                
        self.check_args(self.arg_names, args)
        self.populate_args(self.arg_names, args, exec_context)
        
        if res.should_return():
            return res
        
        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.func_return_value == None: return res
        return_value = (value if self.implicit_return else None) or res.func_return_value or NoneType.none
        # if hasattr(return_value, "value"):
        #     if return_value.value == "none":
        #         return_value.value = NoneType.none
        return res.success(return_value)

    # only class Function calls this method
    def run(self, args, class_name, context=None):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        if len(args) > 0:
            args = [class_name] + args
        if len(self.arg_names) == 1 and len(args) == 0:
            args = [class_name]
        
        
        self.args = args
        res.register(self.run_check_and_populate_args(
            self.arg_names, args, exec_context))
        if res.should_return():
            return res
        
        value = res.register(interpreter.visit(self.body_node, exec_context))
        
        if res.should_return() and res.func_return_value == None:
            return res
        return_value = (
            value if self.implicit_return else None) or res.func_return_value or NoneType.none
        # if hasattr(return_value, "value"):
        #     if return_value.value == "none":
        #         return res.success(None)
        return res.success(return_value)
    
    def run_check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.run_check_args(arg_names, args))
        if res.should_return(): return res
        self.run_populate_args(arg_names, args, exec_ctx)
        return res.success(None)
    
    def run_check_args(self, arg_names, args):
        res = RuntimeResult()
        
        if len(args) > len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args) -1} argument(s) given, but {self.name if self.name != 'none' else 'anonymous'}() expects {len(arg_names) - 1 if len(arg_names) > 0 else 0}",
                'context': self.context,
                'exit': False
            }))

        if len(args) < len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args) -1 if len(args) > 0 else 0} few argument(s) given, but {self.name if self.name != 'none' else 'anonymous'}() expects {len(arg_names) - 1 }",
                'context': self.context,
                'exit': False
            }))
        return res.success(None)
    
    def run_populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)
                     
                      
    def copy(self):
        copy = Function(self.name, self.body_node,
                    self.arg_names, self.implicit_return, self.default_values,self.properties,self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<Function {str(self.name) if self.name != 'none' else 'anonymous'}()>, {self.arg_names if len(self.arg_names) > 0 else '[no args]'}"


class ClassInstance:
    def __init__(self, klass:"Class"):
        self.klass = klass
    
    def __repr__(self):
        return f"<ClassInstance {str(self.klass.class_name)}>"


class Class(BaseFunction):
    def __init__(self, class_name, constructor_args, inherit_class_name, inherit_class, methods, context):
        super().__init__(class_name)
        self.id = class_name
        self.class_name = class_name
        self.constructor_args = constructor_args
        self.inherit_class_name = inherit_class_name
        self.inherit_class = inherit_class
        self.methods = methods
        self.methods_properties = methods if methods else {}
        self.value = self.methods_properties
        self.context = context
        self.body_node = None
        
        
    def execute(self, args):
        res = RuntimeResult()
        instance = ClassInstance(self)
        new_context = self.generate_new_context()
        class_args = dict({arg_name.value: arg_value for arg_name, arg_value in zip(self.constructor_args, args)}, **self.methods_properties)
        self.check_args(self.constructor_args, args)
        self.populate_args(self.constructor_args, args, self.context)
        if res.should_return(): return res
        if  self.methods_properties == {}:
            self.methods_properties = class_args
        else:
            for method_name, method in self.methods_properties.items():
                method.context = new_context
                method = method.copy()
                self.methods_properties[method_name] = method
                self.methods_properties = class_args
                
                # run init method if it exists
                if method_name == 'init':
                    method_args = method.arg_names
                    if len(method_args) == 1:
                        method_args = method_args[1:]
                    else:
                        return res.failure(Program.error()['Runtime']({
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"{method_name} method cannot have any arguments",
                            'context': self.context,
                            'exit': False
                        }))
                    res.register(method.run(method_args, self, new_context))
                    if res.should_return(): return res
        return res.success(self)
        
        
        
    def set_method(self, key, value):
        self.methods_properties[key] = value
        return self


    def get_method(self, method_name):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Method '{method_name}' does not exist on class '{self.class_name}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(method_name, String):
            result = []
            for key, value in self.properties:
                if key == method_name.value:
                    result.append(value)
                    if len(result) == 0:
                        return None, self.key_error(error, method_name)
                    return value, None
            return "none", self.key_error(error, method_name)

    
    def isSame(self, other):
        if isinstance(other, Class):
            _new_class = f"{{{', '.join([f'{k}: {v}' for k, v in self.methods_properties.items()])}}}"
            other_class = f"{{{', '.join([f'{k}: {v}' for k, v in other.methods_properties.items()])}}}"
            return _new_class == other_class
        return False

    def merge(self, other):
        if isinstance(other, Dict) or isinstance(other, Object):
            for key, value in other.properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        elif isinstance(other, Class):
            for key, value in other.methods_properties.items():
                if key.startswith("__"):
                    continue
                else:
                    self.properties[key] = value
            return Dict(self.properties), None
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't merge '{TypeOf(self.value).getType()}' with '{TypeOf(other.value).getType()}'",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error, other)
   
    def copy(self):
        copy = Class(self.class_name, self.constructor_args,
                     self.inherit_class_name, self.inherit_class, self.methods_properties, self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<Class {str(self.class_name)}>"
        

class ModuleObject(Value):
    def __init__(self, name, properties, type=None):
        super().__init__()
        self.id = name
        self.name = name
        self.properties = properties if properties is not None else {}
        self.value = self.properties
        self.type = type
        self.get_property = self.get_property

    def set_property(self, key, value):
        self.properties[key] = value
        return self

    def get_property(self, obj, key):
        value = ""
        if type(key).__name__ == "String":
            if key.value in obj.properties:
                value = obj.properties[key.value]
                return value
            else:
                return NoneType.none
        return value

    def get_key(self, key):
        if key.value in self.properties:
            return self.properties[key.value]
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"Key '{key}' not found in {self.name}",
                'context': self.context,
                'exit': False
            }
        return None, self.key_error(error, key)

    def get_keys(self):
        keys = []
        for key in self.properties:
            keys.append(String(key))
        return keys

    def get_values(self):
        values = []
        for value in self.properties.values():
            values.append(value)
        return values

    def get_length(self):
        return len(self.properties)

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on object",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                list_values = list(self.properties)
                return self.properties[list_values[other.value]], None
            except:
                return None, self.none_value()
        else:
            return None, self.illegal_operation(error, other)

    def get_comparison_eq(self, other):
        return Boolean(self.setTrueorFalse(self.value == other.value)), None

    def get_comparison_ne(self, other):
        return Boolean(self.setTrueorFalse(self.value != other.value)), None

    def get_comparison_lt(self, other):
        return Boolean(self.setTrueorFalse(self.value < other.value)), None

    def get_comparison_gt(self, other):
        return Boolean(self.setTrueorFalse(self.value > other.value)), None

    def get_comparison_lte(self, other):
        return Boolean(self.setTrueorFalse(self.value <= other.value)), None

    def get_comparison_gte(self, other):
        return Boolean(self.setTrueorFalse(self.value >= other.value)), None

    def copy(self):
        copy = ModuleObject(self.name, self.properties)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        try:
            if self.type == "module":
                return str(self.properties)
            return f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
        except:
            return "{}"

    def __repr__(self):
        return "<ModuleObject {}>".format(self.name)


class Module(Value):
    def __init__(self, name, path, context):
        super().__init__()
        self.id = name
        self.name = name
        self.path = path
        self.context = context
        self.setModule()
        
    def setModule(self):
        res = RuntimeResult()
        path = self.path+"\lib\http\main.alden"
        module = Program.runFile(path)
        context = self.context
        Program.createModule(self.name, module, self.path, context)
        self.value = context.symbolTable.get(self.name)
        if isinstance(self.value, Object):
            self.properties = self.value.properties
            if isinstance(self.value.properties, Class):
                self.properties = self.value.properties.methods_properties
        else:
            self.properties = {}
        return self.value
        
    def copy(self):
        copy = Module(self.name, self.path, self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<Module {str(self.name)}>"


class ModuleExportValue(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        
    def copy(self):
        copy = ModuleExportValue(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"<ModuleExportValue {str(self.name)}>"

   
class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RuntimeResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit)
        res.register(self.check_and_populate_args(
            method.arg_names, args, exec_context))
        if res.should_return():
            return res
        
        return_value = res.register(method(exec_context))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit(self, node, exec_context):
        res = RuntimeResult()
        return res.failure(Program.error()['Runtime']({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name} is not a supported built-in function",
            'context': self.context,
            'exit': False
        }))

    def execute_len(self, exec_context):
        res = RuntimeResult()
        value = exec_context.symbolTable.get("value")
        if isinstance(value, Number):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"type {TypeOf(value).getType()} is not supported",
                'context': self.context,
                'exit': False
            }))
        if isinstance(value, List):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, String):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, Pair):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, Object):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, NoneType):
            return res.success(Number(0).setPosition(self.pos_start, self.pos_end).setContext(self.context))
    execute_len.arg_names = ["value"]
    
    
    

    def execute_append(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        value = exec_context.symbolTable.get("value")
        if isinstance(list, List):
            list.elements.append(value)
            return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'append' must be a list.",
                'context': self.context,
                'exit': False
            }))
    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        index = exec_context.symbolTable.get("index")
        if isinstance(list, List):
            try:
                list.elements.pop(index.value)
                return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
            except:
                return res.failure(Program.error()['Runtime']({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"Element at index {index.value} could not be removed from list because index is out of bounds",
                    'context': self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'pop' must be a list.",
                'context': self.context,
                'exit': False
            }))
    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_context):
        res = RuntimeResult()
        list = exec_context.symbolTable.get("list")
        value = exec_context.symbolTable.get("value")
        if isinstance(list, List):
            list.elements.extend(value.value)
            return res.success(List(list.elements).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'extend' must be a list.",
                'context': self.context
            }))
    execute_extend.arg_names = ["list", "value"]

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<{str(self.name)}()>, [ built-in function ]"


# Built-in functions

def BuiltInFunction_Print(args, node):
    res = RuntimeResult()
    for arg in args:
        value = str(arg)
        if isinstance(arg, String):
            value = arg.value
        try:
            if value[0] == "'":
                value = value[1:-1]
        except:
            pass
        sys.stdout.write(value)
    return res.noreturn()


def BuiltInFunction_PrintLn(args, node):
    res = RuntimeResult()
    for arg in args:
        value = str(arg)
        if isinstance(arg, String):
            value = arg.value
        try:
            if value[0] == "'":
                value = value[1:-1]
        except:
            pass
        sys.stdout.write(value + "\n")
    return res.success(None) 


def BuiltInFunction_Input(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but input() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = input()
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
    if len(args) == 1:
        if isinstance(args[0], String):
            try:
                input_value = input(args[0].value)
            except KeyboardInterrupt:
                return res.failure("KeyboardInterrupt")
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0]} is not a valid argument for input()",
                "context": context,
                'exit': False
            }))


def BuiltInFunction_InputInt(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputInt() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = int(input())
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
        return res.success(Number(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = int(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
                except KeyboardInterrupt:
                    return res.failure("KeyboardInterrupt")
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputInt()",
                "context": context,
                'exit': False
            }))


def BuiltInFunction_InputFloat(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputFloat() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        try:
            input_value = float(input())
        except KeyboardInterrupt:
            return res.failure("KeyboardInterrupt")
        return res.success(Number(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = float(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
                except KeyboardInterrupt:
                    return res.failure("KeyboardInterrupt")
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputFloat()",
                "context": context,
                'exit': False
            }))


def BuiltInFunction_InputBool(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputBool() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        input_value = bool(input())
        return res.success(Boolean(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
    if len(args) == 1:
        if isinstance(args[0], String):
            while True:
                text = input(args[0].value)
                try:
                    number = bool(text)
                    break
                except ValueError:
                    print("Invalid input, please try again")
                except KeyboardInterrupt:
                    return res.failure("KeyboardInterrupt")
            return res.success(Boolean(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for inputBool()",
                "context": context,
                'exit': False
            }))


def BuiltInFunction_Str(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but str() takes 1 argument",
            "context": context,
            'exit': False
        }))
    return res.success(String(str(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    
def BuiltInFunction_Range(args, node, context):
    res = RuntimeResult()
    # built in range takes 1 or 3 arguments eg range(5) or range(1, 5) or range(1, 5, 2)
    #print(args)
    if len(args) not in [1, 3]:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but range() takes 1 or 3 arguments",
            "context": context,
            'exit': False
        }))
    if len(args) == 1:
        if isinstance(args[0], Number):
            return res.success(Number(range(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0].value} is not a valid argument for range()",
            "context": context,
            'exit': False
        }))


def BuiltInFunction_Int(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but int() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for int()",
                "context": context,
                'exit': False
            }))
    if isinstance(args[0], Boolean):
        return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for int()",
        "context": context,
        'exit': False
    }))


def BuiltInFunction_Float(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but float() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for float()",
                "context": context,
                'exit': False
            }))
    if isinstance(args[0], Boolean):
        return res.success(Number(float(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    return res.failure(Program.error()["TypeError"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for float()",
        "context": context,
        'exit': False
    }))


def BuiltInFunction_Bool(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but bool() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Boolean):
        print(args[0])
        return res.success(args[0])
    if isinstance(args[0], Number):
        return res.success(Boolean(bool(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    if isinstance(args[0], String):
        try:
            return res.success(Boolean(bool(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except ValueError:
            return res.failure(Program.error()["TypeError"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid argument for bool()",
                "context": context,
                'exit': False
            }))
    return res.failure(Program.error()["Runtime"]({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"{args[0].value} is not a valid argument for bool()",
        "context": context,
        'exit': False
    }))


def BuiltInFunction_List(args, node, context):
    res = RuntimeResult()
    if len(args) != 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but list() takes 1 argument",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], List):
        return res.success(args[0])
    elif isinstance(args[0], String):
        new_list = []
        for char in args[0].value:
            new_list.append(String(char).setPosition(node.pos_start, node.pos_end).setContext(context))
        return res.success(List(new_list).setPosition(node.pos_start, node.pos_end).setContext(context))
    elif isinstance(args[0], Boolean):
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
    elif isinstance(args[0], Object):
        keys = [key for key in args[0].value]
        values = [args[0].value[key] for key in keys]
        new_list = []
        for value in values:
            new_list.append(value)
        return res.success(List(new_list).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    elif isinstance(args[0], Dict):
        keys = [key for key in args[0].value]
        values = [args[0].value[key] for key in keys]
        new_list = []
        for value in values:
            new_list.append(value)
        return res.success(List(new_list).setPosition(node.pos_start, node.pos_end).setContext(context))
   
    else: 
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
   

def BuiltInFunction_Pair(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but pair() takes 1 argument",
            "context": context,
            'exit': False
        }))
       
    if isinstance(args[0], Pair):
        return res.success(args[0])
    
    elif isinstance(args[0], String):
        new_pair = ()
        for char in args[0].value:
            new_pair += (String(char).setPosition(node.pos_start, node.pos_end).setContext(context),)
        return res.success(Pair(new_pair).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    elif isinstance(args[0], List):
        new_pair = ()
        for value in args[0].value:
            new_pair += (value,)
        return res.success(Pair(new_pair).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    elif isinstance(args[0], Object):
        keys = [key for key in args[0].value]
        values = [args[0].value[key] for key in keys]
        new_pair = ()
        for value in values:
            new_pair += (value,)
        return res.success(Pair(new_pair).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    elif isinstance(args[0], Dict):
        keys = [key for key in args[0].value]
        values = [args[0].value[key] for key in keys]
        new_pair = ()
        for value in values:
            new_pair += (value,)
        return res.success(Pair(new_pair).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))


def BuiltInFunction_Object(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but object() takes 1 argument",
            "context": context,
            'exit': False
        }))
    
    if isinstance(args[0], Object):
        return res.success(args[0])
    
    if isinstance(args[0], Number):
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
 
 
def BuiltInFunction_Max(args, node, context):
    res = RuntimeResult()
    if len(args) > 2:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but max() takes 2 arguments",
            "context": context,
            'exit': False
        }))
        
    if isinstance(args[0], Number) and isinstance(args[1], Number):
        return res.success(Number(max(args[0].value, args[1].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
  

def BuiltInFunction_Min(args, node, context):
    res = RuntimeResult()
    if len(args) > 2:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but min() takes 2 arguments",
            "context": context,
            'exit': False
        }))
        
    if isinstance(args[0], Number) and isinstance(args[1], Number):
        return res.success(Number(min(args[0].value, args[1].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))  


def BuiltInFunction_Sorted(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but sort() takes 1 argument",
            "context": context,
            'exit': False
        }))
        
    if isinstance(args[0], List):
        new_elements = []
        elements = args[0].elements
        for element in elements:
            if hasattr(element, 'value'):
                new_elements.append(element.value)
            else:
                new_elements.append(element)
        is_sorted = sorted(new_elements)
        return res.success(List(is_sorted).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
   

def BuiltInFunction_Substr(args, node, context):
    res = RuntimeResult()
    if len(args) > 3:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but substr() takes 3 arguments",
            "context": context,
            'exit': False
        }))
    
    elif len(args) == 2:
        if isinstance(args[0], String) and isinstance(args[1], Number):
            start = args[1].value
            end = len(args[0].value)
            return res.success(String(getsubstr(args[0].value, start, end)).setPosition(node.pos_start, node.pos_end).setContext(context))
        
        
    elif len(args) == 3:
        if isinstance(args[0], String) and isinstance(args[1], Number) and isinstance(args[2], Number):
            start = args[1].value
            length = args[2].value
            return res.success(String(getsubstr(args[0].value, start, start + length)).setPosition(node.pos_start, node.pos_end).setContext(context))
    
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))


def BuiltInFunction_Reverse(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but reverse() takes 1 argument",
            "context": context,
            'exit': False
        }))
        
    if isinstance(args[0], List):
        new_elements = []
        elements = args[0].elements
        for element in elements:
            if hasattr(element, 'value'):
                new_elements.append(element.value)
            else:
                new_elements.append(element)
        new_elements.reverse()
        return res.success(List(new_elements).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        }))
   
    
def BuiltInFunction_Format(args, node):
    string = args[0].value
    values_list = args[1].value
    regex = Regex().compile('{(.*?)}')
    matches = regex.match(string)
  

def BuiltInFunction_Typeof(args, node, context):
    res = RuntimeResult()
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but typeof() takes 1 argument",
            "context": context,
            'exit': False
        }))
        
    if len(args) == 0:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"typeof() takes 1 argument",
            "context": context,
            'exit': False
        }))
    return res.success(String(TypeOf(args[0]).getType()).setPosition(node.pos_start, node.pos_end).setContext(context))


def BuiltInFunction_IsinstanceOf(args, node, context):
    res = RuntimeResult()
    if len(args) > 2:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but isinstance() takes 2 arguments",
            "context": context,
            'exit': False
        }))
        
    if len(args) == 0:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"isinstance() takes 2 arguments",
            "context": context,
            'exit': False
        }))
        
        
    def  getInstance(type1, type2):
            getType = type2.getType()
            
            if isinstance(type1, Number) and getType == "Number":
                     return True
            if isinstance(type1, String) and getType == "String":
                    return True
            if isinstance(type1, Boolean) and getType == "Boolean":
                    return True
            if isinstance(type1, NoneType) and getType == "NoneType":
                    return True
            if isinstance(type1, List) and getType == "List":
                    return True
            if isinstance(type1, Pair) and getType == "Pair":
                    return True
            if isinstance(type1, Dict) and getType == "Dict":
                    return True
            if isinstance(type1, Object) and getType == "Object":
                    return True
            if isinstance(type1, Class) and getType == "Class":
                    return True
            if isinstance(type1, Function) and getType == "Function":
                    return True
            if isinstance(type1, BuiltInFunction) and getType == "BuiltInFunction":
                    return True
            if isinstance(type1, BuiltInMethod) and getType == "BuiltInMethod":
                    return True
            else:
                    return False
   
    if not isinstance(args[1], Types):
        return res.failure(Program.error()["TypeError"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"isisnstance() argument 2 must be a type",
            "context": context,
            'exit': False
        }))
    else:
        return res.success(Boolean(getInstance(args[0], args[1])).setPosition(node.pos_start, node.pos_end).setContext(context))


def BuiltInFunction_Line(args, node, context):
    res = RuntimeResult()
    if len(args) == 0:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"line() takes at least 1 argument",
            "context": context,
            'exit': False
        }))
    if len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but line() takes 1 argument",
            "context": context,
            'exit': False
        }))
        
    if isinstance(args[0], Number):
        print(f"{args[0].value}:-> ")
        
    elif isinstance(args[0], String):
        print(f"{args[0].value}:-> ")
    
    else:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0].value} is not a valid argument for line()",
            "context": context,
            'exit': False
        }))

    
def BuiltInFunction_Clear(args, node, context):
    res = RuntimeResult()
    if len(args) > 0:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but clear() takes no argument",
            "context": context,
            'exit': False
        }))
    if len(args) == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        return res.success(None)
   
    
def BuiltInFunction_Delay(args, node, context):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but delay() takes 1 argument",
            "context": context,
            'exit': False
        }))

    if isinstance(args[0], Number):
        time.sleep(args[0].value)
        return res.success(None)
    else:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0].value} is not a valid argument for delay()",
            "context": context,
            'exit': False
        }))
 
    
def BuiltInFunction_Exit(args, node, context):
    res = RuntimeResult()
    if len(args) == 0:
        sys.exit()
    elif len(args) > 1:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but exit() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        }))
    if isinstance(args[0], Number):
        if args[0].value == 0:
            sys.exit(0)
        elif args[0].value == 1:
            sys.exit(1)
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid exit code",
                "context": context,
                'exit': False
            }))
    else:
        return res.failure(Program.error()["Runtime"]({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{args[0]} is not a valid argument for exit()",
            "context": context,
            'exit': False
        }))



def BuiltInFunction_Http_Get():
    print(f"I got")


# Built-in methods 

class BuiltInMethod(Value):
    def __init__(self, value, arg=None):
        super().__init__()
        self.value = value
        self.id = value
         
            
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        if value:
            return Boolean(True)
        else:
            return Boolean(False)
    
    def copy(self):
        copy = BuiltInMethod(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
        
    def __repr__(self):
        return f"'{self.value}'"
    
    
class BuiltInMethod_String(Value):
    def __init__(self, type, name, args, node, context):
        super().__init__()
        self.type = type
        self.name = name
        self.value = name
        self.args = args
        self.node = node
        self.context = context
        self.execute()
        
    def execute(self):
        res = RuntimeResult()
        if self.type in string_methods:
            method = f"BuiltInMethod_{string_methods[self.type]}"
            is_method = getattr(self, method, self.no_method)
            value = is_method()
            self.name = value
            if type(self.name).__name__ == "RuntimeResult":
                self.name = ''
        return self.name
    
    
    def no_method(self):
        return RuntimeResult().failure(Program.error()["Runtime"]({
            "pos_start": self.node.pos_start,
            "pos_end": self.node.pos_end,
            'message': f"{self.type} is not a valid method",
            "context": self.context,
            'exit': False
        }))
    
   
    def BuiltInMethod_upperCase(self):
        res = RuntimeResult()
        if len(self.args) != 0:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but UpperCase() takes no argument",
                "context": self.context,
                'exit': False
            }))
        else:
            return String(self.name.value.upper()).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
    
    
    def BuiltInMethod_lowerCase(self):
        res = RuntimeResult()
        if len(self.args) != 0:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but LowerCase() takes no argument",
                "context": self.context,
                'exit': False
            }))
        else:
            return String(self.name.value.lower()).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        
        
    def BuiltInMethod_capitalize(self):
        res = RuntimeResult()
        if len(self.args) != 0:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but Capitalize() takes no argument",
                "context": self.context,
                'exit': False
            }))
        else:
            return String(self.name.value.capitalize()).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
    
        
    def BuiltInMethod_strip(self):
        res = RuntimeResult()
        if len(self.args) != 0:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but strip() takes no argument",
                "context": self.context,
                'exit': False
            }))
        else:
            return String(string_strip(self.name.value)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
    
    
    def BuiltInMethod_split(self):
        res = RuntimeResult()
        if len(self.args) == 0:
            value = []
            split_list = self.name.value.split()
            for i in split_list:
                value.append(String(i).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end))
            return List(value).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        elif len(self.args) == 1:
            if isinstance(self.args[0], String):
                if self.args[0].value == " ":
                    value = []
                    split_list = self.name.value.split()
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end))
                    return List(value).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                elif self.args[0].value == "":
                    value = []
                    split_list = self.name.value.split()
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end))
                    return List(value).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                else:
                    value = []
                    split_list = self.name.value.split(self.args[0].value)
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end))
                    return List(value).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for split()",
                    "context": self.context,
                    'exit': False
                }))
        elif len(self.args) == 2:
            if isinstance(self.args[0], String) and isinstance(self.args[1], Number):
                if self.args[1].value < 0:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": self.node.pos_start,
                        "pos_end": self.node.pos_end,
                        'message': f"{self.args[1].value} is not a valid argument for split()",
                        "context": self.context,
                        'exit': False
                    }))
                else:
                    value = []
                    split_list = self.name.value.split(self.args[0].value, self.args[1].value)
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end))
                    return List(value).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' and '{TypeOf(self.args[1]).getType()}' are not a valid arguments for split()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but split() takes 1 or 2 arguments",
                "context": self.context,
                'exit': False
            }))
    
   
    def BuiltInMethod_join(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], List):
                try:
                    return String(self.name.value.join([x.value for x in self.args[0].elements])).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                except:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": self.node.pos_start,
                        "pos_end": self.node.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(self.args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    }))
            elif isinstance(self.args[0], Pair):
                try:
                    return String(self.name.value.join([x.value for x in self.args[0].elements])).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                except:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": self.node.pos_start,
                        "pos_end": self.node.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(self.args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    }))
            elif isinstance(self.args[0], Object):
                try:
                    return String(self.name.value.join([x.value for x in self.args[0].get_keys()])).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                except:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": self.node.pos_start,
                        "pos_end": self.node.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(self.args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    }))
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for join()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but join() takes 1 argument",
                "context": self.context,
                'exit': False
            }))
    
    
    def BuiltInMethod_replace(self):
        res = RuntimeResult()
        if isinstance(self.name, BuiltInMethod_String):
            print(self.name.value, "replace")
        if len(self.args) == 2:
            if isinstance(self.args[0], String) and isinstance(self.args[1], String):
                return String(self.name.value.replace(self.args[0].value, self.args[1].value)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' and '{TypeOf(self.args[1]).getType()}' are not a valid arguments for replace()",
                    "context": self.context,
                    'exit': False
                }))
        elif len(self.args) == 3:
            if isinstance(self.args[0], String) and isinstance(self.args[1], String) and isinstance(self.args[2], Number):
                return String(self.name.value.replace(self.args[0].value, self.args[1].value, self.args[2].value)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}', '{TypeOf(self.args[1]).getType()}' and '{TypeOf(self.args[2]).getType()}' are not a valid arguments for replace()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but replace() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))
    
   
    def BuiltInMethod_length(self):
        res = RuntimeResult()
        return res.failure(Program.error()["Runtime"]({
            "pos_start": self.node.pos_start,
            "pos_end": self.node.pos_end,
            'message': f"'length' is not a callable",
            "context": self.context,
            'exit': False
        }))
   
   
    def BuiltInMethod_substr(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], Number):
                start = self.args[0].value
                end = len(self.name.value)
                return String(getsubstr(self.name.value, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for substr()",
                    "context": self.context,
                    'exit': False
                }))
        elif len(self.args) == 2:
            if isinstance(self.args[0], Number) and isinstance(self.args[1], Number):
                start = self.args[0].value
                end = self.args[1].value + 1
                return String(getsubstr(self.name.value, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' and '{TypeOf(self.args[1]).getType()}' are not a valid arguments for substr()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but substr() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))
 
    
    def BuiltInMethod_slice(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], Number):
                start = self.args[0].value
                end = len(self.name.value)
                return String(getsubstr(self.name.value, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for slice()",
                    "context": self.context,
                    'exit': False
                }))
        elif len(self.args) == 2:
            if isinstance(self.args[0], Number) and isinstance(self.args[1], Number):
                start = self.args[0].value
                end = self.args[1].value + 1
                return String(getsubstr(self.name.value, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' and '{TypeOf(self.args[1]).getType()}' are not a valid arguments for slice()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but slice() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))
    
    
    def BuiltInMethod_charAt(self):
        res = RuntimeResult()
        if len(self.args) == 0:
            string = self.name.value.replace(" ", "")
            start = 0
            end = 1
            return String(getsubstr(string, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        if len(self.args) == 1:
            if isinstance(self.args[0], Number):
                string = self.name.value.replace(" ", "")
                start = self.args[0].value
                end = start + 1
                return String(getsubstr(string, start, end)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for charAt()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but charAt() takes 1 argument",
                "context": self.context,
                'exit': False
            }))
    
    
    def BuiltInMethod_includes(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], String):
                string = self.name.value.replace(" ", "")
                substring = self.args[0].value.replace(" ", "")
                return Boolean(string.find(substring) != -1).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for includes()",
                    "context": self.context,
                    'exit': False
                }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but includes() takes 1 argument",
                "context": self.context,
                'exit': False
            }))
    
    
    def copy(self):
        copy = BuiltInMethod_String(
            self.type, self.name, self.args, self.node, self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy
    
    
    
    def __str__(self):
        return f"{self.name}"
    
    
    
    def repr(self):
        return f"<{str(self.type)}()>, [ built-in string method ]"


class BuiltInMethod_List(Value):
    def __init__(self, type, name, args, node, context):
        super().__init__()
        self.type = type
        self.name = name
        self.args = args
        self.node = node
        self.context = context
        self.execute()
    
    def execute(self):
        res = RuntimeResult()
        if self.type in list_methods:
            method = f"BuiltInMethod_{list_methods[self.type]}"
            is_method = getattr(self, method, self.no_method)
            value = is_method()
            self.name = value
            if type(self.name).__name__ == "RuntimeResult":
                self.name = ''
        return self.name
    
    
    def no_method(self):
        return RuntimeResult().failure(Program.error()["Runtime"]({
        "pos_start": self.node.pos_start,
        "pos_end": self.node.pos_end,
        'message': f"{self.type} is not a valid method",
        "context": self.context,
        'exit': False
    }))
            
    
    def BuiltInMethod_length(self):
        res = RuntimeResult()
        return res.failure(Program.error()["Runtime"]({
            "pos_start": self.node.pos_start,
            "pos_end": self.node.pos_end,
            'message': f"'length' is not a callable",
            "context": self.context,
            'exit': False
        }))
        
    
    def BuiltInMethod_append(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            self.name.elements.append(self.args[0])
            return NoneType('none').none
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for append()",
                "context": self.context,
                'exit': False
            }))
    
            
    def BuiltInMethod_pop(self):
        res = RuntimeResult()
        if len(self.args) == 0:
             return List(self.name.elements.pop()).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)  
        elif len(self.args) == 1:
            if isinstance(self.args[0], Number):
                    return List(self.name.elements.pop(self.args[0].value)).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for pop()",
                    "context": self.context,
                    'exit': False
                }))
                
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but pop() takes 0 or 1 arguments",
                "context": self.context,
                'exit': False
            }))
     
            
    def BuiltInMethod_remove(self):
        res = RuntimeResult()
        if len(self.args) == 1:
           return List(self.name.elements.remove(self.args[0])).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)  
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but remove() takes 1 argument",
                "context": self.context,
                'exit': False
            }))
            
            
    def BuiltInMethod_insert(self):
        res = RuntimeResult()
        if len(self.args) == 2:
            return List(self.name.elements.insert(self.args[0], self.args[1])).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but insert() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))
            
            
    def BuiltInMethod_reverse(self):
        res = RuntimeResult()
        if len(self.args) == 0:
            new_list = []
            for el in self.name.elements:
                new_list.insert(0, el)
            return List(new_list).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but reverse() takes 0 arguments",
                "context": self.context,
                'exit': False
            }))
   
            
    def BuiltInMethod_empty(self):
        res = RuntimeResult()
        if len(self.args) == 0:
            return List(self.name.elements.clear()).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end) 
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but empty() takes 0 arguments",
                "context": self.context,
                'exit': False
            }))


    def BuiltInMethod_getItem(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], Number):
                    return List(self.name.elements[self.args[0].value]).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for getItem()",
                    "context": self.context,
                    'exit': False
                }))
                
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but getItem() takes 1 argument",
                "context": self.context,
                'exit': False
            }))


    def BuiltInMethod_setItem(self):
        res = RuntimeResult()
        if len(self.args) == 2:
            if isinstance(self.args[0], Number):
                    old_value = self.name.elements[self.args[0].value]
                    new_value = self.args[1]
                    self.name.elements[self.args[0].value] = new_value
                    return List(self.name.elements).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for setItem()",
                    "context": self.context,
                    'exit': False
                }))
                
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but setItem() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))


    def BuiltInMethod_slice(self):
        res = RuntimeResult()
        if len(self.args) == 2:
            if isinstance(self.args[0], Number) and isinstance(self.args[1], Number):
                    return List(self.name.elements[self.args[0].value:self.args[1].value]).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' and '{TypeOf(self.args[1]).getType()}' are not valid arguments for slice()",
                    "context": self.context,
                    'exit': False
                }))
        elif len(self.args) == 1:
            if isinstance(self.name, List):
                if isinstance(self.args[0], Number):
                    return List(self.name.elements[self.args[0].value:]).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                else:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": self.node.pos_start,
                        "pos_end": self.node.pos_end,
                        'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for slice()",
                        "context": self.context,
                        'exit': False
                    }))
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but slice() takes 2 arguments",
                "context": self.context,
                'exit': False
            }))
        
        
    def BuiltInMethod_join(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], String):
                    new_string = ""
                    for element in self.name.elements:
                        if type(element.value) == str:
                            new_string += element.value
                        else:
                            new_string += str(element.value)
                        if element != self.name.elements[-1]:
                            new_string += self.args[0].value
                    return String(new_string).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            else:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": self.node.pos_start,
                    "pos_end": self.node.pos_end,
                    'message': f"type '{TypeOf(self.args[0]).getType()}' is not a valid argument for join()",
                    "context": self.context,
                    'exit': False
                }))
                
        elif len(self.args) == 0:
            new_string = ""
            for element in self.name.elements:
                if type(element.value) == str:
                    new_string += element.value
                else:
                    new_string += str(element.value)
                if element != self.name.elements[-1]:
                    new_string += ","
            return String(new_string).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but join() takes 1 argument",
                "context": self.context,
                'exit': False
            }))
        
    
    def BuiltInMethod_includes(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            new_list = []
            for element in self.name.elements:
                if hasattr(element, "value"):
                    new_list.append(element.value)
                elif hasattr(element, "elements"):
                    new_list.append(element.elements)
                elif hasattr(element, "name"):
                    new_list.append(element.name)
                elif hasattr(element, "methods_properties"):
                    new_list.append(element.methods_properties)
                elif hasattr(element, "properties"):
                    new_list.append(element)
                else:
                    new_list.append(element)
                    
            if isinstance(self.args[0], String) or isinstance(self.args[0], Number):
                if self.args[0].value in new_list:
                    return Boolean(True).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                else:
                    return Boolean(False).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            elif isinstance(self.args[0], BuiltInFunction):
                if self.args[0].name in new_list:
                    return Boolean(True).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
                else:
                    return Boolean(False).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
            elif isinstance(self.args[0], Dict):
                isSame = False
                for element in new_list:
                    if isinstance(element, Dict):
                        isSame = element.isSame(self.args[0])
                        
                return Boolean(isSame).setContext(self.context).setPosition(self.node.pos_start, self.node.pos_end)
        else:
            return res.failure(Program.error()["Runtime"]({
                "pos_start": self.node.pos_start,
                "pos_end": self.node.pos_end,
                'message': f"{len(self.args)} arguments given, but includes() takes 1 argument",
                "context": self.context,
                'exit': False
            }))


class Types(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.getType()
        
    def getType(self):
        res = RuntimeResult()
        data_types = {
            'Number': Number,
            'String': String,
            'Boolean': Boolean,
            'NoneType': NoneType,
            'List': List,
            'Pair': Pair,
            'Dict': Dict,
            'Object': Object,
            'Class': Class,
            'Function': Function,
            'BuiltInFunction': BuiltInFunction,
            'BuiltInMethod': BuiltInMethod
        }
        self.type = data_types[self.name]
        return self.type.__name__
    
    
    def copy(self):
        copy = Types(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy
    
    def __repr__(self):
        return f"<Class {self.name}>"


class BuiltInMethod_Number(Value):
    def __init__(self, type, name, args, node, context):
        super().__init__()
        self.type = type
        self.name = name
        self.args = args
        self.node = node
        self.context = context
        self.execute()
        
        
    def execute(self):
        res = RuntimeResult()
        if self.type in number_methods:
            method = f"BuiltInMethod_{number_methods[self.type]}"
            is_method = getattr(self, method, self.no_method)
            value = is_method()
            self.name = value
            if type(self.name).__name__ == "RuntimeResult":
                self.name = ''
        return self.name

    
# Built-in modules
 
def BuiltInModule_Http(context):
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return Module("http", module_path, context)
 
 
 
class Interpreter:
    
    def __init__(self):
        self.error_detected = False
    
    
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit)
        return method(node, context)

    
    def no_visit(self, node, context):
        return RuntimeResult().success(NoneType.none)


    def visit_StatementsNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)
        return res.success(Statement(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(
            Number(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )


    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.tok.value, node.arg).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )


    def visit_ObjectRefNode(self, node, context):
        return RuntimeResult().success(
            ObjectRefNode(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

    
    def visit_StringInterpNode(self, node, context):
        res = RuntimeResult()
        values_to_replace = node.values_to_replace
        string_to_interp = res.register(self.visit(node.expr, context)).value
        inter_pv = node.inter_pv
        value = ""
        try:
            if isinstance(values_to_replace, list):
                for pv in range(len(inter_pv)):
                    replace_value = res.register(self.visit(values_to_replace[pv], context))
                    value_replaced = str(replace_value)
                    if isinstance(replace_value, String):
                        value_replaced = str(replace_value.value)
                    if value_replaced[0] == "'":
                        value_replaced = str(value_replaced[1:-1])
                    if value_replaced == "None":
                        value_replaced = str(NoneType.none)
                    # replace placeholder with value
                    string_to_interp = string_to_interp.replace(
                        '%{' + str(inter_pv[pv]) + '}', value_replaced)
                    if '%%{{' in string_to_interp and '}}' in string_to_interp:
                        string_to_interp = string_to_interp.replace(
                            '%%{{' + str(inter_pv[pv]) + '}}', '%{' + str(value_replaced) + '}')
                    elif '{{' in string_to_interp and '}}' in string_to_interp:
                        string_to_interp = string_to_interp.replace(
                            '%{{' + str(inter_pv[pv]) + '}}', '{' + str(value_replaced) + '}')
                    value = String(string_to_interp).setContext(
                        context).setPosition(node.pos_start, node.pos_end)
            else:
                string = values_to_replace
                value = String(string).setContext(context).setPosition(node.pos_start, node.pos_end)
                
            if value:
                return res.success(value)
            else:
                res.noreturn()
        except:
            pass
    
    
    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements.append(element_value)
        return res.success(List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_BooleanNode(self, node, context):
        return RuntimeResult().success(
            Boolean(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )
    
   
    def visit_NoneNode(self, node, context):
        return RuntimeResult().success(
            NoneType('none').setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )
        
   
    def visit_PairNode(self, node, context):
        res = RuntimeResult()
        elements = ()
        for element_node in node.elements:
            element_value = res.register(self.visit(element_node, context))
            if res.should_return():
                return res
            elements = elements + (element_value,)
        return res.success(Pair(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    
    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.variable_name_token.value if type(
            node.variable_name_token).__name__ != 'tuple' and type(
            node.variable_name_token).__name__ != 'list' else ''
        if type(node.variable_name_token).__name__ == 'tuple':
            if type(node.variable_name_token[0]).__name__ == 'Token':
                var_name = node.variable_name_token[0].value
            elif type(node.variable_name_token[0]).__name__ == 'VarAccessNode':
                var_name = node.variable_name_token[0].id.value
        if type(node.variable_name_token).__name__ == 'list':
            for element in node.variable_name_token:
                if type(element).__name__ == 'Token':
                    var_name = var_name + element.value
                elif type(element).__name__ == 'VarAccessNode':
                    var_name = var_name + element.id.value
        value = res.register(self.visit(node.value_node, context))
        
        if node.variable_keyword_token == "module":
            value = context.symbolTable.get(node.value_node.value)
            if value == None:
               return res.failure(Program.error()['NameError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"name '{node.value_node.value}' is not defined",
                    'context': context,
                    'exit': False
                }))
        
        if type(node.variable_name_token).__name__ == "tuple" or type(node.variable_name_token).__name__ == "list":
            var_name = node.variable_name_token
            if isinstance(var_name, Pair) or isinstance(var_name, List):
                if len(var_name) != len(value.elements):
                    return res.failure(Program.error()['ValueError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"Expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                        'context': context,
                        'exit': False
                    }))
                else:
                    for i in range(len(var_name)):
                        context.symbolTable.set(
                            var_name[i].name.value, value.elements[i])

            elif isinstance(value, Object) or isinstance(value, Dict):
                if isinstance(value, Dict):
                    for key in list(value.properties.keys()):
                        if key == '__properties':
                            del value.properties[key]

                if len(var_name) != len(value.properties):
                    var = []
                    for v in var_name:
                        if type(v).__name__ != "VarAccessNode" and type(v).__name__ != "StringNode":
                            return res.failure(Program.error()['ValueError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"Cannot pair {TypeOf(value).getType()} with {TypeOf(v).getType()}",
                                'context': context,
                                'exit': False
                            }))
                        var.append(v.name.value)
                    if '*' + v.name.value.split('*')[-1] in var:
                        properties = []
                        for prop in value.properties.values():
                            properties.append(prop)
                        for i in range(len(var_name)):
                            if i < len(var_name) - 1:
                                context.symbolTable.set(
                                    var_name[i].name.value, properties[i])
                            else:
                                context.symbolTable.set(v.name.value.split(
                                    '*')[-1], List(properties[i:]))

                    else:
                        return res.failure(Program.error()['ValueError']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"Expected {len(value.properties)} values, unable to pair {len(var_name)} value(s)",
                            'context': context,
                            'exit': False
                        }))
                else:
                    properties = []
                    var = []
                    for prop in value.properties.values():
                        properties.append(prop)
                    for v in var_name:
                        var.append(v.name.value)
                        if '*' + v.name.value.split('*')[-1] in var:
                            return res.failure(Program.error()['ValueError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"not to many values to pair",
                                'context': context,
                                'exit': False
                            }))
                        else:
                            for i in range(len(var_name)):
                                context.symbolTable.set(
                                    var_name[i].name.value, properties[i])

            elif isinstance(value, Pair) or isinstance(value, List):
                if len(var_name) != len(value.elements):
                    var = []
                    for v in var_name:
                        if type(v).__name__ != "VarAccessNode" and type(v).__name__ != "StringNode":
                            return res.failure(Program.error()['ValueError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"Cannot pair {TypeOf(value).getType()} with {TypeOf(v).getType()}",
                                'context': context,
                                'exit': False
                            }))
                        var.append(v.name.value)
                    if '*' + v.name.value.split('*')[-1] in var:
                        elements = []
                        for elem in value.elements:
                            elements.append(elem)
                        for i in range(len(var_name)):
                            if i < len(var_name) - 1:
                                context.symbolTable.set(
                                    var_name[i].name.value, elements[i])
                            else:
                                context.symbolTable.set(
                                    v.name.value.split('*')[-1], List(elements[i:]))
                    else:
                        return res.failure(Program.error()['ValueError']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"Expected {len(value.elements)} values, unable to pair {len(var_name)} value(s)",
                            'context': context,
                            'exit': False
                        }))
                else:
                    elements = []
                    var = []
                    for elem in value.elements:
                        elements.append(elem)
                    for v in var_name:
                        var.append(v.name.value)
                        if '*' + v.name.value.split('*')[-1] in var:
                            return res.failure(Program.error()['ValueError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"not to many values to pair",
                                'context': context,
                                'exit': False
                            }))
                        else:
                            for i in range(len(var_name)):
                                context.symbolTable.set(
                                    var_name[i].name.value, elements[i])

            else:
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Cannot assign {type(value).__name__} to Pair",
                    'context': context,
                    'exit': False
                }))
        
       
        else:
            if res.should_return():
                return res
            if node.variable_keyword_token == "let":
                if value is None:
                    value = NoneType.none
                context.symbolTable.set(var_name, value, "let")
            elif node.variable_keyword_token == "final":
                if value is None:
                    value = NoneType.none
                context.symbolTable.set_final(var_name, value, "final")
        return res.success(value)


    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value
        value = context.symbolTable.get(var_name)
        if type(value) is dict:
            try:
                value = value['value']
                
            except:
                value = value
                
        if var_name in context.symbolTable.symbols and value is None:
            value = context.symbolTable.get(NoneType.none)
        elif value is None:
            if var_name == "@":
                return res.failure(Program.error()['Runtime']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Expected '@' to be followed by an identifier",
                    'context': context,
                    'exit': False
                }))
            return res.failure(Program.error()['NameError']({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"name '{var_name}' is not defined",
                'context': context,
                'exit': False
            }))
            return res.noreturn()
        value = value.copy().setContext(context).setPosition(
            node.pos_start, node.pos_end) if hasattr(value, 'copy') else value
        return res.success(value)
 
   
    def visit_VarReassignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value if hasattr(node.name, 'value') else node.name.id.value
        operation = node.operation
        v = context.symbolTable.get(var_name)
        value = res.register(self.visit(node.value, context))
        if v != None:
            if type(v) is dict:
                var_type = v['type']
                if var_type == "final":
                    return res.failure(Program.error()['NameError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"name '{var_name}' cannot be reassigned",
                        'context': context,
                        'exit': False
                    }))
                else:
                    if operation == "add":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):  
                                new_value = Number(v['value'].value + value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '+=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], String):
                            if isinstance(value, String):
                                new_value = String(v['value'].value + value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"reassignment of {TypeOf(v['value']).getType()} to {TypeOf(value).getType()} is not allowed",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], List):
                            if isinstance(value, List):
                                new_value = List(v['value'].elements + value.elements)
                                context.symbolTable.set(var_name, new_value)
                            elif isinstance(value, String):
                                new_list = []
                                for char in value.value:
                                    new_list.append(String(char).setPosition(node.pos_start, node.pos_end).setContext(context))
                                new_value = List(v['value'].elements + new_list)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"reassignment of '{TypeOf(v['value']).getType()}' to '{TypeOf(value).getType()}' is not allowed",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], Pair):
                            if isinstance(value, Pair):
                                new_value = Pair(v['value'].elements + value.elements)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"reassignment of '{TypeOf(v['value']).getType()}' to '{TypeOf(value).getType()}' is not allowed",
                                    'context': context,
                                    'exit': False
                                }))    
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })) 
                    elif operation == "sub":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):
                                new_value = Number(v['value'].value - value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                    elif operation == "mul":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):
                                new_value = Number(v['value'].value * value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], String):
                            if isinstance(value, Number):
                                new_value = String(v['value'].value * value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], List):
                            if isinstance(value, Number):
                                new_value = List(v['value'].elements * value.value)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot multiply {TypeOf(v['value']).getType()} and {TypeOf(value).getType()}",
                                    'context': context,
                                    'exit': False
                                }))
                        elif isinstance(v['value'], Pair):
                            if isinstance(value, Number):
                                new_value = Pair(v['value'].elements * value.value)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot multiply {TypeOf(v['value']).getType()} and {TypeOf(value).getType()}",
                                    'context': context,
                                    'exit': False
                                }))
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                    elif operation == "div":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):
                                new_value = Number(v['value'].value / value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '/=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '/=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))    
                    elif operation == "mod":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):
                                new_value = Number(v['value'].value % value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '%=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '%=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                    elif operation == "pow":
                        if isinstance(v['value'], Number):
                            if isinstance(value, Number):
                                new_value = Number(v['value'].value ** value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '**=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                        else:
                            return res.failure(Program.error()['TypeError']({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '**=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                }))
                    else:
                        context.symbolTable.set(var_name, value, "let")
            
        
        else:
            return res.failure(Program.error()['NameError']({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"name '{var_name}' is not defined",
                'context': context,
                'exit': False
            }))
        value = value.copy().setContext(context).setPosition(
            node.pos_start, node.pos_end) if hasattr(value, 'copy') else value
        return res.success(value)
 
 
    def visit_PropertyNode(self, node, context):
        res = RuntimeResult()
        value = ""
        object_name = res.register(self.visit(node.name, context)) 
        object_key = node.property
        #print(type(object_name).__name__, type(object_key).__name__, object_key)
        #TODO: check if object_name is not callable
        error = {
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            "message": "",
            "context": context,
            "exit": False
        }
        
        if isinstance(object_name, Class):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "methods_properties"):
                    if object_key.id.value in object_name.methods_properties:
                        value = object_name.methods_properties[object_key.id.value]
                        return res.success(value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.id.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no method {object_key.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
            
            if type(object_key).__name__ == "Token":
                if hasattr(object_name, "methods_properties"):
                    if object_key.value in object_name.methods_properties:
                        value = object_name.methods_properties[object_key.value]
                        return res.success(value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["PropertyError"](error))
            
            elif type(object_key).__name__ == "CallNode":
                if hasattr(object_name, "methods_properties"):
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in object_name.methods_properties:
                            value = object_name.methods_properties[object_key.node_to_call.value]
                            args_node = object_key.args_nodes
                            args = []
                            
                            for arg in args_node:
                                args.append(res.register(
                                    self.visit(arg, context)))
                                if res.should_return(): return res
                            return_value = res.register(value.run(args, object_name))
                            if res.should_return():
                                    return res
                            
                            if return_value == None or isinstance(return_value, NoneType):
                                return res.success(None)
                            else:
                                return res.success(return_value)
                            
                        else:
                            if object_name.name == "Export":
                                error['message'] = f"Export has no member '{object_key.node_to_call.value}'"
                            else:
                                self.error_detected = True
                                error["message"] = f"{object_name.name} has no method {object_key.node_to_call.value}"
                            return res.failure(Program.error()["PropertyError"](error))
                    # else:
                    #     return res.failure(Program.error()["PropertyError"](error))
        
        elif isinstance(object_name, Object):
            builtin_properties = {
                'get': 'get',
            }
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} has no property {object_key.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                    
            elif type(object_key).__name__ == "CallNode":
                if hasattr(object_name, "properties"):
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in object_name.properties:
                            value = object_name.properties[object_key.node_to_call.value]
                            if isinstance(value, Object):
                                error["message"] = f"{object_key.node_to_call.value} is not callable"
                                return res.failure(Program.error()["PropertyError"](error))
                            else:
                                args_node = object_key.args_nodes
                                args = []
                                
                                for arg in args_node:
                                    args.append(res.register(
                                        self.visit(arg, context)))
                                    if res.should_return(): return res
                                
                                return_value = res.register(value.execute(args))
                                #print(type(return_value).__name__, return_value)
                                if res.should_return():
                                        return res
                                if return_value == None or isinstance(return_value, NoneType):
                                    return res.success(None)
                                else:
                                    return res.success(return_value)
                        else:
                            error["message"] = f"{node.name.id.value} has no property {object_key.node_to_call.value}"
                            return res.failure(Program.error()["PropertyError"](error))
                else:
                    if object_key.node_to_call.id.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.id.value]
                        args_node = object_key.args_nodes
                        args = []
                        
                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        
                        return_value = res.register(value.run(args))
                        if res.should_return():
                                return res
                            
                        if return_value == None or isinstance(return_value, NoneType):
                            return res.success(None)
                        else:
                            return res.success(return_value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.node_to_call.id.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no property {object_key.node_to_call.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                    # else:
                    #     return res.failure(Program.error()["PropertyError"](error))
                    
            elif type(object_key).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        print()
                        # if object_name.properties['__name']:
                        #     name = object_name.properties['__name']
                        #     error["message"] = f"{name} has no property {object_key.value}"
                        # else:
                        error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["PropertyError"](error))
            
            elif type(object_key).__name__ == "PropertyNode":
                if hasattr(object_name, "properties"):
                    if object_key.name.id.value in object_name.properties:
                        value = object_name.properties[object_key.name.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} has no property {object_key.name.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
   
        elif isinstance(object_name, Dict):
            builtin_properties = {
                'get': 'get',
            }
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} has no property {object_key.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))

            elif type(object_key).__name__ == "CallNode":
                if hasattr(object_name, "properties"):
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in object_name.properties:
                            value = object_name.properties[object_key.node_to_call.value]
                            if isinstance(value, Object):
                                error["message"] = f"{object_key.node_to_call.value} is not callable"
                                return res.failure(Program.error()["PropertyError"](error))
                            else:
                                args_node = object_key.args_nodes
                                args = []

                                for arg in args_node:
                                    args.append(res.register(
                                        self.visit(arg, context)))
                                    if res.should_return():
                                        return res

                                return_value = res.register(
                                    value.execute(args))
                                #print(type(return_value).__name__, return_value)
                                if res.should_return():
                                    return res
                                if return_value == None or isinstance(return_value, NoneType):
                                    return res.success(None)
                                else:
                                    return res.success(return_value)
                        else:
                            error["message"] = f"{node.name.id.value} has no property {object_key.node_to_call.value}"
                            return res.failure(Program.error()["PropertyError"](error))
                else:
                    if object_key.node_to_call.id.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.id.value]
                        args_node = object_key.args_nodes
                        args = []

                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return():
                                return res

                        return_value = res.register(value.run(args))
                        if res.should_return():
                            return res

                        if return_value == None or isinstance(return_value, NoneType):
                            return res.success(None)
                        else:
                            return res.success(return_value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.node_to_call.id.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no property {object_key.node_to_call.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                    # else:
                    #     return res.failure(Program.error()["PropertyError"](error))

            elif type(object_key).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        self.error_detected = True
                        error["message"] = f"'{object_key.value}'"
                        return res.failure(Program.error()["PropertyError"](error))

            elif type(object_key).__name__ == "PropertyNode":
                if hasattr(object_name, "properties"):
                    if object_key.name.id.value in object_name.properties:
                        value = object_name.properties[object_key.name.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} has no property {object_key.name.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
   
        elif isinstance(object_name, List):
            if type(object_key).__name__ == "Token":
                if object_key.value in list_methods:
                    value = value = f"<{str(object_key.value)}()>, [ built-in list method ]"
                    if object_key.value == "length":
                        return res.success(Number(len(object_name.elements)))
                    else:
                        value = f"<{str(object_key.value)}()>, [ built-in list method ]"
                        return res.success(BuiltInMethod(value))
                else:
                    error["message"] = f"'list' has no property {object_key.value}"
                    return res.failure(Program.error()["PropertyError"](error))
                
            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in list_methods:
                        args = []
                        for arg in object_key.args_nodes:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        value = BuiltInMethod_List(
                            object_key.node_to_call.value, object_name, args, node, context)
                        return res.success(value.name)
                    else:
                        error["message"] = f"'{TypeOf(object_name.value).getType()}' has no property {object_key.node_to_call.value}"
                        return res.failure(Program.error()["PropertyError"](error))
        
        elif isinstance(object_name, String):
            if type(object_key).__name__ == "Token":
                if object_key.value in string_methods:
                    value = f"<{str(object_key.value)}()>, [ built-in string method ]"
                    if object_key.value == "length":
                        return res.success(Number(len(object_name.value)))
                    else:
                        return res.success(BuiltInMethod(value))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' has no property {object_key.value}"
                    return res.failure(Program.error()["PropertyError"](error))
                
                
            elif type(object_key).__name__ == "VarAccessNode":
                if object_key.id.value in string_methods:
                    value = f"<{str(object_key.id.value)}()>, [ built-in string method ]"
                    return res.success(String(value))
                else:
                    error["message"] = f"'string' has no property {object_key.id.value}"
                    return res.failure(Program.error()["PropertyError"](error))
               
            elif type(object_key).__name__ == "PropertyNode":
                if type(object_key.id).__name__ ==  "CallNode":
                    if object_key.id.node_to_call.id.value in string_methods:
                        args = []
                        for arg in object_key.id.args_nodes:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        value = BuiltInMethod_String(
                            object_key.id.node_to_call.id.value, object_name, args, node, context)
                        return res.success(value)
                    else:
                        error["message"] = f"'string' has no property {object_key.id.node_to_call.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                else:
                    if object_key.id.value in string_methods:
                        value = f"<{str(object_key.id.value)}()>, [ built-in string method ]"
                        return res.success(String(value))
                    else:
                        error["message"] = f"'string' has no property {object_key.id.value}"
                        return res.failure(Program.error()["PropertyError"](error)) 
                
            
            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in string_methods:
                        args = []
                        for arg in object_key.args_nodes:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        value = BuiltInMethod_String(
                            object_key.node_to_call.value, object_name, args, node, context)
                        return res.success(value.name)
                    else:
                        error["message"] = f"'string' has no property {object_key.node_to_call.value}"
                        return res.failure(Program.error()["PropertyError"](error))
        
        elif isinstance(object_name, BuiltInMethod_String):
            if type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in string_methods:
                        args = []
                        for arg in object_key.args_nodes:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        value = BuiltInMethod_String(
                            object_key.node_to_call.value, object_name, args, node, context)
                        return res.success(value)
                    else:
                        error["message"] = f"'string' has no property {object_key.node_to_call.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                
        elif isinstance(object_name, Number):
            if type(object_key).__name__ == "Token":
                if object_key.value in number_methods:
                    value = f"<{str(object_key.value)}()>, [ built-in number method ]"
                    return res.success(BuiltInMethod(value))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' has no property {object_key.value}"
                    return res.failure(Program.error()["PropertyError"](error))
                
            elif type(object_key).__name__ == "VarAccessNode":
                if object_key.id.value in number_methods:
                    value = f"<{str(object_key.id.value)}()>, [ built-in number method ]"
                    return res.success(BuiltInMethod(value))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' has no property {object_key.id.value}"
                    return res.failure(Program.error()["PropertyError"](error))
            
            elif type(object_key).__name__ == "CallNode":
                if object_key.node_to_call.value in number_methods:
                    args = []
                    for arg in object_key.args_nodes:
                        args.append(res.register(
                            self.visit(arg, context)))
                        if res.should_return(): return res
                    value = BuiltInMethod_Number(object_key.node_to_call.id.value, object_name, args, node, context)
                    return res.success(value)
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' has no property {object_key.node_to_call.value}"
                    return res.failure(Program.error()["PropertyError"](error)) 
               
        elif isinstance(object_name, Function):
            if type(object_key).__name__ == "Token":
                if object_key.value in object_name.properties.properties:
                    if object_key.value in object_name.properties.properties:
                        value = object_name.properties.properties[object_key.value]
                        return res.success(value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                else:
                    return res.failure(Program.error()['Runtime']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"{object_name.name} has no property {object_key.value}",
                        'context': context,
                        'exit': False
                    }))
            if type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in object_name.properties.properties:
                        value = object_name.properties.properties[object_key.node_to_call.value]
                        args_node = object_key.args_nodes
                        args = []
                        
                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        _type = object_name.properties.properties[
                            object_key.node_to_call.value].properties.properties['__properties'].properties['__type'].value
                        if _type == "method":
                            return_value = res.register(value.run(args, object_name))
                        else:
                            return_value = res.register(value.execute(args))
                        if res.should_return():
                                return res
                        
                        if return_value == None or isinstance(return_value, NoneType):
                            return res.success(None)
                        else:
                            return res.success(return_value)
                else:
                    return res.failure(Program.error()['Runtime']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"{object_name.name} has no property {object_key.node_to_call.value}",
                        'context': context,
                        'exit': False
                    }))
            else:
                return res.failure(Program.error()['PropertyError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"'{object_name.name}'",
                    'context': context,
                    'exit': False
                }))
         
        elif type(object_name).__name__ == "PropertyNode":
            print(type(object_key))

        elif isinstance(object_name, ModuleObject):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} has no property {object_key.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                    
            elif type(object_key).__name__ == "CallNode":
                if hasattr(object_name, "properties"):
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in object_name.properties:
                            value = object_name.properties[object_key.node_to_call.value]
                            if isinstance(value, Object):
                                error["message"] = f"{object_key.node_to_call.value} is not callable"
                                return res.failure(Program.error()["PropertyError"](error))
                            else:
                                args_node = object_key.args_nodes
                                args = []
                                
                                for arg in args_node:
                                    args.append(res.register(
                                        self.visit(arg, context)))
                                    if res.should_return(): return res
                                
                                return_value = res.register(value.execute(args))
                                if res.should_return():
                                        return res
                                if return_value == None or isinstance(return_value, NoneType):
                                    return res.success(None)
                                else:
                                    return res.success(return_value)
                        else:
                            error["message"] = f"{node.name.id.value} has no property {object_key.node_to_call.value}"
                            return res.failure(Program.error()["PropertyError"](error))
                else:
                    if object_key.node_to_call.id.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.id.value]
                        args_node = object_key.args_nodes
                        args = []
                        
                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        
                        return_value = res.register(value.run(args))
                        if res.should_return():
                                return res
                            
                        if return_value == None or isinstance(return_value, NoneType):
                            return res.success(None)
                        else:
                            return res.success(return_value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = f"Export has no member '{object_key.node_to_call.id.value}'"
                        else:
                            error["message"] = f"{object_name.name} has no property {object_key.node_to_call.id.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                    # else:
                    #     return res.failure(Program.error()["PropertyError"](error))
                    
            elif type(object_key).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        print(object_name.properties)
                        # if object_name.properties['__name']:
                        #     name = object_name.properties['__name']
                        #     error["message"] = f"{name} has no property {object_key.value}"
                        # else:
                        error["message"] = f"{object_name.name} has no property {object_key.value}"
                        return res.failure(Program.error()["PropertyError"](error))
                
        elif isinstance(object_name, Module):
            if type(object_key).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
       
        else:
            error["message"] = f"'{object_key.value}'"
            return res.failure(Program.error()["PropertyError"](error))

    
    def visit_PropertySetNode(self, node, context):
        res = RuntimeResult()
        object_name = res.register(self.visit(node.name, context))
        property = node.property
        value = res.register(self.visit(node.value, context))
        if isinstance(object_name, Class):
            if type(property).__name__ == "Token":
               if hasattr(object_name, "methods_properties"):
                   object_name.methods_properties[property.value] = value
        if isinstance(object_name, Dict):
            if type(property).__name__ == "Token":
               if hasattr(object_name, "properties"):
                   object_name.properties[property.value] = value
        if isinstance(object_name, Object):
            if type(property).__name__ == "Token":
               if hasattr(object_name, "properties"):
                   object_name.properties[property.value] = value
                   
        if isinstance(object_name, Function):
            if type(property).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    object_name.properties.properties[property.value] = value
                    object_name.properties.properties['__properties'].properties[property.value] = value
                    
 
    def visit_IndexNode(self, node, context):
        res = RuntimeResult()
        index_value = res.register(self.visit(node.name, context))
        index  = res.register(self.visit(node.index, context))
        if res.should_return(): return res
        object_type = TypeOf(index_value).getType()
        index_type = TypeOf(index).getType()
        if object_type == "list":
            if index_type == "int":
                try:
                    get_value = index_value.elements[index.value]
                    return res.success(get_value)
                except IndexError:
                    return res.failure(Program.error()['IndexError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"list index out of range",
                        'context': context,
                        'exit': False
                    }))
                except AttributeError:
                     pass
            else:
                return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"list indices must be integers or slices, not {index_type}",
                    'context': context,
                    'exit': False
                }))
        
        elif object_type == "pair":
            if index_type == "int":
                try:
                    get_value = index_value.elements[index.value]
                    return res.success(get_value)
                except IndexError:
                    return res.failure(Program.error()['IndexError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"pair index out of range",
                        'context': context,
                        'exit': False
                    }))
                except AttributeError:
                    pass
            else:
                return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"pair indices must be integers or slices, not {index_type}",
                    'context': context,
                    'exit': False
                }))
        
        elif object_type == "object":
            if index_type == "string":
                try:
                    if (type(index_value).__name__ == "dict"):
                        get_value = index_value[index.value]
                        return res.success(get_value)
                    else:
                        get_value = index_value.properties[index.value]
                        return res.success(get_value)
                except KeyError:
                    return res.failure(Program.error()['KeyError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"'{index.value}'",
                        'context': context,
                        'exit': False
                    }))
                except AttributeError:
                    pass
            else:
                return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"object indices must be strings, not {index_type}",
                    'context': context,
                    'exit': False
                }))
        
        elif object_type == "dict":
            if index_type == "string":
                try:
                    get_value = index_value.properties[index.value]
                    return res.success(get_value)
                except KeyError:
                    return res.failure(Program.error()['KeyError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"'{index.value}'",
                        'context': context,
                        'exit': False
                    }))
                except AttributeError:
                    pass
            else:
                return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"object indices must be strings, not {index_type}",
                    'context': context,
                    'exit': False
                }))
        
        elif object_type == "string":
            try:
                get_value = index_value.value[index.value]
                return res.success(String(get_value))
            except IndexError:
                return res.failure(Program.error()['IndexError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"string index out of range",
                    'context': context,
                    'exit': False
                }))
            except AttributeError:
                pass


    def visit_SliceNode(self, node, context):
        res = RuntimeResult()
        index_value = res.register(self.visit(node.name, context))
        start = res.register(self.visit(node.start, context))
        end = res.register(self.visit(node.end, context))
        step = res.register(self.visit(node.step, context)) if node.step else None
        type_ = node.type
        if res.should_return(): return res
        object_type = TypeOf(index_value).getType()
        start_type = TypeOf(start).getType()
        end_type = TypeOf(end).getType()
        if object_type == "list":
            if type_ == "double_colon":
                if not step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.elements[start.value::end.value]
                            return res.success(List(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(List(index_value.elements[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            get_value = index_value.elements[::end.value]
                            return res.success(List(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.elements[start.value::]
                            return res.success(List(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            }))
                    else:
                        return res.failure(Program.error()['TypeError']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"list indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        }))
            else:
                if start_type == "int" and end_type == "int":
                    try:
                        get_value = index_value.elements[start.value:end.value]
                        return res.success(List(get_value))
                    except IndexError:
                        get_value = index_value.elements[start.value:]
                        return res.success(List(get_value))
                elif start_type == "NoneType" and end_type == "NoneType":
                    return res.success(List(index_value.elements[:]))
                elif start_type == "NoneType" and end_type == "int":
                    try:
                        get_value = index_value.elements[:end.value]
                        return res.success(List(get_value))
                    except IndexError:
                        get_value = index_value.elements[:]
                        return res.success(List(get_value))
                elif start_type == "int" and end_type == "NoneType":
                    try:
                        get_value = index_value.elements[start.value:]
                        return res.success(List(get_value))
                    except IndexError:
                        get_value = index_value.elements[:]
                        return res.success(List(get_value))
                else:
                    return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"slice indices must be integers, not {start_type} and {end_type}",
                    'context': context,
                    'exit': False
                }))

        elif object_type == "pair":
            if type_ == "double_colon":
                if not step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.elements[start.value::end.value]
                            return res.success(Pair(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(Pair(index_value.elements[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            get_value = index_value.elements[::end.value]
                            return res.success(Pair(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.elements[start.value::]
                            return res.success(Pair(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            }))
                    else:
                        return res.failure(Program.error()['TypeError']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"pair indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        }))
            else:
                if start_type == "int" and end_type == "int":
                    try:
                        get_value = index_value.elements[start.value:end.value]
                        return res.success(Pair(get_value))
                    except IndexError:
                        get_value = index_value.elements[start.value:]
                        return res.success(Pair(get_value))
                elif start_type == "NoneType" and end_type == "NoneType":
                    return res.success(Pair(index_value.elements[:]))
                elif start_type == "NoneType" and end_type == "int":
                    try:
                        get_value = index_value.elements[:end.value]
                        return res.success(Pair(get_value))
                    except IndexError:
                        get_value = index_value.elements[:]
                        return res.success(Pair(get_value))
                elif start_type == "int" and end_type == "NoneType":
                    try:
                        get_value = index_value.elements[start.value:]
                        return res.success(Pair(get_value))
                    except IndexError:
                        get_value = index_value.elements[:]
                        return res.success(Pair(get_value))
                else:
                    return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"slice indices must be integers, not {start_type} and {end_type}",
                    'context': context,
                    'exit': False
                }))
          
        elif object_type == "string":
            if type_ == "double_colon":
                if not step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.value[start.value::end.value]
                            return res.success(String(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(String(index_value.value[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            get_value = index_value.value[::end.value]
                            return res.success(String(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            }))
                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.value[start.value::]
                            return res.success(String(get_value))
                        except IndexError:
                            return res.failure(Program.error()['IndexError']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            }))
                    else:
                        return res.failure(Program.error()['TypeError']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"string indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        }))
            else:
                if start_type == "int" and end_type == "int":
                    try:
                        get_value = index_value.value[start.value:end.value]
                        return res.success(String(get_value))
                    except IndexError:
                        get_value = index_value.value[start.value:]
                        return res.success(String(get_value))
                elif start_type == "NoneType" and end_type == "NoneType":
                    return res.success(String(index_value.value[:]))
                elif start_type == "NoneType" and end_type == "int":
                    try:
                        get_value = index_value.value[:end.value]
                        return res.success(String(get_value))
                    except IndexError:
                        get_value = index_value.value[:]
                        return res.success(String(get_value))
                elif start_type == "int" and end_type == "NoneType":
                    try:
                        get_value = index_value.value[start.value:]
                        return res.success(String(get_value))
                    except IndexError:
                        get_value = index_value.value[:]
                        return res.success(String(get_value))
                else:
                    return res.failure(Program.error()['TypeError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"string indices must be integers, not {start_type} and {end_type}",
                    'context': context,
                    'exit': False
                }))

        else:
            return res.failure(Program.error()['TypeError']({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"{object_type} cannot be sliced",
                'context': context,
                'exit': False  
            }))  
        
    
    def visit_SpreadNode(self, node, context):
        res = RuntimeResult()
        assign_token = node.assign_token
        var_name = node.name.value
        value = res.register(self.visit(node.value,context))
        value_type = type(value).__name__
        _type = node._type
        if  isinstance(value, List):
            new_list = []
            for element in value.elements:
                if hasattr(element, 'elements'):
                    new_list += element.elements
                elif hasattr(element, 'value'):
                    new_list.append(element.value)
                elif hasattr(element, 'properties'):
                    new_list.append(element.properties)
                elif hasattr(element, 'methods_properties'):
                    new_list.append(element.methods_properties)
                else:
                    new_list.append(element)
                    
            context.symbolTable.set(var_name, List(new_list), assign_token)
                
            return res.success(None)
        
        elif isinstance(value, Pair):
            new_list = ()
            for element in value.elements:
                if hasattr(element, 'elements'):
                    new_list += element.elements
                elif hasattr(element, 'value'):
                    new_list += (element.value,)
                elif hasattr(element, 'properties'):
                    new_list += (element.properties,)
                elif hasattr(element, 'methods_properties'):
                    new_list += (element.methods_properties,)
                else:
                    new_list += (element,)
            
            context.symbolTable.set(var_name, List(new_list), assign_token)
        
        elif isinstance(value, String):
            new_string = ""
            for element in value.value:
                new_string += element
            context.symbolTable.set(var_name, String(new_string), assign_token)
            
        
    def visit_ExportModuleNode(self, node, context):
        res = RuntimeResult()
        modules = node.modules
        value = ""
        for module in modules:
            if type(module).__name__ == "Token":
                name = module.value
                value = context.symbolTable.get(name)
                if value == None:
                    res.failure(Program.error()['NameError']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"name '{name}' is not defined",
                        'context': context,
                        'exit': False
                    }))
                else:
                    #print(name, value)
                    context.symbolTable.set(name, value)
            elif type(module).__name__ == "VarAccessNode":
                name = module.id.value
                value = res.register(self.visit(module, context))
                context.symbolTable.setSymbol(name, value)
    
    
    def visit_ModuleExport(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value
        value = context.symbolTable.get(node.value.value)
        if value == None:
           return res.failure(Program.error()['NameError']({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"name '{node.value.value}' is not defined",
                'context': context,
                'exit': False
            }))
        return res.success(Object(var_name,value, "module"))
    
    
    def visit_GetNode(self, node, context):
        res = RuntimeResult()
        value = ""
        error = {
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                "message": "",
                "context": context,
                "exit": False
            }
        module_name = node.module_name.value
        module_path = node.module_path.value + ".alden" if node.module_path.value.split('.')[-1] != "alden" else node.module_path.value
        module = Program.runFile(module_path)
        
        if module == None:
            builtin_modules = {
                "math": Program.runFile,
                "http": Program.runFile,
            }
            module_path = node.module_path.value
            if module_path in builtin_modules:

                if  context.symbolTable.modules.is_module_in_members(module_name):
                    error['message'] = "Module '{}' already imported".format(module_name)
                    return res.failure(Program.error()["ModuleError"](error))
                else:
                    try: 
                        module = builtin_modules[module_path](f"./lib/{module_path}/main.alden")
                        Program.createModule(module_name, module, context) 
                        context.symbolTable.set_module(module_name, module)
                    except RecursionError:
                            error['message'] = "Circlular import: module {} is already imported".format(module_name)
                            return res.failure(Program.error()["ModuleError"](error))
            else:
                error['message'] = "Module '{}' not found".format(module_name)
                return res.failure(Program.error()["ModuleError"](error))
        
        else:
            if  context.symbolTable.modules.is_module_in_members(module_name):
                error['message'] = "Module '{}' already imported".format(module_name)
                return res.failure(Program.error()["ModuleError"](error))
            else:
                Program.createModule(module_name, module, context)
                context.symbolTable.set_module(module_name, module)
                
    
    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()
        try:
            left = res.register(self.visit(node.left_node, context))
            if res.should_return(): return res
            right = res.register(self.visit(node.right_node, context))
            if node.op_tok.type == tokenList.TT_PLUS:
                result, error = left.added_to(right)
            if node.op_tok.type == tokenList.TT_PLUS_PLUS:
                result, error = left.increment()
            elif node.op_tok.type == tokenList.TT_MINUS:
                result, error = left.subtracted_by(right)
            elif node.op_tok.type == tokenList.TT_MINUS_MINUS:
                result, error = left.decrement()
            elif node.op_tok.type == tokenList.TT_MUL:
                result, error = left.multiplied_by(right)
            elif node.op_tok.type == tokenList.TT_DIV:
                result, error = left.divided_by(right)
            elif node.op_tok.type == tokenList.TT_POWER:
                result, error = left.powred_by(right)
            elif node.op_tok.type == tokenList.TT_MOD:
                result, error = left.modulo(right)
            elif node.op_tok.type == tokenList.TT_EQEQ:
                result, error = left.get_comparison_eq(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'is'):
                result, error = left.get_comparison_eq(right)
            elif node.op_tok.type == tokenList.TT_NEQ:
                result, error = left.get_comparison_ne(right)
            elif node.op_tok.type == tokenList.TT_LT:
                result, error = left.get_comparison_lt(right)
            elif node.op_tok.type == tokenList.TT_GT:
                result, error = left.get_comparison_gt(right)
            elif node.op_tok.type == tokenList.TT_RSHIFT:
                result, error = left.get_comparison_rshift(right)
            elif node.op_tok.type == tokenList.TT_LSHIFT:
                result, error = left.get_comparison_lshift(right)
            elif node.op_tok.type == tokenList.TT_LTE:
                result, error = left.get_comparison_lte(right)
            elif node.op_tok.type == tokenList.TT_GTE:
                result, error = left.get_comparison_gte(right)
            elif node.op_tok.type == tokenList.TT_MERGE:
                result, error = left.merge(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'in'):
                result, error = right.get_comparison_in(left)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'notin'):
                result, error = right.get_comparison_not_in(left)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'and'):
                result, error = left.and_by(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'or'):
                result, error = left.or_by(right)
            
            if error:
                return res.failure(error)
            else:
                return res.success(result.setPosition(node.pos_start, node.pos_end))
        except KeyboardInterrupt:
            pass

    
    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        unary_node = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        error = None
        # if node.op_tok.type == tokenList.TT_SPREAD:
        #     elements = unary_node.elements
        #     # spread unpacks the elements of an iterable into individual items e.g [1,2,3] returns 1,2,3
        #     # iterate over the elements and add them to the current scope
        #     for element in elements:
        #         context.symbolTable.set(element.name, element.value)
        #     return res.success(unary_node)
        #     expanded_value = ''
        #     for element in elements:
        #         expanded_value += f"[i for i in {element}]"
        if node.op_tok.type == tokenList.TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(tokenList.TT_KEYWORD, 'not'):
            if isinstance(number, Pair):
                for i in range(len(number.elements)):
                    number = Number(not number.elements[i].value)
            number, error = number.notted()
        if error:
            return res.failure(error)
        else:
            return res.success(number.setPosition(node.pos_start, node.pos_end))

    
    def visit_IfNode(self, node, context):
        res = RuntimeResult()
        for condition, expr, return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res
            if hasattr(condition_value, "value") and condition_value.value == "true":
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(NoneType.none if return_null else expr_value)
        if node.else_case:
            expr, return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(NoneType.none if return_null else else_value)

        return res.success(NoneType.none)

    
    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res
        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res
        if node.step_value_node:
            step_value = res.register(
                self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)
        i = start_value.value

        if step_value.value >= 0:
            if not isinstance(start_value, Number) or not isinstance(end_value, Number) or not isinstance(step_value, Number):
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and strings',
                        'exit': False
                    })
                )
            if type(end_value.value) == float:
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and floats',
                        'exit': False
                    })
                )
                
            if type(end_value.value) == range:
                
                return res.failure(
                    Program.error()['Syntax']({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': 'For loop not supported between ints and ranges',
                        'exit': False,
                    })
                )
                
                
            def condition(): return i < end_value.value
        else:
            def condition(): return i > end_value.value

        while condition():
            context.symbolTable.set(node.var_name_token.value, Number(i))
            i += step_value.value
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                return res

            if res.loop_continue:
                continue

            if res.loop_break:
                break

            elements.append(value)
        return res.success(NoneType.none if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_InNode(self, node, context):
        res = RuntimeResult()
        iterable_node = context.symbolTable.get(node.iterable_node.value)
        iterators = node.iterators
        if type(iterable_node) == dict:
            iterable_node = iterable_node['value']
        value = ""
        elements = []
        if type(iterable_node).__name__ == "NoneType":
            return res.failure(
                Program.error()['NameError']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'context': context,
                    'message': f"name '{node.iterable_node.value}' is not defined",
                    'exit': False
                })
            )
        
 
        if isinstance(iterable_node, Object):
            end_value = iterable_node.get_length()
            values = []
            for i in range(end_value):
                if len(iterators) == 1:
                    if type(iterators[0]).__name__ == "VarAccessNode":
                        pair = (iterable_node.get_keys(), iterable_node.get_values())
                        new_pair = ""
                        key, value = pair[0][i], pair[1][i]
                        new_pair = tuple([key, value])
                        context.symbolTable.set(iterators[0].id.value, Pair(new_pair))
                        value = res.register(self.visit(node.body_node, context))
                        elements.append(value)
                        
                    else:
                        return res.failure(
                            Program.error()['Syntax']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                        )
                elif len(iterators) == 2:
                    if type(iterators[0]).__name__ == "VarAccessNode" and type(iterators[1]).__name__ == "VarAccessNode":
                        # create a new pair
                        pair = (iterable_node.get_keys(), iterable_node.get_values())
                        new_pair = ""
                        key, value = pair[0][i], pair[1][i]
                        context.symbolTable.set(iterators[0].id.value, key)
                        context.symbolTable.set(iterators[1].id.value, value)
                        value = res.register(self.visit(node.body_node, context))
                        elements.append(value)
                    else:
                        return res.failure(
                            Program.error()['Syntax']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                        )
        
        elif isinstance(iterable_node, List):
            end_value = len(iterable_node.elements)
            for i in range(end_value):
                if len(iterators) == 1:
                    if type(iterators[0]).__name__ == "VarAccessNode":
                        context.symbolTable.set(iterators[0].id.value, iterable_node.elements[i])
                        value = res.register(self.visit(node.body_node, context))
                        elements.append(value)
                    else:
                        return res.failure(
                            Program.error()['Syntax']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                        )
                elif len(iterators) == 2:
                    return res.failure(
                        Program.error()['Syntax']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                            'exit': False
                        })
                    )
           
        elif isinstance(iterable_node, Pair):
            end_value = len(iterable_node.elements)
            for i in range(end_value):
                if len(iterators) == 1:
                    if type(iterators[0]).__name__ == "VarAccessNode":
                        context.symbolTable.set(iterators[0].id.value, iterable_node.elements[i])
                        value = res.register(self.visit(node.body_node, context))
                        elements.append(value)
                    else:
                        return res.failure(
                            Program.error()['Syntax']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                        )
                elif len(iterators) == 2:
                    return res.failure(
                        Program.error()['Syntax']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                            'exit': False
                        })
                    )
        
        elif isinstance(iterable_node, String):
            end_value = len(iterable_node.value)
            for i in range(end_value):
                if len(iterators) == 1:
                    if type(iterators[0]).__name__ == "VarAccessNode":
                        new_list = list(iterable_node.value)
                        context.symbolTable.set(iterators[0].id.value, String(new_list[i]))
                        value = res.register(self.visit(node.body_node, context))
                        elements.append(value)
                    else:
                        return res.failure(
                            Program.error()['Syntax']({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                        )
                elif len(iterators) == 2:
                    return res.failure(
                        Program.error()['Syntax']({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f'cannot iterate with type {TypeOf(iterable_node.value[i]).getType()}',
                            'exit': False
                        })
                    )
        
        else:
            return res.failure(
                Program.error()['Syntax']({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'context': context,
                    'message': f'In loop not supported for type {TypeOf(iterable_node).getType()}',
                    'exit': False
                })
            )
        
       
        return res.success(NoneType.none if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))
    
    
    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements = []
        try:
            while True:
                condition = res.register(self.visit(node.condition_node, context))
                
                if res.should_return():
                    return res
                is_true = True if hasattr(condition, "value") and condition.value == "true" else False
                if not is_true:
                    break
                value = res.register(self.visit(node.body_node, context))
                if res.should_return() and res.loop_continue == False and res.loop_break == False:
                    return res

                if res.loop_continue:
                    continue

                if res.loop_break:
                    break

                elements.append(value)
        except KeyboardInterrupt:
            print('Exiting...')

        return res.success(NoneType.none if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_MatchNode(self, node, context):
        res = RuntimeResult()
        expression = res.register(self.visit(node.expression, context))
        cases = node.cases
        default_case = node.default_case
        if res.should_return(): return res
        
        for case in cases:
            condition = res.register(self.visit(case['case'], context))
            if res.should_return(): return res
            if hasattr(condition, "value") and hasattr(expression, "value") and condition.value == expression.value:
                value = res.register(self.visit(case['body'], context))
                if res.should_return(): return res
                return res.success(value)
            elif hasattr(condition, "elements") and hasattr(expression, "elements") and condition.isSame(expression):
                value = res.register(self.visit(case['body'], context))
                if res.should_return(): return res
                return res.success(value)
            elif hasattr(condition, "properties") and hasattr(expression, "properties") and condition.isSame(expression):
                value = res.register(self.visit(case['body'], context))
                if res.should_return(): return res
                return res.success(value)
            elif hasattr(condition, "methods_properties") and hasattr(expression, "methods_properties") and condition.isSame(expression):
                value = res.register(self.visit(case['body'], context))
                if res.should_return(): return res
                return res.success(value)
        if default_case:
            value = res.register(self.visit(default_case['body'], context))
            if res.should_return(): return res
            return res.success(value)
                 

    def visit_FunctionNode(self, node, context):
        res = RuntimeResult()
        def_name = node.def_name_token.value if node.def_name_token else "none"
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.args_name_tokens]
        defualt_values = node.default_values
        __type = node.type
        if __type == None:
            __type = "function"
        set_properties = {
            '__properties': Dict({
                '__name': String(def_name),
                '__type': String(__type),
            })
        }
        
        properties = Dict(set_properties)
        def_value = Function(def_name, body_node, arg_names, node.implicit_return, defualt_values, properties, context).setContext(
            context).setPosition(node.pos_start, node.pos_end)
        if node.type != 'method':
            if node.def_name_token:
                context.symbolTable.set(def_name, def_value)


        return res.success(def_value)

    
    def visit_ObjectNode(self, node, context):
        res = RuntimeResult()
        object_name = node.object_name.value
        object_value = ""
        properties = {}
        
        for property in node.properties:
            prop_name = property['name'].value
            prop_value = res.register(self.visit(property['value'], context))
            properties = dict(properties, **{str(prop_name): prop_value})
            if res.should_return():
                return res
            object_value = Object(object_name, properties).setContext(context).setPosition(node.pos_start, node.pos_end)
            if isinstance(prop_value, NoneType):
                object_value = Object(object_name, {}).setContext(
                    context).setPosition(node.pos_start, node.pos_end)
                # already_defined = context.symbolTable.get(object_name)
                
                # if already_defined:
                #     if isinstance(already_defined, Object):
                #         return res.failure(Program.error()["Runtime"]({
                #             "pos_start": node.pos_start,
                #             "pos_end": node.pos_end,
                #             "message": "Object with name '{}' already defined".format(object_name),
                #             "context": context,
                #             "exit": False
                #         }))
                #     else:
                #         return res.failure(Program.error()["Runtime"]({
                #             "pos_start": node.pos_start,
                #             "pos_end": node.pos_end,
                #             "message": "name '{}' already defined".format(object_name),
                #             "context": context,
                #             "exit": False
                #         }))
                context.symbolTable.set(object_name, object_value)
            else:
                if node.other != None:
                    if node.other['name'] == "module":
                        as_name = node.other["as_name"]
                        if as_name != None:
                            properties["__name"] = String(as_name.value).setContext(context).setPosition(node.pos_start, node.pos_end)
                context.symbolTable.set_object(object_name, object_value)
        return res.success(object_value)

    
    def visit_DictNode(self, node, context):
        res = RuntimeResult()
        properties = {}
        keys = List([ String(key.value).setContext(context).setPosition(key.pos_start, key.pos_end) for key in node.keys ])
        values = List( [res.register(self.visit(value, context)) for value in node.values] )
        for prop in node.properties:
            key = prop['key'].value
            value = res.register(self.visit(prop['value'], context))
            if res.should_return(): return res
            #_object = dict(properties, **{str(key): value})
            set_properties = {
                    '__keys': keys,
                    '__values': values,
            }
        
            properties = dict(properties, **{str(key): value}, **{str("__properties"): Dict(set_properties)})
        return res.success(Dict(properties, keys, values).setContext(context).setPosition(node.pos_start, node.pos_end))
    
    
    def visit_ModuleObject(self, node, context):
        res = RuntimeResult()
        object_name = node.object_name.value
        object_value = ""
        properties = {}

        for property in node.properties:
            prop_name = property['name'].value
            prop_value = res.register(self.visit(property['value'], context))
            properties = dict(properties, **{str(prop_name): prop_value})
            if res.should_return():
                return res
            object_value = ModuleObject(object_name, properties).setContext(
                context).setPosition(node.pos_start, node.pos_end)
            if isinstance(prop_value, NoneType):
                object_value = ModuleObject(object_name, {'key': {}, 'value': {}}).setContext(
                    context).setPosition(node.pos_start, node.pos_end)
                already_defined = context.symbolTable.get(object_name)
                if already_defined:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        "message": "Object with name '{}' already defined".format(object_name),
                        "context": context,
                        "exit": False
                    }))
                context.symbolTable.set(object_name, object_value)
            else:
                if node.other != None:
                    if node.other['name'] == "module":
                        as_name = node.other["as_name"]
                        if as_name != None:
                            properties["__name"] = String(as_name.value).setContext(
                                context).setPosition(node.pos_start, node.pos_end)
                context.symbolTable.set_object(object_name, object_value)
        return res.success(object_value)
                                  
    
    def visit_ClassNode(self, node, context):
        res = RuntimeResult()
        class_name = node.class_name.value
        constructor_args = node.class_constuctor_args
        inherits_class_name = node.inherits_class_name
        inherits_class = node.inherits_class
        class_value = {}
        methods = {}
        if node.methods != '' and node.methods != None:
            for method in node.methods:
                method_name = method['name'].value
                method_value = res.register(
                    self.visit(method['value'], context))
                _object = dict(methods, **{str(method_name): method_value})
                if res.should_return(): return res
                set_properties = {
                    '__name': String(class_name),
                    '__type': String('class'),
                    '__methods': Dict(_object),
                }
                
                
                properties = Dict(set_properties).setContext(context).setPosition(node.pos_start, node.pos_end)
                
                methods = dict(methods, **{str(method_name): method_value}, **{str("__properties"): properties})
                class_value = Class(class_name, constructor_args, inherits_class_name, inherits_class,
                                    methods, context).setContext(context).setPosition(node.pos_start, node.pos_end)
                context.symbolTable.set_object(class_name, class_value)
        else:
            class_value = Class(class_name, constructor_args, inherits_class_name, inherits_class,
                                {}, context).setContext(context).setPosition(node.pos_start, node.pos_end)
            context.symbolTable.set_object(class_name, class_value)
        return res.success(class_value)

   
    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        args = []
        value_to_call = res.register(self.visit(
            node.node_to_call, context)) if node.node_to_call else None
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().setPosition(
            node.pos_start, node.pos_end) if hasattr(value_to_call, 'copy') else value_to_call
        if not isinstance(value_to_call, Function) and not isinstance(value_to_call, Class) and not isinstance(value_to_call, BuiltInFunction):
            return res.failure(Program.error()["Runtime"](
                {
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "'{}' is not callable".format(node.node_to_call.name.value),
                    "context": context,
                    "exit": False
                }))
        for arg_node in node.args_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res
            
        if len(args) > 0:
            for arg in args:
                if arg == None:
                    # remove None from args
                    args = [x for x in args if x != None]
                
        builtin = value_to_call.name
        
        builtins = {
            'print': BuiltInFunction_Print,
            'println': BuiltInFunction_PrintLn,
            'input': BuiltInFunction_Input,
            'inputInt': BuiltInFunction_InputInt,
            'inputFloat': BuiltInFunction_InputFloat,
            'format': BuiltInFunction_Format,
            'str': BuiltInFunction_Str,
            'range': BuiltInFunction_Range,
            'int': BuiltInFunction_Int,
            'float': BuiltInFunction_Float,
            'bool': BuiltInFunction_Bool,
            'list': BuiltInFunction_List,
            'pair' : BuiltInFunction_Pair,
            'Object': BuiltInFunction_Object,
            'max': BuiltInFunction_Max,
            'min': BuiltInFunction_Min,
            'sorted': BuiltInFunction_Sorted,
            'substr': BuiltInFunction_Substr,
            'reverse': BuiltInFunction_Reverse,
            #'Binary': BuiltInFunction_Binary,
            'line': BuiltInFunction_Line,
            'clear': BuiltInFunction_Clear,
            'typeof': BuiltInFunction_Typeof,
            'isinstanceof': BuiltInFunction_IsinstanceOf,
            'delay': BuiltInFunction_Delay,
            'exit': BuiltInFunction_Exit
        }
        
        
        
        if builtin in builtins:
            if builtin == 'print' or builtin == 'println':
                return builtins[builtin](args,node)
            return builtins[builtin](args, node, context)
        
        return_value = res.register(value_to_call.execute(args))
        
        if res.should_return():
            return res
        return_value = return_value.copy().setPosition(
            node.pos_start, node.pos_end).setContext(context) if hasattr(return_value, 'copy') else return_value
        if isinstance(return_value, NoneType):
            return res.noreturn()
        return res.success(return_value)
         
    
    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()
        
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if value is None: value = NoneType.none
            if res.should_return(): return res
        else:
            value = NoneType.none
        if value is None:  value = NoneType.none
        if isinstance(value, NoneType):
            return res.noreturn()
        return res.success_return(value)

    
    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()

    
    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.println = BuiltInFunction("println")
BuiltInFunction.exit = BuiltInFunction("exit")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.inputInt = BuiltInFunction("inputInt")
BuiltInFunction.inputFloat = BuiltInFunction("inputFloat")
BuiltInFunction.inputBool = BuiltInFunction("inputBool")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.len = BuiltInFunction("len")
#BuiltInFunction.range = BuiltInFunction("range")
BuiltInFunction.str = BuiltInFunction("str")
BuiltInFunction.int = BuiltInFunction("int")
BuiltInFunction.float = BuiltInFunction("float")
BuiltInFunction.bool = BuiltInFunction("bool")
BuiltInFunction.list = BuiltInFunction("list")
BuiltInFunction.pair = BuiltInFunction("pair")
BuiltInFunction.Object = BuiltInFunction("Object")
BuiltInFunction.line = BuiltInFunction("line")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.remove = BuiltInFunction("remove")
BuiltInFunction.sorted = BuiltInFunction("sorted")
BuiltInFunction.clearList = BuiltInFunction("clearList")
BuiltInFunction.delay = BuiltInFunction("delay")
BuiltInFunction.split = BuiltInFunction("split")
BuiltInFunction.substr = BuiltInFunction("substr")
BuiltInFunction.reverse = BuiltInFunction("reverse")
BuiltInFunction.format = BuiltInFunction("format")
BuiltInFunction.typeof = BuiltInFunction("typeof")
BuiltInFunction.isinstanceof = BuiltInFunction("isinstanceof")
BuiltInFunction.max = BuiltInFunction("max")
BuiltInFunction.min = BuiltInFunction("min")

Types.Number = Types("Number")
Types.String = Types("String")
Types.Boolean = Types("Boolean")
Types.NoneType = Types("NoneType")
Types.List = Types("List")
Types.Pair = Types("Pair")
Types.Dict = Types("Dict")
Types.Object = Types("Object")
Types.Class = Types("Class")
Types.Function = Types("Function")
Types.BuiltInFunction = Types("BuiltInFunction")
Types.BuiltInMethod = Types("BuiltInMethod")

symbolTable_ = SymbolTable()
symbolTable_.set('print', BuiltInFunction.print)
symbolTable_.set('println', BuiltInFunction.println)
symbolTable_.set('exit', BuiltInFunction.exit)
symbolTable_.set('input', BuiltInFunction.input)
symbolTable_.set('inputInt', BuiltInFunction.inputInt)
symbolTable_.set('inputFloat', BuiltInFunction.inputFloat)
symbolTable_.set('inputBool', BuiltInFunction.inputBool)
symbolTable_.set('clear', BuiltInFunction.clear)
symbolTable_.set('len', BuiltInFunction.len)
#symbolTable_.set('range', BuiltInFunction.range)
symbolTable_.set('str', BuiltInFunction.str)
symbolTable_.set('int', BuiltInFunction.int)
symbolTable_.set('float', BuiltInFunction.float)
symbolTable_.set('bool', BuiltInFunction.bool)
symbolTable_.set('list', BuiltInFunction.list)
symbolTable_.set('pair', BuiltInFunction.pair)
symbolTable_.set('Object', BuiltInFunction.Object)
symbolTable_.set('line', BuiltInFunction.line)
symbolTable_.set('append', BuiltInFunction.append)
symbolTable_.set('pop', BuiltInFunction.pop)
symbolTable_.set('extend', BuiltInFunction.extend)
symbolTable_.set('remove', BuiltInFunction.remove)
symbolTable_.set('sorted', BuiltInFunction.sorted)
symbolTable_.set('clearList', BuiltInFunction.clearList)
symbolTable_.set('delay', BuiltInFunction.delay)
symbolTable_.set('split', BuiltInFunction.split)
symbolTable_.set('substr', BuiltInFunction.substr)
symbolTable_.set('reverse', BuiltInFunction.reverse)
symbolTable_.set('format', BuiltInFunction.format)
symbolTable_.set('typeof', BuiltInFunction.typeof)
symbolTable_.set('isinstanceof', BuiltInFunction.isinstanceof)
symbolTable_.set('max', BuiltInFunction.max)
symbolTable_.set('min', BuiltInFunction.min)
symbolTable_.set('Number', Types.Number)
symbolTable_.set('String', Types.String)
symbolTable_.set('Boolean', Types.Boolean)
symbolTable_.set('NoneType', Types.NoneType)
symbolTable_.set('List', Types.List)
symbolTable_.set('Pair', Types.Pair)
symbolTable_.set('Dict', Types.Dict)
symbolTable_.set('Object', Types.Object)
symbolTable_.set('Class', Types.Class)
symbolTable_.set('Function', Types.Function)    
symbolTable_.set('BuiltInFunction', Types.BuiltInFunction)
symbolTable_.set('BuiltInMethod', Types.BuiltInMethod)
symbolTable_.setSymbol()
