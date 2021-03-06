# This is a very basic assembler for the RISC-V RV32I base instruction set.
# It supports most instructions, except for FENCE, FENCE.I, ECALL, EBREAK, 
# CSRRW, CSRRS, CSRRC, CSRRWI, CSRRWI, CSRRSI, and CSRRCI.

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
    "lw": "010",
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

path = input("Enter assembly file path: ")
instrList = []
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

        #assemble instructions in binary
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

        elif (instrType == "I"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            funct3 = funct3Dict[opcode]

            #print(lineToken)
            #print(args)
            
            rs1Int = regDict[args[1]]
            rs1 = bindigits(rs1Int, 5)

            imm = ""
            
            if (opcode == "slli" or opcode == "srli"):
                imm = "0000000" + bindigits(int(args[2]), 5)
            elif (opcode == "srai"):
                imm = "0100000" + bindigits(int(args[2]), 5)
            else:
                imm = bindigits(int(args[2]), 12)     

            instruction += (imm + rs1 + funct3 + rd + opcodeBin)

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

        #currently does shift BEFORE re-arranging bits--not sure if correct
        elif (instrType == "B"):

            immUnsplit = bindigits((int(args[2], 16) - pc) >> 1, 12)
            upperImm = immUnsplit[0] + immUnsplit[2:8]
            lowerImm = immUnsplit[8:12] + immUnsplit[1]

            funct3 = funct3Dict[opcode]

            rs1Int = regDict[args[0]]
            rs1 = bindigits(rs1Int, 5)

            rs2Int = regDict[args[1]]
            rs2 = bindigits(rs2Int, 5)

            instruction += (upperImm + rs2 + rs1 + funct3 + lowerImm + opcodeBin)

        elif (instrType == "U"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            imm = bindigits(int(args[1], 16), 20)

            instruction += (imm + rd + opcodeBin)

        #currently does shift BEFORE re-arranging bits--not sure if correct
        elif (instrType == "J"):

            rdInt = regDict[args[0]]
            rd = bindigits(rdInt, 5)

            immUnordered = bindigits((int(args[1], 16) - pc) >> 1, 20)
            immOrdered = (immUnordered[0] + immUnordered[10:20] + immUnordered[9] + immUnordered[1:9])
            #immOrdered = bindigits((int(immOrdered, 2) >> 1), 20)

            instruction += (immOrdered + rd + opcodeBin)

        #skip junk instructions
        else:
            continue 

        #prepare for writing to file
        instructionHex = '{0:08X}'.format(int(instruction, 2))
        instrList.append(instructionHex)

        #end stuff
        line = fp.readline()
        pc += 4

#generate string to write (imitates given vmh format)
instrString = "@00000000"
instrCount = 0

for instr in instrList:

    if (instrCount % 4 == 0):
        instrString += "\n"

    instrString += (instr + " ")
    instrCount += 1

#write to file
destPath = (path.split(".")[0]) + ".vmh"
print("Generated vmh file: " + destPath)
destFile = open(destPath, "w")
destFile.write(instrString)
destFile.close()


