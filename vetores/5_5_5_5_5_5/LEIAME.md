# Vetor {5, 5, 5, 5, 5, 5}

Gerado com o `gerar_binario.py` do
[`mips-assembler`](https://github.com/samymallmann/mips-assembler).
Caso de teste: **todos iguais: nenhuma troca (slt estrito)**.

| | v[0] | v[1] | v[2] | v[3] | v[4] | v[5] |
|---|---|---|---|---|---|---|
| Entrada | 5 | 5 | 5 | 5 | 5 | 5 |
| Saída esperada | 5 | 5 | 5 | 5 | 5 | 5 |

Na placa: `HEX5 HEX4 HEX3 HEX2 HEX1 HEX0` = `5 5 5 5 5 5`.

Validado no Icarus Verilog (testbenches `tb_sort_program_monociclo` e
`tb_de10lite_top_monociclo` apontados para este `.bin`): vetor ordenado
corretamente e PC preso no laço `done` (PC = 128).
