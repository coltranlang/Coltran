import sys
from Lexer.lexer import Lexer
from Parser.parser import Parser
from Interpreter.interpreter import Context, Interpreter, symbolTable_

class Program:
    def error():
        def IllegalCharacter(options):
            error = f'\nFile: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n\nSyntaxError: Illegal character unexpected  {options["originator"]}\n'
            Program.printError(error)

        def Syntax(options):
            error = ""
            error += f'\nFile: {options["fileName"]}  \n\nSyntaxError: {options["originator"]}\n'
            Program.printError(error)

        def Runtime(options):
            error = ""
            error += f'\nFile: {options["fileName"]}  \n\nRuntimeError: {options["originator"]}\n'
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
  
    def printError(arg):
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
        interpreter = Interpreter()
        context = Context('<module>')
        parser_error_detected = parser.error_detected
        if parser_error_detected == False:
            if ast:
                if ast.error:
                    return "", ast.error
                context.symbolTable = symbolTable_
                result = interpreter.visit(ast.node, context)
                interpreter_error_detected = interpreter.error_detected
                #print(f"Error detected: {interpreter_error_detected}")
                if hasattr(result, 'value') and hasattr(result, 'error'):
                    return result.value, ""

                return result, "none"
            else:
                return "none"
        else:
            return "", ''
        # try:
        #     ast = parser.parse()
        #     interpreter = Interpreter()
        #     context = Context('<module>')
        #     parser_error_detected = parser.error_detected
        #     if parser_error_detected == False:
        #         if ast:
        #             if ast.error:
        #                 return "", ast.error
        #             context.symbolTable = symbolTable_
        #             result = interpreter.visit(ast.node, context)
        #             interpreter_error_detected = interpreter.error_detected
        #             if hasattr(result, 'value') and hasattr(result, 'error'):
        #                 return result.value, ""

        #             return result, "none"
        #         else:
        #             return "none"
        #     else:
        #         return "", ''
        # except:
        #     Program.error()['Syntax']({
        #         'originator': 'invalid syntax or unexpected error',
        #         'fileName': fileName,
        #     })

    def runFile(fileName):
        try:
            with open(fileName, 'r') as file:
                text = file.read()
                if fileName[-4:] != ".ald":
                    print(f"File '{fileName}' is not a valid alden file")
                    return
                else:
                    result  = Program.run(fileName, text)
                    return result
        except FileNotFoundError:
            print(f"can't open file '{fileName}': No such file or directory")
            return False
    
    def repl():
        while True:
            text = input('>>> ')
            result, error = Program.run("<stdin>", text)
            if type(result).__name__ == "List":
                if len(result.elements) == 1:
                    result = result.elements[0]
                    print(result) if result != None else print("")
                else:
                    result = result.elements
                    print(result)
            if error:
                error = 'none'
                print(error)
   
    def runRepl():
        try:
            Program.repl()
        except KeyboardInterrupt:
            print("\nExit?")
            print('Use exit() to exit')
            Program.runRepl()
            

