from Program.program import Program

while True:
    text = input('alden >> ')
    #if text.strip(): continue
    if text:
        result, error = Program.run("<stdin>",text)
        if error:
            print(error)
        elif result:
            if result == None:
                result
            else:
                print(result)
    else:
        result, error = Program.runFile("./aldenlang/input.alden")
        if error:
            print("")
        elif result:
            result
