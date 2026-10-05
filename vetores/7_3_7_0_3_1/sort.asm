# Programa sort/swap gerado pelo gerar_binario.py (mips-assembler)
# Vetor de entrada: {7, 3, 7, 0, 3, 1}  ->  saida esperada: {0, 1, 3, 3, 7, 7}
# Mesma logica de asm/sort.asm, so muda a inicializacao do vetor.

addi $a1, $0, 6
addi $a0, $0, 0
addi $t0, $0, 7
sw   $t0, 0($a0)
addi $t0, $0, 3
sw   $t0, 4($a0)
addi $t0, $0, 7
sw   $t0, 8($a0)
addi $t0, $0, 0
sw   $t0, 12($a0)
addi $t0, $0, 3
sw   $t0, 16($a0)
addi $t0, $0, 1
sw   $t0, 20($a0)
sort:
        addi $s0, $0, 0
for1tst:
        slt  $t0, $s0, $a1
        beq  $t0, $0, exit1
        addi $s1, $s0, -1
for2tst:
        slt  $t0, $s1, $0
        bne  $t0, $0, exit2
        sll  $t1, $s1, 2
        add  $t2, $a0, $t1
        lw   $t3, 0($t2)
        lw   $t4, 4($t2)
        slt  $t0, $t4, $t3
        beq  $t0, $0, exit2
        sw   $t4, 0($t2)
        sw   $t3, 4($t2)
        addi $s1, $s1, -1
        j    for2tst
exit2:
        addi $s0, $s0, 1
        j    for1tst
exit1:
done:
        j    done
