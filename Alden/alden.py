from click.core import Argument
import typer
import sys
import os
import platform
sys.path.append("./")
from Program.program import Program


app = typer.Typer()


# @app.command()
# def run():
#    text = input('alden >> ')
   
def getOs():
    if os.name == 'nt':
        result = f"windows {64 if platform.machine().endswith('64') else platform.machine()} [{platform.machine()}]"
    else:
        result = f"{os.name} {platform.machine()}"
    return result



def repl():
    """ Repl """
    print(f"Alden 1.0 on {getOs()}")
    Program.runRepl()
    
   

def run(file):
    """ Run an Alden file"""
    if file:
        Program.runFile(file)
    else:
        print("No file specified")
        sys.exit(1)
 

@app.command()
def init(cmd: str = typer.Argument(""), file: str = typer.Argument("")):
    if cmd:
        run(cmd)
    elif cmd == "repl":
        repl()
    else:
        repl()




if __name__ == "__main__":
    typer.run(init)
