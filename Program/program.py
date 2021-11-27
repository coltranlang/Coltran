import sys
from Lexer.lexer import Lexer
from Parser.parser import Parser
from Interpreter.interpreter import Context, Interpreter, BuiltInTask
from Memory.memory import SymbolTable

BuiltInTask.print = BuiltInTask("print")
BuiltInTask.println = BuiltInTask("println")
BuiltInTask.exit = BuiltInTask("exit")
BuiltInTask.input = BuiltInTask("input")
BuiltInTask.inputInt = BuiltInTask("inputInt")
BuiltInTask.inputFloat = BuiltInTask("inputFloat")
BuiltInTask.inputBool = BuiltInTask("inputBool")
BuiltInTask.clear = BuiltInTask("clear")
BuiltInTask.len = BuiltInTask("len")
#BuiltInTask.range = BuiltInTask("range")
BuiltInTask.str = BuiltInTask("str")
BuiltInTask.int = BuiltInTask("int")
BuiltInTask.float = BuiltInTask("float")
BuiltInTask.bool = BuiltInTask("bool")
BuiltInTask.list = BuiltInTask("list")
BuiltInTask.pair = BuiltInTask("pair")
BuiltInTask.object = BuiltInTask("object")
BuiltInTask.line = BuiltInTask("line")
BuiltInTask.typeOf = BuiltInTask("typeOf")
BuiltInTask.append = BuiltInTask("append")
BuiltInTask.pop = BuiltInTask("pop") 
BuiltInTask.extend = BuiltInTask("extend")
BuiltInTask.remove = BuiltInTask("remove")
BuiltInTask.clearList = BuiltInTask("clearList")
BuiltInTask.delay = BuiltInTask("delay")
BuiltInTask.format = BuiltInTask("format")


symbolTable_ = SymbolTable()
symbolTable_.set('print', BuiltInTask.print)   
symbolTable_.set('println', BuiltInTask.println)
symbolTable_.set('exit', BuiltInTask.exit)
symbolTable_.set('input', BuiltInTask.input)
symbolTable_.set('inputInt', BuiltInTask.inputInt)
symbolTable_.set('inputFloat', BuiltInTask.inputFloat)
symbolTable_.set('inputBool', BuiltInTask.inputBool)
symbolTable_.set('clear', BuiltInTask.clear)
symbolTable_.set('len', BuiltInTask.len)
#symbolTable_.set('range', BuiltInTask.range)
symbolTable_.set('str', BuiltInTask.str)
symbolTable_.set('int', BuiltInTask.int)
symbolTable_.set('float', BuiltInTask.float)
symbolTable_.set('bool', BuiltInTask.bool)
symbolTable_.set('list', BuiltInTask.list)
symbolTable_.set('pair', BuiltInTask.pair)
symbolTable_.set('object', BuiltInTask.object)
symbolTable_.set('line', BuiltInTask.line)
symbolTable_.set('typeOf', BuiltInTask.typeOf)
symbolTable_.set('append', BuiltInTask.append)
symbolTable_.set('pop', BuiltInTask.pop)
symbolTable_.set('extend', BuiltInTask.extend)
symbolTable_.set('remove', BuiltInTask.remove)
symbolTable_.set('clearList', BuiltInTask.clearList)
symbolTable_.set('delay', BuiltInTask.delay)
symbolTable_.set('format', BuiltInTask.format)
symbolTable_.setSymbol()

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
        parser = Parser(tokens, fileName)
        ast = parser.parse()
        if ast.error: return "", ast.error
        
        interpreter = Interpreter()
        context = Context('<module>')
        context.symbolTable = symbolTable_
        result = interpreter.visit(ast.node, context)
        
        if hasattr(result, 'value') and hasattr(result, 'error'):
            return result.value, result.error
        
        return result, "none"

    def runFile(fileName):
        try:
            with open(fileName, 'r') as file:
                text = file.read()
                # check if file is ending with .alden
                if fileName[-6:] != ".alden":
                    print("File is not an alden file")
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
            

