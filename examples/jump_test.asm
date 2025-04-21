; Initial values

IN   0000
STO  0020
IN   0001

; Conditional

CMP  0020
JL   JL_teste   ; ACC > Mem[20]
JG   JG_teste   ; ACC < Mem[20]

LDI  0001       ; OUT = 1 são iguais!
OUT  0000
HLT  0000

; Results

JL_teste:

	LDI  0002     ; OUT = 2 (IN1 > IN0)
	OUT  0000
	JUMP END

JG_teste:

	LDI  0003					; OUT = 2 (IN0 > IN1)
	OUT  0000

END:

	HLT 0000


