#  Copyright (c) 2021, Alden Authors.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of Alden Org. nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# File:
#   Memory/memory.py
# Author:
#   Kehinde Akinsanya
# Created:
#   October 28, 2021
# Description:
#   Memory module for Alden

import sys
from Parser.stringsWithArrows import stringsWithArrows




class Program:
    def error():
        def Default(name, message):
            error = f'\n{name}: {message}\n'
            Program.printNoExitError(error)

        def DefaultExit(name, message):
            error = f'\n{name}: {message}\n'
            Program.printError(error)

        def NameError(detail):
            isDetail = {
                'name': 'NameError',
                'message': detail['message'],
                'pos_start': detail['pos_start'],
                'pos_end': detail['pos_end'],
                'context': detail['context']
            }
            Program.printError(Program.asStringTraceBack(isDetail))

        
        methods = {
            'Default': Default,
            'DefaultExit': DefaultExit,
            'NameError': NameError
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
        return sum([ord(char) for char in key]) % self.size
    
    
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


    def __repr__(self):
        return str(self.slots) + '\n' + str(self.data)


class Stack:
    def __init__(self):
        self.stack = []
        self.id = 0

    def push(self, item, id):
        self.stack.append({
            'id': id,
            'item': item
        })

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def isEmpty(self):
        return len(self.stack) == 0

    def __repr__(self):
        output = 'Current stack:\n'
        for item in self.stack:
            output += f'{item}\n'


class Environment:
    def __init__(self, parent=None):
        self.members = HashTable(1000)
        self.parent = parent

    def get(self, key):
        value = self.members.get(key)
        if value == None and self.parent:
            value = self.parent.get(key)
        if value == None:
            return "none"
        return value
    
    def set(self, key, value):
        self.members.set(key, value)
        
    def __repr__(self):
        output = 'Current environment:\n'
        for item in self.members.getSlots():
            if item != None:
                output += str(item) + '\n'
        return output


class Module:
    def __init__(self, parent=None):
        self.modules = {}
        self.parent = parent

    def get(self, key):
        value = self.modules.get(key, None)
        if value == None and self.parent:
            value = self.parent.get(key)
        if value == None:
            return "none"
        return value
    
    def is_module_in_members(self, key):
        return key in self.modules

    def set(self, key, value):
        self.modules[key] = value
        
    def __repr__(self):
        output = 'Current modules:\n'
        for item in self.modules:
            output += str(item) + '\n'
        return output
   
    
class Al_NameError(Exception):
    def __init__(self, message):
        self.name = "NameError"
        self.message = message
        self.error()
        
    def error(self):
        return Program.error()[self.name](self.message)
  
    
class SymbolTable:
   
    def __init__(self, parent=None):
        self.symbols = {}
        self.modules = Module()
        self.id = 0
        self.parent = parent
        self.scope = Environment(self.parent)
    
    def get_by_value(self, value):
        for key, val in self.symbols.items():
                return key
        return None
      
    def set(self, name, value, type=None):
        if not value:
            value = "none"
        if type:
            self.symbols[name] = {
                'value': value,
                'type': type
            }
        else:
            self.symbols[name] = value
        
    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
        
    def set_object(self, obj_name, object):
        self.symbols[obj_name] = object
            
    def get_object(self, owner, obj_name, key, type):
        if owner.name.value in self.symbols:
            return self.symbols[owner.name.value].get_property(owner,obj_name, key, type)
        else:
            return "none"
   
    def set_final(self, name, value, type_=None):
        if name in self.symbols:
            return 'already_declared'
        else:
            if type_:
                self.symbols[name] = {
                    'value': value, 
                    'type': type
                }
            else:
                self.symbols[name] = value
                   
    def set_current_scope(self, scope):
        self.scope = scope

    def get_current_scope(self):
        return self.scope
   
    def set_exception(self, error):
        self.exception = error
        
    def get_exception(self):
        return self.exception
    
    def set_module(self, name, module):
        self.modules.set(name, module)
 
    def setSymbol(self):
        self.set("none", "none")
        self.set("true",  "true")
        self.set("false", "false")
   
    def remove(self, name):
        del self.symbols[name]
           
    def __repr__(self):
        result = {
            'symbols': self.symbols,
            'parent': self.parent
        }
        return str(result)


class ModuleNameSpace:
    def __init__(self):
        self.namespace = {}
    
    
    def set(self, name, value):
        self.namespace[name] = value

        
    def get(self, name):
        value = self.namespace.get(name, None)
        return value
        
   
    def remove(self, name):
        del self.namespace[name]
        
    def __repr__(self):
        result = {
            'namespace': self.namespace,
        }
        return str(result)

# hash = HashTable(1000)
# hash.set("key", "value")
# print(hash.get("key"))

# env = Environment()
# env.set("key", "value")
# print(env.get("key"))
# print(env.get("key2"))

