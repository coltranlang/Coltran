import os
from typing import List
from Parser.stringsWithArrows import *
import Token.tokenList as tokenList
from Global.globalSymbolTable import Global
import sys
import re
import time

regex = '[+-]?[0-9]+\.[0-9]+'


class TypeOf:
    def __init__(self, type):
        self.type = type

    def getType(self):
        result = ''
        if self.type == 'true':
            result = 'boolean'
        elif self.type == 'false':
            result = 'boolean'
        elif self.type == 'none':
            result = 'none'
        elif self.type == 'str':
            result = 'string'
        elif isinstance(self.type, Number):
            if re.match(regex, str(self.type)):
                result = 'float'
            else:
                result = 'int'
        else:
            if isinstance(self.type, str) or isinstance(self.type, String):
                result = 'string'
            elif isinstance(self.type, bool) or isinstance(self.type, Boolean):
                result = 'boolean'
            elif isinstance(self.type, list) or isinstance(self.type, List):
                result = 'list'
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
     

        def Type(detail):
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

        methods = {
            'Default': Default,
            'Error': Error,
            'IllegalCharacter': IllegalCharacter,
            'Syntax': Syntax,
            'Runtime': Runtime,
            'Type': Type
        }
        return methods

    def NoneValue():
        return 'none'

    def print(*args):
        for arg in args:
            print(arg)

    def printWithType(*args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))

    def printError(*args):
        for arg in args:
            print(arg)

    def printErrorExit(*args):
        for arg in args:
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
            result += f'\nFile {detail["pos_start"].fileName}, line {str(pos.line + 1)}, in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        return '\nStack trace (most recent call last):\n' + result


