# Traducao manual do sort/swap do enunciado pra assembly MIPS.
# Registradores: v->$a0, n->$a1, i->$s0, j->$s1 (como pedido).
#
# swap() foi colocada inline dentro do loop de sort() em vez de virar uma
# chamada de funcao com jal/jr - o processador nao implementa $ra/pilha,
# entao inlining evita precisar disso so' pra essa funcao pequena.
#
# Codigo original (do enunciado):
#   void sort (int v[], int n) {
#       int i, j;
#       for (i = 0; i < n; i += 1)
#           for (j = i - 1; j >= 0 && v[j] > v[j+1]; j -= 1)
#               swap(v, j);
#   }
#   void swap (int v[], int k) {
#       int temp;
#       temp = v[k]; v[k] = v[k+1]; v[k+1] = temp;
#   }

# inicializa n, base de v, e os valores do vetor de teste {8,3,7,1,9,4}
        addi $a1, $0,  6        # n = 6
        addi $a0, $0,  0        # v = endereco base 0 na memoria de dados

        addi $t0, $0,  8
        sw   $t0, 0($a0)        # v[0] = 8
        addi $t0, $0,  3
        sw   $t0, 4($a0)        # v[1] = 3
        addi $t0, $0,  7
        sw   $t0, 8($a0)        # v[2] = 7
        addi $t0, $0,  1
        sw   $t0, 12($a0)       # v[3] = 1
        addi $t0, $0,  9
        sw   $t0, 16($a0)       # v[4] = 9
        addi $t0, $0,  4
        sw   $t0, 20($a0)       # v[5] = 4

# --- sort(v, n) --------------------------------------------------------
sort:
        addi $s0, $0, 0         # i = 0

for1tst:
        slt  $t0, $s0, $a1      # t0 = (i < n)
        beq  $t0, $0, exit1     # if (!(i < n)) goto exit1

        addi $s1, $s0, -1       # j = i - 1

for2tst:
        slt  $t0, $s1, $0       # t0 = (j < 0)
        bne  $t0, $0, exit2     # if (j < 0) goto exit2

        sll  $t1, $s1, 2        # t1 = j * 4
        add  $t2, $a0, $t1      # t2 = &v[j]
        lw   $t3, 0($t2)        # t3 = v[j]
        lw   $t4, 4($t2)        # t4 = v[j+1]

        slt  $t0, $t4, $t3      # t0 = (v[j+1] < v[j])  <=>  v[j] > v[j+1]
        beq  $t0, $0, exit2     # if (!(v[j] > v[j+1])) goto exit2

        # --- swap(v, j) inline: troca v[j] e v[j+1] ---
        sw   $t4, 0($t2)        # v[j]   = v[j+1]
        sw   $t3, 4($t2)        # v[j+1] = v[j]

        addi $s1, $s1, -1       # j -= 1
        j    for2tst

exit2:
        addi $s0, $s0, 1        # i += 1
        j    for1tst

exit1:
done:
        j    done                # fim do programa: laco infinito (halt)
