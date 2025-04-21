; CALCULAR: Y = 4X + 3

; Carrega X

IN  0000
STO 0000

; Multiplica Y por 4

LDI 0004    ; Multiplicador (4)
STO 0001

LDI 0000    ; Variável acumuladora (inicializa em 0)
STO 0002

LDI 0000    ; Break-point
STO 0003

mult:

    LD   0000  ; Carrega X
    ADD  0002  ; Acumulador += X
		OUT  0001  ; Exibe valor da multiplicação
    STO  0002  ; Armazena de volta no acumulador
    LD   0001  ; Carrega multiplicador
    SUBI 0001  ; Decrementa multiplicador
		OUT  0000  ; Exibe o valor do multiplicador
		STO  0001  ; Armazena de volta no multiplicador
    CMP  0003  ; Compara multiplicador com zero
    JNE  mult  ; Continua loop se multiplicador não for zero

; Adiciona 3 à variável acumuladora (Y = 4X + 3)

LDI 0003
ADD 0002
STO 0002

eop:

    LD   0002
    OUT  0000  ; Exibe o resultado
    HLT  0000  ; Para a execução
