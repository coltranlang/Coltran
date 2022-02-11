#  Copyright (c) 2021, Alden Authors.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of Alden Org. nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# File:
#   Parser/parser.py
# Author:
#   Kehinde Akinsanya
# Created:
#   October 28, 2021
# Description:
#   This file contains the parser for the language.


from os import access, error, path
from re import S, split
from types import NoneType

from Parser.stringsWithArrows import *
from Token.token import Token
from Token import tokenList
from Lexer.lexer import Lexer
import sys
import re
sys.path.append('./Parser/')
# def match(pattern, text, pos_start, pos_end):
#     matches = []
#     if len(pattern) == 0:
#         return matches
#     if len(text) == 0:
#         return matches
#     for i in len(text):
#         if pattern[0] == text[i]:
#             string = text.substring(i, i+1)
#             if len(pattern) == 1:
#                 matches.append(string)
#             else:
#                 matches.append(match(pattern[1:], text[i+1:], i+1, i+1))
#     return matches


class Regex:
    def __init__(self):
            self.value = None

    def parse(self, text, pos_start, pos_end):
        wildcard_token = Token(tokenList.TT_WILDCARD,
                                None, pos_start, pos_end)
        start_token = Token(tokenList.TT_START, None, pos_start, pos_end)
        end_token = Token(tokenList.TT_END, None, pos_start, pos_end)
        comma_token = Token(tokenList.TT_COMMA, None, pos_start, pos_end)
        arrow_token = Token(tokenList.TT_ARROW, None, pos_start, pos_end)
        plus_token = Token(tokenList.TT_PLUS, None, pos_start, pos_end)
        star_token = Token(tokenList.TT_STAR, None, pos_start, pos_end)
        question_token = Token(tokenList.QUESTION,
                                None, pos_start, pos_end)
        pipe_token = Token(tokenList.TT_PIPE, None, pos_start, pos_end)

    def compile(self, pattern):
        self.pattern = re.compile(pattern)
        return self

    def match(self, text):
        return self.pattern.findall(text)

    def sub(self, pattern, text):
            return self.pattern.sub(pattern, text)


def lower(text):
    return text.islower()


def isOnlyLetters(text):
    return text.isalpha()


def isFirstLetterUpper(text):
    return text[0].isupper()


def has_at_symbol(text):
    if len(text) == 0:
        return False
    if text[0] == "@":
        return True
    return False


builtin_modules = {
    'math': 'math',
    'http': 'http',
    'file': 'file',
    'system': 'system',
    'os': 'os',
    'date': 'date',
    're': 're',
    'random': 'random',
    'hashlib': 'hashlib',
    'vna': 'vna',
}

operation_methods = {
    'PLUS_EQ': 'add',
    'MINUS_EQ': 'sub',
    'MUL_EQ': 'mul',
    'DIV_EQ': 'div',
    'FLOOR_DIV_EQ': 'floor_div',
    'MOD_EQ': 'mod',
    'POWER_EQ': 'pow'
}


def is_varags(string):
    if len(string) == 0:
        return False
    return string[0] == '*'


def is_kwargs(string):
    if len(string) == 0:
        return False
    return string[0] == '**'


class A_SyntaxError(Exception):
    def __init__(self, error_details):
        super().__init__()
        self.name = 'SyntaxError'
        self.error_details = error_details
        self.error_details['name'] = self.name
        self.setError()
        
    def setError(self):
        if self.error_details['exit']:
            Program.printErrorExit(Program.asString(self.error_details))
        else:
            Program.printError(Program.asString(self.error_details))


