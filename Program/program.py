
import sys
from Lexer.lexer import Lexer
from Parser.parser import Parser
from Interpreter.interpreter import Context, Interpreter, BuiltInTask
from Global.globalSymbolTable import Global

BuiltInTask.print = BuiltInTask("print")
BuiltInTask.exit = BuiltInTask("exit")
GlobalSymbolTable = Global()
GlobalSymbolTable.set('print', BuiltInTask.print)
GlobalSymbolTable.set('exit', BuiltInTask.exit)
GlobalSymbolTable.setGlobal()

class Program:
    def error():
        def IllegalCharacter(options):
            error = f'\nFile: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n\nSyntaxError: Illegal character unexpected  {options["originator"]}\n'
            Program.printError(error)

        def Syntax(options):
            error = f'Syntax error {options["message"]}'
            Program.printError(error)

        def Runtime(options):
            error = f'Runtime error {options["originator"]} at line {options["line"]}'
            Program.printError(error)
        methods = {
            'IllegalCharacter': IllegalCharacter,
            'Syntax': Syntax,
            'Runtime': Runtime
        }
        return methods

    def print(args):
        for arg in args:
            print(arg)

    def printWithType(args):
        for arg in args:
            print(str(type(arg)) + " <===> " + str(arg))
    def printError(args):
        for arg in args:
            print(arg)
        sys.exit(1)

    def run(fileName, text):
        # Generate tokens
        lexer = Lexer(fileName, text)
        tokens, error = lexer.make_tokens()
        if error: return "", error

        # Generate AST
        parser = Parser(tokens)
        ast = parser.parse()
        if ast.error: return "", ast.error
        
        interpreter = Interpreter()
        context = Context('<program>')
        context.symbolTable = GlobalSymbolTable
        result = interpreter.visit(ast.node, context)
        return result.value, result.error

    def runFile(fileName):
        with open(fileName, 'r') as file:
            text = file.read()
            return Program.run(fileName, text)
