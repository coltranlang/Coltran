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
        result, error = Program.runFile("./aldenlang/main.alden")
        if error:
            print("")
        elif result:
            result
            
# import basic

# while True:
# 	text = input('basic > ')
# 	if text.strip() == "":
# 	    continue
# 	result, error = basic.runFile("./aldenlang/main.alden")

# 	if error:
# 		print(error.as_string())
# 	elif result:
# 		if len(result.elements) == 1:
# 			print(repr(result.elements[0]))
# 		else:
# 			print(repr(result))
