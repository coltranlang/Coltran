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
#   Interpreter/interpreter.py
# Author:
#   Kehinde Akinsanya
# Created:
#   October 28, 2021
# Description:
#   This file contains the interpreter class which is responsible for interpreting the code


import os
from pyclbr import Function
from Parser.parser import Parser
from Parser.stringsWithArrows import *
from Token.token import Token
import Token.tokenList as tokenList
from Lexer.lexer import Lexer
from Memory.memory import SymbolTable, ModuleNameSpace

import sys
import re
import time
import socket
import json



regex = '[+-]?[0-9]+\.[0-9]+'






immutables = [
    'NoneType',
    'Boolean',
    'Pair',
]



def getsubstr(string, start, end):
        return string[start:end]


def string_strip(text):
    list_text = []
    new_text = ''
    for i in range(len(text)):
        list_text.append(text[i])
    for i in range(len(list_text)):
        if list_text[i] != ' ':
            new_text += list_text[i]
    return new_text


def string_rstrip(text):
    list_text = []
    new_text = ''
    for i in range(len(text)):
        list_text.append(text[i])
    while list_text[-1] == ' ':
        list_text.pop()
    for i in range(len(list_text)):
        new_text += list_text[i]
    return new_text

       
def string_lstrip(text):
    list_text = []
    new_text = ''
    for i in range(len(text)):
        list_text.append(text[i])
    while list_text[0] == ' ':
        list_text.pop(0)
    for i in range(len(list_text)):
        new_text += list_text[i]
    return new_text


def string_rsplit(string, delimiter, maxsplit=-1):
    return string.rsplit(delimiter, maxsplit)
        
        
def string_split(string, delimiter):
    max_split = -1
    return string.split(delimiter, max_split)
        
        
def string_count(string, value, start=0, end=None):
    count = 0
    if end is None:
        end = len(string)
    for i in range(start, end):
        if string[i] == value:
            count += 1
    return count


def string_partition(string, string_to_search):
    index = string.find(string_to_search)
    if index == -1:
        return (string, '', '')
    else:
        return (string[:index], string_to_search, string[index + len(string_to_search):])
    
    
def string_rpartition(string, string_to_search):
    index = string.rfind(string_to_search)
    if index == -1:
        return ('', '', string)
    else:
        return (string[:index], string_to_search, string[index + len(string_to_search):])
    

def is_static(string):
    if len(string) == 0:
        return False
    return string[0] == '@'


def is_varags(string):
    if len(string) == 0:
        return False
    return string[0] == '*'


def is_kwargs(string):
    if len(string) == 0:
        return False
    return string[0] == '**'


def make_varargs(string):
    if is_varags(string):
        return string[1:]


def make_kwargs(string):
    if is_kwargs(string):
        return string[2:]


def vna_algorithm(params, args):
    len_params = len(params)
    len_args = len(args)
    starargs = []
    nonstarargs = []
    for i in range(len_params):
        first_positional_arg = i
        last_positional_arg  = len_params - 1
        if is_varags(params[i]):
            if len_params == 1:
                start_index = params.index(params[i])
                starargs = args[start_index:]
            else:
                # if first_positional_arg is == to 0 then the starargs is the first positional arg
                # and we need to get the args starting from the starargs index and ending at the index of the nonstarargs e.g params = ["*args","a","b","c"] args = [1,2,3,4,5,6,7,8,9,10]
                # starargs = [1,2,3,4,5,6,7] nonstarargs = [8,9,10]
                if first_positional_arg == 0:
                    start_index = params.index(params[i])
                    starargs = args[start_index:len_args - len_params + 1]
                    nonstarargs = args[len_args - len_params + 1:]
                # if last_positional_arg is == to i then the *args is at the last position of the pramater, then we get the args starting from the nonargs and ending at the startargs index e.g params = ["a","b","c","*args"] args = [1,2,3,4,5,6,7,8,9,10]
                # starargs = [4,5,6,7,8,9,10] nonstarargs = [1,2,3]
                elif last_positional_arg == i:
                    start_index = params.index(params[i])
                    starargs = args[start_index:len_args]
                    nonstarargs = args[0:start_index]
                # if the *args is in the middle of the params then we get the args starting from the nonargs and ending at the startargs index e.g params = ["a","b","c","*args","d","e"] args = [1,2,3,4,5,6,7,8,9,10]
                # starargs = [4,5,6,7,8] nonstarargs = [1,2,3,9,10]
                else:
                    start_index = params.index(params[i])
                    first_args = args[0:start_index]
                    non_args_names = params[start_index:len_params]
                    non_args_names = [name for name in non_args_names if is_varags(name) == False]
                    # we reverse the args
                    reversed_args = args[::-1][0:len(non_args_names)]
                    reversed_args_names = non_args_names[::-1]
                    starargs = args[start_index:len_args - len_params + start_index + 1]
                    re_reversed_args = reversed_args[::-1]
                    re_reversed_args_names = reversed_args_names[::-1]
                    nonstarargs = first_args + re_reversed_args

    return starargs, nonstarargs


def create_module_path(module_path):
    new_path = [path for path in module_path]
    # for path in module_path:
    #     if path == '.':
    #         root_path = os.getcwd()
    #         new_path.insert(0, root_path)
    path = '/'.join(module_path)
    path = path+'.ald'
    path_ = ''
    # get last index of the path
    path_ = new_path[-1]
    return path, path_





symbolTable_ = SymbolTable()

module_namespace = ModuleNameSpace()

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
            question_token = Token(
                tokenList.QUESTION, None, pos_start, pos_end)
            pipe_token = Token(tokenList.TT_PIPE, None, pos_start, pos_end)

        def compile(self, pattern):
            self.pattern = re.compile(pattern)
            return self

        def match(self, text):
            return self.pattern.findall(text)


def is_emptyString(value):
    return value == ""


def check_args(expected_len, args_given, message, pos_start, pos_end, context):
    expected_len1 = expected_len
    expected_len2 = None
    if isinstance(expected_len, tuple):
        expected_len1 = expected_len[0]
        expected_len2 = expected_len[1]
    
    if expected_len2 == None:
        if len(args_given) != expected_len1:
            raise Al_ArgumentError({
                'pos_start': pos_start,
                'pos_end': pos_end,
                'message': message,
                'context': context,
                'exit': False
            })
    else:
        if len(args_given) > expected_len2 or len(args_given) < expected_len1:
            raise Al_ArgumentError({
                'pos_start': pos_start,
                'pos_end': pos_end,
                'message': message,
                'context': context,
                'exit': False
            })
    
  
def check_type(expected_type, type_given, message, pos_start, pos_end, context):
    if isinstance(expected_type, list):
        if type_given not in expected_type:
            raise Al_ArgumentError({
                'pos_start': pos_start,
                'pos_end': pos_end,
                'message': message,
                'context': context,
                'exit': False
            })
    else:
        if not isinstance(type_given, expected_type):
            raise Al_TypeError({
                'pos_start': pos_start,
                'pos_end': pos_end,
                'message': message,
                'context': context,
                'exit': False
            })
 
def is_iterable(obj):
    return isinstance(obj, List) or isinstance(obj, Pair) or isinstance(obj, Dict) or isinstance(obj, Object) or isinstance(obj, String) or isinstance(obj, Module)

class TypeOf:
    def __init__(self, type):
        self.type = type

    def getType(self):
        result = ''
        if self.type == 'str':
            result = 'string'
        elif self.type == 'tuple':
            result = 'pair'
        elif isinstance(self.type, Number):
            if isinstance(self.type.value, int):
                result = 'int'
            elif isinstance(self.type.value, float):
                result = 'float'
            elif isinstance(self.type.value, complex):
                result = 'complex'
        else:
            if isinstance(self.type, str) or isinstance(self.type, String):
                result = 'string'
            elif isinstance(self.type, Bytes):
                result = 'bytes'
            elif isinstance(self.type, tuple) or isinstance(self.type, Pair):
                result = 'pair'
            elif isinstance(self.type, Object):
                result = 'object'
            elif isinstance(self.type, Module):
                result = 'module'
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
            elif isinstance(self.type, BuiltInClass):
                result = 'class'
            elif isinstance(self.type, BuiltInMethod):
                result = 'builtin_function_or_method'
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
        value = token
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
        
        def SyntaxError(detail):
            pass
               
        def Exception(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'Exception',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def RuntimeError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'RuntimeError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'ZeroDivisionError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'NameError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def ArgumentError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'ArgumentError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'TypeError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'KeyError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'ValueError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'PropertyError',
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
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'IndexError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
        
        def LookupError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'LookupError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))
        
        def UnicodeDecodeError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'UnicodeDecodeError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def ImportError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'ImportError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def ModuleNotFoundError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'ModuleNotFoundError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def KeyboardInterrupt(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'KeyboardInterrupt',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def RecursionError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'RecursionError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def IOError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'IOError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def OSError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'OSError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def FileNotFoundError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'FileNotFoundError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def PermissionError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'PermissionError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def NotImplementedError(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'NotImplementedError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def SystemExit(detail):
            if 'name' in detail:
                if isinstance(detail['name'], String):
                    detail['name'] = detail['name'].value
            isDetail = {
                'name': detail['name'] if 'name' in detail else 'SystemExit',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            if detail['exit']:
                Program.printErrorExit(Program.asStringTraceBack(isDetail))
            else:
                Program.printError(Program.asStringTraceBack(isDetail))

        def Warning(detail):
            isDetail = {
                'name': 'Warning',
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
            'SyntaxError': SyntaxError,
            'Exception': Exception,
            'RuntimeError': RuntimeError,
            'ZeroDivisionError': ZeroDivisionError,
            'NameError': NameError,
            'ArgumentError': ArgumentError,
            'TypeError': TypeError,
            'KeyError': KeyError,
            'ValueError': ValueError,
            'PropertyError': PropertyError,
            'IndexError': IndexError,
            'LookupError': LookupError,
            'UnicodeDecodeError': UnicodeDecodeError,
            'ImportError': ImportError,
            'ModuleNotFoundError': ModuleNotFoundError,
            'KeyboardInterrupt': KeyboardInterrupt,
            'RecursionError': RecursionError,
            'IOError': IOError,
            'OSError': OSError,
            'FileNotFoundError': FileNotFoundError,
            'PermissionError': PermissionError,
            'NotImplementedError': NotImplementedError,
            'SystemExit': SystemExit,
            'Warning': Warning
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
        pos_start = detail["pos_start"]
        pos_end = detail["pos_end"]
        result = f'\n{detail["name"]}: {detail["message"]}\n'
        result += f'\nFile {pos_start.fileName}, line {pos_start.line + 1}'
        result += '\n\n'+ stringsWithArrows(pos_start.fileText, pos_start, pos_end)
        return result

    def asStringTraceBack(detail):
        result = Program.generateTraceBack(detail)
        pos_start = detail["pos_start"]
        pos_end = detail["pos_end"]
        fileText = pos_start.fileText
        if isinstance(detail["message"], String):
            detail["message"] = detail["message"].value
        result += '' + stringsWithArrows(fileText, pos_start, pos_end) + ''
        result += f'\n{detail["name"]}: {detail["message"]}\n'
        return result

    def generateTraceBack(detail):
        result = ''
        error_count = 0
        pos = detail['pos_start']
        pos_start = detail['pos_start']
        pos_end = detail['pos_end']
        context = detail['context']
        while context:
            error_count += 1
            result = '' + f'   File "{pos.fileName}", (at line:{pos.line + 1}, col:{pos.column + 1}) in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        return 'Traceback (most recent call last):\n' + result

    def runFile(file):
        try:
            with open(file, 'r') as file_handle:
                code = file_handle.read()
                if file[-4:] != ".ald":
                    print(f"File '{file}' is not a valid alden file")
                    return
                else:
                    return code
        except FileNotFoundError:
            return None

    def createBuiltIn(path,name, value):
        res = RuntimeResult()
        lexer = Lexer(path, value)
        tokens, error = lexer.make_tokens()
        new_context = Context('<module>')
        new_context.symbolTable = symbolTable_
        if error: return "", error
        parser = Parser(tokens, name, new_context)
        ast = parser.parse()
        if ast.error: return "", ast.error
        interpreter = Interpreter()
        result = interpreter.visit(ast.node, new_context)
        new_object = {}
        for key, value in new_context.symbolTable.symbols.items():
            if key == name:
                if isinstance(value, Class):
                    new_object['new'] = value
            else:
                new_object[key] = value
        if result.error: return "", result.error
        result_object = Module(name, new_object, 'builtin')
        return result_object

    def createModule(path, module_name, module_from_name, module,properties_list, context, is_builtin,pos_start,pos_end):
        res = RuntimeResult()
        mod_name = module_from_name if module_from_name != None else module_name
        if mod_name == '.':
            mod_name = module_name
        new_context = Context(mod_name, context, pos_start)
        new_context.symbolTable = SymbolTable(context.symbolTable)
        lexer = Lexer(path, module, new_context, None, 'module', module_name)
        mod = None
        tokens, error = lexer.make_tokens()
        if error: return "", error
        parser = Parser(tokens, path, new_context)
        ast = parser.parse()
        interpreter = Interpreter()
        parser_error_detected = parser.error_detected
        if parser_error_detected == True:
            return None
        else:
            result = interpreter.visit(ast.node, new_context)
            if result.error: return "", result.error
            new_object = {}
            module_namespace_properties = {}
            name = None
            value = None

            for key, value in new_context.symbolTable.symbols.items():
                if isinstance(value, dict):
                    new_object[key] = value['value']
                else:
                    new_object[key] = value



            if module_name == '*':
                for key, value in new_object.items():
                    value = value
                    context.symbolTable.set(key, value)
                return value



            if properties_list != None:
                value = None
                if len(properties_list) > 1:
                    for property in properties_list:
                        name = property.value
                        if name in new_object:
                            value = new_object[name]
                            context.symbolTable.set(name, value)
                            for k, v in value.context.symbolTable.symbols.items():
                                if  k != name:
                                    module_namespace_properties[k] = v
                                    module_namespace.set(name, module_namespace_properties)
                        else:
                            return None, name
                    return value

                elif len(properties_list) == 1:
                    name = properties_list[0].value
                    if name in new_object:
                        value = new_object[name]
                        context.symbolTable.set(module_name, value)
                        for k, v in value.context.symbolTable.symbols.items():
                            if  k != name:
                                module_namespace_properties[k] = v
                                module_namespace.set(name, module_namespace_properties)
                        
                    else:
                        return None, name
                    return value

            else:
                module_object = {}
                value_ = None
                for key, value in new_object.items():
                    value_ = value
                if value_ != 'none':
                    for k, v in value_.context.symbolTable.symbols.items():
                        module_namespace_properties[k] = v
                        module_namespace.set(module_name, module_namespace_properties)
                if is_builtin:
                    module_object = Module(module_name, new_object, 'builtin')
                else:
                    module_object = Module(module_name, new_object, 'module')
                value = module_object
                context.symbolTable.set(module_name, module_object)
                return value

        return None, module_name
    
    def makeModule(module_path, module,context,pos_start,pos_end):
        res = RuntimeResult()
        lexer = Lexer(module_path, module, None, 'module')
        tokens, error = lexer.make_tokens()
        if error: return "", error
        new_context = Context('<module>', context, pos_start)
        new_context.symbolTable = SymbolTable(context.symbolTable)
        parser = Parser(tokens, module_path, new_context)
        ast = parser.parse()
        parser_error_detected = parser.error_detected
        interpreter = Interpreter()
        if parser_error_detected == True:
            sys.exit(1)
        else:
            result = interpreter.visit(ast.node, new_context)
            if result.error: return "", result.error
            new_object = {}
            for key, value in new_context.symbolTable.symbols.items():
                if isinstance(value, dict):
                    new_object[key] = value['value']
                else:
                    new_object[key] = value

            module_object = {}
            if module_path in builtin_modules:
                module_object = Module(module_path, new_object, 'builtin')
            else:
                module_object = Module('annonymous', new_object, 'module')
            return module_object
        

builtin_modules = {
    "math": Program.runFile,
    "http": Program.runFile,
    "file": Program.runFile,
    'system': Program.runFile,
    'os': Program.runFile,
    'date': Program.runFile,
    're': Program.runFile,
    'random': Program.runFile,
    'hashlib': Program.runFile,
    'vna': Program.runFile,
}




class RuntimeResult:
    def __init__(self, exception_details=None):
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

    def failure(self, error, value=None):
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


class Al_Exception(Exception):
    def __init__(self, name, message):
        self.name = name
        self.message = message
        properties = {
            'name': String(name),
            'message': String(message)
        }
        self.properties = Dict(properties)

    def __repr__(self):
        return f"<Exception {self.name}: {self.message}>"


class Al_SyntaxError(Exception):
    def __init__(self, message):
        self.name = "SyntaxError"
        self.message = message


class Al_ZeroDivisionError(Al_Exception):
    def __init__(self, message):
        super().__init__("ZeroDivisionError", message)

    def __repr__(self):
        return f"<ZeroDivisionError {self.name}: {self.message}>"


class Al_RuntimeError(Al_Exception):
    def __init__(self, message):
        super().__init__("RuntimeError", message)

    def __repr__(self):
        return f"<RuntimeError {self.message}>"


class Al_NameError(Al_Exception):
    def __init__(self, message):
        super().__init__("NameError", message)

    def __repr__(self):
        return f"<NameError {self.message}>"


class Al_ArgumentError(Al_Exception):
    def __init__(self, message):
        super().__init__("ArgumentError", message)

    def __repr__(self):
        return f"<ArgumentError {self.message}>"


class Al_KeyError(Al_Exception):
    def __init__(self, message):
        super().__init__("KeyError", message)

    def __repr__(self):
        return f"<KeyError {self.message}>"


class Al_TypeError(Al_Exception):
    def __init__(self, message):
        super().__init__("TypeError", message)

    def __repr__(self):
        return f"<TypeError {self.message}>"


class Al_PropertyError(Al_Exception):
    def __init__(self, message):
        super().__init__("PropertyError", message)

    def __repr__(self):
        return f"<PropertyError {self.message}>"


class Al_ValueError(Al_Exception):
    def __init__(self, message):
        super().__init__("ValueError", message)

    def __repr__(self):
        return f"<ValueError {self.message}>"


class Al_IndexError(Al_Exception):
    def __init__(self, message):
        super().__init__("IndexError", message)

    def __repr__(self):
        return f"<IndexError {self.message}>"


class Al_LookupError(Al_Exception):
    def __init__(self, message):
        super().__init__("LookupError", message)
    
    def __repr__(self):
        return f"<LookupError {self.message}>"


class Al_UnicodeDecodeError(Al_Exception):
    def __init__(self, message):
        super().__init__("UnicodeDecodeError", message)
    
    def __repr__(self):
        return f"<UnicodeDecodeError {self.message}>"


class Al_ImportError(Al_Exception):
    def __init__(self, message):
        super().__init__("ImportError", message)

    def __repr__(self):
        return f"<ImportError {self.message}>"


class Al_ModuleNotFoundError(Al_Exception):
    def __init__(self, message):
        super().__init__("ModuleNotFoundError", message)

    def __repr__(self):
        return f"<ModuleNotFoundError {self.message}>"


class Al_KeyboardInterrupt(Al_Exception):
    def __init__(self, message):
        super().__init__("KeyboardInterrupt", message)

    def __repr__(self):
        return f"<KeyboardInterrupt {self.message}>"


class Al_RecursionError(Al_Exception):
    def __init__(self, message):
        super().__init__("RecursionError", message)

    def __repr__(self):
        return f"<RecursionError {self.message}>"


class Al_IOError(Al_Exception):
    def __init__(self, message):
        super().__init__("IOError", message)

    def __repr__(self):
        return f"<IOError {self.message}>"


class Al_OSError(Al_Exception):
    def __init__(self, message):
        super().__init__("OSError", message)

    def __repr__(self):
        return f"<OSError {self.message}>"


class Al_FileNotFoundError(Al_Exception):
    def __init__(self, message):
        super().__init__("FileNotFoundError", message)

    def __repr__(self):
        return f"<FileNotFoundError {self.message}>"


class Al_PermissionError(Al_Exception):
    def __init__(self, message):
        super().__init__("PermissionError", message)

    def __repr__(self):
        return f"<PermissionError {self.message}>"


class Al_NotImplementedError(Al_Exception):
    def __init__(self, message):
        super().__init__("NotImplementedError", message)

    def __repr__(self):
        return f"<NotImplementedError {self.message}>"


class Al_SystemExit(Al_Exception):
    def __init__(self, message):
        super().__init__("SystemExit", message)

    def __repr__(self):
        return f"<SystemExit {self.message}>"


class Al_Warning(Al_Exception):
    def __init__(self, message):
        super().__init__("Warning", message)

    def __repr__(self):
        return f"<Warning {self.message}>"


builtin_exceptions = {
    'Exception': Al_Exception,
    'RuntimeError': Al_RuntimeError,
    'NameError': Al_NameError,
    'ArgumentError': Al_ArgumentError,
    'TypeError': Al_TypeError,
    'IndexError': Al_IndexError,
    'ValueError': Al_ValueError,
    'PropertyError': Al_PropertyError,
    'KeyError': Al_KeyError,
    'ZeroDivisionError': Al_ZeroDivisionError,
    'LookupError': Al_LookupError,
    'UnicodeDecodeError': Al_UnicodeDecodeError,
    'ImportError': Al_ImportError,
    'ModuleNotFoundError': Al_ModuleNotFoundError,
    'KeyboardInterrupt': Al_KeyboardInterrupt,
    'RecursionError': Al_RecursionError,
    'IOError': Al_IOError,
    'OSError': Al_OSError,
    'FileNotFoundError': Al_FileNotFoundError,
    'PermissionError': Al_PermissionError,
    'NotImplementedError': Al_NotImplementedError,
    'SystemExit': Al_SystemExit,
}


def splat_args(a, n):
    new_a = []  # a is a list of arguments
    new_n = []  # n is a list of names


class Value:
    def __init__(self):
        self.setPosition()
        self.setContext()
        self.has_error = False

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

    def floordivided_by(self, other):
        return None, self.illegal_operation_typerror({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'//' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
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
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def or_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None

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

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def execute(self, args, keyword_args_list):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'{TypeOf(self).getType()}' is not callable",
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
            raise Al_TypeError({
                'message': error['message'] if error['message'] else f"Illegal operation on {TypeOf(self).getType()} with {TypeOf(other).getType()}",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit'] if 'exit' in error else True
            })
        else:
            raise Al_TypeError({
                'message': f"Illegal operation",
                'pos_start': error['pos_start'],
                'pos_end': error['pos_end'],
                'context': error['context'],
                'exit': error['exit']
            })

    def key_error(self, error, property):
            raise Al_KeyError({
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
                errorDetail['message'] = f"Illegal operation for type '{TypeOf(self.value).getType()}' and '{TypeOf(other.value).getType()}'"
                raise Al_TypeError(errorDetail)
            else:
                errorDetail['message'] = f"illegal operation"
                raise Al_TypeError(errorDetail)
        raise Al_TypeError(errorDetail)

    def zero_division_error(self, error):
        raise Al_ZeroDivisionError({
            'pos_start': error['pos_start'],
            'pos_end': error['pos_end'],
            'message': error['message'],
            'context': error['context'],
            'exit': error['exit'] if 'exit' in error else False
        })

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
                raise Al_IndexError(errorDetail)
            else:
                errorDetail['message'] = f"illegal operation"
                raise Al_IndexError(errorDetail)
        raise Al_IndexError(errorDetail)


class Statement(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
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
            'pos_start': self.pos_start if self.pos_start else other.pos_start,
            'pos_end': self.pos_end if self.pos_end else other.pos_end,
            'message': f"can't add type '{TypeOf(self.value).getType()}' to type '{TypeOf(other.value).getType()}'",
            'context': self.context if self.context else other.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) + setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.elements) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    value += setNumber(element.value)
            return Number(setNumber(self.value) + value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def increment(self):
        return Number(setNumber(self.value) + 1).setContext(self.context), None

    def decrement(self):
        return Number(setNumber(self.value) - 1).setContext(self.context), None

    def subtracted_by(self, other):
        error = {
            'pos_start': self.pos_start if self.pos_start else other.pos_start,
            'pos_end': self.pos_end if self.pos_end else other.pos_end,
            'message': f"can't subtract type '{TypeOf(self.value).getType()}' from type '{TypeOf(other.value).getType()}'",
            'context': self.context if self.context else other.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.elements) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    value += setNumber(element.value)
            return Number(setNumber(self.value) - value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start if self.pos_start else other.pos_start,
            'pos_end': self.pos_end if self.pos_end else other.pos_end,
            'message': f"can't multiply '{TypeOf(self.value).getType()}' with '{TypeOf(other.value).getType()}'",
            'context': self.context if self.context else other.context,
            'exit': False
        }

        if isinstance(other, Number):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) * setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.value) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    value += setNumber(element.value)
            return Number(setNumber(self.value) * value).setContext(self.context), None

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
            return None, self.zero_division_error(error)
        error = {
            'pos_start': self.pos_start if self.pos_start else other.pos_start,
            'pos_end': self.pos_end if self.pos_end else other.pos_end,
            'message': f"can't divide type '{TypeOf(self.value).getType()}' by type '{TypeOf(other.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.value) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    if element.value == 0:
                        error = {
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"division by zero",
                            'context': self.context,
                            'exit': False
                        }
                        return None, self.zero_division_error(error)
                    value += setNumber(element.value)
            return Number(setNumber(self.value) / value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def floordivided_by(self, other):
        if other.value == 0:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"division by zero",
                'context': self.context,
                'exit': False
            }
            return None, self.zero_division_error(error)
        error = {
            'pos_start': self.pos_start if self.pos_start else other.pos_start,
            'pos_end': self.pos_end if self.pos_end else other.pos_end,
            'message': f"can't divide type '{TypeOf(self.value).getType()}' by type '{TypeOf(other.value).getType()}'",
            'context': self.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) // setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) // setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.value) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    if element.value == 0:
                        error = {
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"division by zero",
                            'context': self.context,
                            'exit': False
                        }
                        return None, self.zero_division_error(error)
                    value += setNumber(element.value)
            return Number(setNumber(self.value) // value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def powred_by(self, other):
        error = {
                    'pos_start': self.pos_start if self.pos_start else other.pos_start,
                    'pos_end': self.pos_end if self.pos_end else other.pos_end,
                    'message': f"can't raise type '{TypeOf(self.value).getType()}' to type '{TypeOf(other.value).getType()}'",
                    'context': self.context if self.context else other.context,
                    'exit': False
                }
        if isinstance(other, Number):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) ** setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.value) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    value += setNumber(element.value)
            return Number(setNumber(self.value) ** value).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def modulo(self, other):
        error = {
                    'pos_start': self.pos_start if self.pos_start else other.pos_start,
                    'pos_end': self.pos_end if self.pos_end else other.pos_end,
                    'message': f"can't perform modulo on type '{TypeOf(self.value).getType()}' and type '{TypeOf(other.value).getType()}'",
                    'context': self.context if self.context else other.context,
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
                return None, self.zero_division_error(error)
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
                return None, self.zero_division_error(error)
            else:
                return Number(setNumber(self.value) % setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Pair):
            value = 0
            if len(other.value) > 1:
                return self.illegal_operation_typerror(error, other), None
            for element in other.elements:
                if not isinstance(element, Number):
                    return None, self.illegal_operation_typerror(error)
                else:
                    if element.value == 0 or setNumber(element.value) == 0:
                        error = {
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"modulo by zero",
                            'context': self.context,
                            'exit': False
                        }
                        return None, self.zero_division_error(error)
                    else:
                        value += setNumber(element.value)
            return Number(setNumber(self.value) % value).setContext(self.context), None
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
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def or_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


number_methods = {
}


class String(Value):
    def __init__(self, value):
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
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start, 
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't perform concatenation on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}" if hasattr(other, 'value') and hasattr(self, 'value') else f"can't perform concatenation on type none",
            'context': self.context if self.context is not None else other.context,
            'exit': False
        }
        if isinstance(other, Number):
            self.has_error = True
            return None, self.illegal_operation_typerror(error, other)
        if isinstance(other, String):
            return String(setNumber(str(self.value)) + setNumber(str(other.value))).setContext(self.context), None
        else:
            self.has_error = True
            return "none", self.illegal_operation_typerror(error, other)

    def multiplied_by(self, other):
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't perform multiplication on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
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
        #print(self, other)
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'in' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        }
        if isinstance(other, String) or isinstance(other, Bytes):
            try:
                return self.setTrueorFalse(other.value in self.value).setContext(self.context), None
            except:
                error['message'] = f"invaid operation on 'in'"
                return None, self.illegal_operation_typerror(error, other)
        elif isinstance(other, List) or isinstance(other, Pair):
            return self.setTrueorFalse(other.value in self.value).setContext(self.context), None
        elif isinstance(other, Boolean):
            if other.value == "true":
                return self.setTrueorFalse(True).setContext(self.context), None
            else:
                return self.setTrueorFalse(False).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_not_in(self, other):
        value = self.get_comparison_in(other)[0].value
        return self.setTrueorFalse(True if value == "false" else False), None

    def get_index(self, other):
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't perform indexing on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
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
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def and_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def or_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None
     
    def upperCase(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("upperCase", self.context)
        if len(kwargs) > 0:
            raise Al_ArgumentError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"upperCase() takes no keyword argument",
                'context': self.context,
                'exit': False
            })
        
        
        check_args(0, args, f"{len(args)} arguments given, but upperCase() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        return String(self.value.upper()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
     
    def lowerCase(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("lowerCase", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"lowerCase() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but lowerCase() takes no argument", self.pos_start, self.pos_end, self.context)
        
        return String(self.value.lower()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def capitalize(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("capitalize", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"capitalize() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(0, args, f"{len(args)} arguments given, but capitalize() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        return String(self.value.capitalize()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def title(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("title", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"title() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but title() takes no argument", self.pos_start, self.pos_end, self.context)
        
        return String(self.value.title()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def zfill(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("zfill", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"zfill() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but zfill() takes 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Number, args[0], f"zfill() argument must be of type Number, but got {TypeOf(args[0]).getType()}", self.pos_start, self.pos_end, self.context)
        
        return String(self.value.zfill(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def swapcase(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("swapcase", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"swapcase() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but swapcase() takes no argument", self.pos_start, self.pos_end, self.context)
        
        return String(self.value.swapcase()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                
    def ascii_code(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("ascii_code", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"ascii_code() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })

        check_args(0, args, f"{len(args)} arguments given, but ascii_code() takes no argument", self.pos_start, self.pos_end, self.context)
        
        return Number(ord(self.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def partition(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("partition", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"partition() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(1, args, f"{len(args)} arguments given, but partition() takes 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(String, args[0], f"partition() argument must be of type String, but got {TypeOf(args[0]).getType()}", self.pos_start, self.pos_end, self.context)
        
        if args[0].value == '':
            raise Al_ValueError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': "no empty separator",
                'context': self.context,
                'exit': False
            })
        values = string_partition(self.value, args[0].value)
        pair_result = ()
        for value in values:
            pair_result += (String(value).setContext(self.context).setPosition(self.pos_start, self.pos_end),)
        return Pair(pair_result).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def rpartition(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("rpartition", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"rpartition() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(1, args, f"{len(args)} arguments given, but rpartition() takes 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(String, args[0], f"rpartition() argument must be of type String, but got {TypeOf(args[0]).getType()}", self.pos_start, self.pos_end, self.context)
        
        if args[0].value == '':
            raise Al_ValueError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': "no empty separator",
                'context': self.context,
                'exit': False
            })
            
        values = string_rpartition(self.value, args[0].value)
        pair_result = ()
        for value in values:
            pair_result += (String(value).setContext(self.context).setPosition(self.pos_start, self.pos_end),)
        return Pair(pair_result).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def strip(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("strip", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"strip() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) != 0:
            raise Al_ArgumentError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but strip() takes no argument",
                "context": self.context,
                'exit': False
            })
        else:
            return String(string_strip(self.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def rstrip(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("rstrip", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"rstrip() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but rstrip() takes no argument", self.pos_start, self.pos_end, self.context)
        return String(string_rstrip(self.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
      
    def lstrip(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("lstrip", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"lstrip() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but lstrip() takes no argument", self.pos_start, self.pos_end, self.context)
        
        return String(string_lstrip(self.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def split(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("split", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"split() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 0:
            value = []
            split_list = self.value.split()
            for i in split_list:
                value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 1:
            if isinstance(args[0], String):
                if args[0].value == " ":
                    value = []
                    split_list = self.value.split()
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                    return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                elif args[0].value == "":
                    value = []
                    split_list = self.value.split()
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                    return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                else:
                    value = []
                    split_list = self.value.split(args[0].value)
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                    return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for split()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], String) and isinstance(args[1], Number):
                if args[1].value < 0:
                    raise Al_RuntimeError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"{args[1].value} is not a valid argument for split()",
                        "context": self.context,
                        'exit': False
                    })
                else:
                    value = []
                    split_list = self.value.split(args[0].value, args[1].value)
                    for i in split_list:
                        value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                    return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not a valid arguments for split()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but split() takes 1 or 2 arguments",
                "context": self.context,
                'exit': False
            })

    def rsplit(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("rsplit", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"rsplit() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but rsplit() takes at least 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(String, args[0], f"argument 1 of type '{TypeOf(args[0]).getType()}' is not a valid argument for rsplit()", self.pos_start, self.pos_end, self.context)
        
            
        if len(args) == 2:
            check_type(Number, args[1], f"argument 2 of type '{TypeOf(args[1]).getType()}' is not a valid argument for rsplit()", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 1:
            value = []
            split_list = string_rsplit(self.value, args[0].value)
            for i in split_list:
                value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
        elif len(args) == 2:
            value = []
            split_list = string_rsplit(self.value, args[0].value, args[1].value)
            for i in split_list:
                value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            
    def splitlines(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("splitlines", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"splitlines() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args((0,1), args, f"{len(args)} arguments given, but splitlines() takes 0 or 1 argument", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 0:
            value = []
            split_list = self.value.splitlines(False)
            for i in split_list:
                value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 1:
            check_type(Boolean, args[0], f"argument 1 of type '{TypeOf(args[0]).getType()}' is not a valid argument for splitlines()", self.pos_start, self.pos_end, self.context)
            
            if args[0].value == 'true':
                # keep line breaks
                value = []
                split_list = str(self.value).splitlines(True)
                for i in split_list:
                    value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                value = []
                split_list = self.value.splitlines(False)
                for i in split_list:
                    value.append(String(i).setContext(self.context).setPosition(self.pos_start, self.pos_end))
                return List(value).setContext(self.context).setPosition(self.pos_start, self.pos_end)
         
    def join(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("join", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"join() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], List):
                try:
                    return String(self.value.join([x.value for x in args[0].elements])).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                except:
                    raise Al_TypeError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    })
            elif isinstance(args[0], Pair):
                try:
                    return String(self.value.join([x.value for x in args[0].elements])).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                except:
                    raise Al_TypeError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    })
            elif isinstance(args[0], Object) or isinstance(args[0], Module):
                try:
                    return String(self.value.join([x for x in args[0].get_keys()])).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                except:
                    raise Al_TypeError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"expected sequence of strings, but got {TypeOf(args[0]).getType()}",
                        "context": self.context,
                        'exit': False
                    })
            elif isinstance(args[0], String):
                return String(self.value.join(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for join()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_ArgumentError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but join() takes 1 argument",
                "context": self.context,
                'exit': False
            })

    def replace(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("replace", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"replace() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 2:
            if isinstance(args[0], String) and isinstance(args[1], String):
                return String(self.value.replace(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not a valid arguments for replace()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 3:
            if isinstance(args[0], String) and isinstance(args[1], String) and isinstance(args[2], Number):
                return String(self.value.replace(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}', '{TypeOf(args[1]).getType()}' and '{TypeOf(args[2]).getType()}' are not a valid arguments for replace()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but replace() takes 2 arguments",
                "context": self.context,
                'exit': False
            })

    def length(self, args, kwargs, var_name=None):
        if args == None:
            return Number(len(self.value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'length' is not callable",
                "context": self.context,
                'exit': False
            })

    def substr(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("substr", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"substr() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], Number):
                start = args[0].value
                end = len(self.value)
                return String(getsubstr(self.value, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for substr()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], Number) and isinstance(args[1], Number):
                start = args[0].value
                end = args[1].value + 1
                return String(getsubstr(self.value, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not a valid arguments for substr()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but substr() takes 2 arguments",
                "context": self.context,
                'exit': False
            })

    def slice(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("slice", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"slice() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], Number):
                start = args[0].value
                end = len(self.value)
                return String(getsubstr(self.value, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for slice()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], Number) and isinstance(args[1], Number):
                start = args[0].value
                end = args[1].value + 1
                return String(getsubstr(self.value, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not a valid arguments for slice()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but slice() takes 2 arguments",
                "context": self.context,
                'exit': False
            })

    def charAt(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("charAt", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"charAt() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 0:
            string = self.value.replace(" ", "")
            start = 0
            end = 1
            return String(getsubstr(string, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        if len(args) == 1:
            if isinstance(args[0], Number):
                string = self.value.replace(" ", "")
                start = args[0].value
                end = start + 1
                return String(getsubstr(string, start, end)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for charAt()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but charAt() takes 1 argument",
                "context": self.context,
                'exit': False
            })

    def includes(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("includes", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"includes() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], String):
                string = self.value.replace(" ", "")
                substring = args[0].value.replace(" ", "")
                return Boolean(string.find(substring) != -1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_RuntimeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for includes()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but includes() takes 1 argument",
                "context": self.context,
                'exit': False
            })

    def count(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("count", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"count() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], String):
                return Number(self.value.count(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for count()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], String) and isinstance(args[1], Number):
                return Number(self.value.count(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not a valid arguments for count()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 3:
            if isinstance(args[0], String) and isinstance(args[1], Number) and isinstance(args[2], Number):
                return Number(self.value.count(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' and '{TypeOf(args[2]).getType()}' are not a valid arguments for count()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but count() takes 1 argument and 2 optional arguments",
                "context": self.context,
                'exit': False
            })

    def startsWith(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("startsWith", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"startsWith() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], String):
                string = self.value.replace(" ", "")
                substring = args[0].value.replace(" ", "")
                return Boolean(string.startswith(substring)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for startsWith()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], String) and isinstance(args[1], Number):
                string = self.value.replace(" ", "")
                substring = args[0].value.replace(" ", "")
                start = args[1].value
                end = start + 1
                return Boolean(getsubstr(string, start, end).startswith(substring)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not valid arguments for startsWith()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but startsWith() takes 1 or 2 arguments",
                "context": self.context,
                'exit': False
            })

    def endsWith(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("endsWith", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"endsWith() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        if len(args) == 1:
            if isinstance(args[0], String):
                string = self.value.replace(" ", "")
                substring = args[0].value.replace(" ", "")
                return Boolean(string.endswith(substring)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' is not a valid argument for endsWith()",
                    "context": self.context,
                    'exit': False
                })
        elif len(args) == 2:
            if isinstance(args[0], String) and isinstance(args[1], Number):
                string = self.value.replace(" ", "")
                substring = args[0].value.replace(" ", "")
                start = args[1].value
                end = start + 1
                return Boolean(getsubstr(string, start, end).endswith(substring)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not valid arguments for endsWith()",
                    "context": self.context,
                    'exit': False
                })
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(args)} arguments given, but endsWith() takes 1 or 2 arguments",
                "context": self.context,
                'exit': False
            })

    def find(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("find", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"find() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,3), args, f"{len(args)} arguments given, but find() takes 1, 2 or 3 arguments", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 1:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 2:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            
        elif len(args) == 3:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[2], f"type '{TypeOf(args[2]).getType()}' is not a valid argument for find()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def rfind(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("rfind", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"rfind() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,3), args, f"{len(args)} arguments given, but rfind() takes 1, 2 or 3 arguments", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 1:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rfind(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 2:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rfind(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
           
        elif len(args) == 3:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[2], f"type '{TypeOf(args[2]).getType()}' is not a valid argument for rfind()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rfind(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def findIndex(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("findIndex", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"findIndex() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,3), args, f"{len(args)} arguments given, but findIndex() takes 1, 2 or 3 arguments", self.pos_start, self.pos_end, self.context)
        
        
        if len(args) == 1:
            check_type(String, args[0],f"type '{TypeOf(args[0]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 2:
            check_type(String, args[0],f"type '{TypeOf(args[0]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1],f"type '{TypeOf(args[1]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 3:
            check_type(String, args[0],f"type '{TypeOf(args[0]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1],f"type '{TypeOf(args[1]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[2],f"type '{TypeOf(args[2]).getType()}' is not a valid argument for findIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.find(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def rfindIndex(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("rfindIndex", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"rfindIndex() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,3), args, f"{len(args)} arguments given, but rfindIndex() takes 1, 2 or 3 arguments", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 1:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rindex(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 2:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rindex(args[0].value, args[1].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                
        elif len(args) == 3:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"type '{TypeOf(args[1]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[2], f"type '{TypeOf(args[2]).getType()}' is not a valid argument for rfindIndex()", self.pos_start, self.pos_end, self.context)
            return Number(self.value.rindex(args[0].value, args[1].value, args[2].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_upperCase(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_uppercase", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_upperCase() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_upper() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isupper()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_lowerCase(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_lowercase", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_lowerCase() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_lower() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.islower()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_alpha(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_alpha", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_alpha() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_alpha() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isalpha()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_digit(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_digit", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_digit() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_digit() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isdigit()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def is_decimal(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_decimal", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_decimal() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_decimal() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isdecimal()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_numeric(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_numeric", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_numeric() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_numeric() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isnumeric()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_alnum(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_alnum", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_alnum() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_alnum() takes no argument",self.pos_start, self.pos_end, self.context)
    
        return Boolean(self.value.isalnum()).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def is_ascii(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_ascii", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_ascii() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_ascii() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isascii()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
          
    def is_space(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_space", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_space() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(0, args, f"{len(args)} arguments given, but is_space() takes no argument",self.pos_start, self.pos_end, self.context)
        
        
        return Boolean(self.value.isspace()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def is_title(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_title", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_title() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_title() takes no argument",self.pos_start, self.pos_end, self.context)
        
        
        return Boolean(self.value.istitle()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
     
    def is_identifier(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_identifier", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_identifier() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_identifier() takes no argument",self.pos_start, self.pos_end, self.context)
        
        return Boolean(self.value.isidentifier()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
      
    def is_printable(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_printable", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_printable() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_printable() takes no argument",self.pos_start, self.pos_end, self.context)
        
        
        return Boolean(self.value.isprintable()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
     
    def is_empty(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_empty", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_empty() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(0, args, f"{len(args)} arguments given, but is_empty() takes no argument",self.pos_start, self.pos_end, self.context)
        
        
        return Boolean(self.value == '').setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def format(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("format", self.context)
        res = RuntimeResult()
        interpreter = Interpreter()
        new_args = []
        string = self.value
        keywords = {}
        kwargs_names = []
        keys_replace = []
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                value = res.register(interpreter.visit(key['value'], self.context))
                keywords[name] = value
                kwargs_names.append(name)
            for name, value in keywords.items():
                string_replace = f"{'{' + str(name) + '}'}"
                string_key_match = re.findall(r'{(.*?)}', string)
                key_not_valid_names = [name for name in string_key_match if name not in kwargs_names]
                for key_not_valid_name in key_not_valid_names:
                    raise Al_KeyError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"'{key_not_valid_name}'",
                        "context": self.context,
                        'exit': False
                    })
                if not string_replace in string:
                    raise Al_KeyError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"'{name}'",
                        "context": self.context,
                        'exit': False
                    })
                string = string.replace('{' + str(name) + '}', str(value.value))
                        
             

        else:
            if len(args) == 0:
                raise Al_ArgumentError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"{len(args)} arguments given, but format() takes 1 or more arguments",
                    "context": self.context,
                    'exit': False
                })
            if isinstance(args[0], List) or isinstance(args[0], Pair):
                for arg in args[0].elements:
                    new_args.append(arg)
            
                
            for arg in args:
                new_args.append(arg)
            for i in range(len(new_args)):
                keys_replace.append(i)
            for i in range(len(new_args)):
                keys_empty = []
                is_keys_empty = False
                new_keys = []
                string_key_match = re.findall(r'{(.*?)}', string)
                for key_not_valid_name in string_key_match:
                    try:
                       key_not_valid_name = int(key_not_valid_name)
                       key_not_valid_name * 1
                    except Exception as e:
                        if key_not_valid_name == '':
                            raise Al_KeyError({
                                'pos_start': self.pos_start,
                                'pos_end': self.pos_end,
                                'message': f"cannot use empty string in place of an index",
                                'context': self.context,
                                'exit': False
                            })
                            # is_keys_empty = True
                            # keys_empty.append(i)  
                        raise Al_KeyError({
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"'{key_not_valid_name}'",
                            'context': self.context,
                            'exit': False
                        })
               
                
                keys = re.findall(r'{(.*?)}', string)
                # if is_keys_empty:
                #     for i in range(len(keys)):
                #         if i not in keys_empty:
                #             new_keys.append(i)
                #     keys = new_keys
                    # change the emty braces to contain the numbers in keys
                
                
                if len(keys) != len(new_args):
                    for key in keys:
                        k = int(key)
                        if k not in keys_replace:
                            raise Al_IndexError({
                                "pos_start": self.pos_start,
                                "pos_end": self.pos_end,
                                'message': f"replacement index '{k}' is out of range",
                                "context": self.context,
                                'exit': False
                            })
                            
                
                string = string.replace('{' + str(i) + '}', str(new_args[i].value))
        
        return String(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
           
    def format_dict(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("format_dict", self.context)
        string = self.value
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                raise Al_KeyError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"format_dict() got an unexpected keyword argument '{name}'",
                    'context': self.context,
                    'exit': False
                })
                
        check_type(Dict, args[0], f"format_dict() argument 1 must be dict, not {TypeOf(args[0]).getType()}", self.pos_start, self.pos_end, self.context)
       
        if isinstance(args[0], Dict):
            for name, value in args[0].properties.items():
                string_replace = f"{'{' + str(name) + '}'}"
                string_key_match = re.findall(r'{(.*?)}', string)
                key_not_valid_names = [name for name in string_key_match if name not in args[0].properties]
                for key_not_valid_name in key_not_valid_names:
                    if key_not_valid_name == '':
                        raise Al_ValueError({
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"format string contains positional fields",
                            'context': self.context,
                            'exit': False
                        })
                    raise Al_KeyError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"'{key_not_valid_name}'",
                        "context": self.context,
                        'exit': False
                    })
                string = string.replace('{' + str(name) + '}', str(value.value))
        else:
            raise Al_TypeError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"format_dict() argument 1 must be dict, not {TypeOf(args[0]).getType()}",
                'context': self.context,
                'exit': False
            })
        return String(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                
    def encode(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("encode", self.context)
        res = RuntimeResult()
        interpreter = Interpreter()
        keywords = {}
        valid_kwargs = ['encoding', 'errors']
        encoding_index = 0
        errors_index = 1
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if not name in valid_kwargs:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"encode() got an unexpected keyword argument '{name}'",
                        'context': self.context,
                        'exit': False
                    })
                value = res.register(interpreter.visit(key['value'], self.context))
                if not isinstance(value, String):
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"encode() argument {name} must be of type string, not {TypeOf(value).getType()}",
                        'context': self.context,
                        'exit': False
                    })
                keywords[name] = value
        if len(args) == 1:
            if len(keywords) == 1:
                args.insert(errors_index, keywords['errors'])
        elif len(args) == 0:
            if len(keywords) == 1:
                if not 'encoding' in keywords:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"too few arguments for encode()",
                        'context': self.context,
                        'exit': False
                    })
                args.insert(encoding_index, keywords['encoding'])
            elif len(keywords) == 2:
                args.insert(encoding_index, keywords['encoding'])
                args.insert(errors_index, keywords['errors'])

        
        string = ''
        check_args((0, 2), args, f"{len(args)} arguments given, but encode() takes 0, 1 or 2 arguments",
                   self.pos_start, self.pos_end, self.context)
        
        
        errors = [ 'strict', 'backsplashreplace', 'errors', 'ignore', 'namereplace','replace','xmlcharrefreplace' ]
        
        encodings = ['ascii','utf8','utf-8','utf-16','utf']
                     
                     
                     
                     
        if len(args) == 0:
            encoding = 'utf-8'
            error = 'strict'
            try:
                string = self.value.encode(encoding, error)
                return Bytes(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except:
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
        elif len(args) == 1:
            encoding = args[0].value
            error = 'strict'
            if encoding not in encodings:
                raise Al_LookupError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"unknown encoding: '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
            try:
                string = self.value.encode(encoding, error)
                return Bytes(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except:
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
        elif len(args) == 2:
            encoding = args[0].value
            error = args[1].value
            if encoding not in encodings:
                raise Al_LookupError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"unknown encoding: '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
            if error not in errors:
                error = 'strict'
            try:
                string = self.value.encode(encoding, error)
                return Bytes(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except Exception as e:
                print(e)
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
                                                 
    def copy(self):
        copy = String(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def is_true(self):
        return self.value != ''
    
    def __methods__(self, args, kwargs, var_name=None):
        if args == None:
            keys = [String(key) for key, value in string_methods.items() if key != '__@methods__']
            return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })
             
    def __str__(self):
        return f"'{self.value}'"

    def __repr__(self):
        return f"'{self.value}'"


class DocString(String):
    def __init__(self, value):
        super().__init__(value)
        self.type = 'docstring'
    
    def __str__(self):
        return f"{self.value}"

string_methods = {
    'upperCase': String.upperCase, # DONE
    'lowerCase': String.lowerCase, # DONE
    'capitalize': String.capitalize, # DONE
    'split': String.split, # DONE
    'rsplit': String.rsplit, # DONE
    'join': String.join, # DONE
    'substr': String.substr, # DONE
    'replace': String.replace, # DONE
    'slice': String.slice, # DONE
    'strip': String.strip, # DONE
    'lstrip': String.lstrip, # DONE
    'rstrip': String.rstrip, # DONE
    'length': String.length, # DONE
    'charAt': String.charAt, # DONE
    'includes': String.includes, # DONE
    'startsWith': String.startsWith, # DONE
    'find': String.find, # DONE
    'rfind': String.rfind, # DONE
    'findIndex': String.findIndex, # DONE
    'rfindIndex': String.rfindIndex, # DONE
    'count': String.count, # DONE
    'format': String.format, # DONE
    'format_dict': String.format_dict, # DONE
    'is_empty': String.is_empty, # DONE
    'is_digit': String.is_digit, # DONE
    'is_decimal': String.is_decimal, # DONE
    'is_alpha': String.is_alpha, # DONE
    'is_numeric': String.is_numeric, # DONE
    'is_alnum': String.is_alnum, # DONE
    'is_ascii': String.is_ascii, # DONE
    'is_lowerCase': String.is_lowerCase, # DONE
    'is_upperCase': String.is_upperCase, # DONE
    'is_title': String.is_title, # DONE
    'is_space': String.is_space, # DONE
    'is_printable': String.is_printable, # DONE
    'is_identifier': String.is_identifier, # DONE
    'startsWith': String.startsWith, # DONE
    'endsWith': String.endsWith, # DONE
    'title': String.title, # DONE
    'zfill': String.zfill, # DONE
    'ascii_code': String.ascii_code, # DONE
    'swapcase': String.swapcase, # DONE
    'splitlines': String.splitlines, # DONE
    'partition': String.partition, # DONE
    'rpartition': String.rpartition, # DONE
    'encode': String.encode, # DONE 
    '__@methods__': String.__methods__ # DONE
}

class Bytes(Value):
    def __init__(self, value):
        self.value = bytes(str(value), 'utf-8') if isinstance(value, str) else value
        self.representation = 'bt' + f"'{str(self.value.decode('utf-8'))}'"
        super().__init__()
        
    def get_comparison_eq(self, other):
        return self.setTrueorFalse(setNumber(self.value) == setNumber(other.value)).setContext(self.context), None

    def get_comparison_ne(self, other):
        return self.setTrueorFalse(setNumber(self.value) != setNumber(other.value)).setContext(self.context), None
     
    def get_comparison_in(self, other):
        error = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"'in' not supported between type '{TypeOf(self).getType()}' and '{TypeOf(other).getType()}'",
            'context': self.context
        }
        if isinstance(other, String) or isinstance(other, Bytes):
            try:
                return self.setTrueorFalse(other.value in self.value).setContext(self.context), None
            except:
                error['message'] = f"invaid operation on 'in'"
                return None, self.illegal_operation_typerror(error, other)
        elif isinstance(other, List) or isinstance(other, Pair):
            return self.setTrueorFalse(other.value in self.value).setContext(self.context), None
        elif isinstance(other, Boolean):
            if other.value == "true":
                return self.setTrueorFalse(True).setContext(self.context), None
            else:
                return self.setTrueorFalse(False).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error, other)

    def get_comparison_not_in(self, other):
        value = self.get_comparison_in(other)[0].value
        return self.setTrueorFalse(True if value == "false" else False), None
      
    def decode(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("decode", self.context)
        res = RuntimeResult()
        interpreter = Interpreter()
        keywords = {}
        valid_kwargs = ['encoding', 'errors']
        encoding_index = 0
        errors_index = 1
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if not name in valid_kwargs:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"decode() got an unexpected keyword argument '{name}'",
                        'context': self.context,
                        'exit': False
                    })
                value = res.register(interpreter.visit(key['value'], self.context))
                if not isinstance(value, String):
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"encode() argument {name} must be of type string, not {TypeOf(value).getType()}",
                        'context': self.context,
                        'exit': False
                    })
                keywords[name] = value
        if len(args) == 1:
            if len(keywords) == 1:
                args.insert(errors_index, keywords['errors'])
        elif len(args) == 0:
            if len(keywords) == 1:
                if not 'encoding' in keywords:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"too few arguments for encode()",
                        'context': self.context,
                        'exit': False
                    })
                args.insert(encoding_index, keywords['encoding'])
            elif len(keywords) == 2:
                args.insert(encoding_index, keywords['encoding'])
                args.insert(errors_index, keywords['errors'])

        
        string = ''
        check_args((0, 2), args, f"{len(args)} arguments given, but decode() takes 0, 1 or 2 arguments",
                   self.pos_start, self.pos_end, self.context)
        
        
        errors = [ 'strict', 'backsplashreplace', 'errors', 'ignore', 'namereplace','replace','xmlcharrefreplace' ]
        
        encodings = ['ascii','utf8','utf-8','utf-16','utf']
                     
                     
                     
                     
        if len(args) == 0:
            encoding = 'utf-8'
            error = 'strict'
            try:
                string = self.value.decode(encoding, error)
                return String(str(string)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except:
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
        elif len(args) == 1:
            encoding = args[0].value
            error = 'strict'
            if encoding not in encodings:
                raise Al_LookupError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"unknown encoding: '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
            try:
                string = self.value.encode(encoding, error)
                return String(str(string)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except:
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
        elif len(args) == 2:
            encoding = args[0].value
            error = args[1].value
            if encoding not in encodings:
                raise Al_LookupError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"unknown encoding: '{encoding}'",
                    'context': self.context,
                    'exit': False
                })
            if error not in errors:
                error = 'strict'
            try:
                string = self.value.decode(encoding, error)
                return String(str(string)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            except:
                raise Al_UnicodeDecodeError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"invalid encoding '{encoding}'",
                    'context': self.context,
                    'exit': False
                })  
          
    def copy(self):
        copy = Bytes(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
        
    def __str__(self):
        return self.representation

    def __repr__(self):
        return self.representation

bytes_methods = {
    'decode': Bytes.decode, # DONE
}

class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
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

    def added_to(self, other):
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't add {TypeOf(self.value).getType()} to {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
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
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't perform multiplication on {TypeOf(self).getType()} of type {TypeOf(other.value).getType()}",
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
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't subtract {TypeOf(self).getType()} from {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) - setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)

    def divided_by(self, other):
        if other.value == 0:
            error = {
                    'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
                    'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
                    'message': f"zero division error",
                    'context': self.context if self.context is not None else other.context,
                    'exit': False
                }
            return None, self.zero_division_error(error)
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't divide {TypeOf(self).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
            'exit': False
        }
        if isinstance(other, Boolean):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Number):
            return Number(setNumber(self.value) / setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation(error, other)

    def floordivided_by(self, other):
        if other.value == 0:
            error = {
                'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
                'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
                'message': f"division by zero",
                'context': self.context if self.context is not None else other.context,
                'exit': False
            }
            return None, self.zero_division_error(error)
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't divide {TypeOf(self.value).getType()} by {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
            'exit': False
        }
        if isinstance(other, Number):
            return Number(setNumber(self.value) // setNumber(other.value)).setContext(self.context), None
        elif isinstance(other, Boolean):
            return Number(setNumber(self.value) // setNumber(other.value)).setContext(self.context), None
        else:
            return None, self.illegal_operation_typerror(error)

    def modulo_by(self, other):
        if other.value == 0:
            error = {
                'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
                'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
                'message': f"modulo by zero",
                'context': self.context if self.context is not None else other.context,
                'exit': False
            }
            return None, self.zero_division_error(error)
        error = {
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end, 
            'message': f"can't perform modulo on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
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
            'pos_start': self.pos_start if self.pos_start is not None else other.pos_start,
            'pos_end': self.pos_end if self.pos_end is not None else other.pos_end,
            'message': f"can't perform powred on {TypeOf(self.value).getType()} of type {TypeOf(other.value).getType()}",
            'context': self.context if self.context is not None else other.context,
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
        return self.setTrueorFalse(setNumber(self.value) and setNumber(other.value)).setContext(self.context), None

    def or_by(self, other):
        return self.setTrueorFalse(setNumber(self.value) or setNumber(other.value)).setContext(self.context), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def is_true(self):
        return True if self.value == "true" else False

    def copy(self):
            copy = Boolean(self.value)
            copy.setPosition(self.pos_start, self.pos_end)
            copy.setContext(self.context)
            return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'


class NoneType(Value):
    def __init__(self, value=None):
        super().__init__()
        self.value = value
        if self.value == None or self.value == "none":
            self.value = "none"
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

    def get_comparison_eq(self, other):
        return self.setTrueorFalse(other.value == "none"), None

    def get_comparison_ne(self, other):
        return self.setTrueorFalse(other.value != "none"), None

    def and_by(self, other):
        return self.setTrueorFalse(other.value == "none"), None

    def or_by(self, other):
        return self.setTrueorFalse(other.value != "none"), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def is_true(self):
        return self.value == "true" if self.value else "false"

    def copy(self):
        copy = NoneType(self.value)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'{self.value}'



Boolean.true = Boolean("true")
Boolean.false = Boolean("false")
NoneType.none = NoneType("none")

def sort_list_pair(elements, key=None, reverse=False):
    new_elements = []
    sorted_elements = []
    len_elements = len(elements)
    element_types = {
        'String': String,
        'Number': Number,
        'Boolean': Boolean
    }
    elements_type_at_index = {}
    
    for element in elements:
        if isinstance(element, Boolean):
            if element.value == "true":
                new_elements.append(int(1))
            else:
                new_elements.append(int(0))
        else:
            new_elements.append(element.value)
    
    # for i in range(len_elements):
    #     for j in range(len_elements -1):
    #         try:
    #             if new_elements[j] > new_elements[j + 1]:
    #                 temp = new_elements[j]
    #                 new_elements[j] = new_elements[j + 1]
    #                 new_elements[j + 1] = temp
    #                 # we need to convert each element to its type

    #         except:
    #             pass  
        sorted_elements = sorted(new_elements, key=key, reverse=reverse)
    for i in range(len_elements):
       elements_type_at_index[i] = type(elements[i]).__name__
    for i in range(len_elements):
        if elements_type_at_index[i] == 'String':
            sorted_elements[i] = element_types['String'](sorted_elements[i])
        elif elements_type_at_index[i] == 'Number':
            sorted_elements[i] = element_types['Number'](sorted_elements[i])
        elif elements_type_at_index[i] == 'Boolean':
            sorted_elements[i] = element_types['Boolean'](sorted_elements[i])
        
    
    return sorted_elements


def sort_dict(properties, keys, key=None, reverse=False):
    new_props = {}
    sorted_props = {}
    len_keys = len(keys)
    props_type_at_index = {}
    for i in range(len_keys):
        new_props[keys[i]] = properties[keys[i]]
    
    sorted_props_keys = sorted(new_props, key=key, reverse=reverse)
    for i in range(len(sorted_props_keys)):
        sorted_props[sorted_props_keys[i]] = new_props[sorted_props_keys[i]]
        
    
    return sorted_props
    
    
def sort_string(string, key=None, reverse=False):
    return sorted(string, key=key, reverse=reverse)
    


class List(Value):
    
    def __init__(self, elements, properties=None):
        super().__init__()
        self.elements = elements
        self.value = self.elements
        self.type = type
        self.id = self.elements
        self.properties = properties if properties else {}
        self.list_methods = ['length', 'push', 'pop', 'get', 'set', 'remove', 'insert', 'clear', 'contains', 'index_of', 'join', 'reverse', 'sort']

    def added_to(self, other):
        if isinstance(other, List):
            return List(self.elements + other.elements), None
        elif isinstance(other, String):
            new_list = []
            for char in other.value:
                new_list.append(String(char).setContext(
                    self.context).setPosition(self.pos_start, self.pos_end))
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

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None
   
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

    def is_true(self):
        return len(self.elements) > 0
    
    def length(self, args, kwargs, var_name=None):
        if args == None:
            return Number(len(self.elements))
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'length' is not callable",
                "context": self.context,
                'exit': False
            })

    def append(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("append", self.context)
        
        
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"append() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but append() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        
       
       
        
        self.elements.append(args[0])
        values = self.elements
        value = List(values).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return value
        
    def pop(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("pop", self.context)
        
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"pop() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((0,1), args, f"{len(args)} arguments given, but pop() takes 0 or 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        if len(args) == 0:
             return List(self.elements.pop()).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif len(args) == 1:
            check_type(Number, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for pop()", self.pos_start, self.pos_end, self.context)
            
            return List(self.elements.pop(args[0].value)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def extend(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("extend", self.context)
        pass
            
    def remove(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("remove", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"remove() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        
        
        check_args(1, args, f"{len(args)} arguments given, but remove() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type((Number, String), args[0], f"argument 1 for remove() must be of type int or string, not {TypeOf(args[0]).getType()}", self.pos_start, self.pos_end, self.context)
        
        new_list = []
        
        
        def is_supported_type(elements):
            for element in elements:
                if not isinstance(element, String) and not isinstance(element, Number) and not isinstance(element, Boolean):
                    return False
            return True
        
        if is_supported_type(self.elements):
            value_to_remove = args[0].value
            for element in self.elements:
                if element.value != value_to_remove:
                    new_list.append(element)
        else:
            for i in range(len(self.elements)):
                for j in range(len(self.elements)):
                    if type(self.elements[i]).__name__ != type(self.elements[j]).__name__:
                        raise Al_TypeError({
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"'>' not supported between instances of '{TypeOf(self.elements[j]).getType()}' and '{TypeOf(self.elements[i]).getType()}'",
                            'context': self.context,
                            'exit': False
                        })
        
        return List(new_list).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def insert(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("insert", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"insert() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(2, args, f"{len(args)} arguments given, but insert() takes exactly 2 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Number, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for insert()", self.pos_start, self.pos_end, self.context)
        
        return List(self.elements.insert(args[0].value, args[1])).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def reverse(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("reverse", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"reverse() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but reverse() takes 0 argument", self.pos_start, self.pos_end, self.context)
        
        new_list = []
        for el in self.elements:
            new_list.insert(0, el)
            
        value = List(new_list).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        self.context.symbolTable.set(var_name, value)
        
        return value

    def empty(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("empty", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"empty() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but empty() takes 0 argument", self.pos_start, self.pos_end, self.context)
        
        value = List([]).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return value

    def getItem(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("getItem", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"getItem() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but getItem() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Number, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for getItem()", self.pos_start, self.pos_end, self.context)
        
        return List(self.elements[args[0].value]).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def setItem(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("setItem", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"setItem() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(2, args, f"{len(args)} arguments given, but setItem() takes exactly 2 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Number, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for setItem()", self.pos_start, self.pos_end, self.context)
        
        old_value = self.elements[args[0].value]
        new_value = args[1]
        self.elements[args[0].value] = new_value
        return List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)

    def join(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("join", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"join() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((0,1), args, f"{len(args)} arguments given, but join() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 1:
            check_type(String, args[0], f"type '{TypeOf(args[0]).getType()}' is not a valid argument for join()", self.pos_start, self.pos_end, self.context)
            
            new_string = ""
            for element in self.elements:
                if type(element.value) == str:
                    new_string += element.value
                else:
                    new_string += str(element.value)
                if element != self.elements[-1]:
                    new_string += args[0].value
            return String(new_string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
           

        elif len(args) == 0:
            new_string = ""
            for element in self.elements:
                if type(element.value) == str:
                    new_string += element.value
                else:
                    new_string += str(element.value)
                if element != self.elements[-1]:
                    new_string += ","
            return String(new_string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def includes(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("includes", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"includes() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but includes() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        new_list = []
        for element in self.elements:
            if hasattr(element, "value"):
                new_list.append(element.value)
            elif hasattr(element, "elements"):
                new_list.append(element.elements)
            elif hasattr(element, "name"):
                new_list.append(element.name)
            elif hasattr(element, "properties"):
                new_list.append(element.properties)
            elif hasattr(element, "properties"):
                new_list.append(element)
            else:
                new_list.append(element)

        if isinstance(args[0], String) or isinstance(args[0], Number):
            if args[0].value in new_list:
                return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], BuiltInFunction):
            if args[0].name in new_list:
                return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], Dict):
            isSame = False
            for element in new_list:
                if isinstance(element, Dict):
                    isSame = element.isSame(args[0])

            return Boolean(isSame).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def count(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("count", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"count() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but count() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        count = 0
        if isinstance(args[0], String) or isinstance(args[0], Number):
            for element in self.elements:
                if element.value == args[0].value:
                    count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], BuiltInFunction):
            for element in self.elements:
                if element.name == args[0].name:
                    count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Module) or isinstance(args[0], Class) or isinstance(args[0], List) or isinstance(args[0], Pair):
            for element in self.elements:
                if isinstance(element, Dict):
                    if element.isSame(args[0]):
                        count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
      
    def indexOf(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("indexOf", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"indexOf() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
                    
        check_args(1, args, f"{len(args)} arguments given, but indexOf() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        if isinstance(args[0], String) or isinstance(args[0], Number):
            for index, element in enumerate(self.elements):
                if isinstance(element, String) or isinstance(element, Number):
                    if element.value == args[0].value:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], BuiltInFunction) or isinstance(args[0], BuiltInClass):
            for index, element in enumerate(self.elements):
                if isinstance(element, BuiltInFunction) or isinstance(element, BuiltInClass):
                    if element.name == args[0].name:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Class) or isinstance(args[0], List) or isinstance(args[0], Pair) or isinstance(args[0], Module):
            for index, element in enumerate(self.elements):
                if isinstance(element, Dict) or isinstance(element, Object) or isinstance(element, Class) or isinstance(element, List) or isinstance(element, Pair) or isinstance(element, Module):
                    if element.isSame(args[0]):
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
         
    def is_empty(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_empty", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_empty() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_empty() takes exactly 0 argument", self.pos_start, self.pos_end, self.context)
        
       
        return Boolean(len(self.elements) == 0).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def is_number(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_number", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_number() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_number() takes exactly 0 argument", self.pos_start, self.pos_end, self.context)
        
        not_numbers = []
        
        for element in self.elements:
            if  not isinstance(element, Number):
                not_numbers.append(element)
        if len(not_numbers) == 0:
            return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
       
    def is_string(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("is_string", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"is_string() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but is_string() takes exactly 0 argument", self.pos_start, self.pos_end, self.context)
       
        not_strings = [] 
        for element in self.elements:
            if not isinstance(element, String):
                not_strings.append(element)
        if len(not_strings) == 0:
            return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
       
    def map(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("map", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"map() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
       
       
        check_args(1, args, f"{len(args)} arguments given, but map() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        check_type(Function, args[0],f"map() takes a function as an argument", self.pos_start, self.pos_end, self.context)
        
        res = RuntimeResult()
        
        func = args[0]
        new_list = []
        
        check_args((1,3), func.arg_names, f"{len(func.arg_names)} arguments given, but map function accepts no more than 3 arguments", self.pos_start, self.pos_end, self.context)
        
        if len(func.arg_names) == 1:
            for element in self.elements:
                new_list.append(res.register(func.execute([element], kwargs)))
                if res.should_return(): return res
                
        elif len(func.arg_names) == 2:
            index = 0
            for i in range(len(self.elements)):
                index = Number(i).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                new_list.append(res.register(func.execute([self.elements[i], index], kwargs)))
                if res.should_return(): return res
            
                
        elif len(func.arg_names) == 3:
            index = 0
            elements = List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            for i in range(len(self.elements)):
                index = Number(i).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                new_list.append(res.register(func.execute([self.elements[i], index, elements], kwargs)))
                if res.should_return(): return res
                
                
                
        return List(new_list).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def filter(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("filter", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"filter() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but filter() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Function, args[0],f"filter() takes a function as an argument", self.pos_start, self.pos_end, self.context)

        res = RuntimeResult()
        
        func = args[0]
        new_list = []
        
        check_args((1,3), func.arg_names, f"{len(func.arg_names)} arguments given, but filter function takes no more than 3 arguments", self.pos_start, self.pos_end, self.context)
        
        
        if len(func.arg_names) == 1:
            for element in self.elements:
                new_res = res.register(func.execute([element], kwargs))
                if res.should_return(): return res
                if isinstance(new_res, Boolean):
                    if new_res.value == "true":
                        new_list.append(element)
                        
        elif len(func.arg_names) == 2:
            index = 0
            for i in range(len(self.elements)):
                element = self.elements[i]
                index = Number(i).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                new_res = res.register(func.execute([self.elements[i], index], kwargs))
                if res.should_return(): return res
                if isinstance(new_res, Boolean):
                    if new_res.value == "true":
                        new_list.append(element)
                    
                    
        elif len(func.arg_names) == 3:
            index = 0
            elements = List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            for i in range(len(self.elements)):
                element = self.elements[i]
                index = Number(i).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                new_res = res.register(func.execute([self.elements[i], index, elements], kwargs))
                if res.should_return(): return res
                if isinstance(new_res, Boolean):
                    if new_res.value == "true":
                        new_list.append(element)
                    
                        
                        
        return List(new_list).setContext(self.context).setPosition(self.pos_start, self.pos_end)
     
    def sort(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("sort", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"sort() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but sort() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        if len(self.elements) == 0:
            return List([]).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
        if len(args) == 0:
            new_elements = []
            def is_all_strings(elements):
                for element in elements:
                    if not isinstance(element, String):
                        return False
                return True
            def is_all_numbers(elements):
                for element in elements:
                    if not isinstance(element, Number):
                        return False
                return True
            def is_all_booleans(elements):
                for element in elements:
                    if not isinstance(element, Boolean):
                        return False
                return True
                    
            
            if is_all_strings(self.elements):
                sorted_elements = sort_list_pair(self.elements)
                value = List(sorted_elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return value
            elif is_all_numbers(self.elements):
                sorted_elements = sort_list_pair(self.elements)
                value = List(sorted_elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return value
            elif is_all_booleans(self.elements):
                sorted_elements = sort_list_pair(self.elements)
                value = List(sorted_elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return value
            else:
                for i in range(len(self.elements)):
                    for j in range(len(self.elements)):
                        if type(self.elements[i]).__name__ != type(self.elements[j]).__name__:
                            raise Al_TypeError({
                                'pos_start': self.pos_start,
                                'pos_end': self.pos_end,
                                'message': f"'>' not supported between instances of '{TypeOf(self.elements[j]).getType()}' and '{TypeOf(self.elements[i]).getType()}'",
                                'context': self.context,
                                'exit': False
                            })
                        
        # if len(args) == 1:
        #     check_type(Function, args[0],f"sort() takes a function as an argument", self.pos_start, self.pos_end, self.context)
            
        #     res = RuntimeResult()

        #     compare_func = args[0]
        #     compare_value = None
        #     check_args(2, compare_func.arg_names, f"{len(compare_func.arg_names)} arguments given, but sort function accepts exactly 2 arguments", self.pos_start, self.pos_end, self.context)
            
            
            
        #     new_elements = []
            
        #     try:
        #         # sort based on the return value of the compare function
        #         for i in range(len(self.elements)):
        #             for j in range(len(self.elements)):
        #                 compare_value = res.register(compare_func.execute([self.elements[i], self.elements[j]], kwargs))
        #                 if res.error: return res
        #                 if res.should_return(): return res
        #         print(compare_value)
        #     except Al_TypeError as e:
        #         raise e
                    
        #     return List(new_elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)

                      
    def find(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("find", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"find() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but find() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Function, args[0],f"find() takes a function as an argument", self.pos_start, self.pos_end, self.context)
        
        
        check_args((1,3), args, f"{len(args)} arguments given, but find() takes 1 to 3 arguments", self.pos_start, self.pos_end, self.context)
        
        
        res = RuntimeResult()
        
        func = args[0]
        if len(func.arg_names) == 1:
            for element in self.elements:
                new_res = res.register(func.execute([element], kwargs))
                if res.should_return(): return res
                if isinstance(new_res, Boolean):
                    if new_res.value == "true":
                        return element
            return NoneType.none
        else:
            if len(func.arg_names) == 2:
                for i in range(len(self.elements)):
                    index = Number(i).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                    new_res = res.register(func.execute([self.elements[i], index], kwargs))
                    if isinstance(new_res, Boolean):
                        if new_res.value == "true":
                            return self.elements[i]
            elif len(func.arg_names) == 3:
                index = 0
                elements = List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                for i in range(len(self.elements)):
                    new_res = res.register(func.execute(
                        [self.elements[i], index, elements], kwargs))
                    if isinstance(new_res, Boolean):
                        if new_res.value == "true":
                            return self.elements[i]
    
    def findIndex(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("findIndex", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"findIndex() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but findIndex() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Function, args[0],f"findIndex() takes a function as an argument", self.pos_start, self.pos_end, self.context)
        
        res = RuntimeResult()
        
        func = args[0]
        if len(func.arg_names) == 1:
            for i in range(len(self.elements)):
                new_res = res.register(func.execute([self.elements[i]], kwargs))
                if res.should_return(): return res
                if isinstance(new_res, Boolean):
                    if new_res.value == "true":
                        return Number(i)
            return NoneType.none
        else:
            if len(func.arg_names) == 2:
                for i in range(len(self.elements)):
                    new_res = res.register(func.execute([self.elements[i], Number(i)], self.keyword_args))
                    if isinstance(new_res, Boolean):
                        if new_res.value == "true":
                            return Number(i)
            elif len(func.arg_names) == 3:
                for i in range(len(self.elements)):
                    new_res = res.register(func.execute([self.elements[i], Number(i), self.name], self.keyword_args))
                    if isinstance(new_res, Boolean):
                        if new_res.value == "true":
                            return Number(i)
                 
    def removeAt(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("removeAt", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"removeAt() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but removeAt() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Number, args[0],f"removeAt() takes a number as an argument", self.pos_start, self.pos_end, self.context)
        
        index = args[0].value
        check_type(int, index, f"expected an integer, but got (type '{TypeOf(index).getType()}')", self.pos_start, self.pos_end, self.context)
        if index <= len(self.elements):
            self.elements.pop(index)
            return List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_IndexError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"position at index '{index}' is out of range",
                'context': self.context,
                'exit': False
            })
        
    def slice(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("slice", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"slice() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but slice() takes exactly 2 arguments", self.pos_start, self.pos_end, self.context)
        
        if len(args) == 2:
            check_type(Number, args[0], f"argument 1 of slice() must be a number", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"argument 2 of slice() must be a number", self.pos_start, self.pos_end, self.context)
            
            return List(self.elements[args[0].value:args[1].value]).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
        elif len(args) == 1:
            check_type(Number, args[0], f"argument 1 of slice() must be a number", self.pos_start, self.pos_end, self.context)
            
            return List(self.elements[args[0].value:]).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            
    def splice(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("splice", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"splice() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but splice() takes exactly 2 arguments", self.pos_start, self.pos_end, self.context)
        if len(args) == 2:
            check_type(Number, args[0], f"argument 1 of splice() must be a number", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"argument 2 of splice() must be a number", self.pos_start, self.pos_end, self.context)
            index = args[0].value
            deleteCount = args[1].value
            if index <= len(self.elements) :
                if deleteCount > 0:
                    element_index = self.elements[index:index+deleteCount]
                    new_list = self.elements[:index] + self.elements[index+deleteCount:]
                    self.elements = new_list
                    value = List(new_list).setContext(self.context).setPosition(
                        self.pos_start, self.pos_end)
                    self.context.symbolTable.set(var_name, value)
                    return value
           
        elif len(args) == 1:
            check_type(Number, args[0], f"argument 1 of splice() must be a number", self.pos_start, self.pos_end, self.context)
            
            return List(self.elements[:args[0].value]).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                     
    def reduce(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("reduce", self.context)
        
        
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"reduce() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args((1,2), args, f"{len(args)} arguments given, but reduce() takes exactly 2 arguments", self.pos_start, self.pos_end, self.context)
        
        check_type(Function, args[0], f"argument 1 of reduce() must be a function", self.pos_start, self.pos_end, self.context)
        
        
        res = RuntimeResult()
        
        if len(self.elements) == 0:
            raise Al_ValueError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"reduce() of empty list with no initial value",
                'context': self.context,
                'exit': False
            })
        func = args[0]
        if len(args) == 1:
            check_args((2,4), func.arg_names, f"reduce() expects no more than 4 arguments", self.pos_start, self.pos_end, self.context)
            total = self.elements[0]
            if len(func.arg_names) == 2:
                for element in self.elements[1:]:
                    current_value = element
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value], kwargs))
                    if res.should_return(): return res
            elif len(func.arg_names) == 3:
                for element in self.elements[1:]:
                    current_value = element
                    current_index = Number(self.elements.index(element))
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value, current_index], kwargs))
                    if res.should_return(): return res
            elif len(func.arg_names) == 4:
                for element in self.elements[1:]:
                    current_value = element
                    current_index = Number(self.elements.index(element))
                    return_list = List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value, current_index, return_list], kwargs))
                    if res.should_return(): return res

            return total
        elif len(args) == 2:
            check_args((2,4), func.arg_names, f"reduce() expects no more than 4 arguments", self.pos_start, self.pos_end, self.context)
            check_type(Number, args[1], f"argument 2 of reduce() must be a number", self.pos_start, self.pos_end, self.context)
            total = args[1]
            if len(func.arg_names) == 2:
                for element in self.elements:
                    current_value = element
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value], kwargs))
                    if res.should_return(): return res
            elif len(func.arg_names) == 3:
                for index, element in enumerate(self.elements):
                    current_value = element
                    current_index = Number(index)
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value, current_index], kwargs))
                    if res.should_return(): return res
            elif len(func.arg_names) == 4:
                for index, element in enumerate(self.elements):
                    current_value = element
                    current_index = Number(index)
                    return_list = List(self.elements).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                    # update the total as the result of the function
                    total = res.register(func.execute([total, current_value, current_index, return_list], kwargs))
                    if res.should_return(): return res
            return total
    
    def some(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("some", self.context)
        raise Al_NotImplementedError({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"some() is not implemented",
            'context': self.context,
            'exit': False
        })
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"some() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
                    
        check_args(1, args, f"{len(args)} arguments given, but some() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type(Function, args[0], f"argument 1 of some() must be a function", self.pos_start, self.pos_end, self.context)
        
        res = RuntimeResult()
        
        func = args[0]
        if len(func.arg_names) == 1:
            for element in self.elements:
                new_res = res.register(func.execute([element], kwargs))
                if res.should_return(): return res
                print(new_res)

    def every(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("every", self.context)
        raise Al_NotImplementedError({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"some() is not implemented",
            'context': self.context,
            'exit': False
        })
     
    def each(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("each", self.context)
        raise Al_NotImplementedError({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"some() is not implemented",
            'context': self.context,
            'exit': False
        })
              
    def copy(self):
        copy = List(self.elements, self.properties)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy
        
    def __methods__(self, args, kwargs, var_name=None):
        if args == None:
            keys = [String(key) for key, value in list_methods.items() if key != '__@methods__']
            return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })
                  
    def __string__(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("__@str__", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"__@str__() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(0, args, f"{len(args)} arguments given, but __@str__() takes exactly 0 argument", self.pos_start, self.pos_end, self.context)
        
        string = ""
        
        for element in self.elements:
            string += str(element) + ", "
        string = string[:-2]
        return String(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            
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

list_methods = {
    'length': List.length,
    'append': List.append,
    'pop': List.pop,
    'extend': List.extend,
    'remove': List.remove,
    'insert': List.insert,
    'empty': List.empty,
    'is_empty': List.is_empty,
    'reverse': List.reverse,
    'getItem': List.getItem,
    'setItem': List.setItem,
    'slice': List.slice,
    #'splice': List.splice,
    'removeAt': List.removeAt,
    'join': List.join,
    'sort': List.sort,
    'includes': List.includes,
    'count': List.count,
    'indexOf': List.indexOf,
    'findIndex': List.findIndex,
    'map': List.map,
    'filter': List.filter,
    'find': List.find,
    'reduce': List.reduce,
    'some': List.some,
    'every': List.every,
    'each': List.each,
    'is_number': List.is_number,
    'is_string': List.is_string,
    '__@str__': List.__string__,
    '__@methods__': List.__methods__,
}


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

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

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

    def count(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("count", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"count() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but count() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        count = 0
        if isinstance(args[0], String) or isinstance(args[0], Number):
            for element in self.elements:
                if element.value == args[0].value:
                    count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], BuiltInFunction):
            for element in self.elements:
                if element.name == args[0].name:
                    count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Module) or isinstance(args[0], Class) or isinstance(args[0], List) or isinstance(args[0], Pair):
            for element in self.elements:
                if isinstance(element, Dict):
                    if element.isSame(args[0]):
                        count += 1
            return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def length(self, args, kwargs, var_name=None):
        if args == None:
            return Number(len(self.elements)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'length' is not callable",
                "context": self.context,
                'exit': False
            })
    
    def indexOf(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("indexOf", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"indexOf() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
                    
        check_args(1, args, f"{len(args)} arguments given, but indexOf() takes exactly 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        if isinstance(args[0], String) or isinstance(args[0], Number):
            for index, element in enumerate(self.elements):
                if isinstance(element, String) or isinstance(element, Number):
                    if element.value == args[0].value:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], BuiltInFunction) or isinstance(args[0], BuiltInClass):
            for index, element in enumerate(self.elements):
                if isinstance(element, BuiltInFunction) or isinstance(element, BuiltInClass):
                    if element.name == args[0].name:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Class) or isinstance(args[0], List) or isinstance(args[0], Pair) or isinstance(args[0], Module):
            for index, element in enumerate(self.elements):
                if isinstance(element, Dict) or isinstance(element, Object) or isinstance(element, Class) or isinstance(element, List) or isinstance(element, Pair) or isinstance(element, Module):
                    if element.isSame(args[0]):
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
             
    def is_true(self):
        return len(self.elements) > 0

    def copy(self):
        copy = Pair(self.elements)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __methods__(self, args, kwargs, var_name=None):
        if args == None:
            keys = [String(key) for key, value in list_methods.items() if key != '__@methods__']
            return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })

    def __string__(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("__@str__", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"__@str__() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })

        check_args(0, args, f"{len(args)} arguments given, but __@str__() takes exactly 0 argument",
                   self.pos_start, self.pos_end, self.context)

        string = ""

        for element in self.elements:
            string += str(element) + ", "
        string = string[:-2]
        return String(string).setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def __str__(self):
        try:
            return f'({", ".join([str(x) for x in self.elements])})'
        except:
            return "()"


pair_methods = {
    'length': Pair.length,
    'count': Pair.count,
    'indexOf': Pair.indexOf,
    '__@str__': Pair.__string__,
    '__@methods__': Pair.__methods__,
}

class Dict(Value):
    def __init__(self, properties, keys=None, values=None, context=None):
        super().__init__()
        self.properties = properties
        self.value = self.properties
        self.context = context

    def get_length(self):
        return len(self.properties)

    def get_property(self, key):
        pass

    def get_key(self, key):
        if key.value in self.properties:
            return self.properties[key.value]
        else:
            error = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"Key '{key}' not found in dict",
                'context': self.context,
                'exit': False
            }
        return None, self.key_error(error, key)

    def get_keys(self):
        keys = []
        for key in self.properties:
            keys.append(key)
        return keys

    def get_values(self):
        values = []
        for value in self.properties.values():
            values.append(value)
        return values

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
            for key, value in other.properties.items():
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

    def has_property(self, property_name):
        return property_name in self.properties

    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None

    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def is_true(self):
        return len(self.properties) > 0
  
    def length(self,args,kwargs,var_name=None):
        if args == None:
            return Number(len(self.properties)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'length' is not callable",
                "context": self.context,
                'exit': False
            })

    def hasProp(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("hasProp", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"hasProp() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but hasProp() takes 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        check_type((String,Number), args[0], f"hasProp() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
        
        
        for key, value in self.properties.items():
            if key == args[0].value:
                return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def keys(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("keys", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"keys() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but keys() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        
        keys = []
        for key in self.properties.keys():
            keys.append(String(key))
        return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def values(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("values", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"values() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but values() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        values = []
        for value in self.properties.values():
            values.append(value)
        return List(values).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def items(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("items", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"items() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but items() takes no argument", self.pos_start, self.pos_end, self.context)
        

        items = []
        
        for key, value in self.properties.items():
            if isinstance(key, str):
                key = String(key)
            elif isinstance(key, int):
                key = Number(key)
            items.append(Pair([key, value]))
        return List(items).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                          
    def get(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("get", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"get() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but get() expects at least 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type((String,Number), args[0], f"get() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
        
        
        if len(args) == 2:
            key = args[0].value
            default = args[1]
            if key in self.properties:
                return self.properties[key]
            else:
                return default
            
        
        key = args[0].value
        default = NoneType()
        if key in self.properties:
            return self.properties[key]
        else:
            return default
             
    def set(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("set", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"set() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but set() expects 2 arguments", self.pos_start, self.pos_end, self.context)
        
        
        
        
        if len(args) == 1:
            check_type((Dict,Object), args[0], f"set() argument 1 must be of type dict or object, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
            
            for key, value in args[0].properties.items():
                self.properties[key] = value
                    
                
            
        
        
        if len(args) == 2:
            check_type(
                (String, Number), args[0], f"set() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
            name = args[0]
            value = args[1]
            
            if isinstance(name, String):
                if name.value in self.properties:
                    self.properties[name.value] = value
                else:
                    self.properties[String(name.value)] = value
                
            elif isinstance(name, Number):
                if name.value in self.properties:
                    self.properties[name.value] = value
                else:
                    self.properties[Number(name.value)] = value
            
        return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def update(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("update", self.context)
        res = RuntimeResult()
        interpreter = Interpreter()
        
        
        check_args((0,2), args, f"{len(args)} arguments given, but update() expects 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        
        if len(args) == 2:
            check_type((String,Number), args[0], f"update() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
            name = args[0]
            value = args[1]
            if isinstance(name, String):
                if name.value in self.properties:
                    self.properties[name.value] = value
                else:
                    raise Al_KeyError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"cannot update non-existing key: '{name.value}'",
                        'context': self.context,
                        'exit': False
                    })
            
            elif isinstance(name, Number):
                if name.value in self.properties:
                    self.properties[name.value] = value
                else:
                   raise Al_KeyError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"cannot update non-existing key: '{name.value}'",
                        'context': self.context,
                        'exit': False
                    })
             
            
        if len(args) == 1:
            if len(kwargs) != 0:
                for key in kwargs:
                    name = key['name']
                raise Al_ArgumentError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"update() requires no keyword argument, when using a {TypeOf(args[0]).getType()} as argument",
                    'context': self.context,
                    'exit': False
                })
            check_type((Dict,Object), args[0], f"update() argument 1 must be of type dict or object, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
            
            for key, value in args[0].properties.items():
                if key in self.properties:
                    self.properties[key] = value
                else:
                    raise Al_KeyError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"cannot update non-existing key: '{key}'",
                        'context': self.context,
                        'exit': False
                    })        
            
            
        if len(args) == 0:
            if len(kwargs) == 0:
                raise Al_ArgumentError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"update() takes at least 1 keyword argument",
                    'context': self.context,
                    'exit': False
                })
            else:
                keywords = {}
                name = None
                value = None
                for key in kwargs:
                    name = key['name']
                    value = res.register(interpreter.visit(key['value'], self.context))
                    if name in self.properties:
                        self.properties[name] = value
                    else:
                        raise Al_KeyError({
                            'pos_start': self.pos_start,
                            'pos_end': self.pos_end,
                            'message': f"cannot update non-existing key: '{name.value}'",
                            'context': self.context,
                            'exit': False
                        })
        
        return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
    
    def delete(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("delete", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"delete() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but delete() expects 1 argument",
                   self.pos_start, self.pos_end, self.context)
        
        
        check_type((String,Number), args[0], f"delete() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
        
        
        
        if args[0].value in self.properties:
            del self.properties[args[0].value]
        
        
        return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
                
    def clear(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("clear", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"clear() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        
        check_args(0, args, f"{len(args)} arguments given, but clear() expects 0 arguments", self.pos_start, self.pos_end, self.context)
        
        
        self.properties = {}
        
        return Dict(self.properties).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            
    def pretty(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("pretty", self.context)
        pass   
    
    def __methods__(self,args,kwargs,var_name=None):
        if args == None:
            keys = [String(key) for key, value in dict_methods.items() if key != '__@methods__']
            return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })
               
    def copy(self):
        copy = Dict(self.properties)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        try:
            return f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items() if not k.startswith('__')])}}}"
        except:
            return f'{self.properties}'

dict_methods = {
    'length': Dict.length,
    'hasProp': Dict.hasProp,
    'keys': Dict.keys,
    'values': Dict.values,
    'items': Dict.items,
    'get': Dict.get,
    'set': Dict.set,
    'update': Dict.update,
    'delete': Dict.delete,
    'clear': Dict.clear,
    'pretty': Dict.pretty,
    '__@methods__': Dict.__methods__,
}



class Object(Value):

    def __init__(self, name, properties):
        super().__init__()
        self.id = name
        self.name = name
        self.properties = properties
        self.value = self.properties
        self.get_property = self.get_property
        self.representation = f"<object {self.name}>"

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
            keys.append(key)
        return keys

    def get_values(self):
        values = []
        for value in self.properties:
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

    def has_property(self, property_name):
        return property_name in self.properties

    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None

    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

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
            for key, value in other.properties.items():
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

    def length(self,args,kwargs,var_name=None):
        if args == None:
            return Number(len(self.properties)).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'length' is not callable",
                "context": self.context,
                'exit': False
            })

    def hasProp(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("hasProp", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"hasProp() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(1, args, f"{len(args)} arguments given, but hasProp() takes 1 argument", self.pos_start, self.pos_end, self.context)
        
        
        check_type((String,Number), args[0], f"hasProp() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
        
        
        for key, value in self.properties.items():
            if key == args[0].value:
                return Boolean(True).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        return Boolean(False).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def keys(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("keys", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"keys() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but keys() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        
        keys = []
        for key in self.properties.keys():
            keys.append(String(key))
        return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def values(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("values", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"values() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but values() takes no argument", self.pos_start, self.pos_end, self.context)
        
        
        values = []
        for value in self.properties.values():
            values.append(value)
        return List(values).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        
    def items(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("items", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"items() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args(0, args, f"{len(args)} arguments given, but items() takes no argument", self.pos_start, self.pos_end, self.context)
        

        items = []
        
        for key, value in self.properties.items():
            items.append(Pair([String(key), value]))
        return List(items).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                          
    def get(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("get", self.context)
        if len(kwargs) > 0:
            for key in kwargs:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"get() takes no keyword argument",
                        'context': self.context,
                        'exit': False
                    })
        check_args((1,2), args, f"{len(args)} arguments given, but get() expects at least 1 argument", self.pos_start, self.pos_end, self.context)
        
        check_type((String,Number), args[0], f"get() argument 1 must be of type string or number, not '{TypeOf(args[0]).getType()}'", self.pos_start, self.pos_end, self.context)
        
        
        if len(args) == 2:
            key = args[0].value
            default = args[1]
            if key in self.properties:
                return self.properties[key]
            else:
                return default
            
        
        key = args[0].value
        default = NoneType()
        if key in self.properties:
            return self.properties[key]
        else:
            return default
                        
    def pretty(self,args,kwargs,var_name=None):
        if args == None:
            return BuiltInFunction("pretty", self.context)
        pass   
       
    def __methods__(self,args,kwargs,var_name=None):
        if args == None:
            if args == None:
                keys = [String(key) for key, value in object_methods.items() if key != '__@methods__']
                return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })
        
    def is_true(self):
        return len(self.properties) > 0

    def copy(self):
        copy = Object(self.name, self.properties)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

    def __repr__(self):
        return self.representation

object_methods = {
    'length': Object.length,
    'hasProp': Object.hasProp,
    'keys': Object.keys,
    'values': Object.values,
    'items': Object.items,
    'get': Object.get,
    'pretty': Object.pretty,
    '__@properties__': Object.__methods__,
}

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name if name != None and name != "none" else "<anonymous>"

    def generate_new_context(self,context=None):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbolTable = SymbolTable(new_context.parent.symbolTable)
        return new_context

    def make_missing_args(self, missing_args, len_args):
        missing_args_name = ''
        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f"but {len_args} {'was' if len_args == 1 or len_args == 0 else 'were'} given"

        return missing_args_name

    def check_args(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        default_values = {}
        len_args = len(args)
        if len_args == 0:
            len_args = "none"
        was_or_were = "was" if len_args == 1 or len_args == 0 or len_args == "none" else "were"
        len_expected = len(self.arg_names)
        new_args_names = self.arg_names
        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value
                len_expected = len(self.arg_names) - len(default_values)

        missing_args = []
        missing_args_name = ": "
        keys = []

        for key, value in default_values.items():
            keys.append(key)

        for i in range(len(self.arg_names)):
            if self.arg_names[i] not in keys:
                missing_args.append(self.arg_names[i])

        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f"but {len_args} {'was' if len(args) == 1 or len(args) == 0 else 'were'} given"

        exception_details = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given",
            'context': self.context,
            'exit': False
        }

        if default_values == {} or default_values == None:
            has_var_args = False
            if len(args) > len(self.arg_names):
                len_arg_names = len(self.arg_names)
                len_args = len(args)
                for i in range(len(self.arg_names)):
                    if is_varags(self.arg_names[i]):
                        has_var_args = True
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"

                    raise Al_ArgumentError(exception_details)

            if len(args) < len(self.arg_names):
                has_var_args = False
                for i in range(len(args)):
                    if is_varags(self.arg_names[i]):
                        has_var_args = True
                        new_args_names.pop(i)
                        missing_args_name = self.make_missing_args(
                            new_args_names, len_args)
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() missing {len(new_args_names)} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"

                    raise Al_ArgumentError(exception_details)

        else:
            if len(args) > len_expected:
                if len(args) > len_expected and len(self.arg_names) == 0:
                    exception_details['message'] = f"{self.name}() takes 0 positional arguments but {len_args} {was_or_were} given"
                    raise Al_ArgumentError(exception_details)

                if len(missing_args) == 0:
                    if len(args) > len(self.arg_names):
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"
                        raise Al_ArgumentError(exception_details)
                    else:
                        return res.success(None)
                else:
                    if len(args) > len(self.arg_names):
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() expected {len_expected} positional arguments"
                        raise Al_ArgumentError(exception_details)

            if len(args) < len_expected:
                has_var_args = False
                if len(args) == 0:
                    for name in self.arg_names:
                        if is_varags(name):
                            has_var_args = True
                            new_args_names.pop(i)
                            return res.success(None)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"
                    raise Al_ArgumentError(exception_details)

        return res.success(None)

    def populate_args(self, keyword_args, args, exec_context):
        res = RuntimeResult()
        interpreter = Interpreter()
        default_values = {}
        len_expected = len(self.arg_names)
        has_var_args = False
        new_args_names = self.arg_names
        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value
                len_expected = len(self.arg_names) - len(default_values)

        len_args = len(args)
        len_arg_names = len(self.arg_names)
        if len_args == 0:
            len_args = "none"
        was_or_were = "was" if len_args == 1 or len_args == 0 or len_args == "none" else "were"
        len_expected = len(self.arg_names)

        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value
                len_expected = len(self.arg_names) - len(default_values)

        missing_args = []
        missing_args_name = ""
        keys = []

        for key, value in default_values.items():
            keys.append(key)

        for i in range(len(self.arg_names)):
            if self.arg_names[i] not in keys:
                missing_args.append(self.arg_names[i])

        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f"but {len_args} {'was' if len(args) == 1 or len(args) == 0 else 'were'} given"

        if len(keyword_args) > 0:
            if len(keyword_args) > len(args):
                if len(args) > 1:
                    args.pop(0)
            elif len(keyword_args) == len(args):
                args = []
            else:
                new_args = []
                args_index_default = len(args) - len(keyword_args)
                if args_index_default - len(keyword_args) == 1:
                    # remove duplicate in args
                    for i in range(len(args)):
                        if i == 0:
                            new_args.append(args[i])
                        else:
                            if args[i] != args[i-1]:
                                new_args.append(args[i])

                if len(args) > len(keyword_args):
                    args_index_default = len(args) - len(keyword_args)
                    args_index = args_index_default - 1
                    for key, value in keyword_args.items():
                          # get position of key in keyword_args
                          key_pos = self.arg_names.index(key)
                           # check if key pos exists in args
                           # print(args_index_default, key_pos, "kk")
                           # if key_pos in range(len(args) - 1)  and key_pos != args_index_default:
                           #         raise Al_ValueError({
                           #             'pos_start': self.pos_start,
                           #             'pos_end': self.pos_end,
                           #             'message': f"{self.name if self.name != 'none' else 'anonymous'}() got multiple values for argument '{key}'",
                           #             'context': self.context,
                           #             'exit': False
                           #         })
                           # key_index = self.arg_names.index(key)
                           # new_arg_index = self.arg_names.index(key)
                           # print(key_pos,key_index, args_index,new_arg_index,args, key)
                           # if key_index == args_index:
                           #     raise Al_ValueError({
                           #         'pos_start': self.pos_start,
                           #         'pos_end': self.pos_end,
                           #         'message': f"{self.name if self.name != 'none' else 'anonymous'}() got multiple values for argument '{key}'",
                           #         'context': self.context,
                           #         'exit': False
                           #     })
                        # except:
                        #     raise Al_ValueError({
                        #         'pos_start': self.pos_start,
                        #         'pos_end': self.pos_end,
                        #         'message':  f"{self.name if self.name != 'none' else 'anonymous' }() got an unexpected keyword argument '{key}'",
                        #         'context': self.context,
                        #         'exit': False
                        #     })
                    # raise Al_ValueError({
                    #     'pos_start': self.pos_start,
                    #     'pos_end': self.pos_end,
                    #     'message': f"{self.name if self.name != 'none' else 'anonymous'}() got multiple values for argument '{key}'",
                    #     'context': self.context,
                    #     'exit': False
                    # })

        if len(args) == len_expected:
            for i in range(len(args)):
                arg_name = self.arg_names[i]
                if is_varags(self.arg_names[i]):
                    arg_name = make_varargs(self.arg_names[i])
                    arg_value = List([args[i]]).setContext(exec_context)
                    exec_context.symbolTable.set(arg_name, arg_value)
                else:
                    arg_value = args[i]
                    arg_value.setContext(exec_context)
                    exec_context.symbolTable.set(arg_name, arg_value)
            for i in range(len(args), len(self.arg_names)):
                arg_name = self.arg_names[i]
                if len(args) == 0:
                    for name in self.arg_names:
                        if is_varags(name):
                            arg_name = make_varargs(name)
                            arg_value = List([]).setContext(exec_context)
                        else:
                            arg_value = default_values[arg_name]
                else:
                    arg_value = default_values[arg_name]
                arg_value.setContext(exec_context)
                exec_context.symbolTable.set(arg_name, arg_value)
        else:

            for key, value in default_values.items():
                for i in range(len(args)):
                    if self.arg_names[i] == key:
                        arg_name = self.arg_names[i]
                        arg_value = args[i]
                        arg_value.setContext(exec_context)
                        exec_context.symbolTable.set(arg_name, arg_value)

            try:
                for i in range(len(args), len(self.arg_names)):
                    arg_name = self.arg_names[i]
                    arg_value = default_values[arg_name]
                    arg_value.setContext(exec_context)
                    exec_context.symbolTable.set(arg_name, arg_value)
            except Exception as e:
                for i in range(len(args)):
                    arg_name = self.arg_names[i]
                    arg_value = args[i]
                    arg_value.setContext(exec_context)
                    exec_context.symbolTable.set(arg_name, arg_value)

                # raise Al_ValueError({
                #     'pos_start': self.pos_start,
                #     'pos_end': self.pos_end,
                #     'message': f"{self.name if self.name != 'none' else 'anonymous'}() missing {len_expected} required positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} ",
                #     'context': self.context,
                #     'exit': False
                # })

        if len(args) == len(self.arg_names):
            var_args = []
            remaining_args = []
            exception_details = {
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given",
                'context': self.context,
                'exit': False
            }
            has_var_args = False
            has_default_args = False
            for i in range(len(args)):
                if is_varags(self.arg_names[i]):
                    has_var_args = True
                    last_positional_arg = len_arg_names - 1
                    for j in range(len_arg_names):
                        if last_positional_arg == j:
                            start_index = self.arg_names.index(
                                self.arg_names[j])
                            var_args = args[start_index:len_args]
                            remaining_args = args[0:start_index]
                            len_remaining_args = len(remaining_args)
                            len_arg_names_remaining = len_arg_names - 1
                            var_name = make_varargs(self.arg_names[j])
                            var_value = List(var_args)
                            var_value.setContext(exec_context)
                            exec_context.symbolTable.set(var_name, var_value)
                            for k in range(len_remaining_args):
                                arg_name = self.arg_names[k]
                                arg_value = remaining_args[k]
                                arg_value.setContext(exec_context)
                                exec_context.symbolTable.set(
                                    arg_name, arg_value)
                        else:
                            if is_varags(self.arg_names[j]):
                                if len_args == len_arg_names:
                                    var_args = args[i:len_args]
                                    var_name = make_varargs(self.arg_names[j])
                                    var_value = List(var_args)
                                    var_value.setContext(exec_context)
                                    exec_context.symbolTable.set(
                                        var_name, var_value)
                                if len(default_values) > 0:
                                    names = []
                                    values = []
                                    for key, value in default_values.items():
                                        for i in range(len_arg_names):
                                            if self.arg_names[i] == key:
                                                names.append(key)
                                                values.append(value)
                                                has_default_args = True
                                    for i in range(len(names)):
                                        arg_name = names[i]
                                        arg_value = values[i]
                                        arg_value.setContext(exec_context)
                                        exec_context.symbolTable.set(
                                            arg_name, arg_value)

                            if not has_default_args:
                                new_args_names.pop(i)
                                missing_args_name = self.make_missing_args(
                                    new_args_names, len_args)
                                exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() missing {len(new_args_names)} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name}"
                                raise Al_ArgumentError(exception_details)

            if not has_var_args:
                arg_name = self.arg_names[i]
                arg_value = args[i]
                arg_value.setContext(exec_context)
                exec_context.symbolTable.set(arg_name, arg_value)
        else:
            len_arg_names = len(self.arg_names)
            len_args = len(args)
            new_args_names = [
                name for name in self.arg_names if is_varags(name) == False]
            var_args = []
            has_var_args = False
            remaining_args = []
            has_remaining_args = False
            if len_args > len_arg_names:
                for i in range(len(self.arg_names)):
                    first_positional_arg = i
                    last_positional_arg = len_arg_names - 1
                    if is_varags(self.arg_names[i]):
                            has_var_args = True
                            # check if *args is the first positional arg and last positional arg
                            if len_arg_names == 1:
                                var_args = args[self.arg_names.index(
                                    self.arg_names[i]):]
                                var_name = make_varargs(self.arg_names[i])
                                var_value = List(var_args)
                                var_value.setContext(exec_context)
                                exec_context.symbolTable.set(
                                    var_name, var_value)
                            else:
                                if first_positional_arg == 0:
                                    start_index = self.arg_names.index(
                                        self.arg_names[i])
                                    var_args = args[start_index:len_args -
                                                    len_arg_names + 1]
                                    remaining_args = args[len_args -
                                                          len_arg_names + 1:]
                                    var_name = make_varargs(self.arg_names[i])
                                    var_value = List(var_args)
                                    var_value.setContext(exec_context)
                                    exec_context.symbolTable.set(
                                        var_name, var_value)
                                    has_remaining_args = True
                                if last_positional_arg == i:
                                    start_index = self.arg_names.index(
                                        self.arg_names[i])
                                    var_args = args[start_index:len_args]
                                    remaining_args = args[0:start_index]
                                    var_name = make_varargs(self.arg_names[i])
                                    var_value = List(var_args)
                                    var_value.setContext(exec_context)
                                    exec_context.symbolTable.set(
                                        var_name, var_value)
                                    has_remaining_args = True
                                else:
                                    # check for *args in the middle
                                    # first index gets the first element of the list, second index gets the second element of the list and last index gets the last element of the list
                                    # if *args is at the middle, the *args will be elements in the list until we reach a non-*args element
                                    # e.g a, b, *args, c, d = [1,2,3,4,5,6,7,8,9,10] a = 1, b = 2, *args = [3,4,5,6,7,8] c = 9, d = 10
                                    # *args will be [3,4,5,6,7,8]
                                    start_index = self.arg_names.index(
                                        self.arg_names[i])
                                    first_args = args[0:start_index]
                                    # get the indecies remaining of the arg_names after the start index
                                    remaining_arg_names = self.arg_names[start_index:len_arg_names]
                                    remaining_arg_names = [
                                        name for name in remaining_arg_names if is_varags(name) == False]
                                    # get remaining args names from backwards to front of starting index
                                    reversed_args = args[::-
                                                         1][0:len(remaining_arg_names)]
                                    reversed_args_names = remaining_arg_names[::-1]
                                    var_args = args[start_index:len_args -
                                                    len_arg_names + start_index + 1]
                                    re_reverse_args = reversed_args[::-1]
                                    re_reverse_args_names = reversed_args_names[::-1]
                                    remaining_args = first_args + re_reverse_args
                                    var_name = make_varargs(self.arg_names[i])
                                    var_value = List(var_args)
                                    var_value.setContext(exec_context)
                                    exec_context.symbolTable.set(
                                        var_name, var_value)
                                    has_remaining_args = True

                    if has_remaining_args:
                        len_remaining_args = len(remaining_args)
                        for k in range(len_remaining_args):
                            arg_name = new_args_names[k]
                            arg_value = remaining_args[k]
                            arg_value.setContext(exec_context)
                            exec_context.symbolTable.set(arg_name, arg_value)

                if not has_var_args:
                    for i in range(len(args)):
                        arg_name = self.arg_names[i]
                        arg_value = args[i]
                        arg_value.setContext(exec_context)
                        exec_context.symbolTable.set(arg_name, arg_value)

        if len(keyword_args) > 0:
            for key, value in keyword_args.items():
                value.setContext(exec_context)
                if key in self.arg_names:
                    exec_context.symbolTable.set(key, value)
                    # the rest of the arg_names should be default values
                    if len(self.arg_names) > len(args):
                        for name in self.arg_names:
                            if name not in keyword_args:
                                if len(self.default_values) > 0:
                                    if name in self.default_values:
                                        exec_context.symbolTable.set(
                                            name, default_values[name])

                else:
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{self.name if self.name != 'none' else 'anonymous' }() got an unexpected keyword argument '{key}'",
                        'context': self.context,
                        'exit': False
                    })

    def check_and_populate_args(self, keyword_args, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(keyword_args, args))
        if res.should_return(): return res
        self.populate_args(keyword_args, args, exec_ctx)
        return res.success(None)

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

    def isSame(self, other):
        if isinstance(other, BuiltInFunction):
            return self.name == other.name
        return False

    def is_true(self):
        return True


class BaseClass(Value):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbolTable = SymbolTable(new_context.parent.symbolTable)
        return new_context

    def make_missing_args(self, missing_args, len_args):
        missing_args_name = ''
        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f""

        return missing_args_name

    def check_args(self, constructor_args, args, default_values_list):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        # remove self from constructor_args
        default_values = {}
        len_args = len(args)
        if len_args == 0:
            len_args = "none"
        was_or_were = "was" if len_args == 1 or len_args == 0 or len_args == "none" else "were"
        len_expected = len(constructor_args)
        new_args_names = constructor_args
        if len(default_values_list) > 0:
            for default_value in default_values_list:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))

                default_values[name] = value
                len_expected = len(constructor_args) - len(default_values)

        missing_args = []
        missing_args_name = ""
        keys = []

        for key, value in default_values.items():
            keys.append(key)

        for i in range(len(constructor_args)):
            if constructor_args[i] not in keys:
                # append the missing args but remove the self
                if constructor_args[i] != 'self':
                    missing_args.append(constructor_args[i])



        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f""

        exception_details = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given",
            'context': self.context,
            'exit': False
        }

        if default_values == {} or default_values == None:
            has_var_args = False
            if len(args) > len(constructor_args):
                len_arg_names = len(constructor_args)
                len_args = len(args)
                for i in range(len(constructor_args)):
                    if is_varags(constructor_args[i]):
                        has_var_args = True
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"

                    raise Al_ArgumentError(exception_details)

            if len(args) < len(constructor_args):
                has_var_args = False
                for i in range(len(args)):
                    if is_varags(constructor_args[i]):
                        has_var_args = True
                        new_args_names.pop(i)
                        missing_args_name = self.make_missing_args(
                            new_args_names, len_args)
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() missing {len(new_args_names)} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"

                    raise Al_ArgumentError(exception_details)

        else:
            if len(args) > len_expected:
                if len(args) > len_expected and len(constructor_args) == 0:
                    exception_details['message'] = f"{self.name}() takes 0 positional arguments but {len_args} {was_or_were} given"
                    raise Al_ArgumentError(exception_details)

                if len(missing_args) == 0:
                    if len(args) > len(constructor_args):
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"
                        raise Al_ArgumentError(exception_details)
                    else:
                        return res.success(None)
                else:
                    if len(args) > len(constructor_args):
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() expected {len_expected} positional arguments"
                        raise Al_ArgumentError(exception_details)

            if len(args) < len_expected:
                has_var_args = False
                if len(args) == 0:
                    for name in constructor_args:
                        if is_varags(name):
                            has_var_args = True
                            new_args_names.pop(i)
                            return res.success(None)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name} but {len_args} {was_or_were} given"
                    raise Al_ArgumentError(exception_details)

        return res.success(None)

    def populate_args(self, keyword_args, constructor_args, args, default_values_list,exec_context):
        res = RuntimeResult()
        interpreter = Interpreter()
        default_values = {}
        len_expected = len(constructor_args)
        len_args = len(args)
        len_arg_names = len(constructor_args)
        has_var_args = False
        # remove first arg in constructor_args
        new_args_names = constructor_args
        new_args = args[1:]
        has_star = False

        for i in range(len(constructor_args)):
            if is_varags(constructor_args[i]):
                has_star = True
        if has_star:
            star_names = [name for name in constructor_args if is_varags(name) == True]
            non_star_names = [name for name in constructor_args if is_varags(name) == False]
            starags, nonstarargs = vna_algorithm(constructor_args, args)
            for star_name in star_names:
                name = make_varargs(star_name)
                exec_context.symbolTable.set(name, List(starags))
            for i in range(len(non_star_names)):
                try:
                    exec_context.symbolTable.set(
                        non_star_names[i], nonstarargs[i])
                except Exception as e:
                    raise Al_ValueError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{self.name}() missing {len(non_star_names) - i} required keyword-only argument{'s' if len(non_star_names) - i > 1 else ''}",
                        'context': self.context,
                        'exit': False
                    })
        else:
            for i in range(len(args)):
                arg_name = constructor_args[i]
                arg_value = args[i]
                arg_value.setContext(exec_context)
                exec_context.symbolTable.set(arg_name, arg_value)



        if len(default_values) > 0:
            for default_value in default_values:
                name = default_value
                value = default_values[name]
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value

            if len_args < len_arg_names:
                for i in range(len_arg_names):
                    if  new_args_names[i] in default_values:
                        arg_name = new_args_names[i]
                        arg_value = default_values[arg_name]
                        arg_value.setContext(exec_context)
                        exec_context.symbolTable.set(arg_name, arg_value)


        if len(keyword_args) > 0:
            for key, value in keyword_args.items():
                value.setContext(exec_context)
                if key in constructor_args:
                    exec_context.symbolTable.set(key, value)
                    # the rest of the arg_names should be default values
                    if len(constructor_args) > len(args):
                        for name in constructor_args:
                            if name not in keyword_args:
                                if len(default_values) > 0:
                                    if name in default_values:
                                        exec_context.symbolTable.set(
                                            name, default_values[name])

                else:
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{self.name}() got an unexpected keyword argument '{key}'",
                        'context': self.context,
                        'exit': False
                    })

    def or_by(self, other):
        return self.setTrueorFalse(self.value or other.value), None

    def is_true(self):
        return True


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, implicit_return, default_values, properties, type, doc, context):
        super().__init__(name)
        self.name = name if name != None and name != "none" else "<anonymous>"
        self.id = name
        self.body_node = body_node
        self.arg_names = arg_names
        self.implicit_return = implicit_return
        self.default_values = default_values
        self.properties = properties
        self.type = type
        self.doc = doc
        self.context = context
        self.value = f"<function {str(self.name) if self.name != 'none' else 'anonymous'}()>, {self.arg_names if len(self.arg_names) > 0 else '[no args]'}"

    def execute(self, args, keyword_args_list):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        self.args = args
        keyword_args = {}
        default_values = {}
        new_args = []
        exec_context.symbolTable.set("self", self)
        #new_args = args
        # default values
        if self.default_values != None:
            if len(self.default_values) > 0:
                for default_value in self.default_values:
                    name = default_value['name']
                    value = res.register(interpreter.visit(
                        default_value['value'], exec_context))
                    default_values[name] = value

        if keyword_args_list != None:
            if len(keyword_args_list) > 0:

                for keyword_arg in keyword_args_list:
                    name = keyword_arg['name']
                    value = res.register(interpreter.visit(
                        keyword_arg['value'], exec_context))
                    keyword_args[name] = value
                if len(self.arg_names) > 0:
                    for i in range(len(self.arg_names)):
                        has_star_name = [name for name in self.arg_names if is_varags(name) == True]
                        has_star = False if len(has_star_name) == 0 else True
                        if not has_star:
                            for key, value in keyword_args.items():
                                if self.arg_names[i] == key:
                                    args.append(value)
                                elif key not in self.arg_names:
                                    raise Al_ArgumentError({
                                        'pos_start': self.pos_start,
                                        'pos_end': self.pos_end,
                                        'message': f"{self.name}() got an unexpected keyword argument '{key}'",
                                        'context': self.context,
                                        'exit': False
                                    })
                        else:
                            pass
                            #print("varags", self.arg_names[i])

                    # len_old_args = len(args) - len(keyword_args)
                    # if len(args) > 0:
                    #     for i in range(len_old_args):
                    #         new_args.insert(i, args[i])
                    #     # new_args.insert(0, args[0])

                    # if len(keyword_args) > 0:
                    #     for i in range(len(self.arg_names)):
                    #         if self.arg_names[i] in keyword_args:
                    #             index_key = self.arg_names.index(self.arg_names[i])
                    #             args_index = len_old_args - 1

            else:
                new_args = args

        # if len(self.default_values) > 0:
        #     for default_value in self.default_values:
        #         name = default_value['name']
        #         value = res.register(interpreter.visit(default_value['value'], exec_context))
        #         default_values[name] = value

        #     # default values
        #     # if len(default_values) > 0:
        #     #     print(default_values, len(args), len(self.arg_names))
        #     #     # check if key in keyword_args
        #     #     if len(ke)

        # if len(self.arg_names) > 0:
        #     args_expected = len(self.arg_names)
        #new_args = args + new_args
        # if keyword_args_list != None and len(keyword_args_list) > 0:
        #     args = new_args
        self.check_args(args, keyword_args)
        self.populate_args(keyword_args, args, exec_context)

        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.func_return_value == None: return res
        return_value = (
            value if self.implicit_return else None) or res.func_return_value
        # if hasattr(return_value, "value"):
        #     if return_value.value == "none":
        #         return_value.value = NoneType.none
        # 
        
        return res.success(return_value)

    def make_missing_args(self, missing_args, len_args):
        missing_args_name = ': '
        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f"but {len_args} {'was' if len_args == 1 or len_args == 0 else 'were'} given"

        return missing_args_name

    def check_args(self, args,keyword_args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        default_values = {}
        len_args = len(args)
        len_arg_names = len(self.arg_names)
        # if len_args == 0:
        #     len_args = "none"
        was_or_were = "was" if len_args == 1 or len_args == 0 or len_args == "none" else "were"
        len_expected = len(self.arg_names)
        new_args_names = self.arg_names
        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value
                len_expected = len(self.arg_names) - len(default_values)

        missing_args = []
        missing_args_name = ": "
        keys = []

        for key, value in default_values.items():
            keys.append(key)

        for i in range(len(self.arg_names)):
            if self.arg_names[i] not in keys:
                missing_args.append(self.arg_names[i])

        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f""

        exception_details = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}",
            'context': self.context,
            'exit': False
        }
        if default_values == {} or default_values == None:
            has_var_args = False
            if len(args) > len(self.arg_names):
                len_arg_names = len(self.arg_names)
                len_args = len(args)
                for i in range(len(self.arg_names)):
                    if is_varags(self.arg_names[i]):
                        has_var_args = True
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) <= 1 else 'arguments'}{missing_args_name} but {len_args} {was_or_were} given"

                    raise Al_ArgumentError(exception_details)

            if len(args) < len(self.arg_names):
                has_var_args = False
                for i in range(len(args)):
                    if is_varags(self.arg_names[i]):
                        if len(keyword_args) > 0:
                            for key, value in keyword_args.items():
                                if key in self.arg_names:
                                    return res.success(None)
                        has_var_args = True
                        new_args_names.pop(i)
                        missing_args_name = self.make_missing_args(
                            new_args_names, len_args)
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() missing {len(new_args_names)} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"

                    raise Al_ArgumentError(exception_details)

        else:
            if len(args) > len_expected:
                if len(args) > len_expected and len(self.arg_names) == 0:
                    exception_details['message'] = f"{self.name}() takes 0 positional arguments"
                    raise Al_ArgumentError(exception_details)

                if len(missing_args) == 0:
                    if len(args) > len(self.arg_names):
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}: {missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                    else:
                        return res.success(None)
                else:
                    non_var_ags = []
                    values = []
                    if len(args) > len(self.arg_names):
                        # for i in range(len(self.arg_names)):
                        #         non_var_ags.append(self.arg_names[i])
                        #         non_var_ags.reverse()
                        #         if len(default_values) > 0:
                        #             if self.arg_names[i] in default_values:
                        #                 values.append(default_values[self.arg_names[i]])
                        #         if is_varags(self.arg_names[i]):
                        #             first_positional_arg = self.arg_names.index(self.arg_names[i])
                        #             if first_positional_arg == 0:
                        #                 start_index = self.arg_names.index(self.arg_names[i]) + 1
                        #                 var_args = args[start_index:len_args]
                        #                 print(var_args)
                        exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() expected {len_expected} positional arguments"
                        raise Al_ArgumentError(exception_details)


            if len(args) < len_expected:
                has_var_args = False
                if len(args) == 0:
                    for name in self.arg_names:
                        if is_varags(name):
                            has_var_args = True
                            new_args_names.pop(i)
                            return res.success(None)
                if not has_var_args:
                    exception_details['message'] = f"{self.name if self.name != 'none' else 'anonymous'}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                    raise Al_ArgumentError(exception_details)

        return res.success(None)

    def populate_args(self, keyword_args, args, exec_context):
        res = RuntimeResult()
        interpreter = Interpreter()
        default_values = {}
        len_expected = len(self.arg_names)
        len_args = len(args)
        len_arg_names = len(self.arg_names)
        has_var_args = False
        # remove first arg in self.arg_names
        new_args_names = self.arg_names
        new_args = args[1:]
        has_star = False
        for i in range(len(self.arg_names)):
            if is_varags(self.arg_names[i]):
                has_star = True
        if has_star:
            star_names = [name for name in self.arg_names if is_varags(name) == True]
            non_star_names = [name for name in self.arg_names if is_varags(name) == False]
            starags, nonstarargs = vna_algorithm(self.arg_names, args)
            #print(star_names, non_star_names)
            #print(starags, nonstarargs, "args: ", args)
            for star_name in star_names:
                name = make_varargs(star_name)
                exec_context.symbolTable.set(name, List(starags))
            for i in range(len(non_star_names)):
                try:
                    name = non_star_names[i]
                    value = nonstarargs[i].setContext(exec_context)
                    exec_context.symbolTable.set(name, value)
                except Exception as e:
                    raise Al_ValueError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{self.name if self.name != 'none' else 'anonymous'}() missing {len(non_star_names) - i} required keyword-only argument{'s' if len(non_star_names) - i > 1 else ''}",
                        'context': self.context,
                        'exit': False
                    })
        else:
            for i in range(len(args)):
                arg_name = self.arg_names[i]
                arg_value = args[i]
                arg_value.setContext(exec_context)
                exec_context.symbolTable.set(arg_name, arg_value)



        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value

            if len_args < len_arg_names:
                for i in range(len_arg_names):
                    if  new_args_names[i] in default_values:
                        arg_name = new_args_names[i]
                        arg_value = default_values[arg_name]
                        arg_value.setContext(exec_context)
                        exec_context.symbolTable.set(arg_name, arg_value)


        if len(keyword_args) > 0:
            for key, value in keyword_args.items():
                value.setContext(exec_context)
                if key in self.arg_names:
                    exec_context.symbolTable.set(key, value)
                    # the rest of the arg_names should be default values
                    if len(self.arg_names) > len(args):
                        for name in self.arg_names:
                            if name not in keyword_args:
                                if len(self.default_values) > 0:
                                    if name in self.default_values:
                                        exec_context.symbolTable.set(
                                            name, default_values[name])

                else:
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{self.name if self.name != 'none' else 'anonymous'}() got an unexpected keyword argument '{key}'",
                        'context': self.context,
                        'exit': False
                    })

    # only class Function calls this method
    def run(self, keyword_args_list, args, Klass, context=None, is_Init=None):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        keyword_args = {}
        default_values = {}
        new_args = []
        new_args = args
        # default values
        if self.default_values != None:
            if len(self.default_values) > 0:
                for default_value in self.default_values:
                    name = default_value['name']
                    value = res.register(interpreter.visit(
                        default_value['value'], exec_context))
                    default_values[name] = value


        if keyword_args_list != None:
            if len(keyword_args_list) > 0:

                for keyword_arg in keyword_args_list:
                    name = keyword_arg['name']
                    value = res.register(interpreter.visit(
                        keyword_arg['value'], exec_context))
                    keyword_args[name] = value
                values = []
                if len(self.arg_names) > 0:
                    for i in range(len(self.arg_names)):
                        for key, value in keyword_args.items():
                            if self.arg_names[i] == key:
                                new_args.append(value)
                                values.append(value)
                            elif key not in self.arg_names:
                                raise Al_ArgumentError({
                                    'pos_start': self.pos_start,
                                    'pos_end': self.pos_end,
                                    'message': f"{Klass.name}() got an unexpected keyword argument '{key}'",
                                    'context': self.context,
                                    'exit': False
                                })
                            # else:
                            #     for key, value in keyword_args.items():
                            #         if key in self.arg_names:
                            #             if key not in default_values:
                            #                 # checkif key is at the right index of non default values
                            #                 if len(keyword_args) > 0:
                            #                     for i in range(len(self.arg_names)):
                            #                         if self.arg_names[i] == key:
                            #                             print(self.arg_names[i], key)
                            #                 raise Al_ValueError({
                            #                     'pos_start': self.pos_start,
                            #                     'pos_end': self.pos_end,
                            #                     'message': f"{self.name}() got multiple values for argument '{key}'",
                            #                     'context': self.context,
                            #                     'exit': False
                            #                 })

                    # len_old_args = len(args) - len(keyword_args)
                    # if len(args) > 0:
                    #     for i in range(len_old_args):
                    #         new_args.insert(i, args[i])
                        # new_args.insert(0, args[0])

                    # if len(keyword_args) > 0:
                    #     for i in range(len(self.arg_names)):
                    #         if self.arg_names[i] in keyword_args:
                    #             index_key = self.arg_names.index(self.arg_names[i])
                    #             args_index = len_old_args - 1
            else:
                new_args = args

        # if len(self.default_values) > 0:
        #     for default_value in self.default_values:
        #         name = default_value['name']
        #         value = res.register(interpreter.visit(default_value['value'], exec_context))
        #         default_values[name] = value

        #     # default values
        #     # if len(default_values) > 0:
        #     #     print(default_values, len(args), len(self.arg_names))
        #     #     # check if key in keyword_args
        #     #     if len(ke)

        # if len(self.arg_names) > 0:
        #     args_expected = len(self.arg_names)

        # if keyword_args_list != None and len(keyword_args_list) > 0:
        #     args = new_args
        #print(Klass.properties)
        if '__@init__' in Klass.properties:
            args = [Klass] + new_args

        # if len(args) > 0:
        #     args = [Klass] + args
        # if len(self.arg_names) == 1 and len(args) == 0:
        #     args = [Klass]
        # if len(self.arg_names) == 0 and len(args) == 0:
        #     args = [Klass]
        # if len(args) == 0:
        #     args = [Klass]

        #print(self.name,self.arg_names, args)
        self.args = args
        res.register(self.run_check_and_populate_args(keyword_args, args, exec_context, Klass))

        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_context))

        if res.should_return() and res.func_return_value == None: return res
        return_value = (
            value if self.implicit_return else None) or res.func_return_value or NoneType.none
        # if hasattr(return_value, "value"):
        #     if return_value.value == "none":
        #         return_value.value = NoneType.none
        return self.wrap_return_value(return_value)

    def wrap_return_value(self, return_value):
        return_value = return_value.copy()
        return return_value

    def run_check_and_populate_args(self, keyword_args, args, exec_ctx, Klass):
        res = RuntimeResult()
        res.register(self.run_check_args(args, Klass,keyword_args))
        if res.should_return(): return res
        self.run_populate_args(Klass,keyword_args, args, exec_ctx)
        return res.success(None)

    def run_check_args(self, args, klass_,keyword_args):
        res = RuntimeResult()
        interpreter = Interpreter()
        class_name = klass_.name if self.name == "__@init__" else self.name
        exec_context = self.generate_new_context()
        default_values = {}
        len_args = len(args)
        len_arg_names = len(self.arg_names)
        was_or_were = "was" if len_args == 1 or len_args == 0 or len_args == "none" else "were"
        len_expected = len(self.arg_names) - 1
        new_args_names = self.arg_names
        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value
                len_expected = len(self.arg_names) - len(default_values) - 1


        missing_args = []
        missing_args_name = ": "
        keys = []

        for key, value in default_values.items():
            keys.append(key)
        for i in range(len(self.arg_names)):
            if self.arg_names[i] not in keys:
                name = self.arg_names[i]
                if is_varags(self.arg_names[i]):
                    name = make_varargs(self.arg_names[i])
                if i == 0:
                    pass
                else:
                    missing_args.append(name)

        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f""

        exception_details = {
            'pos_start': klass_.pos_start if klass_ != None else self.pos_start,
            'pos_end': klass_.pos_end if klass_ != None else self.pos_end,
            'message': f"{class_name}() requires {len_expected} positional {'argument'  if len(missing_args) <= 1 else 'arguments'}{missing_args_name} but {len_args} {was_or_were} given",
            'context': klass_.context if klass_ != None else self.context,
            'exit': False
        }
        if default_values == {} or default_values == None:

            has_var_args = False
            if len_args > len_arg_names:
                if  len_arg_names == 1:
                    exception_details['message'] = f"{class_name}() takes 0 positional argument"
                    raise Al_ArgumentError(exception_details)
                for i in range(len_arg_names):
                    if is_varags(self.arg_names[i]):
                        has_var_args = True
                if not has_var_args:
                    exception_details['message'] = f"{class_name}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name} "

                    raise Al_ArgumentError(exception_details)

            if len_args < len_arg_names:
                has_var_args = False
                for i in range(len_args):
                    if is_varags(self.arg_names[i]):
                        if len(keyword_args) > 0:
                            for key, value in keyword_args.items():
                                if key in self.arg_names:
                                    return res.success(None)
                        has_var_args = True
                        new_args_names.pop(i)
                        len_expected = len(new_args_names) - 1
                        missing_args = missing_args[1:]
                        missing_args_name = self.make_missing_args(
                            missing_args, len_args)
                        exception_details['message'] = f"{class_name}() missing {len_expected} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                if not has_var_args:
                    exception_details['message'] = f"{class_name}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name} "

                    raise Al_ArgumentError(exception_details)
            else:
                new_args = args[1:]
                new_args_names = new_args_names[1:]
                len_args = len(new_args)
                len_arg_names = len(new_args_names)
                for i in range(len_arg_names):
                    new_args_names_ = [arg for arg in new_args_names if is_varags(arg) == False]
                    #print(new_args_names_,args)
                    if is_varags(new_args_names[i]):
                        if len(keyword_args) > 0:
                            for key, value in keyword_args.items():
                                if key in new_args_names_:
                                    return res.success(None)
                                else:
                                    len_expected = len(new_args_names) - 1
                                    missing_args = missing_args[1:]
                                    missing_args_name = self.make_missing_args(missing_args, len_args)
                                    exception_details['message'] = f"{class_name}() missing {len_expected} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                                    raise Al_ArgumentError(exception_details)
                        else:
                            len_expected = len(new_args_names) - 1
                            missing_args = missing_args[1:]
                            missing_args_name = self.make_missing_args(missing_args, len_args)
                            exception_details['message'] = f"{class_name}() missing {len_expected} required keyword-only {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                            raise Al_ArgumentError(exception_details)
        else:
            if len_args > len_expected:
                if len_arg_names > 0:
                    len_expected = len_expected - 1
                    if len_expected == -1:
                        len_expected = 0
                len_args = len_args - 1
                if len_args > len_expected and len_arg_names == 0:
                    exception_details['message'] = f"{class_name}()  takes 0 positional argument"
                    raise Al_ArgumentError(exception_details)

                if len(missing_args) == 0:
                    if len_args > len_arg_names:
                        exception_details['message'] = f"{class_name}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                        raise Al_ArgumentError(exception_details)
                    else:
                        return res.success(None)
                else:
                    if len_args > len_arg_names:
                        exception_details['message'] = f"{class_name}() expected {len_expected} positional arguments"
                        raise Al_ArgumentError(exception_details)

            if len_args < len_expected:
                len_expected = len_expected - 1
                len_args = len_args - 1
                has_var_args = False
                if len_args == 0:
                    for name in self.arg_names:
                        if is_varags(name):
                            has_var_args = True
                            new_args_names.pop(i)
                            return res.success(None)
                if not has_var_args:
                    exception_details['message'] = f"{class_name}() requires {len_expected} positional {'argument'  if len(missing_args) == 1 else 'arguments'}{missing_args_name}"
                    raise Al_ArgumentError(exception_details)

        return res.success(None)

    def run_populate_args(self, klass_, keyword_args, args, exec_context):
        res = RuntimeResult()
        interpreter = Interpreter()
        class_name = klass_.name if self.name == "__@init__" else self.name
        default_values = {}
        len_expected = len(self.arg_names)
        len_args = len(args) - 1
        len_arg_names = len(self.arg_names) - 1
        has_var_args = False
        # remove first arg in self.arg_names
        new_args_names = self.arg_names[1:]
        new_args = args[1:]
        has_star = False
        for i in range(len(self.arg_names)):
            if is_varags(self.arg_names[i]):
                has_star = True
        if has_star:
            star_names = [name for name in self.arg_names if is_varags(name) == True]
            non_star_names = [name for name in self.arg_names if is_varags(name) == False]
            starags, nonstarargs = vna_algorithm(self.arg_names, args)
            for star_name in star_names:
                name = make_varargs(star_name)
                exec_context.symbolTable.set(name, List(starags))
            for i in range(len(non_star_names)):
                try:
                    exec_context.symbolTable.set(
                        non_star_names[i], nonstarargs[i])
                except Exception as e:
                    raise Al_ValueError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{class_name}() missing {len(non_star_names) - i} required keyword-only argument{'s' if len(non_star_names) - i > 1 else ''}",
                        'context': klass_.context if klass_ != None else self.context,
                        'exit': False
                    })
        else:
            for i in range(len(args)):
                arg_name = self.arg_names[i]
                arg_value = args[i]
                arg_value.setContext(exec_context)
                exec_context.symbolTable.set(arg_name, arg_value)



        if len(self.default_values) > 0:
            for default_value in self.default_values:
                name = default_value['name']
                value = res.register(interpreter.visit(
                    default_value['value'], exec_context))
                default_values[name] = value

            if len_args < len_arg_names:
                for i in range(len_arg_names):
                    if  new_args_names[i] in default_values:
                        arg_name = new_args_names[i]
                        arg_value = default_values[arg_name]
                        arg_value.setContext(exec_context)
                        exec_context.symbolTable.set(arg_name, arg_value)


        if len(keyword_args) > 0:
            for key, value in keyword_args.items():
                value.setContext(exec_context)
                if key in self.arg_names:
                    exec_context.symbolTable.set(key, value)
                    # the rest of the arg_names should be default values
                    if len(self.arg_names) > len(args):
                        for name in self.arg_names:
                            if name not in keyword_args:
                                if len(self.default_values) > 0:
                                    if name in self.default_values:
                                        exec_context.symbolTable.set(
                                            name, default_values[name])

                else:
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"{klass_.class_name}()  got an unexpected keyword argument '{key}'",
                        'context': self.context,
                        'exit': False
                    })

    def copy(self):
        copy = Function(self.name, self.body_node,
                    self.arg_names, self.implicit_return, self.default_values,self.properties,self.type,self.doc,self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __Name__(self, args, kwargs, var_name=None):
        if args == None:
            if 'name' in self.properties:
                if isinstance(self.properties['name'], str):
                    return String(self.properties['name'])
                else:
                    return self.properties['name']
            else:
                return String(self.name)

            
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@name__' is not callable",
                "context": self.context,
                'exit': False
            })

    def __call__(self, args, kwargs, var_name=None):
        if args == None:
            return BuiltInFunction("__@call__", self.context)
        
        if len(kwargs) > 0:
            raise Al_ArgumentError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"__@call__() takes no keyword argument",
                'context': self.context,
                'exit': False
            })
        
        
        
        self.execute(args, kwargs)
             
    def __params__(self, args, kwargs, var_name=None):
        if args == None:
            params = []
            for arg in self.arg_names:
                params.append(String(arg))
            return List(params)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@params__' is not callable",
                "context": self.context,
                'exit': False
            })

    def __Doc__(self, args, kwargs, var_name=None):
        if args == None:
            if self.doc == None:
                return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                if isinstance(self.doc, String) or isinstance(self.doc, DocString):
                    return self.doc
                else:
                    return String(self.doc).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@doc__' is not callable",
                "context": self.context,
                'exit': False
            })
     
    def __repr__(self):
        return f"<function {str(self.name) if self.name != 'none' else 'anonymous'}()>, {self.arg_names if len(self.arg_names) > 0 else '[no args]'}"


function_methods = {
    '__@call__': Function.__call__,
    '__@name__': Function.__Name__,
    '__@params__': Function.__params__,
    '__@doc__': Function.__Doc__
}


class BuiltInFunction(BaseFunction):
    def __init__(self, name, doc=None, context=None, properties=None):
        super().__init__(name)
        self.value = name
        self.doc = doc
        self.context = context
        self.properties = properties
        self.representation = f"<{str(self.name)}()>, [ built-in function_method ]"


    def execute(self, args, keyword_args_list):
        res = RuntimeResult()
        exec_context = self.generate_new_context()
        interpreter = Interpreter()
        keyword_args = {}

        new_args = []

        if keyword_args_list != None and len(keyword_args_list) > 0:
            for keyword_arg in keyword_args_list:
                name = keyword_arg['name']
                value = res.register(interpreter.visit(keyword_arg['value'], exec_context))
                keyword_args[name] = value

        # if len(args) > 0:
        #     for arg in args:
        #         v = res.register(interpreter.visit(arg, exec_context))
        #         args.append(v)

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit)

        res.register(self.check_and_populate_args(
            method.arg_names, method.default_values, args, keyword_args, exec_context))

        if res.should_return():
            return res

        return_value = res.register(method(exec_context))
        if res.should_return(): return res
        return res.success(return_value)


    def check_and_populate_args(self, arg_names, default_values, args, keyword_args, exec_context):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, default_values,  args, keyword_args, exec_context))
        if res.should_return(): return res

        return res.success(None)


    def check_args(self, arg_names, default_values, args, keyword_args, exec_context):
        res = RuntimeResult()
        len_expected = len(arg_names)
        len_args = len(args)
        keyword_args_names = []

        exception_details = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name}() requires {len_expected} positional {'argument'  if len_expected <= 1 else 'arguments'} but {len_args} {'was' if len_args <= 1 else 'were'} given",
            'context': self.context,
            'exit': False
        }

        if len(keyword_args) > 0:
            for name, value in keyword_args.items():
                if not name in arg_names:
                    raise Al_ArgumentError({
                    'pos_start': self.pos_start,
                    'pos_end': self.pos_end,
                    'message': f"{self.name}() got an unexpected keyword argument '{name}'",
                    'context': self.context,
                    'exit': False
                })
                if not isinstance(value, String):
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"File() keyword argument '{name}' must be of type string",
                        'context': self.context,
                        'exit': False
                    })

                keyword_args_names.append(name)
            len_keyword_args = len(keyword_args_names)
            #print(keyword_args_names, len_keyword_args, len_expected, len_args)

            if len_keyword_args > len_expected:
                exception_details['message'] = f"{self.name}() requires {len_expected} positional {'argument'  if len_expected <= 1 else 'arguments'} but {len_keyword_args} {'was' if len_keyword_args <= 1 else 'were'} given"
                raise Al_ArgumentError(exception_details)
            if len_keyword_args < len_expected:
                if len_keyword_args == 1 and len_args == 1:
                    args.append(keyword_args[keyword_args_names[0]])
                else:
                    exception_details['message'] = f"{self.name}() requires {len_expected} positional {'argument'  if len_expected <= 1 else 'arguments'} but {len_keyword_args} {'was' if len_keyword_args <= 1 else 'were'} given"
                    raise Al_ArgumentError(exception_details)
            elif len_keyword_args == len_expected:
                for i in range(len_expected):
                    if keyword_args_names[i] in arg_names:
                        # append at the correct index
                        args.insert(arg_names.index(keyword_args_names[i]), keyword_args[keyword_args_names[i]])


        else:
            if len(args) > len_expected:
                raise Al_ArgumentError(exception_details)
            if len(args) < len_expected:
                raise Al_ArgumentError(exception_details)



        res.register(self.populate_args(arg_names, default_values, args, exec_context))
        return res.success(None)


    def populate_args(self, arg_names, default_values, args, exec_context):
        res = RuntimeResult()
        for i in range(len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)


        return res.success(None)

    #file
    def execute_read(self, exec_context):
        return handle_file_read(self.properties['file'], self, exec_context)

    execute_read.arg_names = []
    execute_read.default_values = [{}]

    def execute_seek(self, exec_context):
        offset = exec_context.symbolTable.get('offset')
        whence = exec_context.symbolTable.get('whence')
        try:
            return handle_file_seek(self.properties['file'], offset.value, whence.value, self, exec_context)
        except:
            raise Al_IOError({
                "pos_start": self.pos_start if self.pos_start != None else offset.pos_start,
                "pos_end": self.pos_end if self.pos_end != None else offset.pos_end,
                'message': f"unable to seek file to {offset.value} with whence {whence.value}",
                "context": self.context,
                'exit': False
            })

    execute_seek.arg_names = ['offset', 'whence']
    execute_seek.default_values = [{}]

    def execute_write(self, exec_context):
        res = RuntimeResult()
        value = exec_context.symbolTable.get('value')
        if not isinstance(value, String):
            raise Al_TypeError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"write() argument must be of type string, not {TypeOf(value).getType()}",
                'context': self.context,
                'exit': False
            })
        content = value.value
        return handle_file_write(self.properties['file'], content, self, exec_context)

    execute_write.arg_names = ['value']
    execute_write.default_values = [{}]


    def execute_close(self, exec_context):
        res = RuntimeResult()
        file = self.properties['file']
        node = self
        closed = handle_file_close(file, node, exec_context)
        return res.success(Pair([closed, Boolean(file.closed)]).setContext(exec_context).setPosition(node.pos_start, node.pos_end))

    execute_close.arg_names = []
    execute_close.default_values = [{}]


    def no_visit(self):
        res = RuntimeResult()
        raise Al_NameError({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Name '{self.name}' is not defined",
            'context': self.context,
            'exit': False
        })

    def copy(self):
        copy = BuiltInFunction(self.name, self.doc)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __Doc__(self, args, kwargs, var_name=None):
        if args == None:
            if self.doc == None:
                return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                if isinstance(self.doc, String) or isinstance(self.doc, DocString):
                    return self.doc
                else:
                    return String(self.doc).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@doc__' is not callable",
                "context": self.context,
                'exit': False
            })


    def __repr__(self):
        return self.representation
builtin_function_methods = {
    '__@doc__': BuiltInFunction.__Doc__,  # Class.__@doc__()
}


class Class(BaseClass):
    def __init__(self, class_name, class_args,inherit_class_name, inherited_from, class_methods, methods,class_fields_modifiers, doc, context):
        super().__init__(class_name)
        self.id = class_name
        self.class_name = class_name
        self.class_args = class_args
        self.inherit_class_name = inherit_class_name
        self.inherited_from = inherited_from
        self.class_methods = class_methods
        self.methods = methods
        self.properties = methods
        self.class_fields_modifiers = class_fields_modifiers
        self.value = f"<class {str(self.class_name)}>"
        self.doc = doc
        self.context = context
        self.body_node = None
        self.str__ = self.value
        args = []
        for arg in self.class_args:
            args.append(arg.value) if hasattr(arg, "value") else args.append(arg)
        self.class_args = args

    
    def execute(self, args, keyword_args_list):
        res = RuntimeResult()
        interpreter = Interpreter()
        new_context = self.generate_new_context()
        class_args = []
        new_args = []
        keyword_args = {}
        default_values = []
        class_properties = dict({arg_name: arg_value for arg_name, arg_value in zip(
            self.class_args, args)}, **self.methods)
        if keyword_args_list != None and len(keyword_args_list) > 0:
            for keyword_arg in keyword_args_list:
                name = keyword_arg['name']
                value = res.register(interpreter.visit(keyword_arg['value'], new_context))
                keyword_args[name] = value
        
        if len(self.properties) > 0:
            method_ = None
            for method_name, method in self.properties.items():
                method.context = new_context
                method = method.copy()
                self.properties[method_name] = method
                self.properties = class_properties
                method.context.symbolTable.set(
                    "super", self.inherit_class_name) if self.inherit_class_name != None else None
                if method_name == "__@init__":
                    method_ = method
                    method_args = method.arg_names
                    default_values = method.default_values
                    class_args = method_args
                    # remove self from args
                    if len(method_args) > 0:
                        method_args = method_args[1:]
                        class_args = method_args
                
                    

            if method_ != None:
                value = res.register(method_.run(keyword_args_list,args, self, new_context))
                if not isinstance(value, NoneType):
                    raise Al_TypeError({
                        'pos_start': self.pos_start,
                        'pos_end': self.pos_end,
                        'message': f"__@init__() must return none, not '{TypeOf(value).getType()}'",
                        'context': self.context,
                        'exit': False
                    })
        
        self.check_args(class_args, args, default_values)
        self.populate_args(keyword_args,class_args, args, default_values, self.context)

        if res.should_return(): return res

        #new_context.symbolTable.set("self", self)
        

        if self.inherit_class_name != None:

            if isinstance(self.inherit_class_name, BuiltInClass):
                pass
            else:
                pass
                # for key, value in self.properties.items():
                #     if key not in self.properties:
                #         self.inherit_class_name.properties[key] = value
                # while self.inherit_class_name != None:
                #     print("inherit_class_name", self.inherit_class_name, self.class_name)
                # class_args = self.inherit_class_name.class_args + class_args
                # since the inherited class is not a executed yet, we need to set each inherited class parameter to args
                # for i in range(len(self.inherit_class_name.class_args)):
                #     self.inherit_class_name.properties[self.inherit_class_name.class_args[i]] = args[i]

                # print(self.properties,"==",self.inherit_class_name.properties)
        # return a new class instancex
        #new_args = args + new_args
        # create new class instance
        # everytime a class is called we need to create a new instance of the class, so we need to create a new context
        new_class_context = Context(self.name, self.context, self.pos_start)
        new_class_context.symbolTable = SymbolTable(new_context.parent.symbolTable)
        new_class_context.symbolTable.set("self", self)
        new_class_context.symbolTable.set("super", self.inherit_class_name) if self.inherit_class_name != None else None
        return res.success(self.generate_new_instance(class_args, new_class_context))


    def generate_new_instance(self, class_args,new_context):
        return Class(self.class_name, class_args,self.inherit_class_name, self.inherited_from, self.class_methods, self.properties, self.class_fields_modifiers, self.doc, new_context)

    def set_method(self, key, value):
        self.properties[key] = value
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


    def has_property(self, property_name):
        return property_name in self.properties


    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None


    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None


    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None


    def isSame(self, other):
        if isinstance(other, Class):
            _new_class = f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
            other_class = f"{{{', '.join([f'{k}: {v}' for k, v in other.properties.items()])}}}"
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
            for key, value in other.properties.items():
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
        copy = Class(self.class_name, self.class_args,self.inherit_class_name, self.inherited_from, self.class_methods, self.properties, self.class_fields_modifiers, self.doc,self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __methods__(self, args, kwargs, var_name=None):
        if args == None:
            methods = []
            for property_name, property_value in self.class_methods.items():
                if isinstance(property_value, Function):
                    methods.append(String(property_name).setContext(self.context).setPosition(self.pos_start, self.pos_end))
            return methods
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@methods__' is not callable",
                "context": self.context,
                'exit': False
            })
            
            
    def __Doc__(self, args, kwargs, var_name=None):
        if args == None:
            if self.doc == None:
                return NoneType().setContext(self.context).setPosition(self.pos_start, self.pos_end)
            else:
                if isinstance(self.doc, String) or isinstance(self.doc, DocString):
                    return self.doc
                else:
                    return String(self.doc).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@doc__' is not callable",
                "context": self.context,
                'exit': False
            })

    
    def __set_str__(self):
        res = RuntimeResult()
        string = f"<class {str(self.class_name)}>"
        if len(self.properties) > 0:
            for method_name, method in self.properties.items():
                if method_name == "__@str__":
                    _str = method
                    _str_args = method.arg_names
                    default_values = method.default_values
                    string = res.register(_str.run([], [], self, self.generate_new_context()))
                    if res.should_return(): return res
        return string
                    
 
    def __repr__(self):
        return str(self.__set_str__())

class_methods = {
    '__@name__': '__@name__',  # Class.__@name__()
    '__@bases__': '__@bases__',  # Class.__@bases__()
    'is_subclass': 'is_subclass',  # Class.is_subclass(Class)
    '__@fields__': '__@fields__',  # Class.__@fields__()
    '__@methods__': Class.__methods__,  # Class.__@methods__()
    '__@doc__': Class.__Doc__,  # Class.__@doc__()
}

class BuiltInClass(BaseClass):
    def __init__(self, name,properties):
        super().__init__(name)
        self.properties = properties
        self.value = f"<class {str(self.name)}>"
        self.representation = self.value
        self.ACCEPTED_KEYWORD_ARGS_CLASS = {
            'File': {
                'args': 2,
                'kwargs': 2,
                'optional': False,
                'names': ['file', 'mode'],
                'required': True
            },
            'str': {
                'args': 1,
                'kwargs': 'none',
                'optional': True,
                'optional_args': 1,
                'total_args': 2,
                'required': False
            },
            'int': {
                'args': 1,
                'kwargs': 'one',
                'optional': True,
                'optional_args': 1,
                'total_args': 2,
                'names': ['base'],
                'default': Number(10),
                'required': False
            },
            'float': {
                'args': 1,
                'kwargs': 'none',
                'optional': False,
                'required': False
            },
            'chr': {
                'args': 1,
                'kwargs': 'none',
                'optional': False,
                'required': True
            },
            'bool': {
                'args': 1,
                'kwargs': 'none',
                'required': False
            },
            'list': {
                'args': 1,
                'kwargs': 'none',
                'required': False
            },
            'pair': {
                'args': 1,
                'kwargs': 'none',
                'required': False
            },
            'dict': {
                'args': 1,
                'kwargs': 'many',
                'required': False
            },
        }


    def execute(self, args, keyword_args_list):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()
        keyword_args = {}

        if keyword_args_list != None and len(keyword_args_list) > 0:
            for keyword_arg in keyword_args_list:
                name = keyword_arg['name']
                value = res.register(interpreter.visit(keyword_arg['value'], exec_context))
                keyword_args[name] = value



        class_name = f'execute_{self.name}'
        class_ = getattr(self, class_name, self.no_visit)
        res.register(self.check_and_populate_args(
            class_.arg_names, args, keyword_args, exec_context))
        if res.should_return():
            return res

        return_value = res.register(class_(exec_context, keyword_args, args))
        if res.should_return():
            return res
        return res.success(return_value)

    def make_missing_args(self, missing_args, len_args):
        missing_args_name = ''
        if len(missing_args) > 1:
            for i in range(len(missing_args)):
                if i == len(missing_args) - 2:
                    missing_args_name += f"'{missing_args[i]}'" + " and "
                elif i == len(missing_args) - 1:
                    missing_args_name += f"'{missing_args[i]}'"
                else:
                    missing_args_name += f"'{missing_args[i]}'" + ", "
        elif len(missing_args) == 1:
            missing_args_name += f"'{missing_args[0]}'"
        if len(missing_args) == 0:
            missing_args_name = f"but {len_args} {'was' if len_args == 1 or len_args == 0 else 'were'} given"

        return missing_args_name
    
    
    def check_and_populate_args(self, arg_names, args, keyword_args, exec_context):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args, keyword_args, exec_context))
        if res.should_return(): return res
        return res.success(None)


    def check_args(self, arg_names, args, keyword_args, exec_context):
        res = RuntimeResult()
        len_expected = len(arg_names)
        len_args = len(args)
        len_kwargs = len(keyword_args)
        exception_details = {
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"{self.name}() requires {len_expected} positional {'argument'  if len_expected <= 1 else 'arguments'} but {len_args if len_args != 0 else 'none'} {'was' if len_args <= 1 else 'were'} given",
            'context': self.context,
            'exit': False
        }

        
        if self.name in self.ACCEPTED_KEYWORD_ARGS_CLASS:
            if len_args > self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args']:
                if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['optional']:
                    if len_args == self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['total_args']:
                        return res.success(None)
                    else:
                        exception_details['message'] = f"{self.name}() requires {len_expected} positional {'argument'  if len_expected <= 1 else 'arguments'} but {len_args if len_args != 0 else 'none'} {'was' if len_args <= 1 else 'were'} given"
                        raise Al_ArgumentError(exception_details)
                raise Al_ArgumentError(exception_details)
            if len_args < self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args']:
                if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs'] == 'many':
                    if len_kwargs == 0:
                        if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                            raise Al_ArgumentError(exception_details)
                        else:
                            return res.success(None)
                    else:
                        return res.success(None)
                elif self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs'] == 'one':
                    if len_kwargs == 0:
                        if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                            raise Al_ArgumentError(exception_details)
                        else:
                            return res.success(None)
                    else:
                        return res.success(None)
                    
                elif self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs'] == 'none':
                    if len_kwargs > 0:
                        exception_details['message'] = f"{self.name}() takes no keyword argument"
                        raise Al_ArgumentError(exception_details)
                    else:
                        if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                            raise Al_ArgumentError(exception_details)
                        else:
                            return res.success(None)
                
                elif len_args == 0 and len_kwargs == 0 and self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                    raise Al_ArgumentError(exception_details)
                                 
                elif self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs'] == len_kwargs:
                    return res.success(None)
                else:
                    if len_args == 1 and len_kwargs == 1 and self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required'] and len_args + len_kwargs == self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args']:
                        return res.success(None)
                    else:
                        missing_args = []
                        if 'names' in self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]:
                            for name in self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['names']:
                                missing_args.append(name)
                                if name not in keyword_args:
                                    missing_arg_name = self.make_missing_args(missing_args, len_kwargs)
                                    exception_details['message'] = f"{self.name}() requires {self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs']} {'keyword' if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['kwargs'] == 1 else 'keyword arguments'}: {missing_arg_name} but {len_kwargs} {'was' if len_kwargs == 1 else 'were'} given"
                                    raise Al_ArgumentError(exception_details)
            
            if len_args == self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args'] and len_kwargs != 0:
                for name, value in keyword_args.items():
                    if name not in self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['names']:
                        exception_details['message'] = f"{self.name}() got an unexpected keyword argument '{name}'"
                    else:
                        if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['optional']:
                            if len_args + len_kwargs == self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['total_args']:
                                return res.success(None)
                        else:
                            exception_details['message'] = f"{self.name}() got multiple values for '{name}'"
                            raise Al_ArgumentError(exception_details)                    

            
            if len_args == 0 and len_kwargs == 0 and self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                    raise Al_ArgumentError(exception_details)
            
            
            elif len_args < self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args'] and self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['required']:
                    raise Al_ArgumentError(exception_details)

        
        else:
            if len_args > len_expected:
                raise Al_ArgumentError(exception_details)
            if len_args < len_expected:
                raise Al_ArgumentError(exception_details)


        res.register(self.populate_args(arg_names, args, keyword_args,exec_context))
        return res.success(None)


    def populate_args(self, arg_names, args, keyword_args,exec_context):
        res = RuntimeResult()
        len_args = len(args)
        len_expected = len(arg_names)
        len_kwargs = len(keyword_args)
        if self.name in self.ACCEPTED_KEYWORD_ARGS_CLASS:
            if len_args < len_expected:
                if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['optional']:
                    if self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['args'] == len_args:
                        args.append(self.ACCEPTED_KEYWORD_ARGS_CLASS[self.name]['default'])
        for i in range(len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.setContext(exec_context)
            exec_context.symbolTable.set(arg_name, arg_value)


        return res.success(None)


    def no_visit(self):
        raise Al_NameError({
            'pos_start': self.pos_start,
            'pos_end': self.pos_end,
            'message': f"Name '{self.name}' is not defined",
            'context': self.context,
            'exit': False
        })


    def execute_File(self, exec_context, keyword_args, args):
        res = RuntimeResult()
        file = exec_context.symbolTable.get("file")
        mode = exec_context.symbolTable.get("mode")
        if not isinstance(file, String):
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"File() argument 1 must be of type string",
                "context": self.context,
                'exit': False
            })
        if not isinstance(mode, String):
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"File() argument 2 must be of type string",
                "context": self.context,
                'exit': False
            })

        node = self
        valid_modes = ['r', 'w', 'a', 'r+', 'w+', 'a+']
        if not mode.value in valid_modes:
            raise Al_ValueError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"invalid mode: '{mode.value}'",
                "context": self.context,
                'exit': False
            })
        file_ = handle_file_open(file.value, mode.value, node, exec_context)


        fread = BuiltInFunction("read", exec_context, {
            'file': file_
        })
        fwrite = BuiltInFunction("write", exec_context, {
            'file': file_
        })
        fseek = BuiltInFunction("seek", exec_context, {
            'file': file_
        })
        fclose = BuiltInFunction("close", exec_context, {
            'file': file_,
            'isClosed': Boolean(False)
        })

        file_object = Dict({
            'name': file.value,
            'mode': mode.value,
            'close': fclose,
        })

        if mode.value == 'r':
            file_object.properties['read'] = fread
            file_object.properties['seek'] = fseek
        elif mode.value == 'w':
            file_object.properties['write'] = fwrite
            file_object.properties['seek'] = fseek
        elif mode.value == 'r+':
            file_object.properties['read'] = fread
            file_object.properties['write'] = fwrite
            file_object.properties['seek'] = fseek
        elif mode.value == 'w+':
            file_object.properties['write'] = fwrite
            file_object.properties['read'] = fread
            file_object.properties['seek'] = fseek
        elif mode.value == 'a':
            file_object.properties['write'] = fwrite
            file_object.properties['seek'] = fseek
        elif mode.value == 'a+':
            file_object.properties['write'] = fwrite
            file_object.properties['read'] = fread
            file_object.properties['seek'] = fseek

        file_object.setContext(exec_context).setPosition(node.pos_start, node.pos_end)
        return res.success(file_object)

    execute_File.arg_names = ["file", "mode"]

    def execute_str(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        if object == None:
            return res.success(String(''))
        
        
        if hasattr(object, "value"):
            return res.success(String(str(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        else:
            new_string = String(str(object))
            new_string.setPosition(self.pos_start, self.pos_end).setContext(exec_context)
            return res.success(new_string)

    execute_str.arg_names = ["object"]
    
      
    def execute_float(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
            
        if isinstance(object, Number):
            return res.success(Number(float(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        if isinstance(object, String):
            try:
                return res.success(Number(float(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
            except ValueError:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(object).getType()}' is not a valid type for float()",
                    "context": exec_context,
                    'exit': False
                })
        if isinstance(object, Boolean):
            return res.success(Number(float(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        raise Al_TypeError({
            "pos_start": self.pos_start,
            "pos_end": self.pos_end,
            'message': f"float() argument must be of type number, string or boolean, not {TypeOf(object).getType()}",
            "context": exec_context,
            'exit': False
        })
    
    execute_float.arg_names = ['object']
        
    
    def execute_chr(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        
        check_type(Number, object, "chr() argument must be of type number, not '{}'".format(TypeOf(object).getType()), self.pos_start, self.pos_end, exec_context)
        
        check_type(int, object.value, f"'float' object cannot be interpreted as an integer", self.pos_start, self.pos_end, exec_context)
        try:
            return res.success(String(chr(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        except Exception as e:
            raise Al_ValueError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"invalid literal for chr(): '{object.value}'",
                'context': exec_context,
                'exit': False
            })

    
    execute_chr.arg_names = ['object']
    
    
    
    def execute_ord(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        
        
        check_args(1, args, f"ord() takes exactly 1 argument ({len(args)} given)", self.pos_start, self.pos_end, exec_context)
        
        
        check_type(String, object, "ord() argument must be of type string, not '{}'".format(TypeOf(object).getType()), self.pos_start, self.pos_end, exec_context)
        
        try:
            return res.success(Number(ord(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        except Exception as e:
            raise Al_ValueError({
                'pos_start': self.pos_start,
                'pos_end': self.pos_end,
                'message': f"invalid literal for ord(): '{object.value}'",
                'context': exec_context,
                'exit': False
            })
    
    execute_ord.arg_names = ['object']
    
    def execute_bool(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        if object == None:
            return res.success(Boolean(False))
        if isinstance(object, Boolean):
            return res.success(object)
        if isinstance(object, Number):
            return res.success(Boolean(bool(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        if isinstance(object, String):
            try:
                return res.success(Boolean(bool(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
            except ValueError:
                raise Al_TypeError({
                    "pos_start": self.pos_start,
                    "pos_end": self.pos_end,
                    'message': f"type '{TypeOf(object).getType()}' is not a valid type for bool()",
                    "context": exec_context,
                    'exit': False
                })
        else:
            bool_ = Boolean(bool(object.value)).setPosition(self.pos_start, self.pos_end).setContext(exec_context)
            return res.success(bool_)
    
    execute_bool.arg_names = ['object']
    
    
    def execute_list(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        if object == None:
            return res.success(List([]))
        if isinstance(object, List):
            return res.success(object)
        if isinstance(object, Pair):
            new_list = []
            for element in object.elements:
                new_list.append(element)
            return res.success(List(new_list).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        elif isinstance(object, String):
            new_list = []
            for char in object.value:
                new_list.append(String(char).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
            return res.success(List(new_list).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        elif isinstance(object, Boolean):
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"type '{TypeOf(object).getType()}' is not iterable",
                "context": exec_context,
                'exit': False
            })
        elif isinstance(object, Object) or isinstance(object, Dict) or isinstance(object, Module):
            keys = [key for key in object.value]
            values = [object.value[key] for key in keys]
            new_list = []
            for key in keys:
                if isinstance(key, str):
                    new_list.append(String(key).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
                elif isinstance(key, int):
                    new_list.append(Number(key).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
            return res.success(List(new_list).setPosition(self.pos_start, self.pos_end).setContext(exec_context))


        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"type '{TypeOf(object).getType()}' is not iterable",
                "context": exec_context,
                'exit': False
            })
    
    execute_list.arg_names = ['object']
    
    
    def execute_pair(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        if object == None:
            return res.success(Pair([]))

        if isinstance(object, Pair):
            return res.success(object)

        elif isinstance(object, String):
            new_pair = ()
            for char in object.value:
                new_pair += (String(char).setPosition(self.pos_start, self.pos_end).setContext(exec_context),)
            return res.success(Pair(new_pair).setPosition(self.pos_start, self.pos_end).setContext(exec_context))

        elif isinstance(object, List):
            new_pair = ()
            for value in object.value:
                new_pair += (value,)
            return res.success(Pair(new_pair).setPosition(self.pos_start, self.pos_end).setContext(exec_context))

        elif isinstance(object, Object) or isinstance(object, Dict) or isinstance(object, Module):
            keys = [key for key in object.value]
            values = [object.value[key] for key in keys]
            new_pair = ()
            for key in keys:
                if isinstance(key, str):
                    new_pair += (String(key).setPosition(self.pos_start, self.pos_end).setContext(exec_context),)
                elif isinstance(key, int):
                    new_pair += (Number(key).setPosition(self.pos_start, self.pos_end).setContext(exec_context),)  
            return (Pair(new_pair).setPosition(self.pos_start, self.pos_end).setContext(exec_context))

        else:
            raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"type '{TypeOf(object).getType()}' is not iterable",
                "context": exec_context,
                'exit': False
            })
    
    execute_pair.arg_names = ['object']
    
    
    def execute_dict(self, exec_context, keyword_args, args):
        object = exec_context.symbolTable.get("object")
        res = RuntimeResult()
        if keyword_args is None or len(keyword_args) == 0:
            if object == None:
                return res.success(Dict({}))
            if isinstance(object, String):
                if object.value == "":
                    return res.success(Dict({}).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
                else:
                    raise Al_ArgumentError({
                        "pos_start": self.pos_start,
                        "pos_end": self.pos_end,
                        'message': f"dict expected 1 argument, but got {len(object)}",
                        "context": exec_context,
                        'exit': False
                    })
            elif isinstance(object, Dict) or isinstance(object, Object) or isinstance(object, Module):
                return res.success(object)
               
            return res.success(Dict({}).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
        else:
            return res.success(Dict(keyword_args).setPosition(self.pos_start, self.pos_end).setContext(exec_context))
    
    execute_dict.arg_names = ['object']
    
    

    def generate_new_instance(self, class_args,new_context):
        return Class(self.class_name, class_args, self.inherit_class_name, self.inherited_from, self.properties, self.class_fields_modifiers, new_context)


    def set_method(self, key, value):
        self.properties[key] = value
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


    def has_property(self, property_name):
        return property_name in self.properties


    def get_comparison_eq(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(True if value else False), None


    def get_comparison_ne(self, other):
        value = self.isSame(other)
        return self.setTrueorFalse(False if value else True), None


    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None


    def isSame(self, other):
        if isinstance(other, Class):
            _new_class = f"{{{', '.join([f'{k}: {v}' for k, v in self.properties.items()])}}}"
            other_class = f"{{{', '.join([f'{k}: {v}' for k, v in other.properties.items()])}}}"
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
            for key, value in other.properties.items():
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
        copy = BuiltInClass(self.name, self.properties)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy


    def __repr__(self):
        return self.representation


class Module(Value):
    def __init__(self, name, properties, type_):
        super().__init__()
        self.id = name
        self.name = name
        self.properties = properties if properties is not None else {}
        self.value = self.properties
        self.type_ = type_
        self.get_property = self.get_property
        self.representation =f"<module {self.name}>"
 
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
            keys.append(key)
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
        copy = Module(self.name, self.properties, self.type_)
        copy.setPosition(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy
    
    def __members__(self,args,kwargs,var_name=None):
        if args == None:
            keys = [String(key) for key, value in self.properties.items()]
            return List(keys).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        raise Al_TypeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"'__@members__' is not callable",
                "context": self.context,
                'exit': False
            })
        
         
    def __repr__(self):
        return f"<module '{str(self.name)}', [built-in]>" if self.type_ != None and self.type_ == "builtin" else self.representation


module_methods = {
    '__@members__': Module.__members__,
}


def getproperty(object, property, type_):
    value = False
    if isinstance(object, Dict):
        if type(property).__name__ == "String":
            if property.value in dict_methods:
                if type_ == "check":
                    value = True
            if hasattr(object, "properties"):
                if property.value in object.properties:
                    if type_ == "check":
                        value = True

    return value

# Built-in functions
def handle_sep(values, sep, type_,node, context):
    result = ''
    if isinstance(sep, String):
        seperator = sep.value
        if seperator != '':
            for value in values:
                result += value + seperator
            result = result[:-len(seperator)]
        else:
            result = ''.join(values)
    elif isinstance(sep, NoneType):
        result = ' '.join(values)
    else:
        raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"sep must be none or a string, not {TypeOf(sep).getType()}",
                'context': context,
                'exit': False
            })
    return result


def handle_end(end, type_, node, context):
    result = ''
    if isinstance(end, String):
        end_value = end.value
        escape_chars = {
            '\n': '\\n',
            '\t': '\\t',
            }
        if end != '':
            if end in escape_chars:
                result = escape_chars[end_value]
            else:
                result = end_value
    elif isinstance(end, NoneType):
        result = end.value
    else:
        raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"sep must be none or a string, not {TypeOf(end).getType()}",
                'context': context,
                'exit': False
            })
    return result


def BuiltInFunction_Print(args, node, context,keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    values = []
    v = ''
    for arg in args:
        value = str(arg)
        if isinstance(arg, String):
            value = arg.value
        if isinstance(arg, Bytes):
            value = arg.representation
        else:
            try:
                if value[0] == "'":
                    value = value[1:-1]
            except:
                pass
        values.append(value)

    valid_keywords_args = ["@sep", "@end", "@file"]
    keyword_args_names = []
    if keyword_args != None and len(keyword_args) > 0:
        for keyword_arg in keyword_args:
            name = keyword_arg['name']
            if name in valid_keywords_args:
                keyword_args_names.append(name)
            else:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"print() got an unexpected keyword argument '{keyword_arg['name']}'",
                    'context': context,
                    'exit': False
                })
        # todo: check if keyword args are used at the same time e.g if sep, end and file are being used then we need to handle them e.g print(1,2,3,sep="-",end="\n", file=sys.stdout) the result will be 1-2-3 with a new line at the end of the line and the output will be printed to the stdout
        if len(keyword_args_names) > 0:
            if "@sep" in keyword_args_names and "@end" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@sep" in keyword_args_names and "@end" in keyword_args_names:
                sep_object = [v for v in keyword_args if v['name'] == "@sep"][0]
                sep_value = res.register(interpreter.visit(sep_object['value'], context))
                sep = handle_sep(values, sep_value, "println",node, context)
                end_object = [v for v in keyword_args if v['name'] == "@end"][0]
                end_value = res.register(interpreter.visit(end_object['value'], context))
                end = handle_end(end_value, "print", node, context)
                result = sep + end
                print(result)
            elif "@sep" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@end" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@sep" in keyword_args_names:
                sep_object = [v for v in keyword_args if v['name'] == "@sep"][0]
                sep_value = res.register(interpreter.visit(sep_object['value'], context))
                sep = handle_sep(values, sep_value, "print", node, context)
                result = sep
                print(result)
            elif "@end" in keyword_args_names:
                end_object = [v for v in keyword_args if v['name'] == "@end"][0]
                end_value = res.register(interpreter.visit(end_object['value'], context))
                end = handle_end(end_value, "print", node, context)
                result = ' '.join(values) + end
                print(result)
            elif "@file" in keyword_args_names:
                pass





    else:
        sep = ' '
        end = '\n'
        result = sep.join(values) + end
        sys.stdout.write(result)
    return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end))


def BuiltInFunction_PrintLn(args, node, context,keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    values = []
    v = ''
    for arg in args:
        value = str(arg)
        if isinstance(arg, String):
            value = arg.value
        if isinstance(arg, Bytes):
            value = arg.representation
        else:
            try:
                if value[0] == "'":
                    value = value[1:-1]
            except:
                pass
        values.append(value)
    valid_keywords_args = ["@sep", "@end", "@file"]
    keyword_args_names = []
    if keyword_args != None and len(keyword_args) > 0:
        for keyword_arg in keyword_args:
            name = keyword_arg['name']
            if name in valid_keywords_args:
                keyword_args_names.append(name)
            else:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"print() got an unexpected keyword argument '{keyword_arg['name']}'",
                    'context': context,
                    'exit': False
                })
        # todo: check if keyword args are used at the same time e.g if sep, end and file are being used then we need to handle them e.g print(1,2,3,sep="-",end="\n", file=sys.stdout) the result will be 1-2-3 with a new line at the end of the line and the output will be printed to the stdout
        if len(keyword_args_names) > 0:
            if "@sep" in keyword_args_names and "@end" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@sep" in keyword_args_names and "@end" in keyword_args_names:
                sep_object = [v for v in keyword_args if v['name'] == "@sep"][0]
                sep_value = res.register(interpreter.visit(sep_object['value'], context))
                sep = handle_sep(values, sep_value, "println",node, context)
                end_object = [v for v in keyword_args if v['name'] == "@end"][0]
                end_value = res.register(interpreter.visit(end_object['value'], context))
                end = handle_end(end_value, "println",node, context)
                result = sep + end
                sys.stdout.write(result)
            elif "@sep" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@end" in keyword_args_names and "@file" in keyword_args_names:
                pass
            elif "@sep" in keyword_args_names:
                sep_object = [v for v in keyword_args if v['name'] == "@sep"][0]
                sep_value = res.register(interpreter.visit(sep_object['value'], context))
                sep = handle_sep(values, sep_value, "println",node, context)
                result = sep
                sys.stdout.write(result)
            elif "@end" in keyword_args_names:
                end_object = [v for v in keyword_args if v['name'] == "@end"][0]
                end_value = res.register(interpreter.visit(end_object['value'], context))
                end = handle_end(end_value, "println",node, context)
                result = ' '.join(values) + end
                sys.stdout.write(result)
            elif "@file" in keyword_args_names:
                pass


    


    else:
        sep = ''
        end = '\n'
        file = None
        result = sep + end.join(values) + end
        sys.stdout.write(result)
    return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end))


def BuiltInFunction_Len(args, node, context, keyword_args=None):
        res = RuntimeResult()
        if keyword_args != None and len(keyword_args) > 0:
            for key in keyword_args:
                name = key['name']
                if name:
                    raise Al_ArgumentError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"len() takes no keyword argument",
                        'context': context,
                        'exit': False
                    })
        if len(args) > 1:
            raise Al_ArgumentError({'pos_start': node.pos_start, 'pos_end': node.pos_end, 'message': f"{len(args)} arguments passed, len() requires 1 argument", 'context': context, 'exit': False})

        value = args[0]
        if isinstance(value, Number):
            raise Al_RuntimeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(value).getType()}' is not supported",
                'context': context,
                'exit': False
            })
        if isinstance(value, List):
            return res.success(Number(len(value.value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        if isinstance(value, String):
            return res.success(Number(len(value.value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        if isinstance(value, Pair):
            return res.success(Number(len(value.value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        if isinstance(value, Object) or isinstance(value, Module):
            return res.success(Number(len(value.value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        if isinstance(value, Dict):
            return res.success(Number(len(value.value)).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(value).getType()}' has no len()",
                'context': context,
                'exit': False
            })


def BuiltInFunction_Input(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"input() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but input() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        })
    if len(args) == 0:
        try:
            input_value = input()
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
    if len(args) == 1:
        if isinstance(args[0], String):
            try:
                input_value = input(args[0].value)
            except KeyboardInterrupt:
                raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
                })
            return res.success(String(input_value).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not a valid type for input()",
                "context": context,
                'exit': False
            })


def BuiltInFunction_InputInt(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"inputInt() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_RuntimeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputInt() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        })
    if len(args) == 0:
        try:
            input_value = int(input())
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
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
                    raise Al_KeyboardInterrupt({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"KeyboardInterrupt",
                        'context': context,
                        'exit': False
                   })
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not a valid type for inputInt()",
                "context": context,
                'exit': False
            })


def BuiltInFunction_InputFloat(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"inputFloat() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_RuntimeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputFloat() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        })
    if len(args) == 0:
        try:
            input_value = float(input())
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"KeyboardInterrupt",
                        'context': context,
                        'exit': False
                   })
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
                    raise Al_KeyboardInterrupt({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"KeyboardInterrupt",
                        'context': context,
                        'exit': False
                   })
            return res.success(Number(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not a valid type for inputFloat()",
                "context": context,
                'exit': False
            })


def BuiltInFunction_InputBool(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"inputBool() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but inputBool() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        })
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
                    raise Al_KeyboardInterrupt({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"KeyboardInterrupt",
                        'context': context,
                        'exit': False
                   })
            return res.success(Boolean(number).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not a valid type for inputBool()",
                "context": context,
                'exit': False
            })


def BuiltInFunction_Append(args, node,context, keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"append() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2 or len(args) < 2:
        raise Al_ArgumentError({'pos_start': node.pos_start, 'pos_end': node.pos_end, 'message': f"{len(args)} arguments passed, append() requires 2 arguments", 'context': context, 'exit': False})
    list_ = args[0]
    value = args[1]
    if isinstance(list_, List):
        list_.elements.append(value)
        return res.success(List(list_.elements).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"first argument to 'append' must be a list.",
            'context': context,
            'exit': False
        })


def BuiltInFunction_Pop(args, node, context, keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"pop() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2 or len(args) < 2:
        raise Al_ArgumentError({'pos_start': node.pos_start, 'pos_end': node.pos_end, 'message': f"{len(args)} arguments passed, pop() requires 2 arguments", 'context': context, 'exit': False})
    list_ = args[0]
    index = args[1]
    if isinstance(list_, List):
        if isinstance(index, Number):
            try:
                list_.elements.pop(index.value)
                return res.success(List(list_.elements).setPosition(node.pos_start, node.pos_end).setContext(context))
            except:
                raise Al_IndexError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"element at index {index.value} could not be removed from list because index is out of bounds",
                    'context': context,
                    'exit': False
                })
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"second argument to 'pop' must be a number.",
                'context': context,
                'exit': False
            })
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"first argument to 'pop' must be a list.",
            'context': context,
            'exit': False
        })


def BuiltInFunction_Extend(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"extend() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2 or len(args) < 2:
        raise Al_ArgumentError({'pos_start': node.pos_start, 'pos_end': node.pos_end, 'message': f"{len(args)} arguments passed, extend() requires 2 arguments", 'context': context, 'exit': False})
    list_ = args[0]
    value = args[1]
    if isinstance(list_, List):
        if isinstance(value, List):
            list_.elements.extend(value.elements)
            return res.success(List(list_.elements).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"second argument to 'extend' must be a list.",
                'context': context,
                'exit': False
            })
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"first argument to 'extend' must be a list.",
            'context': context,
            'exit': False
        })


def BuiltInFunction_Remove(args, node, context, keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"remove() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2 or len(args) < 2:
        raise Al_ArgumentError({'pos_start': node.pos_start, 'pos_end': node.pos_end, 'message': f"{len(args)} arguments passed, remove() requires 2 arguments", 'context': context, 'exit': False})
    list_ = args[0]
    value = args[1]
    if isinstance(list_, List):
        if isinstance(value, Number):
            try:
                list_.elements.remove(value.value)
                return res.success(List(list_.elements).setPosition(node.pos_start, node.pos_end).setContext(context))
            except:
                raise Al_IndexError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"element at index {value.value} could not be removed from list because index is out of bounds",
                    'context': context,
                    'exit': False
                })
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"second argument to 'remove' must be a number.",
                'context': context,
                'exit': False
            })
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"first argument to 'remove' must be a list.",
            'context': context,
            'exit': False
        })


def Range(start, end, step):
    return List([Number(i) for i in range(start, end, step)])


def BuiltInFunction_Range(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"range() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    start = 0
    end = 0
    step = 0
    if len(args) > 3:
        raise Al_RuntimeError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"{len(args)} arguments given, but range() takes 1 or 3 arguments",
            'context': context,
            'exit': False
        })
    if len(args) == 1:
        start = 0
        if isinstance(args[0], Number):
            end = args[0].value
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not a valid type for range()",
                'context': context,
                'exit': False
            })
        step = 1
    elif len(args) == 3:
        if isinstance(args[0], Number) and isinstance(args[1], Number) and isinstance(args[2], Number):
            start = args[0].value
            end = args[1].value
            step = args[2].value
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"range() arguments must be of type Number",
                'context': context,
                'exit': False
            })
    elif len(args) == 2:
        if isinstance(args[0], Number) and isinstance(args[1], Number):
            start = args[0].value
            end = args[1].value
            step = 1
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' and '{TypeOf(args[1]).getType()}' are not valid types for range()",
                'context': context,
                'exit': False
            })
    if step == 0:
        raise Al_RuntimeError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"step cannot be 0",
            'context': context,
            'exit': False
        })
    if step > 0:
        if start > end:
            raise Al_RuntimeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"start cannot be greater than end",
                'context': context,
                'exit': False
            })
    elif step < 0:
        if start < end:
            raise Al_RuntimeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"start cannot be less than end",
                'context': context,
                'exit': False
            })
    # check if range is called from a for loop
    
    return res.success(Range(start, end, step).setPosition(node.pos_start, node.pos_end).setContext(context))
    


def BuiltInFunction_Zip(args, node, context,keyword_args=None):
    res = RuntimeResult()
    # zip takes any number of iterables as arguments and returns a list of tuples, where the i-th tuple contains the i-th element from each of the argument sequences or iterables.
    # zip can accept multiple iterables, but the resulting list is truncated to the length of the shortest input iterable.


def BuiltInFunction_Max(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"max() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but max() takes 2 arguments",
            "context": context,
            'exit': False
        })

    if isinstance(args[0], Number) and isinstance(args[1], Number):
        return res.success(Number(max(args[0].value, args[1].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Min(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"min() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but min() takes 2 arguments",
            "context": context,
            'exit': False
        })

    if isinstance(args[0], Number) and isinstance(args[1], Number):
        return res.success(Number(min(args[0].value, args[1].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })


def BuiltInFunction_is_finite(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"is_finite() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) != 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but is_finite() takes 1 argument",
            "context": context,
            'exit': False
        })


    if isinstance(args[0], Number):
        # custom implementation of is_finite()
        def is_finite(num):
            return num == num and num != float('inf') and num != float('-inf')
        return res.success(Boolean(is_finite(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Sorted(args, node, context,keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    key = None
    reverse = False
    if keyword_args != None and len(keyword_args) > 0:
        for k in keyword_args:
            name = k['name']
            if name:
                if name == 'reverse':
                    value = res.register(interpreter.visit(k['value'], context))
                    # if k['name'] == 'key':
                    #     check_type(Function, value, f"type '{TypeOf(value).getType()}' is not a function", node.pos_start, node.pos_end, context)
                    #     key = value
                    if k['name'] == 'reverse':
                        if isinstance(value, Boolean):
                            if value.value == "true":
                                reverse = True
                        elif isinstance(value, Number):
                            if isinstance(value.value, int):
                                reverse = True
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"expected an integer, got (type '{TypeOf(value).getType()}')",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"expected an integer, got (type '{TypeOf(value).getType()}')",
                                'context': context,
                                'exit': False
                            })
                        
                else:
                    raise Al_ArgumentError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"sorted() got an unexpected keyword argument '{name}'",
                        'context': context,
                        'exit': False
                    })
    res = RuntimeResult()
    
    if len(args) > 2 or len(args) < 1:
            raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but sorted() takes 1 to 2 arguments",
            "context": context,
            'exit': False
        })
    
    
    if is_iterable(args[0]) == False:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })
        
   
        
    # if len(args) == 2:
    #     check_type(Function, args[1], f"type '{TypeOf(args[1]).getType()}' is not a function", node.pos_start, node.pos_end, context)
    #     key = value  
        
        
          
    elif len(args) == 2:
        if isinstance(args[1], Boolean):
            if args[1].value == "true":
                reverse = True
            elif isinstance(args[1], Number):
                if isinstance(args[1].value, int):
                    reverse = True
                else:
                    raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"expected an integer, got (type '{TypeOf(args[1]).getType()}')",
                        'context': context,
                        'exit': False
                    })
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"expected an integer, got (type '{TypeOf(args[1]).getType()}')",
                'context': context,
                'exit': False
            })
                
                
                
                
                
    if isinstance(args[0], List) or isinstance(args[0], Pair):
        if len(args[0].elements) == 0:
            if isinstance(args[0], List):
                return res.success(List([]).setPosition(node.pos_start, node.pos_end).setContext(context))
            else:
                return res.success(Pair([]).setPosition(node.pos_start, node.pos_end).setContext(context))
            
            
        elements = args[0].elements
        def is_all_strings(elements):
            for element in elements:
                if not isinstance(element, String):
                    return False
            return True
        def is_all_numbers(elements):
            for element in elements:
                if not isinstance(element, Number):
                    return False
            return True
        def is_all_booleans(elements):
            for element in elements:
                if not isinstance(element, Boolean):
                    return False
            return True
                
        
        if is_all_strings(elements):
            sorted_elements = sort_list_pair(elements, key, reverse)
            value = List(sorted_elements).setContext(context).setPosition(node.pos_start, node.pos_end)
            return value
        elif is_all_numbers(elements):
            sorted_elements = sort_list_pair(elements, key, reverse)
            value = List(sorted_elements).setContext(context).setPosition(node.pos_start, node.pos_end)
            return value
        elif is_all_booleans(elements):
            sorted_elements = sort_list_pair(elements, key, reverse)
            value = List(sorted_elements).setContext(context).setPosition(node.pos_start, node.pos_end)
            return value
        else:
            for i in range(len(elements)):
                for j in range(len(elements)):
                    if type(elements[i]).__name__ != type(elements[j]).__name__:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"'>' not supported between instances of '{TypeOf(elements[j]).getType()}' and '{TypeOf(elements[i]).getType()}'",
                            'context': context,
                            'exit': False
                        }) 
   
    if isinstance(args[0], Module) or isinstance(args[0], Object):
        raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"cannot iterate over {'module' if isinstance(args[0], Module) else 'object'} object",
                "context": context,
                'exit': False
            })
   
    if isinstance(args[0], Dict):
        if len(args[0].properties) == 0:
            return res.success(Dict([]).setPosition(node.pos_start, node.pos_end).setContext(context))
    
        keys = [key for key, _ in args[0].properties.items()]
        
        def is_all_strings(keys):
            for key in keys:
                if not isinstance(key, str):
                    return False
            return True
        def is_all_numbers(keys):
            for key in keys:
                if not isinstance(key, int):
                    return False
            return True
        
                
        
        if is_all_strings(keys):
            sorted_keys = sort_dict(args[0].properties,keys, key, reverse)
            value = List(sorted_keys).setContext(context).setPosition(node.pos_start, node.pos_end)
            return value
        elif is_all_numbers(keys):
            sorted_keys = sort_dict(args[0].properties,keys, key, reverse)
            value = Dict(sorted_keys).setContext(context).setPosition(node.pos_start, node.pos_end)
            return value
        
        else:
            for i in range(len(keys)):
                for j in range(len(keys)):
                    if type(keys[i]).__name__ != type(keys[j]).__name__:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"'>' not supported between instances of '{TypeOf(keys[j]).getType()}' and '{TypeOf(keys[i]).getType()}'",
                            'context': context,
                            'exit': False
                        }) 
    
    if isinstance(args[0], String):
        sorted_string = sort_string(args[0].value, key, reverse)
        new_list = []
        for char in sorted_string:
            new_list.append(String(char).setPosition(node.pos_start, node.pos_end).setContext(context))
        return res.success(List(new_list).setPosition(node.pos_start, node.pos_end).setContext(context)) 


def BuiltInFunction_Substr(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"substr() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 3:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but substr() takes 3 arguments",
            "context": context,
            'exit': False
        })

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
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Reverse(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"reverse() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but reverse() takes 1 argument",
            "context": context,
            'exit': False
        })

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
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Format(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"format() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    string = args[0].value
    values_list = args[1].value
    regex = Regex().compile('{(.*?)}')
    matches = regex.match(string)


def BuiltInFunction_Typeof(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"typeof() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but typeof() takes 1 argument",
            "context": context,
            'exit': False
        })

    if len(args) == 0:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"typeof() takes 1 argument",
            "context": context,
            'exit': False
        })
    return res.success(String(TypeOf(args[0]).getType()).setPosition(node.pos_start, node.pos_end).setContext(context))


def  getInstance(type1, type2):
    getType = type(type2).__name__
    if isinstance(type1, Number):
        if isinstance(type1.value, int) and type2.name == "int":
            return True
        elif isinstance(type1.value, float) and type2.name == "float":
            return True
    if isinstance(type1, String):
        if type2.name == "str":
            return True
    if isinstance(type1, Boolean):
        if type2.name == "bool":
            return True
    if isinstance(type1, List):
        if type2.name == "list":
            return True
    if isinstance(type1, Pair):
        if type2.name == "pair":
            return True
    if isinstance(type1, Dict):
        if type2.name == "dict":
            return True
    if isinstance(type1, BuiltInClass):
        if type2.name == "builtin":
            return True
    if isinstance(type1, Module):
        if type2.name == "module":
            return True
   
    return False


def BuiltInFunction_IsinstanceOf(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"isinstanceof() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) == 1 or len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but isinstance() takes 2 arguments",
            "context": context,
            'exit': False
        })

    if len(args) == 0:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"isinstance() takes 2 arguments",
            "context": context,
            'exit': False
        })


    if not isinstance(args[1], BuiltInClass):
        if isinstance(args[1], Class):
            if isinstance(args[0], Class):
                return res.success(Boolean(args[0].name == args[1].name).setPosition(node.pos_start, node.pos_end).setContext(context))
            else:
                return res.success(Boolean(False).setPosition(node.pos_start, node.pos_end).setContext(context))
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"isisnstance() argument 2 must be a type",
                "context": context,
                'exit': False
            })
    else:
        if not args[1].name in types:
             raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"isisnstance() argument 2 must be a type",
                "context": context,
                'exit': False
            })
        return res.success(Boolean(getInstance(args[0], args[1])).setPosition(node.pos_start, node.pos_end).setContext(context))


def BuiltInFunction_hasprop(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"hasprop() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()

    if len(args) == 0:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"hasprop() takes 2 arguments",
            "context": context,
            'exit': False
        })

    elif len(args) == 1:
        raise Al_RuntimeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"hasprop() takes 2 arguments",
            "context": context,
            'exit': False
        })

    elif len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but hasprop() takes 2 arguments",
            "context": context,
            'exit': False
        })

    else:
        if not isinstance(args[1], String):
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"hasprop() property name must be string",
                "context": context,
                'exit': False
            })
        object_ = args[0]
        object_type = TypeOf(object_).getType()
        property_to_check = args[1]
        value = getproperty(object_, property_to_check, "check")
        return res.success(Boolean(value).setPosition(node.pos_start, node.pos_end).setContext(context))


def BuiltInFunction_Line(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"line() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) == 0:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"line() takes at least 1 argument",
            "context": context,
            'exit': False
        })
    if len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but line() takes 1 argument",
            "context": context,
            'exit': False
        })

    if isinstance(args[0], Number):
        print(f"{args[0].value}:-> ")

    elif isinstance(args[0], String):
        print(f"{args[0].value}:-> ")

    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"line() argument must be number",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Clear(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"clear() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) > 0:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but clear() takes no argument",
            "context": context,
            'exit': False
        })
    if len(args) == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        return res.success(None)


def BuiltInFunction_Delay(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"delay() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but delay() takes 1 argument",
            "context": context,
            'exit': False
        })

    if isinstance(args[0], Number):
        time.sleep(args[0].value)
        return res.success(None)
    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"delay() argument must be number",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Require(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"require() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    error = {
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                "message": "",
                "context": context,
                "exit": False
            }
    if len(args) == 0 or len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but require() takes 1 argument",
            "context": context,
            'exit': False
        })


    if isinstance(args[0], String):
        module_path = args[0].value
        if module_path.endswith(".ald"):
            module_path = module_path[:-4]
        else:
            if not module_path in builtin_modules:
                module_path = module_path + ".ald"

        module = Program.runFile(module_path)
        if module == None:
            if module == None:
                if module_path in builtin_modules:
                    if  context.symbolTable.modules.is_module_in_members(module_path):
                        error['message'] = "Module '{}' already imported".format(module_path)
                        raise Al_ImportError(error)
                    else:
                        try:
                            path = f"./lib/{module_path}/@{module_path}.ald"
                            module = builtin_modules[module_path](path)
                            module_object = Program.makeModule(module_path, module, context, node.pos_start, node.pos_end)
                            return res.success(module_object)
                        except RecursionError:
                                error['message'] = f"cannot import name '{module_path}' (most likely due to a circular import)"
                                raise Al_ImportError(error)
                        except FileNotFoundError:
                            error['message'] = f"cannot import name '{module_path}' (file does not exist)"
                            raise Al_ImportError(error)
                else:
                    error['message'] = "Module '{}' not found".format(module_path)
                    raise Al_ModuleNotFoundError(error)

        else:
            if  context.symbolTable.modules.is_module_in_members(module_path):
                error['message'] = "Module '{}' already imported".format(module_path)
                raise Al_ImportError(error)
            else:
                module_object = Program.makeModule(module_path, module, context, node.pos_start, node.pos_end)
                return res.success(module_object)


    else:
        raise Al_TypeError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"require() argument must be string",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Enumerate(args, node, context,keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    valid_keywords_args = ["start"]
    keyword_args_names = []
    keywords = {}
    if len(args) == 0:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"enumerate() takes at least 1 argument",
            'context': context,
            'exit': False
        })
    if len(args) > 2:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"enumerate() takes at most 2 arguments",
            'context': context,
            'exit': False
        })
    if keyword_args != None and len(keyword_args) > 0:
        for keyword_arg in keyword_args:
            name = keyword_arg['name']
            value = res.register(interpreter.visit(keyword_arg['value'], context))
            if not isinstance(value, Number):
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"type '{TypeOf(value).getType()}' cannot be interpreted as an integer",
                    'context': context,
                    'exit': False
                })
            value = value.value
            if not isinstance(value, int):
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"type '{TypeOf(value).getType()}' cannot be interpreted as an integer",
                    'context': context,
                    'exit': False
                })
            keywords[name] = value
            if name in valid_keywords_args:
                keyword_args_names.append(name)
            else:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"enumerate() got an unexpected keyword argument '{keyword_arg['name']}'",
                    'context': context,
                    'exit': False
                })
    
        
    if len(args) == 1:
        if isinstance(args[0], List) or isinstance(args[0], Pair): 
            if len(keyword_args_names) == 0:
                dict_enumerate = {}
                for i in range(len(args[0].elements)):
                    key = Number(i)
                    value = args[0].elements[i]
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            elif len(keyword_args_names) == 1:
                if isinstance(args[0], List) or isinstance(args[0], Pair):
                    dict_enumerate = {}
                    for i in range(len(args[0].elements)):
                        start_value = keywords["start"]
                        key = Number(i + start_value)
                        value = args[0].elements[i]
                        dict_enumerate[key] = value
                    enumerate_object = Dict(dict_enumerate)
                    return res.success(enumerate_object)
        elif isinstance(args[0], String):
            if len(keyword_args_names) == 0:
                dict_enumerate = {}
                for i in range(len(args[0].value)):
                    key = Number(i)
                    value = String(args[0].value[i])
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            elif len(keyword_args_names) == 1:
                if isinstance(args[0], String):
                    dict_enumerate = {}
                    for i in range(len(args[0].value)):
                        start_value = keywords["start"]
                        key = Number(i + start_value)
                        value = String(args[0].value[i])
                        dict_enumerate[key] = value
                    enumerate_object = Dict(dict_enumerate)
                    return res.success(enumerate_object)
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Module):
            if len(keyword_args_names) == 0:
                dict_enumerate = {}
                object_key = -1
                for key in args[0].properties:
                    value_key = key
                    object_key += 1
                    key = Number(object_key)
                    value = Number(value_key)
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            elif len(keyword_args_names) == 1:
                if isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Module):
                    dict_enumerate = {}
                    object_key = -1
                    for key in args[0].properties:
                        start_value = keywords["start"]
                        value_key = key
                        object_key += 1
                        key = Number(object_key + start_value)
                        value = Number(value_key)
                        dict_enumerate[key] = value
                    enumerate_object = Dict(dict_enumerate)
                    return res.success(enumerate_object)
                    
                    
                               
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
                'context': context,
                'exit': False
            })
    elif len(args) == 2:
        if isinstance(args[0], List) or isinstance(args[0], Pair):
            if isinstance(args[1], Number):
                dict_enumerate = {}
                for i in range(len(args[0].elements)):
                    start_value = args[1].value
                    if not isinstance(start_value, int):
                       raise Al_TypeError({
                           'pos_start': node.pos_start,
                           'pos_end': node.pos_end,
                           'message': f"type '{TypeOf(start_value).getType()}' cannot be interpreted as an integer",
                           'context': context,
                           'exit': False
                          })
                    key = Number(i + start_value)
                    value = args[0].elements[i]
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            else:
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"type '{TypeOf(args[1]).getType()}' cannot be interpreted as an integer",
                    'context': context,
                    'exit': False
                })
        elif isinstance(args[0], String):
            if isinstance(args[1], Number):
                dict_enumerate = {}
                for i in range(len(args[0].value)):
                    start_value = args[1].value
                    if not isinstance(start_value, int):
                          raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"type '{TypeOf(start_value).getType()}' cannot be interpreted as an integer",
                                'context': context,
                                'exit': False
                            })
                    key = Number(i + start_value)
                    value = String(args[0].value[i])
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            else:
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"type '{TypeOf(args[1]).getType()}' cannot be interpreted as an integer",
                    'context': context,
                    'exit': False
                })
        elif isinstance(args[0], Dict) or isinstance(args[0], Object) or isinstance(args[0], Module):
            if isinstance(args[1], Number):
                dict_enumerate = {}
                object_key = -1
                for key in args[0].properties:
                    start_value = args[1].value
                    if not isinstance(start_value, int):
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"type '{TypeOf(start_value).getType()}' cannot be interpreted as an integer",
                                'context': context,
                                'exit': False
                            })
                    value_key = key
                    object_key += 1
                    key = Number(object_key + start_value)
                    value = Number(value_key)
                    dict_enumerate[key] = value
                enumerate_object = Dict(dict_enumerate)
                return res.success(enumerate_object)
            else:
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"type '{TypeOf(args[1]).getType()}' cannot be interpreted as an integer",
                    'context': context,
                    'exit': False
                })
            
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"type '{TypeOf(args[0]).getType()}' is not iterable",
                'context': context,
                'exit': False
            })
   
   
def BuiltInFunction_Freeze(args, node, context, keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    if len(args) != 0:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"freeze() takes no argument but {len(args)} were given",
            'context': context,
            'exit': False
        })
        
    
    if len(keyword_args) == 0:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"missing keyword argument for freeze()",
            'context': context,
            'exit': False
        })   
        
    keywords = {}
    
    for key in keyword_args:
        name = key['name']
        value = res.register(interpreter.visit(key['value'], context))
        keywords = {
            'name': name,
            'value': value
        }
        
    if len(keywords) != 2:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"too many keyword arguments for freeze()",
            'context': context,
        })
    
    for name, value in keywords.items():
        var_name = context.symbolTable.get(name)
        print(var_name)
    
    
def handle_file_open(file_name, mode, node, context):
    res = RuntimeResult()
    if mode == 'r':
        try:
            file = open(file_name, 'r')
            return file
        except FileNotFoundError:
            raise Al_FileNotFoundError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"File '{file_name}' not found",
                "context": context,
                'exit': False
            })
        except PermissionError:
            raise Al_PermissionError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"permission denied for file '{file_name}'",
                "context": context,
                'exit': False
            })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })
    elif mode == 'r+':
        try:
            file = open(file_name, 'r+')
            return file
        except FileNotFoundError:
            raise Al_FileNotFoundError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"File '{file_name}' not found",
                "context": context,
                'exit': False
            })
        except PermissionError:
            raise Al_PermissionError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"permission denied for file '{file_name}'",
                "context": context,
                'exit': False
            })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })
    elif mode == 'w':
        try:
            file = open(file_name, 'w')
            return file
        except PermissionError:
           raise Al_PermissionError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"unable to write to file '{file_name}' due to permission error",
                "context": context,
                'exit': False
            })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })
    elif mode == 'w+':
        try:
            file = open(file_name, 'w+')
            return file
        except PermissionError:
            raise Al_PermissionError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"unable to write to file '{file_name}' due to permission error",
                "context": context,
                'exit': False
            })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })
    elif mode == 'a':
        try:
            file = open(file_name, 'a')
            return file
        except PermissionError:
           raise Al_PermissionError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"unable to write to file '{file_name}' due to permission error",
                "context": context,
                'exit': False
            })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })
    elif mode == 'a+':
        try:
            file = open(file_name, 'a+')
            return file
        except PermissionError:
           raise Al_PermissionError({
               "pos_start": node.pos_start,
               "pos_end": node.pos_end,
               'message': f"unable to write to file '{file_name}' due to permission error",
               "context": context,
               'exit': False
           })
        except:
            raise Al_IOError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"Unexpected error while opening file '{file_name}'",
                "context": context,
                'exit': False
            })


def handle_file_read(file, node, context):
    res = RuntimeResult()
    try:
        if file.closed:
            raise Al_ValueError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"I/O operation on closed file",
                "context": context,
                'exit': False
            })
        else:
            content = file.read()
            return res.success(String(content))
    except:
        raise Al_IOError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"unable to read file",
            "context": context,
            'exit': False
        })


def handle_file_write(file, data, node, context):
    res = RuntimeResult()
    try:
        if file.closed:
            raise Al_ValueError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"I/O operation on closed file",
                "context": context,
                'exit': False
            })
        else:
            content = file.write(data)
            return res.success(Dict({
                'size': Number(content),
                'text': String(data),
                'success': Boolean(True)
            }))
    except:
        raise Al_IOError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"unable to write file",
            "context": context,
            'exit': False
        })


def handle_file_seek(file, offset, whence, node, context):
    res = RuntimeResult()
    try:
        if file.closed:
            raise Al_ValueError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"I/O operation on closed file",
                "context": context,
                'exit': False
            })

        else:
            file.seek(offset, whence)
            return res.success(None)
    except:
        raise Al_IOError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"unable to seek file to {offset} with whence {whence}",
            "context": context,
            'exit': False
        })


def handle_file_close(file, node, context):
    res = RuntimeResult()
    file.close()
    value = NoneType('none')
    return res.success(value)


def handle_std_in(node, context):
    print("std_input")


def BuiltInFunction_Exit(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"exit() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    res = RuntimeResult()
    if len(args) == 0:
        sys.exit(0)
    elif len(args) > 1:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"{len(args)} arguments given, but exit() takes 0 or 1 argument(s)",
            "context": context,
            'exit': False
        })
    if isinstance(args[0], Number):
        if args[0].value == 0:
            sys.exit(0)
        elif args[0].value == 1:
            sys.exit(1)
        else:
            raise Al_ValueError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{args[0].value} is not a valid exit code",
                "context": context,
                'exit': False
            })
    else:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"exit() argument must be number",
            "context": context,
            'exit': False
        })


def BuiltInFunction_Random(args, node, context,keyword_args=None):
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            if name:
                raise Al_ArgumentError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"random() takes no keyword argument",
                    'context': context,
                    'exit': False
                })
    print(args)


def BuiltInFunction_StdInRead(args, node, context,keyword_args=None):
    res = RuntimeResult()
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            raise Al_ArgumentError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"@std_in_read() got an unexpected keyword argument '{name}'",
                'context': context,
                'exit': False
            })
    if len(args) == 0:
        content = ''
        res = RuntimeResult()
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
        except:
            raise Al_IOError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"unable to read from stdin",
                'context': context,
                'exit': False
            })

        return res.success(String(content).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"{len(args)} arguments given, but std_in_read() takes 0 argument(s)",
            'context': context,
            'exit': False
        })


def BuiltInFunction_StdInReadLine(args, node, context,keyword_args=None):
    res = RuntimeResult()
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            raise Al_ArgumentError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"@std_in_readline() got an unexpected keyword argument '{name}'",
                'context': context,
                'exit': False
            })
    if len(args) == 0:
        content = ''
        res = RuntimeResult()
        try:
            content = sys.stdin.readline()
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
        except:
            raise Al_IOError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"unable to read from stdin",
                'context': context,
                'exit': False
            })

        return res.success(String(content).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"{len(args)} arguments given, but std_in_read() takes 0 argument(s)",
            'context': context,
            'exit': False
        })


def BuiltInFunction_StdInReadLines(args, node, context,keyword_args=None):
    res = RuntimeResult()
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            raise Al_ArgumentError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"@std_in_readlines() got an unexpected keyword argument '{name}'",
                'context': context,
                'exit': False
            })

    if len(args) == 0:
        content = ''
        res = RuntimeResult()
        try:
            content = sys.stdin.readlines()
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
        except:
            raise Al_IOError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"unable to read from stdin",
                'context': context,
                'exit': False
            })

        return res.success(String(content).setPosition(node.pos_start, node.pos_end).setContext(context))
    else:
        raise Al_ArgumentError({
            'pos_start': node.pos_start,
            'pos_end': node.pos_end,
            'message': f"{len(args)} arguments given, but std_in_read() takes 0 argument(s)",
            'context': context,
            'exit': False
        })


def BuiltInFunction_StdOutWrite(args, node, context,keyword_args=None):
    res = RuntimeResult()
    if keyword_args != None and len(keyword_args) > 0:
        for key in keyword_args:
            name = key['name']
            raise Al_ArgumentError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"@std_out_write() got an unexpected keyword argument '{name}'",
                'context': context,
                'exit': False
            })

    if len(args) == 1:
        if isinstance(args[0], String):
            content = args[0].value
            res = RuntimeResult()
            try:
                sys.stdout.write(content)
            except KeyboardInterrupt:
                raise Al_KeyboardInterrupt({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"KeyboardInterrupt",
                    'context': context,
                    'exit': False
                })
            except:
                raise Al_IOError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"unable to write to stdout",
                    'context': context,
                    'exit': False
                })
            return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end))
        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"@std_out_write() argument must be of type string, but got {TypeOf(args[0]).getType()}",
                'context': context,
                'exit': False
            })


def BuiltInFunction_StdOutWriteLines(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysPath(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysArgv(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysExit(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysVersion(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysPlatform(args, node, context,keyword_args=None):
    pass


def BuiltInFunction_SysExec(args, node, context,keyword_args=None):
    pass

builtin_variables = {
    'Math': {
        'random': BuiltInFunction_Random,
    },
}
# Built-in class



def BuiltInClass_Exception(args, node, context, type, name=None):
    res = RuntimeResult()

    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError('Exception',{
            'name': 'Exception',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'Exception' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_Exception('Exception',{
                'name': name if name else 'Exception',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_Exception('Exception',{
                'name': name if name else 'Exception',
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but Exception takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        return BuiltInClass.Exception


def BuiltInClass_RuntimeError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'RuntimeError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'RuntimeError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_RuntimeError({
                'name': 'RuntimeError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_RuntimeError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String("RuntimeError"),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but RuntimeError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("RuntimeError", Dict({'name': String("RuntimeError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("RuntimeError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_NameError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'NameError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_NameError({
                'name': 'NameError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_NameError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('NameError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but NameError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("NameError", Dict({'name': String("NameError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("NameError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_ArgumentError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'ArgumentError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_ArgumentError({
                'name': 'ArgumentError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_ArgumentError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('ArgumentError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but ArgumentError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("ArgumentError", Dict({'name': String("ArgumentError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("ArgumentError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_TypeError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'TypeError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'TypeError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_TypeError({
                'name': 'TypeError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_TypeError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('TypeError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but TypeError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("TypeError", Dict({'name': String("TypeError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("TypeError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_IndexError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'IndexError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_IndexError({
                'name': 'IndexError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_IndexError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('IndexError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but IndexError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("IndexError", Dict({'name': String("IndexError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("IndexError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_ValueError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'ValueError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_ValueError({
                'name': 'ValueError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_ValueError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('ValueError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but ValueError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("ValueError", Dict({'name': String("ValueError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("ValueError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_PropertyError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'PropertyError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'PropertyError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_PropertyError({
                'name': 'PropertyError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_PropertyError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('PropertyError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but PropertyError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("PropertyError", Dict({'name': String("PropertyError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("PropertyError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_KeyError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'KeyError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'KeyError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_KeyError({
                'name': 'KeyError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_KeyError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('KeyError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but KeyError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("KeyError", Dict({'name': String("KeyError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("KeyError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_ZeroDivisionError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'ZeroDivisionError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'ZeroDivisionError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_ZeroDivisionError({
                'name': 'ZeroDivisionError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_ZeroDivisionError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('ZeroDivisionError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but ZeroDivisionError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("ZeroDivisionError", Dict({'name': String("ZeroDivisionError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("ZeroDivisionError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_LookupError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'LookupError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'LookupError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_LookupError({
                'name': 'LookupError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_UnicodeDecodeError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('LookupError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but LookupError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("LookupError", Dict({'name': String("LookupError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("LookupError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))
 
    
def BuiltInClass_UnicodeDecodeError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'UnicodeDecodeError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'UnicodeDecodeError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_UnicodeDecodeError({
                'name': 'UnicodeDecodeError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_UnicodeDecodeError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('UnicodeDecodeError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but UnicodeDecodeError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("UnicodeDecodeError", Dict({'name': String("UnicodeDecodeError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("UnicodeDecodeError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))
    
        
def BuiltInClass_ImportError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'ImportError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'ImportError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_ImportError({
                'name': 'ImportError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_ImportError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('ImportError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but ImportError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("ImportError", Dict({'name': String("ImportError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("ImportError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_ModuleNotFoundError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'ModuleNotFoundError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'ModuleNotFoundError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_ModuleNotFoundError({
                'name': 'ModuleNotFoundError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_ModuleNotFoundError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('ModuleNotFoundError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but ModuleNotFoundError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("ModuleNotFoundError", Dict({'name': String("ModuleNotFoundError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("ModuleNotFoundError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_KeyboardInterrupt(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'KeyboardInterrupt',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'KeyboardInterrupt' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_KeyboardInterrupt({
                'name': 'KeyboardInterrupt',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_KeyboardInterrupt({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('KeyboardInterrupt'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_RuntimeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but KeyboardInterrupt takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("KeyboardInterrupt", Dict({'name': String("KeyboardInterrupt"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("KeyboardInterrupt", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_RecursionError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'RecursionError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'RecursionError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_RecursionError({
                'name': 'RecursionError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_RecursionError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('RecursionError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but RecursionError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("RecursionError", Dict({'name': String("RecursionError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("RecursionError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_IOError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'IOError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'IOError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_IOError({
                'name': 'IOError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_IOError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('IOError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but IOError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("IOError", Dict({'name': String("IOError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("IOError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_OSError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'OSError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'OSError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_OSError({
                'name': 'OSError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_OSError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('OSError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but OSError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("OSError", Dict({'name': String("OSError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("OSError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_FileNotFoundError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'FileNotFoundError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'FileNotFoundError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_FileNotFoundError({
                'name': 'FileNotFoundError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_FileNotFoundError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('FileNotFoundError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but FileNotFoundError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("FileNotFoundError", Dict({'name': String("FileNotFoundError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("FileNotFoundError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_PermissionError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'PermissionError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'PermissionError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_PermissionError({
                'name': 'PermissionError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_PermissionError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('PermissionError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but PermissionError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("PermissionError", Dict({'name': String("PermissionError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("PermissionError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_NotImplementedError(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'NotImplementedError',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'NotImplementedError' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_NotImplementedError({
                'name': 'NotImplementedError',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_NotImplementedError({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('NotImplementedError'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but NotImplementedError takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("NotImplementedError", Dict({'name': String("NotImplementedError"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("NotImplementedError", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_SystemExit(args, node, context, type):
    res = RuntimeResult()
    if len(args) == 0 or len(args) > 2:
        raise Al_ArgumentError({
            'name': 'SystemExit',
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            'message': f"'SystemExit' takes 1 or 2 arguments",
            "context": context,
            'exit': False
        })
    if type == "raise":
        if len(args) == 1 and isinstance(args[0], String):
            raise Al_SystemExit({
                'name': 'SystemExit',
                'message': args[0].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            raise Al_SystemExit({
                'name': args[0].value if hasattr(args[0], 'value') and args[0].value else String('SystemExit'),
                'message': args[1].value,
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'context': context,
                'exit': False
            })
        else:
            raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but SystemExit takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    else:
        # return exception object
        if len(args) == 1 and isinstance(args[0], String):
            return res.success(BuiltInClass("SystemExit", Dict({'name': String("SystemExit"), 'message': String(args[0].value)})))
        elif len(args) == 2 and isinstance(args[0], String) and isinstance(args[1], String):
            return res.success(BuiltInClass("SystemExit", Dict({'name': String(args[0].value), 'message': String(args[1].value)})))


def BuiltInClass_Int(args, node, context, keyword_args=None):
    res = RuntimeResult()
    interpreter = Interpreter()
    base = 10
    keywords = {}
    if keyword_args != None and len(keyword_args) > 0:
        for keyword_arg in keyword_args:
            name = keyword_arg['name']
            value = res.register(interpreter.visit(keyword_arg['value'], context))
            keywords[name] = value
            
    if len(keywords) > 0:
        for name, value in keywords.items():
            if name != "base":
                raise Al_ArgumentError({
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    'message': f"int() got an unexpected keyword argument '{name}'",
                    "context": context,
                    'exit': False
                })    
            if not isinstance(value, Number):
                raise Al_TypeError({
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    'message': f"invalid type for int() base: '{TypeOf(value).getType()}'",
                    "context": context,
                    'exit': False
                })
            base = value.value
            
    if len(args) == 0:
        return res.success(Number(0))
    if len(args) > 2:
        raise Al_ArgumentError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"{len(args)} arguments given, but int() takes 1 or 2 arguments",
                "context": context,
                'exit': False
            })
    
    if len(args) == 2:
        if isinstance(args[1], Number):
            base = args[1].value
        else:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"invalid type for int() base: '{TypeOf(args[1]).getType()}'",
                "context": context,
                'exit': False
            })
    
    if isinstance(args[0], Number):
        value = args[0].value
        if isinstance(args[0].value, float):
            value = int(args[0].value)
        else:
            try:
                value = int(args[0].value, base)
            except:
                raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"int() can't convert non-string with explicit base",
                "context": context,
                'exit': False
            })
        
        return res.success(Number(value).setContext(context).setPosition(node.pos_start, node.pos_end))
    
    if isinstance(args[0], String):
        try:
            return res.success(Number(int(args[0].value, base)).setPosition(node.pos_start, node.pos_end).setContext(context))
        except Exception as e:
            raise Al_TypeError({
                "pos_start": node.pos_start,
                "pos_end": node.pos_end,
                'message': f"invalid literal for int() with base {base}: '{args[0].value}'",
                "context": context,
                'exit': False
            })
    if isinstance(args[0], Boolean):
        return res.success(Number(int(args[0].value)).setPosition(node.pos_start, node.pos_end).setContext(context))
    raise Al_TypeError({
        "pos_start": node.pos_start,
        "pos_end": node.pos_end,
        'message': f"int() argument must be of type number, string or boolean, not {TypeOf(args[0]).getType()}",
        "context": context,
        'exit': False
    })


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

    def no_method(self):
        raise Al_PropertyError({
            "pos_start": self.pos_start,
            "pos_end": self.pos_end,
            'message': f"'{TypeOf(self.name).getType()}' object has no property '{self.type}'",
            "context": self.context,
            'exit': False
        })


   



    def __str__(self):
        return f"{self.name}"



    def repr(self):
        return f"<{str(self.type)}()>, [ built-in string method ]"



class BuiltInMethod_Pair(Value):
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
        if self.type in pair_methods:
            method = f"BuiltInMethod_{pair_methods[self.type]}"
            is_method = getattr(self, method, self.no_method)
            value = is_method()
            self.name = value
            if type(self.name).__name__ == "RuntimeResult":
                self.name = ''
        return self.name

    def no_method(self):
        raise Al_PropertyError({
            "pos_start": self.pos_start,
            "pos_end": self.pos_end,
            'message': f"'{TypeOf(self.name).getType()}' object has no property '{self.type}'",
            "context": self.context,
            'exit': False
        })


    def is_true(self):
        return True if self.name else False

    def BuiltInMethod_count(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            # returns the number of elements within the specified value
            count = 0
            if isinstance(self.args[0], String) or isinstance(self.args[0], Number):
                for element in self.name.elements:
                    if element.value == self.args[0].value:
                        count += 1
                return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            elif isinstance(self.args[0], BuiltInFunction):
                for element in self.name.elements:
                    if element.name == self.args[0].name:
                        count += 1
                return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            elif isinstance(self.args[0], Dict) or isinstance(self.args[0], Object) or isinstance(self.args[0], Module) or isinstance(self.args[0], Class) or isinstance(self.args[0], List) or isinstance(self.args[0], Pair):
                for element in self.name.elements:
                    if isinstance(element, Dict):
                        if element.isSame(self.args[0]):
                            count += 1
                return Number(count).setContext(self.context).setPosition(self.pos_start, self.pos_end)

        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(self.args)} arguments given, but count() takes 1 argument",
                "context": self.context,
                'exit': False
            })

    def BuiltInMethod_findIndex(self):
        res = RuntimeResult()
        if len(self.args) == 1:
            if isinstance(self.args[0], String) or isinstance(self.args[0], Number):
                for index, element in enumerate(self.name.elements):
                    if element.value == self.args[0].value:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            elif isinstance(self.args[0], BuiltInFunction) or isinstance(self.args[0], BuiltInClass):
                for index, element in enumerate(self.name.elements):
                    if element.name == self.args[0].name:
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
            elif isinstance(self.args[0], Dict) or isinstance(self.args[0], Object) or isinstance(self.args[0], Module) or isinstance(self.args[0], Class) or isinstance(self.args[0], List) or isinstance(self.args[0], Pair):
                for index, element in enumerate(self.name.elements):
                    if element.isSame(self.args[0]):
                        return Number(index).setContext(self.context).setPosition(self.pos_start, self.pos_end)
                return Number(-1).setContext(self.context).setPosition(self.pos_start, self.pos_end)
        else:
            raise Al_RuntimeError({
                "pos_start": self.pos_start,
                "pos_end": self.pos_end,
                'message': f"{len(self.args)} arguments given, but findIndex() takes 1 argument",
                "context": self.context,
                'exit': False
            })


    def copy(self):
        copy = BuiltInMethod_Pair(
            self.type, self.name, self.args, self.node, self.context)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy



    def __str__(self):
        return f"{self.name}"



    def repr(self):
        return f"<{str(self.type)}()>, [ built-in pair method ]"

types = {
        'int': 'int',
        'float': 'float',
        'complex': 'complex',
        'chr': 'chr',
        'str': 'str',
        'bool': 'bool',
        'bytes': 'bytes',
        'list': 'list',
        'pair': 'pair',
        'dict': 'dict',
        'builtin': 'builtin',
        'module': 'module',
        }

class Types(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = name
        self.types = types
        self.getType()

    def getType(self):
        res = RuntimeResult()
        
        self.type = self.types[self.name]
        return self.type

    def get_comparison_eq(self, other):
        if self.value == other.value:
            return Boolean(True), None
        else:
            return Boolean(False), None

    def get_comparison_ne(self, other):
        return self.setTrueorFalse(other.value != "none"), None

    def and_by(self, other):
        return self.setTrueorFalse(other.value == "none"), None

    def notted(self):
        value = setNumber(self.value)
        return self.setTrueorFalse(not value).setContext(self.context), None

    def copy(self):
        copy = Types(self.name)
        copy.setContext(self.context)
        copy.setPosition(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<class {self.name}>"


class Interpreter:

    def __init__(self):
        self.error_detected = False
        self.environment = None


    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit)
        self.context = context
        return method(node, context)


    def no_visit(self, node, context):
        return RuntimeResult().success(None)


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


    def visit_DocStringNode(self, node, context):
        return RuntimeResult().success(
            DocString(node.tok.value).setContext(
                context).setPosition(node.pos_start, node.pos_end)
        )


    def visit_ByteStringNode(self, node, context):
        return RuntimeResult().success(
            Bytes(node.tok.value).setContext(
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
                    # if isinstance(replace_value, String):
                    #     value_replaced = str(replace_value.value)
                    # else:
                    #     if value_replaced[0] == "'":
                    #         value_replaced = str(value_replaced[1:-1])
                    if value_replaced == "None":
                        value_replaced = str(NoneType.none)
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
        except Exception as e:
            raise e


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
            NoneType(node.tok.value).setContext(
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
               raise Al_NameError({
                    'name': "NameError",
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"name '{node.value_node.value}' is not defined",
                    'context': context,
                    'exit': False
               })

        if type(node.variable_name_token).__name__ == "tuple" or type(node.variable_name_token).__name__ == "list":
            var_name = node.variable_name_token
            if isinstance(var_name, Pair) or isinstance(var_name, List):
                if len(var_name) != len(value.elements):
                    raise Al_ValueError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                        'context': context,
                        'exit': False
                    })
                else:
                    for i in range(len(var_name)):
                        context.symbolTable.set(
                            var_name[i].name.value, value.elements[i])

            elif isinstance(value, Object) or isinstance(value, Dict) or isinstance(value, Module):

                if len(var_name) != len(value.properties):
                    has_star = False
                    var = []
                    var_names = [name.name.value for name in var_name]
                    for name in var_names:
                        if is_varags(name):
                            has_star = True
                            break
                    values = [v  for v in value.properties.values()]
                    for v in var_name:
                        if type(v).__name__ != "VarAccessNode" and type(v).__name__ != "StringNode":
                            raise Al_ValueError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"Cannot pair '{TypeOf(value).getType()}' with '{TypeOf(v).getType()}'",
                                'context': context,
                                'exit': False
                            })
                        var.append(v.name.value)

                    if has_star:
                        star_names = [name for name in var_names if is_varags(name) == True]
                        non_star_names = [name for name in var_names if is_varags(name) == False]
                        starags, nonstarargs = vna_algorithm(var_names, values)
                        for star_name in star_names:
                            name = make_varargs(star_name)
                            context.symbolTable.set(name, List(starags))
                        for i in range(len(non_star_names)):
                            try:
                                context.symbolTable.set(non_star_names[i], nonstarargs[i])
                            except:
                                raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"expected at least {len(var_names) - 1} values, unable to pair {len(values)} value(s)",
                                        'context': context,
                                        'exit': False
                                })



                    else:
                        raise Al_ValueError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"expected {len(var_name)} values, unable to pair {len(value.properties)} value(s)",
                            'context': context,
                            'exit': False
                        })
                else:
                    has_star = False
                    properties = []
                    var = []
                    var_names = [name.name.value for name in var_name]
                    for name in var_names:
                        if is_varags(name):
                            has_star = True
                            break
                    values = [v for v in value.properties.keys()]
                    for prop in value.properties.values():
                        properties.append(prop)
                    for v in var_name:
                        var.append(v.name.value)
                        if has_star:
                            star_names = [name for name in var_names if is_varags(name) == True]
                            non_star_names = [name for name in var_names if is_varags(name) == False]
                            starags, nonstarargs = vna_algorithm(var_names, values)
                            for star_name in star_names:
                                name = make_varargs(star_name)
                                context.symbolTable.set(name, List(starags))
                            for i in range(len(non_star_names)):
                                try:
                                    context.symbolTable.set(non_star_names[i], nonstarargs[i])
                                except:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"expected {len(var_name)} values, unable to pair {len(value.properties)} value(s)",
                                        'context': context,
                                        'exit': False
                                    })
                        else:
                            for i in range(len(var_name)):
                                context.symbolTable.set(
                                    var_name[i].name.value, properties[i])

            elif isinstance(value, Pair) or isinstance(value, List):
                if len(var_name) != len(value.elements):
                    has_star = False
                    var = []
                    var_names = [name.name.value for name in var_name]
                    for name in var_names:
                        if is_varags(name):
                            has_star = True
                            break
                    values = value.elements
                    for v in var_name:
                        if type(v).__name__ != "VarAccessNode" and type(v).__name__ != "StringNode":
                            raise Al_ValueError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"Cannot pair '{TypeOf(value).getType()}' with '{TypeOf(v).getType()}'",
                                'context': context,
                                'exit': False
                            })
                        var.append(v.name.value)

                        if has_star:
                            star_names = [name for name in var_names if is_varags(name) == True]
                            non_star_names = [name for name in var_names if is_varags(name) == False]
                            starags, nonstarargs = vna_algorithm(var_names, values)
                            for star_name in star_names:
                                name = make_varargs(star_name)
                                context.symbolTable.set(name, List(starags))
                            for i in range(len(non_star_names)):
                                try:
                                    context.symbolTable.set(non_star_names[i], nonstarargs[i])
                                except:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"expected at least {len(var_names) - 1} values, unable to pair {len(values)} value(s)",
                                        'context': context,
                                        'exit': False
                                    })
                        else:
                            raise Al_ValueError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                                'context': context,
                                'exit': False
                            })
                else:
                    has_star = False
                    elements = []
                    var = []
                    var_names = [name.name.value for name in var_name]
                    values = value.elements
                    for elem in value.elements:
                        elements.append(elem)
                    for name in var_names:
                        if is_varags(name):
                            has_star = True
                            break
                    for v in var_name:
                        var.append(v.name.value)
                        if has_star:
                            star_names = [
                                name for name in var_names if is_varags(name) == True]
                            non_star_names = [
                                name for name in var_names if is_varags(name) == False]
                            starags, nonstarargs = vna_algorithm(
                                var_names, values)
                            for star_name in star_names:
                                name = make_varargs(star_name)
                                context.symbolTable.set(name, List(starags))
                            for i in range(len(non_star_names)):
                                try:
                                    context.symbolTable.set(
                                    non_star_names[i], nonstarargs[i])
                                except:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"expected {len(var_name)} values, unable to pair {len(value.elements)} value(s)",
                                        'context': context,
                                        'exit': False
                                    })
                        else:
                            for i in range(len(var_name)):
                                context.symbolTable.set(
                                    var_name[i].name.value, elements[i])

            else:
                raise Al_RuntimeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"Cannot pair '{TypeOf(value).getType()}' with '{TypeOf(var_name).getType()}'",
                    'context': context,
                    'exit': False
                })


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
                v_ = context.symbolTable.set_final(var_name, value, "final")
                redeclared = v_ == 'already_declared'
                if redeclared:
                    raise Al_NameError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"assignment to final variable '{var_name}'",
                        'context': context,
                        'exit': False
                    })
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
            is_module_environment = node.pos_start.environment == 'module'
            module_name = node.pos_start.module_name
            if is_module_environment and module_name != None and module_namespace is not None and len(module_namespace.namespace) > 0:
                if  module_namespace.get(module_name) is not None and var_name in module_namespace.get(module_name):
                    value = module_namespace.namespace[module_name][var_name]
                if type(value) is dict:
                    try:
                        value = value['value']
                    except:
                        value = value
                if value is None:
                    if var_name == "@":
                        raise Al_RuntimeError({
                            'name': "RuntimeError",
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"Expected '@' to be followed by an identifier",
                            'context': context,
                            'exit': False
                        })


                    exception_details =  {
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"name '{var_name}' is not defined",
                        'node': node,
                        'context': context,
                        'exit': False
                    }
                    self.error_detected = True
                    if var_name == "super":
                        exception_details['message'] = "cannot use 'super' outside of a class or no superclass exists"
                        raise Al_RuntimeError(exception_details)
                    raise Al_NameError(exception_details)
                else:
                    value = value.copy().setContext(context).setPosition(node.pos_start, node.pos_end) if hasattr(value, 'copy') else value
                    return res.success(value)
            else:
                if var_name == "@":
                    raise Al_RuntimeError({
                        'name': "RuntimeError",
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"Expected '@' to be followed by an identifier",
                        'context': context,
                        'exit': False
                    })

                exception_details =  {
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"name '{var_name}' is not defined",
                    'node': node,
                    'context': context,
                    'exit': False
                }
                self.error_detected = True
                if var_name == "super":
                    exception_details['message'] = "cannot use 'super' outside of a class or no superclass exists"
                    raise Al_RuntimeError(exception_details)
                raise Al_NameError(exception_details)
        else:
            value = value.copy().setContext(context).setPosition(node.pos_start, node.pos_end) if hasattr(value, 'copy') else value
            return res.success(value)


    def visit_VarReassignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.name.value if hasattr(node.name, 'value') else node.name.id.value
        if hasattr(var_name, 'value'):
            var_name = var_name.value
        elif hasattr(var_name, 'id'):
            var_name = var_name.id.value
        operation = node.operation
        value_ = context.symbolTable.get(var_name)
        value = res.register(self.visit(node.value, context))
        property = node.property
        v = value_
        error = {
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            "message": "",
            "context": context,
            "exit": False
        }
        if value_ != None:
            if isinstance(value_, Class):
                v = {
                    'value': value_,
                    'type': 'let'
                }
            if type(v) is dict:
                var_type = v['type']
                if var_type == "final":
                    raise Al_NameError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"name '{var_name}' cannot be reassigned",
                        'context': context,
                        'exit': False
                    })
                if var_type == "freeze":
                    raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"assignment to frozen variable '{var_name}'",
                        'context': context,
                        'exit': False
                    })
                else:
                    if operation == "add":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                new_value = Number(setNumber(v['value'].value) + setNumber(value.value))
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'name': 'TypeError',
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '+=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], String):
                            if isinstance(value, String):
                                new_value = String(v['value'].value + value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"can only concatenate string (not '{TypeOf(value).getType()}') to string",
                                    'context': context,
                                    'exit': False
                                })
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
                            elif isinstance(value, Object) or isinstance(value, Dict):
                                new_list = []
                                for key, value in value.properties.items():
                                    new_list.append(String(key).setPosition(node.pos_start, node.pos_end).setContext(context))
                                new_value = List(v['value'].elements + new_list)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"type '{TypeOf(value).getType()}' is not iterable",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Pair):
                            if isinstance(value, Pair):
                                new_value = Pair(v['value'].elements + value.elements)
                                context.symbolTable.set(var_name, new_value)
                            else:
                                raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"can only concatenate pair (not '{TypeOf(value).getType()}') to pair",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Dict) or isinstance(v['value'], Object) or isinstance(v['value'], Class):
                                if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '+=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                                if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                                property_value = v['value'].properties[property.value]

                                if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                    if isinstance(value, Number) or isinstance(value, Boolean):
                                        new_value = Number(setNumber(property_value.value) + setNumber(value.value))
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                            'name': String('TypeError'),
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': String(f"unsupported '+=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'"),
                                            'context': context,
                                            'exit': False
                                        })
                                elif isinstance(property_value, String):
                                    if isinstance(value, String):
                                        new_value = String(property_value.value + value.value)
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                            'name': String('TypeError'),
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"can only concatenate string (not '{TypeOf(value).getType()}') to string",
                                            'context': context,
                                            'exit': False
                                        })
                                elif isinstance(property_value, List):
                                    if isinstance(value, List):
                                        new_value = List(property_value.elements + value.elements)
                                        v['value'].properties[property.value] = new_value
                                    elif isinstance(value, String):
                                        new_list = []
                                        for char in value.value:
                                            new_list.append(String(char).setPosition(node.pos_start, node.pos_end).setContext(context))
                                        new_value = List(property_value.elements + new_list)
                                        v['value'].properties[property.value] = new_value
                                    elif isinstance(value, Object) or isinstance(value, Dict):
                                        new_list = []
                                        for key, value in value.properties.items():
                                            new_list.append(String(key).setPosition(node.pos_start, node.pos_end).setContext(context))
                                        new_value = List(property_value.elements + new_list)
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                            'name': String('TypeError'),
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"type '{TypeOf(value).getType()}' is not iterable",
                                            'context': context,
                                            'exit': False
                                        })
                                elif isinstance(property_value, Pair):
                                    if isinstance(value, Pair):
                                        new_value = Pair(property_value.elements + value.elements)
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                            'name': String('TypeError'),
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"can only concatenate pair (not '{TypeOf(value).getType()}') to pair",
                                            'context': context,
                                            'exit': False
                                        })
                                else:
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '+=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                        else:
                            raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '+=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                    elif operation == "sub":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                new_value = Number(setNumber(v['value'].value) - setNumber(value.value))
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    new_value = Number(setNumber(property_value.value) - setNumber(value.value))
                                    v['value'].properties[property.value] = new_value
                                else:
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '-=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '-=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                           raise Al_TypeError({
                               'name': String('TypeError'),
                               'pos_start': node.pos_start,
                               'pos_end': node.pos_end,
                               'message': String(f"unsupported '-=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'"),
                               'context': context,
                               'exit': False
                           })
                    elif operation == "mul":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                new_value = Number(setNumber(v['value'].value) * setNumber(value.value))
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'"),
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], String):
                            if isinstance(value, Number):
                                new_value = String(v['value'].value * value.value)
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"cannot multiply {TypeOf(v['value']).getType()} and {TypeOf(value).getType()}"),
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], List):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                if isinstance(setNumber(value.value), int):
                                    new_value = List(v['value'].elements * value.value)
                                    context.symbolTable.set(var_name, new_value)
                                else:
                                    raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"cannot multiply by non-int of type '{TypeOf(value).getType()}'"),
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"cannot multiply by non-int of type '{TypeOf(value).getType()}'"),
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Pair):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                if isinstance(setNumber(value.value), int):
                                    new_value = Pair(v['value'].elements * value.value)
                                    context.symbolTable.set(var_name, new_value)
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot multiply by non-int of type '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot multiply by non-int of type '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    new_value = Number(setNumber(property_value.value) * setNumber(value.value))
                                    v['value'].properties[property.value] = new_value
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '*=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                            elif isinstance(property_value, String):
                                if isinstance(value, Number):
                                    new_value = String(property_value.value * value.value)
                                    v['value'].properties[property.value] = new_value
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot multiply {TypeOf(property_value).getType()} and {TypeOf(value).getType()}",
                                    'context': context,
                                    'exit': False
                                })
                            elif isinstance(property_value, List):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    if isinstance(setNumber(value.value), int):
                                        new_value = List(property_value.elements * value.value)
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': String(f"cannot multiply by non-int of type '{TypeOf(value).getType()}'"),
                                        'context': context,
                                        'exit': False
                                    })
                                else:
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': String(f"cannot multiply by non-int of type '{TypeOf(value).getType()}'"),
                                        'context': context,
                                        'exit': False
                                    })
                            elif isinstance(property_value, Pair):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    if isinstance(setNumber(value.value), int):
                                        new_value = Pair(property_value.elements * value.value)
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"cannot multiply by non-int of type '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                                else:
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"cannot multiply by non-int of type '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '*=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                            raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"unsupported '*=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'"),
                                    'context': context,
                                    'exit': False
                                })
                    elif operation == "div":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                if value.value != 0:
                                    new_value = Number(setNumber(v['value'].value) / setNumber(value.value))
                                    context.symbolTable.set(var_name, new_value, "let")
                                else:
                                    raise Al_ZeroDivisionError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"division by zero",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '/=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '/=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    if value.value != 0:
                                        new_value = Number(setNumber(property_value.value) / setNumber(value.value))
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_ZeroDivisionError({
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"division by zero",
                                            'context': context,
                                            'exit': False
                                        })
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '/=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"unsupported '/=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                'context': context,
                                'exit': False
                            })
                        else:
                            raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '/=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                    elif operation == "floor_div":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                if value.value != 0:
                                    new_value = Number(setNumber(v['value'].value) // setNumber(value.value))
                                    context.symbolTable.set(var_name, new_value, "let")
                                else:
                                    raise Al_ZeroDivisionError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"division by zero",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '//=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '//=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    if value.value != 0:
                                        new_value = Number(setNumber(property_value.value) // setNumber(value.value))
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_ZeroDivisionError({
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"division by zero",
                                            'context': context,
                                            'exit': False
                                        })
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '//=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '//=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                            raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '//=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                    elif operation == "mod":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                if value.value != 0:
                                    new_value = Number(setNumber(v['value'].value) % setNumber(value.value))
                                    context.symbolTable.set(var_name, new_value, "let")
                                else:
                                    raise Al_ZeroDivisionError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"modulo by zero",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '%=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '%=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    if value.value != 0:
                                        new_value = Number(setNumber(property_value.value) % setNumber(value.value))
                                        v['value'].properties[property.value] = new_value
                                    else:
                                        raise Al_ZeroDivisionError({
                                            'pos_start': node.pos_start,
                                            'pos_end': node.pos_end,
                                            'message': f"modulo by zero",
                                            'context': context,
                                            'exit': False
                                        })
                                else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '%=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                    raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '%=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                            raise Al_TypeError({
                                    'name': String('TypeError'),
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': String(f"unsupported '%=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'"),
                                    'context': context,
                                    'exit': False
                                })
                    elif operation == "pow":
                        if isinstance(v['value'], Number) or isinstance(v['value'], Boolean):
                            if isinstance(value, Number) or isinstance(value, Boolean):
                                new_value = Number(setNumber(v['value'].value) ** setNumber(value.value))
                                context.symbolTable.set(var_name, new_value, "let")
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '^=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        elif isinstance(v['value'], Object) or isinstance(v['value'], Dict) or isinstance(v['value'], Class):
                            if not hasattr(property, 'value'):
                                    raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '^=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            if not v['value'].has_property(property.value):
                                    error["message"] = f"{v['value'].name} object has no property '{property.value}'"
                                    raise Al_PropertyError(error)
                            property_value = v['value'].properties[property.value]
                            if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                                if isinstance(value, Number) or isinstance(value, Boolean):
                                    new_value = Number(setNumber(property_value.value) ** setNumber(value.value))
                                    v['value'].properties[property.value] = new_value
                                else:
                                   raise Al_TypeError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'message': f"unsupported '^=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                        'context': context,
                                        'exit': False
                                    })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '^=' operation for '{TypeOf(property_value).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                        else:
                            raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"unsupported '^=' operation for '{TypeOf(v['value']).getType()}' and '{TypeOf(value).getType()}'",
                                    'context': context,
                                    'exit': False
                                })
                    else:
                        context.symbolTable.set(var_name, value, "let")

        else:
            raise Al_NameError({
                'name': String('NameError'),
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': String(f"name '{var_name}' is not defined"),
                'context': context,
                'exit': False
            })
        value = value.copy().setContext(context).setPosition(
            node.pos_start, node.pos_end) if hasattr(value, 'copy') else value
        return res.success(value)


    def visit_PropertyNode(self, node, context):
        res = RuntimeResult()
        value = ""
        object_name = res.register(self.visit(node.name, context))
        var_name = node.name.value if hasattr(node.name, 'value') else node.name.id.value if hasattr(node.name, 'id') and hasattr(node.name.id, 'value') else node.name
        object_key = node.property
        #print(type(object_name).__name__, type(object_key).__name__, object_key)
        error = {
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            "message": "",
            "context": context,
            "exit": False
        }

        if isinstance(object_name, Class):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        if object_name.name == "Export":
                            error['message'] = String(f"Export has no member '{object_key.id.value}'")
                        else:
                            error["message"] = f"'{object_name.name}' object has no method '{object_key.id.value}'"
                        raise Al_PropertyError(error)

            if type(object_key).__name__ == "Token":
                if object_key.value in object_name.properties:
                    value = object_name.properties[object_key.value]
                    return res.success(value)
                elif object_key.value in class_methods:
                    return res.success(class_methods[object_key.value](object_name, None, None, None))
                else:
                    error["message"] = f"'{object_name.name}' object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        args_node = object_key.args_nodes
                        keyword_args_list = object_key.keyword_args_list
                        args = []
                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        if isinstance(value, Function):
                            return_value = res.register(value.run(keyword_args_list,args, object_name))
                        else:
                            return_value = res.register(value.execute(args, keyword_args_list))
                        if res.should_return(): return res
                        #if res.func_return_value is not None: return res.success(res.func_return_value)
                        return res.success(return_value)
                    elif object_key.node_to_call.value in class_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(class_methods[method_name](object_name, args, kwargs, var_name))
                    else:
                        self.error_detected = True
                        error["message"] = String(f"'{object_name.name}' object has no method '{object_key.node_to_call.value}'")
                        raise Al_PropertyError(error)

        elif isinstance(object_name, BuiltInClass):
            if type(object_key).__name__ == "Token":
                if object_key.value in object_name.properties:
                    value = object_name.properties[object_key.value]
                    return res.success(value)
                else:
                    error["message"] = String(
                        f"'{object_name.name}' object has no property {object_key.value}")
                    raise Al_PropertyError(error)
            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        args_node = object_key.args_nodes
                        keyword_args_list = object_key.keyword_args_list
                        args = []

                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        return_value = res.register(value.run(keyword_args_list,args, object_name))
                        if res.should_return():
                                    return res

                        return res.success(return_value)
                    else:
                        error["message"] = f"'{object_name.name}' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
                else:
                    error["message"] = f"'{object_name.name}' object has no property '{object_key.node_to_call.value}'"
                    raise Al_PropertyError(error)
            else:
                error["message"] = f"'{object_key.node_to_call.value}'"
                raise Al_PropertyError(error)

        elif isinstance(object_name, Object):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"'{node.name.id.value}' object has no property '{object_key.id.value}'"
                        raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        if not isinstance(value, Class) and not isinstance(value, Function) and not isinstance(value, BuiltInFunction) and not isinstance(value, BuiltInClass):
                            error["message"] = f"'{object_key.node_to_call.value}' object is not callable"
                            raise Al_NameError(error)
                        else:
                            args_node = object_key.args_nodes
                            keyword_args_list = object_key.keyword_args_list
                            args = []

                            for arg in args_node:
                                args.append(res.register(
                                    self.visit(arg, context)))
                                if res.should_return(): return res

                            return_value = res.register(value.execute(args,keyword_args_list))
                            return res.success(return_value)
                    elif object_key.node_to_call.value in object_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(object_methods[method_name](object_name, args, kwargs, var_name))
                    else:
                        error["message"] = f"'{node.name.id.value}' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
                
                    
            elif type(object_key).__name__ == "Token":
                if object_key.value in object_methods:
                    if object_key.value == "length":
                        value = len(object_name.properties)
                        return res.success(Number(value))
                    else:
                        value = f"<{str(object_key.value)}()>, [ built-in object method ]"
                        return res.success(String(value))
                if hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        error["message"] = f"'{object_name.name}' object has no property '{object_key.value}'"
                        raise Al_PropertyError(error)

        elif isinstance(object_name, Dict):
            if type(object_key).__name__ == "VarAccessNode":
                if object_key.id.value in dict_methods:
                        value = f"<{str(object_key.id.value)}()>, [ built-in dict method ]"
                        return res.success(String(value))
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} object has no property {object_key.id.value}"
                        raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in dict_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(dict_methods[method_name](object_name, args, kwargs, var_name))
                    elif object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        if not isinstance(value, Class) and not isinstance(value, Function) and not isinstance(value, BuiltInFunction) and not isinstance(value, BuiltInClass):
                            error["message"] = f"'{object_key.node_to_call.value}' is not callable"
                            raise Al_NameError(error)
                        else:
                            args_node = object_key.args_nodes
                            keyword_args_list = object_key.keyword_args_list
                            args = []

                            for arg in args_node:
                                args.append(res.register(
                                    self.visit(arg, context)))
                                if res.should_return():
                                    return res

                            return_value = res.register(
                                value.execute(args,keyword_args_list))
                            
                            if res.should_return():
                                return res
                            return res.success(return_value)
                    else:
                        error["message"] = f"'{node.name.id.value}' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
            
            elif type(object_key).__name__ == "Token":
                if object_key.value in dict_methods:
                    if object_key.value == "length":
                        value = len(object_name.properties)
                        return res.success(Number(value))
                    else:
                        value = f"<{str(object_key.value)}()>, [ built-in dict method ]"
                        return res.success(String(value))
                elif hasattr(object_name, "properties"):
                    if object_key.value in object_name.properties:
                        value = object_name.properties[object_key.value]
                        return res.success(value)
                    else:
                        error["message"] = f"'{object_key.value}'"
                        raise Al_PropertyError(error)

            elif type(object_key).__name__ == "PropertyNode":
                if hasattr(object_name, "properties"):
                    if object_key.name.id.value in object_name.properties:
                        value = object_name.properties[object_key.name.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"'{node.name.id.value}' object has no property '{object_key.name.id.value}'"
                        raise Al_PropertyError(error)

        elif isinstance(object_name, List):
            if type(object_key).__name__ == "VarAccessNode":
                if object_key.id.value in list_methods:
                    value = f"<{str(object_key.id.value)}()>, [ built-in list method ]"
                    if object_key.id.value == "length":
                        return res.success(Number(len(object_name.elements)))
                    else:
                        value = f"<{str(object_key.id.value)}()>, [ built-in list method ]"
                        return res.success(String(value))

            if type(object_key).__name__ == "Token":
                if object_key.value in list_methods:
                    return res.success(list_methods[object_key.value](object_name, None, None, None))
                else:
                    error["message"] = f"'list' object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)
                
            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in list_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(list_methods[method_name](object_name, args, kwargs, var_name))
                    else:
                        error["message"] = f"'list' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)

        elif isinstance(object_name, Pair):
            if type(object_key).__name__ == "Token":
                if object_key.value in pair_methods:
                    return res.success(pair_methods[object_key.value](object_name, None,None,None))
                else:
                    error["message"] = f"'pair' object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in pair_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(pair_methods[method_name](object_name, args, kwargs, var_name))
                    else:
                        error["message"] = f"'pair' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)

        elif isinstance(object_name, String):
            if type(object_key).__name__ == "Token":
                if object_key.value in string_methods:
                    return res.success(string_methods[object_key.value](object_name, None,None,None))
                else:
                    error["message"] = f"'string' object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)
            
            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in string_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(string_methods[method_name](object_name, args, kwargs, var_name))
                    else:
                        error["message"] = f"'string' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)

        elif isinstance(object_name, Number):
            if type(object_key).__name__ == "Token":
                if object_key.value in number_methods:
                    return res.success(number_methods[object_key.value](object_name, None,None,None))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' object has no property {object_key.value}"
                    raise Al_PropertyError(error)

            elif type(object_key).__name__ == "VarAccessNode":
                if object_key.id.value in number_methods:
                    return res.success(number_methods[object_key.id.value](object_name, None,None,None))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' object has no property {object_key.id.value}"
                    raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if object_key.node_to_call.value in number_methods:
                    method_name = object_key.node_to_call.value
                    args = []
                    kwargs = object_key.keyword_args_list
                    if kwargs == None:
                        kwargs = []
                    for arg in object_key.args_nodes:
                        args.append(res.register( self.visit(arg, context)))
                        if res.should_return(): return res
                    return res.success(number_methods[method_name](object_name, args, kwargs))
                else:
                    error["message"] = f"'{TypeOf(object_name.value).getType()}' object has no property {object_key.node_to_call.value}"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, Function):
            if type(object_key).__name__ == "Token":
                if object_key.value in function_methods:
                    return res.success(function_methods[object_key.value](object_name, None,None,None))
                if object_key.value in object_name.properties:
                    value = object_name.properties[object_key.value]
                    return res.success(value)
                else:
                    error["message"] = f"{object_name.name} object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)
                
            if type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in function_methods:
                            method_name = object_key.node_to_call.value
                            args = []
                            kwargs = object_key.keyword_args_list
                            if kwargs == None:
                                kwargs = []
                            for arg in object_key.args_nodes:
                                args.append(res.register( self.visit(arg, context)))
                                if res.should_return(): return res
                            return res.success(function_methods[method_name](object_name, args, kwargs, var_name))
                    if object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        args_node = object_key.args_nodes
                        keyword_args_list = object_key.keyword_args_list
                        args = []

                        for arg in args_node:
                            args.append(res.register(
                                self.visit(arg, context)))
                            if res.should_return(): return res
                        _type = object_name.type
                        if _type == "method":
                            return_value = res.register(value.run(keyword_args_list,args, object_name))
                        else:
                            return_value = res.register(value.execute(args,keyword_args_list))
                        if res.should_return():
                                return res

                        return res.success(return_value)
                    else:
                        error["message"] = f"{object_name.name} has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
            else:
                error["message"] = f"'{object_name.name}'"
                raise Al_PropertyError(error)
    
        elif isinstance(object_name, BuiltInFunction):
            if type(object_key).__name__ == "Token":
                    if object_key.value in builtin_function_methods:
                        return res.success(builtin_function_methods[object_key.value](object_name, None,None,None))
            if type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if type(object_key.node_to_call).__name__ == "Token":
                        if object_key.node_to_call.value in builtin_function_methods:
                            method_name = object_key.node_to_call.value
                            args = []
                            kwargs = object_key.keyword_args_list
                            if kwargs == None:
                                kwargs = []
                            for arg in object_key.args_nodes:
                                args.append(res.register( self.visit(arg, context)))
                                if res.should_return(): return res
                            return res.success(builtin_function_methods[method_name](object_name, args, kwargs, var_name))
               
        elif isinstance(object_name, Bytes):
            if type(object_key).__name__ == "Token":
                if object_key.value in bytes_methods:
                    return res.success(bytes_methods[object_key.value](object_name, None,None,None))
                else:
                    error["message"] = f"'bytes' object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in bytes_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(bytes_methods[method_name](object_name, args, kwargs))
                    else:
                        error["message"] = f"'bytes' object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
                               
        elif isinstance(object_name, Module):
            if type(object_key).__name__ == "VarAccessNode":
                if hasattr(object_name, "properties"):
                    if object_key.id.value in object_name.properties:
                        value = object_name.properties[object_key.id.value]
                        return res.success(value)
                    else:
                        error["message"] = f"{node.name.id.value} object has no property '{object_key.id.value}'"
                        raise Al_PropertyError(error)

            elif type(object_key).__name__ == "CallNode":
                if type(object_key.node_to_call).__name__ == "Token":
                    if object_key.node_to_call.value in object_name.properties:
                        value = object_name.properties[object_key.node_to_call.value]
                        if isinstance(value, dict):
                            value = value['value']
                        if not isinstance(value, Class) and not isinstance(value, Function) and not isinstance(value, BuiltInFunction) and not isinstance(value, BuiltInClass):
                            error["message"] = f"'{object_key.node_to_call.value}' is not callable"
                            raise Al_NameError(error)
                        else:
                            args_node = object_key.args_nodes
                            keyword_args_list = object_key.keyword_args_list
                            args = []
                            for arg in args_node:
                                args.append(res.register(
                                    self.visit(arg, context)))
                                if res.should_return(): return res
                            return_value = res.register(value.execute(args,keyword_args_list))

                            if res.should_return():
                                    return res
                            return res.success(return_value)
                    elif object_key.node_to_call.value in module_methods:
                        method_name = object_key.node_to_call.value
                        args = []
                        kwargs = object_key.keyword_args_list
                        if kwargs == None:
                            kwargs = []
                        for arg in object_key.args_nodes:
                            args.append(res.register( self.visit(arg, context)))
                            if res.should_return(): return res
                        return res.success(module_methods[method_name](object_name, args, kwargs))
                    else:
                        error["message"] = f"{node.name.id.value} object has no property '{object_key.node_to_call.value}'"
                        raise Al_PropertyError(error)
                


            elif type(object_key).__name__ == "Token":
                if object_key.value in object_name.properties:
                    value = object_name.properties[object_key.value]
                    if isinstance(value, dict):
                        return res.success(value['value'])
                    else:
                        return res.success(value)
                if object_key.value in module_methods:
                    return res.success(module_methods[object_key.value](object_name, None,None,None))
                else:
                    error["message"] = f"{object_name.name} object has no property '{object_key.value}'"
                    raise Al_PropertyError(error)

        else:
            self.error_detected = True
            key = ''
            message = ''
            if hasattr(object_key, "value"):
                key = object_key.value
            elif hasattr(object_key, "id"):
                key = object_key.id.value
            elif hasattr(object_key, "node_to_call"):
                if hasattr(object_key.node_to_call, "value"):
                    key = object_key.node_to_call.value
                elif hasattr(object_key.node_to_call, "id"):
                    key = object_key.node_to_call.id.value
            if hasattr(object_name, "name"):
                message = f"'{object_name.name}' object has no property {key}"
            else:
                message = f"'{key}'"
            error["message"] = message
            raise Al_PropertyError(error)


    def visit_PropertySetNode(self, node, context):
        res = RuntimeResult()
        object_name = res.register(self.visit(node.name, context))
        property = node.property
        value = res.register(self.visit(node.value, context))
        operation = node.type_
        error = {
            "name": "PropertyError",
            "pos_start": node.pos_start,
            "pos_end": node.pos_end,
            "message": "",
            "context": context,
            "exit": False
        }
        if operation != None and operation == "++":
            if isinstance(object_name, Object) or isinstance(object_name, Dict) or isinstance(object_name, Class):
                if not object_name.has_property(property.value):
                    error["message"] = f"{object_name.name} object has no property '{property.value}'"
                    raise Al_PropertyError(error)
                property_value = object_name.properties[property.value]
                if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                    new_value = setNumber(property_value.value) + 1
                    new_value = Number(new_value)
                    object_name.properties[property.value] = new_value
                    return res.success(object_name.properties[property.value])
                else:
                    error["message"] = f"'++' not supported for type '{TypeOf(property_value).getType()}'"
                    raise Al_TypeError(error)
        if operation != None and operation == "--":
            if isinstance(object_name, Object) or isinstance(object_name, Dict) or isinstance(object_name, Class):
                if not object_name.has_property(property.value):
                    error["message"] = f"{object_name.name} object has no property '{property.value}'"
                    raise Al_PropertyError(error)
                property_value = object_name.properties[property.value]
                if isinstance(property_value, Number) or isinstance(property_value, Boolean):
                    new_value = setNumber(property_value.value) + 1
                    new_value = Number(new_value)
                    object_name.properties[property.value] = new_value
                    return res.success(object_name.properties[property.value])
                else:
                    error["message"] = f"'--' not supported for type '{TypeOf(property_value).getType()}'"
                    raise Al_TypeError(error)

        if isinstance(object_name, Class):
            if type(property).__name__ == "Token":
                name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                var_name = context.symbolTable.get(name)
                if isinstance(var_name,dict):
                    if var_name['type'] == "freeze" or var_name['type'] == "final":
                            if property.value in object_name.properties:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{property.value}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot set '{property.value}' on immutable object",
                                    'context': context,
                                    'exit': False
                                })
                if hasattr(object_name, "properties"):
                    if is_static(property.value):
                        Program.printError(f"Warning: assignment to static property '{property.value}' \nCannot modify static property '{property.value}'")
                    else:
                        object_name.properties[property.value] = value

                if property.value in class_methods:
                    error["message"] = f"'class' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, BuiltInClass):
            if property.value in object_name.properties:
                object_name.properties[property.value] = value
            else:
                error['name'] = String("TypeError")
                error["message"] = f"cannot set '{property.value}' on immutable type '{TypeOf(object_name).getType()}'"
                raise Al_TypeError(error)

        elif isinstance(object_name, Dict):
            if type(property).__name__ == "Token":
                name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                var_name = context.symbolTable.get(name)
                if isinstance(var_name,dict):
                    if var_name['type'] == "freeze" or var_name['type'] == "final":
                            if property.value in object_name.properties:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{property.value}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot set '{property.value}' on immutable object",
                                    'context': context,
                                    'exit': False
                                })
                if hasattr(object_name, "properties"):
                   object_name.properties[property.value] = value

                if property.value in dict_methods:
                    error["message"] = f"'dict' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, Object):
            if type(property).__name__ == "Token":
                name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                var_name = context.symbolTable.get(name)
                if isinstance(var_name,dict):
                    if var_name['type'] == "freeze" or var_name['type'] == "final":
                            if property.value in object_name.properties:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{property.value}'",
                                    'context': context,
                                    'exit': False
                                })
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"cannot set '{property.value}' on immutable object",
                                    'context': context,
                                    'exit': False
                                })
                if property.value in object_methods:
                    error["message"] = f"'object' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)
                else:
                    error['name'] = String("TypeError")
                    error["message"] = f"cannot set '{property.value}' on immutable type 'object'"
                    raise Al_TypeError(error)

        elif isinstance(object_name, Function):
            if type(property).__name__ == "Token":
                if hasattr(object_name, "properties"):
                    object_name.properties[property.value] = value
                if property.value in function_methods:
                    error["message"] = f"'function' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, List):
            if type(property).__name__ == "Token":
                
                if property.value in list_methods:
                    error["message"] = f"'list' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)
                else:
                    error["message"] = f"'list' object has no property '{property.value}'"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, Pair):
            if type(property).__name__ == "Token":
                if property.value in pair_methods:
                    error["message"] = f"'pair' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)
                else:
                    error['name'] = String("TypeError")
                    error["message"] = f"cannot set '{property.value}' on immutable type 'pair'"
                    raise Al_TypeError(error)

        elif isinstance(object_name, String):
            if type(property).__name__ == "Token":
                if property.value in string_methods:
                    error["message"] = f"'string' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)
                else:
                    error["message"] = f"'string' object has no property '{property.value}'"
                    raise Al_PropertyError(error)

        elif isinstance(object_name, Number):
            if type(property).__name__ == "Token":
                if property.value in number_methods:
                    error["message"] = f"'number' object property '{property.value}' is read-only"
                    raise Al_PropertyError(error)
                else:
                    error["message"] = f"'{TypeOf(object_name).getType()}' object has no property '{property.value}'"
                    raise Al_PropertyError(error)

        else:
            if type(property).__name__ == "Token":
                error['name'] = String("TypeError")
                error["message"] = f"type '{TypeOf(object_name).getType()}' object has no property '{property.value}'"
                raise Al_TypeError(error)


    def visit_IndexNode(self, node, context):
        res = RuntimeResult()
        index_value = res.register(self.visit(node.name, context))
        index  = res.register(self.visit(node.index, context))
        type_ = node.type
        value_ = res.register(self.visit(node.value, context))
        if res.should_return(): return res
        object_type = TypeOf(index_value).getType()
        index_type = TypeOf(index).getType()
        if object_type == "list":
            if index_type == "int":
                try:
                    get_value = index_value.elements[index.value]
                    if type_ == "=":
                        name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                        var_name = context.symbolTable.get(name)
                        if isinstance(var_name,dict):
                            if var_name['type'] == "freeze" or var_name['type'] == "final":
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{index.value}'",
                                    'context': context,
                                    'exit': False
                                })
                        index_value.elements[index.value] = value_
                    return res.success(get_value)
                except IndexError:
                    raise Al_IndexError({
                        'name': String("IndexError"),
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"list index out of range",
                        'context': context,
                        'exit': False
                    })
                except AttributeError:
                     pass
            else:
                raise Al_TypeError({
                    'name': String("TypeError"),
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"list indices must be integers or slices, not {index_type}",
                    'context': context,
                    'exit': False
                })

        elif object_type == "pair":
            if index_type == "int":
                try:
                    get_value = index_value.elements[index.value]
                    if type_ == "=":
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"assignment on immutable object",
                            'context': context,
                            'exit': False
                        })
                    return res.success(get_value)
                except IndexError:
                    raise Al_IndexError({
                        'name': "IndexError",
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"pair index out of range",
                        'context': context,
                        'exit': False
                    })
                except AttributeError:
                    pass
            else:
                raise Al_TypeError({
                    'name': String("TypeError"),
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"pair indices must be integers or slices, not {index_type}",
                    'context': context,
                    'exit': False
                })

        elif object_type == "dict" or object_type == "object":
                try:
                    if type_ == "=":
                        name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                        var_name = context.symbolTable.get(name)
                        if isinstance(var_name,dict):
                            if var_name['type'] == "freeze":
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{index.value}'",
                                    'context': context,
                                    'exit': False
                                })
                        index_value.properties[index.value] = value_
                    else:
                        get_value = index_value.properties[index.value]
                        return res.success(get_value)
                except KeyError:
                    raise Al_KeyError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"{index}",
                        'context': context,
                        'exit': False
                    })
                except AttributeError:
                    pass

        elif object_type == "string":
            if index_type == "int":
                try:
                    get_value = index_value.value[index.value]
                    if type_ == "=":
                        name = node.name.value if hasattr(node.name, "value") else node.name.id.value
                        var_name = context.symbolTable.get(name)
                        if isinstance(var_name,dict):
                            if var_name['type'] == "freeze":
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"assignment to read-only property: '{index.value}'",
                                    'context': context,
                                    'exit': False
                                })
                        index_value.value[index.value] = value_
                    return res.success(String(get_value))
                except IndexError:
                    raise Al_IndexError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': "string index out of range",
                        'context': context,
                        'exit': False
                    })
                except AttributeError:
                    pass
            else:
                raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': "string indices must be integers",
                    'context': context,
                    'exit': False
                })

        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"'{node.name.id.value}' object is not subscriptable" if hasattr(node.name, 'id') and hasattr(node.name.id, 'value') else f"'{TypeOf(index_value).getType()}' object is not subscriptable",
                'context': context,
                'exit': False
            })


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
                if not step or step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.elements[start.value::end.value]
                            return res.success(List(get_value))
                        except IndexError:
                           raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            })
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(List(index_value.elements[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            if end.value == 0:
                                raise Al_ValueError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"slice step cannot be zero",
                                    'context': context,
                                    'exit': False
                                })
                            get_value = index_value.elements[::end.value]
                            return res.success(List(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            })

                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.elements[start.value::]
                            return res.success(List(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"list index out of range",
                                'context': context,
                                'exit': False
                            })
                    else:
                        raise Al_TypeError({
                            'name': String("TypeError"),
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"list indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        })
                
            else:
                if step and step.value == 0:
                    raise Al_ValueError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"slice step cannot be zero",
                        'context': context,
                        'exit': False
                    })
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
                    raise Al_TypeError({
                        'name': String("TypeError"),
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"slice indices must be integers, not {start_type} and {end_type}",
                        'context': context,
                        'exit': False
                    })

        elif object_type == "pair":
            if type_ == "double_colon":
                if not step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.elements[start.value::end.value]
                            return res.success(Pair(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            })
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(Pair(index_value.elements[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            if end.value == 0:
                                raise Al_ValueError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"slice step cannot be zero",
                                    'context': context,
                                    'exit': False
                                })
                            get_value = index_value.elements[::end.value]
                            return res.success(Pair(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            })
                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.elements[start.value::]
                            return res.success(Pair(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'name': String("IndexError"),
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"pair index out of range",
                                'context': context,
                                'exit': False
                            })
                    else:
                        raise Al_TypeError({
                            'name': String("TypeError"),
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"pair indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        })
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
                    raise Al_TypeError({
                    'name': String("TypeError"),
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"slice indices must be integers, not {start_type} and {end_type}",
                    'context': context,
                    'exit': False
                })

        elif object_type == "string":
            if type_ == "double_colon":
                if not step:
                    if start_type == "int" and end_type == "int":
                        try:
                            get_value = index_value.value[start.value::end.value]
                            return res.success(String(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            })
                    elif start_type == "NoneType" and end_type == "NoneType":
                        return res.success(String(index_value.value[::]))
                    elif start_type == "NoneType" and end_type == "int":
                        try:
                            if end.value == 0:
                                raise Al_ValueError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'message': f"slice step cannot be zero",
                                    'context': context,
                                    'exit': False
                                })
                            get_value = index_value.value[::end.value]
                            return res.success(String(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            })
                    elif start_type == "int" and end_type == "NoneType":
                        try:
                            get_value = index_value.value[start.value::]
                            return res.success(String(get_value))
                        except IndexError:
                            raise Al_IndexError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'message': f"string index out of range",
                                'context': context,
                                'exit': False
                            })
                    else:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'message': f"string indices must be integers or slices, not {start_type}",
                            'context': context,
                            'exit': False
                        })
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
                    raise Al_TypeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"string indices must be integers, not {start_type} and {end_type}",
                    'context': context,
                    'exit': False
                })

        else:
            raise Al_TypeError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"{object_type} cannot be sliced",
                'context': context,
                'exit': False
            })


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
                elif hasattr(element, 'properties'):
                    new_list.append(element.properties)
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
                elif hasattr(element, 'properties'):
                    new_list += (element.properties,)
                else:
                    new_list += (element,)

            context.symbolTable.set(var_name, List(new_list), assign_token)

        elif isinstance(value, String):
            new_string = ""
            for element in value.value:
                new_string += element
            context.symbolTable.set(var_name, String(new_string), assign_token)


    def visit_ImportNode(self, node, context):
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
        module_from_name = node.from_module_name
        module_name_as = node.module_name_as.value if hasattr(node.module_name_as, 'value') else node.module_name_as
        properties_list = node.properties
        mods = node.mods
        current_dir_name = os.path.dirname(node.pos_start.fileName)
        curr_dir = os.path.basename(current_dir_name)
        module_path_ = module_name
        if node.module_path != None:
            if len(node.module_path) == 1:
                calling_module_path = node.pos_start.fileName
                current_dir_name = os.path.realpath(os.path.dirname(calling_module_path))
                curr_dir = os.path.basename(current_dir_name)
                paths = []
                for path in node.module_path:
                    paths = [curr_dir] + [path]
                module_path = create_module_path(paths)[0]

                module_path_ = create_module_path(paths)[1]
            else:
                module_path = create_module_path(node.module_path)[0]
                module_path_ = create_module_path(node.module_path)[1]
        else:
            calling_module_path = node.pos_start.fileName
            current_dir_name = os.path.realpath(os.path.dirname(calling_module_path))
            curr_dir = os.path.basename(current_dir_name)
            if not module_name in builtin_modules:
                module_path =  curr_dir + "/" + module_name + '.ald'
                module_path_ = module_name
            else:
                module_path = module_name + '.ald'
                module_path_ = module_name

        module = Program.runFile(module_path)
        path = module_path
        if module == None:
            if mods != None and len(mods) > 0:
                module_object = None
                for mod in mods:
                    module_path = mod.value
                    module_name = mod.value
                    if module_path in builtin_modules:
                        if  context.symbolTable.modules.is_module_in_members(module_name):
                            pass
                        else:
                            try:
                                if properties_list != None and len(properties_list) > 0:
                                    module_from_name = node.from_module_name.value if node.from_module_name != None else node.module_name.value
                                path = f"./lib/{module_path}/@{module_path}.ald"
                                module = builtin_modules[module_path](path)
                                if node.module_alias is not None:
                                    module_name = node.module_alias.value
                                module_object = Program.createModule(path, module_name, module_from_name, module, None, context, True, node.pos_start, node.pos_end)
                            except RecursionError:
                                    error['message'] = f"cannot import name '{module_name}' from '{module_path}' (most likely due to a circular import)"
                                    raise Al_ImportError(error)
                            except FileNotFoundError:
                                error['message'] = f"cannot import name '{module_name}' from '{module_path}' (file does not exist)"
                                raise Al_ImportError(error)
                            except Exception as e:
                                name = type(e).__name__
                                if name.split('_')[0] == 'Al':
                                    raise e
                                else:
                                    error['message'] = f"cannot import name '{module_name_as}' (most likely due to a circular import)"

                    else:
                        error['message'] = "Module '{}' not found".format(
                            module_name_as)
                        raise Al_ModuleNotFoundError(error)
                if isinstance(module_object, tuple) and module_object[0] == None:
                    error['message'] = f"cannot import name '{module_object[1]}' from '{module_path_}'"
                    raise Al_ImportError(error)
                if not isinstance(module_object, tuple) and module_object == None:
                    raise Al_SyntaxError(error)
                else:
                    context.symbolTable.modules.add_module(
                        module_name, module_object)
                    return res.success(module_object)
            else:
                name = node.module_name.value if properties_list == None else node.module_path[0]
                module_path = name
                if module_path in builtin_modules:
                    if  context.symbolTable.modules.is_module_in_members(module_name):
                        pass
                    else:
                        try:
                            if properties_list != None and len(properties_list) > 0:
                                module_from_name = node.from_module_name.value if node.from_module_name != None else node.module_name.value
                            path = f"./lib/{module_path}/@{module_path}.ald"
                            module = builtin_modules[module_path](path)
                            if node.module_alias is not None:
                                module_name = node.module_alias.value
                            module_object = Program.createModule(path,module_name,module_from_name, module, properties_list, context, True, node.pos_start, node.pos_end)
                            if isinstance(module_object, tuple) and module_object[0] == None:
                                error['message'] = f"cannot import name '{module_object[1]}' from '{module_path_}'"
                                raise Al_ImportError(error)
                            if not isinstance(module_object, tuple) and module_object == None:
                                raise Al_SyntaxError('error')
                            else:
                                context.symbolTable.modules.add_module(module_name, module_object)
                                return res.success(module_object)
                        except RecursionError:
                                error['message'] = f"cannot import name '{module_name}' from '{module_path}' (most likely due to a circular import)"
                                raise Al_ImportError(error)
                        except FileNotFoundError:
                            error['message'] = f"cannot import name '{module_name}' from '{module_path}' (file does not exist)"
                            raise Al_ImportError(error)
                        except Exception as e:
                            name = type(e).__name__
                            if name.split('_')[0] == 'Al':
                                raise e
                            else:
                                error['message'] = f"cannot import name '{module_name_as}' (most likely due to a circular import)"
                else:
                    error['message'] = "Module '{}' not found".format(
                        module_name_as)
                    raise Al_ModuleNotFoundError(error)
        else:
            if  context.symbolTable.modules.is_module_in_members(module_name):
                pass
            # if context.symbolTable.modules.is_path_in_members(module_path):
            #     module = context.symbolTable.modules.get_module(module_name)
            else:
                try:
                    if node.module_alias is not None:
                        module_name = node.module_alias.value
                    if properties_list != None and len(properties_list) > 0:
                            module_from_name = node.from_module_name.value if node.from_module_name != None else node.module_name.value
                    module_object = Program.createModule(path,module_name, module_from_name, module, properties_list, context, False, node.pos_start, node.pos_end)
                    if isinstance(module_object, tuple) and module_object[0] == None:
                        error['message'] = f"cannot import name '{module_object[1]}' from '{module_path_}'"
                        raise Al_ImportError(error)
                    if not isinstance(module_object, tuple) and module_object == None:
                        raise Al_SyntaxError(error)
                    else:
                        context.symbolTable.modules.add_module(module_name, module_object)
                        context.symbolTable.modules.add_path(module_path, module_name)
                        return res.success(module_object)
                except RecursionError:
                    error['message'] = f"cannot import name '{module_name}' from '{module_path}' (most likely due to a circular import)"
                    raise Al_ImportError(error)
                except FileNotFoundError:
                        error['message'] = f"cannot import name '{module_name}' from '{module_path}' (file does not exist)"
                        raise Al_ImportError(error)
                except Exception as e:
                    name = type(e).__name__
                    if name.split('_')[0] == 'Al':
                        raise e
                    else:
                        error['message'] = f"cannot import name '{module_name_as}' (most likely due to a circular import)"


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
            elif node.op_tok.type == tokenList.TT_FLOOR_DIV:
                result, error = left.floordivided_by(right)
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
                raise Al_RuntimeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': error,
                    'context': context,
                    'exit': False
                })
            else:
                return res.success(result.setPosition(node.pos_start, node.pos_end))
        except KeyboardInterrupt:
            pass


    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        error = None
        if node.op_tok.type == tokenList.TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(tokenList.TT_KEYWORD, 'not'):
            if isinstance(number, Pair):
                for i in range(len(number.elements)):
                    number = Number(number.elements[i].value)
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
                if res.should_return(): return res
                return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if return_null else expr_value)
            else:
                if  hasattr(condition_value, 'is_true') and condition_value.is_true():
                    expr_value = res.register(self.visit(expr, context))
                    if res.should_return(): return res
                    return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if return_null else expr_value)
        if node.else_case:
            expr, return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if return_null else else_value)

        return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []
        try:
            start_value = res.register(self.visit(node.start_value_node, context))
            if res.should_return():
                return res
            end_value = res.register(self.visit(node.end_value_node, context))
            if res.should_return() :
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
                if type(node.end_value_node).__name__ == 'CallNode':
                    name = node.end_value_node.node_to_call.value if hasattr(node.end_value_node.node_to_call, 'value') else node.end_value_node.node_to_call.id.value if hasattr(node.end_value_node.node_to_call, 'id') else node.end_value_node.node_to_call
                    if name == "range":
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"For loop not supported with range()",
                            'exit': False
                        })
                if not isinstance(start_value, Number) or not isinstance(end_value, Number) or not isinstance(step_value, Number):
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"For loop not supported between '{TypeOf(start_value).getType()}' and '{TypeOf(end_value).getType()}'",
                            'exit': False
                        })
                if type(end_value.value) == float:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"For loop not supported between '{TypeOf(start_value).getType()}' and '{TypeOf(end_value).getType()}'",
                            'exit': False
                        })

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
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
        return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_InNode(self, node, context):
        res = RuntimeResult()
        if type(node.iterable_node).__name__ == 'ListNode' or type(node.iterable_node).__name__ == 'PairNode' or type(node.iterable_node).__name__ == 'DictNode' or type(node.iterable_node).__name__ == 'ObjectNode' or type(node.iterable_node).__name__ == 'ModuleNode' or type(node.iterable_node).__name__ == 'StringNode':
            iterable_node = res.register(self.visit(node.iterable_node, context))
        else:
            iterable_node = res.register(self.visit(node.iterable_node, context))

        iterators = node.iterators
        if type(iterable_node) == dict:
            iterable_node = iterable_node['value']
        value = ""
        elements = []
        try:
            if type(iterable_node).__name__ == "NoneType":
                raise Al_RuntimeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': f"type 'NoneType' is not iterable",
                        'exit': False
                    })


            if isinstance(iterable_node, Object) or isinstance(iterable_node, Dict) or isinstance(iterable_node, Module):
                end_value = iterable_node.get_length()
                values = []
                if res.should_return() :
                    return res
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
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res

                            if res.loop_continue:
                                continue

                            if res.loop_break:
                                break
                        else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': 'cannot assign to non-identifier',
                                    'exit': False
                                })
                    elif len(iterators) > 1:
                        if type(iterators[0]).__name__ == "VarAccessNode" and type(iterators[1]).__name__ == "VarAccessNode":
                            # create a new pair
                            len_iterators = len(iterators)
                            pair = (iterable_node.get_keys(), iterable_node.get_values())
                            len_iterable_node = len(pair)
                            if len_iterators > len_iterable_node:
                                raise Al_ValueError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': f"Too many values to unpack (expected {len_iterable_node}, got {len_iterators})",
                                    'exit': False
                                })
                            elif len_iterators < len_iterable_node:
                                raise Al_ValueError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': f"Not enough values to unpack (expected {len_iterable_node}, got {len_iterators})",
                                    'exit': False
                                })
                            else:
                                key, value = pair[0][i], pair[1][i]
                                context.symbolTable.set(iterators[0].id.value, key)
                                context.symbolTable.set(iterators[1].id.value, value)
                                value = res.register(self.visit(node.body_node, context))
                                elements.append(value)
                                # key, value = pair[0][i], pair[1][i]
                                # context.symbolTable.set(iterators[0].id.value, key)
                                # context.symbolTable.set(iterators[1].id.value, value)
                                # value = res.register(self.visit(node.body_node, context))
                                # elements.append(value)

                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })

            elif isinstance(iterable_node, List):
                end_value = len(iterable_node.elements)
                if res.should_return() :
                    return res
                for i in range(end_value):
                    if len(iterators) == 1:
                        if type(iterators[0]).__name__ == "VarAccessNode":
                            context.symbolTable.set(iterators[0].id.value, iterable_node.elements[i])
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res

                            if res.loop_continue:
                                continue

                            if res.loop_break:
                                break
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                    elif len(iterators) == 2:
                        iterators_keys = []
                        for iterator in iterators:
                            if type(iterator).__name__ == "VarAccessNode":
                                iterators_keys.append(iterator.id.value)
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': 'cannot assign to non-identifier',
                                    'exit': False
                                })
                        is_iterable = False
                        for iterable in iterable_node.elements:
                            if isinstance(iterable, Pair) or isinstance(iterable, List):
                                if len(iterable.elements) == 2:
                                    is_iterable = True
                                else:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'context': context,
                                        'message': f"Too many values to unpack (expected {len(iterators)}, got {len(iterable.elements)})",
                                        'exit': False
                                    })

                            
                        
                        
                        if is_iterable:
                            context.symbolTable.set(iterators_keys[0], iterable_node.elements[i].elements[0])
                            context.symbolTable.set(iterators_keys[1], iterable_node.elements[i].elements[1])
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                                'exit': False
                            })
                    else:
                        iterators_keys = []
                        for iterator in iterators:
                            if type(iterator).__name__ == "VarAccessNode":
                                iterators_keys.append(iterator.id.value)
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': 'cannot assign to non-identifier',
                                    'exit': False
                                })
                        is_iterable = False
                        for iterable in iterable_node.elements:
                            if isinstance(iterable, Pair) or isinstance(iterable, List):
                                if len(iterable.elements) == len(iterators):
                                    is_iterable = True
                                else:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'context': context,
                                        'message': f"Too many values to unpack (expected {len(iterators)}, got {len(iterable.elements)})",
                                        'exit': False
                                    })

                        if is_iterable:
                            for j in range(len(iterators)):
                                context.symbolTable.set(
                                    iterators_keys[j], iterable_node.elements[i].elements[j])

                            value = res.register(self.visit(
                                node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                                'exit': False
                            })
                        
            elif isinstance(iterable_node, Pair):
                is_iterable = False
                end_value = len(iterable_node.elements)
                if res.should_return() :
                    return res
                for i in range(end_value):
                    if len(iterators) == 1:
                        if type(iterators[0]).__name__ == "VarAccessNode":
                            context.symbolTable.set(iterators[0].id.value, iterable_node.elements[i])
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res

                            if res.loop_continue:
                                continue

                            if res.loop_break:
                                break
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                    elif len(iterators) == 2:
                        iterators_keys = []
                        for iterator in iterators:
                            if type(iterator).__name__ == "VarAccessNode":
                                iterators_keys.append(iterator.id.value)
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': 'cannot assign to non-identifier',
                                    'exit': False
                                })
                        
                        for iterable in iterable_node.elements:
                            if isinstance(iterable, Pair) or isinstance(iterable, List):
                                if len(iterable.elements) == 2:
                                    is_iterable = True
                                else:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'context': context,
                                        'message': f"Too many values to unpack (expected {len(iterators)}, got {len(iterable.elements)})",
                                        'exit': False
                                    })

                            
                        if is_iterable:
                            context.symbolTable.set(iterators_keys[0], iterable_node.elements[i].elements[0])
                            context.symbolTable.set(iterators_keys[1], iterable_node.elements[i].elements[1])
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                                'exit': False
                            })
                    else:
                        iterators_keys = []
                        for iterator in iterators:
                            if type(iterator).__name__ == "VarAccessNode":
                                iterators_keys.append(iterator.id.value)
                            else:
                                raise Al_TypeError({
                                    'pos_start': node.pos_start,
                                    'pos_end': node.pos_end,
                                    'context': context,
                                    'message': 'cannot assign to non-identifier',
                                    'exit': False
                                })
                        is_iterable = False
                        for iterable in iterable_node.elements:
                            if isinstance(iterable, Pair) or isinstance(iterable, List):
                                if len(iterable.elements) == len(iterators):
                                    is_iterable = True
                                else:
                                    raise Al_ValueError({
                                        'pos_start': node.pos_start,
                                        'pos_end': node.pos_end,
                                        'context': context,
                                        'message': f"Too many values to unpack (expected {len(iterators)}, got {len(iterable.elements)})",
                                        'exit': False
                                    })
                                    
                      
                        if is_iterable:
                            for j in range(len(iterators)):
                                context.symbolTable.set(iterators_keys[j], iterable_node.elements[i].elements[j])
                                
                            
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False: 
                                return res
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f'cannot iterate with type {TypeOf(iterable_node.elements[i]).getType()}',
                                'exit': False
                            })  
                        
                        
                        
                        
            elif isinstance(iterable_node, String):
                end_value = len(iterable_node.value)
                if res.should_return() :
                    return res
                for i in range(end_value):
                    if len(iterators) == 1:
                        if type(iterators[0]).__name__ == "VarAccessNode":
                            new_list = list(iterable_node.value)
                            context.symbolTable.set(iterators[0].id.value, String(new_list[i]))
                            value = res.register(self.visit(node.body_node, context))
                            elements.append(value)
                            if res.should_return() and res.loop_continue == False and res.loop_break == False:
                                return res

                            if res.loop_continue:
                                continue

                            if res.loop_break:
                                break
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': 'cannot assign to non-identifier',
                                'exit': False
                            })
                    elif len(iterators) == 2:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f'cannot iterate with type {TypeOf(iterable_node.value[i]).getType()}',
                                'exit': False
                            })

            else:
                raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': f"type '{TypeOf(iterable_node).getType()}'' is not iterable",
                        'exit': False
                    })
        except KeyboardInterrupt:
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })
        return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


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
            raise Al_KeyboardInterrupt({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"KeyboardInterrupt",
                'context': context,
                'exit': False
            })

        return res.success(NoneType().setContext(context).setPosition(node.pos_start, node.pos_end) if node.return_null else List(elements).setContext(context).setPosition(node.pos_start, node.pos_end))


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
        if default_case:
            value = res.register(self.visit(default_case['body'], context))
            if res.should_return(): return res
            return res.success(value)


    def visit_RaiseNode(self, node, context):
        res = RuntimeResult()
        if type(node.expression).__name__ != "CallNode":
            exception = res.register(self.visit(node.expression, context))
            if res.should_return(): return res
            if type(exception).__name__ == "BuiltInClass" and exception.name in builtin_exceptions:
                args = [exception.properties["message"]]

                if  exception.name in builtin_exceptions:
                    attr = builtin_exceptions[exception.name].__name__
                    attr_name = attr.split("Al_")[1]
                    exception = f'BuiltInClass_{attr_name}'
                    if exception in globals():
                        return globals()[exception](args, node, context, "raise")
            else:
                if isinstance(exception, Class) or isinstance(exception, BuiltInClass):
                    if exception.inherit_class_name.class_name not in builtin_exceptions:
                        if exception.inherit_class_name.inherit_class_name.class_name in builtin_exceptions:
                            if exception.properties["message"] == None or exception.properties["message"] == "":
                                raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f"'{exception.class_name}' object is not callable",
                                'exit': False
                            })
                            args = [exception.properties["message"]]
                            # since this is a user defined exception, we just need to return the exception
                            return BuiltInClass_Exception(args, node, context, "raise", exception.class_name)
                        else:
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f"exceptions must be of type Exception",
                                'exit': False
                            })
                    else:
                        if exception.properties["message"] == None or exception.properties["message"] == "":
                            raise Al_TypeError({
                                'pos_start': node.pos_start,
                                'pos_end': node.pos_end,
                                'context': context,
                                'message': f"'{exception.class_name}' object is not callable",
                                'exit': False
                            })
                        args = [exception.properties["message"]]
                        # since this is a user defined exception, we just need to return the exception
                        return BuiltInClass_Exception(args, node, context, "raise", exception.class_name)
                else:
                    raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': f"exceptions must be of type Exception",
                        'exit': False
                    })
        else:
            if type(node.expression.node_to_call).__name__ == "VarAccessNode":
                if not hasattr(node.expression, 'node_to_call'):
                    raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': f"type '{TypeOf(node.expression).getType()}'' is not callable",
                        'exit': False
                    })
                name = node.expression.node_to_call.id.value
                if not name in builtin_exceptions:
                    exception = context.symbolTable.get(name)
                    if exception == None:
                        raise Al_NameError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"name '{node.expression.node_to_call.id.value}' is not defined",
                            'exit': False
                        })
                    else:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"exceptions must be of type Exception",
                            'exit': False
                        })
                else:
                    args_nodes = node.expression.args_nodes
                    args = []
                    for arg_node in args_nodes:
                        args.append(res.register(self.visit(arg_node, context)))
                        if res.should_return(): return res
                    if name in builtin_exceptions:
                        attr = builtin_exceptions[name].__name__
                        attr_name = attr.split("Al_")[1]
                        exception = f'BuiltInClass_{attr_name}'
                        if exception in globals():
                            return globals()[exception](args, node, context, "raise")


    def visit_AttemptNode(self, node, context):
        res = RuntimeResult()
        attempt_statement = node.attempt_statement
        catches = node.catches
        exceptions_names = []
        finally_statement = node.finally_statement
        for catch in catches:
            exception = catch['exception']
            if exception:
                exception_name = exception["name"].value
                exceptions_names.append(exception_name)
        for name in exceptions_names:
            if not name in builtin_exceptions:
                exceptionName = name
                name = context.symbolTable.get(name)
                if name == None:
                    raise Al_NameError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'context': context,
                        'message': f"name '{exceptionName}' is not defined",
                        'exit': False
                    })
                else:
                    if isinstance(name, Class) or isinstance(name, BuiltInClass):
                        if  name.inherit_class_name == None:
                            raise Al_TypeError({
                                'pos_start': [catch['pos_start'] for catch in catches][0] if len(catches) > 0 else node.pos_start,
                                'pos_end': [catch['pos_end'] for catch in catches][0] if len(catches) > 0 else node.pos_end,
                                'context': context,
                                'message': f"exceptions must be of type Exception",
                                'exit': False
                            })
                        if name.inherit_class_name.class_name not in builtin_exceptions:
                            raise Al_TypeError({
                                'pos_start': [catch['pos_start'] for catch in catches][0] if len(catches) > 0 else node.pos_start,
                                'pos_end': [catch['pos_end'] for catch in catches][0] if len(catches) > 0 else node.pos_end,
                                'context': context,
                                'message': f"exceptions must be of type Exception",
                                'exit': False
                            })
                        else:
                            exception_name = name.inherit_class_name.class_name
                    else:
                        raise Al_TypeError({
                            'pos_start': node.pos_start,
                            'pos_end': node.pos_end,
                            'context': context,
                            'message': f"exceptions must be of type Exception",
                            'exit': False
                        })
        try:
            value = res.register(self.visit(attempt_statement['body'], context))
            if res.should_return(): return res
            return res.success(value)
        except Exception as attempt_exception:
            for catch in catches:
                exception = catch['exception']
                if exception:
                    exception_name = exception["name"].value
                    exceptions_names.append(exception_name)
                if catch != None and catch != {}:
                    if exception:
                        exception_error = Dict({
                                    'name': attempt_exception.name if isinstance(attempt_exception.name, String) else String(attempt_exception.name),
                                    'message': attempt_exception.message['message'] if isinstance(attempt_exception.message['message'], String) else String(attempt_exception.message['message']),
                        })
                        exception_name = exception["name"].value
                        if not exception_name in builtin_exceptions:
                            name = context.symbolTable.get(exception_name)
                            exception_name =  "Exception"
                            exception_error.properties["name"] = name.class_name if isinstance(name.class_name, String) else String(name.class_name)
                        exception_name_as = exception["as"]
                        if  attempt_exception.name == exception_name or exception_name == "Exception":

                                if exception_name_as != None:
                                    context.symbolTable.set(exception_name_as.value, exception_error)
                                try:
                                    value = res.register(self.visit(catch['body'], context))
                                    if res.should_return(): return res
                                    return res.success(value)
                                except Exception as catch_exception:
                                    Program.printError("\nAnother exception occurred while handling the above exception: \n")
                                    raise catch_exception
                    else:
                        try:
                            value = res.register(self.visit(catch['body'], context))
                            if res.should_return(): return res
                            return res.success(value)
                        except Exception as catch_exception:
                            Program.printError("\nAnother exception occurred while handling the above exception: \n")
                            raise catch_exception
            raise attempt_exception
        finally:
            if finally_statement:
                res.register(self.visit(finally_statement['body'], context))
                if res.should_return(): return res


    def visit_FunctionNode(self, node, context):
        res = RuntimeResult()
        def_name = node.def_name_token.value if node.def_name_token else "none"
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.args_name_tokens]
        _properties = {}
        defualt_values = node.default_values
        _type = node.type
        doc = node.doc
        if doc != None:
            doc = res.register(self.visit(doc, context))
        if _type == None:
            _type = "function"
        

        
        def_value = Function(def_name, body_node, arg_names, node.implicit_return, defualt_values, _properties, _type, doc, context).setContext(
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
            properties = {**properties, **{prop_name: prop_value}}
            if res.should_return(): return res
            object_value = Object(object_name, properties).setContext(context).setPosition(node.pos_start, node.pos_end)
            if isinstance(prop_value, NoneType):
                object_value = Object(object_name, {}).setContext(
                    context).setPosition(node.pos_start, node.pos_end)
                # already_defined = context.symbolTable.get(object_name)

                # if already_defined:
                #     if isinstance(already_defined, Object):
                #         raise Al_RuntimeError({
                #             "pos_start": node.pos_start,
                #             "pos_end": node.pos_end,
                #             "message": "Object with name '{}' already defined".format(object_name),
                #             "context": context,
                #             "exit": False
                #         }))
                #     else:
                #         raise Al_RuntimeError({
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
        for prop in node.properties:
            key = prop['key'].value
            value = res.register(self.visit(prop['value'], context))
            if res.should_return(): return res
            properties = {**properties, **{key: value}}
        return res.success(Dict(properties, None,None,context).setContext(context).setPosition(node.pos_start, node.pos_end))


    def visit_ClassNode(self, node, context):
        res = RuntimeResult()
        class_name = node.class_name.value
        inherits_class_name = node.inherits_class_name
        class_args = []
        class_fields_modifiers = node.class_fields_modifiers
        inherited_from = None
        if inherits_class_name != None:
            if type(inherits_class_name).__name__ == 'list':
                raise Al_RuntimeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"multiple inheritance not supported",
                    'context': context,
                    'exit': False
                })
            inherits_class_name_ = inherits_class_name.value if hasattr(inherits_class_name, 'value') else inherits_class_name
            inherits_class_name = context.symbolTable.get(inherits_class_name_)
            inherited_from = inherits_class_name
            if inherits_class_name_ == class_name:
                raise Al_RuntimeError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"a class cannot inherit from itself",
                    'context': context,
                    'exit': False
                })
            if inherits_class_name == None:
                raise Al_NameError({
                    'pos_start': node.pos_start,
                    'pos_end': node.pos_end,
                    'message': f"name '{node.inherits_class_name.value}' is not defined",
                    'context': context,
                    'exit': False
                })
            if isinstance(inherits_class_name, dict):
                inherits_class_name = inherits_class_name['value']
                inherited_from = inherits_class_name
            if not isinstance(inherits_class_name, Class):
                if isinstance(inherits_class_name, BuiltInClass):
                    inherited_from = inherits_class_name
                else:
                    raise Al_TypeError({
                        'pos_start': node.pos_start,
                        'pos_end': node.pos_end,
                        'message': f"cannot inherit from non-class type '{TypeOf(inherits_class_name).getType()}'",
                        'context': context,
                        'exit': False
                    })
        _properties = {}
        class_value = {}
        class_methods = {}
        methods = {}
        doc = node.doc
        if doc != None:
            doc = res.register(self.visit(doc, context))
        if class_fields_modifiers != None:
            if len(class_fields_modifiers) > 0:
                for modifier in class_fields_modifiers:
                    name = modifier['name'].value
                    value = res.register(self.visit(modifier['value'], context))
                    if res.should_return(): return res
                    methods = {**methods, **{name: value}}

        if node.methods != '' and node.methods != None:
            for method in node.methods:
                method_name = method['name'].value
                # if method_name == '__@init__':
                #     for arg in method['args']:
                #         class_args.append(arg)
                method_value = res.register(self.visit(method['value'], context))
                if res.should_return(): return res

                class_methods = {**methods, **{method_name: method_value}}
                methods = {**methods, **{method_name: method_value}}
                class_value = Class(class_name, class_args,inherits_class_name,inherited_from,
                                     class_methods,methods,class_fields_modifiers,doc,context).setContext(context).setPosition(node.pos_start, node.pos_end)
                context.symbolTable.set_object(class_name, class_value)
        else:
            class_value = Class(class_name, class_args,inherits_class_name, inherited_from,
                                {},{},class_fields_modifiers, doc,context).setContext(context).setPosition(node.pos_start, node.pos_end)
            context.symbolTable.set_object(class_name, class_value)

        return res.success(class_value)


    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        args = []
        keyword_args_list = node.keyword_args_list
        value_to_call = res.register(self.visit(
            node.node_to_call, context)) if node.node_to_call else None
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().setPosition(
            node.pos_start, node.pos_end) if hasattr(value_to_call, 'copy') else value_to_call

        if not isinstance(value_to_call, Function) and not isinstance(value_to_call, Class) and not isinstance(value_to_call, BuiltInFunction) and not isinstance(value_to_call, BuiltInClass):
            raise Al_NameError({
                'pos_start': node.pos_start,
                'pos_end': node.pos_end,
                'message': f"'{node.node_to_call.name.value}' is not callable" if hasattr(node.node_to_call, 'name') and hasattr(node.node_to_call.name, 'value') else f"type '{TypeOf(value_to_call).getType()}' is not callable",
                'context': context,
                'exit': False
            })
        for arg_node in node.args_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res

        if len(args) > 0:
            for arg in args:
                if arg == None:
                    # remove None from args
                    args = [x for x in args if x != None]

        name = value_to_call.name
        builtins = {
            'print': BuiltInFunction_Print,
            'println': BuiltInFunction_PrintLn,
            'len': BuiltInFunction_Len,
            'int': BuiltInClass_Int,
            'input': BuiltInFunction_Input,
            'inputInt': BuiltInFunction_InputInt,
            'inputFloat': BuiltInFunction_InputFloat,
            'format': BuiltInFunction_Format,
            'range': BuiltInFunction_Range,
            'zip': BuiltInFunction_Zip,
            'max': BuiltInFunction_Max,
            'min': BuiltInFunction_Min,
            'append': BuiltInFunction_Append,
            'pop': BuiltInFunction_Pop,
            'extend': BuiltInFunction_Extend,
            'remove': BuiltInFunction_Remove,
            'is_finite': BuiltInFunction_is_finite,
            'sorted': BuiltInFunction_Sorted,
            'substr': BuiltInFunction_Substr,
            'reverse': BuiltInFunction_Reverse,
            # 'Binary': BuiltInFunction_Binary,
            'line': BuiltInFunction_Line,
            'clear': BuiltInFunction_Clear,
            'typeof': BuiltInFunction_Typeof,
            'isinstanceof': BuiltInFunction_IsinstanceOf,
            'hasprop': BuiltInFunction_hasprop,
            'delay': BuiltInFunction_Delay,
            'require': BuiltInFunction_Require,
            'enumerate': BuiltInFunction_Enumerate,
            'freeze': BuiltInFunction_Freeze,
            'std_in_read': BuiltInFunction_StdInRead,
            'std_in_readline': BuiltInFunction_StdInReadLine,
            'std_in_readlines': BuiltInFunction_StdInReadLines,
            'std_out_write': BuiltInFunction_StdOutWrite,
            'std_out_writelines': BuiltInFunction_StdOutWriteLines,
            'sys_path': BuiltInFunction_SysPath,
            'sys_argv': BuiltInFunction_SysArgv,
            'sys_exit': BuiltInFunction_SysExit,
            'sys_version': BuiltInFunction_SysVersion,
            'sys_platform': BuiltInFunction_SysPlatform,
            'exit': BuiltInFunction_Exit
        }

        # if builtin in builtin_variables:
        #     raise Al_RuntimeError({
        #         'pos_start': node.pos_start,
        #         'pos_end': node.pos_end,
        #         'message': f"'{builtin}' is not callable",
        #         'context': context,
        #         'exit': False
        #     })


        if name in builtins:
            return builtins[name](args, node, context, keyword_args_list)


        return_value = res.register(value_to_call.execute(args, keyword_args_list))

        if res.should_return():
            return res
        return_value = return_value.copy().setPosition(
            node.pos_start, node.pos_end).setContext(context) if hasattr(return_value, 'copy') else return_value
        # if isinstance(return_value, NoneType):
        #     return res.noreturn()
        return res.success(return_value)


    def visit_DelNode(self, node, context):
        res = RuntimeResult()
        identifier = context.symbolTable.get(node.identifier.value)
        if type(identifier).__name__ == 'dict':
            identifier = identifier['value']
        expression = node.expression
        if type(expression).__name__ == 'ListNode':
            expression = res.register(self.visit(expression, context))
        if type(identifier).__name__ == 'Dict' or type(identifier).__name__ == 'Object' or type(identifier).__name__ == 'Class':
            new_properties = {}
            for key, value in identifier.properties.items():
                if expression != None and expression != '':
                    if type(expression).__name__ == 'List':
                        if len(expression.elements) == 0:
                            raise Al_IndexError(
                            {
                                "pos_start": node.pos_start,
                                "pos_end": node.pos_end,
                                "message": "Property name cannot be empty",
                                "context": context,
                                "exit": False
                            })
                        elif len(expression.elements) > 1:
                            raise Al_IndexError(
                            {
                                "pos_start": node.pos_start,
                                "pos_end": node.pos_end,
                                "message": "invalid index expression",
                                "context": context,
                                "exit": False
                            })
                        else:
                            if not isinstance(expression.elements[0], String):
                                raise Al_TypeError(
                                {
                                    "pos_start": node.pos_start,
                                    "pos_end": node.pos_end,
                                    "message": f"type '{TypeOf(expression.elements[0]).getType()}' must be of type 'string'",
                                    "context": context,
                                    "exit": False
                                })
                            name = expression.elements[0].value
                            if not name in identifier.properties:
                                raise Al_PropertyError(
                                    {
                                        "pos_start": node.pos_start,
                                        "pos_end": node.pos_end,
                                        "message": f"{node.identifier.value} object has no property '{name}'" if hasattr(node.identifier, 'value') else f"'{name}'",
                                        "context": context,
                                        "exit": False
                                    })
                            identifier.properties = {key: value for key, value in identifier.properties.items() if key != name}
                            new_properties = {**new_properties, **identifier.properties}
                            context.symbolTable.set(node.identifier.value, Dict(new_properties))
                            return res.success(None)
                    else:
                        if type(expression).__name__ == 'PropertyNode':
                            name = expression.property.value
                            if not name in identifier.properties:
                                raise Al_PropertyError(
                                    {
                                        "pos_start": node.pos_start,
                                        "pos_end": node.pos_end,
                                        "message": f"{node.identifier.value} object has no property '{name}'" if hasattr(node.identifier, 'value') else f"'{name}'",
                                        "context": context,
                                        "exit": False
                                    })
                            identifier.properties = {key: value for key, value in identifier.properties.items() if key != name}
                            new_properties = {**new_properties, **identifier.properties}
                            context.symbolTable.set(node.identifier.value, Dict(new_properties))
                            return res.success(None)
                else:
                    identifier.properties = {}
                    context.symbolTable.set(node.identifier.value, identifier)
                    return res.success(None)
        else:
             raise Al_TypeError(
                {
                    "pos_start": node.pos_start,
                    "pos_end": node.pos_end,
                    "message": f"del on type '{TypeOf(identifier).getType()}' is not supported",
                    "context": context,
                    "exit": False
                })


    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()
        return_value = None
        if node.node_to_return:
            try:
                value = res.register(self.visit(node.node_to_return, context))
                if value is None: value = NoneType.none
                if res.should_return(): return res
                return_value = value
            except RecursionError:
                raise Al_RecursionError(
                    {
                        "pos_start": node.pos_start,
                        "pos_end": node.pos_end,
                        "message": "'RecursionError': maximum recursion depth exceeded",
                        "context": context,
                        "exit": False
                    })
        else:
            return_value = NoneType.none
        if return_value is None:  return_value = NoneType.none
        if isinstance(return_value, NoneType):
            return res.noreturn()

        return res.success_return(return_value)


    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()


    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()


    def visit_FreezeNode(self, node, context):
        res = RuntimeResult()
        name = node.object.id.value if hasattr(node.object, 'id') else node.object.value
        object = res.register(self.visit(node.object, context))
        context.symbolTable.set(name, {
            'value': object,
            'type': 'freeze'
        })


print_doc = DocString(""" 
Prints the given value to stdout.
Opitional arguments: 
@file: the file to print to. Defaults to stdout.
@sep: the separator to use. Defaults to ' '
@end: the end of line character to use. Defaults to '\\n'
""")
println_doc = DocString("""
Prints the given value to stdout.
Opitional arguments:
@file: the file to print to. Defaults to stdout.
@sep: the separator to use. Defaults to ' '
@end: the end of line character to use. Defaults to '\\n'
""")


BuiltInFunction.print = BuiltInFunction("print", print_doc)
BuiltInFunction.println = BuiltInFunction("println", println_doc)
BuiltInFunction.exit = BuiltInFunction("exit", None)
BuiltInFunction.input = BuiltInFunction("input", None)
BuiltInFunction.inputInt = BuiltInFunction("inputInt", None)
BuiltInFunction.inputFloat = BuiltInFunction("inputFloat", None)
BuiltInFunction.inputBool = BuiltInFunction("inputBool", None)
BuiltInFunction.clear = BuiltInFunction("clear", None)
BuiltInFunction.len = BuiltInFunction("len", None)
BuiltInFunction.range = BuiltInFunction("range", None)
BuiltInFunction.zip = BuiltInFunction("zip", None)
BuiltInFunction.line = BuiltInFunction("line", None)
BuiltInFunction.append = BuiltInFunction("append", None)
BuiltInFunction.pop = BuiltInFunction("pop", None)
BuiltInFunction.extend = BuiltInFunction("extend", None)
BuiltInFunction.remove = BuiltInFunction("remove", None)
BuiltInFunction.sorted = BuiltInFunction("sorted", None)
BuiltInFunction.clearList = BuiltInFunction("clearList", None)
BuiltInFunction.delay = BuiltInFunction("delay", None)
BuiltInFunction.open = BuiltInFunction("open", None)
BuiltInFunction.split = BuiltInFunction("split", None)
BuiltInFunction.substr = BuiltInFunction("substr", None)
BuiltInFunction.reverse = BuiltInFunction("reverse", None)
BuiltInFunction.format = BuiltInFunction("format", None)
BuiltInFunction.typeof = BuiltInFunction("typeof", None)
BuiltInFunction.isinstanceof = BuiltInFunction("isinstanceof", None)
BuiltInFunction.hasprop = BuiltInFunction("hasprop", None)
BuiltInFunction.max = BuiltInFunction("max", None)
BuiltInFunction.min = BuiltInFunction("min", None)
BuiltInFunction.is_finite = BuiltInFunction("is_finite", None)
BuiltInFunction.enumerate = BuiltInFunction("enumerate", None)
BuiltInFunction.freeze = BuiltInFunction("freeze", None)
BuiltInFunction.require = BuiltInFunction("require", None)
BuiltInFunction.std_in_read = BuiltInFunction("std_in_read", None)
BuiltInFunction.std_in_readline = BuiltInFunction("std_in_readline", None)
BuiltInFunction.std_in_readlines = BuiltInFunction("std_in_readlines", None)
BuiltInFunction.std_out_write = BuiltInFunction("std_out_write", None)
BuiltInFunction.std_out_writelines = BuiltInFunction("std_out_writelines", None)
BuiltInFunction.sys_path = BuiltInFunction("sys_path", None)
BuiltInFunction.sys_argv = BuiltInFunction("sys_argv", None)
BuiltInFunction.sys_exit = BuiltInFunction("sys_exit", None)
BuiltInFunction.sys_version = BuiltInFunction("sys_version", None)
BuiltInFunction.sys_platform = BuiltInFunction("sys_platform", None)
BuiltInClass.File = BuiltInClass("File", {})
BuiltInClass.str = BuiltInClass("str", {})
BuiltInClass.int = BuiltInClass("int", {})
BuiltInClass.float = BuiltInClass("float", {})
BuiltInClass.complex = BuiltInClass("complex", {})
BuiltInClass.chr = BuiltInClass("chr", {})
BuiltInClass.ord = BuiltInClass("ord", {})
BuiltInClass.bool = BuiltInClass("bool", {})
BuiltInClass.list = BuiltInClass("list", {})
BuiltInClass.pair = BuiltInClass("pair", {})
BuiltInClass.dict = BuiltInClass("dict", {})
#code for the built-in class exceptions
#'class Exception(message)\nend\nclass RuntimeError()~Exception\nend'
code_builtin_exception = 'class Exception()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_runtime = 'class RuntimeError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_nameerror = 'class NameError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_argumenterror = 'class ArgumentError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_typeerror = 'class TypeError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_indexerror = 'class IndexError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_valueerror = 'class ValueError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_propertyerror = 'class PropertyError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_keyerror = 'class KeyError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_zerodivisionerror = 'class ZeroDivisionError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_ImportError = 'class ImportError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_modulenotfounderror = 'class ModuleNotFoundError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_keyboardinterrupt = 'class KeyboardInterrupt()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_recursionerror = 'class RecursionError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_ioerror = 'class IOError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_oserror = 'class OSError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_filenotfounderror = 'class FileNotFoundError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_permissionerror = 'class PermissionError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'
code_builtin_notimplementederror = 'class NotImplementedError()\ndef __@init__(self,message)\n\tself.message = message\nend\nend'



# builtin_exception = Program.createBuiltIn("Exception", code_builtin_exception).elements[0]
# builtin_exception_runtime = Program.createBuiltIn("RuntimeError", code_builtin_runtime).elements[0]
# builtin_exception_nameerror = Program.createBuiltIn("NameError", code_builtin_nameerror).elements[0]
# builtin_exception_argumenterror = Program.createBuiltIn("ArgumentError", code_builtin_argumenterror).elements[0]
# builtin_exception_typeerror = Program.createBuiltIn("TypeError", code_builtin_typeerror).elements[0]
# builtin_exception_indexerror = Program.createBuiltIn("IndexError", code_builtin_indexerror).elements[0]
# builtin_exception_valueerror = Program.createBuiltIn("ValueError", code_builtin_valueerror).elements[0]
# builtin_exception_propertyerror = Program.createBuiltIn("PropertyError", code_builtin_propertyerror).elements[0]
# builtin_exception_keyerror = Program.createBuiltIn("KeyError", code_builtin_keyerror).elements[0]
# builtin_exception_zerodivisionerror = Program.createBuiltIn("ZeroDivisionError", code_builtin_zerodivisionerror).elements[0]
# builtin_exception_ImportError = Program.createBuiltIn("ImportError", code_builtin_ImportError).elements[0]
# builtin_exception_modulenotfounderror = Program.createBuiltIn("ModuleNotFoundError", code_builtin_modulenotfounderror).elements[0]
# builtin_exception_keyboardinterrupt = Program.createBuiltIn("KeyboardInterrupt", code_builtin_keyboardinterrupt).elements[0]
# builtin_exception_recursionerror = Program.createBuiltIn("RecursionError", code_builtin_recursionerror).elements[0]
# builtin_exception_ioerror = Program.createBuiltIn("IOError", code_builtin_ioerror).elements[0]
# builtin_exception_oserror = Program.createBuiltIn("OSError", code_builtin_ioerror).elements[0]
# builtin_exception_filenotfounderror = Program.createBuiltIn("FileNotFoundError", code_builtin_filenotfounderror).elements[0]
# builtin_exception_permissionerror = Program.createBuiltIn("PermissionError", code_builtin_permissionerror).elements[0]
# builtin_exception_notimplementederror = Program.createBuiltIn("NotImplementedError", code_builtin_notimplementederror).elements[0]

# exceptions_ = {
#     'Exception': builtin_exception,
#     'RuntimeError': builtin_exception_runtime,
#     'NameError': builtin_exception_nameerror,
#     'ArgumentError': builtin_exception_argumenterror,
#     'TypeError': builtin_exception_typeerror,
#     'IndexError': builtin_exception_indexerror,
#     'ValueError': builtin_exception_valueerror,
#     'PropertyError': builtin_exception_propertyerror,
#     'KeyError': builtin_exception_keyerror,
#     'ZeroDivisionError': builtin_exception_zerodivisionerror,
#     'ImportError': builtin_exception_ImportError,
#     'ModuleNotFoundError': builtin_exception_modulenotfounderror,
#     'KeyboardInterrupt': builtin_exception_keyboardinterrupt,
#     'RecursionError': builtin_exception_recursionerror,
#     'IOError': builtin_exception_ioerror,
#     'OSError': builtin_exception_oserror,
#     'FileNotFoundError': builtin_exception_filenotfounderror,
#     'PermissionError': builtin_exception_permissionerror,
#     'NotImplementedError': builtin_exception_notimplementederror
# }
# class_name, class_args, inherit_class_name, inherited_from, methods, class_fields_modifiers, context
# BuiltInClass.Exception = BuiltInClass(builtin_exception.class_name, builtin_exception.class_args, builtin_exception.inherit_class_name, builtin_exception.inherited_from, builtin_exception.methods, builtin_exception.class_fields_modifiers, builtin_exception.context)
# BuiltInClass.RuntimeError = BuiltInClass(builtin_exception_runtime.class_name, builtin_exception_runtime.class_args, builtin_exception_runtime.inherit_class_name, builtin_exception_runtime.inherited_from, builtin_exception_runtime.methods, builtin_exception_runtime.class_fields_modifiers, builtin_exception_runtime.context)
# BuiltInClass.NameError = BuiltInClass(builtin_exception_nameerror.class_name, builtin_exception_nameerror.class_args, builtin_exception_nameerror.inherit_class_name, builtin_exception_nameerror.inherited_from, builtin_exception_nameerror.methods, builtin_exception_nameerror.class_fields_modifiers, builtin_exception_nameerror.context)
# BuiltInClass.ArgumentError = BuiltInClass(builtin_exception_argumenterror.class_name, builtin_exception_argumenterror.class_args, builtin_exception_argumenterror.inherit_class_name, builtin_exception_argumenterror.inherited_from, builtin_exception_argumenterror.methods, builtin_exception_argumenterror.class_fields_modifiers, builtin_exception_argumenterror.context)
# BuiltInClass.TypeError = BuiltInClass(builtin_exception_typeerror.class_name, builtin_exception_typeerror.class_args, builtin_exception_typeerror.inherit_class_name, builtin_exception_typeerror.inherited_from, builtin_exception_typeerror.methods, builtin_exception_typeerror.class_fields_modifiers, builtin_exception_typeerror.context)
# BuiltInClass.IndexError = BuiltInClass(builtin_exception_indexerror.class_name, builtin_exception_indexerror.class_args, builtin_exception_indexerror.inherit_class_name, builtin_exception_indexerror.inherited_from, builtin_exception_indexerror.methods, builtin_exception_indexerror.class_fields_modifiers, builtin_exception_indexerror.context)
# BuiltInClass.ValueError = BuiltInClass(builtin_exception_valueerror.class_name, builtin_exception_valueerror.class_args, builtin_exception_valueerror.inherit_class_name, builtin_exception_valueerror.inherited_from, builtin_exception_valueerror.methods, builtin_exception_valueerror.class_fields_modifiers, builtin_exception_valueerror.context)
# BuiltInClass.PropertyError = BuiltInClass(builtin_exception_propertyerror.class_name, builtin_exception_propertyerror.class_args, builtin_exception_propertyerror.inherit_class_name, builtin_exception_propertyerror.inherited_from,  builtin_exception_propertyerror.methods, builtin_exception_propertyerror.class_fields_modifiers, builtin_exception_propertyerror.context)
# BuiltInClass.KeyError = BuiltInClass(builtin_exception_keyerror.class_name, builtin_exception_keyerror.class_args, builtin_exception_keyerror.inherit_class_name, builtin_exception_keyerror.inherited_from, builtin_exception_keyerror.methods, builtin_exception_keyerror.class_fields_modifiers, builtin_exception_keyerror.context)
# BuiltInClass.ZeroDivisionError = BuiltInClass(builtin_exception_zerodivisionerror.class_name, builtin_exception_zerodivisionerror.class_args, builtin_exception_zerodivisionerror.inherit_class_name, builtin_exception_zerodivisionerror.inherited_from,  builtin_exception_zerodivisionerror.methods, builtin_exception_zerodivisionerror.class_fields_modifiers, builtin_exception_zerodivisionerror.context)
# BuiltInClass.ImportError = BuiltInClass(builtin_exception_ImportError.class_name, builtin_exception_ImportError.class_args, builtin_exception_ImportError.inherit_class_name, builtin_exception_ImportError.inherited_from, builtin_exception_ImportError.methods, builtin_exception_ImportError.class_fields_modifiers, builtin_exception_ImportError.context)
# BuiltInClass.ModuleNotFoundError = BuiltInClass(builtin_exception_modulenotfounderror.class_name, builtin_exception_modulenotfounderror.class_args, builtin_exception_modulenotfounderror.inherit_class_name, builtin_exception_modulenotfounderror.inherited_from, builtin_exception_modulenotfounderror.methods, builtin_exception_modulenotfounderror.class_fields_modifiers, builtin_exception_modulenotfounderror.context)
# BuiltInClass.KeyboardInterrupt = BuiltInClass(builtin_exception_keyboardinterrupt.class_name, builtin_exception_keyboardinterrupt.class_args, builtin_exception_keyboardinterrupt.inherit_class_name, builtin_exception_keyboardinterrupt.inherited_from, builtin_exception_keyboardinterrupt.methods, builtin_exception_keyboardinterrupt.class_fields_modifiers, builtin_exception_keyboardinterrupt.context)
# BuiltInClass.RecursionError = BuiltInClass(builtin_exception_recursionerror.class_name, builtin_exception_recursionerror.class_args, builtin_exception_recursionerror.inherit_class_name, builtin_exception_recursionerror.inherited_from, builtin_exception_recursionerror.methods, builtin_exception_recursionerror.class_fields_modifiers, builtin_exception_recursionerror.context)
# BuiltInClass.IOError = BuiltInClass(builtin_exception_ioerror.class_name, builtin_exception_ioerror.class_args, builtin_exception_ioerror.inherit_class_name, builtin_exception_ioerror.inherited_from, builtin_exception_ioerror.methods, builtin_exception_ioerror.class_fields_modifiers, builtin_exception_ioerror.context)
# BuiltInClass.OSError = BuiltInClass(builtin_exception_oserror.class_name, builtin_exception_oserror.class_args, builtin_exception_oserror.inherit_class_name, builtin_exception_oserror.inherited_from, builtin_exception_oserror.methods, builtin_exception_oserror.class_fields_modifiers, builtin_exception_oserror.context)
# BuiltInClass.FileNotFoundError = BuiltInClass(builtin_exception_filenotfounderror.class_name, builtin_exception_filenotfounderror.class_args, builtin_exception_filenotfounderror.inherit_class_name, builtin_exception_filenotfounderror.inherited_from, builtin_exception_filenotfounderror.methods, builtin_exception_filenotfounderror.class_fields_modifiers, builtin_exception_filenotfounderror.context)
# BuiltInClass.PermissionError = BuiltInClass(builtin_exception_permissionerror.class_name, builtin_exception_permissionerror.class_args, builtin_exception_permissionerror.inherit_class_name, builtin_exception_permissionerror.inherited_from, builtin_exception_permissionerror.methods, builtin_exception_permissionerror.class_fields_modifiers, builtin_exception_permissionerror.context)
# BuiltInClass.NotImplementedError = BuiltInClass(builtin_exception_notimplementederror.class_name, builtin_exception_notimplementederror.class_args, builtin_exception_notimplementederror.inherit_class_name, builtin_exception_notimplementederror.inherited_from, builtin_exception_notimplementederror.methods, builtin_exception_notimplementederror.class_fields_modifiers, builtin_exception_notimplementederror.context)



Types.int = Types("int")
Types.float = Types("float")
Types.complex = Types("complex")
Types.chr = Types("chr")
Types.str = Types("str")
Types.bool = Types("bool")
Types.list = Types("list")
Types.pair = Types("pair")
Types.dict = Types("dict")
Types.module = Types("module")


symbolTable_.set('print', BuiltInFunction.print)
symbolTable_.set('println', BuiltInFunction.println)
symbolTable_.set('exit', BuiltInFunction.exit)
symbolTable_.set('input', BuiltInFunction.input)
symbolTable_.set('inputInt', BuiltInFunction.inputInt)
symbolTable_.set('inputFloat', BuiltInFunction.inputFloat)
symbolTable_.set('inputBool', BuiltInFunction.inputBool)
symbolTable_.set('clear', BuiltInFunction.clear)
symbolTable_.set('len', BuiltInFunction.len)
symbolTable_.set('range', BuiltInFunction.range)
symbolTable_.set('str', BuiltInClass.str)
symbolTable_.set('int', BuiltInClass.int)
symbolTable_.set('float', BuiltInClass.float)
symbolTable_.set('complex', BuiltInClass.complex)
symbolTable_.set('chr', BuiltInClass.chr)
symbolTable_.set('ord', BuiltInClass.ord)
symbolTable_.set('bool', BuiltInClass.bool)
symbolTable_.set('list', BuiltInClass.list)
symbolTable_.set('pair', BuiltInClass.pair)
symbolTable_.set('dict', BuiltInClass.dict)
symbolTable_.set('zip', BuiltInFunction.zip)
symbolTable_.set('line', BuiltInFunction.line)
symbolTable_.set('append', BuiltInFunction.append)
symbolTable_.set('pop', BuiltInFunction.pop)
symbolTable_.set('extend', BuiltInFunction.extend)
symbolTable_.set('remove', BuiltInFunction.remove)
symbolTable_.set('sorted', BuiltInFunction.sorted)
symbolTable_.set('clearList', BuiltInFunction.clearList)
symbolTable_.set('delay', BuiltInFunction.delay)
symbolTable_.set('open', BuiltInFunction.open)
symbolTable_.set('split', BuiltInFunction.split)
symbolTable_.set('substr', BuiltInFunction.substr)
symbolTable_.set('reverse', BuiltInFunction.reverse)
symbolTable_.set('format', BuiltInFunction.format)
symbolTable_.set('typeof', BuiltInFunction.typeof)
symbolTable_.set('isinstanceof', BuiltInFunction.isinstanceof)
symbolTable_.set('hasprop', BuiltInFunction.hasprop)
symbolTable_.set('max', BuiltInFunction.max)
symbolTable_.set('min', BuiltInFunction.min)
symbolTable_.set('is_finite', BuiltInFunction.is_finite)
symbolTable_.set('enumerate', BuiltInFunction.enumerate)
symbolTable_.set('freeze', BuiltInFunction.freeze)
# symbolTable_.set('Exception', BuiltInClass.Exception)
# symbolTable_.set('RuntimeError', BuiltInClass.RuntimeError)
# symbolTable_.set('NameError', BuiltInClass.NameError)
# symbolTable_.set('ArgumentError', BuiltInClass.ArgumentError)
# symbolTable_.set('TypeError', BuiltInClass.TypeError)
# symbolTable_.set('IndexError', BuiltInClass.IndexError)
# symbolTable_.set('LookupError', BuiltInClass.LookupError)
# symbolTable_.set('UnicodeDecodeError', BuiltInClass.UnicodeDecodeError)
# symbolTable_.set('ValueError', BuiltInClass.ValueError)
# symbolTable_.set('PropertyError', BuiltInClass.PropertyError)
# symbolTable_.set('KeyError', BuiltInClass.KeyError)
# symbolTable_.set('ZeroDivisionError', BuiltInClass.ZeroDivisionError)
# symbolTable_.set('ImportError', BuiltInClass.ImportError)
# symbolTable_.set('ModuleNotFoundError', BuiltInClass.ModuleNotFoundError)
# symbolTable_.set('KeyboardInterrupt', BuiltInClass.KeyboardInterrupt)
# symbolTable_.set('RecursionError', BuiltInClass.RecursionError)
# symbolTable_.set('IOError', BuiltInClass.IOError)
# symbolTable_.set('OSError', BuiltInClass.OSError)
# symbolTable_.set('FileNotFoundError', BuiltInClass.FileNotFoundError)
# symbolTable_.set('PermissionError', BuiltInClass.PermissionError)
# symbolTable_.set('NotImplementedError', BuiltInClass.NotImplementedError)

symbolTable_.set('__@file__', BuiltInClass.File)
symbolTable_.set('__@std_in_read__', BuiltInFunction.std_in_read)
symbolTable_.set('__@std_in_readline__', BuiltInFunction.std_in_readline)
symbolTable_.set('__@std_in_readlines__', BuiltInFunction.std_in_readlines)
symbolTable_.set('__@std_out_write__', BuiltInFunction.std_out_write)
symbolTable_.set('__@std_out_writelines__', BuiltInFunction.std_out_writelines)
symbolTable_.set('__@sys_path__', BuiltInFunction.sys_path)
symbolTable_.set('__@sys_argv__', BuiltInFunction.sys_argv)
symbolTable_.set('__@sys_exit__', BuiltInFunction.sys_exit)
symbolTable_.set('__@sys_version__', BuiltInFunction.sys_version)
symbolTable_.set('__@sys_platform__', BuiltInFunction.sys_platform)
symbolTable_.set('require', BuiltInFunction.require)
symbolTable_.setSymbol()


