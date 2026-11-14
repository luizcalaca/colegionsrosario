"""
Escritor mínimo de PDF, só com a biblioteca padrão do Python.

Existe porque o site é gerado por `build.py` sem dependências, e o CI confere que
os arquivos commitados batem byte a byte com o que o build produz. Por isso o
PDF é DETERMINÍSTICO: sem data de criação, sem identificador aleatório e sem
zlib (a saída do zlib varia entre versões da biblioteca). Imagens usam
RunLengthDecode, que o próprio módulo codifica.

O que ele sabe fazer: texto nas fontes padrão (Helvetica e Times, codificação
WinAnsi), retângulos, linhas, polígonos, degradês axiais, imagens PNG (RGB/RGBA,
com transparência) e links.

Coordenadas: origem no canto SUPERIOR esquerdo, em pontos (1 pt = 1/72 pol.),
com y crescendo para baixo — como no layout de uma página web.
"""

import re
import struct
import zlib

from minipdf_fontes import LARGURAS

A4 = (595.28, 841.89)

# nome lógico -> (BaseFont do PDF, chave da tabela de larguras)
FONTES = {
    "sans": ("Helvetica", "Helvetica"),
    "sans-b": ("Helvetica-Bold", "Helvetica-Bold"),
    "sans-i": ("Helvetica-Oblique", "Helvetica"),  # oblíqua tem as mesmas larguras
    "serif": ("Times-Roman", "Times-Roman"),
    "serif-b": ("Times-Bold", "Times-Bold"),
    "serif-i": ("Times-Italic", "Times-Italic"),
}
_NOMES_FONTE = list(FONTES)


# --------------------------------------------------------------------------
# Cores e texto
# --------------------------------------------------------------------------
def hex_rgb(cor):
    cor = cor.lstrip("#")
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))


def misturar(frente, fundo, alfa):
    """Cor `frente` com opacidade `alfa` sobre `fundo` (equivale ao rgba() do CSS)."""
    f, g = hex_rgb(frente), hex_rgb(fundo)
    return "#%02X%02X%02X" % tuple(round(a * alfa + b * (1 - alfa)) for a, b in zip(f, g))


def _cor(cor):
    return " ".join(f"{c / 255:.4f}".rstrip("0").rstrip(".") or "0" for c in hex_rgb(cor))