class RuntimeResult:
    def __init__(self):
        self.reset()

    def reset(self):
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
        self.reset()
        self.error = error
        return self

    def noreturn(self):
        self.reset()
        return self

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

    def added_to(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'+' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"Illegal operation '+' not allowed",
            'context': self.context
        })

    def subtracted_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'-' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"Illegal operation '-' not allowed",
        })

    def multiplied_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'*' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '*' not allowed",
            'context': self.context
        })

    def divided_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'/' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '/' not allowed",
            'context': self.context
        })

    def powred_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'**' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '**' not allowed",
            'context': self.context
        })

    def modulo(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'%' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '%' not allowed",
            'context': self.context
        })

    def get_comparison_eq(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'==' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '==' not allowed",
            'context': self.context
        })

    def get_comparison_ne(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'!=' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '!=' not allowed",
            'context': self.context
        })

    def get_comparison_lt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '<' not allowed",
            'context': self.context
        })

    def get_comparison_gt(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '>' not allowed",
            'context': self.context
        })

    def get_comparison_lte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'<=' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '<=' not allowed",
            'context': self.context
        })

    def get_comparison_gte(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'>=' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '>=' not allowed",
            'context': self.context,
        })

    def and_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'&&' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '&&' not allowed",
            'context': self.context
        })

    def or_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'||' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '||' not allowed",
            'context': self.context
        })

    def notted(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'!' operator is not allowed for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}" if hasattr(self, "value") and hasattr(other, "value") else f"'Illegal operation '!' not allowed",
            'context': self.context
        })

    def execute(self, args):
        return RuntimeResult().failure(self.illegal_operation_typerror())

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return "false"

    def illegal_operation(self, error, other=None):
        if not other:
            other = self
        if hasattr(other, 'value'):
            return Program.error()["Syntax"]({
                'message': f'Illegal operation for type {TypeOf(self.value).getType()} and {TypeOf(other.value).getType()}' if self.value != None and other.value != None else f'Illegal operation for type {TypeOf(self.value).getType()}',
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

    def none_value(self):
        return Program.NoneValue()

    def illegal_operation_typerror(self, error, other=None):
        errorDetail = {
            'pos_start': error['pos_start'],
            'pos_end': error['pos_end'],
            'message': error['message'],
            'context': error['context'],
            'exit': error['exit'] if 'exit' in error else True
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
        return Program.error()['Type'](errorDetail)


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
        self.value = value
        
        
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        self.value = "true" if value else "false"
        return self

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't add {TypeOf(self.value).getType()} to {TypeOf(other.value).getType()}",
            'context': self.context
        }
        if isinstance(other, Number):
            if self.value == "none" or other.value == "none":
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            if self.value == "true" or self.value == "false" or other.value == "true" or other.value == "false":
                return None, self.illegal_operation_typerror(error)
            if self.value == "none" or other.value == "none":
                return None, self.illegal_operation_typerror(error)
            else:
                return Number(self.value + other.value).setContext(self.context), None
        else:
            return "None", self.illegal_operation(other)

    def subtracted_by(self, other):
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't subtract {TypeOf(self.value).getType()} from {TypeOf(other.value).getType()}",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't multiply {TypeOf(self.value).getType()} with {TypeOf(other.value).getType()}",
            'context': self.context,
            'exit': False
        }
        if self.value == "none" or other.value == "none":
            return None, self.illegal_operation_typerror(error)
        if hasattr(other, 'value'):
            if other.value == "true" or self.value == "true":
                return String(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
            elif other.value == "false" or self.value == "false":
                return String(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None

        if isinstance(other, Number):
            if other.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't multiply '{type(self.value).__name__}' of type 'none'",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't divide {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            if other.value == 0:
                return None, Program.error()['Runtime']({
                    'pos_start': other.pos_start,
                    'pos_end': other.pos_end,
                    'message': 'division by zero',
                    'context': self.context,
                    'exit': False
                })
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def powred_by(self, other):
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't power {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def modulo(self, other):
        if isinstance(other, Number):
            if other.value == "none" or self.value == "none":
                error = {
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"can't perform modulo on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                    'context': self.context
                }
                return None, self.illegal_operation_typerror(error)
            return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) < setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) > setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) <= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) >= setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def and_by(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "none" or self.value == "none":
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform and on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                'context': self.context
            }
            return None, self.illegal_operation_typerror(error)
        if isinstance(other, String):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def or_by(self, other):
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def notted(self):
        return self.setTrueorFalse(self.value).setContext(self.context), None

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
    def __init__(self, value):
        super().__init__()
        self.value = value
    def setPosition(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context=None):
        self.context = context
        return self

    def setTrueorFalse(self, value):
        self.value = "true" if value else "false"
        return self

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"can't perform concatenation on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}" if hasattr(other, 'value') and hasattr(self, 'value') else f"can't perform concatenation on type none",
            'context': self.context,
            'exit': False
        }
        if hasattr(other, 'value') and hasattr(self, 'value'):
            if other.value == "true" or other.value == "false" or other.value == "none" or self.value == "true" or self.value == "false" or self.value == "none":
                return None, self.illegal_operation_typerror(error, other)
        if isinstance(other, Number):
            return String(setNumber(str(self.value)) + setNumber(str(other.value))).setContext(self.context), None
        if isinstance(other, String):
            return String(setNumber(str(self.value)) + setNumber(str(other.value))).setContext(self.context), None
        else:
            return "None", self.illegal_operation(error, other)

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

    def and_by(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)), None
        elif other.value == "none" or self.value == "none":
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"can't perform and on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
                'context': self.context,
                'exit': False
            }
            return None, self.illegal_operation_typerror(error)
        if isinstance(other, String):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return String(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if other.value == "true":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "false":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        elif other.value == "none":
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, String):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Number):
            return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(self, other)

    def copy(self):
        copy = String(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return "true" if len(self.value) > 0 else "false"

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f'"{self.value}"'


class Boolean:
    def __init__(self, value):
        self.value = value
        self.setPosition(0, 0)
        self.setContext(None)

    def setPosition(self, pos_start, pos_end):
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

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


class NoneType:
    def __init__(self):
        self.setPosition(0, 0)
        self.setContext("none")

    def setPosition(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def setContext(self, context):
        self.context = context
        return self

    def copy(self):
        copy = NoneType()
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        return "none"

    def __repr__(self):
        return f'none'


Boolean.true = Boolean("true")
Boolean.false = Boolean("false")
NoneType.none = NoneType()


class List(Value):
    def __init__(self, elements=None):
        super().__init__()
        self.elements = elements if elements is not None else []
        self.value = self.elements

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, "none"
        else:
            return None, self.illegal_operation(error, other)

    def divided_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Did you mean to use the `:` operator to get the element at a certain index?",
            'context': self.context,
            'exit': False
        }
        return None, self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, self.illegal_operation(error, other)

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Illegal operation on list",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, self.none_value()
        else:
            return None, self.illegal_operation(error, other)

    def get_element_at(self, index):
        return self.elements[index]

    def set_element_at(self, index, value):
        self.elements[index] = value
        return self

    def length(self):
        return len(self.elements)

    def copy(self):
        copy = List(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        # returnlist with brackets
        if len(self.elements) > 0:
            return f"[{', '.join([str(x) for x in self.elements])}]"
        else:
            return "[]"


class BaseTask(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbolTable = Global(new_context.parent.symbolTable)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()
        if len(args) > len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} arguments given, but {self.name}() expected {len(arg_names)}",
                'context': self.context,
                'exit': True
            }))

        if len(args) < len(arg_names):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{len(args)} few arguments given, but {self.name}() expects {len(arg_names)}",
                'context': self.context,
                'exit': True
            }))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_context):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Task(BaseTask):
    def __init__(self, name, body_node, arg_names, implicit_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.implicit_return = implicit_return

    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        res.register(self.check_and_populate_args(
            self.arg_names, args, exec_context))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.func_return_value == None:
            return res

        return_value = (
            value if self.implicit_return else None) or res.func_return_value or NoneType.none
        return res.success(return_value)

    def copy(self):
        copy = Task(self.name, self.body_node,
                    self.arg_names, self.implicit_return)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<Task {str(self.name)}()>, {self.arg_names if len(self.arg_names) > 0 else '[no args]'}"


class Class(Value):
    def __init__(self, name, inherit_from, body_node, pos_start, pos_end):
        super().__init__()
        self.name = name
        self.inherit_from = inherit_from
        self.body_node = body_node
        self.pos_start = pos_start
        self.pos_end = pos_end
        
        self.methods = {}
        self.attributes = {}
    def set_method(self, name, method):
        self.methods[name] = method
    def set_attribute(self, name, attribute):
        self.attributes[name] = attribute
    def get_method(self, name):
        return self.methods[name]
    def get_attribute(self, name):
        return self.attributes[name]
    
    def copy(self):
        copy = Class(self.name, self.inherit_from, self.body_node,
                    self.pos_start, self.pos_end)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<Class {str(self.name)}>"

class BuiltInTask(BaseTask):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RuntimeResult()
        exec_context = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visiit)

        res.register(self.check_and_populate_args(
            method.arg_names, args, exec_context))
        if res.should_return():
            return res

        return_value = res.register(method(exec_context))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visiit(self, node, exec_context):
        res = RuntimeResult()
        return res.failure(Program.error()['Runtime']({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name} is not a supported built-in task",
            'context': self.context
        }))

    def execute_len(self, exec_context):
        res = RuntimeResult()
        value = exec_context.symbolTable.get("value")
        if isinstance(value, Number):
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"type {TypeOf(value).getType()} is not supported",
                'context': self.context
            }))
        if isinstance(value, List):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
        if isinstance(value, String):
            return res.success(Number(len(value.value)).setPosition(self.pos_start, self.pos_end).setContext(self.context))
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
                'context': self.context
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
                    'context': self.context
                }))
        else:
            return res.failure(Program.error()['Runtime']({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"First argument to 'pop' must be a list.",
                'context': self.context
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
        copy = BuiltInTask(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<{str(self.name)}()>, [ built-in task ]"


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visiit)
        return method(node, context)

    def no_visiit(self, node, context):
        return RuntimeResult().success("None")

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
            String(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

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
            Number(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value
        value = context.symbolTable.get(var_name)
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
            Program.error()['Error']({
                'name': 'IdentifierError',
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f'{var_name} is not defined',
                'context': context,
                'exit': False
            })
            return res.noreturn()
        value = value.copy().setPosition(node.pos_start, node.pos_end).setContext(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.variable_name_token.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res
        if node.variable_keyword_token == "let":
            if value is None:
                value = NoneType.none
            context.symbolTable.set(var_name, value)
        elif node.variable_keyword_token == "final":
            if value is None:
                value = NoneType.none
            context.symbolTable.set_final(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()
        try:
            left = res.register(self.visit(node.left_node, context))
            if res.should_return():
                return res
            right = res.register(self.visit(node.right_node, context))
            if node.op_tok.type == tokenList.TT_PLUS:
                result, error = left.added_to(right)
            elif node.op_tok.type == tokenList.TT_MINUS:
                result, error = left.subtracted_by(right)
            elif node.op_tok.type == tokenList.TT_MUL:
                result, error = left.multiplied_by(right)
            elif node.op_tok.type == tokenList.TT_DIVISION:
                result, error = left.divided_by(right)
            elif node.op_tok.type == tokenList.TT_POWER:
                result, error = left.powred_by(right)
            elif node.op_tok.type == tokenList.TT_MOD:
                result, error = left.modulo(right)
            elif node.op_tok.type == tokenList.TT_COLON:
                result, error = left.get_index(right)
            elif node.op_tok.type == tokenList.TT_EQEQ:
                result, error = left.get_comparison_eq(right)
            elif node.op_tok.type == tokenList.TT_NEQ:
                result, error = left.get_comparison_ne(right)
            elif node.op_tok.type == tokenList.TT_LT:
                result, error = left.get_comparison_lt(right)
            elif node.op_tok.type == tokenList.TT_GT:
                result, error = left.get_comparison_gt(right)
            elif node.op_tok.type == tokenList.TT_LTE:
                result, error = left.get_comparison_lte(right)
            elif node.op_tok.type == tokenList.TT_GTE:
                result, error = left.get_comparison_gte(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'and'):
                result, error = left.and_by(right)
            elif node.op_tok.matches(tokenList.TT_KEYWORD, 'or'):
                result, error = left.or_by(right)
            if error:
                return res.failure(error)
            else:
                return res.success(result.setPosition(node.pos_start, node.pos_end))
        except AttributeError or TypeError or ValueError:
            return RuntimeResult()

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        error = None

        if node.op_tok.type == tokenList.TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(tokenList.TT_KEYWORD, 'not'):
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

            if condition_value.is_true():
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

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res
            if not condition.is_true():
                break
            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                return res

            if res.loop_continue:
                continue

            if res.loop_break:
                break

            elements.append(value)

        return res.success(NoneType.none if node.implicit_return else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))

    def visit_TaskDefNode(self, node, context):
        res = RuntimeResult()
        task_name = node.task_name_token.value if node.task_name_token else "None"
        body_node = node.body_node
        # methods = node.methods
        # #task_methods = []
        # for method in methods:
        #     #task_methods.append(res.register(self.visit(method, context)))
        #     if res.should_return(): return res
        #     method_name = method.task_name_token.value
        #     method_body = method.body_node
        #     method_args = [arg.value for arg in method.args_name_tokens]
        #     task_method = Task(method_name, method_body, method_args, False).setContext(context).setPosition(method.pos_start, method.pos_end)
        #     t = Context(context.symbolTable.set(method_name, task_method))
        #     print(t, "t")
            
        arg_names = [arg_name.value for arg_name in node.args_name_tokens]
        task_value = Task(task_name, body_node, arg_names, node.implicit_return).setContext(
            context).setPosition(node.pos_start, node.pos_end)
        if node.task_name_token:
            context.symbolTable.set(task_name, task_value)

        # if task_name in context.symbolTable.symbols:
        #     return res.failure(Program.error()["Runtime"]({
        #         "pos_start": node.pos_start,
        #         "pos_end": node.pos_end,
        #         "message": "Task with name '{}' already defined".format(task_name),
        #         "context": context
        #     }))
        # print(context.symbolTable.symbols)
        return res.success(task_value)

    def visit_ClassNode(self, node, context):
        res = RuntimeResult()
        class_name = node.class_name_token.value
        inherits = node.inherits_name
        body_node = node.body_node
        if inherits:
            inherits_name = inherits.value
            if inherits_name not in context.symbolTable.symbols:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "Class '{}' not found".format(inherits_name),
                    "context": context,
                    "exit": False
                }))
            
            if not isinstance(context.symbolTable.get(inherits_name), Class):
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "{} is not a class".format(inherits_name),
                    "context": context,
                    "exit": False
                }))
                
            if inherits_name == class_name:
                return res.failure(Program.error()["Runtime"]({
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": "Class {} cannot inherit from itself".format(class_name),
                    "context": context,
                    "exit": False
                }))
                
            class_value = Class(class_name, inherits_name, body_node, node.pos_start, node.pos_end).setContext(context).setPosition(node.pos_start, node.pos_end)
        else:
            class_value = Class(class_name, None, body_node, node.pos_start, node.pos_end).setContext(context).setPosition(node.pos_start, node.pos_end)
        context.symbolTable.set(class_name, class_value)
        return res.success(class_value)

        # if task_name in context.symbolTable.symbols:
        #     return res.failure(Program.error()["Runtime"]({
    
    # def visit_MethodCallNode(self, node, context):
    #     res = RuntimeResult()
    #     print(node)
    #     method_name = node.method_name_token.value
    #     args = []
    #     value = res.register(self.visit(node.node_to_call, context))
        
    #     if res.should_return():
    #         return res

    #     if not isinstance(value, Task):
    #         return res.failure(Program.error()['Runtime']({
    #             'pos_start': node.pos_start,
    #             'pos_end': node.pos_end,
    #             'context': context,
    #             'message': 'Method called on non-task object',
    #             'exit': False
    #         }))
            
    #     task = value
    #     if method_name not in task.methods:
    #         return res.failure(Program.error()['Runtime']({
    #             'pos_start': node.pos_start,
    #             'pos_end': node.pos_end,
    #             'context': context,
    #             'message': 'Method {} not defined for task {}'.format(method_name, task.name),
    #             'exit': False
    #         }))
    #     method = task.methods[method_name]
    #     if len(node.args) != len(method.arg_names):
    #         return res.failure(Program.error()['Runtime']({
    #             'pos_start': node.pos_start,
    #             'pos_end': node.pos_end,
    #             'context': context,
    #             'message': 'Method {} takes {} arguments but {} were given'.format(method_name, len(method.arg_names), len(node.args)),
    #             'exit': False
    #         }))
            
    #     for arg_value, arg_name in zip(node.args, method.arg_names):
    #         arg_value_obj = res.register(self.visit(arg_value, context))
    #         if res.should_return():
    #             return res
    #         args.append(arg_value_obj)
    #     return res.success(method.execute(task, args))

    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        try:
            args = []

            value_to_call = res.register(self.visit(
                node.node_to_call, context)) if node.node_to_call else None
            if res.should_return():
                return res
            value_to_call = value_to_call.copy().setPosition(node.pos_start, node.pos_end)

            for arg_node in node.args_nodes:
                args.append(res.register(self.visit(arg_node, context)))
                if res.should_return():
                    return res
            for arg in args:
                if arg is None:
                    args = []
            builtintask = value_to_call.name
            if builtintask == "print":
                for arg in args:
                    value = str(arg)
                    print(value, end="")
                return res.success(String(str(NoneType.none)).setPosition(node.pos_start, node.pos_end))

            if builtintask == "println":
                for arg in args:
                    value = str(arg)
                    print(value)
                return res.success(String(str(NoneType.none)).setPosition(node.pos_start, node.pos_end))

            if builtintask == "exit":
                if len(args) == 0:
                    sys.exit()
                elif len(args) > 1:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{len(args)} arguments given, but exit() takes 0 or 1 argument(s)",
                        "context": context
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
                            "context": context
                        }))
                else:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{args[0]} is not a valid argument for exit()",
                        "context": context
                    }))

            if builtintask == "input":
                if len(args) > 1:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{len(args)} arguments given, but input() takes 0 or 1 argument(s)",
                        "context": context
                    }))
                if len(args) == 0:
                    input_value = input()
                    return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
                if len(args) == 1:
                    if isinstance(args[0], String):
                        input_value = input(args[0].value)
                        return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
                    else:
                        return res.failure(Program.error()["Runtime"]({
                            "pos_start": node.pos_start,
                            "pos_end": node.pos_end,
                            'message': f"{args[0]} is not a valid argument for input()",
                            "context": context
                        }))

            if builtintask == 'inputInt':
                if len(args) > 1:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{len(args)} arguments given, but intInput() takes 0 or 1 argument(s)",
                        "context": context
                    }))
                if len(args) == 0:
                    input_value = int(input())
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
                        return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
                    else:
                        return res.failure(Program.error()["Runtime"]({
                            "pos_start": node.pos_start,
                            "pos_end": node.pos_end,
                            'message': f"{args[0].value} is not a valid argument for intInput()",
                            "context": context
                        }))

            if builtintask == 'inputFloat':
                if len(args) > 1:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{len(args)} arguments given, but floatInput() takes 0 or 1 argument(s)",
                        "context": context
                    }))
                if len(args) == 0:
                    input_value = float(input())
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
                        return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
                    else:
                        return res.failure(Program.error()["Runtime"]({
                            "pos_start": node.pos_start,
                            "pos_end": node.pos_end,
                            'message': f"{args[0].value} is not a valid argument for floatInput()",
                            "context": context
                        }))

            if builtintask == 'clear':
                if len(args) > 0:
                    return res.failure(Program.error()["Runtime"]({
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        'message': f"{len(args)} arguments given, but clear() takes no argument",
                        "context": context
                    }))
                if len(args) == 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return res.success(None)

            if builtintask == 'delay':
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

            # if builtintask == 'len':
                # if len(args) > 1:
                #     return res.failure(Program.error()["Runtime"]({
                #         "pos_start": node.pos_start,
                #         "pos_end": node.pos_end,
                #         'message': f"{len(args)} arguments given, but len() takes 1 argument",
                #         "context": context
                #     }))
                # if len(args) == 0:
                #     return res.failure(Program.error()["Runtime"]({
                #         "pos_start": node.pos_start,
                #         "pos_end": node.pos_end,
                #         'message': f"{len(args)} arguments given, but len() takes 1 argument",
                #         "context": context
                #     }))
                # if len(args) == 1:
                    # if isinstance(args[0], List):
                    #     return res.success(Number(len(args[0].elements)).setPosition(node.pos_start, node.pos_end).setContext(context))
                    # if isinstance(args[0], String):
                    #     return res.success(Number(len(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
                    # else:
                    #     return res.failure(Program.error()["Runtime"]({
                    #         "pos_start": node.pos_start,
                    #         "pos_end": node.pos_end,
                    #         'message': f"{args[0].value} is not a valid argument for len()",
                    #         "context": context
                    #     }))

            # if builtintask == 'append':
            #     if len(args) > 2:
            #         return res.failure(Program.error()["Runtime"]({
            #             "pos_start": node.pos_start,
            #             "pos_end": node.pos_end,
            #             'message': f"{len(args)} arguments given, but append() takes 2 argument",
            #             "context": context
            #         }))
            #     if len(args) == 0:
            #         return res.failure(Program.error()["Runtime"]({
            #             "pos_start": node.pos_start,
            #             "pos_end": node.pos_end,
            #             'message': f"{len(args)} arguments given, but append() takes 2 argument",
            #             "context": context
            #         }))
            #     if len(args) == 1:
            #         return res.failure(Program.error()["Runtime"]({
            #             "pos_start": node.pos_start,
            #             "pos_end": node.pos_end,
            #             'message': f"{len(args)} arguments given, but append() takes 2 argument",
            #             "context": context
            #         }))
            #     if len(args) == 2:
            #         if isinstance(args[0], List):
            #             args[0].elements.append(args[1])
            #             return res.success(List(args[0].elements).setPosition(node.pos_start, node.pos_end).setContext(context))
            #         else:
            #             return res.failure(Program.error()["Runtime"]({
            #                 "pos_start": node.pos_start,
            #                 "pos_end": node.pos_end,
            #                 'message': f"{args[0].value} is not a valid argument for append(), argument must be a list",
            #                 "context": context
            #             }))

            return_value = res.register(value_to_call.execute(args))
            if res.should_return():
                return res
            return_value = return_value.copy().setPosition(
                node.pos_start, node.pos_end).setContext(context)
            if isinstance(return_value, NoneType):
                return res.noreturn()
            return res.success(return_value)
        except AttributeError or TypeError or ValueError:
            return RuntimeResult()

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
