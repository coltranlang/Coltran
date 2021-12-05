from os import access, path
from re import split

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
        def sub(self, pattern, text):
            return self.pattern.sub(pattern, text)

def lower(text):
    return text.islower()

def isOnlyLetters(text):
    return text.isalpha()

def isFirstLetterUpper(text):
    return text[0].isupper()               

class Program:
    def error():
        def Default(detail):
            error = detail['name'] + " : " + detail['message']
            if detail['exit']:
                Program.printErrorExit(error)
            else:
                Program.printError(error)

        def Syntax(detail):
            isDetail = {
                'name': 'SyntaxError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
            }
            if detail['exit']:
                Program.printErrorExit(Program.asString(isDetail))
            else:
                Program.printError(Program.asString(isDetail))

        def Runtime(options):
            error = f'Runtime error {options["originator"]}, line {options["line"]}'
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
        result = f'\nFile {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' +  \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        result += f'\n{detail["name"]}: {detail["message"]}'
        return result


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
    def __init__(self, tok, arg=None):
        self.tok = tok
        self.id = tok
        self.arg = arg
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

class ObjectRefNode:
    def __init__(self, tok):
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
       
class PipeNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end 
    

class VarAccessNode:
    def __init__(self, name, type=None):
        self.name = name
        self.id = name
        self.type = type
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class VarTypeNode:
    def __init__(self, name, value=None, type=None):
        self.name = name
        self.id = name
        self.type = type
        self.value = value
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'{self.name}'


class PropertyNode:
    def __init__(self, name, property):
        self.name = name
        self.id = name
        self.property = property
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end
        
    def __repr__(self):
        return f'{self.property}'
    

class PropertySetNode:
    def __init__(self, name, property, value):
        self.name = name
        self.id = name
        self.property = property
        self.value = value
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end
        
    def __repr__(self):
        return f'{self.name}'
        

class ExportModuleNode:
    def __init__(self, modules):
        self.modules = modules
        if isinstance(self.modules[0], dict):
            self.pos_start = self.modules[0]['pos_start']
            self.pos_end = self.modules[-1]['pos_end']
        else:
            self.pos_start = self.modules[0].pos_start
            self.pos_end = self.modules[-1].pos_end
        
    def __repr__(self):
        return f'{self.modules}'


class ModuleExport:
    def __init__(self, name, value):
        self.name = name
        self.id = name
        self.value = value
        self.pos_start = self.name.pos_start
        self.pos_end = self.value.pos_end
    

class ObjectGetNode:
    def __init__(self, left , right):
        self.id = left
        self.left = left
        self.right = right
        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end
        
    def __repr__(self):
        return f'{self.left}'


class ObjectCall:
    def __init__(self, left, op_tok, right, args):
        self.id = left
        self.left = left
        self.op_tok = op_tok
        self.right = right
        self.args = args
        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end

    def __repr__(self):
        return f'{self.left}'

class GetterNode:
    def __init__(self, left, right):
        self.id = left
        self.left = left
        self.right = right
        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end
        
    def __repr__(self):
        return f'{self.left}'



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
        else:
            self.pos_start = variable_name_token.pos_start
            self.pos_end = value_node.pos_end
        
        
class BooleanNode:
    def __init__(self, tok):
        self.tok = tok
        self.value = self.tok.value
        if tok.value == 'true':
            self.value = True
        elif tok.value == 'false':
            self.value = False
        elif tok.value == 'none':
            self.value = None
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'
    
    
class NoneNode:
    def __init__(self, tok):
        self.tok = tok
        self.id = tok
        self.value = self.tok.value
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'   


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        if self.left_node == '' or self.right_node == '' or self.op_tok == '':
            Program.error()['Syntax']({
                'message': 'Invalid syntax',
                'pos_start': self.op_tok.pos_start,
                'pos_end': self.op_tok.pos_end,
                'exit': False
            })
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


class TaskDefNode:
    def __init__(self, task_name_token, args_name_tokens, body_node, implicit_return, class_name=None, type=None):
        self.task_name_token = task_name_token
        self.id = task_name_token
        self.args_name_tokens = args_name_tokens
        self.body_node = body_node
        self.implicit_return = implicit_return
        self.class_name = class_name
        self.type = type
        if self.task_name_token:
            self.pos_start = self.task_name_token.pos_start
        elif len(self.args_name_tokens) > 0:
            self.pos_start = self.args_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end


