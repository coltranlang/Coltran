import sys
from Parser.stringsWithArrows import *

class Program:
    def error():
        def Default(name, message):
            error = f'\n{name}: {message}\n'
            Program.printNoExitError(error)

        def DefaultExit(name, message):
            error = f'\n{name}: {message}\n'
            Program.printError(error)

        def Runtime(detail):
            isDetail = {
                'name': 'RuntimeError',
                'type': 'invalid syntax',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            Program.printError(Program.asStringTraceBack(isDetail))
        methods = {
            'Default': Default,
            'Runtime': Runtime,
            'DefaultExit': DefaultExit
        }
        return methods

    def printError(*args):
        for arg in args:
            print(arg)
        sys.exit(1)

    def printNoExitError(*args):
        for arg in args:
            print(arg)

    def asStringTraceBack(detail):
        result = Program.generateTraceBack(detail)
        result += f'\n{detail["name"]}: {detail["message"]}\n'
        result += '\n\n' + \
            stringsWithArrows(
                detail["pos_start"].fileText, detail["pos_start"], detail["pos_end"])
        return result

    def generateTraceBack(detail):
        result = ''
        pos = detail['pos_start']
        context = detail['context']
        while context:
            result += f'\nFile {detail["pos_start"].fileName}, line {str(pos.line + 1)} in {context.display_name}\n' + result
            pos = context.parent_entry_pos
            context = context.parent
        return '\nStack trace (most recent call last):\n' + result



class Global:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def set_final(self, name, value):
        if name in self.symbols:
            Program.error()["Default"](
                "SyntaxError", "Identifier '{name}' cannot be redecalred".format(name=name))
        else:
            self.symbols[name] = value

    def setGlobal(self):
        self.set("none", "none")
        self.set("Boolean",  "true")
        self.set("Boolean", "false")

    def remove(self, name):
        del self.symbols[name]


