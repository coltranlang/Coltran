import sys
from Lexer.lexer import Lexer
from Parser.parser import Parser
from Interpreter.interpreter import Context, Interpreter, BuiltInTask
from Global.globalSymbolTable import Global

BuiltInTask.print = BuiltInTask("print")
BuiltInTask.println = BuiltInTask("println")
BuiltInTask.exit = BuiltInTask("exit")
BuiltInTask.input = BuiltInTask("input")
BuiltInTask.inputInt = BuiltInTask("inputInt")
BuiltInTask.inputFloat = BuiltInTask("inputFloat")
BuiltInTask.clear = BuiltInTask("clear")
BuiltInTask.len = BuiltInTask("len")
BuiltInTask.toString = BuiltInTask("toString")
BuiltInTask.append = BuiltInTask("append")
BuiltInTask.pop = BuiltInTask("pop") 
BuiltInTask.extend = BuiltInTask("extend")
BuiltInTask.remove = BuiltInTask("remove")
BuiltInTask.clearList = BuiltInTask("clearList")
BuiltInTask.delay = BuiltInTask("delay")
BuiltInTask.format = BuiltInTask("format")

GlobalSymbolTable = Global()
GlobalSymbolTable.set('print', BuiltInTask.print)   
GlobalSymbolTable.set('println', BuiltInTask.println)
GlobalSymbolTable.set('exit', BuiltInTask.exit)
GlobalSymbolTable.set('input', BuiltInTask.input)
GlobalSymbolTable.set('inputInt', BuiltInTask.inputInt)
GlobalSymbolTable.set('inputFloat', BuiltInTask.inputFloat)
GlobalSymbolTable.set('clear', BuiltInTask.clear)
GlobalSymbolTable.set('len', BuiltInTask.len)
GlobalSymbolTable.set('toString', BuiltInTask.toString)
GlobalSymbolTable.set('append', BuiltInTask.append)
GlobalSymbolTable.set('pop', BuiltInTask.pop)
GlobalSymbolTable.set('extend', BuiltInTask.extend)
GlobalSymbolTable.set('remove', BuiltInTask.remove)
GlobalSymbolTable.set('clearList', BuiltInTask.clearList)
GlobalSymbolTable.set('delay', BuiltInTask.delay)
GlobalSymbolTable.set('format', BuiltInTask.format)
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
        context = Context('<module>')
        context.symbolTable = GlobalSymbolTable
        result = interpreter.visit(ast.node, context)
        
        if hasattr(result, 'value') and hasattr(result, 'error'):
            return result.value, result.error
        return result, None

    def runFile(fileName):
        try:
            with open(fileName, 'r') as file:
                text = file.read()
                # check if file is ending with .alden
                if fileName[-6:] != ".alden":
                    print("File is not alden file")
                    return
                else:
                    return Program.run(fileName, text)
        except FileNotFoundError:
            print(f'File {fileName} not found')
            
    def repl():
        while True:
            text = input('>>> ')
            result, error = Program.run("<stdin>", text)
            if error:
                print(error)
            elif result:
                if result == None:
                    result
                else:
                    if result == "()":  # empty result, parser is returning ParserResult() or RuntimeResult() so we can't print it
                        result
                    else:
                        print(result)
    def runRepl():
        try:
            Program.repl()
        except KeyboardInterrupt:
            print("\nExit?")
            print('Use exit() to exit')
            Program.runRepl()
            

