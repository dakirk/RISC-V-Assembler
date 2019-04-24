# RISC-V-Assembler
Very basic assembler for the RISC-V RV32I instruction set. Intended to help with the BU EC413 final project.

This assembler does not support the FENCE, FENCE.I, ECALL, EBREAK, CSRRW, CSRRS, CSRRC, CSRRWI, CSRRWI, CSRRSI,
or CSRRCI instructions. For the rest, this assembler supports two syntaxes for writing instruction arguments:
- "imm(rs)" for LW, SW, and JALR (immediate is an offset)
- "rs imm" for all other instructions with immediates

