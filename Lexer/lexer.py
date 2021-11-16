import sys
from Token import tokenList
from Token.token import Token
from Parser.stringsWithArrows import *
import re

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
class Program:
    def error():
        def IllegalCharacter(options):
            error = f'\nFile: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n\nSyntaxError: Illegal character unexpected  {options["originator"]}\n'
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
            Program.printError(error)
        methods = {
            'IllegalCharacter': IllegalCharacter,
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
        #sys.exit(1)
        
    def printErrorExit(*args):
        for arg in args:
            print(arg)
        sys.exit(1)

    def asString(detail):
        result = f'\nFile {detail["pos_start"].fileName}, line {detail["pos_start"].line + 1}'
        result += '\n\n' +  \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        result += f'\n{detail["name"]}: {detail["message"]}'
        return result


class Lexer:
    def __init__(self, fileName, fileText):
        self.fileName = fileName
        self.fileText = fileText
        self.pos = Position(-1, 0, -1, fileName, fileText)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.fileText[self.pos.index] if self.pos.index < len(self.fileText) else None

    def make_tokens(self, token=None):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char == '#':
                self.make_comment()
            elif self.current_char in '\n':
                tokens.append(Token(tokenList.TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in tokenList.DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in tokenList.LETTERS_SYMBOLS:
                tokens.append(self.make_identifier())
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == "'":
                tokens.append(self.make_single_string())
            elif self.current_char == '+':
                tokens.append(Token(tokenList.TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(tokenList.TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(tokenList.TT_DIVISION, pos_start=self.pos))
                self.advance()
            elif self.current_char == '%':
                tokens.append(Token(tokenList.TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(tokenList.TT_POWER, pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(tokenList.TT_COLON, pos_start=self.pos))
                self.advance()
            elif self.current_char == '.':
                tokens.append(Token(tokenList.TT_DOT, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(tokenList.TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(tokenList.TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(tokenList.TT_LSQBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(tokenList.TT_RSQBRACKET, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(tokenList.TT_LBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(tokenList.TT_RBRACE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ',':
                    tokens.append(Token(tokenList.TT_COMMA, pos_start=self.pos))
                    self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], Program.error()['IllegalCharacter'](
                    {
                        'originator': char,
                        'pos_start': pos_start
                    })
        tokens.append(Token(tokenList.TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        
        
        while self.current_char != None and self.current_char in tokenList.DIGITS + '.':
            
                
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            
            return Token(tokenList.TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(tokenList.TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        identifier_str = ''
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in tokenList.LETTERS_DIGITS_SYMBOLS:
            identifier_str += self.current_char
            self.advance()
            #check if dot is in the identifier and if it is, create a new token
        token_type = tokenList.TT_KEYWORD if identifier_str in tokenList.KEYWORDS else tokenList.TT_IDENTIFIER
        return Token(token_type, identifier_str, pos_start, self.pos)

    # def make_concat(self):
    #     pos_start = self.pos.copy()
    #     self.advance()
    #     return Token(tokenList.TT_COLON, pos_start=pos_start, pos_end=self.pos)
    # def make_method_call(self):
    #     method_name = ''
    #     pos_start = self.pos.copy()
    #     self.advance()
    #     #get the method name
    #     while self.current_char != None and self.current_char in tokenList.LETTERS_DIGITS + '_':
    #         method_name += self.current_char
    #         self.advance()
    #     token_type = tokenList.TT_KEYWORD if method_name in tokenList.KEYWORDS else tokenList.TT_IDENTIFIER
    #     return Token(token_type, method_name, pos_start, self.pos)
    
    
    def make_minus_or_arrow(self):
        tok_type = tokenList.TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '>':
            self.advance()
            tok_type = tokenList.TT_ARROW
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(tokenList.TT_NEQ, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, Program.error()['Syntax']({
            'pos_start': pos_start,
            'pos_end': self.pos,
            'message': 'Expected = after !',
            'exit': False
        })

    def make_equals(self):
        tok_type = tokenList.TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_EQEQ
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = tokenList.TT_LT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = tokenList.TT_GT
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = tokenList.TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self):
        string = ''
        string_concat = ''
        character = True
        pos_start = self.pos.copy()
        escape_character = False
        
        self.advance()
        escape_characters = {
            '\\': '\\',
            'n': '\n',
            't': '\t'
            # '{': '{',
            # '}': '}',
        }
        
        while self.current_char != None and (self.current_char != '"' or escape_character):
            # if self.current_char == '{':
            #     if self.current_char != None and self.current_char != '}':
            #         self.advance()
            #         string += '{'
            if self.current_char == '\\':
                self.advance()
                if self.current_char in escape_characters:
                    string += escape_characters[self.current_char]
                else:
                    character = False
                    Program.error()['Syntax']({
                        'pos_start': pos_start,
                        'pos_end': self.pos,
                        'message': 'Invalid escape character',
                        'exit': False
                    })
                    
            else:
                if character:
                    string += self.current_char
                    regex = Regex().compile('{(.*?)}')
                    interp_values = regex.match(string)
                    concat_string = ''
                else:
                    string = ''
                    return Token(tokenList.TT_STRING, string, pos_start, self.pos)
            self.advance()
            escape_character = False 
        if self.current_char == None:
            return None, Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.pos,
                'message': "Expected ' \" ' at (line: {}, column: {})".format(self.pos.line + 1, self.pos.column),
                'exit': False
            })
        self.advance()
        return Token(tokenList.TT_STRING, string, pos_start, self.pos)

    def make_interp(self, string, interp_values):
        pass
    def make_single_string(self):
        string = ''
        character = True
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()
        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != "'" or escape_character):
            if self.current_char == '\\':
                self.advance()
                if self.current_char in escape_characters:
                    string += escape_characters[self.current_char]
                else:
                    character = False
                    Program.error()['Syntax']({
                        'pos_start': pos_start,
                        'pos_end': self.pos,
                        'message': 'Invalid escape character',
                        'exit': False
                    })

            else:
                if character:
                    string += self.current_char
                else:
                    string = ''
                    return Token(tokenList.TT_SINGLE_STRING, string, pos_start, self.pos)
            self.advance()
            escape_character = False 
            
        if self.current_char == None:
            return None, Program.error()['Syntax']({
                'pos_start': pos_start,
                'pos_end': self.pos,
                'message': 'Expected " \' " at (line: {}, column: {})'.format(self.pos.line + 1, self.pos.column),
                'exit': False
            })
        self.advance()
        return Token(tokenList.TT_SINGLE_STRING, string, pos_start, self.pos)
    
    def make_comment(self):
        self.advance()
        while self.current_char != None and self.current_char != '\n':
            self.advance()



class Position:
    def __init__(self, index, line, column, fileName, fileText):
        self.index = index
        self.line = line
        self.column = column
        self.fileName = fileName
        self.fileText = fileText

    def __repr__(self):
        return str({
            'index': self.index,
            'line': self.line,
            'column': self.column,
            'fileName': self.fileName,
            'fileText': self.fileText
        })

    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.column, self.fileName, self.fileText)
