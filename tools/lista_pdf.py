"""
Monta o PDF da Lista de Materiais de uma turma, com a cara do site.

As cores são lidas do próprio assets/css/style.css (variáveis em :root), então
mudar a paleta lá muda o PDF no próximo build. As fontes são as padrão do PDF —
Times no lugar da Cormorant Garamond e Helvetica no lugar da Lato —, porque as
fontes do site são baixadas do Google Fonts no navegador e não existem no PDF.
"""

import os
import re

import minipdf as mp

# ---- medidas, em pontos ----
W, H = mp.A4
M = 42.0                      # margem lateral
CW = W - 2 * M                # largura útil
CABECALHO_H = 72.0
FILETE_H = 2.2                # borda dourada sob o cabeçalho (border-bottom do .page-hero)
RODAPE_H = 34.0
TOPO_P1 = CABECALHO_H + FILETE_H + 30
TOPO_PN = CABECALHO_H + FILETE_H + 22
LIMITE = H - RODAPE_H - 22    # abaixo disso não se escreve

TAM = 9.5                     # texto das tabelas e das notas
ENTRELINHA = 14.0
PAD_X, PAD_Y = 7.5, 6.0
TAM_TH, ESP_TH = 7.4, 0.9     # cabeçalho de tabela: caixa-alta com espaçamento (.12em)


def cores_do_css(caminho):
    """Lê as variáveis de cor de :root em style.css -> {'navy-800': '#12295C', ...}."""
    with open(caminho, encoding="utf-8") as fh:
        css = fh.read()
    bloco = re.search(r":root\s*\{(.*?)\}", css, re.S).group(1)
    return {n: c.upper() for n, c in re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})\s*;", bloco)}


_cache_imagens = {}


def _png(raiz, caminho):
    """PNG decodificado (decodificar é a parte lenta: guarda para os demais PDFs do build)."""
    chave = ("png", caminho)
    if chave not in _cache_imagens:
        _cache_imagens[chave] = mp.ler_png(os.path.join(raiz, caminho))
    return _cache_imagens[chave]


def _imagem(raiz, caminho, fator, fundo=None):
    chave = (caminho, fator, fundo)
    if chave not in _cache_imagens:
        _cache_imagens[chave] = mp.reduzir(_png(raiz, caminho), fator, fundo)
    return _cache_imagens[chave]


