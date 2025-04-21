; ======================================================================================== ;
; BIP I CPU INSTRUCTION SET TEST PROGRAM																																													 ;
; ======================================================================================== ;
;                                                                                          ;
; Description:                                                                             ;
;   This program tests all instructions in the BIP I CPU's instruction set.                ;
;   It uses output ports to indicate test status and input ports to provide test data.     ;
;                                                                                          ;                
; Output Port Usage:                                                                       ;
;   - out_port_1 (port 0000): Test status (0 = fail, 1 = pass)                             ;
;   - out_port_2 (port 0001): Current test step (1–8)                                      ;
;                                                                                          ;
; Input Port Usage:      																																													 ;
;   - in_port_1 (port 0000): Provides an input value for testing (e.g., X = 4095).         ;
;     This value is used in TEST 6 to verify the IN instruction.																											;
;                                                                                          ;
; Notes:       																																													 ;
;   - The input value X = 4095 (0xFFF in hexadecimal) is preloaded into in_port_1.         ;
;   - The program halts if any test fails, setting out_port_1 to 0.                        ;
;                                                                                          ;
; ======================================================================================== ;

; Initialize outputs to 0

LDI 0
OUT 0000  ; Reset out_port_1
OUT 0001  ; Reset out_port_2

; ---------------------------------------------------------------------------------------- ;
; TEST 1: LDI, STO, LD, OUT       																																													 ;
; ---------------------------------------------------------------------------------------- ;

LDI 1
OUT 0001  ; Test step = 1
LDI 4095  ; Max 12-bit value (4095)
STO 0000  ; Store in memory[0000]
LD 0000   ; Load back into ACC
CMP 0000  ; Compare ACC with memory[0000]
JNE fail  ; Fail if mismatch
LDI 1
OUT 0000  ; Pass

; ---------------------------------------------------------------------------------------- ;
; TEST 2: ADD and ADDI                                                                     ;
; ---------------------------------------------------------------------------------------- ;

LDI 2
OUT 0001  ; Test step = 2
LDI 2000
STO 0001  ; Store 2000 in memory[0001]
LDI 2000
ADD 0001  ; ACC = 2000 + 2000 = 4000 (valid 16-bit)
STO 0002  ; Store 4000 in memory[0002]
LDI 2000
ADDI 2000 ; ACC = 2000 + 2000 = 4000
CMP 0002  ; Compare with memory[0002]
JNE fail
LDI 1
OUT 0000  ; Pass

; ---------------------------------------------------------------------------------------- ;
; TEST 3: SUB and SUBI                                                                     ;
; ---------------------------------------------------------------------------------------- ;

LDI 3
OUT 0001  ; Test step = 3
LDI 4000
STO 0003  ; Store 4000 in memory[0003]
LDI 4000
SUB 0003  ; ACC = 4000 - 4000 = 0
STO 0004  ; Store 0 in memory[0004]
LDI 0
CMP 0004  ; Compare ACC (0) with memory[0004]
JNE fail
LDI 3000
SUBI 3000 ; ACC = 0
CMP 0004  ; Compare with memory[0004] (0)
JNE fail
LDI 1
OUT 0000  ; Pass

; ---------------------------------------------------------------------------------------- ;
; TEST 4: JUMP, NOP                                                                        ;
; ---------------------------------------------------------------------------------------- ;

LDI 4
OUT 0001  ; Test step = 4
JUMP skip
fail:     ; Unreachable if JUMP works
  LDI 0
  OUT 0000
  HLT 0
skip:
NOP       ; Verify no side effects
LDI 1
OUT 0000  ; Pass

; ---------------------------------------------------------------------------------------- ;
; TEST 5: CMP, JNE, JL, JG                                                                 ;
; ---------------------------------------------------------------------------------------- ;

LDI 5
OUT 0001  ; Test step = 5
LDI 100
STO 0005  ; memory[0005] = 100
LDI 50
CMP 0005  ; Compare 100 > 50
JG  greater  ; Jump if ACC < memory[0005]
JUMP fail
greater:
LDI 200
CMP 0005  ; Compare 100 < 200
JL  less
JUMP fail
less:
LDI 1
OUT 0000  ; Pass

; ---------------------------------------------------------------------------------------- ;
; TEST 6: IN, HLT                                                                          ;
; ---------------------------------------------------------------------------------------- ;

LDI 6
OUT 0001  ; Test step = 6
IN 0000   ; Read input from port 0000 (simulate X=4095)
STO 0006  ; Store input
LD 0006   ; Load input back
CMP 0006  ; Compare with memory[0000] (4095)
JNE fail
LDI 1
OUT 0000  ; Pass
HLT 0     ; Halt

; ======================================================================================== ;
; FAIL HANDLER                                                                             ;
; ======================================================================================== ;

fail:
  LDI 0
  OUT 0000  ; Signal failure
  HLT 0

; ======================================================================================== ;
