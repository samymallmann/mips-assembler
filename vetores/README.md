# Vetores testados

Um vetor por pasta (nome = valores de entrada). Cada pasta tem:

- `sort_program.bin` — binário gerado pelo [`gerar_binario.py`](../gerar_binario.py);
- `sort.asm` — assembly correspondente;
- `LEIAME.md` — entrada e saída esperada.

| Pasta | Entrada | Saída esperada |
|---|---|---|
| [`8_3_7_1_9_4/`](8_3_7_1_9_4/) | 8 3 7 1 9 4 | 1 3 4 7 8 9 (enunciado) |
| [`5_2_9_0_6_1/`](5_2_9_0_6_1/) | 5 2 9 0 6 1 | 0 1 2 5 6 9 |
| [`7_3_7_0_3_1/`](7_3_7_0_3_1/) | 7 3 7 0 3 1 | 0 1 3 3 7 7 (valores repetidos) |

Todos validados no Icarus Verilog com o processador do
[`mips-monociclo`](https://github.com/samymallmann/mips-monociclo), onde as
mesmas pastas ficam em `programas/`.

## Usar na placa

Copie a pasta para `programas/` do `mips-monociclo` (se ainda não estiver lá),
aponte `INSTR_INIT_FILE` em `rtl/de10lite_top_monociclo.v` para ela e recompile:

```verilog
parameter INSTR_INIT_FILE = "programas/7_3_7_0_3_1/sort_program.bin",
```