class ObjectDefNode:
    def __init__(self, object_name, properties):
        self.object_name = object_name
        self.id = object_name
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
    def __init__(self,class_name, class_constuctor_args,inherits_class_name, inherits_class, methods):
        self.id = class_name
        self.class_name = class_name
        self.class_constuctor_args = class_constuctor_args
        self.inherits_class_name = inherits_class_name
        self.inherits_class = inherits_class
        self.methods = methods
        self.body_node = methods
        self.pos_start = self.class_name.pos_start
        for method in self.methods:
            self.pos_end = method['pos_end']
        self.class_object = {
            'name': self.class_name.value,
            'properties': self.methods
        }
        
    def __repr__(self):
        return f'{self.class_name}'



class CallNode:
    def __init__(self, node_to_call, args_nodes, owner=None, type=None):
        self.id = node_to_call
        self.node_to_call = node_to_call
        self.args_nodes = args_nodes
        self.type = type
        self.owner = owner
        self.pos_start = self.node_to_call.pos_start
        if len(self.args_nodes) > 0:
            self.pos_end = self.args_nodes[len(self.args_nodes) - 1].pos_end# if self.args_nodes[len(self.args_nodes) - 1] else 0
        else:
            self.pos_end = self.node_to_call.pos_end
    def __repr__(self):
        return f'{self.node_to_call}({self.args_nodes})'


class GetNode:
    def __init__(self, module_name, module_path):
        self.id = module_name
        self.module_name = module_name
        self.module_path = module_path
        self.pos_start = self.module_name.pos_start
        self.pos_end = self.module_name.pos_end
        
    def __repr__(self):
        return f'{self.module_name}'
    
    