class Program:
    def error():
        def Default(detail):
            if detail['exit']:
                Program.printErrorExit(Program.asString(detail))
            else:
                Program.printError(Program.asString(detail))

        def Syntax(detail):
            isDetail = {
                'name': 'SyntaxError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context'],
                'exit': True
            }

            raise A_SyntaxError(isDetail)

        def Runtime(options):
            error = f'RuntimeError: {options["originator"]}, line {options["line"]}'
            Program.printErrorExit(error)

        def NameError(detail):
            isDetail = {
                'name': 'NameError',
                'type': 'name error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))

        def KeyError(detail):
            isDetail = {
                'name': 'KeyError',
                'type': 'key error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))

        def ValueError(detail):
            isDetail = {
                'name': 'ValueError',
                'type': 'value error',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))

        methods = {
            'Default': Default,
            'Syntax': Syntax,
            'Runtime': Runtime,
            'NameError': NameError,
            'KeyError': KeyError,
            'ValueError': ValueError,
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
        result = Program.generateTraceBack(detail)
        name = detail['name']
        message = detail['message']
        pos_start = detail['pos_start']
        pos_end = detail['pos_end']
        fileText = pos_start.fileText
        result += '' + stringsWithArrows(fileText, pos_start, pos_end)
        result += f'\n{name}: {message}\n'
        return result

    def generateTraceBack(detail):
        result = ''
        pos = detail['pos_start']
        context = detail['context']
        while context:
            result = '' + \
                    f'   File "{pos.fileName}", (at line:{pos.line + 1}, col:{pos.column + 1}) in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        return 'Traceback (most recent call last):\n' + result


class StatementsNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.id = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.name = tok
        self.tok = tok
        self.id = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class DocStringNode:
    def __init__(self, tok):
        self.name = tok
        self.tok = tok
        self.id = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class ByteStringNode:
    def __init__(self, tok):
        self.name = tok
        self.tok = tok
        self.id = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringInterpNode:
    def __init__(self, expr, values_to_replace, string_to_interp, pos_start, pos_end, inter_pv=None):
        self.expr = expr
        self.values_to_replace = values_to_replace
        self.string_to_interp = string_to_interp
        self.inter_pv = inter_pv
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f'{self.values_to_replace}'


class ListNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class PairNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class DictNode:
    def __init__(self, properties, keys, values, pos_start, pos_end):
        self.properties = properties
        self.keys = keys
        self.values = values
        self.pos_start = pos_start
        self.pos_end = pos_end
        
            
class SetNode:
    def __init__(self, sets, pos_start, pos_end):
        self.sets = sets
        self.pos_start = pos_start
        self.pos_end = pos_end


class VarAssignNode:
    def __init__(self, variable_name_token, value_node, variable_keyword_token):
        self.variable_keyword_token = variable_keyword_token
        self.variable_name_token = variable_name_token
        self.id = variable_name_token
        self.value_node = value_node
        if type(self.variable_name_token).__name__ == "tuple":
            for t in self.variable_name_token:
                self.pos_start = t.pos_start
                self.pos_end = t.pos_end
        elif type(self.variable_name_token).__name__ == "list":
            for t in self.variable_name_token:
                self.pos_start = t.pos_start
                self.pos_end = t.pos_end
        else:
            self.pos_start = self.variable_name_token.pos_start
            if self.value_node == None:
                self.pos_end = self.variable_name_token.pos_end


class VarAccessNode:
    def __init__(self, name, type=None):
        self.name = name
        self.id = name
        self.type = type
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class VarReassignNode:
    def __init__(self, name, value=None, operation=None, property=None):
        res = ParseResult()
        self.name = name
        self.id = name
        self.value = value
        self.operation = operation
        self.property = property

        if self.name == "" or self.name == None:
            pass
        else:
            self.pos_start = self.name.pos_start
            self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class PropertyNode:
    def __init__(self, name, property):
        self.name = name
        self.value = name.value if hasattr(name, 'value') else name
        self.id = name
        self.property = property
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.property}'


class PropertySetNode:
    def __init__(self, name, property, value, type_=None):
        self.name = name
        self.id = name
        self.property = property
        self.value = value
        self.type_ = type_
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end if self.value != None else self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class IndexNode:
    def __init__(self, name, index, value_=None, type_=None):
        self.name = name
        self.id = name
        self.index = index
        self.value_ = value_
        self.type = type_
        self.pos_start = self.name.pos_start
        self.pos_end = self.index.pos_end

    def __repr__(self):
        return f'{self.name}'


class SliceNode:
    def __init__(self, name, start, end, step=None, type=None):
        self.name = name
        self.id = name
        self.start = start
        self.end = end
        self.step = step
        self.type = type
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end if self.end is None else self.end.pos_end

    def __repr__(self):
        return f'{self.name}'


class SpreadNode:
    def __init__(self, assign_token, name, value, pos_start, pos_end, _type=None):
        self.assign_token = assign_token
        self.name = name
        self.id = name
        self.value = value
        self.pos_start = pos_start
        self.pos_end = pos_end
        self._type = _type

    def __repr__(self):
        return f'{self.name}'


class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.value = self.tok.value
        if tok.value == 'true':
            self.value = True
        elif tok.value == 'false':
            self.value = False
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class NoneNode:
    def __init__(self, tok):
        self.tok = tok
        self.id = tok
        self.value = self.tok.value
        if tok.value == 'none':
            self.value = None
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        res = ParseResult()
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (
            self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

    def __repr__(self):
        return f'IfNode'


class ForNode:
    def __init__(self, var_name_token, start_value_node, end_value_node, step_value_node, body_node, return_null):
        self.var_name_token = var_name_token
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.body_node.pos_end


class InNode:
    def __init__(self, iterable_node, iterators, body_node, return_null):
        self.iterable_node = iterable_node
        self.iterators = iterators
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.iterable_node.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class MatchNode:
    def __init__(self, expression, cases, default_case):
        self.expression = expression
        self.cases = cases
        self.default_case = default_case

        self.pos_start = self.expression.pos_start
        if self.default_case:
            self.pos_end = self.default_case['pos_end']
        else:
            self.pos_end = self.cases[len(
                    self.cases) - 1]['pos_end'] if self.cases else self.expression.pos_end


class RaiseNode:
    def __init__(self, expression):
        self.expression = expression
        self.pos_start = self.expression.pos_start
        self.pos_end = self.expression.pos_end


class DelNode:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
        self.pos_start = self.identifier.pos_start
        self.pos_end = self.identifier.pos_end


class AttemptNode:
    def __init__(self, attempt_statement, catches, finally_statement, pos_start, pos_end):
        self.attempt_statement = attempt_statement
        self.catches = catches
        self.finally_statement = finally_statement
        self.pos_start = pos_start
        self.pos_end = pos_end


class FunctionNode:
    def __init__(self, def_name_token, args_name_tokens, body_node, implicit_return, default_values, type=None, doc=None, type_hints=[]):
        self.def_name_token = def_name_token
        self.id = def_name_token
        self.args_name_tokens = args_name_tokens
        self.body_node = body_node
        self.implicit_return = implicit_return
        self.default_values = default_values
        self.type = type
        self.doc = doc
        self.type_hints = type_hints
        if self.def_name_token:
            self.pos_start = self.def_name_token.pos_start
        elif len(self.args_name_tokens) > 0:
            self.pos_start = self.args_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end


class ObjectNode:
    def __init__(self, object_name, properties, other=None):
        self.object_name = object_name
        self.id = object_name
        self.other = other
        if self.other != None and self.other['name'] == "module":
            self.type = "module"
            self.as_name = self.other['as_name']
        object_properties = []
        for prop in properties:
            object_properties.append(prop)
            if hasattr(prop['value'], 'pos_end'):
                self.pos_end = prop['value'].pos_end if len(
                    properties) != 0 else self.object_name.pos_end
            else:
                self.pos_end = self.object_name.pos_end
        self.properties = object_properties
        self.pos_start = self.object_name.pos_start
        self.object = {
            'name': self.object_name.value,
            'properties': self.
            properties
        }





class ModuleObject:
    def __init__(self, object_name, properties, other):
        self.object_name = object_name
        self.id = object_name
        self.other = other
        self.as_name = self.other['as_name']
        object_properties = []
        for prop in properties:
            object_properties.append(prop)
            if hasattr(prop['value'], 'pos_end'):
                self.pos_end = prop['value'].pos_end if len(
                    properties) != 0 else self.object_name.pos_end
            else:
                self.pos_end = self.object_name.pos_end
        self.properties = object_properties
        self.pos_start = self.object_name.pos_start
        self.object = {
            'name': self.object_name.value,
            'properties': self.
            properties
        }


class ClassNode:
    def __init__(self, class_name,inherits_class_name, methods, class_fields_modifiers, doc=None):
        self.id = class_name
        self.class_name = class_name
        self.inherits_class_name = inherits_class_name
        self.methods = methods
        self.class_fields_modifiers = class_fields_modifiers
        self.doc = doc
        self.pos_start = self.class_name.pos_start
        self.pos_end = self.class_name.pos_end
        self.class_object = {
            'name': self.class_name.value,
            'properties': self.methods
        }

    def __repr__(self):
        return f'{self.class_name}'


class CallNode:
    def __init__(self, node_to_call, args_nodes, keyword_args_list=None, has_unpack=None):
        self.id = node_to_call
        self.node_to_call = node_to_call
        self.args_nodes = args_nodes
        self.keyword_args_list = keyword_args_list
        self.has_unpack = has_unpack
        self.pos_start = self.node_to_call.pos_start
        self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        return f'{self.node_to_call}({self.args_nodes})'


class ImportNode:
    def __init__(self, module_name, properties, module_alias, module_path, module_name_as,type_,mods=None, from_module_name=None):
        self.id = module_name
        self.module_name = module_name
        self.properties = properties if len(properties) > 0 else None
        self.module_alias = module_alias
        self.module_path = module_path
        self.module_name_as = module_name_as
        self.type_ = type_
        self.mods = mods
        self.from_module_name = from_module_name
        if self.module_alias:
            self.pos_start = self.module_alias.pos_start
        else:
            self.pos_start = self.module_name.pos_start
        if len(properties) > 0:
            self.pos_end = self.properties[len(properties) - 1].pos_end
        else:
            self.pos_end = self.module_name.pos_end
        self.module_object = {
            'name': self.module_name.value,
            'path': self.module_path if self.module_path else None
        }

    def __repr__(self):
        return f'{self.module_name}'


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, scope,pos_start, pos_end):
        self.scope = scope
        self.pos_start = pos_start
        self.pos_end = pos_end


class FreezeNode:
    def __init__(self, object):
        self.object = object
        self.pos_start = self.object.pos_start
        self.pos_end = self.object.pos_end
    

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count if res else 0
        self.advance_count += res.advance_count if res else 0
        if res:
            if res.error:
                self.error = res.error
        else:
            self.error = ''
        return res.node if res else ''

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self

    def noreturn(self):
        return self


class Parser:

    def __init__(self, tokens, file_name, context, position=None):
        self.tokens = tokens
        self.file_name = file_name
        self.context = context
        self.position = position
        # get file name without extension
        #self.file_name_no_ext = self.file_name.split('/')[2].split('.')[0]
        self.tok_index = -1
        self.error = Program.error()
        self.error_detected = False
        self.scope = ''
        self.if_scope = False
        self.advance()

    def advance(self):
        self.tok_index += 1
        self.update_current_tok()
        return self.current_token

    def peek(self, step=1):
        self.tok_index += step
        if self.tok_index < len(self.tokens):
            self.update_current_tok()
            return self.current_token
        return self.current_token

    def reverse(self, count=1):
        self.tok_index -= count
        self.update_current_tok()
        return self.current_token

    def update_current_tok(self):
        if self.tok_index >= 0 and self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]
        else:
            self.current_token = None

    def parse(self):
        res = self.statements()
        try:
            error = {
                'name': '',
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'context': self.context,
                'exit': False
            }
           
            if not res.error and self.current_token.type != tokenList.TT_EOF:
                tok_detected = self.current_token
                error['name'] = 'SynaxError'
                error['message'] = "Invalid syntax or unknown token"
                if tok_detected:
                    if self.error_detected != True:
                        self.error_detected = True
                        return res.failure(self.error['Default'](error))
            return res
        except:
            pass

    def property(self, tok):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False,
            }))
        prop_name = self.current_token
        res.register_advancement()
        self.advance()
        return res.success(PropertyNode(tok, prop_name))

    def skipLines(self):
        res = ParseResult()
        res.register_advancement()
        self.advance()

    def statements(self):
        try:
            res = ParseResult()
            statements = []
            pos_start = self.current_token.pos_start.copy()

            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

            statement = res.register(self.statement())
            if res.error:
                return res
            statements.append(statement)

            more_statements = True

            while True:
                newline_count = 0
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    newline_count += 1
                if newline_count == 0:
                    more_statements = False

                if not more_statements:
                        break
                statement = res.try_register(self.statement())
                if not statement:
                    self.reverse(res.to_reverse_count)
                    more_statements = False
                    continue
                statements.append(statement)
            return res.success(ListNode(statements, pos_start, self.current_token.pos_end.copy()))

        except KeyboardInterrupt:
            pass

    def statement(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        values = ()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()
            expr = res.try_register(self.expr())
            values = (expr,)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                values += (res.try_register(self.expr()),)
                expr = PairNode(values, pos_start,
                                self.current_token.pos_end.copy())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'continue'):
            if hasattr(Parser, 'scope'):
                if Parser.scope != 'loop':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "can only use 'continue' within a loop",
                        'context': self.context,
                        'exit': False,
                    }))
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "can only use 'continue' within a loop",
                    'context': self.context,
                    'exit': False,
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
            return res.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'break'):
            #print(Parser.scope)
            if hasattr(Parser, 'scope'):
                if Parser.scope != 'loop':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "'break' outside of loop",
                        'context': self.context,
                        'exit': False,
                    }))
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "'break' outside of loop",
                    'context': self.context,
                    'exit': False,
                }))
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
            return res.success(BreakNode(self.scope,pos_start, self.current_token.pos_end.copy()))
        expr = res.register(self.expr())
        if res.error:
            return res.failure(self.error['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.current_token.pos_start,
                'message': "invalid syntax",
                'context': self.context,
                'exit': False
            }))
        return res.success(expr)

    def expr(self):
        res = ParseResult()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'let') or self.current_token.matches(tokenList.TT_KEYWORD, 'final'):
            res.register_advancement()
            variable_keyword_token = "let" if self.current_token.matches(
                tokenList.TT_KEYWORD, 'let') else "final"
            self.advance()

            if(self.current_token.value in tokenList.KEYWORDS):
                if self.current_token.value == "fm":
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Cannot use keyword '{self.current_token.value}' as an identifier",
                    'context': self.context,
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_LPAREN:
                expr = res.register(self.expr())
                if res.error:
                        return res
                values = expr.elements
                for val in values:
                    if isinstance(val, StringNode):
                        single_check_for_rest_operator = val.name.value.split(
                                '*')
                        if len(single_check_for_rest_operator) > 1 and single_check_for_rest_operator[0] == "":
                            self.error_detected = False
                    elif not isinstance(val, VarAccessNode):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': val.pos_start,
                            'pos_end': val.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                var_values = ()
                if self.current_token.type != tokenList.TT_EQ:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected '='",
                        'context': self.context,
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                for value in values:
                    var_values += (value,)
                return res.success(VarAssignNode(var_values, expr, variable_keyword_token))

            if self.current_token.type == tokenList.TT_LSQBRACKET:
                expr = res.register(self.expr())
                if res.error:
                    return res
                values = expr.elements
                for val in values:
                    if isinstance(val, StringNode):
                        single_check_for_rest_operator = val.name.value.split(
                                '*')
                        if len(single_check_for_rest_operator) > 1 and single_check_for_rest_operator[0] == "":
                            self.error_detected = False
                    elif not isinstance(val, VarAccessNode):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': val.pos_start,
                            'pos_end': val.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                var_values = []
                if self.current_token.type != tokenList.TT_EQ:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected '='",
                        'context': self.context,
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                for value in values:
                    var_values.append(value)
                return res.success(VarAssignNode(var_values, expr, variable_keyword_token))

            if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_MUL:
                   return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))

            if self.current_token.type == tokenList.TT_MUL:
                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                var_name = StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok
                res.register_advancement()
                self.advance()
                if self.current_token.type != tokenList.TT_COMMA:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "starred assignment must be in a list or pair",
                        'context': self.context,
                        'exit': False
                    }))
                else:
                    self.reverse()
            else:
                var_name = self.current_token
            res.register_advancement()
            self.advance()
            if len(var_name.value) > 255:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Identifier too long",
                    'context': self.context,
                    'exit': False
                }))

            while self.current_token.type == tokenList.TT_COMMA:
                identifiers = [VarAccessNode(var_name)]
                values = []
                res.register_advancement()
                self.advance()
                comma_token = self.current_token
                if self.current_token.type == tokenList.TT_IDENTIFIER or self.current_token.type == tokenList.TT_MUL:
                    if self.current_token.type == tokenList.TT_MUL:
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "expected an identifier",
                                'context': self.context,
                                'exit': False
                            }))
                        identifiers.append(VarAccessNode(StringNode(Token(tokenList.TT_IDENTIFIER, str(
                            "*") + str(self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok))

                    else:
                        identifiers.append(VarAccessNode(self.current_token))
                    res.register_advancement()
                    self.advance()
                    while self.current_token.type == tokenList.TT_COMMA:
                        comma_token = self.current_token
                        res.register_advancement()
                        self.advance()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            if self.current_token.type == tokenList.TT_MUL:
                                self.skipLines()
                                if self.current_token.type != tokenList.TT_IDENTIFIER:
                                    return res.failure(self.error['Syntax']({
                                        'pos_start': self.current_token.pos_start,
                                        'pos_end': self.current_token.pos_end,
                                        'message': "expected an identifier",
                                        'context': self.context,
                                        'exit': False
                                    }))
                                identifiers.append(VarAccessNode(StringNode(Token(tokenList.TT_IDENTIFIER, str(
                                    "*") + str(self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok))
                                res.register_advancement()
                                self.advance()
                            else:
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': comma_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "expected an identifier after ','",
                                    'context': self.context,
                                    'exit': False
                                }))
                        while self.current_token.type == tokenList.TT_IDENTIFIER:
                            identifiers.append(
                                    VarAccessNode(self.current_token))
                            res.register_advancement()
                            self.advance()
                    if self.current_token.type == tokenList.TT_EQ:
                        # check if multiple star operators are used
                        is_multiple_starred_expression = [
                                name.name.value for name in identifiers if is_varags(name.name.value)]
                        if len(is_multiple_starred_expression) > 1:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "assignment to multiple starred expressions",
                                'context': self.context,
                                'exit': False
                            }))
                        res.register_advancement()
                        self.advance()
                        new_values = []
                        expr = res.register(self.expr())
                        values.append(expr)
                        # if isinstance(expr, PairNode) or isinstance(expr, ListNode):
                        #     for val in expr.elements:
                        #         new_values.append(val)
                        #         values = new_values
                        # else:
                        #     values = [expr]
                        if self.current_token.type == tokenList.TT_COMMA:
                            while self.current_token.type == tokenList.TT_COMMA:
                                res.register_advancement()
                                self.advance()
                                comma_token = self.current_token
                                values.append(res.register(self.expr()))
                                for v in values:
                                    if v == '':
                                        values.remove(v)
                            values_list = ListNode(
                                    values, comma_token.pos_start, comma_token.pos_end)
                            # if isinstance(expr, DictNode) or isinstance(expr, ObjectNode):
                            #     values_list = expr
                            # print(values_list)
                            return res.success(VarAssignNode(identifiers, values_list, variable_keyword_token))
                        else:
                            values = expr
                            return res.success(VarAssignNode(identifiers, values, variable_keyword_token))
                    else:
                        none_values = []
                        tok = Token(tokenList.TT_KEYWORD, 'none', None, None)
                        for i in range(len(identifiers)):
                            none_values.append(tok)
                        values_list = ListNode(
                                none_values, comma_token.pos_start, comma_token.pos_end)
                        return res.success(VarAssignNode(identifiers, values_list, variable_keyword_token))
                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': comma_token.pos_start,
                        'pos_end': comma_token.pos_end,
                        'message': "expected an identifier after ','",
                        'context': self.context,
                        'exit': False
                    }))
                # res.register_advancement()
                # self.advance()
                if res.error:
                    return res
               # return res.success(VarAssignNode(var_name, expr, variable_keyword_token))

            if self.current_token.type == tokenList.TT_RSHIFT:
                res.register_advancement()
                self.advance()

            if self.current_token.type != tokenList.TT_EQ:
                if variable_keyword_token == "let":
                    expr = res.register(self.expr())
                    return res.success(VarAssignNode(var_name, None, variable_keyword_token))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected '='",
                        'context': self.context,
                        'exit': False
                    }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_SPREAD:
                spread_expr = res.register(self.spread_expr(
                        var_name, variable_keyword_token))
                return res.success(spread_expr)
            
            expr = res.register(self.expr())
            if expr == "":
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an expression",
                    'context': self.context,
                    'exit': False
                }))
            if res.error:
                return res
            pair_exprs = []
            
            while self.current_token.type == tokenList.TT_COMMA:
                self.skipLines()
                pair_exprs.append(res.register(self.expr()))
                
                if expr == "":
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an expression",
                        'context': self.context,
                        'exit': False
                    }))
                if res.error: return res
            
            if len(pair_exprs) > 0:
                pair_exprs.insert(0, expr)
                pair_node = PairNode(pair_exprs, self.current_token.pos_start, self.current_token.pos_end)
                return res.success(VarAssignNode(var_name, pair_node, variable_keyword_token))
            else:
                return res.success(VarAssignNode(var_name, expr, variable_keyword_token))
            
        node = res.register(self.binaryOperation(
            self.comp_expr, ((tokenList.TT_KEYWORD, 'and'), (tokenList.TT_KEYWORD, 'or'), (tokenList.TT_KEYWORD, 'in'), (tokenList.TT_KEYWORD, 'notin'))))
        if res.error:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "invalid syntax or unexpected token",
                'context': self.context,
                'exit': False
            }))
        
        return res.success(node)

    def comp_expr(self):
        res = ParseResult()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'not'):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(self.binaryOperation(
            self.arith_expr, (tokenList.TT_EQEQ, tokenList.TT_NEQ, tokenList.TT_LT, tokenList.TT_GT, tokenList.TT_RSHIFT, tokenList.TT_LSHIFT, tokenList.TT_LTE, tokenList.TT_GTE, tokenList.TT_AND)))

        if res.error:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'context': self.context,
                'exit': False
            }))

        return res.success(node)

    def arith_expr(self):
        return self.binaryOperation(self.term, (tokenList.TT_PLUS, tokenList.TT_MINUS, tokenList.TT_FLOOR_DIV))

    def term(self):
        return self.binaryOperation(self.factor, (tokenList.TT_MUL, tokenList.TT_DIV, tokenList.TT_MOD, tokenList.TT_MERGE))

    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_PLUS, tokenList.TT_MINUS, tokenList.TT_FLOOR_DIV):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                    return res
            if tok and not factor: # if tok and factor is None
                self.error_detected = True
                self.error['Syntax']({
                    'message': 'Invalid syntax',
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'context': self.context,
                    'exit': False
                })
            return res.success(UnaryOpNode(tok, factor))
        return self.power()

    def increment_or_decrement(self, atom):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_PLUS_PLUS, tokenList.TT_MINUS_MINUS):
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                identifier = res.register(self.atom())
                return res.success(UnaryOpNode(tok, identifier))

            return res.success(BinOpNode(atom, tok, atom))

        return res.success(atom)

    def power(self):
        return self.binaryOperation(self.set_node_expr, (tokenList.TT_POWER, tokenList.TT_DOT), self.factor)

    def set_node_expr(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
                return res
        while True:
            if self.current_token.type == tokenList.TT_LPAREN:
                atom = res.register(self.finish_call(atom))
            elif self.current_token.type == tokenList.TT_DOT:
                res.register_advancement()
                self.advance()
                name = self.current_token
                if name != None and name.value == '' or name.value == None:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected property name after '.'",
                        'context': self.context,
                        'exit': False
                    }))
                
                if name == None:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected property name after '.'",
                        'context': self.context,
                        'exit': False
                    }))
                    
                if atom == '':
                    # then we want to make it a floating point number e.g. .5 == 0.5
                    if name != '' and isinstance(name.value, int):
                        tok = Token(tokenList.TT_FLOAT, float(
                            '0.' + str(name.value)), name.pos_start, name.pos_end)
                        res.register_advancement()
                        self.advance()
                        return res.success(NumberNode(tok))
                    else:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Invalid syntax or unknown token",
                            'context': self.context,
                            'exit': False
                        }))
                else:
                    atom = res.register(self.access_property(atom))
                    if res.error:
                            return res
                    if name.type != tokenList.TT_IDENTIFIER and name.type != tokenList.TT_KEYWORD:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': name.pos_start,
                            'pos_end': name.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
            elif self.current_token.type == tokenList.TT_LSQBRACKET:
                atom = res.register(self.index_get(atom))
            elif self.current_token.type == tokenList.TT_PLUS_PLUS:
                atom = res.register(self.increment_or_decrement(atom))
            elif self.current_token.type == tokenList.TT_MINUS_MINUS:
                atom = res.register(self.increment_or_decrement(atom))
            elif self.current_token.type != None and self.current_token.type in operation_methods:
                operator = self.current_token
                
                if not isinstance(atom, VarAccessNode):
                    print(type(atom))
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Illegal expression: invalid left hand side",
                        'context': self.context,
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:
                    identifier = res.register(self.expr())
                    return res.success(VarReassignNode(atom, identifier, operation_methods[operator.type]))
                elif self.current_token.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
                    value = res.register(self.atom())
                    return res.success(VarReassignNode(atom, value, operation_methods[operator.type]))
                elif self.current_token == None or self.current_token.type == tokenList.TT_NEWLINE or self.current_token.type == tokenList.TT_EOF:
                    self.error_detected = True
                    self.error['Syntax']({
                        'message': "invalid syntax",
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'context': self.context,
                        'exit': False
                    })
                else:
                    expr = res.register(self.expr())
                    return res.success(VarReassignNode(atom, expr, operation_methods[operator.type]))

            else:
                break

        return res.success(atom)

    def make_call(self):
        res = ParseResult()
        arg_nodes = []
        keyword_args = {}
        keyword_args_list = []
        has_unpack = False
        if self.current_token.type == tokenList.TT_MUL:
            self.skipLines()
            has_unpack = True
            # else:
            #     self.error_detected = True
            #     return res.failure(self.error['Syntax']({
            #         'pos_start': self.current_token.pos_start,
            #         'pos_end': self.current_token.pos_end,
            #         'message': "expected an expression after '*'",
            #         'context': self.context,
            #         'exit': False
            #     }))
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            keyword_args = {
                'name': self.current_token.value,
                'value': ''
            }
            self.skipLines()
            if self.current_token.type == tokenList.TT_EQ:
                self.skipLines()
                keyword_args['value'] = res.register(self.expr())
                if res.error:
                        return res
                keyword_args_list.append(keyword_args)
                if keyword_args['value'] == None or keyword_args['value'] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
                if res.error:
                        return res
                while self.current_token.type == tokenList.TT_COMMA:
                    self.skipLines()
                    if self.current_token.type == tokenList.TT_IDENTIFIER:
                        keyword_args = {
                            'name': self.current_token.value,
                            'value': ''
                        }
                        self.skipLines()
                        if self.current_token.type == tokenList.TT_EQ:
                            self.skipLines()
                            keyword_args['value'] = res.register(self.expr())
                            if res.error:
                                    return res
                            keyword_args_list.append(keyword_args)

                            if keyword_args['value'] == None or keyword_args['value'] == '':
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "invalid syntax",
                                    'context': self.context,
                                    'exit': False
                                }))
                            if res.error:
                                    return res
                        else:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "positional argument cannot be followed by keyword argument",
                                'context': self.context,
                                'exit': False
                            }))
                    else:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "positional argument cannot be followed by keyword argument",
                            'context': self.context,
                            'exit': False
                        }))
            else:
                self.reverse()
                expr = res.register(self.expr())
                if res.error:
                        return res
                arg_nodes.append(expr)
        else:
            expr = res.register(self.expr())
            if res.error:
                    return res
            
            # if has_unpack:
            #     if not isinstance(expr, ListNode):
            #         self.error_detected = True
            #         return res.failure(self.error['Syntax']({
            #             'pos_start': self.current_token.pos_start,
            #             'pos_end': self.current_token.pos_end,
            #             'message': "expected a list after '*'",
            #             'context': self.context,
            #             'exit': False
            #         }))
            
            # else:
            arg_nodes.append(expr)

        while self.current_token.type == tokenList.TT_COMMA:
            self.skipLines()
            if has_unpack == True:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "only one argument is allowed after '*' unpack",
                    'context': self.context,
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                keyword_args = {
                    'name': self.current_token.value,
                    'value': ''
                }
                self.skipLines()
                if self.current_token.type == tokenList.TT_EQ:
                    self.skipLines()
                    keyword_args['value'] = res.register(self.expr())
                    if res.error:
                            return res
                    keyword_args_list.append(keyword_args)

                    if keyword_args['value'] == None or keyword_args['value'] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax",
                            'context': self.context,
                            'exit': False
                        }))
                    if res.error:
                            return res
                    while self.current_token.type == tokenList.TT_COMMA:
                        self.skipLines()
                        if self.current_token.type == tokenList.TT_IDENTIFIER:
                            keyword_args = {
                                'name': self.current_token.value,
                                'value': ''
                            }
                            self.skipLines()
                            if self.current_token.type == tokenList.TT_EQ:
                                self.skipLines()
                                keyword_args['value'] = res.register(
                                        self.expr())
                                if res.error:
                                        return res
                                keyword_args_list.append(keyword_args)

                                if keyword_args['value'] == None or keyword_args['value'] == '':
                                    self.error_detected = True
                                    return res.failure(self.error['Syntax']({
                                        'pos_start': self.current_token.pos_start,
                                        'pos_end': self.current_token.pos_end,
                                        'message': "invalid syntax",
                                        'context': self.context,
                                        'exit': False
                                    }))
                                if res.error:
                                        return res
                            else:
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "positional argument cannot be followed by keyword argument",
                                    'context': self.context,
                                    'exit': False
                                }))
                        else:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "positional argument cannot be followed by keyword argument",
                                'context': self.context,
                                'exit': False
                            }))
                else:
                    self.reverse()
                    expr = res.register(self.expr())
                    if res.error:
                            return res
                    arg_nodes.append(expr)
            else:
                expr = res.register(self.expr())
                if res.error:
                        return res
                arg_nodes.append(expr)

        if self.current_token.type != tokenList.TT_RPAREN:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected ',', or ')'",
                'context': self.context,
                'exit': False
            }))

        self.skipLines()
        return arg_nodes, keyword_args_list, has_unpack

    def finish_call(self, atom):
        res = ParseResult()
        arg_nodes = []
        keyword_args = {}
        keyword_args_list = []
        has_unpack = False
        if self.current_token.type == tokenList.TT_LPAREN:
            self.skipLines()
            if self.current_token.type == tokenList.TT_RPAREN:
                self.skipLines()

            else:
                arg_nodes, keyword_args_list, has_unpack = self.make_call()


        for i in range(len(arg_nodes)):
            if arg_nodes[i] == None or arg_nodes[i] == '':
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invlaid syntax",
                    'context': self.context,
                    'exit': False
                }))

        duplicate_key = None
        is_duplicate = False
        keys_count = []
        for key in keyword_args_list:
            first_key = key['name']
            keys_count.append(first_key)
        for key in keys_count:
            if keys_count.count(key) > 1:
                duplicate_key = key
                is_duplicate = True
                break
        if is_duplicate:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': f"repeated keyword argument: '{duplicate_key}'",
                'context': self.context,
                'exit': False
            }))

        #print(f"arg_nodes: {arg_nodes}", f"keyword_args_list: {keyword_args_list}")
        return res.success(CallNode(atom, arg_nodes, keyword_args_list, has_unpack))

    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == tokenList.TT_DOUBLE_STRING or tok.type == tokenList.TT_SINGLE_STRING or tok.type == tokenList.TT_BACKTICK_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == tokenList.TT_DOC_STRING:
            res.register_advancement()
            self.advance()
            return res.success(DocStringNode(tok))
        elif tok.type == tokenList.TT_IDENTIFIER:
            self.skipLines()
            if self.current_token.type == tokenList.TT_EQ:
                if self.if_scope == True:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
                self.skipLines()
                name = tok
                value = res.register(self.expr())
                if res.error:
                        return res
                return self.re_assign(name, value)
            else:
                return res.success(VarAccessNode(tok))
        elif tok.value == 'true' or tok.value == 'false':
            res.register_advancement()
            self.advance()
            return res.success(BooleanNode(tok))
        elif tok.value == 'none':
            res.register_advancement()
            self.advance()
            return res.success(NoneNode(tok))
        elif tok.type == tokenList.TT_LPAREN:
            pair_expr = res.register(self.pair_expr())
            if res.error:
                    return res
            return res.success(pair_expr)
        elif tok.type == tokenList.TT_RPAREN:
            return res.failure(self.error['Syntax']({
                'pos_start': tok.pos_start,
                'pos_end': tok.pos_end,
                'message': f"invalid syntax or unexpected token",
                'context': self.context,
                'exit': False
            }))
        elif tok.type == tokenList.TT_LSQBRACKET:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
        elif tok.type == tokenList.TT_LBRACE:
            dict_expr = res.register(self.dict_expr())
            if res.error:
                return res
            return res.success(dict_expr)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'if'):
            if_expression = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expression)
        elif tok.matches(tokenList.TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'in'):
            in_expr = res.register(self.in_expr())
            if res.error:
                return res
            return res.success(in_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'def'):
            function_expr = res.register(self.function_expr())
            if res.error:
                  return res
            return res.success(function_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'object'):
            object_expr = res.register(self.object_def())
            if res.error:
                return res
            return res.success(object_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'class'):
            class_expr = res.register(self.class_def())
            if res.error:
                return res
            return res.success(class_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'match'):
            match_expr = res.register(self.match_expr())
            if res.error:
                return res
            return res.success(match_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'attempt'):
            attempt_expr = res.register(self.attempt_expr())
            if res.error:
                return res
            return res.success(attempt_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'raise'):
            raise_expr = res.register(self.raise_expr())
            if res.error:
                return res
            return res.success(raise_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'fm'):
            string_interp = res.register(self.string_interp())
            if res.error:
                    return res
            return res.success(string_interp)
        elif tok.matches(tokenList.TT_KEYWORD, 'bt'):
            byte_expr = res.register(self.byte_expr())
            if res.error:
                    return res
            return res.success(byte_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'del'):
            del_expr = res.register(self.del_expr())
            if res.error:
                return res
            return res.success(del_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'import'):
            import_expr = res.register(self.import_expr())
            if res.error:
                return res
            return res.success(import_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'from'):
            from_import_expr = res.register(self.from_import_expr())
            if res.error:
                    return res
            return res.success(from_import_expr)       
        elif tok.matches(tokenList.TT_KEYWORD, 'freeze'):
            freeze_expr = res.register(self.freeze_expr())
            if res.error:
                    return res
            return res.success(freeze_expr)
         
    def re_assign(self, name,value):
        res = ParseResult()
        return res.success(VarReassignNode(name, value))

    def access_property(self, object_):
        res = ParseResult()
        name = self.current_token
        self.skipLines()
        arg_nodes = []
        has_unpack = False
        if self.current_token.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
                call_node = res.success(CallNode(name, arg_nodes))
                name = res.register(call_node)
            else:
                arg_nodes, keyword_args_list, has_unpack = self.make_call()
                call_node = res.success(
                        CallNode(name, arg_nodes, keyword_args_list, has_unpack))
                name = res.register(call_node)

        if self.current_token.type == tokenList.TT_PLUS_PLUS:
            res.register_advancement()
            self.advance()
            return res.success(PropertySetNode(object_, name, None, "++"))

        elif self.current_token.type == tokenList.TT_MINUS_MINUS:
            res.register_advancement()
            self.advance()
            return res.success(PropertySetNode(object_, name, None, "--"))

        elif self.current_token.type != None and self.current_token.type in operation_methods:
            operator = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                value = res.register(self.expr())
                return res.success(VarReassignNode(object_, value, operation_methods[operator.type], name))
            elif self.current_token.type in (tokenList.TT_INT, tokenList.TT_FLOAT, tokenList.TT_BINARY, tokenList.TT_HEX, tokenList.TT_OCTAL):
                value = res.register(self.atom())
                return res.success(VarReassignNode(object_, value, operation_methods[operator.type], name))
            elif self.current_token == None or self.current_token.type == tokenList.TT_NEWLINE or self.current_token.type == tokenList.TT_EOF:
                self.error_detected = True
                self.error['Syntax']({
                    'message': "invalid syntax",
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'context': self.context,
                    'exit': False
                })
            else:
                expr = res.register(self.expr())
                return res.success(VarReassignNode(object_, expr, operation_methods[operator.type], name))

        if self.current_token.type == tokenList.TT_EQ:
            res.register_advancement()
            self.advance()
            value = res.register(self.expr())
            if res.error:
                    return res
            return res.success(PropertySetNode(object_, name, value))

        return res.success(PropertyNode(object_, name))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error:
            self.error_detected = True
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_token.matches(tokenList.TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_COLON:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"expected ':'",
                    'context': self.context,
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                start_token = self.current_token
                statements = res.register(self.statements())
                if len(statements.elements) > 0:
                    if statements.elements[0] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax'](
                            {
                                'pos_start': start_token.pos_start,
                                'pos_end': start_token.pos_end,
                                'message': 'expected an expression',
                                'context': self.context,
                                'exit': False
                            }
                        ))
                if res.error:
                    return res
                else_case = (statements, True)
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()

                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'expected "end"',
                            'context': self.context,
                            'exit': False
                        }
                    ))
            else:
                current_token = self.current_token
                expr = res.register(self.statement())
                if self.current_token.type == tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "':' is not allowed here",
                            'context': self.context,
                            'exit': False
                        }
                    ))
                if expr == "":
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'expected an expression',
                            'context': self.context,
                            'exit': False
                        }
                    ))
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_token.matches(tokenList.TT_KEYWORD, 'elif'):
            all_cases = res.register(self.if_expr_b())
            
            if res.error:
                self.error_detected = True
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                self.error_detected = True
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_name):
        res = ParseResult()
        cases = []
        else_case = None
        if not self.current_token.matches(tokenList.TT_KEYWORD, case_name):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected "{}"'.format(case_name),
                    'context': self.context,
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()
        
        
        is_loop = True if hasattr(Parser, 'scope') and Parser.scope == 'loop' else False
        self.if_scope = True
        Parser.scope = "loop" if is_loop else None
        condition = res.register(self.expr())
        self.if_scope = False
        
        
        if condition == "":
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected an expression',
                    'context': self.context,
                    'exit': False
                }
            ))
        if res.error:
            return res

        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected ":"',
                    'context': self.context,
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())
            if len(statements.elements) > 0:
                if statements.elements[0] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': start_token.pos_start,
                            'pos_end': start_token.pos_end,
                            'message': 'expected an expression',
                            'context': self.context,
                            'exit': False
                        }
                    ))
            if res.error:
                return res
            cases.append((condition, statements, True))
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                self.error_detected = True
                return res
            cases.append((condition, expr, False))
            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                self.error_detected = True
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        
        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()
        Parser.scope = "loop"
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'for'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'for'"
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))

        var_name_token = self.current_token
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_EQ:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected '='",
                'context': self.context,
                'exit': False
            }))
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'to'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'to'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_token.matches(tokenList.TT_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected ':'",
                'context': self.context,
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_NEWLINE:

            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            Parser.scope = None
            return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, True))
        body = res.register(self.statement())
        if res.error:
            return res
        # if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
        #     return res.failure(self.error['Syntax'](
        #         {
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': 'return is not allowed in for loop',
        #             'context': self.context,
        #             'exit': False
        #         }
        #     ))
       
        return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, False))

    def in_expr(self):
        res = ParseResult()
        Parser.scope = "loop"
            
            
        iterable_name_token = None
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'in'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'in'"
            }))

        res.register_advancement()
        self.advance()


        iterable_name_token = res.register(self.expr())
        if iterable_name_token == None or iterable_name_token == '':
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'as'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        iterator_keys = []
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            expr = res.register(self.expr())
            iterator_keys.append(expr)
            if self.current_token.type == tokenList.TT_COMMA:
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                    expr = res.register(self.expr())
                    iterator_keys.append(expr)
                    if res.error:
                            return res
                    if len(iterator_keys) == 0:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))

                    if self.current_token.type != tokenList.TT_COLON:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected ':'",
                            'context': self.context,
                            'exit': False
                        }))
                    res.register_advancement()
                    self.advance()

                    if self.current_token.type == tokenList.TT_NEWLINE:
                        res.register_advancement()
                        self.advance()

                        body = res.register(self.statements())
                        if res.error:
                            return res

                        if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "invalid syntax",
                                'context': self.context,
                                'exit': False
                            }))

                        res.register_advancement()
                        self.advance()

                        return res.success(InNode(iterable_name_token, iterator_keys, body, False))

                    else:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected a newline",
                            'context': self.context,
                            'exit': False
                        }))

            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected ':'",
                    'context': self.context,
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                body = res.register(self.statements())
                if res.error:
                    return res

                if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                Parser.scope = None
                return res.success(InNode(iterable_name_token, iterator_keys, body, False))
        else:
            expr = res.register(self.expr())
            if not isinstance(expr, PairNode):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an identifier or a pair",
                    'context': self.context,
                    'exit': False
                }))

            for el in expr.elements:
                iterator_keys.append(el)

            if len(iterator_keys) == 0:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a value",
                    'context': self.context,
                    'exit': False
                }))
           
            

            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected ':'",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()

            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                body = res.register(self.statements())
                if res.error:
                    return res

                if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()

                return res.success(InNode(iterable_name_token, iterator_keys, body, False))

        
        body = res.register(self.statement())
        
        return res.success(InNode(iterable_name_token, iterator_keys, body, False))

    def while_expr(self):
        res = ParseResult()
        Parser.scope = "loop"
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'while'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'while'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_token.type != tokenList.TT_COLON:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected ':'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            Parser.scope = None
            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def function_expr(self):
        res = ParseResult()
        doc_string = None
        #print(Parser.scope)
        Parser.scope = "function_method"
        default_values = {}
        default_values_list = []
        varargs = False
        varkwargs = False
        varargs_name = None
        type_hints = []
        type_hint = {}
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'def'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'def'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            def_name_token = self.current_token
            if def_name_token.value[0] != '@':
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': def_name_token.pos_start,
                    'pos_end': def_name_token.pos_end,
                    'message': "expected '@' before function name",
                    'context': self.context,
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected '('",
                    'context': self.context,
                    'exit': False
                }))
        else:
            def_name_token = None
            def_name = self.current_token.value
            if def_name in tokenList.KEYWORDS:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Cannot use reserved keyword as function name",
                    'context': self.context,
                    'exit': False
                    }))
            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an identifier or '('",
                    'context': self.context,
                    'exit': False
                }))
        res.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == tokenList.TT_IDENTIFIER or self.current_token.type == tokenList.TT_MUL:
            arg_name_tokens.append(self.current_token)
            if self.current_token.type == tokenList.TT_MUL:
                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                arg_name_tokens[0] = StringNode(Token(tokenList.TT_IDENTIFIER, str(
                    "*") + str(self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok
            default_values = {
                'name': arg_name_tokens[0].value,
                'value': ''
            }
            self.skipLines()
            if self.current_token.type == tokenList.TT_COLON:
                type_hint = {
                    arg_name_tokens[0].value: {
                        'type': '',
                    }
                }
                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected a type",
                        'context': self.context,
                        'exit': False
                    }))
                type_hint[arg_name_tokens[0].value]['type'] = self.current_token.value
                type_hints.append(type_hint)
                self.skipLines()
               
            if self.current_token.type == tokenList.TT_EQ:
                self.skipLines()
                default_values['value'] = res.register(self.expr())
                default_values_list.append(default_values)
                # parameter with *args or **kwargs can't have default values
                for default_value in default_values_list:
                    if is_varags(default_value['name']):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "parameter with * or ** cannot have default values",
                            'context': self.context,
                            'exit': False
                        }))
                if default_values['value'] == None or default_values['value'] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
                if res.error:
                        return res

            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_MUL:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))

                arg_name_tokens.append(self.current_token)
                if self.current_token.type == tokenList.TT_MUL:
                    self.skipLines()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                    arg_name_tokens[-1] = StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(
                        self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok

                default_values = {
                    'name': arg_name_tokens[-1].value,
                    'value': ''
                }
                # if len(arg_name_tokens) > 20:
                #     self.error_detected = True
                #     return res.failure(self.error['Syntax']({
                #         'pos_start': self.current_token.pos_start,
                #         'pos_end': self.current_token.pos_end,
                #         'message': "Cannot have more than 12 arguments",
                #         'context': self.context,
                #         'exit': False
                #     }))
                self.skipLines()
                # only one *args or **kwargs is allowed
                splats = []
                for arg_name in arg_name_tokens:
                       if is_varags(arg_name.value):
                            splats.append(arg_name.value)
                if len(splats) > 1:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid syntax - only one * or ** is allowed",
                        'context': self.context,
                        'exit': False
                    }))
                # named arguments cannot be followed by a default value
                if self.current_token.type == tokenList.TT_COLON:
                    type_hint = {
                        arg_name_tokens[-1].value: {
                            'type': '',
                        }
                    }
                    self.skipLines()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected a type",
                            'context': self.context,
                            'exit': False
                        }))
                    type_hint[arg_name_tokens[-1].value]['type'] = self.current_token.value
                    type_hints.append(type_hint)
                    self.skipLines()
                if self.current_token.type == tokenList.TT_EQ:
                    self.skipLines()
                    default_values['value'] = res.register(self.expr())
                    default_values_list.append(default_values)
                    # parameter with *args or **kwargs can't have default values
                    for default_value in default_values_list:
                        if is_varags(default_value['name']):
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "parameter with * or ** cannot have default values",
                                'context': self.context,
                                'exit': False
                            }))
                    if default_values['value'] == None or default_values['value'] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax",
                            'context': self.context,
                            'exit': False
                        }))
                    if res.error:
                            return res
                    duplicate_key = None
                    is_duplicate = False
                    keys_count = []
                    for key in default_values_list:
                        first_key = key['name']
                        keys_count.append(first_key)
                    for key in keys_count:
                        if keys_count.count(key) > 1:
                            duplicate_key = key
                            is_duplicate = True
                            break
                    if is_duplicate:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': f"duplicate argument: '{duplicate_key}' in function definition",
                            'context': self.context,
                            'exit': False
                        }))
                else:
                    if len(default_values_list) > 0:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "non-default argument cannot be followed by a default argument",
                            'context': self.context,
                            'exit': False
                        }))

            if self.current_token.type != tokenList.TT_RPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected ',' or ')'",
                    'context': self.context,
                    'exit': False
                })) 
            
        else:
            if self.current_token.type != tokenList.TT_RPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an identifier or ')'",
                    'context': self.context,
                    'exit': False
                }))
        self.skipLines()
        if self.current_token.type == tokenList.TT_COLON:
            type_hint = {
                "return_type": {
                    'type': '',
                }
            }
            self.skipLines()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected a type",
                        'context': self.context,
                        'exit': False
                    }))
            type_hint['return_type']['type'] = self.current_token.value
            type_hints.append(type_hint)
            self.skipLines()
        if self.current_token.type == tokenList.TT_ARROW:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an expression",
                    'context': self.context,
                    'exit': False
                }))
            body = res.register(self.expr())
            if res.error:
                    return res
            return res.success(FunctionNode(def_name_token, arg_name_tokens, body, True, default_values_list, type_hints=type_hints))

        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected  '->', or a newline",
                'context': self.context,
                'exit': False
            }))
        
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_DOC_STRING:
            doc_string = res.register(self.expr())
        
        body = res.register(self.statements())
        if res.error:
                return res
        
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            return res.success(FunctionNode(def_name_token, arg_name_tokens, body, False, default_values_list, None, doc_string, type_hints=type_hints))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "invalid syntax",
                'context': self.context,
                'exit': False
            }))

    def object_def(self):
        res = ParseResult()
        object_properties = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'object'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'object'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))

        object_name = self.current_token

        if object_name in tokenList.KEYWORDS:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as object name",
                'context': self.context,
                'exit': False
            }))
        if isOnlyLetters(object_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use non-letter characters as object name",
                'context': self.context,
                'exit': False
            }))
        if isFirstLetterUpper(object_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Object name must start with a capital letter",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected a newline",
                'context': self.context,
                'exit': False
            }))

        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()

                object_properties.append({
                    'name': object_name,
                    'value': [],
                    'pos_start': object_name.pos_start,
                    'pos_end': object_name.pos_end
                })
                return res.success(ObjectNode(object_name, object_properties))
            if self.current_token.type != tokenList.TT_IDENTIFIER and str(self.current_token.value) not in tokenList.DIGITS:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an identifier",
                    'context': self.context,
                    'exit': False
                }))

            while self.current_token.type == tokenList.TT_IDENTIFIER or str(self.current_token.value) in tokenList.DIGITS:

                obj_name = self.current_token
                if hasattr(obj_name, 'value'):
                    if not isinstance(obj_name.value, str):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid object property name '{}'".format(obj_name.value),
                            'context': self.context,
                            'exit': False
                        }))
                if res.error:
                        return res
                # object property name cannot start with a @ or a symbol
                if obj_name.value[0] == '@' or obj_name.value[0] in tokenList.SYMBOLS:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Object name cannot start with a symbol",
                        'context': self.context,
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()

                if self.current_token.type != tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ':'",
                        'context': self.context,
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:

                    if self.current_token.value == 'self':
                        self.current_token.value = object_name.value
                obj_value = res.register(self.expr())

                object_properties.append({
                    'name': obj_name,
                    'value': obj_value,
                    'pos_start': obj_name.pos_start,
                    'pos_end': self.current_token.pos_end
                })

                
                #return res.success(ObjectNode(object_name, object_properties))

                if res.error:
                        return res
                if obj_value == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected property value",
                        'context': self.context,
                        'exit': False
                    }))
                if self.current_token.type == tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "no comma allowed after property value in object declaration",
                        'context': self.context,
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_NEWLINE:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected a newline",
                        'context': self.context,
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                
                
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()

                    return res.success(ObjectNode(object_name, object_properties))
                if self.current_token.value in tokenList.NOT_ALLOWED_OBJECTS_KEYS:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unterminated object literal, Object key '{}' is not allowed".format(self.current_token.value),
                        'context': self.context,
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                    while self.current_token.type == tokenList.TT_NEWLINE:
                        res.register_advancement()
                        self.advance()
                        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                            res.register_advancement()
                            self.advance()
                            return res.success(ObjectNode(object_name, object_properties))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected 'end' or you have forgottem to close a newline",
                            'context': self.context,
                            'exit': False
                            }))
                    else:
                        res.register_advancement()
                        self.advance()
                        return res.success(ObjectNode(object_name, object_properties))
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid or missing object name",
                    'context': self.context,
                    'exit': False
                }))
           
           
            return res.success(ObjectNode(object_name, object_properties))

    def dict_expr(self):
        res = ParseResult()
        properties = []
        keys = []
        values = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LBRACE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected '{'",
                'context': self.context,
                'exit': False
            }))

        self.skipLines()

        start_token = self.current_token
        if self.current_token.type == tokenList.TT_LPAREN:
            self.reverse()
            sets_ = res.register(self.set_expr())
            if res.error: return res
            return res.success(sets_)
        else:
            if self.current_token.type == tokenList.TT_RBRACE:
                self.skipLines()
                return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
            else:
                while self.current_token.type == tokenList.TT_NEWLINE:
                    self.skipLines()
                if self.current_token.type == tokenList.TT_EOF:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': start_token.pos_start,
                        'pos_end': start_token.pos_end,
                        'message': "expected ',', '}' or a newline",
                        'context': self.context,
                        'exit': False
                    }))
                    
                if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                    if self.current_token.type == tokenList.TT_RBRACE:
                        self.skipLines()
                        return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                    properties.append({
                        'key': self.current_token,
                        'value': [],
                        'pos_start': self.current_token.pos_start.copy(),
                        'pos_end': self.current_token.pos_end.copy()
                    })
                    keys.append(self.current_token)
                    self.skipLines()
                    
                    if self.current_token.type != tokenList.TT_COLON:
                        if self.current_token.type == tokenList.TT_EQ or self.current_token.type == tokenList.TT_EQEQ:
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "expression cannot be an assignment",
                                'context': self.context,
                                'exit': False
                                }))
                        else:
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "'{' was not closed",
                                'context': self.context,
                                'exit': False
                            }))

                    self.skipLines()

                    value = res.register(self.expr())
                    if value == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an expression after ':'",
                            'context': self.context,
                            'exit': False
                        }))
                    if res.error:
                            return res
                    properties[-1]['value'] = value
                    values.append(value)

                    while self.current_token.type == tokenList.TT_NEWLINE:
                        self.skipLines()

                    if self.current_token.type == tokenList.TT_RBRACE:
                        self.skipLines()
                        return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))

                    while self.current_token.type == tokenList.TT_COMMA:
                        self.skipLines()

                        while self.current_token.type == tokenList.TT_NEWLINE:
                            self.skipLines()

                        if self.current_token.type == tokenList.TT_RBRACE:
                            self.skipLines()
                            return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))

                        if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                            properties.append({
                                'key': self.current_token,
                                'value': [],
                                'pos_start': self.current_token.pos_start.copy(),
                                'pos_end': self.current_token.pos_end.copy()
                            })
                            keys.append(self.current_token)
                            self.skipLines()

                            if self.current_token.type != tokenList.TT_COLON:
                                if self.current_token.type == tokenList.TT_EQ or self.current_token.type == tokenList.TT_EQEQ:
                                    return res.failure(self.error['Syntax']({
                                        'pos_start': self.current_token.pos_start,
                                        'pos_end': self.current_token.pos_end,
                                        'message': "expression cannot be an assignment",
                                        'context': self.context,
                                        'exit': False
                                        }))
                                else:
                                    return res.failure(self.error['Syntax']({
                                        'pos_start': self.current_token.pos_start,
                                        'pos_end': self.current_token.pos_end,
                                        'message': "'{' was not closed",
                                        'context': self.context,
                                        'exit': False
                                    }))

                            self.skipLines()

                            value = res.register(self.expr())
                            if value == '':
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "expected an expression after ':'",
                                    'context': self.context,
                                    'exit': False
                                }))
                            if res.error:
                                    return res
                            properties[-1]['value'] = value
                            values.append(value)

                            while self.current_token.type == tokenList.TT_NEWLINE:
                                self.skipLines()

                            if self.current_token.type == tokenList.TT_RBRACE:
                                self.skipLines()
                                return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))


                        # while self.current_token.type == tokenList.TT_NEWLINE:
                        #     self.skipLines()

                        # print(self.current_token, "is the current token")

                        # if self.current_token.type == tokenList.TT_EOF:
                        #     self.error_detected = True
                        #     return res.failure(self.error['Syntax']({
                        #         'pos_start': self.current_token.pos_start,
                        #         'pos_end': self.current_token.pos_end,
                        #         'message': "expected '}' or a newline",
                        #         'context': self.context,
                        #         'exit': False
                        #     }))

                        # if self.current_token.type == tokenList.TT_IDENTIFIER or tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING:
                        #     properties.append({
                        #         'key': self.current_token,
                        #         'value': [],
                        #         'pos_start': self.current_token.pos_start.copy(),
                        #         'pos_end': self.current_token.pos_end.copy()
                        #     })
                        #     keys.append(self.current_token)
                        #     self.skipLines()
                        #     print(keys,values, self.current_token)
                        #     if self.current_token.type != tokenList.TT_COLON:
                        #         return res.failure(self.error['Syntax']({
                        #             'pos_start': self.current_token.pos_start,
                        #             'pos_end': self.current_token.pos_end,
                        #             'message': "expected ':'",
                        #             'context': self.context,
                    #              'exit': False
                        #         }))
                        #     res.register_advancement()
                        #     self.advance()
                        #     value = res.register(self.expr())
                        #     if res.error: return res
                        #     properties[-1]['value'] = value
                        #     values.append(value)

                        #     while self.current_token.type == tokenList.TT_NEWLINE:
                        #         self.skipLines()

                        #     if self.current_token.type == tokenList.TT_RBRACE:
                        #         self.skipLines()
                        #         return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))

                        # else:
                        #     if self.current_token.type == tokenList.TT_RBRACE:
                        #         self.skipLines()
                        #         return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                        #     else:
                        #         return res.failure(self.error['Syntax']({
                        #             'pos_start': self.current_token.pos_start,
                        #             'pos_end': self.current_token.pos_end,
                        #             'message': "expected '}' or a newline",
                        #             'context': self.context,
                        #             'exit': False
                        #         }))

                    if self.current_token.type == tokenList.TT_RBRACE:
                        self.skipLines()
                        return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
                    else:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "'expected ',', or '}'",
                            'context': self.context,
                            'exit': False
                        }))
                self.skipLines()
            return res.success(DictNode(properties, keys, values, pos_start, self.current_token.pos_end.copy()))
  
    def set_expr(self):
        res = ParseResult()
        sets = []
        
        if self.current_token.type == tokenList.TT_LBRACE:
            self.skipLines()
        
        if self.current_token.type != tokenList.TT_LPAREN:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected '('",
                'context': self.context,
                'exit': False
            }))
            
        self.skipLines()
        
        pos_start = self.current_token.pos_start.copy()
        sets.append(res.register(self.expr()))
        
        while self.current_token.type == tokenList.TT_COMMA:
            self.skipLines()
            sets.append(res.register(self.expr()))
        
        
        if self.current_token.type != tokenList.TT_RPAREN:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected ')'",
                'context': self.context,
                'exit': False
            }))
        
        self.skipLines()
        

        
        if self.current_token.type == tokenList.TT_RBRACE:
            self.skipLines()
            
            return res.success(SetNode(sets, pos_start, self.current_token.pos_end.copy()))
        
        
        self.error_detected = True
        return res.failure(self.error['Syntax']({
            'pos_start': self.current_token.pos_start,
            'pos_end': self.current_token.pos_end,
            'message': "expected '}'",
            'context': self.context,
            'exit': False
        }))
    
    def class_def(self):
        res = ParseResult()
        inherit_class_name = None
        class_name = None
        doc_string = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'class'):
            res.register_advancement()
            self.advance()
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'class'",
                'context': self.context,
                'exit': False
            }))
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected a class name",
                'context': self.context,
                'exit': False
            }))

        class_name = self.current_token
        #class name has to be upper case
        # class name must be only letters
        if isFirstLetterUpper(class_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name must start with a capital letter",
                'context': self.context,
                'exit': False
            }))
        if isOnlyLetters(class_name.value) == False:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name can only contain letters",
                'context': self.context,
                'exit': False
            }))
        if class_name in tokenList.KEYWORDS:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as class name",
                'context': self.context,
                'exit': False
            }))
        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_LPAREN:
            self.skipLines()
            if self.current_token.type == tokenList.TT_IDENTIFIER:

                inherit_class_name = self.current_token
                self.skipLines()
                if self.current_token.type == tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "multiple inheritance not supported",
                        'context': self.context,
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ',' or ')'",
                        'context': self.context,
                        'exit': False
                    }))

                self.skipLines()

            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ')'",
                        'context': self.context,
                        'exit': False
                    }))

                self.skipLines()


        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected a newline",
                'context': self.context,
                'exit': False
            }))
        self.skipLines()

        methods = None
        class_fields_modifiers = None
        if self.current_token.type == tokenList.TT_DOC_STRING:
            doc_string = res.register(self.expr())
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers, doc_string))

        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers, doc_string))

            if self.current_token.type == tokenList.TT_IDENTIFIER:
                class_fields_modifiers = self.class_fields_modifiers()
            if self.current_token.matches(tokenList.TT_KEYWORD, "def"):
                methods = self.set_methods()
            else:
                while self.current_token.type != tokenList.TT_NEWLINE:
                    self.skipLines()
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_start,
                        'message': "invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers, doc_string))

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            class_fields_modifiers = self.class_fields_modifiers()

        if self.current_token.matches(tokenList.TT_KEYWORD, "def"):
            methods = self.set_methods()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers, doc_string))
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
            res.register_advancement()
            self.advance()
            return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers, doc_string))
        if self.current_token.type == tokenList.TT_EOF:
            return res.success(ClassNode(class_name, inherit_class_name, methods, class_fields_modifiers))

        self.error_detected = True
        return res.failure(self.error['Syntax']({
            'pos_start': self.current_token.pos_start,
            'pos_end': self.current_token.pos_end,
            'message': "invalid syntax",
            'context': self.context,
            'exit': False
        }))

    def class_fields_modifiers(self):
        res = ParseResult()
        class_fields = []
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))

        # class fields must start with @
        while self.current_token.type == tokenList.TT_IDENTIFIER:
            name = self.current_token
            # if has_at_symbol(name.value) == False:
            #     self.error_detected = True
            #     return res.failure(self.error['Syntax']({
            #         'pos_start': self.current_token.pos_start,
            #         'pos_end': self.current_token.pos_end,
            #         'message': "expected '@' before identifier",
            #         'context': self.context,
            #         'exit': False
            #     }))

            self.skipLines()

            field = {
                'name': name,
                'value': None
            }
            class_fields.append(field)
            if self.current_token.type != tokenList.TT_EQ:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected '='",
                    'context': self.context,
                    'exit': False
                }))

            self.skipLines()

            expr = res.register(self.expr())
            if res.error:
                    return res
            field['value'] = expr
            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a newline",
                    'context': self.context,
                    'exit': False
                }))
            while self.current_token.type == tokenList.TT_NEWLINE:
                self.skipLines()
        return class_fields

    def set_methods(self):
        res = ParseResult()
        methods = []
        Parser.scope = "function_method"
        doc_string = None
        type_hints = []
        type_hint = {}
        while self.current_token.matches(tokenList.TT_KEYWORD, "def"):
            default_values = {}
            default_values_list = []
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_KEYWORD:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an identifier",
                    'context': self.context,
                    'exit': False
                }))
            method_name = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token.type != tokenList.TT_LPAREN:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected '('",
                    'context': self.context,
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            args_list = []
            if self.current_token.type == tokenList.TT_IDENTIFIER or self.current_token.type == tokenList.TT_MUL:
                args_list.append(self.current_token)
                if self.current_token.type == tokenList.TT_MUL:
                    self.skipLines()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                    args_list[0] = StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(
                        self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok

                default_values = {
                    'name': args_list[0].value,
                    'value': ''
                }

                self.skipLines()
                if self.current_token.type == tokenList.TT_COLON:
                    type_hint = {
                        args_list[0].value: {
                            'type': '',
                        }
                    }
                    self.skipLines()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected a type",
                            'context': self.context,
                            'exit': False
                        }))
                    type_hint[args_list[0].value]['type'] = self.current_token.value
                    type_hints.append(type_hint)
                    self.skipLines()
                if self.current_token.type == tokenList.TT_EQ:
                    self.skipLines()
                    default_values['value'] = res.register(self.expr())
                    default_values_list.append(default_values)
                    for default_value in default_values_list:
                        if is_varags(default_value['name']):
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "parameter with * or ** cannot have default values",
                                'context': self.context,
                                'exit': False
                            }))
                    if default_values['value'] == None or default_values['value'] == '':
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax",
                            'context': self.context,
                            'exit': False
                        }))
                    if res.error:
                            return res
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    if self.current_token.type != tokenList.TT_IDENTIFIER and self.current_token.type != tokenList.TT_MUL:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))

                    args_list.append(self.current_token)

                    if self.current_token.type == tokenList.TT_MUL:
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "expected an identifier",
                                'context': self.context,
                                'exit': False
                            }))
                        args_list[-1] = StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(
                            self.current_token.value), self.current_token.pos_start, self.current_token.pos_end)).tok

                    default_values = {
                        'name': args_list[-1].value,
                        'value': ''
                    }

                    self.skipLines()
                    # if len(args_list) > 20:
                    #     self.error_detected = True
                    #     return res.failure(self.error['Syntax']({
                    #     'pos_start': self.current_token.pos_start,
                    #     'pos_end': self.current_token.pos_end,
                    #     'message': "Cannot have more than 12 arguments",
                    #     'context': self.context,
                    #     'exit': False
                    # }))
                    # only one *args or **kwargs is allowed
                    splats = []
                    for arg_name in args_list:
                        if is_varags(arg_name.value):
                            splats.append(arg_name.value)
                    if len(splats) > 1:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "invalid syntax - only one * or ** is allowed",
                            'context': self.context,
                            'exit': False
                        }))
                    if self.current_token.type == tokenList.TT_COLON:
                        type_hint = {
                            args_list[-1].value: {
                                'type': '',
                            }
                        }
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "expected a type",
                                'context': self.context,
                                'exit': False
                            }))
                        type_hint[args_list[-1].value]['type'] = self.current_token.value
                        type_hints.append(type_hint)
                        self.skipLines()
                    if self.current_token.type == tokenList.TT_EQ:
                        self.skipLines()
                        default_values['value'] = res.register(self.expr())
                        default_values_list.append(default_values)
                        # parameter with *args or **kwargs can't have default values
                        for default_value in default_values_list:
                            if is_varags(default_value['name']):
                                self.error_detected = True
                                return res.failure(self.error['Syntax']({
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': "parameter with * or ** cannot have default values",
                                    'context': self.context,
                                    'exit': False
                                }))
                        if default_values['value'] == None or default_values['value'] == '':
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "invalid syntax",
                                'context': self.context,
                                'exit': False
                            }))
                        if res.error:
                                return res
                        duplicate_key = None
                        is_duplicate = False
                        keys_count = []
                        for key in default_values_list:
                            first_key = key['name']
                            keys_count.append(first_key)
                        for key in keys_count:
                            if keys_count.count(key) > 1:
                                duplicate_key = key
                                is_duplicate = True
                                break
                        if is_duplicate:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': f"duplicate argument: '{duplicate_key}' in method '{method_name.value}'",
                                'context': self.context,
                                'exit': False
                            }))
                    else:
                        if len(default_values_list) > 0:
                            self.error_detected = True
                            return res.failure(self.error['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "non-default argument cannot be followed by a default argument",
                                'context': self.context,
                                'exit': False
                            }))
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ')'",
                        'context': self.context,
                        'exit': False
                    }))

            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ')'",
                        'context': self.context,
                        'exit': False
                    }))

            self.skipLines()
            if self.current_token.type == tokenList.TT_COLON:
                type_hint = {
                    "return_type": {
                        'type': '',
                    }
                }
                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected a type",
                        'context': self.context,
                        'exit': False
                    }))
                type_hint['return_type']['type'] = self.current_token.value
                type_hints.append(type_hint)
                self.skipLines()
            
            if self.current_token.type == tokenList.TT_ARROW:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "'->' not allowed in class methods",
                    'context': self.context,
                    'exit': False
                }))

            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a newline",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_DOC_STRING:
                doc_string = res.register(self.expr())
            body = res.register(self.statements())
            if res.error:
                    return res
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                methods.append({
                    'name': method_name,
                    'value': FunctionNode(method_name, args_list, body, False, default_values_list, "method", doc_string, type_hints=type_hints),
                    'args': args_list,
                    'pos_start': method_name.pos_start,
                    'pos_end': body.pos_end
                })

                if self.current_token.type != tokenList.TT_NEWLINE:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected a 'end' or a newline",
                        'context': self.context,
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_start,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
        self.methods = methods
        # ini_args = []
        # for method in self.methods:
        #     if method['name'].value == "init":

        return methods

    def match_expr(self):
        res = ParseResult()
        cases = []
        default_case = None

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'match'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'match'",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        expression = res.register(self.expr())
        if expression == "":
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected an expression',
                    'context': self.context,
                    'exit': False
                }
            ))
        if res.error:
                return res

        if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected ":"',
                        'context': self.context,
                        'exit': False
                    }
                ))
        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_NEWLINE:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected a newline",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                cases = []
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
            if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
                cases = self.set_cases()
            elif self.current_token.matches(tokenList.TT_KEYWORD, "default"):
                default_case = res.register(self.set_default_case())
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                cases = []
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))

        if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            cases = self.set_cases()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
            res.register_advancement()
            self.advance()
            return res.success(MatchNode(expression, cases, default_case))

        if self.current_token.matches(tokenList.TT_KEYWORD, "default"):
            default_case = self.set_default_case()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        if self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            cases = self.set_cases()
            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
                return res.success(MatchNode(expression, cases, default_case))
        return res.failure(self.error['Syntax']({
            'pos_start': self.current_token.pos_start,
            'pos_end': self.current_token.pos_end,
            'message': "invalid syntax for match, expected 'end' or 'case'",
            'context': self.context,
            'exit': False
        }))

    def set_cases(self):
        res = ParseResult()
        cases = []
        while self.current_token.matches(tokenList.TT_KEYWORD, "case"):
            res.register_advancement()
            self.advance()
            case_expr = res.register(self.expr())
            if res.error:
                    return res
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected ":"',
                        'context': self.context,
                        'exit': False
                    }
                ))
            res.register_advancement()
            self.advance()

            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a newline",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())

            if len(statements.elements) > 0:
                if statements.elements[0] == '':
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': start_token.pos_start,
                            'pos_end': start_token.pos_end,
                            'message': 'expected an expression',
                            'context': self.context,
                            'exit': False
                        }
                    ))
            if res.error:
                return res
            cases.append({
                'case': case_expr,
                'body': statements,
                "pos_start": start_token.pos_start,
                "pos_end": statements.pos_end
            })

            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                res.register_advancement()
                self.advance()
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected "end"',
                        'context': self.context,
                        'exit': False
                    }
                ))


        return cases

    def set_default_case(self):
        res = ParseResult()
        default_case = {}
        if self.current_token.matches(tokenList.TT_KEYWORD, "default"):
            res.register_advancement()
            self.advance()
            default_case_expr = res.register(self.expr())
            if default_case_expr != "":
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'default case must be an empty expression',
                        'context': self.context,
                        'exit': False
                    }
                ))
            if res.error:
                    return res
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected ":"',
                        'context': self.context,
                        'exit': False
                    }
                ))
            res.register_advancement()
            self.advance()

            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a newline",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            start_token = self.current_token
            statements = res.register(self.statements())

            # if len(statements.elements) > 0:
            #     if statements.elements[0] == '':
            #         self.error_detected = True
            #         return res.failure(self.error['Syntax'](
            #             {
            #                 'pos_start': start_token.pos_start,
            #                 'pos_end': start_token.pos_end,
            #                 'message': 'expected an expression',
            #                 'context': self.context,
            #                 'exit': False
            #             }
            #         ))
            if res.error:
                return res
            default_case = {
                'case': default_case_expr,
                'body': statements,
                'pos_start': start_token.pos_start,
                'pos_end': start_token.pos_end
            }
            if self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                res.register_advancement()
                self.advance()
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected "end"',
                        'context': self.context,
                        'exit': False
                    }
                ))

        return default_case

    def spread_expr(self, name, assign_token):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        start_token = self.current_token
        dict_values = []
        

        expr = res.register(self.expr())
        if res.error:
                return res
        if not isinstance(expr, ListNode) and isinstance(expr, PairNode) and isinstance(expr, DictNode) and isinstance(expr, ObjectNode):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end,
                    'message': 'cannot spread a non-iterable',
                    'context': self.context,
                    'exit': False
                }
            ))
        spread_node = SpreadNode(
                assign_token, name, expr, start_token.pos_start, self.current_token.pos_end)
        return res.success(spread_node)

    def list_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LSQBRACKET:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected '['",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        start_token = self.current_token
        if self.current_token.type == tokenList.TT_RSQBRACKET:
            res.register_advancement()
            self.advance()
        else:
            while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()

                    start_token = self.current_token
            if self.current_token.type == tokenList.TT_MUL:
                self.skipLines()
                if res.error:
                        return res
                current_token = self.current_token
                if current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str(
                    "*") + str(current_token.value), current_token.pos_start, current_token.pos_end)))
                self.skipLines()

                if self.current_token.type != tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "cannot use starred expression here",
                        'context': self.context,
                        'exit': False
                    }))

            else:
                element = res.register(self.expr())
                if res.error:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Epected an expression",
                        'context': self.context,
                        'exit': False
                    }))
                elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    return res.success(ListNode(elements, pos_start, self.current_token.pos_end))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                if self.current_token.type == tokenList.TT_MUL:
                    self.skipLines()
                    if res.error:
                            return res
                    current_token = self.current_token
                    if current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                    elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(current_token.value), current_token.pos_start, current_token.pos_end)))
                    self.skipLines()
                else:
                    element = res.register(self.expr())
                    if res.error:
                        return res
                    elements.append(element)

                if element == "":
                    elements.pop()
                    continue
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    return res.success(ListNode(elements, pos_start, self.current_token.pos_start.copy()))


            if self.current_token.type != tokenList.TT_RSQBRACKET:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': start_token.pos_start,
                    'pos_end': start_token.pos_end,
                    'message': "expected an expression, ',', or ']'",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            for element in elements:
                if element == "":
                    elements.pop()
                    continue

            if self.current_token != None and self.current_token.type in operation_methods:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))

        return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))

    def pair_expr(self):
        
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LPAREN:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected '('",
                'context': self.context,
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        start_token = self.current_token
        if self.current_token.type == tokenList.TT_RPAREN:
            res.register_advancement()
            self.advance()
        else:
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                start_token = self.current_token
            
            if self.current_token.type == tokenList.TT_MUL:
                self.skipLines()
                if res.error:
                        return res
                current_token = self.current_token
                if current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str(
                    "*") + str(current_token.value), current_token.pos_start, current_token.pos_end)))
                self.skipLines()

                if self.current_token.type != tokenList.TT_COMMA:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "cannot use starred expression here",
                        'context': self.context,
                        'exit': False
                    }))

            else:
                element = res.register(self.expr())
                if res.error:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Epected an expression",
                        'context': self.context,
                        'exit': False
                    }))
                elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                    return res.success(PairNode(elements, pos_start, self.current_token.pos_start.copy()))
                while self.current_token.type == tokenList.TT_NEWLINE:
                    self.skipLines()

                if self.current_token.type == tokenList.TT_MUL:
                    self.skipLines()
                    if res.error:
                            return res
                    current_token = self.current_token
                    if current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an identifier",
                            'context': self.context,
                            'exit': False
                        }))
                    elements.append(StringNode(Token(tokenList.TT_IDENTIFIER, str("*") + str(current_token.value), current_token.pos_start, current_token.pos_end)))
                    self.skipLines()

                else:
                    element = res.register(self.expr())
                    if res.error:
                            return res
                    elements.append(element)
                if element == "":
                    elements.pop()
                    continue
            while self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_RPAREN:
                    res.register_advancement()
                    self.advance()
                    return res.success(PairNode(elements, pos_start, self.current_token.pos_start.copy()))

            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected an expression, ',', or ')'",
                    'context': self.context,
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            for element in elements:
                if element == "":
                    elements.pop()
                    continue

            if self.current_token != None and self.current_token.type in operation_methods:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
        return res.success(PairNode(elements, pos_start, self.current_token.pos_end.copy()))

    def string_interp(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        inter_pv = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'fm'):
            res.register_advancement()
            self.advance()
            string_to_interp = self.current_token.value
            while self.current_token.type == tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING or tokenList.TT_BACKTICK:
                value = self.current_token.value
                string_repr = self.current_token
                regex = Regex().compile('%{(.*?)}')
                if value.count('{') != value.count('}'):
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "fm-string: unmatched '{'" if value.count('{') > value.count('}') else "fm-string: unmatched '}'",
                        'context': self.context,
                        'exit': False
                    }))
                regex2 = Regex().compile('%%{{(.*?)}}')
                if regex2.match(value):
                    value = regex2.sub('%{\\1}', value)
                if value.find('{{') != -1:
                    value = value.replace('{{', '{').replace('}}', '}')
                interp_values = regex.match(value)
                if interp_values:
                    inter_pv = interp_values
                    expr = res.register(self.expr())
                    interpolated_string = self.make_string_expr(
                        inter_pv, pos_start, string_repr)
                    return res.success(StringInterpNode(expr,  interpolated_string, string_to_interp, pos_start, self.current_token.pos_end.copy(), inter_pv))
                else:
                    expr = res.register(self.expr())
                    return res.success(StringInterpNode(expr, value, string_to_interp, pos_start, self.current_token.pos_end.copy()))
            else:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "expected a string",
                    'context': self.context,
                    'exit': False
                }))
        return res.success(StringNode(self.current_token))

    def make_string_expr(self, inter_pv, position, string_repr):
        interpolated = []
        for el in inter_pv:
            if el == '':
                self.error_detected = True
                self.error['Syntax']({
                    'pos_start': position,
                    'pos_end': position,
                    'message': "fm-string: no empty expressions",
                    'context': self.context,
                    'exit': False
                })

            environment = self.current_token.pos_start.environment if self.current_token != None else None
            mod_name = self.current_token.pos_start.module_name if self.current_token != None else None
            lexer = Lexer(self.file_name, el, self.context, position,
                          environment, mod_name, string_repr)
            token, error = lexer.make_tokens()
            parser = Parser(token, self.file_name, self.context, position)
            ast = parser.parse()
            for element in ast.node.elements:
                interpolated.append(element)
                self.string_expr = interpolated
        return self.string_expr

    def byte_expr(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        self.skipLines()
        if self.current_token.type == tokenList.TT_DOUBLE_STRING or tokenList.TT_SINGLE_STRING or tokenList.TT_BACKTICK:
            byte_string = self.current_token
            self.skipLines()
            return res.success(ByteStringNode(byte_string))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected a string",
                'context': self.context,
                'exit': False
            }))

    def index_get(self, atom):
        res = ParseResult()
        index = 0
        if self.current_token.type == tokenList.TT_LSQBRACKET:
            res.register_advancement()
            self.advance()
            index = res.register(self.expr())
            if index == None or index == "":
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected index or slice expression",
                        'context': self.context,
                        'exit': False
                    }))
            if isinstance(index, ListNode) or isinstance(index, PairNode):
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
            if res.error:
                    return res

            if self.current_token.type == tokenList.TT_RSQBRACKET:
                self.skipLines()
                
                if self.current_token.type == tokenList.TT_EQ:
                    res.register_advancement()
                    self.advance()
                    value = res.register(self.expr())
                    if value == "":
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an expression",
                            'context': self.context,
                            'exit': False
                        }))

                    if res.error:
                            return res
                    if index == "":
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an expression",
                            'context': self.context,
                            'exit': False
                        }))
                    return res.success(IndexNode(atom, index, value, "="))
                elif self.current_token.type != None and self.current_token.type in operation_methods:
                    operator = self.current_token
                    # if not isinstance(atom, VarAccessNode):
                    #     print(type(atom))
                    #     self.error_detected = True
                    #     return res.failure(self.error['Syntax']({
                    #         'pos_start': self.current_token.pos_start,
                    #         'pos_end': self.current_token.pos_end,
                    #         'message': "Illegal expression: invalid left hand side",
                    #         'context': self.context,
                    #         'exit': False
                    #     }))
                    res.register_advancement()
                    self.advance()
                    value = res.register(self.expr())
                    if value == "":
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an expression",
                            'context': self.context,
                            'exit': False
                        }))
                    if res.error: return res
                    if index == "":
                        self.error_detected = True
                        return res.failure(self.error['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "expected an expression",
                            'context': self.context,
                            'exit': False
                        }))
                    return res.success(IndexNode(atom, index, value, operation_methods[operator.type]))
                return res.success(IndexNode(atom, index))

            elif self.current_token.type == tokenList.TT_COLON:
                res.register_advancement()
                self.advance()
                start = index if index != "" else None
                end = res.register(self.expr())
                if res.error:
                        return res
                if self.current_token.type == tokenList.TT_COLON:
                    res.register_advancement()
                    self.advance()
                    step = res.register(self.expr())
                    if res.error:
                            return res
                    if self.current_token.type == tokenList.TT_RSQBRACKET:
                        res.register_advancement()
                        self.advance()
                        if end == "":
                            end = None
                        return res.success(SliceNode(atom, start, end, step=step, type="colon"))
                elif self.current_token.type == tokenList.TT_RSQBRACKET:
                    res.register_advancement()
                    self.advance()
                    if end == "":
                        end = None
                    return res.success(SliceNode(atom, start, end, step=None))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ']'",
                        'context': self.context,
                        'exit': False
                    }))

            elif self.current_token.type == tokenList.TT_DOUBLE_COLON:
                self.skipLines()
                start = index if index != "" else None
                end = res.register(self.expr())
                type_ = "double_colon"
                if res.error:
                        return res
                if self.current_token.type == tokenList.TT_RSQBRACKET:
                    self.skipLines()
                    if end == "":
                        end = None
                    return res.success(SliceNode(atom, start, end, step=None, type=type_))
                else:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "expected ']'",
                        'context': self.context,
                        'exit': False
                    }))

            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "invalid index expression",
                    'context': self.context,
                    'exit': False
                }))

    def raise_expr(self):
        res = ParseResult()
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'raise'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'raise'",
                'context': self.context,
                'exit': False
            }))
        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            _Exception = res.register(self.expr())
            if res.error:
                    return res
            return res.success(RaiseNode(_Exception))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))

    def del_expr(self):
        res = ParseResult()
        expression = None
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'del'):
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected 'del'",
                'context': self.context,
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        identifier = self.current_token
        if identifier == "":
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an expression",
                'context': self.context,
                'exit': False
            }))
        if identifier.type == tokenList.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_DOT:
                res.register_advancement()
                self.advance()
                expression = res.register(self.access_property(identifier))
                return res.success(DelNode(identifier, expression))
            elif self.current_token.type == tokenList.TT_LSQBRACKET:
                expression = res.register(self.expr())
                return res.success(DelNode(identifier, expression))
            else:
                if self.current_token.type != tokenList.TT_NEWLINE and self.current_token.type != tokenList.TT_EOF:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "invalid del expression",
                        'context': self.context,
                        'exit': False
                    }))
        else:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "expected an identifier",
                'context': self.context,
                'exit': False
            }))
        if res.error:
                return res
        return res.success(DelNode(identifier, expression))

    def attempt_expr(self):
        res = ParseResult()
        is_loop = True if hasattr(Parser, 'scope') and Parser.scope == 'loop' else False
        Parser.scope = "loop" if is_loop else None
        exception = None
        attempt_statement = {}
        catches = []
        catch_statement = {}
        finally_statement = {}
        pos_start = self.current_token.pos_start.copy()
        if not self.current_token.matches(tokenList.TT_KEYWORD, "attempt"):
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected "attempt"',
                    'context': self.context,
                    'exit': False
                }
            ))
        start_token = self.current_token
        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_COLON:
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected ":"',
                    'context': self.context,
                    'exit': False
                }
            ))

        res.register_advancement()
        self.advance()
        attempt_statements = res.register(self.statements())
        attempt_statement = {
            'body': attempt_statements,
            'pos_start': start_token.pos_start,
            'pos_end': attempt_statements.pos_end
        }
        for statement in attempt_statements.elements:
            if statement == None or statement == '':
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': start_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'attempt statement cannot be empty',
                        'context': self.context,
                        'exit': False
                    }
                ))
        while self.current_token.type == tokenList.TT_NEWLINE:
            self.skipLines()
        is_loop = True if hasattr(Parser, 'scope') and Parser.scope == 'loop' else False
        
        # if is_loop == False:
        #     Parser.scope = "loop"
        
        while self.current_token.matches(tokenList.TT_KEYWORD, "catch"):
            
            self.skipLines()
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                    exception = {
                        'name': self.current_token,
                        'as': None,
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end
                    }
                    self.skipLines()
                    if self.current_token.matches(tokenList.TT_KEYWORD, "as"):
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_IDENTIFIER:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'expected an identifier',
                                    'context': self.context,
                                    'exit': False
                                }
                            ))
                        exception['as'] = self.current_token
                        self.skipLines()
                        if self.current_token.type != tokenList.TT_COLON:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'expected ":"',
                                    'context': self.context,
                                    'exit': False
                                }
                            ))
                        self.skipLines()
                        statements = res.register(self.statements())
                        catch_statement = {
                            'exception': exception,
                            'body': statements,
                            'pos_start': exception['pos_start'],
                            'pos_end': exception['pos_end']
                        }
                        catches.append(catch_statement)
                    else:
                        if self.current_token.type != tokenList.TT_COLON:
                            self.error_detected = True
                            return res.failure(self.error['Syntax'](
                                {
                                    'pos_start': self.current_token.pos_start,
                                    'pos_end': self.current_token.pos_end,
                                    'message': 'expected ":"',
                                    'context': self.context,
                                    'exit': False
                                }
                            ))
                        self.skipLines()
                        
                        
                        statements = res.register(self.statements())
                        catch_statement = {
                            'exception': exception,
                            'body': statements,
                            'pos_start': exception['pos_start'],
                            'pos_end': exception['pos_end']
                        }
                        catches.append(catch_statement)
            else:
                if self.current_token.type != tokenList.TT_COLON:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'expected ":"',
                            'context': self.context,
                            'exit': False
                        }
                    ))
                pos_start = self.current_token.pos_start.copy()
                self.skipLines()
                statements = res.register(self.statements())
                catch_statement = {
                    'exception': None,
                    'body': statements,
                    'pos_start': pos_start,
                    'pos_end':  statements.pos_end
                }
                catches.append(catch_statement)

        if self.current_token.matches(tokenList.TT_KEYWORD, "finally"):
            
            self.skipLines()
            if self.current_token.type != tokenList.TT_COLON:
                self.error_detected = True
                return res.failure(self.error['Syntax'](
                    {
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected ":"',
                        'context': self.context,
                        'exit': False
                    }
                ))
            self.skipLines()
            statements = res.register(self.statements())
            finally_statement = {
                'body': statements,
                'pos_start': self.current_token.pos_start,
                'pos_end': statements.pos_end
            }

        # else:
        #     print("no finally", self.current_token)
        #     self.error_detected = True
        #     return res.failure(self.error['Syntax'](
        #         {
        #             'pos_start': start_token.pos_start,
        #             'pos_end': start_token.pos_end,
        #             'message': 'attempt statement must have a catch or finally clause',
        #             'context': self.context,
        #             'exit': False
        #         }
        #     ))

        while self.current_token.type == tokenList.TT_NEWLINE:
            self.skipLines()

        # catch with no exception must be last
        if len(catches) > 1:
            for i in range(len(catches) - 1):
                if catches[i]['exception'] == None:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': catches[i]['pos_start'],
                            'pos_end': catches[i]['pos_end'],
                            'message': "default 'catch' must be last",
                            'context': self.context,
                            'exit': False
                        }
                    ))

        if not self.current_token.matches(tokenList.TT_KEYWORD, "end"):
                self.error_detected = True
                if self.current_token.matches(tokenList.TT_KEYWORD, "finally") or self.current_token.matches(tokenList.TT_KEYWORD, "catch"):
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'invalid syntax',
                            'context': self.context,
                        'exit': False
                    }))
                else:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': 'expected "end"',
                        'context': self.context,
                        'exit': False
                    }))
        self.skipLines()
        attempt_node = AttemptNode(
                attempt_statement, catches, finally_statement, pos_start, self.current_token.pos_end)
        
        return res.success(attempt_node)

    def make_path(self, base_):
        res = ParseResult()
        paths = []
        paths.append(base_)
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'expected an identifier',
                    'context': self.context,
                    'exit': False
                }
            ))

        path = self.current_token.value
        self.skipLines()
        paths.append(path)
        while True:
            if self.current_token.type == tokenList.TT_DOUBLE_COLON:
                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    self.error_detected = True
                    return res.failure(self.error['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'expected an identifier',
                            'context': self.context,
                            'exit': False
                        }
                    ))
                paths.append(self.current_token.value)
                self.skipLines()
                while self.current_token.type == tokenList.TT_DOUBLE_COLON:
                    self.skipLines()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        self.error_detected = True
                        return res.failure(self.error['Syntax'](
                            {
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': 'expected an identifier',
                                'context': self.context,
                                'exit': False
                            }
                        ))
                    paths.append(self.current_token.value)
                    self.skipLines()
            else:
                break

        return paths

    def import_expr(self):
        res = ParseResult()
        module_name = ''
        properties = []
        mods = []
        module_alias = None
        module_path = None
        module_name_as = None

        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'import'):
            self.skipLines()


        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': f"expected an identifier",
                'context': self.context,
                'exit': False
            }))

        module_name = self.current_token

        self.skipLines()

        while self.current_token.type == tokenList.TT_COMMA:
            self.skipLines()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"expected an identifier",
                    'context': self.context,
                    'exit': False
                }))

            properties.append(module_name)
            properties.append(self.current_token)
            self.skipLines()

        if self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
                if len(properties) > 0:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))

                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                module_alias = self.current_token
                self.skipLines()

        if self.current_token.matches(tokenList.TT_KEYWORD, 'from'):
            if len(properties) == 0:
                properties.append(module_name)
            if module_name.value in builtin_modules:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
            self.skipLines()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"expected an identifier",
                    'context': self.context,
                    'exit': False
                }))

            base = res.register(self.atom()).name.value
            if self.current_token.type == tokenList.TT_DOUBLE_COLON:
                self.skipLines()
                make_path = self.make_path(base)
                module_path = make_path

            if module_path is None:
                module_path = [base]

            if self.current_token.type != tokenList.TT_NEWLINE:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"invalid syntax",
                    'context': self.context,
                    'exit': False
                }))
        else:
            mods = properties
        module_name_as = properties[-1] if len(properties) > 0 else module_name
        return res.success(ImportNode(module_name, properties, module_alias, module_path, module_name_as, "import",mods))

    def from_import_expr(self):
        res = ParseResult()
        module_name = ''
        properties = []
        module_alias = None
        module_path = None
        module_name_as = None
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'from'):
            self.skipLines()


        if self.current_token.type != tokenList.TT_IDENTIFIER:
            if self.current_token.type == tokenList.TT_DOT:
                module_name = Token(tokenList.TT_IDENTIFIER, str("."), pos_start, self.current_token.pos_end)
                from_module_name = module_name
                self.skipLines()
            else:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"expected an identifier or '.'",
                    'context': self.context,
                    'exit': False
                }))

        elif self.current_token.type == tokenList.TT_IDENTIFIER:
            module_name = self.current_token
            from_module_name = module_name
            self.skipLines()

        if self.current_token.type == tokenList.TT_DOUBLE_COLON:
            self.skipLines()
            make_path = self.make_path(module_name.value)
            module_path = make_path

        if module_path is None:
            module_path = [module_name.value]


        if not self.current_token.matches(tokenList.TT_KEYWORD, 'import'):
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': f"expected an identifier",
                'context': self.context,
                'exit': False
            }))

        self.skipLines()

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            module_name = self.current_token
            properties.append(self.current_token)
            self.skipLines()

        elif self.current_token.type == tokenList.TT_MUL:
                module_name = Token(tokenList.TT_IDENTIFIER, '*', self.current_token.pos_start, self.current_token.pos_end)
                properties.append(module_name)
                self.skipLines()
        else:
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': f"expected an identifier",
                'context': self.context,
                'exit': False
            }))


        while self.current_token.type == tokenList.TT_COMMA:
            self.skipLines()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                self.error_detected = True
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"expected an identifier",
                    'context': self.context,
                    'exit': False
                }))
            properties.append(self.current_token)
            self.skipLines()

        if self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
                if module_name.value  == '*':
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))
                if len(properties) > 1:
                    self.error_detected = True
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"invalid syntax",
                        'context': self.context,
                        'exit': False
                    }))

                self.skipLines()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    return res.failure(self.error['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"expected an identifier",
                        'context': self.context,
                        'exit': False
                    }))
                module_alias = self.current_token
                self.skipLines()

        module_name_as = module_path[-1] if len(
                module_path) > 0 else module_name

        return res.success(ImportNode(module_name, properties, module_alias, module_path, module_name_as, "from", None, from_module_name))

    def freeze_expr(self):
        res = ParseResult()
        
        self.skipLines()
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            self.error_detected = True
            return res.failure(self.error['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': f"expected an identifier",
                'context': self.context,
                'exit': False
            }))
        object = res.register(self.expr())
        
        return res.success(FreezeNode(object))

    def binaryOperation(self, func_1, ops, func_2=None):
        if func_2 == None:
            func_2 = func_1

        res = ParseResult()
        left = res.register(func_1())
        if res.error:
            self.error_detected = True
            return res

        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(func_2())
            if res.error:
                return res
            try:
                left = BinOpNode(left, op_tok, right)
                # if left == '' or right == '' or op_tok == '':
                #     res.failure(self.error['Syntax']({
                #         'pos_start': self.current_token.pos_start,
                #         'pos_end': self.current_token.pos_end,
                #         'message': 'Invalid syntax',
                #         'context': self.context,
                #         'exit': False
                #     }))
            except Exception as e:
                return res.failure(self.error['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Invalid syntax",
                    'context': self.context,
                    'exit': False
                }))

        return res.success(left)






