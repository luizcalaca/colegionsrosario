#!/usr/bin/env python3
"""
Gera tools/minipdf_fontes.py: larguras dos caracteres das fontes padrão do PDF.

O PDF usa as fontes "base 14" (Helvetica e Times), que o leitor já traz e que
dispensam embutir arquivo de fonte. Para quebrar linhas é preciso saber a largura
de cada caractere, e essas larguras são idênticas às das fontes métricas-compatíveis
Arial (= Helvetica) e Times New Roman (= Times), que vêm com o macOS.

Só é preciso rodar de novo se um dia trocarem as fontes do PDF:

    python3 tools/extrair-metricas-fontes.py

Lê os .ttf (tabelas head, hhea, hmtx e cmap), sem dependências externas.
"""

import os
import struct

PASTA = "/System/Library/Fonts/Supplemental"
FONTES = {
    "Helvetica": "Arial.ttf",
    "Helvetica-Bold": "Arial Bold.ttf",
    "Times-Roman": "Times New Roman.ttf",
    "Times-Bold": "Times New Roman Bold.ttf",
    "Times-Italic": "Times New Roman Italic.ttf",
}
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minipdf_fontes.py")


def tabelas(dados):
    n = struct.unpack(">H", dados[4:6])[0]
    return {
        dados[12 + 16 * i: 16 + 16 * i].decode("latin-1"):
            struct.unpack(">II", dados[20 + 16 * i: 28 + 16 * i])
        for i in range(n)
    }


def cmap_unicode(dados, off):
    """Mapa unicode -> índice de glifo (subtabela formato 4, plataforma 3 ou 0)."""
    n = struct.unpack(">H", dados[off + 2: off + 4])[0]
    escolhida = None
    for i in range(n):
        plat, enc, sub = struct.unpack(">HHI", dados[off + 4 + 8 * i: off + 12 + 8 * i])
        if (plat, enc) in ((3, 1), (0, 3), (0, 4)):
            escolhida = off + sub
            if plat == 3:
                break
    if escolhida is None:
        raise SystemExit("cmap unicode não encontrada")
    o = escolhida
    if struct.unpack(">H", dados[o:o + 2])[0] != 4:
        raise SystemExit("cmap não está no formato 4")
    segx2 = struct.unpack(">H", dados[o + 6:o + 8])[0]
    seg = segx2 // 2
    fim = struct.unpack(f">{seg}H", dados[o + 14: o + 14 + segx2])
    ini = struct.unpack(f">{seg}H", dados[o + 16 + segx2: o + 16 + 2 * segx2])
    delta = struct.unpack(f">{seg}h", dados[o + 16 + 2 * segx2: o + 16 + 3 * segx2])
    pos_ro = o + 16 + 3 * segx2
    ro = struct.unpack(f">{seg}H", dados[pos_ro: pos_ro + segx2])

    def glifo(cp):
        for s in range(seg):
            if ini[s] <= cp <= fim[s]:
                if ro[s] == 0:
                    return (cp + delta[s]) & 0xFFFF
                p = pos_ro + 2 * s + ro[s] + 2 * (cp - ini[s])
                g = struct.unpack(">H", dados[p:p + 2])[0]
                return (g + delta[s]) & 0xFFFF if g else 0
        return 0
    return glifo


def larguras(caminho):
    dados = open(caminho, "rb").read()
    t = tabelas(dados)
    upem = struct.unpack(">H", dados[t["head"][0] + 18: t["head"][0] + 20])[0]
    n_h = struct.unpack(">H", dados[t["hhea"][0] + 34: t["hhea"][0] + 36])[0]
    hmtx = t["hmtx"][0]
    glifo = cmap_unicode(dados, t["cmap"][0])

    def adv(g):
        g = min(g, n_h - 1)
        return struct.unpack(">H", dados[hmtx + 4 * g: hmtx + 4 * g + 2])[0]

    saida = []
    for cod in range(32, 256):
        ch = bytes([cod]).decode("cp1252", errors="replace")
        g = glifo(ord(ch)) if ch != "�" else 0
        saida.append(round(adv(g) * 1000 / upem) if g else 0)
    return saida


def main():
    linhas = [
        '"""Larguras (em milésimos de em) dos códigos 32..255 de cada fonte, em cp1252.',
        "",
        "ARQUIVO GERADO por tools/extrair-metricas-fontes.py — não edite à mão.",
        '"""',
        "",
        "LARGURAS = {",
    ]
    for nome, arq in FONTES.items():
        lg = larguras(os.path.join(PASTA, arq))
        linhas.append(f'    "{nome}": [')
        for i in range(0, len(lg), 16):
            linhas.append("        " + ", ".join(str(x) for x in lg[i:i + 16]) + ",")
        linhas.append("    ],")
    linhas.append("}")
    with open(SAIDA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")
    print("gravado", SAIDA)


if __name__ == "__main__":
    main()
