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
                if result == "()": # empty result, parser is returning ParserResult() or RuntimeResult() so we can't print it
                    print()
                else:
                    print(result)
    else:
        result, error = Program.runFile("./aldenlang/input.alden")
        if error:
            print("")
        elif result:
            result