li = [1, 2,3,4,5,6,7,8,9,10]
# print(li[])

# pa = (1,2,3,4,5,6,7,8,9,10)
# print(pa[:2:1])
# di = {'name1':'james', 'name2':'bond'}
# print(di['name1'])
# def getname(name):
#     return di[name]
# print(getname('name1'))
# name = 'james'
# print(name[::-1])

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SYMBOLS = '@_'
num = 123
num2 = 123.456
LETTERS_SYMBOLS = LETTERS + SYMBOLS


# class Test:
#     def test(a, b):
#         return a + b

# test.go = 1
# # print all test attributes
# print(test)
# num = 1
# for i in range(10):
#     num = num + i
#     print(f"num = {num}")
# hello = 'hello'
# world = 'world'
# li += "hello"
# print(li * 2)
# a = 20
# b = 30
# a = b
# print(a)
# num = 16
# # fizzbuzz
# for i in range(num):
#     print(i)
# a = 20
# b = 30
# c = a+1
# d = b+1
# e = a-1
# f = int("40")
# def setnum():
#     return 2

# a += setnum() + 1 # expecting to 23
# b -= setnum() - 1 # expecting to 29
# c /= setnum() / 2 # expecting to 21.0
# d *= setnum() * 2 # expecting to 120
# e %= setnum() % 3 # expecting to 1
# print(f"a = {a}, b = {b}, c = {c}, d = {d}, e = {e}")
# count = 0
# for i in range(1, 10):
#     for j in range(1, 10):
#         for k in range(1, 10):
#             if i != j and i != k and j != k:
#                 count += 1
#                 print(f"{i} * {j} * {k} = {i*j*k}")
# print(count)
# r = 'name'
# li = [1,2,]
# d = {2:1, 3:2, 4:3}
# li2 = [4,5,6]
# new_li = [*li, *li2, 7, 8, 9]
# print(hasattr(d, "2"))
# num1 = 0
# class Test:
#     pass
# def greet(name):
#     pass
# try:
#     print(greet())
# except NameError as e:
#     print(f"Error: {e}")
# except Exception as e:
#     print(f"Exception: {e}")
# except TypeError as TypeError:
#     print(f"TypeError: {TypeError}")
# finally:
#     print("Finally")
# name = "Kenny"
# def greet(name):
#     return f"Hello, {name}"

