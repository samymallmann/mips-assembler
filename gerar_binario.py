#!/usr/bin/env python3
"""
Gerador de binario para o programa MIPS de ordenacao (sort/swap).

Pede ao usuario os valores do vetor, monta o assembly (mesma logica de
sort.asm nesta pasta: v->$a0, n->$a1, i->$s0, j->$s1, swap inline) com
esses valores e grava um arquivo .bin de 32 bits por linha, no formato
lido pelo $readmemb do Verilog (compativel com o mips_pipeline).
"""
import re

REGS = {
    "$0": 0, "$zero": 0,
    "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11, "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19,
}

R_FUNCT = {"add": 0x20, "sub": 0x22, "and": 0x24, "or": 0x25, "slt": 0x2A}
I_OPC   = {"addi": 0x08, "lw": 0x23, "sw": 0x2B, "beq": 0x04, "bne": 0x05}
J_OPC   = {"j": 0x02}


def reg(tok):
    return REGS[tok.strip().rstrip(',')]


def parse_line(line):
    line = line.split('#', 1)[0].strip()
    if not line:
        return None, None
    label = None
    m = re.match(r'^(\w+):\s*(.*)$', line)
    if m:
        label = m.group(1)
        line = m.group(2).strip()
    if not line:
        return label, None
    parts = line.split(None, 1)
    mnemonic = parts[0]
    operands = parts[1] if len(parts) > 1 else ""
    return label, (mnemonic, operands)


def montar_texto_assembly(valores):
    """Monta o texto assembly (inicializacao do vetor + sort/swap) para os valores dados."""
    n = len(valores)
    linhas = [
        f"addi $a1, $0, {n}",   # n = tamanho do vetor
        "addi $a0, $0, 0",      # v = endereco base 0 na memoria de dados
    ]
    for i, v in enumerate(valores):
        linhas.append(f"addi $t0, $0, {v}")
        linhas.append(f"sw   $t0, {i * 4}($a0)")

    linhas += [
        "sort:",
        "        addi $s0, $0, 0",
        "for1tst:",
        "        slt  $t0, $s0, $a1",
        "        beq  $t0, $0, exit1",
        "        addi $s1, $s0, -1",
        "for2tst:",
        "        slt  $t0, $s1, $0",
        "        bne  $t0, $0, exit2",
        "        sll  $t1, $s1, 2",
        "        add  $t2, $a0, $t1",
        "        lw   $t3, 0($t2)",
        "        lw   $t4, 4($t2)",
        "        slt  $t0, $t4, $t3",
        "        beq  $t0, $0, exit2",
        "        sw   $t4, 0($t2)",
        "        sw   $t3, 4($t2)",
        "        addi $s1, $s1, -1",
        "        j    for2tst",
        "exit2:",
        "        addi $s0, $s0, 1",
        "        j    for1tst",
        "exit1:",
        "done:",
        "        j    done",
    ]
    return "\n".join(linhas) + "\n"


def montar(texto_asm):
    """Duas passadas: monta a lista de instrucoes + tabela de rotulos, depois codifica cada uma."""
    instrs = []
    labels = {}
    for raw in texto_asm.splitlines():
        label, instr = parse_line(raw)
        if label is not None:
            labels[label] = len(instrs)  # endereco = indice da PROXIMA instrucao
        if instr is not None:
            instrs.append(instr)

    machine_code = []
    for idx, (mnemonic, operands) in enumerate(instrs):
        ops = [o.strip() for o in operands.split(',')] if operands else []

        if mnemonic in R_FUNCT:
            rd, rs, rt = reg(ops[0]), reg(ops[1]), reg(ops[2])
            word = (0 << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (0 << 6) | R_FUNCT[mnemonic]

        elif mnemonic == "sll":
            rd, rt, shamt = reg(ops[0]), reg(ops[1]), int(ops[2])
            word = (0 << 26) | (0 << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | 0x00

        elif mnemonic == "addi":
            rt, rs, imm = reg(ops[0]), reg(ops[1]), int(ops[2])
            word = (I_OPC[mnemonic] << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)

        elif mnemonic in ("lw", "sw"):
            rt = reg(ops[0])
            m = re.match(r'^(-?\d+)\((\$\w+)\)$', ops[1])
            imm, rs = int(m.group(1)), reg(m.group(2))
            word = (I_OPC[mnemonic] << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)

        elif mnemonic in ("beq", "bne"):
            rs, rt, target_label = reg(ops[0]), reg(ops[1]), ops[2]
            target = labels[target_label]
            offset = target - (idx + 1)
            word = (I_OPC[mnemonic] << 26) | (rs << 21) | (rt << 16) | (offset & 0xFFFF)

        elif mnemonic in J_OPC:
            target_label = ops[0]
            target = labels[target_label]
            word = (J_OPC[mnemonic] << 26) | (target & 0x3FFFFFF)

        else:
            raise ValueError("Instrucao nao suportada pelo montador: %s" % mnemonic)

        machine_code.append(word & 0xFFFFFFFF)

    return machine_code, labels


def ler_vetor():
    while True:
        entrada = input("Digite os valores do vetor separados por espaco ou virgula: ")
        partes = entrada.replace(',', ' ').split()
        if not partes:
            print("Digite pelo menos um valor.")
            continue
        try:
            valores = [int(p) for p in partes]
        except ValueError:
            print("Valores invalidos, use apenas numeros inteiros.")
            continue
        fora_do_intervalo = [v for v in valores if not (-32768 <= v <= 32767)]
        if fora_do_intervalo:
            print(f"Valores fora do intervalo de imm de 16 bits (-32768 a 32767): {fora_do_intervalo}")
            continue
        return valores


def main():
    print("=== Gerador de binario MIPS - sort/swap ===")
    valores = ler_vetor()

    texto_asm = montar_texto_assembly(valores)
    machine_code, labels = montar(texto_asm)

    nome_saida = input("Nome do arquivo de saida [sort_program.bin]: ").strip() or "sort_program.bin"

    with open(nome_saida, "w", newline="\n") as f:
        for word in machine_code:
            f.write(format(word, "032b") + "\n")

    print(f"\nVetor de entrada ({len(valores)} elementos): {valores}")
    print(f"Gravado '{nome_saida}' com {len(machine_code)} instrucoes ({len(labels)} rotulos)")
    for lbl, addr in labels.items():
        print("  %-10s -> palavra %2d (byte %3d)" % (lbl, addr, addr * 4))


if __name__ == "__main__":
    main()
