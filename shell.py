from Program.program import Program

while True:
    text = input('alden >> ')
    if text:
        result, error = Program.run("<stdin>",text)
        if error:
            print(error.as_string())
        elif result:
            print(result)
    else:
        result, error = Program.runFile("./test/main.alden")
        if error:
            print("")
        elif result:
            print(result)
  