# pair = ("a", "e", "i", "o", "u", 'e')
# list = [1,2,3,4,5,6,7,8,9,10]
# dict = {'name': 'Kenny', 'age': 23, 'hobby': 'Playing soccer'}
# strn = "Hello, World!"
# class Employee:
#     def create(self,name):
#         return f"Hello, {name}"
# data = {}
# if data or {}:
#     print("data is empty")
# else:
#     print("data is not empty")

# print(f"'not' operator on true: %{not(True)}")  # false
# print(f"'not' operator on false: %{not(False)}") # true
# print(f"'not' operator on none: %{not(None)}")  # true
# print(f"'not' operator on int: %{not(1)}")     # false
# print(f"'not' operator on float: %{not(1.0)}") # false
# print(f"'not' operator on string: %{not('')}") # true
# print(f"'not' operator on list: %{not([])}")  # false
# print(f"'not' operator on pair: %{not(pair)}") # false
# print(f"'not' operator on dict: %{not(dict)}") # false
# print(f"'not' operator on class: %{not(Employee)}") # false
# print(f"'not' operator on function: %{not(greet)}") # false
# print(f"'not' operator on builtin_function: %{not(print)}") # false
# print(f"'not' operator on builtin_class: %{not(Exception)}") # false
# print(f"'not' operator on builtin_method: %{not(strn.upper)}") # false
# print(f"'not' operator on builtin_type: %{not(strn)}") # false
# print(f"'not' operator on none: %{not(None)}") # false
# l = [1,2,3,4,5,6,7,8,9,10]
# l += {'name': 'Kenny'}
# print(l)
# num = 2
# num **= 0
# print("num is: %d" % num)
# x = range(1,10)
# # for i in x:
# #     print(i)

