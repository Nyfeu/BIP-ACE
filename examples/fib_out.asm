; BREAK CONDITION

LDI 0987
STO 0007

; INITIAL VALUES

IN  0000
STO 0000
OUT 0000
IN  0001
STO 0001
OUT 0001

; CALC FIBONACCI

fib:
ADD 0000
STO 0000
OUT 0000
ADD 0001
STO 0001
OUT 0001

CMP  0007
JNE  fib
JUMP display

; DISPLAY RESULTS

display:

OUT 0001 ; x0262
LDI 0007
OUT 0000 ; x0007
HLT 0000

