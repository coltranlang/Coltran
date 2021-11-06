from os import error
from Parser.stringsWithArrows import *
from Token.token import Token
from Token import tokenList
import sys
sys.path.append('./Parser/')


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
            error = f'Runtime error {options["originator"]} at line {options["line"]}'
            Program.printErrorExit(error)
        methods = {
            'Default': Default,
            'Syntax': Syntax,
            'Runtime': Runtime
        }
        return methods

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
        result = f'\nFile {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}, column {detail["pos_start"].column + 1}'
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
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class ListNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end


class VarAccessNode:
    def __init__(self, name):
        self.name = name
        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end


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


class VarAssignNode:
    def __init__(self, variable_name_token, value_node, variable_keyword_token):
        self.variable_keyword_token = variable_keyword_token
        self.variable_name_token = variable_name_token
        self.value_node = value_node
        self.pos_start = self.variable_name_token.pos_start
        self.pos_end = self.value_node.pos_end


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


class WhileNode:
    def __init__(self, condition_node, body_node, return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.return_null = return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class TaskDefNode:
    def __init__(self, task_name_token, args_name_tokens, body_node, implicit_return):
        self.task_name_token = task_name_token
        self.args_name_tokens = args_name_tokens
        self.body_node = body_node
        self.implicit_return = implicit_return
        # function methods
        methods = {
        }
        properties = {
            'name': self.task_name_token.value,
            'args': [arg.value for arg in args_name_tokens],
        }
        if self.task_name_token:
            self.pos_start = self.task_name_token.pos_start
        elif len(self.args_name_tokens) > 0:
            self.pos_start = self.args_name_tokens[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end
        self.methods = methods
        self.properties = properties


class CallNode:
    def __init__(self, node_to_call, args_nodes):
        self.node_to_call = node_to_call
        self.args_nodes = args_nodes

        self.pos_start = self.node_to_call.pos_start
        if len(self.args_nodes) > 0:
            self.pos_end = self.args_nodes[len(self.args_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


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
    def __init__(self, tokens):
        self.tokens = tokens
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
                if (value == "endTask"):
                    error['message'] = "Cannot end task here, without starting it, perhaps you forgot to add 'task' before 'endTask'?"
                return res.failure(Program.error()['Syntax'](error))
            return res
        except AttributeError:
            return ParseResult()

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
            return res.success(StatementsNode(statements, pos_start, self.current_token.pos_end.copy()))

        except AttributeError:
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
                'exit': True
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
                if self.current_token.matches(tokenList.TT_KEYWORD, 'endIf'):
                    res.register_advancement()
                    self.advance()

                else:
                    return res.failure(Program.error()['Syntax'](
                        {
                            'pos_start': self.current_token.pos_start,
                            'pos_end': self.current_token.pos_end,
                            'message': 'Expected "endIf"',
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
                    'exit': True
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
                    'exit': True
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

            if self.current_token.matches(tokenList.TT_KEYWORD, 'endIf'):
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
                'message': "Expected an identifier"
            }))

        var_name_token = self.current_token
        res.register_advancement()
        self.advance()
        if self.current_token.type != tokenList.TT_EQ:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '='"
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
                'message': "Expected 'to'"
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
                'exit': True
            }))
        res.register_advancement()
        self.advance()
        if self.current_token.type == tokenList.TT_NEWLINE:

            res.register_advancement()
            self.advance()
            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_token.matches(tokenList.TT_KEYWORD, 'endFor'):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'endFor'",
                    'exit': True
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
        #             'exit': True
        #         }
        #     ))

        return res.success(ForNode(var_name_token, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'while'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'while'",
                'exit': True
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
                'exit': True
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res
            if not self.current_token.matches(tokenList.TT_KEYWORD, 'endWhile'):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected 'endWhile'",
                    'exit': True
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
                'exit': True
            }))

        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_IDENTIFIER:
            var_name_tokens = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != tokenList.TT_LPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '('",
                    'exit': True
                }))
        else:
            var_name_tokens = None
            if self.current_token.type != tokenList.TT_LPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or '('",
                    'exit': True
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
                        'exit': True
                    }))
                arg_name_tokens.append(self.current_token)
                res.register_advancement()
                self.advance()
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ',' or ')'",
                    'exit': True
                }))
        else:
            if self.current_token.type != tokenList.TT_RPAREN:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier or ')'",
                    'exit': True
                }))
        res.register_advancement()
        self.advance()

        if self.current_token.type == tokenList.TT_ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(TaskDefNode(var_name_tokens, arg_name_tokens, body, True))

        if self.current_token.type != tokenList.TT_NEWLINE:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected  '->', or a newline",
                'exit': True
            }))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if not self.current_token.matches(tokenList.TT_KEYWORD, 'endTask'):
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected 'endTask'",
                'exit': True
            }))

        res.register_advancement()
        self.advance()

        return res.success(TaskDefNode(var_name_tokens, arg_name_tokens, body, False))

    def list_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_token.pos_start.copy()

        if self.current_token.type != tokenList.TT_LSQBRACKET:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Expected '['",
                'exit': True
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
                    'exit': True
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
                    'exit': True
                }))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(elements, pos_start, self.current_token.pos_end.copy()))

    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (tokenList.TT_INT, tokenList.TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        if tok.type == tokenList.TT_STRING or tok.type == tokenList.TT_SINGLE_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == tokenList.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.value == 'true' or tok.value == 'false' or tok.value == 'none':
            res.register_advancement()
            self.advance()
            return res.success(BooleanNode(tok))
        # elif tok.type == tokenList.TT_MOD:
        #     res.register_advancement()
        #     self.advance()
        #     return res.success(NumberNode(tok))
        elif tok.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            expression = res.register(self.expr())
            if res.error:
                return res
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expression)
            else:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected ')'",
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
        elif tok.matches(tokenList.TT_KEYWORD, 'while'):
            while_node = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_node)
        elif tok.matches(tokenList.TT_KEYWORD, 'task'):
            task_node = res.register(self.task_def())
            if res.error:
                return res
            return res.success(task_node)
        # return res.failure(Program.error()['Syntax']({
        #     'pos_start': tok.pos_start,
        #     'pos_end': tok.pos_end,
        #     'message': "Invalid syntax or unknown token",
        #     'exit': True
        # }))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_token.type == tokenList.TT_LPAREN:
            res.register_advancement()
            self.advance()
            args = []
            if self.current_token.type == tokenList.TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                args.append(res.register(self.expr()))
                if res.error:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Invalid syntax or unknown token",
                        'exit': False
                    }))
                while self.current_token.type == tokenList.TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    args.append(res.register(self.expr()))
                    if res.error:
                        return res
                if self.current_token.type != tokenList.TT_RPAREN:
                    return res.failure(Program.error()['Syntax']({
                        'pos_start': self.current_token.pos_start,
                        'pos_end': self.current_token.pos_end,
                        'message': "Expected a ',' or a closing parenthesis ')'",
                        'exit': False
                    }))
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, args))
        return res.success(atom)

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
            if tok and not factor: # if tok and factor is None then it is a syntax error because the factor is missing and the current token is the + or -
                Program.error()['Syntax']({
                    'message': 'Invalid syntax',
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'exit': False
                })
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.binaryOperation(self.factor, (tokenList.TT_MUL, tokenList.TT_DIVISION, tokenList.TT_MOD, tokenList.TT_COLON))

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
            self.arith_expr, (tokenList.TT_EQEQ, tokenList.TT_NEQ, tokenList.TT_LT, tokenList.TT_GT, tokenList.TT_LTE, tokenList.TT_GTE)))

        if res.error:
            return res.failure(Program.error()['Syntax']({
                'pos_start': self.current_token.pos_start,
                'pos_end': self.current_token.pos_end,
                'message': "Invalid syntax or unknown token",
                'exit': True
            }))

        return res.success(node)

    def expr(self):
        res = ParseResult()
        if self.current_token.matches(tokenList.TT_KEYWORD, 'let') or self.current_token.matches(tokenList.TT_KEYWORD, 'final'):
            res.register_advancement()
            variable_keyword_token = "let" if self.current_token.matches(
                tokenList.TT_KEYWORD, 'let') else "final"
            self.advance()
            if(self.current_token.value in tokenList.KEYWORDS):
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': f"Expected an identifier, '{self.current_token.value}' is a reserved keyword",
                    'exit': True
                }))
            if self.current_token.type != tokenList.TT_IDENTIFIER:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected an identifier",
                    'exit': True
                }))
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type == tokenList.TT_COMMA:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Assignments on multiple variables are not supported",
                    'exit': True
                }))
            if self.current_token.type != tokenList.TT_EQ:
                return res.failure(Program.error()['Syntax']({
                    'pos_start': self.current_token.pos_start,
                    'pos_end': self.current_token.pos_end,
                    'message': "Expected '='",
                    'exit': True
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
                'exit': True
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
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)
