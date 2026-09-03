# mips-asm2bin

Do algoritmo em C do enunciado até o código de máquina em binário
executado pelo processador — passo a passo, e depois automatizado em
Python.

Este repositório documenta e automatiza especificamente a etapa de
**tradução do algoritmo de ordenação para assembly MIPS e a montagem
desse assembly em binário puro** (o formato lido por `$readmemb` na
memória de instruções). É complementar ao repositório do processador
em si — [`mips-pipeline`](https://github.com/samymallmann/mips-pipeline) —,
onde esse mesmo assembly e binário já estão implementados e validados
(pasta `mips_pipeline/asm/` e `mips_pipeline/tb/`). Aqui o foco é
explicar **como** se chega do C ao binário, e mostrar a ferramenta que
automatiza essa conversão pra qualquer vetor de teste.

## Sumário

1. [O algoritmo em C (do enunciado)](#1-o-algoritmo-em-c-do-enunciado)
2. [Tradução para assembly MIPS](#2-tradução-para-assembly-mips)
3. [Do assembly ao binário: como a montagem funciona](#3-do-assembly-ao-binário-como-a-montagem-funciona)
4. [Automatizando com Python: `gerar_binario.py`](#4-automatizando-com-python-gerar_binariopy)
5. [Validação](#5-validação)
6. [Arquivos deste repositório](#6-arquivos-deste-repositório)
7. [Como usar](#7-como-usar)


## 1) O algoritmo em C (do enunciado)

O enunciado do projeto pede que o processador seja testado executando
o seguinte algoritmo de ordenação por inserção, com `swap` como uma
função auxiliar de troca:

```c
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
```

(reproduzido em [`sort.c`](sort.c))

O enunciado também fixa o mapeamento de variáveis para registradores
que a tradução precisa respeitar: `v` → `$a0`, `n` → `$a1`, `i` →
`$s0`, `j` → `$s1`.


## 2) Tradução para assembly MIPS

A tradução manual está em [`sort.asm`](sort.asm). Duas decisões de
projeto vale destacar:

- **`swap()` foi colocada inline** dentro do laço de `sort()`, em vez
  de virar uma chamada de função com `jal`/`jr`. O processador que
  executa este programa não implementa `$ra`/pilha de chamadas (fora
  do escopo do conjunto de instruções necessário pra este programa de
  teste), então inlining evita precisar disso só para essa função
  pequena.
- O laço duplo do C vira dois laços em assembly com rótulos
  (`for1tst`/`for2tst`), e as condições dos `for` (`i < n`,
  `j >= 0 && v[j] > v[j+1]`) viram testes com `slt`/`beq`/`bne` no
  início de cada laço — o padrão clássico de tradução de `for` para
  MIPS.

Assembly completo (33 instruções, incluindo a inicialização do vetor
de teste `{8, 3, 7, 1, 9, 4}` usada como exemplo):

```asm
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
        sw   $t4, 0($t2)        # v[j]   = v[j+1]
        sw   $t3, 4($t2)        # v[j+1] = v[j]
        addi $s1, $s1, -1       # j -= 1
        j    for2tst
exit2:
        addi $s0, $s0, 1        # i += 1
        j    for1tst
exit1:
done:
        j    done               # fim do programa: laco infinito (halt)
```


## 3) Do assembly ao binário: como a montagem funciona

O processador implementa um subconjunto pequeno e fixo do MIPS —
`add`, `sub`, `and`, `or`, `slt`, `sll` (tipo-R), `addi`, `lw`, `sw`,
`beq`, `bne` (tipo-I) e `j` (tipo-J) — cada um decodificado por
`opcode`/`funct` em `control_unit.v`/`alu_control.v` do processador.
Montar assembly em binário é, essencialmente, transformar cada linha
de mnemônico + operandos numa palavra de 32 bits que respeite esses
três formatos:

```
Tipo-R:  opcode(6) | rs(5) | rt(5) | rd(5) | shamt(5) | funct(6)
Tipo-I:  opcode(6) | rs(5) | rt(5) | immediate(16)
Tipo-J:  opcode(6) | address(26)
```

### Opcodes e funct usados

| Instrução | Tipo | opcode (bin) | funct (bin) |
|---|---|---|---|
| add  | R | 000000 | 100000 |
| sub  | R | 000000 | 100010 |
| and  | R | 000000 | 100100 |
| or   | R | 000000 | 100101 |
| slt  | R | 000000 | 101010 |
| sll  | R | 000000 | 000000 (usa o campo `shamt`, não `rs`) |
| addi | I | 001000 | — |
| lw   | I | 100011 | — |
| sw   | I | 101011 | — |
| beq  | I | 000100 | — |
| bne  | I | 000101 | — |
| j    | J | 000010 | — |

### Registradores usados neste programa

| Registrador | Número | Binário (5 bits) |
|---|---|---|
| `$0`  | 0  | 00000 |
| `$a0` | 4  | 00100 |
| `$a1` | 5  | 00101 |
| `$t0`–`$t4` | 8–12 | 01000–01100 |
| `$s0` | 16 | 10000 |
| `$s1` | 17 | 10001 |

### Rótulos: de nome simbólico a endereço numérico

Um montador de duas passadas resolve os rótulos:

- **1ª passada**: percorre o assembly contando instruções (ignorando
  comentários e linhas de rótulo puro) e anota em que **índice**
  (posição da instrução, começando em 0) cada rótulo aparece. Por
  exemplo, no assembly acima `sort` fica no índice 14, `for1tst` no
  15, `exit1`/`done` no 32.
- **2ª passada**: codifica cada instrução. Para `beq`/`bne`, o campo
  de 16 bits é um **deslocamento relativo em instruções** — não o
  endereço absoluto do rótulo — calculado como:

  ```
  offset = indice_do_rotulo_destino - (indice_da_instrucao_atual + 1)
  ```

  (o "+1" existe porque o processador soma o offset ao PC **já
  incrementado** para a próxima instrução — ver `mips_pipeline_top.v`:
  `branch_target = pc_plus4 + (sign_ext_imm << 2)`). Para `j`, o campo
  de 26 bits é o índice absoluto do rótulo (`jump_target` monta o
  endereço final concatenando os 4 bits altos do PC atual com esse
  índice e dois zeros à direita, já que endereços são múltiplos de 4).

### Dois exemplos montados à mão

**`addi $a1, $0, 6`** (primeira instrução do programa, índice 0):

```
opcode(addi) = 001000
rs ($0)      = 00000
rt ($a1)     = 00101
immediate(6) = 0000000000000110
                                   ---------------------------------
palavra final:                    00100000000001010000000000000110
```

**`beq $t0, $0, exit1`** (índice 16; `exit1` está no índice 32, então
`offset = 32 - (16 + 1) = 15`):

```
opcode(beq) = 000100
rs ($t0)    = 01000
rt ($0)     = 00000
immediate(15) = 0000000000001111
                                   ---------------------------------
palavra final:                    00010001000000000000000000001111
```

### Resultado: as 33 instruções em binário

Tabela completa (índice, endereço em bytes, instrução, palavra de 32
bits), pro vetor de teste original `{8, 3, 7, 1, 9, 4}`:

```
idx  end.  instrucao                       codigo binario (32 bits)
---  ----  ------------------------------  --------------------------------
 0     0  addi $a1, $0, 6                 00100000000001010000000000000110
 1     4  addi $a0, $0, 0                 00100000000001000000000000000000
 2     8  addi $t0, $0, 8                 00100000000010000000000000001000
 3    12  sw   $t0, 0($a0)                10101100100010000000000000000000
 4    16  addi $t0, $0, 3                 00100000000010000000000000000011
 5    20  sw   $t0, 4($a0)                10101100100010000000000000000100
 6    24  addi $t0, $0, 7                 00100000000010000000000000000111
 7    28  sw   $t0, 8($a0)                10101100100010000000000000001000
 8    32  addi $t0, $0, 1                 00100000000010000000000000000001
 9    36  sw   $t0, 12($a0)               10101100100010000000000000001100
10    40  addi $t0, $0, 9                 00100000000010000000000000001001
11    44  sw   $t0, 16($a0)               10101100100010000000000000010000
12    48  addi $t0, $0, 4                 00100000000010000000000000000100
13    52  sw   $t0, 20($a0)               10101100100010000000000000010100
14    56  sort:    addi $s0, $0, 0        00100000000100000000000000000000
15    60  for1tst: slt  $t0, $s0, $a1     00000010000001010100000000101010
16    64           beq  $t0, $0, exit1    00010001000000000000000000001111
17    68           addi $s1, $s0, -1      00100010000100011111111111111111
18    72  for2tst: slt  $t0, $s1, $0      00000010001000000100000000101010
19    76           bne  $t0, $0, exit2    00010101000000000000000000001010
20    80           sll  $t1, $s1, 2       00000000000100010100100010000000
21    84           add  $t2, $a0, $t1     00000000100010010101000000100000
22    88           lw   $t3, 0($t2)       10001101010010110000000000000000
23    92           lw   $t4, 4($t2)       10001101010011000000000000000100
24    96           slt  $t0, $t4, $t3     00000001100010110100000000101010
25   100           beq  $t0, $0, exit2    00010001000000000000000000000100
26   104           sw   $t4, 0($t2)       10101101010011000000000000000000
27   108           sw   $t3, 4($t2)       10101101010010110000000000000100
28   112           addi $s1, $s1, -1      00100010001100011111111111111111
29   116           j    for2tst           00001000000000000000000000010010
30   120  exit2:   addi $s0, $s0, 1       00100010000100000000000000000001
31   124           j    for1tst           00001000000000000000000000001111
32   128  exit1:/done: j done             00001000000000000000000000100000
```

O arquivo `.bin` final é exatamente essa última coluna, uma palavra
por linha, sem cabeçalho — o formato puro que `$readmemb` espera.


## 4) Automatizando com Python: `gerar_binario.py`

Fazer esse processo à mão (como nos exemplos acima) funciona, mas
escala mal: para testar o processador com **outro vetor**, seria
preciso reescrever manualmente cada `addi`/`sw` de inicialização,
recalcular o `n`, remontar tudo e recontar rótulos — repetitivo e
fácil de errar (um endereço de `sw` errado, um offset de branch
errado). Esse esforço extra não foi pedido pelo enunciado, mas resolve
um problema real de continuidade do projeto.

`gerar_binario.py` resolve isso: pede os valores do vetor no terminal
e devolve o `.bin` pronto, aplicando exatamente as regras da seção 3
acima, para um vetor de qualquer tamanho — não só os 6 elementos do
exemplo.

Como funciona, por dentro:

1. **Monta o assembly equivalente** ao de `sort.asm`, mas gerando
   dinamicamente uma instrução `addi`/`sw` para cada valor do vetor
   informado (em vez dos 6 pares fixos), com `n` = quantidade de
   valores.
2. **Roda o mesmo montador de duas passadas** descrito na seção 3:
   primeiro resolve os rótulos (posição de `sort`, `for1tst`,
   `for2tst`, `exit2`, `exit1`, `done`), depois codifica cada
   instrução em 32 bits — mesmos opcodes, mesmo funct, mesmo cálculo
   de offset de branch e endereço de jump.
3. **Grava o `.bin`** — uma palavra de 32 bits em binário por linha,
   com fim de linha `\n` forçado explicitamente (o Python no Windows
   grava `\r\n` por padrão em modo texto; o `$readmemb` espera o
   mesmo formato simples usado pelo restante do projeto).

Suporta exatamente o mesmo subconjunto de instruções da tabela da
seção 3 — nada além do que o processador decodifica.


## 5) Validação

- **Byte a byte**: o `.bin` gerado pela ferramenta para o vetor
  original `{8, 3, 7, 1, 9, 4}` é idêntico, instrução por instrução,
  ao `tb/sort_program.bin` do repositório do processador (já validado
  pelos testbenches de sistema completo, 6/6 checagens).
- **Funcional (simulação do conjunto de instruções)**: um simulador do
  subconjunto MIPS implementado (semântica de opcode/funct e cálculo
  de branch/jump conferidos contra o RTL do processador) executou o
  binário gerado para **9 vetores de teste diferentes** — já ordenado,
  ordem reversa, duplicatas, 1 elemento, 2 elementos, valores
  negativos e um vetor de 10 elementos com sinais mistos. Em todos os
  casos a memória de dados final ficou corretamente ordenada.

Ainda não foi rodada a testbench de verdade do processador
(`tb_sort_program.v`, via Icarus Verilog) com um `.bin` gerado por
esta ferramenta para um vetor diferente do original — isso validaria
também o comportamento do **pipeline** (forwarding/hazard), não só a
codificação das instruções.


## 6) Arquivos deste repositório

- [`sort.c`](sort.c) — o algoritmo original do enunciado, sem
  alterações.
- [`sort.asm`](sort.asm) — tradução manual para assembly MIPS.
- [`gerar_binario.py`](gerar_binario.py) — a ferramenta: pede os
  valores do vetor, monta o programa equivalente e grava o `.bin`.
- [`relatorio_gerador_binario.txt`](relatorio_gerador_binario.txt) —
  relatório técnico da ferramenta (motivação, funcionamento interno,
  validação, fluxo de uso), em formato mais formal.


## 7) Como usar

```bash
python gerar_binario.py
```

1. Informe os valores do vetor separados por espaço ou vírgula
   (ex.: `8 3 7 1 9 4`).
2. Informe o nome do arquivo de saída, ou aceite o padrão
   (`sort_program.bin`).
3. Copie o `.bin` gerado para a pasta do projeto no Quartus (mesma
   pasta do `.qpf`), substituindo o `sort_program.bin` existente — é
   lá que `de10lite_top.v` aponta `INSTR_INIT_FILE`.
4. Recompile o projeto no Quartus e regrave a placa. Não é preciso
   alterar nenhum arquivo `.v`.

Requisitos: Python 3.x, sem dependências externas.
