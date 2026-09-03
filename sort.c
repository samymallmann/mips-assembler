/* Algoritmo de ordenacao do enunciado do projeto (Arquitetura de
 * Sistemas Digitais e Laboratorio - Processador MIPS Pipeline).
 * Reproduzido aqui sem alteracoes, como ponto de partida da traducao
 * pra assembly MIPS em sort.asm. */

void sort(int v[], int n) {
    int i, j;
    for (i = 0; i < n; i += 1) {
        for (j = i - 1; j >= 0 && v[j] > v[j + 1]; j -= 1) {
            swap(v, j);
        }
    }
}

void swap(int v[], int k) {
    int temp;
    temp = v[k];
    v[k] = v[k + 1];
    v[k + 1] = temp;
}