# employee = Employee()
# print(employee)

class Animal:
    animals = []

    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name} is eating")

    def set_animals(self):
        self.animals.append(self.name)

    def get_animals(self):
        return self.animals


animal = Animal("Dog")
animal2 = Animal("Cat")
animal3 = Animal("Bird")
animal.set_animals()
animal2.set_animals()
animal3.set_animals()
#print(animal.get_animals())
#print(dict(key="name", value="Bob", age=23))


def greet(name, age, email=None, hobby=None, verified=False, test=""):
    print("SENDING EMAIL")
    print(f"Hello, %{name}, you are %{age} years old and your email is %{email}, and your hobby is %{hobby}, and you are %{verified} and your test is %{test}")


#greet("Bob",age=25)


def greet(*names, message="Hello",):
    for name in names:
        print(f"{message}, {name}")

#greet()


class Person:
    def __init__(self, *args):
        self.name = args[0]
        self.age = args[1]

person = Person("Bob", 23)


def join_sep(*args, sep=","):
    nums = ''
    for arg in args:
        nums += str(arg) + sep
    return nums
#print(join_sep('-',1,2,3,4,5))

li = [1, 2,3,]
*args, a,b = li
#print( args, "is args")

# d = {'name': 'John', 'age': 21, 'hobby': 'Playing soccer'}
# *args,a,b,c = d
# print(a,b,c, args, "is args dict")

#print(1,2,3, sep="-", end="\n")
# class A:
#     def __init__(self, name):
#         self.name = name

#     def Test(self, *args,greeting, name):
#         print(args,greeting, name)

#     def toString(self):
#         return f"Class %{self.name}"

# a = A("Bob")
# a.Test("Hello", "World", greeting="Hi", name="Bob")

# d = dict()
# print(d)
