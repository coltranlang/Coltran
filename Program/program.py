import os
import sys
from Lexer.lexer import Lexer
from Parser.parser import Parser
from Interpreter.interpreter import Context, Interpreter, symbolTable_, Program, ModuleNameSpace

I_Al_Program = Program
language_ext = {
    'coltran': 'coltran',
    'ctrn': 'ctrn',
    'ctn': 'ctn',
    'ct': 'ct',
}

class Al_Program:
    def error():
        def IllegalCharacter(options):
            error = f'\nFile: {options["pos_start"].fileName} at line {options["pos_start"].line + 1}\n\nSyntaxError: Illegal character unexpected  {options["originator"]}\n'
            Al_Program.printError(error)

        def Syntax(options):
            error = ""
            error += f'\nFile: {options["fileName"]}  \n\nSyntaxError: {options["originator"]}\n'
            Al_Program.printError(error)

        def Runtime(options):
            error = ""
            error += f'\nFile: {options["fileName"]}  \n\nRuntimeError: {options["originator"]}\n'
            Al_Program.printError(error)
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
        context = Context('<module>')
        modulenameSpace = ModuleNameSpace()
        lexer = Lexer(fileName, text, context)
        try:
            tokens, error = lexer.make_tokens()
            if error:
                return "", error

            # Generate AST
            parser = Parser(tokens, fileName, context)
            ast = parser.parse()
            interpreter = Interpreter()
            parser_error_detected = parser.error_detected
            # ast = parser.parse()
            # interpreter = Interpreter()
            # context = Context('<module>')
            # parser_error_detected = parser.error_detected
            # if parser_error_detected == False:
            #     if ast:
            #         if ast.error:
            #             return "", ast.error
            #         context.symbolTable = symbolTable_
            #         result = interpreter.visit(ast.node, context)
            #         interpreter_error_detected = interpreter.error_detected
            #         #print(f"Error detected: {interpreter_error_detected}")
            #         if hasattr(result, 'value') and hasattr(result, 'error'):
            #             return result.value, ""

            #         return result, "none"
            #     else:
            #         return "none"
            # else:
            #     return "", ''
            try:
                if parser_error_detected == False:
                    if ast:
                        if ast.error:
                            return "", ast.error
                        context.symbolTable = symbolTable_
                        result = interpreter.visit(ast.node, context)
                        return result.value, ""
                    else:
                        return ""
                else:
                    return None
            except Exception as e:
                return I_Al_Program.error()[e.name](e.message)
        except Exception as e:
           raise e
        
    def runFile(fileName):
        try:
            with open(fileName, 'r', encoding='utf-8') as file:
                text = file.read()
                if fileName[-7:] != language_ext['coltran'] and fileName[-4:] != language_ext['ctrn'] and fileName[-3:] != language_ext['ctn'] and fileName[-2:] != language_ext['ct']:
                    print(f"File '{fileName}' is not a valid coltran file")
                    return
                else:
                    fileName = os.path.abspath(fileName)
                    result  = Al_Program.run(fileName, text)
                    return result
                
        except FileNotFoundError:
            print(f"can't open file '{fileName}': No such file or directory")
            return False
        except Exception as e:
            raise e
    
    def repl():
        try:
            while True:
                text = input('>>> ')
                # allow user to be able to create a function
                if text == 'def':
                    text = input('>>> ')
                    text = 'def ' + text
                result, error = Al_Program.run("<stdin>", text)
                if type(result).__name__ == "List":
                    if len(result.elements) == 1:
                        result = result.elements[0]
                        print(result) if result != None else print("")
                    else:
                        result = result.elements
                        print(result) if result != None else print("")
                if error:
                    error = 'none' if error == '' else error
                    print(error)
        except KeyboardInterrupt:
            print("\nExit?")
            print('Use exit() to exit')
            Al_Program.repl()
        except Exception as e:
            if text == "exit()" or text == "exit":
                sys.exit(0)
            Al_Program.repl()
   
    def runRepl():
        Al_Program.repl()
            

