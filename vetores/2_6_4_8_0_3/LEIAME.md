# Vetor {2, 6, 4, 8, 0, 3}

Gerado com o `gerar_binario.py` do
[`mips-assembler`](https://github.com/samymallmann/mips-assembler) e testado
pelo fluxo da pasta `ao_vivo/` (colar o `.bin`, compilar, gravar).

| | v[0] | v[1] | v[2] | v[3] | v[4] | v[5] |
|---|---|---|---|---|---|---|
| Entrada | 2 | 6 | 4 | 8 | 0 | 3 |
| Saída esperada | 0 | 2 | 3 | 4 | 6 | 8 |

Na placa: `HEX5 HEX4 HEX3 HEX2 HEX1 HEX0` = `0 2 3 4 6 8`.

Validado no Icarus Verilog e **conferido na DE10-Lite** (displays mostraram
`0 2 3 4 6 8`).
