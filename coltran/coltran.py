import sys
import os
import platform
sys.path.append("./")
from Program.program import Al_Program





   
def getOs():
    if os.name == 'nt':
        result = f"windows {64 if platform.machine().endswith('64') else platform.machine()} [{platform.machine()}]"
    else:
        result = f"{os.name} {platform.machine()}"
    return result



def repl():
    """ Coltran Repl """
    print(f"Coltran 1.0 on {getOs()}")
    print('Type "help" for more information. Use "exit()" to exit.')
    Al_Program.runRepl()
    
   

def run(file):
    """ Run an Coltran file"""
    if file:
        Al_Program.runFile(file)
    else:
        print("No file specified")
        sys.exit(1)
 


def init_cmd(cmd: str):
    if cmd:
        run(cmd)
    elif cmd == "repl":
        repl()

def init_cmd_file(cmd: str, file: str):
    if cmd == "-r":
        run(file)
    elif cmd:
        run(cmd)
    else:
        repl()

def init():
    repl()




if __name__ == "__main__":
    if len(sys.argv) == 1:
        init()
    elif len(sys.argv) == 2:
        init_cmd(sys.argv[1])
    elif len(sys.argv) == 3:
        init_cmd_file(sys.argv[1], sys.argv[2])
