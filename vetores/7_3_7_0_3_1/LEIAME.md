# Vetor {7, 3, 7, 0, 3, 1}

Gerado com o `gerar_binario.py` do
[`mips-assembler`](https://github.com/samymallmann/mips-assembler).
Testa **valores repetidos** (dois 3 e dois 7): como a comparação é `slt`
(estritamente menor), elementos iguais não são trocados.

| | v[0] | v[1] | v[2] | v[3] | v[4] | v[5] |
|---|---|---|---|---|---|---|
| Entrada | 7 | 3 | 7 | 0 | 3 | 1 |
| Saída esperada | 0 | 1 | 3 | 3 | 7 | 7 |

Na placa: `HEX5 HEX4 HEX3 HEX2 HEX1 HEX0` = `0 1 3 3 7 7`.

Validado no Icarus Verilog (testbenches `tb_sort_program_monociclo` e
`tb_de10lite_top_monociclo` apontados para este `.bin`): vetor ordenado
corretamente e PC preso no laço `done` (PC = 128).
