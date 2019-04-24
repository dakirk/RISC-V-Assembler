import re

#does 2's complement (from here: https://stackoverflow.com/questions/12946116/twos-complement-binary-in-python/12946226)
def bindigits(n, bits):
    s = bin(n & int("1"*bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)

#dictionary for registers
regDict = {
    "zero": 0,
    "ra": 1,
    "sp": 2,
    "gp": 3,
    "tp": 4,
    "t0": 5,
    "t1": 6,
    "t2": 7,
    "s0": 8,
    "fp": 8,
    "s1": 9
}
for key in map(lambda x: 'a' + str(x), range(8)):
    regDict[key] = int(key[1:]) + 10
for key in map(lambda x: 's' + str(x), range(2,12)):
    regDict[key] = int(key[1:]) + 16
for key in map(lambda x: 't' + str(x), range(3,7)):
    regDict[key] = int(key[1:]) + 25


#dictionary for opcodes
opcodeDict = {
    "lui": ["0110111", "U"],
    "auipc": ["0010111", "U"],
    "jal": ["1101111", "J"],
    "jalr": ["1100111", "I"],
    "lw": ["0000011", "I"],
    "sw": ["0100011", "S"]
}
for key in ["addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai"]:
    opcodeDict[key] = ["0010011", "I"]
for key in ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"]:
    opcodeDict[key] = ["0110011", "R"]
for key in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
    opcodeDict[key] = ["1100011", "B"]


#dictionary for funct7
funct7Dict = {}
for key in ["add", "sll", "slt" "sltu", "xor", "srl", "or", "and"]:
    funct7Dict[key] = "0000000"
for key in ["sub", "sra"]:
    funct7Dict[key] = "0100000"

#dictionary for funct3
funct3Dict = {
    "add": "000",
    "addi": "000",
    "sub": "000",
    "jalr": "000",
    "sll": "001",
    "slli": "001",
    "slt": "010",
    "slti": "010",
    "lw": "101",
    "sltu": "011",
    "sltiu": "011",
    "xor": "100",
    "xori": "100",
    "srl": "101",
    "srli": "101",
    "sra": "101",
    "srai": "101",
    "or": "110",
    "ori": "110",
    "and": "111",
    "andi": "111",
    "beq": "000",
    "bne": "001",
    "blt": "100",
    "bge": "101",
    "bltu": "110",
    "bgeu": "111"
    
}    

print("Warning! B-type and J-type instruction offsets aren't working properly")
path = input("Enter assembly file path: ")
dest = input("Enter destination file path: ")
#print(path)

with open(path, 'r') as fp:
    line = fp.readline()
    pc = 0

    while line:

        #skip over empty lines
        if (line.strip() == ''):
            line = fp.readline()
            continue

        

        lineToken = (line.strip()).split()
        opcode = lineToken[0]
        args = []

        #handle parentheses syntax
        if (opcode == "jalr" or opcode == "lw" or opcode == "sw"):
            tempArgs = lineToken[1].split(",")
            rs1Imm = [tempArgs[1].split("(")[0], tempArgs[1].split("(")[1].split(")")[0]] #I know this is horriffic but I don't understand regex
            args = [tempArgs[0], rs1Imm[1], rs1Imm[0]]
        else:
            args = lineToken[1].split(",")
        
        instrType = opcodeDict[opcode][1]
        opcodeBin = opcodeDict[opcode][0]

        instruction = ""
        #print(opcodeDict[opcode])

        if (instrType == "R"):
            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            funct3 = funct3Dict[opcode]

            rs1Int = regDict[args[1]]
            rs1 = bindigits(rs1Int, 5)

            rs2Int = regDict[args[2]]
            rs2 = bindigits(rs2Int, 5)

            funct7 = funct7Dict[opcode]

            instruction += (funct7 + rs2 + rs1 + funct3 + rd + opcodeBin)
            #print(instruction)
            #print(hex(int(instruction, 2)))

        elif (instrType == "I"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            funct3 = funct3Dict[opcode]

            #print(lineToken)
            #print(args)
            
            rs1Int = regDict[args[1]]
            rs1 = bindigits(rs1Int, 5)

            imm = ""

            #print(lineToken)
            
            if (opcode == "slli" or opcode == "srli"):
                imm = "0000000" + bindigits(int(args[2]), 5)
            elif (opcode == "srai"):
                imm = "0100000" + bindigits(int(args[2]), 5)
            else:
                imm = bindigits(int(args[2]), 12)

            #if (opcode == "jalr"):
                #("rd: " + rd + "\nrs1: " + rs1 + "\nimm: " + imm)
                          

            instruction += (imm + rs1 + funct3 + rd + opcodeBin)
            #print(hex(int(instruction, 2)))
            #print(instruction)

        elif (instrType == "S"):
            
            rs2Int = regDict[args[0]]
            rs2 = bindigits(rs2Int, 5)

            funct3 = "010"

            immUnsplit = bindigits(int(args[2]), 12)
            upperImm = immUnsplit[0:7]
            lowerImm = immUnsplit[7:12]

            rs1Int = regDict[args[1]]
            rs1 = bindigits(rs1Int, 5)

            instruction += (upperImm + rs2 + rs1 + funct3 + lowerImm + opcodeBin)
            #print(line)
            #print(instruction)
            #print(hex(int(instruction, 2)))

        #jumps to the PC + given offset, so beware!
        elif (instrType == "B"):

            immUnsplit = bindigits(int(args[2], 16), 12)
            upperImm = immUnsplit[0] + immUnsplit[2:8]
            lowerImm = immUnsplit[8:12] + immUnsplit[1]

            funct3 = funct3Dict[opcode]

            rs1Int = regDict[args[0]]
            rs1 = bindigits(rs1Int, 5)

            rs2Int = regDict[args[1]]
            rs2 = bindigits(rs2Int, 5)

            instruction += (upperImm + rs2 + rs1 + funct3 + lowerImm + opcodeBin)
            #print(line)
            #print(int(args[2], 16))
            #print(immUnsplit)
            #print(instruction)
            #print(hex(int(instruction, 2)))

        elif (instrType == "U"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            imm = bindigits(int(args[1], 16), 20)

            instruction += (imm + rd + opcodeBin)

            #print(lineToken)
            #print(args)
            #print(instruction)
            #print(hex(int(instruction, 2)))

        #jumps to the PC + given offset, so beware! offset seems weird right now
        elif (instrType == "J"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            immUnordered = bindigits(int(args[1], 16), 20)
            immOrdered = immUnordered[0] + immUnordered[10:20] + immUnordered[9] + immUnordered[1:9]

            instruction += (immOrdered + rd + opcodeBin)
            
            #print(args)
            #print(immOrdered)
            #print(instructionHex)

        #skip junk instructions
        else:
            continue 

        instructionHex = '{0:08X}'.format(int(instruction, 2))
        #print(lineToken)
        print('{0:04X}'.format(pc) + ": " + lineToken[0] + " " + lineToken[1] + ": " + instructionHex)






        #end stuff
        line = fp.readline()
        pc += 4

print("done")
