# mips-asm2bin

Ferramenta de apoio ao projeto de processador MIPS com pipeline
(disciplina de Arquitetura de Sistemas Digitais e Laboratório): gera
o código de máquina em **binário puro**, pronto para a memória de
instruções do processador (`$readmemb`), a partir dos valores de um
vetor informados diretamente no terminal — sem precisar editar
assembly à mão.

Complementa (sem alterar) o repositório principal do processador
(`mips_pipeline`), que continua sendo a fonte oficial do assembly
(`asm/sort.asm`) e do montador original (`tb/assemble_sort.py`).

## Sobre o projeto MIPS

O processador em questão é um MIPS com pipeline de 5 estágios (IF,
ID, EX, MEM, WB), implementado em Verilog, com tratamento de perigos
de dados (forwarding), controle (branch resolvido em ID, com
stall/flush) e estrutural, desenvolvido para a disciplina de
Arquitetura de Sistemas Digitais e Laboratório. Ele é validado
executando um programa de ordenação (sort/swap, com `swap()` inline
no laço de `sort()`) e, ao final, embarcado numa placa FPGA
DE10-Lite, que exibe o vetor já ordenado nos displays de 7 segmentos.

A memória de instruções do processador é carregada via `$readmemb`, a
partir de um arquivo de texto com uma palavra de 32 bits em binário
puro por linha — é exatamente esse arquivo que esta ferramenta gera.

## Status

**Implementado e validado.** Não é trabalho futuro: o script já pede
os valores do vetor e já devolve o `.bin` pronto para uso. O `.bin`
gerado para o vetor de teste original `{8, 3, 7, 1, 9, 4}` foi
comparado byte a byte com o `tb/sort_program.bin` oficial do projeto
(já validado pelos testbenches) — resultado idêntico, instrução por
instrução.

Detalhes completos de motivação, funcionamento interno e validação
estão em [`relatorio_gerador_binario.txt`](relatorio_gerador_binario.txt).

## Arquivos

- `sort.asm` — cópia de referência do assembly original do projeto
  (algoritmo de ordenação sort/swap, mapeamento `v->$a0`, `n->$a1`,
  `i->$s0`, `j->$s1`).
- `gerar_binario.py` — a ferramenta: pede os valores do vetor, monta
  o programa equivalente e grava o `.bin`.
- `relatorio_gerador_binario.txt` — relatório técnico completo da
  ferramenta.

## Como usar

```bash
python gerar_binario.py
```

1. Informe os valores do vetor separados por espaço ou vírgula
   (ex.: `8 3 7 1 9 4`).
2. Informe o nome do arquivo de saída, ou aceite o padrão
   (`sort_program.bin`).
3. Copie o `.bin` gerado para a pasta do projeto no Quartus (mesma
   pasta do `.qpf`), substituindo o `sort_program.bin` existente —
   é lá que `de10lite_top.v` aponta `INSTR_INIT_FILE`.
4. Recompile o projeto no Quartus e regrave a placa. Não é preciso
   alterar nenhum arquivo `.v`.

## Requisitos

- Python 3.x (sem dependências externas).

## Trabalho futuro (ideias, não implementadas)

- Copiar o `.bin` automaticamente para a pasta do projeto Quartus,
  recebendo o caminho como parâmetro do script (hoje esse passo é
  manual).
- Generalizar o montador para aceitar um programa assembly qualquer
  (hoje ele monta especificamente o programa sort/swap com o vetor
  parametrizado, não um `.asm` arbitrário).