class _Construtor:
    def __init__(self, raiz, escola, contato, titulo_doc, turma, cor):
        self.raiz, self.escola, self.contato, self.turma, self.c = raiz, escola, contato, turma, cor
        self.doc = mp.Documento(titulo_doc, escola, f"Lista de material escolar — {turma}")
        self.pag = None
        self.y = 0.0
        self.n_img = 0
        self.nomes_img = {}
        # Brasão: o mesmo PNG do site, reduzido à metade (272x340 -> 136x170), com transparência.
        w, h, rgb, alfa = _imagem(raiz, "assets/img/brasao.png", 2)
        self.doc.registrar_imagem("Brasao", w, h, rgb, alfa)
        self.brasao_proporcao = w / h

    # ---------- página ----------
    def nova_pagina(self):
        c = self.c
        p = self.pag = self.doc.nova_pagina()
        p.retangulo(0, 0, W, H, c["cream"])
        self._cabecalho(p)
        self.y = TOPO_P1 if len(self.doc.paginas) == 1 else TOPO_PN
        return p

    def _cabecalho(self, p):
        """Faixa azul-marinho com o nome da escola, 'Lista de Materiais' e a turma."""
        c = self.c
        # degradê 160° do .page-hero (navy-800 -> navy-900), na geometria do CSS
        import math
        ang = math.radians(160)
        dx, dy = math.sin(ang), -math.cos(ang)
        comp = abs(W * dx) + abs(CABECALHO_H * dy)
        cx, cy = W / 2, CABECALHO_H / 2
        p.degrade(0, 0, W, CABECALHO_H, c["navy-800"], c["navy-900"],
                  cx - dx * comp / 2, cy - dy * comp / 2, cx + dx * comp / 2, cy + dy * comp / 2)
        p.retangulo(0, CABECALHO_H, W, FILETE_H, c["gold-500"])

        alt = 52.0
        larg = alt * self.brasao_proporcao
        p.imagem("Brasao", M, (CABECALHO_H - alt) / 2, larg, alt)

        x = M + larg + 12
        p.texto(x, 33, self.escola, "serif-b", 15, c["gold-200"], 0.3)
        tag = "FÉ · EXCELÊNCIA · VIRTUDE"
        p.texto(x, 46, tag, "sans", 6.2, mp.misturar("#FFFFFF", c["navy-800"], .55), 1.3)
        esquerda_fim = x + max(mp.largura(self.escola, "serif-b", 15, 0.3),
                               mp.largura(tag, "sans", 6.2, 1.3))

        direita = W - M
        rotulo = "LISTA DE MATERIAIS 2027"
        p.texto(direita - mp.largura(rotulo, "sans-b", 7, 1.8) + 1.8, 29, rotulo, "sans-b", 7, c["gold-300"], 1.8)
        # a turma ocupa o que sobrar ao lado do nome da escola, até 20 pt
        disponivel = direita - esquerda_fim - 18
        tam = min(20.0, disponivel / mp.largura(self.turma, "serif-b", 1))
        p.texto(direita - mp.largura(self.turma, "serif-b", tam), 29 + 7 + tam * 0.72, self.turma,
                "serif-b", tam, c["white"])

    def _rodape(self, p, n, total):
        c = self.c
        p.retangulo(0, H - RODAPE_H, W, RODAPE_H, c["navy-900"])
        p.retangulo(0, H - RODAPE_H, W, 1.2, c["gold-500"])
        cor = mp.misturar("#FFFFFF", c["navy-900"], .68)
        for i, linha in enumerate(self.contato):
            p.texto(M, H - RODAPE_H + 14 + i * 10, linha, "sans", 6.8, cor)
        txt = f"Página {n} de {total}"
        p.texto(W - M - mp.largura(txt, "sans-b", 7.2), H - RODAPE_H + 19.5, txt, "sans-b", 7.2, c["gold-300"])

    def garantir(self, altura):
        if self.y + altura > LIMITE:
            self.nova_pagina()

    # ---------- blocos ----------
    def titulo(self, texto):
        c = self.c
        # h2 do site é peso 600: usa a fonte em negrito
        linhas = mp.quebrar_linhas([(texto, True, False, None)], "serif", 20, CW, c["navy-900"], c["navy-900"])
        for i, lin in enumerate(linhas):
            x = M
            for t, f, cor, _, w in lin:
                self.pag.texto(x, self.y + 17 + i * 23, t, f, 20, cor)
                x += w
        self.y += len(linhas) * 23 + 7
        # filete dourado (.rule): 84px de largura, degradê gold-500 -> gold-200
        self.pag.degrade(M, self.y, 50, 1.5, c["gold-500"], c["gold-200"], M, 0, M + 50, 0)
        self.y += 1.5 + 17

    def notas(self, itens_html):
        c = self.c
        recuo = 15.0
        for html in itens_html:
            runs, _ = mp.analisar_html(html)
            linhas = mp.quebrar_linhas(runs, "sans", TAM, CW - recuo, c["ink-soft"], c["navy-700"])
            altura = len(linhas) * ENTRELINHA
            self.garantir(altura)
            base0 = self.y + (ENTRELINHA - TAM) / 2 + TAM * 0.8
            self._estrela(M + 4, base0 - 3.3, c["gold-500"])
            self._linhas(linhas, M + recuo, self.y, TAM)
            self.y += altura + 4.5
        self.y += 14

    def _estrela(self, cx, cy, cor):
        """O ✦ do marcador dourado, desenhado como polígono (a fonte padrão não tem o glifo)."""
        import math
        pts = []
        for i in range(8):
            r = 4.2 if i % 2 == 0 else 1.3
            a = math.radians(-90 + i * 45)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.pag.poligono(pts, cor)

    def _linhas(self, linhas, x0, topo, tam, entrelinha=ENTRELINHA, espaco=0.0):
        """Escreve linhas já quebradas; segmentos com url viram link sublinhado."""
        c = self.c
        for i, lin in enumerate(linhas):
            base = topo + i * entrelinha + (entrelinha - tam) / 2 + tam * 0.8
            x = x0
            for t, f, cor, url, w in lin:
                self.pag.texto(x, base, t, f, tam, cor, espaco)
                if url:
                    self.pag.linha(x, base + 1.6, x + w, base + 1.6, c["gold-500"], 0.6)
                    self.pag.link(x, base - tam * 0.85, x + w, base + 2.5, url)
                x += w

    def _foto(self, src):
        """Foto do item: composta sobre o branco da célula, tamanho máximo ~180 px do site."""
        if src not in self.nomes_img:
            fator = max(1, round(_png(self.raiz, src)[0] / 190))
            w, h, rgb, _ = _imagem(self.raiz, src, fator, "#FFFFFF")
            self.n_img += 1
            nome = f"Im{self.n_img}"
            self.doc.registrar_imagem(nome, w, h, rgb)
            self.nomes_img[src] = (nome, w, h)
        nome, w, h = self.nomes_img[src]
        escala = min(96 / w, 104 / h)
        return nome, w * escala, h * escala

    def tabela(self, titulo, linhas, coluna="Quantidade"):
        c = self.c
        com_qtd = any(q for _, q in linhas)

        # largura da coluna de quantidade: cabe o maior valor sem quebrar (até um limite)
        wq = 0.0
        if com_qtd:
            vals = [mp.largura(q, "sans", TAM) for _, q in linhas if q]
            vals.append(mp.largura(coluna.upper(), "sans-b", TAM_TH, ESP_TH))
            wq = min(max(vals) + 2 * PAD_X, 150.0)
        wi = CW - wq

        # cabeçalho (th): caixa-alta, espaçado, dourado claro sobre navy-800
        cab = mp.quebrar_linhas([(titulo.upper(), True, False, None)], "sans", TAM_TH,
                                wi - 2 * PAD_X, c["gold-200"], c["gold-200"], ESP_TH)
        cab_h = max(len(cab) * 11.0 + 2 * 7.5, 24.0)

        linhas_lay = []
        for item_html, q in linhas:
            runs, imagens = mp.analisar_html(item_html)
            txt = mp.quebrar_linhas(runs, "sans", TAM, wi - 2 * PAD_X, c["ink"], c["navy-700"])
            h_txt = len(txt) * ENTRELINHA
            fotos = []
            for src, _alt in imagens:
                nome, fw, fh = self._foto(src)
                fotos.append((nome, fw, fh))
                h_txt += 7 + fh
            qlin = []
            if q:
                qlin = mp.quebrar_linhas([(q, False, False, None)], "sans", TAM, wq - 2 * PAD_X, c["ink"], c["ink"])
            h_q = len(qlin) * ENTRELINHA
            linhas_lay.append((txt, fotos, qlin, max(h_txt, h_q) + 2 * PAD_Y, len(txt) * ENTRELINHA))

        def desenha_cab():
            p = self.pag
            p.retangulo(M, self.y, CW, cab_h, c["navy-800"])
            topo = self.y + (cab_h - len(cab) * 11.0) / 2
            for i, lin in enumerate(cab):
                x = M + PAD_X
                for t, f, cor, _, w in lin:
                    p.texto(x, topo + i * 11.0 + 8.2, t, f, TAM_TH, cor, ESP_TH)
                    x += w
            if com_qtd:
                p.texto(M + wi + PAD_X, self.y + cab_h / 2 + TAM_TH * 0.36, coluna.upper(),
                        "sans-b", TAM_TH, c["gold-200"], ESP_TH)
            self.y += cab_h

        # o cabeçalho nunca fica sozinho no fim da página: leva junto a primeira linha
        self.garantir(cab_h + linhas_lay[0][3])
        desenha_cab()
        borda = mp.misturar(c["navy-900"], "#FFFFFF", .10)   # rgba(11,27,63,.1) sobre o branco
        for txt, fotos, qlin, altura, h_txt in linhas_lay:
            if self.y + altura > LIMITE:
                self.nova_pagina()
                desenha_cab()
            p = self.pag
            p.retangulo(M, self.y, CW, altura, "#FFFFFF")
            p.linha(M, self.y + altura, M + CW, self.y + altura, borda, 0.6)
            self._linhas(txt, M + PAD_X, self.y + PAD_Y, TAM)
            fy = self.y + PAD_Y + h_txt + 7
            for nome, fw, fh in fotos:
                p.imagem(nome, M + PAD_X, fy, fw, fh)
                fy += fh + 7
            if qlin:
                self._linhas(qlin, M + wi + PAD_X, self.y + PAD_Y, TAM)
            self.y += altura
        self.y += 22

    def finalizar(self):
        total = len(self.doc.paginas)
        for i, p in enumerate(self.doc.paginas, 1):
            self._rodape(p, i, total)
        return self.doc.salvar()


def gerar_pdf_lista(raiz, escola, contato, nome_turma, secoes, notas, css="assets/css/style.css"):
    """Devolve os bytes do PDF da lista de `nome_turma`.

    secoes: [(titulo, [(item_html, quantidade|None), ...], coluna?), ...] — o mesmo
    formato que a página do site usa em _tabela_lista().
    """
    cor = cores_do_css(os.path.join(raiz, css))
    b = _Construtor(
        raiz, escola, contato,
        f"Lista de Materiais 2027 — {nome_turma} — {escola}", nome_turma, cor,
    )
    b.nova_pagina()
    b.titulo(f"Lista de Material Escolar 2027 — {nome_turma}")
    b.notas(notas)
    for sec in secoes:
        b.tabela(*sec)
    return b.finalizar()
