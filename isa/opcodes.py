"""Opcode definitions for the stack-based architecture."""

from enum import IntEnum


class Opcode(IntEnum):
    """Instruction opcodes for stack-based architecture with vector extensions."""
    
    # Core stack operations
    PUSH = 0x00     # Push value to stack
    POP = 0x01      # Pop value from stack
    DUP = 0x02      # Duplicate top of stack
    SWAP = 0x03     # Swap top two elements
    DROP = 0x04     # Drop top element
    
    # Arithmetic
    ADD = 0x10      # Add
    SUB = 0x11      # Subtract
    MUL = 0x12      # Multiply
    DIV = 0x13      # Divide
    MOD = 0x14      # Remainder
    NEG = 0x15      # Negate
    
    # Logic
    AND = 0x20      # Logical AND
    OR = 0x21       # Logical OR
    XOR = 0x22      # XOR
    NOT = 0x23      # Logical NOT
    
    # Comparisons
    EQ = 0x30       # Equal
    NE = 0x31       # Not equal
    LT = 0x32       # Less than
    LE = 0x33       # Less or equal
    GT = 0x34       # Greater than
    GE = 0x35       # Greater or equal
    
    # Control flow
    JMP = 0x40      # Unconditional jump
    JZ = 0x41       # Jump if zero
    JNZ = 0x42      # Jump if not zero
    CALL = 0x43     # Call
    RET = 0x44      # Return
    
    # Memory
    LOAD = 0x50     # Load from data memory at TOS
    STORE = 0x51    # Store to data memory
    LOAD_I = 0x52   # Load from instruction memory
    LOADB = 0x53    # Load byte from data memory
    STOREB = 0x54   # Store byte to data memory
    
    # I/O
    IN = 0x60       # Input from port
    OUT = 0x61      # Output to port
    
    # System
    HALT = 0x70     # Halt
    NOP = 0x71      # No operation
    INT = 0x72      # Software interrupt
    IRET = 0x73     # Interrupt return
    
    # Vector extension
    V_LOAD = 0x80   # Load vector
    V_STORE = 0x81  # Store vector
    V_ADD = 0x82    # Vector add
    V_SUB = 0x83    # Vector sub
    V_MUL = 0x84    # Vector mul
    V_DIV = 0x85    # Vector div
    V_CMP = 0x86    # Vector compare
    V_DOT = 0x87    # Dot product
    V_NORM = 0x88   # Vector norm
    V_MAX = 0x89    # Max element
    V_MIN = 0x8A    # Min element
    V_SUM = 0x8B    # Sum elements
    V_AVG = 0x8C    # Average
    V_SCALE = 0x8D  # Scale vector
    V_COPY = 0x8E   # Copy vector
    V_SET = 0x8F    # Set element


# Instruction sizes (in words)
INSTRUCTION_SIZES = {
    # No-operand instructions
    Opcode.POP: 1,
    Opcode.DUP: 1,
    Opcode.SWAP: 1,
    Opcode.DROP: 1,
    Opcode.ADD: 1,
    Opcode.SUB: 1,
    Opcode.MUL: 1,
    Opcode.DIV: 1,
    Opcode.MOD: 1,
    Opcode.NEG: 1,
    Opcode.AND: 1,
    Opcode.OR: 1,
    Opcode.XOR: 1,
    Opcode.NOT: 1,
    Opcode.EQ: 1,
    Opcode.NE: 1,
    Opcode.LT: 1,
    Opcode.LE: 1,
    Opcode.GT: 1,
    Opcode.GE: 1,
    Opcode.LOAD: 1,
    Opcode.STORE: 1,
    Opcode.LOAD_I: 1,
    Opcode.LOADB: 1,
    Opcode.STOREB: 1,
    Opcode.RET: 1,
    Opcode.HALT: 1,
    Opcode.NOP: 1,
    Opcode.IRET: 1,
    
    # Single-operand instructions
    Opcode.PUSH: 2,
    Opcode.JMP: 2,
    Opcode.JZ: 2,
    Opcode.JNZ: 2,
    Opcode.CALL: 2,
    Opcode.IN: 2,
    Opcode.OUT: 2,
    Opcode.INT: 2,
    
    # Vector instructions (with operands where applicable)
    Opcode.V_LOAD: 2,
    Opcode.V_STORE: 2,
    Opcode.V_ADD: 1,
    Opcode.V_SUB: 1,
    Opcode.V_MUL: 1,
    Opcode.V_DIV: 1,
    Opcode.V_CMP: 1,
    Opcode.V_DOT: 1,
    Opcode.V_NORM: 1,
    Opcode.V_MAX: 1,
    Opcode.V_MIN: 1,
    Opcode.V_SUM: 1,
    Opcode.V_AVG: 1,
    Opcode.V_SCALE: 1,
    Opcode.V_COPY: 1,
    Opcode.V_SET: 2,
}


# Instruction cycle counts
INSTRUCTION_CYCLES = {
    Opcode.NOP: 1,
    Opcode.PUSH: 2,
    Opcode.POP: 1,
    Opcode.DUP: 2,
    Opcode.SWAP: 2,
    Opcode.DROP: 1,
    Opcode.ADD: 3,
    Opcode.SUB: 3,
    Opcode.MUL: 4,
    Opcode.DIV: 6,
    Opcode.MOD: 6,
    Opcode.NEG: 2,
    Opcode.AND: 2,
    Opcode.OR: 2,
    Opcode.XOR: 2,
    Opcode.NOT: 2,
    Opcode.EQ: 3,
    Opcode.NE: 3,
    Opcode.LT: 3,
    Opcode.LE: 3,
    Opcode.GT: 3,
    Opcode.GE: 3,
    Opcode.JMP: 2,
    Opcode.JZ: 3,
    Opcode.JNZ: 3,
    Opcode.CALL: 4,
    Opcode.RET: 3,
    Opcode.LOAD: 4,
    Opcode.STORE: 4,
    Opcode.LOAD_I: 4,
    Opcode.LOADB: 4,
    Opcode.STOREB: 4,
    Opcode.IN: 5,
    Opcode.OUT: 5,
    Opcode.HALT: 1,
    Opcode.INT: 8,
    Opcode.IRET: 6,
    # Vector operations (slower)
    Opcode.V_LOAD: 8,
    Opcode.V_STORE: 8,
    Opcode.V_ADD: 4,
    Opcode.V_SUB: 4,
    Opcode.V_MUL: 6,
    Opcode.V_DIV: 12,
    Opcode.V_CMP: 4,
    Opcode.V_DOT: 8,
    Opcode.V_NORM: 10,
    Opcode.V_MAX: 4,
    Opcode.V_MIN: 4,
    Opcode.V_SUM: 4,
    Opcode.V_AVG: 6,
    Opcode.V_SCALE: 4,
    Opcode.V_COPY: 4,
    Opcode.V_SET: 2,
}


def get_opcode_name(opcode: int) -> str:
    """Get opcode name by numeric value."""
    try:
        return Opcode(opcode).name
    except ValueError:
        return f"UNKNOWN_{opcode:02X}"


VECTOR_BASE = 0x80


def is_vector_operation(opcode: int) -> bool:
    """Check if opcode is a vector operation."""
    return opcode >= VECTOR_BASE