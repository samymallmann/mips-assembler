# Vetores testados

Um vetor por pasta (nome = valores de entrada). Cada pasta tem:

- `sort_program.bin` — binário gerado pelo [`gerar_binario.py`](../gerar_binario.py);
- `sort.asm` — assembly correspondente;
- `LEIAME.md` — entrada e saída esperada.

| Pasta | Entrada | Saída esperada |
|---|---|---|
| [`8_3_7_1_9_4/`](8_3_7_1_9_4/) | 8 3 7 1 9 4 | 1 3 4 7 8 9 (enunciado, conferido na placa) |
| [`5_2_9_0_6_1/`](5_2_9_0_6_1/) | 5 2 9 0 6 1 | 0 1 2 5 6 9 |
| [`7_3_7_0_3_1/`](7_3_7_0_3_1/) | 7 3 7 0 3 1 | 0 1 3 3 7 7 (valores repetidos) |
| [`9_8_7_6_5_4/`](9_8_7_6_5_4/) | 9 8 7 6 5 4 | 4 5 6 7 8 9 (pior caso: decrescente) |
| [`1_2_3_4_5_6/`](1_2_3_4_5_6/) | 1 2 3 4 5 6 | 1 2 3 4 5 6 (melhor caso: já ordenado) |
| [`5_5_5_5_5_5/`](5_5_5_5_5_5/) | 5 5 5 5 5 5 | 5 5 5 5 5 5 (todos iguais) |
| [`2_6_4_8_0_3/`](2_6_4_8_0_3/) | 2 6 4 8 0 3 | 0 2 3 4 6 8 (conferido na placa) |
| [`6_0_9_3_5_2/`](6_0_9_3_5_2/) | 6 0 9 3 5 2 | 0 2 3 5 6 9 (conferido na placa) |

Todos validados no Icarus Verilog com o processador do
[`mips-monociclo`](https://github.com/samymallmann/mips-monociclo), onde as
mesmas pastas ficam em `programas/`.

## Usar na placa

No `mips-monociclo`, a placa carrega sempre `programas/ao_vivo/sort_program.bin`:
cole ali o `.bin` do vetor (substituindo), compile (Ctrl+L) e grave o
`output_files/mips_monociclo.sof` no Programmer.
