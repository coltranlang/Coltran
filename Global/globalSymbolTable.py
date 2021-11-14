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



class HashTable:
    def __init__(self, size):
        self.size = size
        self.slots = [None] * self.size
        self.data = [None] * self.size

    def hashFunction(self, key):
        return key % self.size

    def rehash(self, oldHash):
        return (oldHash + 1) % self.size

    def get(self, key):
        start = self.hashFunction(key)

        pos = start
        while self.slots[pos] != None and self.slots[pos] != key:
            pos = self.rehash(pos)
            if pos == start:
                return None

        return self.data[pos]

    def set(self, key, data):
        start = self.hashFunction(key)

        pos = start
        while self.slots[pos] != None and self.slots[pos] != key:
            pos = self.rehash(pos)
            if pos == start:
                return None

        self.slots[pos] = key
        self.data[pos] = data
        
    def getSlots(self):
        return self.slots

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, data):
        self.set(key, data)

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def isEmpty(self):
        return len(self.stack) == 0

    def __str__(self):
        return str(self.stack)


class Global:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    
    def get_by_value(self, value):
        for key, val in self.symbols.items():
                return key
        return None
    
    def get_by_interp_value(self, value):
        for key, val in self.symbols.items():
            if str(val) == value:
                return key
        return None

    def set(self, name, value):
        self.symbols[name] = value
        if not value:
            value = "none"
        #print(f"{name} is set to {value}")

    def set_object(self, obj_name, object):
        if obj_name in self.symbols:
            self.set(obj_name, object)
        else:
            self.symbols[obj_name] = object
        
    def get_object(self, obj_name, key):
        if obj_name in self.symbols:
            return self.symbols[obj_name].get_property(key)
        else:
            return "none"

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
        
    def __repr__(self):
        result = {
            'symbols': self.symbols,
            'parent': self.parent
        }
        return str(result)