class GetModuleNode:
    def __init__(self, module_name, module_path):
        self.id = module_name
        self.module_name = module_name
        self.module_path = module_path
        self.pos_start = self.module_name.pos_start
        self.pos_end = self.module_name.pos_end
        
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
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


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
    def __init__(self, tokens, file_name, position=None):
        self.tokens = tokens
        self.file_name = file_name
        self.position = position
        # get file name without extension
        #self.file_name_no_ext = self.file_name.split('/')[2].split('.')[0]
        self.tok_index = -1
        self.advance()

    def advance(self):
        self.tok_index += 1
        self.update_current_tok()
        return self.current_token
        # if hasattr(self, 'current_token'):
        #     return self.current_token
        # else:
        #     sys.exit(1)

    def reverse(self, count=1):
        self.tok_index -= count
        self.update_current_tok()
        return self.current_token
        # if hasattr(self, 'current_token'):
        #     return self.current_token
        # else:
        #     sys.exit(1)

    def update_current_tok(self):
        if self.tok_index >= 0 and self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]
        else:
            self.current_token = None

    def parse(self):
        res = self.statements()
        #errors_generated = [res.error]
        #print(len(errors_generated), 'errors generated')
        try:
            error = {
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'exit': False
            }
                
            if not res.error and self.current_token.type != tokenList.TT_EOF:
                value = self.current_token.value
                error['message'] = "Invalid syntax or unknown token"
                # if (value == "end"):
                #     error['message'] = "Cannot end task here, without starting it, perhaps you forgot to add 'task' before 'endTask'?"
                #     return res.failure(Program.error()['Syntax'](error))
            return res
        except AttributeError:
            return ParseResult()
        
    def property(self, tok):
        res = ParseResult()
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        prop_name = self.current_token
        res.register_advancement()
        self.advance()
        return res.success(PropertyNode(tok, prop_name))
    
    def skipLines(self):
        while self.current_token.type == tokenList.TT_NEWLINE:
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

        if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'continue'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))

        if self.current_token.matches(tokenList.TT_KEYWORD, 'break'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_end.copy()))
        expr = res.register(self.expr())
        if res.error:
            return res.failure(Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.current_token.pos_start,
                'message': "Expected 'return', 'continue', 'break', 'task', 'endTask', 'if', 'for', 'while', 'do', 'print', 'input', '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '=', ';', ':', ',' or '{'",
                'exit': False
            }))
        return res.success(expr)

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error:
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

            if self.current_token.type == tokenList.TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error:
                    return res
                else_case = (statements, True)
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()

                else:
                    return res.failure(Program.error()['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'Expected "end"',
                            'exit': False
                        }
                    ))
            else:
                expr = res.register(self.statement())
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
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_name):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(tokenList.TT_KEYWORD, case_name):
            return res.failure(Program.error()['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected "{}"'.format(case_name),
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
            return res.failure(Program.error()['Syntax'](
                {
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': 'Expected "then"',
                    'exit': False
                }
            ))
        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()
            
            statements = res.register(self.statements())
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
                return res
            cases.append((condition, expr, False))
            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'for'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'for'"
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))

        var_name_token = self.current_token
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_EQ:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '='",
                'exit': False
            }))
        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'to'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'to'",
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

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'then'",
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
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'end'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
            return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, True))
        body = res.register(self.statement())
        if res.error:
            return res
        # if self.current_token.matches(tokenList.TT_KEYWORD, 'return'):
        #     return res.failure(Program.error()['Syntax'](
        #         {
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': 'return is not allowed in for loop',
        #             'exit': False
        #         }
        #     ))

        return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, False))

    def in_expr(self):
        res = ParseResult()
    
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'in'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'in'"
            }))
            
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        
        iterable_name_token = self.current_token
        res.register_advancement()
        self.advance()
        
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'as'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'as'",
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
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    expr = res.register(self.expr())
                    iterator_keys.append(expr)
                    if res.error: return res
                    if len(iterator_keys) == 0:
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    elif len(iterator_keys) > 2:
                        return res.failure(Program.error()['ValueError']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Too many values, expected 2 or 1 but got {}".format(len(iterator_keys)),
                            'exit': False
                        }))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected 'then'",
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
                            return res.failure(Program.error()['Syntax']({
                                'pos_start': self.current_token.pos_start,
                                'pos_end': self.current_token.pos_end,
                                'message': "Expected 'end'",
                                'exit': False
                            }))

                        res.register_advancement()
                        self.advance()

                        return res.success(InNode(iterable_name_token, iterator_keys, body, False))
                    
                    else:
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected a newline",
                            'exit': False
                        }))
            
            
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'then'",
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
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()

                return res.success(InNode(iterable_name_token, iterator_keys, body, False))
            else:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
        else:
            expr = res.register(self.expr())
            if not isinstance(expr, PairNode):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a pair of values",
                    'exit': False
                }))
                
            for el in expr.elements:
                iterator_keys.append(el)
                
            if len(iterator_keys) == 0:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a value",
                    'exit': False
                }))
                
            elif len(iterator_keys) > 2:
                return res.failure(Program.error()['ValueError']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Too many values, expected 2 or 1 but got {}".format(len(iterator_keys)),
                    'exit': False
                }))
                
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'then'",
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
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                
                return res.success(InNode(iterable_name_token, iterator_keys, body, False))
                
                
                
        print(iterator_keys)
        body = res.register(self.statement())
        return res.success(InNode(iterable_name_token, iterator_keys, body, False)) 
    
    def while_expr(self):
        res = ParseResult()

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'while'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'while'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'then'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'then'",
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
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'end'",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def task_def(self):
        res = ParseResult()
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'task'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'task'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            task_name = self.current_token.value
            if task_name[0] != '@':
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Task name must start with '@'",
                    'exit': False
                }))
            var_name_tokens = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_LPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '('",
                    'exit': False
                }))
        else:
            var_name_tokens = None
            task_name = self.current_token.value
            if task_name in tokenList.KEYWORDS:
                return res.failure(Program.error()['NameError']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Cannot use reserved keyword as task name",
                    'exit': False
                }))
            if self.current_token.type != tokenList.TT_LPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or '('",
                    'exit': False
                }))
        res.register_advancement()
        self.advance()
        arg_name_tokens = []

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            arg_name_tokens.append(self.current_token)
            res.register_advancement()
            self.advance()
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected an identifier",
                        'exit': False
                    }))
                arg_name_tokens.append(self.current_token)
                if len(arg_name_tokens) > 12:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Cannot have more than 12 arguments",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',' or ')'",
                    'exit': False
                }))
        else:
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or ')'",
                    'exit': False
                }))
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_ARROW:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_NEWLINE:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an expression",
                    'exit': False
                }))
            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(TaskDefNode(var_name_tokens, arg_name_tokens, body, True))
        
        
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected  '->', or a newline",
                'exit': False
            }))
            
            
        res.register_advancement()
        self.advance()
        
        
        body = res.register(self.statements())
        if res.error: return res
        
        
        # while self.current_token.matches(tokenList.TT_KEYWORD, 'method'):
        #     method = res.register(self.method())
        #     if res.error: return res
        #     methods.append(method)
        #     body = methods
        #     res.register_advancement()
        #     self.advance()
            
            
        
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            return res.success(TaskDefNode(var_name_tokens, arg_name_tokens, body, False))
        else:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'end'",
                'exit': False
            }))     
  
    def object_def(self):
        res = ParseResult()
        object_properties = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'object'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'object'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))
        
        object_name = self.current_token
        
        if object_name in tokenList.KEYWORDS:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as object name",
                'exit': False
            }))
        if isOnlyLetters(object_name.value) == False:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use non-letter characters as object name",
                'exit': False
            }))
        if isFirstLetterUpper(object_name.value) == False:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Object name must start with a capital letter",
                'exit': False
            }))
        
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
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
                return res.success(ObjectDefNode(object_name, object_properties))
            if self.current_token.type != tokenList.TT_IDENTIFIER and str(self.current_token.value) not in tokenList.DIGITS:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            
            while self.current_token.type == tokenList.TT_IDENTIFIER or str(self.current_token.value) in tokenList.DIGITS:
                
                obj_name = self.current_token
                if res.error: return res
                # obj_name cannot start with a @ or a symbol
                if obj_name.value[0] == '@' or obj_name.value[0] in tokenList.SYMBOLS:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Object name cannot start with a symbol",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                
                if self.current_token.type != tokenList.TT_COLON:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ':'",
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
                
                
                
                #return res.success(ObjectDefNode(object_name, object_properties))
                
                if res.error: return res
                if obj_value == '':
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected property value",
                        'exit': False
                    }))
                if self.current_token.type == tokenList.TT_COMMA:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unexpected token, expected a newline",
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_NEWLINE:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a newline",
                        'exit': False
                    }))
                
                res.register_advancement()
                self.advance()
                
                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()
                    
                    return res.success(ObjectDefNode(object_name, object_properties))
                if self.current_token.value in tokenList.NOT_ALLOWED_OBJECTS_KEYS:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unterminated object literal, Object key '{}' is not allowed".format(self.current_token.value),
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
                            return res.success(ObjectDefNode(object_name, object_properties))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                        return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected 'end' or you have forgottem to close a newline",
                        'exit': False
                    }))
                    else:
                        res.register_advancement()
                        self.advance()
                        return res.success(ObjectDefNode(object_name, object_properties))
            return res.success(ObjectDefNode(object_name, object_properties))   
          
    def set_method(self, class_name):
        res = ParseResult()
        
        class_methods = []
        while self.current_token.matches(tokenList.TT_KEYWORD, "def"):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier, '{}' is a reserved keyword".format(self.current_token.value) if self.current_token.value in tokenList.KEYWORDS else "Expected an identifier",
                    'exit': False
                }))
            method_name = self.current_token
            res.register_advancement()
            self.advance()

            if self.current_token.type != tokenList.TT_LPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '('",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            args_list = []
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                args_list.append(self.current_token)
                res.register_advancement()
                self.advance()
                if len(args_list) > 0:
                    if args_list[0].value == 'self':
                        args_list[0] = class_name
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    if self.current_token.type != tokenList.TT_IDENTIFIER:
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected an identifier",
                            'exit': False
                        }))
                    args_list.append(self.current_token)
                    res.register_advancement()
                    self.advance()
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_ARROW:
                    return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "'->' not allowed in class methods",
                    'exit': False
                }))
            if self.current_token.type != tokenList.TT_NEWLINE:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected a newline",
                    'exit': False
                }))
            
            res.register_advancement()
            self.advance()
            
            body = res.register(self.statements())
            if res.error:
                return res
            if self.current_token.matches(tokenList.TT_KEYWORD, 'def'):
                res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'end'",
                    'exit': False
                }))
            if self.current_token.matches(tokenList.TT_KEYWORD, "end") and not self.current_token.matches(tokenList.TT_KEYWORD, "def"):
                res.register_advancement()
                self.advance()
                class_methods.append({
                    'name': method_name,
                    'value': TaskDefNode(method_name, args_list, body, False, class_name, "method"),
                    'pos_start': method_name.pos_start,
                    'pos_end': body.pos_end
                })
                if self.current_token.type != tokenList.TT_NEWLINE:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a newline",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                
        self.class_methods = class_methods
        return class_methods
      
    def class_def(self):
        res = ParseResult()
        inherit_class = None
        inherit_class_name = None
        class_name = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'class'):
            res.register_advancement()
            self.advance()
        else:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'class'",
                'exit': False
            }))
        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a class name",
                'exit': False
            }))
            
            
        class_name = self.current_token
        #class name has to be upper case
        # class name cannot start with @ keyword or symbol or number
        if  isFirstLetterUpper(class_name.value) == False:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name must start with a capital letter",
                'exit': False
            }))
        if isOnlyLetters(class_name.value) == False:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Class name can only contain letters",
                'exit': False
            }))
        if class_name in tokenList.KEYWORDS:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as class name",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        
        if self.current_token.type != tokenList.TT_LPAREN:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '('",
                'exit': False
            }))
        
        res.register_advancement()
        self.advance()
        class_constuctor_args = []
        if self.current_token.type == tokenList.TT_IDENTIFIER:
            # all constructor args must start with _ or $
            # if self.current_token.value[0] != '_' and self.current_token.value[0] != '$':
            #     return res.failure(Program.error()['Syntax']({
            #         'pos_start': self.current_token.pos_start,
            #         'pos_end': self.current_token.pos_end,
            #         'message': "Constructor argument must start with '_' or '$'",
            #         'exit': False
            #     }))
            class_constuctor_args.append(self.current_token)
            res.register_advancement()
            self.advance()
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type != tokenList.TT_IDENTIFIER:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected an identifier",
                        'exit': False
                    }))
                class_constuctor_args.append(self.current_token)
                res.register_advancement()
                self.advance()
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',' or ')'",
                    'exit': False
                }))
            else:
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ')'",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
        else:
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ')'",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))
        res.register_advancement()
        self.advance()
        class_methods = ''
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            res.success(ClassNode(class_name, inherit_class_name, inherit_class, class_methods))
        if self.current_token.matches(tokenList.TT_KEYWORD, "def"):
                self.set_method(class_name)
                if res.error:
                    return res
                class_methods = self.class_methods
        else:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'def'",
                'exit': False
            }))
        if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
            res.register_advancement()
            self.advance()
            #res.success(ClassNode(class_constuctor_args,class_name, inherit_class_name, inherit_class, class_methods))
            return res.success(ClassNode(class_name, class_constuctor_args, inherit_class_name, inherit_class, class_methods))
        else:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'end'",
                'exit': False
            }))
                             
    def list_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LSQBRACKET:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '['",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_RSQBRACKET:
            res.register_advancement()
            self.advance()
        else:
            element = res.register(self.expr())
            if res.error:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Epected an expression",
                    'exit': False
                }))
            elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()

                element = res.register(self.expr())
                if res.error:
                    return res
                elements.append(element)

            if self.current_token.type != tokenList.TT_RSQBRACKET:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',', or ']'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))

    def pair_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LPAREN:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '('",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        
        if self.current_token.type == tokenList.TT_RPAREN:
            res.register_advancement()
            self.advance()
        else:
            element = res.register(self.expr())
            if res.error:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Epected an expression",
                    'exit': False
                }))
            elements.append(element)
            while self.current_token.type == tokenList.TT_COMMA:
                res.register_advancement()
                self.advance()

                element = res.register(self.expr())
                if res.error:
                    return res
                elements.append(element)
                for el in elements:
                    if el == "":
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Epected an expression",
                            'exit': False
                        }))
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',', or ')'",
                    'exit': False
                }))

            res.register_advancement()
            self.advance()
        return res.success(PairNode(elements, pos_start, self.current_token.pos_end.copy()))

    def string_interp(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        inter_pv = None
        if self.current_token.matches(tokenList.TT_KEYWORD, 'fv'):
            res.register_advancement()
            self.advance()
            string_to_interp = self.current_token.value
            while self.current_token.type == tokenList.TT_BACKTICK_STRING:
                value = self.current_token.value
                regex = Regex().compile('%{(.*?)}')
                # we need to allow escaping of the %{}
                # check if the string has a double % and double { and double }
                regex2 = Regex().compile('%%{{(.*?)}}')
                if regex2.match(value):
                    value = regex2.sub('%{\\1}', value)
                if value.find('{{') != -1:
                    value = value.replace('{{', '{')
                    value = value.replace('}}', '}')
                interp_values = regex.match(value)
                if interp_values:
                    inter_pv = interp_values
                    expr = res.register(self.expr())
                    interpolated_string = self.make_expr(
                        inter_pv, self.current_token.pos_start)
                    return res.success(StringInterpNode(expr,  interpolated_string, string_to_interp, pos_start, self.current_token.pos_end.copy(),inter_pv))
                else:
                    expr = res.register(self.expr())
                    return res.success(StringInterpNode(expr, value, string_to_interp, pos_start, self.current_token.pos_end.copy()))
            else:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected a backtick string",
                    'exit': False
                }))
        return res.success(StringNode(self.current_token))
    
    def make_expr(self, inter_pv, position):
        interpolated = []
        for el in inter_pv:
            lexer = Lexer(self.file_name, el, position)
            token, error = lexer.make_tokens()
            parser = Parser(token, self.file_name, position)
            ast = parser.parse()
            for element in ast.node.elements:
                interpolated.append(element)
                self.string_expr = interpolated
        return self.string_expr
    
    def get_expr(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'get'):
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected an identifier",
                    'exit': False
                }))
                
            module_name = self.current_token
            res.register_advancement()
            self.advance()
            
            
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'from'):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected 'from'",
                    'exit': False
                }))
                
            res.register_advancement()
            self.advance()
            
            if self.current_token.type != tokenList.TT_STRING and self.current_token.type != tokenList.TT_SINGLE_STRING:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected a string",
                    'exit': False
                }))
                
            module_path = self.current_token

            res.register_advancement()
            self.advance()

            return res.success(GetNode(module_name, module_path))
    
    def module_expr(self):
        res = ParseResult()
        module_properties = []
        if not self.current_token.matches(tokenList.TT_KEYWORD, 'module'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'module'",
                'exit': False
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenList.TT_IDENTIFIER:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected an identifier",
                'exit': False
            }))

        module_name = self.current_token
        if module_name.value != 'Export':
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'Export'",
                'exit': False
            }))
        if module_name in tokenList.KEYWORDS:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use reserved keyword as object name",
                'exit': False
            }))
        if isOnlyLetters(module_name.value) == False:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Cannot use non-letter characters as object name",
                'exit': False
            }))
        if isFirstLetterUpper(module_name.value) == False:
            return res.failure(Program.error()['NameError']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Object name must start with a capital letter",
                'exit': False
            }))

        res.register_advancement()
        self.advance()
        # if self.current_token.type == tokenList.TT_EQ:
        #     res.register_advancement()
        #     self.advance()
        #     module_value = self.current_token
        #     if module_value.type != tokenList.TT_IDENTIFIER:
        #         return res.failure(Program.error()['Syntax']({
        #             'pos_start': self.current_token.pos_start,
        #             'pos_end': self.current_token.pos_end,
        #             'message': "Expected an identifier",
        #             'exit': False
        #         }))
        #     return res.success(ModuleExport(module_name, module_value))
        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected a newline",
                'exit': False
            }))

        while self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()

                module_properties.append({
                    'name': module_name,
                    'value': [],
                    'pos_start': module_name.pos_start,
                    'pos_end': module_name.pos_end
                })
                return res.success(ObjectDefNode(module_name, module_properties))
            if self.current_token.type != tokenList.TT_IDENTIFIER and str(self.current_token.value) not in tokenList.DIGITS:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))

            while self.current_token.type == tokenList.TT_IDENTIFIER or str(self.current_token.value) in tokenList.DIGITS:

                mod_name = self.current_token
                if res.error:
                    return res
                # obj_name cannot start with a @ or a symbol
                if mod_name.value[0] == '@' or mod_name.value[0] in tokenList.SYMBOLS:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Object name cannot start with a symbol",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()

                if self.current_token.type != tokenList.TT_COLON:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ':'",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()
                if self.current_token.type == tokenList.TT_IDENTIFIER:

                    if self.current_token.value == 'self':
                        self.current_token.value = module_name.value
                mod_value = res.register(self.expr())

                module_properties.append({
                    'name': mod_name,
                    'value': mod_value,
                    'pos_start': mod_name.pos_start,
                    'pos_end': self.current_token.pos_end
                })

                #return res.success(ObjectDefNode(module_name, module_properties))

                if res.error:
                    return res
                if mod_value == '':
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected property value",
                        'exit': False
                    }))
                if self.current_token.type == tokenList.TT_COMMA:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unexpected token, expected a newline",
                        'exit': False
                    }))
                if self.current_token.type != tokenList.TT_NEWLINE:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a newline",
                        'exit': False
                    }))

                res.register_advancement()
                self.advance()

                if self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()

                    return res.success(ObjectDefNode(module_name, module_properties))
                if self.current_token.value in tokenList.NOT_ALLOWED_OBJECTS_KEYS:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Unterminated object literal, Object key '{}' is not allowed".format(self.current_token.value),
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
                            return res.success(ObjectDefNode(module_name, module_properties))
                    if not self.current_token.matches(tokenList.TT_KEYWORD, 'end'):
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': "Expected 'end' or you have forgottem to close a newline",
                            'exit': False
                        }))
                    else:
                        res.register_advancement()
                        self.advance()
                        return res.success(ObjectDefNode(module_name, module_properties))
            return res.success(ObjectDefNode(module_name, module_properties))
    
    def export_expr(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'export'):
            res.register_advancement()
            self.advance()
            modules = []
            if self.current_token.type == tokenList.TT_IDENTIFIER:
                module = self.current_token
                res.register_advancement()
                self.advance()
                modules.append(module)
                if self.current_token.type == tokenList.TT_NEWLINE:
                    return res.success(ExportModuleNode(modules))
                elif self.current_token.type == tokenList.TT_EOF:
                    return res.success(ExportModuleNode(modules))
                else:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected a newline",
                        'exit': False
                    }))
                # if self.current_token.type == tokenList.TT_COMMA:
                #     while self.current_token.type == tokenList.TT_COMMA:
                #         res.register_advancement()
                #         self.advance()
                #         current_token = self.current_token
                #         if current_token.type != tokenList.TT_IDENTIFIER:
                #             return res.failure(Program.error()['Syntax']({
                #                 'pos_start': self.current_token.pos_start,
                #                 'pos_end': self.current_token.pos_end,
                #                 'message': f"Expected an identifier",
                #                 'exit': False
                #             }))
                #         res.register_advancement()
                #         self.advance()
                #         modules.append(current_token)
            # else:
            #     expr = res.register(self.expr())
            #     if isinstance(expr, ListNode):
            #         for element in expr.elements:
            #             if isinstance(element, VarAccessNode) != True:
            #                 return res.failure(Program.error()['Syntax']({
            #                     'pos_start': self.current_token.pos_start,
            #                     'pos_end': self.current_token.pos_end,
            #                     'message': f"Expected an identifier, or perhaps you forgot to close the list?",
            #                     'exit': False
            #                 }))
            #             modules.append(element)
            #     else:
            #         return res.failure(Program.error()['Syntax']({
            #             'pos_start': self.current_token.pos_start,
            #             'pos_end': self.current_token.pos_end,
            #             'message': f"Expected an identifier or list of identifiers",
            #             'exit': False
            #         }))
        return res.success(ExportModuleNode(modules))
     
    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_INT, tokenList.TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == tokenList.TT_STRING or tok.type == tokenList.TT_SINGLE_STRING or tok.type == tokenList.TT_BACKTICK_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == tokenList.TT_OBJECT_REF:
            res.register_advancement()
            self.advance()
            return res.success(ObjectRefNode(tok))    
        elif tok.type == tokenList.TT_IDENTIFIER:
            res.register_advancement()
            self.advance() 
            if self.current_token.type == tokenList.TT_EQ:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                return res.success(VarTypeNode(tok, expr))
            
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
             if res.error: return res
             return res.success(pair_expr)
        elif tok.type == tokenList.TT_RPAREN:
            return res.failure(Program.error()['Syntax']({
                'pos_start': tok.pos_start,
                'pos_end': tok.pos_end,
                'message': f"Invalid syntax or unexpected token",
                'exit': False
            }))
        elif tok.type == tokenList.TT_LSQBRACKET:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)
        elif tok.matches(tokenList.TT_KEYWORD, 'if'):
            if_expression = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expression)
        elif tok.matches(tokenList.TT_KEYWORD, 'for'):
            for_node = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_node)
        elif tok.matches(tokenList.TT_KEYWORD, 'in'):
            in_node = res.register(self.in_expr())
            if res.error:
                return res
            return res.success(in_node)
        elif tok.matches(tokenList.TT_KEYWORD, 'while'):
            while_node = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_node)
        elif tok.matches(tokenList.TT_KEYWORD, 'task'):
            task_def = res.register(self.task_def())
            if res.error:
                return res
            return res.success(task_def)
        elif tok.matches(tokenList.TT_KEYWORD, 'object'):
            object_node = res.register(self.object_def())
            if res.error:
                return res
            return res.success(object_node)
        elif tok.matches(tokenList.TT_KEYWORD, 'class'):
            class_node = res.register(self.class_def())
            if res.error:
                return res
            return res.success(class_node)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'fv'):
            string_interp = res.register(self.string_interp())
            if res.error:
                return res
            return res.success(string_interp)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'get'):
            get_node = res.register(self.get_expr())
            if res.error:
                return res
            return res.success(get_node)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'module'):
            get_module_node = res.register(self.module_expr())
            if res.error:
                return res
            return res.success(get_module_node)
        
        elif tok.matches(tokenList.TT_KEYWORD, 'export'):
            export_module = res.register(self.export_expr())
            if res.error:
                return res
            return res.success(export_module)   
    
    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:  return res
        
        while True:
            if self.current_token.type == tokenList.TT_LPAREN:
                atom = res.register(self.finish_call(atom))
            elif self.current_token.type == tokenList.TT_DOT:
                res.register_advancement()
                self.advance()
                name = self.current_token
                if name.type != tokenList.TT_IDENTIFIER:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': name.pos_start,
                        'pos_end': name.pos_end,
                        'message': "Expected an identifier, '{}' is a reserved keyword".format(name.value) if name.value in tokenList.KEYWORDS else "Expected an identifier",
                        'exit': False
                    }))
                atom = res.register(self.access_property(atom))
            else:
                if self.current_token.type == tokenList.TT_GETTER:
                    res.register_advancement()
                    self.advance()
                    if self.current_token.type == tokenList.TT_DOT:
                        return res.failure(Program.error()['Syntax']({
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': f"Expected a property name",
                            'exit': False
                        }))
                break
        
                
        return res.success(atom)
            
    def finish_call(self, atom):
        res = ParseResult()
        arg_nodes = []
        
        if self.current_token.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
                
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': f"Expected ')'",
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res
                      
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected ',' or ')'",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
        
        
        return res.success(CallNode(atom, arg_nodes))
          
    def access_property(self,owner):
        res = ParseResult()
        name = res.register(self.expr())
        return res.success(PropertyNode(owner, name))

    def power(self):
        return self.binaryOperation(self.call, (tokenList.TT_POWER, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_PLUS, tokenList.TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            if tok and not factor: # if tok and factor is None
                Program.error()['Syntax']({
                    'message': 'Invalid syntax',
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'exit': False
                })
            return res.success(UnaryOpNode(tok, factor))
        return self.power()

    def term(self):
        return self.binaryOperation(self.factor, (tokenList.TT_MUL, tokenList.TT_DIVISION, tokenList.TT_MOD, tokenList.TT_PIPE, tokenList.TT_GETTER))

    def arith_expr(self):
        return self.binaryOperation(self.term, (tokenList.TT_PLUS, tokenList.TT_MINUS))

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
            self.arith_expr, (tokenList.TT_EQEQ, tokenList.TT_NEQ, tokenList.TT_LT, tokenList.TT_GT, tokenList.TT_RSHIFT, tokenList.TT_LSHIFT, tokenList.TT_LTE, tokenList.TT_GTE, tokenList.TT_AND, )))

        if res.error:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'exit': False
            }))

        return res.success(node)

    def expr(self):
        res = ParseResult()
        # if self.current_token.type == tokenList.TT_IDENTIFIER:
        #     node_name = self.current_token
        #     res.register_advancement()
        #     self.advance()
            
        if self.current_token.matches(tokenList.TT_KEYWORD, 'let') or self.current_token.matches(tokenList.TT_KEYWORD, 'final'):
            res.register_advancement()
            variable_keyword_token = "let" if self.current_token.matches(
                tokenList.TT_KEYWORD, 'let') else "final"
            self.advance()
            
            if(self.current_token.value in tokenList.KEYWORDS):
                if self.current_token.value == "fv":
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Invalid syntax or unknown token, possibly you meant to use 'fv' instead of 'fv' as an identifier?",
                        'exit': False
                    }))
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Cannot use keyword '{self.current_token.value}' as an identifier",
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_LPAREN:
                expr = res.register(self.expr())
                if res.error: return res
                values = expr.elements
                var_values = ()
                
                if self.current_token.type != tokenList.TT_EQ:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected '='",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                for value in values:
                    var_values += (value,)
                return res.success(VarAssignNode(var_values, expr, variable_keyword_token))
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': False
                }))
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            if len(var_name.value) > 255:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Identifier too long",
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_COMMA:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Assignments on multiple variables are not supported",
                    'exit': False
                }))
            if self.current_token.type == tokenList.TT_RSHIFT:
                res.register_advancement()
                self.advance()
                
            if self.current_token.type != tokenList.TT_EQ:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '='",
                    'exit': False
                }))
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr, variable_keyword_token))
        node = res.register(self.binaryOperation(
            self.comp_expr, ((tokenList.TT_KEYWORD, 'and'), (tokenList.TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unexpected token",
                'exit': False
            }))
        return res.success(node)
      
    def binaryOperation(self, func_1, ops, func_2=None):
        if func_2 == None:
            func_2 = func_1

        res = ParseResult()
        left = res.register(func_1())
        if res.error:
            return res
        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(func_2())
            #print(type(right).__name__,type(left).__name__, )
            # if op_tok.type == tokenList.TT_DOT:
            #     return res.success(PropertyNode(left, right))
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

    
            