def _n(x):
    """Número no PDF: casas fixas, para a saída ser idêntica em qualquer máquina."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def codificar(texto):
    return texto.encode("cp1252", errors="replace")


def largura(texto, fonte, tam, espaco=0.0):
    tabela = LARGURAS[FONTES[fonte][1]]
    total = 0
    for b in codificar(texto):
        total += tabela[b - 32] if b >= 32 else 0
    return total * tam / 1000 + espaco * len(texto)


def _literal(texto):
    b = codificar(texto)
    b = b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
    return b"(" + b + b")"


def _utf16_hex(texto):
    return "<FEFF" + texto.encode("utf-16-be").hex().upper() + ">"


# --------------------------------------------------------------------------
# Imagens
# --------------------------------------------------------------------------
def ler_png(caminho):
    """Decodifica um PNG de 8 bits, sem entrelaçamento (RGB ou RGBA) -> (w, h, rgba)."""
    with open(caminho, "rb") as fh:
        dados = fh.read()
    if dados[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{caminho} não é um PNG")
    pos, idat, ihdr = 8, [], None
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8: pos + 8 + n]
        if tipo == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", corpo)
        elif tipo == b"IDAT":
            idat.append(corpo)
        pos += 12 + n
    w, h, prof, cor_tipo, _, _, entrelacado = ihdr
    if prof != 8 or cor_tipo not in (2, 6) or entrelacado:
        raise ValueError(f"{caminho}: só PNG RGB/RGBA de 8 bits sem entrelaçamento é suportado")
    bpp = 4 if cor_tipo == 6 else 3
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    linhas, ant = [], bytearray(stride)
    for y in range(h):
        filtro = raw[y * (stride + 1)]
        lin = bytearray(raw[y * (stride + 1) + 1: (y + 1) * (stride + 1)])
        if filtro == 1:
            for i in range(bpp, stride):
                lin[i] = (lin[i] + lin[i - bpp]) & 255
        elif filtro == 2:
            for i in range(stride):
                lin[i] = (lin[i] + ant[i]) & 255
        elif filtro == 3:
            for i in range(stride):
                esq = lin[i - bpp] if i >= bpp else 0
                lin[i] = (lin[i] + ((esq + ant[i]) >> 1)) & 255
        elif filtro == 4:
            for i in range(stride):
                a = lin[i - bpp] if i >= bpp else 0
                b = ant[i]
                c = ant[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                lin[i] = (lin[i] + pred) & 255
        elif filtro != 0:
            raise ValueError(f"{caminho}: filtro PNG {filtro} inválido")
        linhas.append(lin)
        ant = lin
    if bpp == 3:
        rgba = bytearray()
        for lin in linhas:
            for i in range(0, stride, 3):
                rgba += lin[i:i + 3] + b"\xff"
    else:
        rgba = b"".join(linhas)
    return w, h, bytes(rgba)


def reduzir(png, fator, fundo=None):
    """Reduz por média de blocos (fator x fator), no espaço pré-multiplicado.

    Com `fundo` (hex), compõe sobre essa cor e devolve só RGB; sem ele, devolve
    (rgb, alfa) separados, para a imagem manter a transparência.
    """
    w, h, rgba = png
    nw, nh = w // fator, h // fator
    bg = hex_rgb(fundo) if fundo else (0, 0, 0)
    n = fator * fator
    rgb, alfa = bytearray(), bytearray()
    for oy in range(nh):
        for ox in range(nw):
            sr = sg = sb = sa = 0
            for dy in range(fator):
                base = ((oy * fator + dy) * w + ox * fator) * 4
                for dx in range(fator):
                    i = base + dx * 4
                    a = rgba[i + 3]
                    sr += rgba[i] * a
                    sg += rgba[i + 1] * a
                    sb += rgba[i + 2] * a
                    sa += a
            A = sa / n  # alfa médio, 0..255
            if fundo:
                k = 1 - A / 255
                rgb += bytes(min(255, round(s / (255 * n) + c * k)) for s, c in zip((sr, sg, sb), bg))
            else:
                if sa:
                    rgb += bytes(min(255, round(s / sa)) for s in (sr, sg, sb))
                else:
                    rgb += b"\0\0\0"
                alfa.append(round(A))
    return nw, nh, bytes(rgb), (None if fundo else bytes(alfa))


def run_length(dados):
    """Codificação RunLengthDecode do PDF (variante do PackBits)."""
    out, i, n = bytearray(), 0, len(dados)
    while i < n:
        j = i + 1
        while j < n and j - i < 128 and dados[j] == dados[i]:
            j += 1
        if j - i >= 2:
            out += bytes((257 - (j - i), dados[i]))
            i = j
        else:
            k = i + 1
            while k < n and k - i < 128 and not (k + 1 < n and dados[k] == dados[k + 1]):
                k += 1
            out.append(k - i - 1)
            out += dados[i:k]
            i = k
    out.append(128)
    return bytes(out)


# --------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------
class Pagina:
    def __init__(self, doc):
        self.doc = doc
        self.largura, self.altura = doc.tamanho
        self.ops = []
        self.links = []  # (x0, y0, x1, y1, url), em coordenadas de layout (topo = 0)

    def _y(self, y):
        return self.altura - y

    def retangulo(self, x, y, w, h, preenchimento=None, traco=None, espessura=0.5, tracejado=None):
        ops = ["q"]
        if preenchimento:
            ops.append(f"{_cor(preenchimento)} rg")
        if traco:
            ops.append(f"{_cor(traco)} RG {_n(espessura)} w")
            if tracejado:
                ops.append(f"[{_n(tracejado[0])} {_n(tracejado[1])}] 0 d")
        op = "B" if preenchimento and traco else ("f" if preenchimento else "S")
        ops.append(f"{_n(x)} {_n(self._y(y + h))} {_n(w)} {_n(h)} re {op}")
        ops.append("Q")
        self.ops.append(" ".join(ops))

    def linha(self, x1, y1, x2, y2, cor, espessura=0.5):
        self.ops.append(
            f"q {_cor(cor)} RG {_n(espessura)} w {_n(x1)} {_n(self._y(y1))} m "
            f"{_n(x2)} {_n(self._y(y2))} l S Q"
        )

    def poligono(self, pontos, cor):
        trajeto = " ".join(
            f"{_n(x)} {_n(self._y(y))} {'m' if i == 0 else 'l'}" for i, (x, y) in enumerate(pontos)
        )
        self.ops.append(f"q {_cor(cor)} rg {trajeto} f Q")

    def degrade(self, x, y, w, h, cor0, cor1, x0, y0, x1, y1):
        """Retângulo com degradê axial de (x0,y0)=cor0 até (x1,y1)=cor1."""
        nome = self.doc._degrade(
            (x0, self._y(y0), x1, self._y(y1)), hex_rgb(cor0), hex_rgb(cor1)
        )
        self.ops.append(
            f"q {_n(x)} {_n(self._y(y + h))} {_n(w)} {_n(h)} re W n /{nome} sh Q"
        )

    def texto(self, x, y, s, fonte, tam, cor, espaco=0.0):
        """Escreve `s` com a linha de base em y. Devolve a largura usada."""
        if not s:
            return 0.0
        idx = _NOMES_FONTE.index(fonte) + 1
        # Tc fica no estado gráfico e atravessa BT/ET: sempre emitido, ou o
        # espaçamento de um texto vaza para os seguintes.
        tc = f"{_n(espaco)} Tc "
        self.ops.append(
            f"BT {_cor(cor)} rg /F{idx} {_n(tam)} Tf {tc}{_n(x)} {_n(self._y(y))} Td "
            f"{_literal(s).decode('latin-1')} Tj ET"
        )
        return largura(s, fonte, tam, espaco)

    def imagem(self, nome, x, y, w, h):
        self.ops.append(
            f"q {_n(w)} 0 0 {_n(h)} {_n(x)} {_n(self._y(y + h))} cm /{nome} Do Q"
        )

    def link(self, x0, y0, x1, y1, url):
        self.links.append((x0, y0, x1, y1, url))


class Documento:
    def __init__(self, titulo, autor, assunto, idioma="pt-BR", tamanho=A4):
        self.titulo, self.autor, self.assunto, self.idioma = titulo, autor, assunto, idioma
        self.tamanho = tamanho
        self.paginas = []
        self._imagens = {}   # nome -> (w, h, rgb, alfa)
        self._degrades = {}  # chave -> nome

    def nova_pagina(self):
        p = Pagina(self)
        self.paginas.append(p)
        return p

    def registrar_imagem(self, nome, w, h, rgb, alfa=None):
        self._imagens[nome] = (w, h, rgb, alfa)
        return nome

    def _degrade(self, coords, c0, c1):
        chave = (tuple(round(c, 2) for c in coords), c0, c1)
        if chave not in self._degrades:
            self._degrades[chave] = f"Sh{len(self._degrades) + 1}"
        return self._degrades[chave]

    # ---- serialização ----
    def salvar(self):
        objs = []  # corpos (bytes); o número do objeto é índice + 1

        def novo(corpo=b""):
            objs.append(corpo)
            return len(objs)

        def stream(dic, dados):
            return (f"<< {dic} /Length {len(dados)} >>\nstream\n").encode("latin-1") + dados + b"\nendstream"

        catalogo = novo()
        arvore = novo()
        info = novo()

        fontes = {}
        for i, nome in enumerate(_NOMES_FONTE, 1):
            fontes[f"F{i}"] = novo(
                f"<< /Type /Font /Subtype /Type1 /BaseFont /{FONTES[nome][0]} "
                f"/Encoding /WinAnsiEncoding >>".encode("latin-1")
            )

        xobjetos = {}
        for nome in sorted(self._imagens):
            w, h, rgb, alfa = self._imagens[nome]
            smask = ""
            if alfa is not None:
                s = novo(stream(
                    f"/Type /XObject /Subtype /Image /Width {w} /Height {h} "
                    f"/ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /RunLengthDecode",
                    run_length(alfa)))
                smask = f" /SMask {s} 0 R"
            xobjetos[nome] = novo(stream(
                f"/Type /XObject /Subtype /Image /Width {w} /Height {h} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /RunLengthDecode{smask}",
                run_length(rgb)))

        degrades = {}
        for (coords, c0, c1), nome in self._degrades.items():
            cs = " ".join(_n(c) for c in coords)
            f0 = " ".join(f"{c / 255:.4f}" for c in c0)
            f1 = " ".join(f"{c / 255:.4f}" for c in c1)
            degrades[nome] = novo(
                (f"<< /ShadingType 2 /ColorSpace /DeviceRGB /Coords [{cs}] /Extend [true true] "
                 f"/Function << /FunctionType 2 /Domain [0 1] /C0 [{f0}] /C1 [{f1}] /N 1 >> >>"
                 ).encode("latin-1"))

        recursos = (
            "<< /Font << " + " ".join(f"/{k} {v} 0 R" for k, v in fontes.items()) + " >>"
            + (" /XObject << " + " ".join(f"/{k} {v} 0 R" for k, v in xobjetos.items()) + " >>" if xobjetos else "")
            + (" /Shading << " + " ".join(f"/{k} {v} 0 R" for k, v in degrades.items()) + " >>" if degrades else "")
            + " >>"
        )

        largura_p, altura_p = self.tamanho
        kids = []
        for pag in self.paginas:
            conteudo = novo(stream("", ("\n".join(pag.ops)).encode("latin-1")))
            anots = []
            for x0, y0, x1, y1, url in pag.links:
                anots.append(novo(
                    (f"<< /Type /Annot /Subtype /Link /Border [0 0 0] "
                     f"/Rect [{_n(x0)} {_n(altura_p - y1)} {_n(x1)} {_n(altura_p - y0)}] "
                     f"/A << /S /URI /URI ({url}) >> >>").encode("latin-1")))
            annots = f" /Annots [{' '.join(f'{a} 0 R' for a in anots)}]" if anots else ""
            kids.append(novo(
                (f"<< /Type /Page /Parent {arvore} 0 R /MediaBox [0 0 {_n(largura_p)} {_n(altura_p)}] "
                 f"/Contents {conteudo} 0 R{annots} >>").encode("latin-1")))

        objs[arvore - 1] = (
            f"<< /Type /Pages /Count {len(kids)} /Kids [{' '.join(f'{k} 0 R' for k in kids)}] "
            f"/Resources {recursos} >>"
        ).encode("latin-1")
        objs[catalogo - 1] = (
            f"<< /Type /Catalog /Pages {arvore} 0 R /Lang ({self.idioma}) "
            f"/ViewerPreferences << /DisplayDocTitle true >> >>"
        ).encode("latin-1")
        objs[info - 1] = (
            f"<< /Title {_utf16_hex(self.titulo)} /Author {_utf16_hex(self.autor)} "
            f"/Subject {_utf16_hex(self.assunto)} /Creator (build.py) /Producer (minipdf) >>"
        ).encode("latin-1")

        saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for i, corpo in enumerate(objs, 1):
            offsets.append(len(saida))
            saida += f"{i} 0 obj\n".encode() + corpo + b"\nendobj\n"
        xref = len(saida)
        saida += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
        for off in offsets:
            saida += f"{off:010d} 00000 n \n".encode()
        saida += (f"trailer\n<< /Size {len(objs) + 1} /Root {catalogo} 0 R /Info {info} 0 R >>\n"
                  f"startxref\n{xref}\n%%EOF\n").encode()
        return bytes(saida)


# --------------------------------------------------------------------------
# Texto corrido com formatação inline (<strong>, <em>, <a href>)
# --------------------------------------------------------------------------
_TAG = re.compile(r"<(/?)([a-zA-Z0-9]+)([^>]*)>")


def _entidades(s):
    import html
    return html.unescape(s)


def analisar_html(trecho):
    """HTML mínimo -> (lista de trechos, lista de imagens).

    Cada trecho é (texto, negrito, italico, url). Tags desconhecidas são ignoradas
    (o texto delas fica), para que editar o conteúdo nunca quebre a geração do PDF.
    As <img> saem separadas: (src, alt).
    """
    runs, imagens = [], []
    neg = ita = 0
    url = None
    pos = 0
    for m in _TAG.finditer(trecho):
        if m.start() > pos:
            runs.append((_entidades(trecho[pos:m.start()]), neg > 0, ita > 0, url))
        fecha, tag, attrs = m.group(1) == "/", m.group(2).lower(), m.group(3)
        if tag in ("strong", "b"):
            neg += -1 if fecha else 1
        elif tag in ("em", "i"):
            ita += -1 if fecha else 1
        elif tag == "a":
            if fecha:
                url = None
            else:
                h = re.search(r'href="([^"]*)"', attrs)
                url = _entidades(h.group(1)) if h else None
        elif tag == "img" and not fecha:
            src = re.search(r'src="([^"]*)"', attrs)
            alt = re.search(r'alt="([^"]*)"', attrs)
            if src:
                imagens.append((src.group(1), _entidades(alt.group(1)) if alt else ""))
        pos = m.end()
    if pos < len(trecho):
        runs.append((_entidades(trecho[pos:]), neg > 0, ita > 0, url))
    return [r for r in runs if r[0]], imagens


def quebrar_linhas(runs, familia, tam, largura_max, cor, cor_link, espaco=0.0):
    """Quebra trechos formatados em linhas de no máximo `largura_max`.

    `familia` é "sans" ou "serif"; `espaco` é o espaçamento entre letras (Tc).
    Devolve linhas; cada linha é uma lista de segmentos
    (texto, fonte, cor, url, largura). Só se quebra em espaços.
    """
    def fonte(neg, ita):
        if neg:
            return f"{familia}-b"
        return f"{familia}-i" if ita else familia

    # átomos: ("esp"|"pal", texto, fonte, cor, url)
    atomos = []
    for texto, neg, ita, url in runs:
        f, c = fonte(neg, ita), (cor_link if url else cor)
        for tok in re.findall(r"\s+|\S+", texto.replace("\n", " ")):
            atomos.append(("esp" if tok.isspace() else "pal", " " if tok.isspace() else tok, f, c, url))

    # agrupa átomos "pal" consecutivos (podem vir de trechos diferentes) em blocos
    blocos, atual = [], []
    for a in atomos:
        if a[0] == "esp":
            if atual:
                blocos.append(atual)
                atual = []
            blocos.append(a)
        else:
            atual.append(a)
    if atual:
        blocos.append(atual)

    def larg(a):
        return largura(a[1], a[2], tam, espaco)

    linhas, linha, usado = [], [], 0.0
    pendente_espaco = None
    for b in blocos:
        if isinstance(b, tuple):  # espaço
            pendente_espaco = b
            continue
        lb = sum(larg(a) for a in b)
        le = larg(pendente_espaco) if (pendente_espaco and linha) else 0
        # tolerância: colunas dimensionadas ao próprio texto não devem quebrar por erro de arredondamento
        if linha and usado + le + lb > largura_max + 0.05:
            linhas.append(linha)
            linha, usado, le, pendente_espaco = [], 0.0, 0, None
        if pendente_espaco and linha:
            linha.append(pendente_espaco)
            usado += le
        linha.extend(b)
        usado += lb
        pendente_espaco = None
    if linha:
        linhas.append(linha)

    # funde átomos vizinhos de mesmo estilo em segmentos
    saida = []
    for lin in linhas:
        segs = []
        for _, texto, f, c, url in lin:
            if segs and segs[-1][1] == f and segs[-1][2] == c and segs[-1][3] == url:
                segs[-1][0] += texto
            else:
                segs.append([texto, f, c, url])
        saida.append([(t, f, c, u, largura(t, f, tam, espaco)) for t, f, c, u in segs])
    return saida
