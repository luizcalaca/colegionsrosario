#!/usr/bin/env python3
"""
Gerador estático do site do Colégio Nossa Senhora do Rosário.

Todas as páginas compartilham cabeçalho, menu e rodapé definidos aqui.
Uso: python3 build.py  (regrava os arquivos .html na raiz do projeto)
"""

import os
import re
from urllib.parse import quote_plus, quote
import hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://colegionsrosario.com.br"
SCHOOL = "Colégio Nossa Senhora do Rosário"
CNPJ = "66.154.330/0001-40"
ENDERECO_RUA = "Rua 255, nº 678 — Quadra 12"
ENDERECO_BAIRRO = "Setor Coimbra"
ENDERECO_CIDADE = "Goiânia — GO"
ENDERECO_CEP = "CEP 74533-150"
ENDERECO_MAPA = "Rua 255, 678 - Setor Coimbra, Goiânia - GO, 74533-150"
EMAIL = "colegionsrgo@gmail.com"
WHATSAPP = "5562991957333"          # formato internacional, para links wa.me
WHATSAPP_FMT = "(62) 99195-7333"    # formato de exibição
CREST = "assets/img/brasao.png"

def asset_url(path):
    """Anexa ao asset um sufixo derivado do seu conteúdo.

    Sem isso, um navegador que já visitou o site continua servindo o CSS antigo
    depois de uma atualização — foi exatamente o que aconteceu em teste.
    """
    with open(os.path.join(ROOT, path), "rb") as fh:
        digest = hashlib.sha1(fh.read()).hexdigest()[:8]
    return f"{path}?v={digest}"


def png_size(path):
    """Lê largura e altura do IHDR de um PNG (sem dependências externas)."""
    with open(os.path.join(ROOT, path), "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} não é um PNG")
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def crest(width, css_class="", alt=None):
    """<img> do brasão com a altura derivada do arquivo real.

    As dimensões vêm sempre do PNG em disco: trocar o arquivo por outro de
    proporção diferente não achata mais a imagem nem provoca salto de layout.
    """
    w, h = png_size(CREST)
    cls = f' class="{css_class}"' if css_class else ""
    alt = alt or f"Brasão do {SCHOOL}"
    return (f'<img{cls} src="{CREST}" alt="{alt}" '
            f'width="{width}" height="{round(width * h / w)}">')




# --------------------------------------------------------------------------
# Estrutura do menu — única fonte de verdade da navegação
# --------------------------------------------------------------------------
NAV = [
    ("O Colégio", None, [
        ("História", "historia.html"),
        ("Proposta Pedagógica", "proposta-pedagogica.html"),
        ("Equipe Docente", "equipe-docente.html"),
        ("Regimento Escolar", "regimento-escolar.html"),
    ]),
    ("Ensino", None, [
        ("Educação Infantil", "ensino-infantil.html"),
        ("Ensino Fundamental I", "ensino-fundamental-1.html"),
        ("Ensino Fundamental II", "ensino-fundamental-2.html"),
    ]),
    ("Currículo", None, [
        ("Pré-alfabetização", "curriculo-pre-alfabetizacao.html"),
        ("Inglês", "curriculo-ingles.html"),
        ("Francês", "curriculo-frances.html"),
        ("Português e Latim", "curriculo-portugues-latim.html"),
        ("Literatura Estrangeira", "curriculo-literatura-estrangeira.html"),
        ("Matemática", "curriculo-matematica.html"),
        ("História e Geografia", "curriculo-historia-geografia.html"),
        ("Filosofia Clássica", "curriculo-filosofia.html"),
        ("Artes", "curriculo-artes.html"),
        ("Música e Teatro", "curriculo-musica-teatro.html"),
        ("Oficinas", "curriculo-oficinas.html"),
        ("Educação Física", "curriculo-educacao-fisica.html"),
        ("Cortesia e Civilidade", "curriculo-cortesia-civilidade.html"),
        ("Materiais", "materiais.html"),
    ]),
    ("Cursos Extras", None, [
        ("Música", "cursos-musica.html"),
        ("Ballet", "cursos-ballet.html"),
    ]),
    ("Admissão", "admissao.html", None),
    ("Contato", "contato.html", None),
]


def render_nav(current):
    out = ['<nav class="nav" id="nav" aria-label="Menu principal">']
    for i, (label, href, children) in enumerate(NAV):
        if children:
            active = any(c[1] == current for c in children)
            aria = ' aria-current="page"' if active else ""
            out.append('<div class="nav-item">')
            out.append(
                f'<button class="nav-link" type="button" aria-expanded="false" '
                f'aria-controls="sub{i}"{aria}>{label}<span class="caret" aria-hidden="true"></span></button>'
            )
            out.append(f'<ul class="submenu" id="sub{i}">')
            for clabel, chref in children:
                ca = ' aria-current="page"' if chref == current else ""
                out.append(f'<li><a href="{chref}"{ca}>{clabel}</a></li>')
            out.append("</ul></div>")
        else:
            ca = ' aria-current="page"' if href == current else ""
            out.append(f'<div class="nav-item"><a class="nav-link" href="{href}"{ca}>{label}</a></div>')
    out.append("</nav>")
    return "\n".join(out)


HEADER = """<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="index.html">
      {crest_header}
      <span class="brand-text">
        <span class="brand-name">Colégio N. Sra. do Rosário</span>
        <span class="brand-tag">Fé · Excelência · Virtude</span>
      </span>
    </a>
    {nav}
    <a class="btn btn--gold header-cta" href="admissao.html">Matrículas 2027</a>
    <button class="nav-toggle" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="nav"><span></span></button>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        {crest_footer}
        <p>Educação clássica de inspiração católica, dedicada à formação integral do aluno — inteligência, caráter e fé.</p>
      </div>
      <div>
        <h4>O Colégio</h4>
        <ul>
          <li><a href="historia.html">História</a></li>
          <li><a href="proposta-pedagogica.html">Proposta Pedagógica</a></li>
          <li><a href="equipe-docente.html">Equipe Docente</a></li>
          <li><a href="regimento-escolar.html">Regimento Escolar</a></li>
        </ul>
      </div>
      <div>
        <h4>Ensino</h4>
        <ul>
          <li><a href="ensino-infantil.html">Educação Infantil</a></li>
          <li><a href="ensino-fundamental-1.html">Fundamental I</a></li>
          <li><a href="ensino-fundamental-2.html">Fundamental II</a></li>
          <li><a href="cursos-musica.html">Curso de Música</a></li>
          <li><a href="cursos-ballet.html">Ballet</a></li>
        </ul>
      </div>
      <div>
        <h4>Contato</h4>
        <ul>
          <li>__END_RUA__</li>
          <li>__END_BAIRRO__ · __END_CIDADE__</li>
          <li>__END_CEP__</li>
          <li><a class="link-contato" href="https://wa.me/__WA__" target="_blank" rel="noopener">WhatsApp __WA_FMT__</a></li>
          <li><a class="link-contato" href="mailto:__EMAIL__">__EMAIL__</a></li>
          <li>Secretaria: seg. a sex., 7h30 às 17h30</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 {school} · CNPJ __CNPJ__</span>
      <span>{site}</span>
    </div>
  </div>
</footer>"""

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<!-- marca JS ativo: sem isso, os blocos .reveal permanecem visíveis -->
<script>document.documentElement.className+=" js";</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{site}/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="assets/img/brasao-icon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/brasao-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
</head>
<body>
{header}
<main id="conteudo">
{body}
</main>
{footer}
<script src="{js}" defer></script>
</body>
</html>
"""


def page_hero(title, sub, crumb):
    return f"""<section class="page-hero">
  <div class="container">
    <p class="breadcrumb"><a href="index.html">Início</a> &nbsp;/&nbsp; {crumb}</p>
    <h1>{title}</h1>
    <p class="lede">{sub}</p>
  </div>
</section>"""


CTA = """<section class="cta-band">
  <div class="container">
    <h2>Venha conhecer o Rosário</h2>
    <p>Agende uma visita e conheça de perto a rotina, os professores e o ambiente que formam nossos alunos.</p>
    <p style="margin-top:1.6rem">
      <a class="btn btn--navy" href="admissao.html">Processo de Admissão</a>
      <a class="btn btn--navy" href="contato.html" style="margin-left:.6rem">Agendar Visita</a>
    </p>
  </div>
</section>"""


def cards(items, cols=3):
    out = [f'<div class="grid grid--{cols}">']
    for icon, title, text in items:
        out.append(
            f'<article class="card reveal"><div class="icon" aria-hidden="true">{icon}</div>'
            f"<h3>{title}</h3><p>{text}</p></article>"
        )
    out.append("</div>")
    return "\n".join(out)


def section(inner, mod="", extra=""):
    cls = f"section {mod}".strip()
    return f'<section class="{cls}"{extra}>\n<div class="container">\n{inner}\n</div>\n</section>'


def intro(eyebrow, title, lede, center=True):
    c = ' class="center reveal"' if center else ' class="reveal"'
    return (
        f"<div{c}><p class=\"eyebrow\">{eyebrow}</p><h2>{title}</h2>"
        f'<hr class="rule"><p class="lede">{lede}</p></div>'
    )


# --------------------------------------------------------------------------
# Página inicial
# --------------------------------------------------------------------------
HOME = """
<section class="hero">
  <div class="container">
""" + crest(118, "hero-crest") + """
    <p class="eyebrow">Desde 2022 · Educação Clássica Católica</p>
    <h1>Formar a inteligência,<br>cultivar a <em>alma</em></h1>
    <p class="hero-sub">Um colégio clássico de orientação católica, onde a excelência acadêmica caminha
    com a formação humana. Da Educação Infantil ao Fundamental II, em turmas reduzidas e
    acompanhamento próximo de cada família.</p>
    <div class="hero-actions">
      <a class="btn btn--gold" href="admissao.html">Matrículas 2027</a>
      <a class="btn btn--ghost" href="proposta-pedagogica.html">Nossa Proposta</a>
    </div>
  </div>
</section>

<section class="hero-strip">
  <div class="container">
    <div><span class="num">2022</span><span class="lbl">Fundado por famílias</span></div>
    <div><span class="num">20</span><span class="lbl">Alunos por turma</span></div>
    <div><span class="num">4</span><span class="lbl">Idiomas no currículo</span></div>
    <div><span class="num">100%</span><span class="lbl">Professores de excelência</span></div>
  </div>
</section>
""" + section(
    intro(
        "Bem-vindo",
        "Fundado por famílias, para as suas famílias",
        "O Rosário nasceu em 2022, criado por um grupo de famílias que não encontrava, para os "
        "próprios filhos, uma escola que unisse rigor intelectual e formação do caráter. "
        "Decidiram construí-la. Esse continua sendo o nosso compromisso: currículo clássico, "
        "professores presentes e uma comunidade que educa junto com a família.",
    )
    + '<div class="grid grid--4" style="margin-top:3.2rem">'
    + "".join(
        f'<a class="card card--link reveal" href="{href}"><div class="icon" aria-hidden="true">{icon}</div>'
        f"<h3>{t}</h3><p>{d}</p><span class=\"more\">Saiba mais →</span></a>"
        for icon, t, d, href in [
            ("I", "Educação Infantil", "Dos 3 aos 5 anos. Rotina acolhedora, alfabetização sólida e o primeiro contato com a música e a arte.", "ensino-infantil.html"),
            ("II", "Fundamental I", "1º ao 5º ano. Leitura, escrita e raciocínio matemático construídos com método e paciência.", "ensino-fundamental-1.html"),
            ("III", "Fundamental II", "6º ao 9º ano. Aprofundamento nas ciências, nas línguas clássicas e no pensamento crítico.", "ensino-fundamental-2.html"),
        ]
    )
    # Etapa ainda não oferecida: cartão sem link, marcado por uma faixa.
    + '<article class="card card--embreve reveal">'
      '<span class="card-faixa">Em breve</span>'
      '<div class="icon" aria-hidden="true">IV</div>'
      "<h3>Ensino Médio</h3>"
      "<p>1ª à 3ª série. A continuidade natural do percurso clássico, hoje em preparação para "
      "abrir as portas às nossas primeiras turmas.</p></article>"
    + "</div>",
) + section(
    '<div class="split">'
    '<div class="reveal"><p class="eyebrow">O que nos distingue</p>'
    "<h2>Um currículo pensado para durar a vida inteira</h2><hr class=\"rule\">"
    "<p>Ensinamos as disciplinas que formam a base de toda cultura ocidental — as línguas, "
    "as letras, as ciências e as artes — na ordem e no ritmo em que a criança é capaz de absorvê-las. "
    "Não perseguimos modismos pedagógicos; perseguimos o aprendizado real.</p>"
    '<ul class="list-gold">'
    "<li>Inglês em forma de Literatura desde a Educação Infantil</li>"
    "<li>Latim a partir do 6º ano, integrado ao ensino de Português</li>"
    "<li>Artes, Música e Teatro como disciplinas regulares, não como extras</li>"
    "<li>Formação católica e acompanhamento espiritual em todos os anos</li>"
    "<li>Avaliação contínua com devolutiva individual às famílias</li>"
    "</ul>"
    '<p style="margin-top:1.6rem"><a class="btn btn--navy" href="proposta-pedagogica.html">Conheça a proposta pedagógica</a></p></div>'
    '<div class="panel reveal"><h3>O dia do aluno</h3>'
    "<ul>"
    "<li><strong>7h</strong> — Acolhida e oração da manhã</li>"
    "<li><strong>7h15</strong> — Aulas do núcleo comum</li>"
    "<li><strong>9h30</strong> — Intervalo e recreio orientado</li>"
    "<li><strong>9h50</strong> — Línguas: Inglês, Francês ou Latim</li>"
    "<li><strong>11h10</strong> — Artes, Música ou Teatro</li>"
    "<li><strong>12h</strong> — Encerramento e saída</li>"
    "<li><strong>13h30</strong> — Cursos extras: Música e Ballet</li>"
    "</ul></div></div>",
    "section--cream",
) + section(
    '<blockquote class="quote">"Educar não é encher um vaso, mas acender uma chama."</blockquote>'
    '<p class="quote-author">Lema do Colégio</p>',
    "section--navy",
) + section(
    intro(
        "Além da sala de aula",
        "Cursos Extras",
        "No contraturno, o Colégio abre suas salas para a formação artística aprofundada, "
        "aberta também a alunos de fora da comunidade escolar.",
    )
    + '<div class="grid grid--2" style="margin-top:3rem">'
    '<a class="card card--link reveal" href="cursos-musica.html"><div class="icon" aria-hidden="true">♪</div>'
    "<h3>Música</h3><p>Piano, violino, violão, canto coral e teoria musical, do iniciante ao "
    "preparatório para conservatório. Aulas individuais e em grupo.</p>"
    '<span class="more">Ver o curso →</span></a>'
    '<a class="card card--link reveal" href="cursos-ballet.html"><div class="icon" aria-hidden="true">✦</div>'
    "<h3>Ballet</h3><p>Ballet clássico com método Royal Academy of Dance, do baby class ao "
    "nível intermediário, com apresentação anual no teatro.</p>"
    '<span class="more">Ver o curso →</span></a>'
    "</div>",
) + CTA


# --------------------------------------------------------------------------
# Blocos reutilizáveis das páginas internas
# --------------------------------------------------------------------------
def text_block(paragraphs, eyebrow=None, title=None):
    out = ['<div class="reveal" style="max-width:74ch;margin-inline:auto">']
    if eyebrow:
        out.append(f'<p class="eyebrow">{eyebrow}</p>')
    if title:
        out.append(f'<h2>{title}</h2><hr class="rule">')
    out += [f"<p>{p}</p>" for p in paragraphs]
    out.append("</div>")
    return "\n".join(out)


def subject_page(nome, eyebrow, resumo, paragrafos, destaques, carga, objetivos):
    """Layout comum das páginas de Currículo."""
    linhas = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in carga)
    return (
        page_hero(nome, resumo, f'<a href="curriculo-ingles.html">Currículo</a> &nbsp;/&nbsp; {nome}')
        + section(text_block(paragrafos, eyebrow, f"{nome} no Rosário"))
        + section(
            '<div class="split">'
            '<div class="reveal"><p class="eyebrow">O que o aluno desenvolve</p>'
            f"<h2>Objetivos de aprendizagem</h2><hr class=\"rule\">"
            '<ul class="list-gold">' + "".join(f"<li>{o}</li>" for o in objetivos) + "</ul></div>"
            '<div class="panel reveal"><h3>Carga horária semanal</h3>'
            '<div class="table-wrap"><table><thead><tr><th>Etapa</th><th>Aulas</th></tr></thead>'
            f"<tbody>{linhas}</tbody></table></div></div></div>",
            "section--cream",
        )
        + section(
            intro("Na prática", "Como as aulas acontecem", "")
            # Com 4 destaques, três colunas deixariam o último cartão sozinho na linha.
            + f'<div style="margin-top:2.4rem">{cards(destaques, 4 if len(destaques) == 4 else 3)}</div>'
        )
        + CTA
    )


# --------------------------------------------------------------------------
# Conteúdo das páginas
# --------------------------------------------------------------------------
PAGES = {}

PAGES["index.html"] = dict(
    title=f"{SCHOOL} — Educação Clássica de Orientação Católica",
    description="Colégio clássico e católico, da Educação Infantil ao Fundamental II. "
    "Inglês, Francês, Latim, Artes, Música e Teatro no currículo. Matrículas abertas.",
    body=HOME,
)

# ---- O Colégio -----------------------------------------------------------
PAGES["historia.html"] = dict(
    title=f"História — {SCHOOL}",
    description="Como o Colégio Nossa Senhora do Rosário nasceu, em 2022, da iniciativa de um grupo de famílias.",
    body=page_hero(
        "História",
        "Uma escola que não existia — até que um grupo de famílias decidiu construí-la.",
        '<a href="historia.html">O Colégio</a> &nbsp;/&nbsp; História',
    )
    + section(
        text_block(
            [
                "O Colégio Nossa Senhora do Rosário foi fundado em 2022 por um grupo de famílias "
                "que compartilhava a mesma inquietação: queriam para os filhos uma educação séria, "
                "enraizada na fé católica, e não a encontravam.",
                "A decisão foi construí-la. Reuniram-se, estudaram propostas pedagógicas, visitaram "
                "escolas, procuraram professores. O Colégio abriu as portas com poucas turmas, um "
                "currículo clássico definido desde o primeiro dia e a convicção de que uma escola "
                "não precisa escolher entre exigência acadêmica e cuidado com cada criança.",
                "Somos uma escola jovem, e temos consciência disso. O que oferecemos não é a "
                "autoridade de um nome antigo, mas o compromisso de quem fundou esta casa para os "
                "próprios filhos — e responde por ela diariamente diante das outras famílias.",
            ],
            "2022 — 2026",
            "Uma escola nascida da iniciativa das famílias",
        )
    )
    + section(
        intro("Linha do tempo", "Marcos da nossa trajetória", "")
        + '<div style="max-width:62ch;margin:3rem auto 0">'
        + '<ul class="timeline">'
        + "".join(
            f'<li class="reveal"><span class="year">{ano}</span><p>{txt}</p></li>'
            for ano, txt in [
                ("2021", "Um grupo de famílias começa a se reunir para estudar a criação de uma escola clássica e católica."),
                ("2022", "Fundação do Colégio, com as primeiras turmas de Educação Infantil e Fundamental I."),
                ("2023", "Implantação do ensino de Inglês em forma de Literatura desde a Educação Infantil."),
                ("2024", "Abertura do Fundamental II e entrada do Latim no currículo, integrado ao Português."),
                ("2025", "Criação dos cursos extras de Música e Ballet, abertos também à comunidade."),
                ("2026", "Consolidação do Fundamental II e revisão integral do currículo clássico."),
            ]
        )
        + "</ul></div>",
        "section--cream",
    )
    + CTA,
)

PAGES["proposta-pedagogica.html"] = dict(
    title=f"Proposta Pedagógica — {SCHOOL}",
    description="Educação clássica católica: currículo, método e formação integral do aluno.",
    body=page_hero(
        "Proposta Pedagógica",
        "Uma educação clássica, católica e integral — da formação da inteligência à formação do caráter.",
        '<a href="historia.html">O Colégio</a> &nbsp;/&nbsp; Proposta Pedagógica',
    )
    + section(
        text_block(
            [
                "Acreditamos que educar é conduzir o aluno ao encontro daquilo que é verdadeiro, bom "
                "e belo. Esse princípio não é um enfeite institucional: ele determina o que ensinamos, "
                "em que ordem e com que método.",
                "Nosso currículo é clássico no sentido próprio do termo. Parte do domínio da língua "
                "materna, avança para as línguas estrangeiras e para o Latim, sustenta-se no raciocínio "
                "matemático e no estudo das ciências, e culmina na capacidade de argumentar com clareza "
                "e julgar com critério.",
                "A formação católica atravessa toda essa estrutura. Não é uma disciplina isolada, "
                "mas o horizonte que dá unidade ao conjunto — vivida na oração diária, nos tempos "
                "litúrgicos e no exemplo cotidiano dos professores.",
            ],
            "Fundamentos",
            "O que orienta nosso trabalho",
        )
    )
    + section(
        intro("Os três pilares", "Como formamos nossos alunos", "")
        + f'<div style="margin-top:3rem">'
        + cards(
            [
                ("I", "Inteligência", "Conteúdo sólido, ensinado com método e cobrado com clareza. Turmas de até 20 alunos permitem que nenhuma dúvida passe despercebida."),
                ("II", "Caráter", "Disciplina, pontualidade, respeito e responsabilidade são ensinados como se ensina qualquer matéria: com constância e com exemplo."),
                ("III", "Fé", "Oração diária, catequese, sacramentos e acompanhamento espiritual, sempre em diálogo respeitoso com as famílias."),
            ]
        )
        + "</div>",
        "section--cream",
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">Método</p><h2>Como ensinamos</h2><hr class="rule">'
        "<p>Nosso método é deliberadamente tradicional em suas escolhas centrais e "
        "moderno naquilo que efetivamente ajuda o aluno a aprender.</p>"
        '<ul class="list-gold">'
        "<li><strong>Aula expositiva bem preparada</strong> — o professor conduz, o aluno acompanha e registra</li>"
        "<li><strong>Memorização orientada</strong> — tabuadas, declinações, poemas e datas, na idade certa</li>"
        "<li><strong>Leitura de textos integrais</strong> — não resumos, não fragmentos</li>"
        "<li><strong>Escrita frequente e corrigida à mão</strong> — redação semanal a partir do 3º ano</li>"
        "<li><strong>Avaliação contínua</strong> — com devolutiva individual a cada bimestre</li>"
        "</ul></div>"
        '<div class="panel reveal"><h3>Compromissos com a família</h3><ul>'
        "<li>Reunião individual de pais a cada bimestre</li>"
        "<li>Relatório descritivo além da nota</li>"
        "<li>Comunicação direta com a coordenação, sem intermediários</li>"
        "<li>Agenda de conteúdos publicada no início de cada bimestre</li>"
        "<li>Política clara sobre uso de telas — o Colégio é livre de celulares</li>"
        "</ul></div></div>"
    )
    + CTA,
)

PAGES["equipe-docente.html"] = dict(
    title=f"Equipe Docente — {SCHOOL}",
    description="Professores de excelência, formação continuada e acompanhamento próximo de cada aluno.",
    body=page_hero(
        "Equipe Docente",
        "Professores que permanecem, conhecem cada aluno pelo nome e dominam o que ensinam.",
        '<a href="historia.html">O Colégio</a> &nbsp;/&nbsp; Equipe Docente',
    )
    + section(
        text_block(
            [
                "Um colégio vale o que valem seus professores. Por isso, o Rosário investe em "
                "contratação criteriosa, formação continuada e — talvez o mais importante — em "
                "condições de trabalho que façam o bom professor querer ficar.",
                "Por sermos uma escola jovem, montamos o corpo docente escolhendo um a um. Cada "
                "professor foi entrevistado pela Direção e conhece a proposta clássica que assumiu "
                "ao entrar — nenhum foi herdado de uma estrutura anterior.",
                "O resultado é uma equipe pequena e coesa, em que todos os professores conhecem "
                "todos os alunos pelo nome.",
            ],
            "Quem ensina",
            "Permanência e preparo",
        )
    )
    + section(
        intro("Números", "A equipe em perspectiva", "")
        + f'<div style="margin-top:3rem">'
        + cards(
            [
                ("100%", "Licenciados", "Todo o corpo docente possui licenciatura plena na disciplina que leciona."),
                ("68%", "Pós-graduados", "Mais de dois terços dos professores possuem especialização, mestrado ou doutorado."),
                ("20", "Máximo por turma", "Nenhuma turma do Colégio passa de 20 alunos, em qualquer etapa."),
                ("40h", "Formação anual", "Horas de formação continuada oferecidas pela instituição a cada ano."),
            ],
            4,
        )
        + "</div>",
        "section--cream",
    )
    + section(
        intro("Coordenação", "Estrutura pedagógica", "")
        + '<div class="table-wrap reveal" style="margin-top:2.6rem">'
        "<table><thead><tr><th>Área</th><th>Responsabilidade</th></tr></thead><tbody>"
        + "".join(
            f"<tr><td><strong>{a}</strong></td><td>{b}</td></tr>"
            for a, b in [
                ("Direção Geral", "Condução institucional, relação com as famílias e guarda da proposta pedagógica."),
                ("Coordenação da Educação Infantil", "Acompanhamento das turmas de 3 a 5 anos e da transição para o Fundamental I."),
                ("Coordenação do Fundamental I", "Alfabetização, progressão de leitura e escrita e acompanhamento individual do 1º ao 5º ano."),
                ("Coordenação do Fundamental II", "Articulação das disciplinas do 6º ao 9º ano e preparação para o Ensino Médio."),
                ("Coordenação de Línguas", "Inglês, Francês, Português e Latim: progressão integrada e avaliação de proficiência."),
                ("Coordenação de Artes", "Artes visuais, Música e Teatro, no currículo e nos cursos extras."),
                ("Orientação Educacional", "Apoio ao aluno, mediação de conflitos e articulação com as famílias."),
            ]
        )
        + "</tbody></table></div>"
    )
    + CTA,
)

PAGES["regimento-escolar.html"] = dict(
    title=f"Regimento Escolar — {SCHOOL}",
    description="Normas de convivência, avaliação, frequência e uniforme do Colégio Nossa Senhora do Rosário.",
    body=page_hero(
        "Regimento Escolar",
        "As normas que organizam a vida escolar e sustentam um ambiente de estudo sereno.",
        '<a href="historia.html">O Colégio</a> &nbsp;/&nbsp; Regimento Escolar',
    )
    + section(
        text_block(
            [
                "O Regimento Escolar é o documento que estabelece a organização administrativa e "
                "didático-pedagógica do Colégio, os direitos e deveres de alunos, famílias e "
                "funcionários, e os critérios de avaliação e promoção.",
                "Abaixo estão resumidos os pontos mais consultados. O documento integral é entregue "
                "no ato da matrícula e pode ser solicitado a qualquer momento na Secretaria.",
            ],
            "Documento institucional",
            "Sobre o Regimento",
        )
        + '<div style="max-width:74ch;margin:3rem auto 0">'
        + "".join(
            f'<div class="acc reveal"><button class="acc-head" type="button" aria-expanded="false">{q}</button>'
            f'<div class="acc-body"><p>{a}</p></div></div>'
            for q, a in [
                ("Avaliação e promoção",
                 "O ano letivo é dividido em quatro bimestres. A média para aprovação é 7,0 por disciplina, "
                 "considerando provas, trabalhos e avaliação contínua. Alunos com média entre 5,0 e 6,9 têm "
                 "direito a estudos de recuperação ao final de cada bimestre e ao final do ano."),
                ("Frequência",
                 "É exigida frequência mínima de 75% da carga horária anual total. As faltas são comunicadas "
                 "às famílias semanalmente; três faltas consecutivas sem justificativa acionam contato da "
                 "Orientação Educacional."),
                ("Uniforme",
                 "O uso do uniforme completo é obrigatório em todas as atividades escolares, incluindo os "
                 "cursos extras e as saídas pedagógicas. O uniforme é adquirido diretamente no Colégio."),
                ("Uso de celulares e dispositivos",
                 "O Colégio é livre de celulares. Aparelhos devem permanecer desligados e guardados no armário "
                 "individual durante todo o período de aula, inclusive nos intervalos."),
                ("Normas de convivência",
                 "Espera-se de cada aluno pontualidade, respeito no trato com colegas e funcionários, zelo pelo "
                 "patrimônio e honestidade acadêmica. Medidas disciplinares seguem gradação prevista no "
                 "Regimento, sempre com comunicação prévia à família."),
                ("Atendimento às famílias",
                 "Reuniões individuais são agendadas a cada bimestre. Fora desse calendário, a Coordenação "
                 "atende mediante agendamento na Secretaria, de segunda a sexta, das 8h às 17h."),
            ]
        )
        + "</div>"
    )
    + section(
        '<div class="center reveal"><h2>Precisa do documento completo?</h2><hr class="rule">'
        "<p class=\"lede\">A Secretaria envia o Regimento Escolar integral em PDF mediante solicitação.</p>"
        '<p style="margin-top:1.6rem"><a class="btn btn--gold" href="contato.html">Solicitar à Secretaria</a></p></div>',
        "section--cream",
    ),
)


# ---- Ensino --------------------------------------------------------------
def ensino_page(nome, faixa, resumo, paragrafos, pilares, grade, rotina):
    linhas = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in grade)
    return (
        page_hero(nome, resumo, f'<a href="ensino-infantil.html">Ensino</a> &nbsp;/&nbsp; {nome}')
        + section(text_block(paragrafos, faixa, f"{nome} no Rosário"))
        + section(
            intro("Eixos do trabalho", "O que sustenta esta etapa", "")
            + f'<div style="margin-top:3rem">{cards(pilares)}</div>',
            "section--cream",
        )
        + section(
            '<div class="split">'
            '<div class="reveal"><p class="eyebrow">Organização</p><h2>Matriz curricular</h2><hr class="rule">'
            '<div class="table-wrap"><table><thead><tr><th>Componente</th><th>Aulas semanais</th></tr></thead>'
            f"<tbody>{linhas}</tbody></table></div></div>"
            '<div class="panel reveal"><h3>Rotina</h3><ul>'
            + "".join(f"<li>{r}</li>" for r in rotina)
            + "</ul></div></div>"
        )
        + CTA
    )


PAGES["ensino-infantil.html"] = dict(
    title=f"Educação Infantil — {SCHOOL}",
    description="Educação Infantil de 3 a 5 anos: rotina acolhedora, alfabetização sólida, música e arte.",
    body=ensino_page(
        "Educação Infantil",
        "3 a 5 anos",
        "Os primeiros anos de escola, num ambiente calmo, previsível e afetuoso — onde a criança aprende a aprender.",
        [
            "A Educação Infantil do Rosário é pensada para acolher sem abrir mão do propósito. "
            "A criança encontra aqui uma rotina estável, adultos atentos e um espaço organizado, "
            "porque é essa previsibilidade que dá segurança para explorar e para errar.",
            "O trabalho pedagógico avança com naturalidade: consciência fonológica, coordenação motora, "
            "linguagem oral, noções de número e espaço. Ao final do Infantil V, a criança chega ao "
            "Fundamental I com a base pronta para a alfabetização formal — e com gosto pelo estudo.",
            "Inglês, Francês, Música e Arte já fazem parte da rotina, sempre em formato lúdico, "
            "com professores especialistas.",
        ],
        [
            ("♦", "Rotina e autonomia", "Sequências previsíveis, responsabilidades pequenas e crescentes, cuidado com o próprio material."),
            ("♦", "Linguagem", "Contação de histórias diária, roda de conversa, consciência fonológica e primeiros traçados."),
            ("♦", "Corpo e arte", "Psicomotricidade, música, artes visuais e brincadeira dirigida ao ar livre."),
        ],
        [
            ("Linguagem e Literatura", "8"), ("Matemática e Natureza", "5"), ("Inglês", "3"),
            ("Francês", "2"), ("Música", "2"), ("Artes Visuais", "2"),
            ("Psicomotricidade", "3"), ("Formação Católica", "2"),
        ],
        [
            "<strong>Período:</strong> matutino (7h30 às 11h45) ou vespertino (13h às 17h15)",
            "<strong>Turmas:</strong> até 20 crianças por turma",
            "<strong>Equipe:</strong> uma professora regente e uma auxiliar por turma",
            "<strong>Adaptação:</strong> primeiras duas semanas com horário progressivo",
            "<strong>Contraturno:</strong> Música e Ballet disponíveis a partir dos 4 anos",
        ],
    ),
)

PAGES["ensino-fundamental-1.html"] = dict(
    title=f"Ensino Fundamental I — {SCHOOL}",
    description="Fundamental I, do 1º ao 5º ano: alfabetização sólida, leitura, escrita e raciocínio matemático.",
    body=ensino_page(
        "Ensino Fundamental I",
        "1º ao 5º ano",
        "A etapa em que se constroem as ferramentas de toda a vida escolar: ler bem, escrever bem e raciocinar com clareza.",
        [
            "O Fundamental I é a etapa decisiva. É aqui que o aluno se torna leitor fluente, "
            "escreve com estrutura e domina as operações fundamentais. Nada disso acontece por acaso: "
            "exige método, repetição inteligente e correção individual.",
            "Alfabetizamos por método fônico sistemático, com progressão explícita e material próprio. "
            "A partir do 3º ano, a redação passa a ser semanal e corrigida individualmente pelo professor. "
            "Em Matemática, o cálculo mental e a tabuada são trabalhados diariamente até a automatização.",
            "Ao lado disso, as línguas e as artes ganham espaço crescente — Inglês e Francês em aulas "
            "regulares, Música e Teatro como disciplinas do currículo.",
        ],
        [
            ("♦", "Leitura e escrita", "Método fônico, leitura de obras integrais e redação semanal corrigida à mão."),
            ("♦", "Raciocínio matemático", "Cálculo mental diário, tabuada automatizada e resolução de problemas."),
            ("♦", "Estudo e organização", "Agenda, caderno organizado e hábito de estudo construídos desde o 1º ano."),
        ],
        [
            ("Português", "7"), ("Matemática", "6"), ("Ciências", "3"),
            ("História e Geografia", "4"), ("Inglês", "4"), ("Francês", "2"),
            ("Artes", "2"), ("Música", "2"), ("Teatro", "1"),
            ("Educação Física", "2"), ("Formação Católica", "2"),
        ],
        [
            "<strong>Período:</strong> matutino (7h às 12h)",
            "<strong>Turmas:</strong> até 20 alunos",
            "<strong>Lição de casa:</strong> diária, de 30 a 50 minutos conforme o ano",
            "<strong>Avaliação:</strong> bimestral, com relatório descritivo individual",
            "<strong>Contraturno:</strong> Música, Ballet e plantão de estudos",
        ],
    ),
)

PAGES["ensino-fundamental-2.html"] = dict(
    title=f"Ensino Fundamental II — {SCHOOL}",
    description="Fundamental II, do 6º ao 9º ano: ciências, línguas clássicas, argumentação e pensamento crítico.",
    body=ensino_page(
        "Ensino Fundamental II",
        "6º ao 9º ano",
        "O aprofundamento: ciências com rigor, línguas clássicas, e a formação de quem sabe argumentar e julgar.",
        [
            "No Fundamental II, o aluno passa a estudar com professores especialistas em cada disciplina "
            "e enfrenta uma exigência crescente de autonomia. É a etapa em que o conhecimento deixa de ser "
            "apenas acumulado e passa a ser articulado.",
            "O Latim entra no 6º ano, integrado ao ensino de Português — não como curiosidade erudita, "
            "mas como ferramenta que ilumina a gramática, amplia o vocabulário e treina o raciocínio "
            "analítico. As ciências ganham laboratório, e a redação passa a incluir dissertação argumentativa.",
            "Ao final do 9º ano, nossos alunos ingressam nos melhores Ensinos Médios da região — "
            "e, mais do que isso, ingressam sabendo estudar sozinhos.",
        ],
        [
            ("♦", "Rigor científico", "Laboratório, método experimental e matemática trabalhada com demonstração."),
            ("♦", "Domínio das línguas", "Inglês e Francês com avaliação de proficiência; Latim integrado ao Português."),
            ("♦", "Argumentação", "Dissertação, seminários, debate regrado e leitura de obras clássicas integrais."),
        ],
        [
            ("Português e Literatura", "6"), ("Latim", "2"), ("Matemática", "6"),
            ("Ciências / Física / Química / Biologia", "5"), ("História", "3"), ("Geografia", "3"),
            ("Inglês", "4"), ("Francês", "3"), ("Artes", "2"),
            ("Música ou Teatro", "2"), ("Educação Física", "2"), ("Formação Católica", "2"),
        ],
        [
            "<strong>Período:</strong> matutino (7h às 12h)",
            "<strong>Turmas:</strong> até 20 alunos",
            "<strong>Estudo dirigido:</strong> duas tardes por semana, com professor de plantão",
            "<strong>Avaliação:</strong> provas bimestrais, trabalhos e simulados a partir do 8º ano",
            "<strong>Orientação:</strong> acompanhamento individual de projeto de vida no 9º ano",
        ],
    ),
)

# ---- Currículo -----------------------------------------------------------
PAGES["curriculo-ingles.html"] = dict(
    title=f"Inglês — Currículo — {SCHOOL}",
    description="Inglês desde a Educação Infantil, com progressão até nível B2 e certificação internacional.",
    body=subject_page(
        "Inglês", "Língua estrangeira",
        "Do primeiro contato lúdico aos 3 anos até a proficiência avaliada por exame internacional no 9º ano.",
        [
            "O ensino de Inglês no Rosário é contínuo e cumulativo. Começa aos 3 anos, em formato "
            "oral e lúdico, e avança sem rupturas até o 9º ano, quando o aluno é capaz de ler textos "
            "autênticos, escrever com correção e sustentar uma conversa sobre temas abstratos.",
            "Trabalhamos com turmas divididas por nível a partir do 4º ano, o que permite que cada "
            "aluno avance no seu ritmo sem ser freado nem atropelado. A avaliação é feita por exames "
            "internos e, ao final do Fundamental II, por exame externo de proficiência.",
            "A literatura entra cedo: do 5º ano em diante, os alunos leem obras integrais adaptadas "
            "e, no 9º ano, ao menos um clássico no original.",
        ],
        [
            ("A", "Turmas por nível", "A partir do 4º ano, as turmas são organizadas por proficiência real, não por idade."),
            ("B", "Prática oral diária", "Todas as aulas são conduzidas em inglês, com foco em produção oral desde o início."),
            ("C", "Certificação", "Preparação e aplicação de exame internacional de proficiência no 9º ano."),
        ],
        [("Educação Infantil", "3 aulas"), ("Fundamental I", "4 aulas"), ("Fundamental II", "4 aulas")],
        [
            "Compreensão e produção oral com naturalidade",
            "Leitura de textos autênticos e obras literárias integrais",
            "Escrita estruturada: narrativa, descritiva e dissertativa",
            "Domínio gramatical explícito, apoiado no estudo do Português e do Latim",
            "Nível B2 do Quadro Comum Europeu ao final do 9º ano",
        ],
    ),
)

PAGES["curriculo-frances.html"] = dict(
    title=f"Francês — Currículo — {SCHOOL}",
    description="Francês desde a Educação Infantil, com preparação para o DELF Junior.",
    body=subject_page(
        "Francês", "Segunda língua estrangeira",
        "A segunda língua estrangeira do currículo, presente desde a Educação Infantil e conduzida até o DELF.",
        [
            "Poucos colégios brasileiros mantêm o Francês como disciplina regular. Mantemos — e desde "
            "os 3 anos — por uma convicção pedagógica: aprender uma segunda língua estrangeira em "
            "paralelo à primeira desenvolve uma flexibilidade linguística que nenhuma outra disciplina "
            "produz.",
            "O Francês também é a porta de entrada para uma tradição literária, filosófica e artística "
            "que dialoga diretamente com o currículo clássico. Nossos alunos leem La Fontaine no "
            "Fundamental I e chegam ao 9º ano lendo textos de Saint-Exupéry no original.",
            "Ao final do Fundamental II, o aluno é preparado para o DELF Junior, certificação oficial "
            "do Ministério da Educação francês.",
        ],
        [
            ("A", "Início precoce", "Contato desde os 3 anos, em canções, jogos e rotinas orais."),
            ("B", "Cultura francófona", "Literatura, música e cinema integrados ao ensino da língua."),
            ("C", "DELF Junior", "Preparação sistemática para a certificação oficial a partir do 8º ano."),
        ],
        [("Educação Infantil", "2 aulas"), ("Fundamental I", "2 aulas"), ("Fundamental II", "3 aulas")],
        [
            "Compreensão oral e pronúncia consistente",
            "Leitura de fábulas, poemas e narrativas no original",
            "Produção escrita adequada ao nível A2/B1",
            "Familiaridade com a cultura e a história francófonas",
            "Preparação para o DELF Junior A2 ou B1",
        ],
    ),
)

PAGES["curriculo-portugues-latim.html"] = dict(
    title=f"Português e Latim — Currículo — {SCHOOL}",
    description="Português e Latim ensinados de forma integrada: gramática, literatura, redação e raízes da língua.",
    body=subject_page(
        "Português e Latim", "Língua materna e língua clássica",
        "O coração do currículo clássico: o domínio da língua materna, iluminado pelo estudo da língua que a originou.",
        [
            "Português e Latim são ensinados de forma integrada porque, no Rosário, entendemos que "
            "são a mesma coisa vista de dois ângulos. Quem estuda a declinação latina entende para "
            "sempre o que é um objeto direto. Quem conhece as raízes latinas nunca mais fica preso "
            "ao vocabulário de uso corrente.",
            "Em Português, o trabalho é sistemático: gramática explícita, análise sintática, leitura "
            "de obras integrais e redação semanal corrigida individualmente. Do 3º ano em diante, "
            "o aluno escreve toda semana — e recebe cada texto de volta com apontamentos.",
            "O Latim entra no 6º ano com duas aulas semanais. Trabalhamos morfologia, tradução de "
            "textos progressivamente mais complexos e vocabulário etimológico. Ao final do 9º ano, "
            "o aluno traduz passagens da Vulgata e de autores clássicos adaptados.",
        ],
        [
            ("A", "Gramática explícita", "Análise morfológica e sintática ensinadas diretamente, com nomenclatura precisa."),
            ("B", "Redação semanal", "Um texto por semana a partir do 3º ano, corrigido individualmente pelo professor."),
            ("C", "Latim aplicado", "Do 6º ano: declinações, conjugações, etimologia e tradução de textos."),
        ],
        [("Fundamental I — Português", "7 aulas"), ("Fundamental II — Português", "6 aulas"), ("Fundamental II — Latim", "2 aulas")],
        [
            "Leitura fluente e crítica de textos literários integrais",
            "Domínio da gramática normativa com nomenclatura correta",
            "Redação narrativa, descritiva e dissertativa-argumentativa",
            "Vocabulário ampliado pelo estudo etimológico latino",
            "Tradução de textos latinos simples e da Vulgata",
        ],
    ),
)

PAGES["curriculo-artes.html"] = dict(
    title=f"Artes — Currículo — {SCHOOL}",
    description="Artes visuais como disciplina regular: desenho de observação, história da arte e ateliê.",
    body=subject_page(
        "Artes", "Artes visuais e estética",
        "Desenho, pintura e história da arte como disciplina séria — porque o belo não é questão de "
        "gosto particular, e também se aprende.",
        [
            "Artes, no Rosário, não é a aula em que se preenche o tempo. É uma disciplina com "
            "programa, progressão e avaliação, ensinada por professores formados em artes visuais.",
            "O eixo central é o desenho de observação, trabalhado desde o Fundamental I. A criança "
            "aprende a olhar antes de aprender a representar — e essa capacidade de observação atenta "
            "transborda para todas as outras disciplinas.",
            "Paralelamente, percorremos a história da arte ocidental, da arte sacra medieval ao "
            "modernismo brasileiro, sempre com contato direto com obras: visitas a museus, reproduções "
            "de qualidade e, quando possível, o ateliê a céu aberto da própria cidade.",
            "Sustentando tudo isso há uma convicção que a tradição clássica formulou como a doutrina "
            "dos transcendentais: o <em>verum</em>, o <em>bonum</em> e o <em>pulchrum</em> — o "
            "verdadeiro, o bom e o belo — não são três gostos independentes, mas três modos de "
            "dizer a mesma realidade. Por isso a estética não é um apêndice decorativo do currículo: "
            "ensinar uma criança a reconhecer o que é belo é da mesma família que ensiná-la a "
            "reconhecer o que é verdadeiro em Matemática e o que é bom na conduta.",
            "Na prática, isso significa que discutimos por que uma obra é boa, e não apenas se o "
            "aluno gostou dela. O juízo estético é tratado como juízo — com razões, critérios e "
            "argumentos —, o que prepara o terreno para a Filosofia no Fundamental II.",
        ],
        [
            ("A", "Desenho de observação", "Fundamento técnico trabalhado com progressão do 1º ao 9º ano."),
            ("B", "História da arte", "Da arte sacra medieval ao modernismo, com foco em leitura de obra."),
            ("C", "Estética", "<em>Verum</em>, <em>bonum</em> e <em>pulchrum</em>: o belo tratado como juízo "
                  "com razões, e não como preferência particular."),
            ("D", "Ateliê e exposição", "Produção própria em diversas técnicas, com mostra anual aberta às famílias."),
        ],
        [("Educação Infantil", "2 aulas"), ("Fundamental I", "2 aulas"), ("Fundamental II", "2 aulas")],
        [
            "Domínio técnico do desenho de observação e da proporção",
            "Repertório de história da arte ocidental e brasileira",
            "Experiência prática com aquarela, guache, carvão e modelagem",
            "Capacidade de ler e interpretar uma obra de arte",
            "Juízo estético fundamentado: saber dizer por que uma obra é boa",
            "Compreensão do belo (<em>pulchrum</em>) em sua unidade com o verdadeiro e o bom",
        ],
    ),
)

PAGES["curriculo-musica-teatro.html"] = dict(
    title=f"Música e Teatro — Currículo — {SCHOOL}",
    description="Música e Teatro como disciplinas regulares: coral, teoria musical, dicção e montagem anual.",
    body=subject_page(
        "Música e Teatro", "Artes performáticas",
        "Duas disciplinas que se apoiam mutuamente: a escuta e a voz, o ritmo e a presença, a técnica e a coragem.",
        [
            "Música e Teatro caminham juntos no currículo do Rosário porque compartilham o essencial: "
            "exigem escuta, disciplina de ensaio, domínio do corpo e da voz, e a coragem de se "
            "apresentar diante dos outros.",
            "Em Música, todos os alunos passam pelo canto coral e pela teoria musical — leitura de "
            "partitura, solfejo e percepção rítmica. O coral do Colégio canta nas celebrações "
            "litúrgicas e nas festas do calendário escolar.",
            "Em Teatro, o trabalho começa com jogos de expressão e dicção no Fundamental I e chega, "
            "no Fundamental II, à montagem de um espetáculo anual com texto integral — frequentemente "
            "um clássico adaptado. Todo aluno participa: no palco, na cenografia ou na produção.",
        ],
        [
            ("A", "Canto coral", "Todos os alunos cantam. Coral estruturado por vozes a partir do 5º ano."),
            ("B", "Teoria musical", "Leitura de partitura, solfejo e percepção rítmica desde o Fundamental I."),
            ("C", "Montagem anual", "Espetáculo de fim de ano com texto integral, aberto às famílias."),
        ],
        [("Educação Infantil — Música", "2 aulas"), ("Fundamental I — Música / Teatro", "2 + 1 aulas"), ("Fundamental II — Música ou Teatro", "2 aulas")],
        [
            "Leitura de partitura e percepção rítmica e melódica",
            "Canto afinado em conjunto, com noção de naipe",
            "Dicção, projeção vocal e presença cênica",
            "Memorização e interpretação de texto dramático",
            "Trabalho em equipe sob a disciplina do ensaio",
        ],
    ),
)


# ---- Cursos Extras -------------------------------------------------------
PAGES["cursos-musica.html"] = dict(
    title=f"Curso de Música — {SCHOOL}",
    description="Curso extracurricular de Música: piano, violino, violão, canto e teoria musical.",
    body=page_hero(
        "Curso de Música",
        "Formação musical aprofundada no contraturno — aberta aos alunos do Colégio e à comunidade.",
        '<a href="cursos-musica.html">Cursos Extras</a> &nbsp;/&nbsp; Música',
    )
    + section(
        text_block(
            [
                "Criado em 2025, o Curso de Música do Rosário oferece formação instrumental e vocal "
                "estruturada, do primeiro contato ao nível preparatório para conservatório.",
                "As aulas de instrumento são individuais, com 50 minutos semanais, complementadas por "
                "aulas coletivas de teoria musical e por prática de conjunto. É essa combinação — "
                "técnica individual e música feita junto — que forma o músico completo.",
                "O curso é aberto também a alunos que não estudam no Colégio e a adultos, em horários "
                "de fim de tarde.",
            ],
            "Contraturno · Desde 2025",
            "Um curso, não uma atividade",
        )
    )
    + section(
        intro("Modalidades", "O que oferecemos", "")
        + f'<div style="margin-top:3rem">'
        + cards(
            [
                ("♪", "Piano", "Aulas individuais com repertório erudito progressivo. A partir dos 6 anos."),
                ("♪", "Violino", "Método Suzuki nos primeiros anos, com transição para leitura tradicional."),
                ("♪", "Violão", "Erudito e popular, com ênfase em leitura e harmonia. A partir dos 8 anos."),
                ("♪", "Canto", "Técnica vocal individual e canto coral. A partir dos 10 anos."),
                ("♪", "Teoria Musical", "Solfejo, percepção e harmonia, em turmas coletivas por nível."),
                ("♪", "Prática de Conjunto", "Câmara e conjunto instrumental, com apresentações semestrais."),
            ]
        )
        + "</div>",
        "section--cream",
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">Organização</p><h2>Como funciona</h2><hr class="rule">'
        '<ul class="list-gold">'
        "<li><strong>Aula de instrumento:</strong> individual, 50 min semanais</li>"
        "<li><strong>Teoria musical:</strong> coletiva, 50 min semanais, por nível</li>"
        "<li><strong>Prática de conjunto:</strong> quinzenal, a partir do nível intermediário</li>"
        "<li><strong>Horários:</strong> de segunda a sexta, das 13h30 às 19h</li>"
        "<li><strong>Avaliação:</strong> audição semestral aberta às famílias</li>"
        "<li><strong>Instrumento próprio:</strong> necessário a partir do segundo semestre</li>"
        "</ul>"
        '<p style="margin-top:1.6rem"><a class="btn btn--navy" href="contato.html">Consultar vagas e valores</a></p></div>'
        '<div class="panel reveal"><h3>Calendário de apresentações</h3><ul>'
        "<li><strong>Maio</strong> — Audição de alunos iniciantes</li>"
        "<li><strong>Junho</strong> — Concerto de meio de ano no auditório</li>"
        "<li><strong>Outubro</strong> — Recital de câmara</li>"
        "<li><strong>Dezembro</strong> — Concerto de Natal, com coral e conjunto instrumental</li>"
        "</ul></div></div>"
    )
    + CTA,
)

PAGES["cursos-ballet.html"] = dict(
    title=f"Ballet — {SCHOOL}",
    description="Curso de Ballet clássico com método Royal Academy of Dance, do baby class ao intermediário.",
    body=page_hero(
        "Ballet",
        "Ballet clássico no contraturno, com método Royal Academy of Dance e apresentação anual em teatro.",
        '<a href="cursos-musica.html">Cursos Extras</a> &nbsp;/&nbsp; Ballet',
    )
    + section(
        text_block(
            [
                "O Ballet chegou ao Rosário em 2025 e rapidamente se tornou um dos programas mais "
                "procurados do Colégio. A razão é simples: é ballet de verdade, com método reconhecido, "
                "professoras certificadas e exigência técnica adequada a cada idade.",
                "Seguimos o método da Royal Academy of Dance, com progressão por níveis e possibilidade "
                "de exame oficial. Mas o objetivo não é formar bailarinas profissionais — é oferecer "
                "postura, disciplina, musicalidade e consciência corporal a quem quiser.",
                "As aulas acontecem em sala própria, com barras, espelhos e piso adequado, no "
                "contraturno escolar.",
            ],
            "Contraturno · Royal Academy of Dance",
            "Técnica, postura e disciplina",
        )
    )
    + section(
        intro("Níveis", "Turmas por faixa etária", "")
        + '<div class="table-wrap reveal" style="margin-top:2.6rem">'
        "<table><thead><tr><th>Turma</th><th>Idade</th><th>Frequência</th></tr></thead><tbody>"
        + "".join(
            f"<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td></tr>"
            for a, b, c in [
                ("Baby Class", "4 e 5 anos", "1x por semana, 45 min"),
                ("Pre-Primary", "6 e 7 anos", "1x por semana, 60 min"),
                ("Primary", "8 e 9 anos", "2x por semana, 60 min"),
                ("Grade 1 e 2", "10 a 12 anos", "2x por semana, 75 min"),
                ("Grade 3 e 4 — Intermediário", "13 anos ou mais", "3x por semana, 90 min"),
            ]
        )
        + "</tbody></table></div>",
        "section--cream",
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">O que a aluna desenvolve</p><h2>Muito além dos passos</h2><hr class="rule">'
        '<ul class="list-gold">'
        "<li>Postura, alinhamento e consciência corporal</li>"
        "<li>Musicalidade e senso de ritmo</li>"
        "<li>Disciplina de ensaio e persistência</li>"
        "<li>Memória de sequência e coordenação</li>"
        "<li>Confiança para se apresentar em público</li>"
        "</ul></div>"
        '<div class="panel reveal"><h3>Informações práticas</h3><ul>'
        "<li><strong>Uniforme:</strong> collant, meia-calça e sapatilha adquiridos no Colégio</li>"
        "<li><strong>Sapatilha de ponta:</strong> avaliada individualmente, a partir do Grade 3</li>"
        "<li><strong>Exames RAD:</strong> opcionais, aplicados anualmente</li>"
        "<li><strong>Espetáculo:</strong> apresentação anual em teatro, em novembro</li>"
        "<li><strong>Inscrições:</strong> abertas o ano todo, conforme vagas</li>"
        "</ul></div></div>"
    )
    + CTA,
)

# ---- Admissão ------------------------------------------------------------
PAGES["admissao.html"] = dict(
    title=f"Admissão — Matrículas 2027 — {SCHOOL}",
    description="Processo de admissão 2027: etapas, documentos, calendário e agendamento de visita.",
    body=page_hero(
        "Admissão",
        "Matrículas abertas para 2027. Conheça as etapas do processo e agende sua visita ao Colégio.",
        "Admissão",
    )
    + section(
        intro(
            "Processo",
            "Quatro etapas, sem mistério",
            "Nosso processo é feito para que a família conheça o Colégio tão bem quanto o Colégio conhece a família. "
            "Não há prova classificatória na Educação Infantil e no Fundamental I.",
        )
        + f'<div style="margin-top:3.2rem">'
        + cards(
            [
                ("1", "Visita agendada", "A família conhece as instalações, conversa com a coordenação da etapa e assiste a parte de uma aula."),
                ("2", "Entrevista", "Encontro com a Direção para alinhar expectativas, proposta pedagógica e compromissos mútuos."),
                ("3", "Avaliação diagnóstica", "Sem caráter eliminatório até o 5º ano. Do 6º ao 9º, avaliação de Português e Matemática."),
                ("4", "Matrícula", "Entrega de documentos, assinatura do contrato e reunião de acolhida antes do início das aulas."),
            ],
            4,
        )
        + "</div>"
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">Documentação</p><h2>O que trazer na matrícula</h2><hr class="rule">'
        '<ul class="list-gold">'
        "<li>Certidão de nascimento do aluno (cópia)</li>"
        "<li>RG e CPF dos responsáveis</li>"
        "<li>Comprovante de residência atualizado</li>"
        "<li>Histórico escolar ou declaração de transferência</li>"
        "<li>Carteira de vacinação (Educação Infantil e Fundamental I)</li>"
        "<li>Duas fotos 3x4 recentes</li>"
        "<li>Laudos ou relatórios, quando houver acompanhamento especializado</li>"
        "</ul></div>"
        '<div class="panel reveal"><h3>Calendário 2026/2027</h3><ul>'
        "<li><strong>Agosto</strong> — Abertura das visitas agendadas</li>"
        "<li><strong>Setembro</strong> — Rematrícula de alunos veteranos</li>"
        "<li><strong>Outubro</strong> — Início das matrículas de novos alunos</li>"
        "<li><strong>Novembro</strong> — Avaliações diagnósticas do Fundamental II</li>"
        "<li><strong>Janeiro</strong> — Reunião de acolhida das novas famílias</li>"
        "<li><strong>Fevereiro</strong> — Início do ano letivo</li>"
        "</ul></div></div>",
        "section--cream",
    )
    + section(
        intro("Dúvidas frequentes", "Antes de agendar", "")
        + '<div style="max-width:74ch;margin:3rem auto 0">'
        + "".join(
            f'<div class="acc reveal"><button class="acc-head" type="button" aria-expanded="false">{q}</button>'
            f'<div class="acc-body"><p>{a}</p></div></div>'
            for q, a in [
                ("Há vagas em todas as séries?",
                 "As vagas variam a cada ano. A Educação Infantil e o 1º ano costumam ter maior disponibilidade; "
                 "nas demais séries, a abertura depende de transferências. Consulte a Secretaria para a situação atual."),
                ("É obrigatório ser católico para estudar no Colégio?",
                 "Não. Recebemos famílias de todas as convicções. Pedimos apenas que conheçam e respeitem a "
                 "identidade católica da instituição, que se expressa na oração diária, nas celebrações e na "
                 "disciplina de Formação Católica, obrigatória para todos os alunos."),
                ("Como funcionam as mensalidades e descontos?",
                 "Os valores são divulgados anualmente em setembro. Oferecemos desconto para irmãos matriculados "
                 "e para pagamento antecipado do ano letivo. A Secretaria envia a tabela completa mediante solicitação."),
                ("Os cursos extras estão incluídos na mensalidade?",
                 "Não. Música e Ballet são cursos com matrícula e mensalidade próprias, abertos também a alunos "
                 "externos. Alunos do Colégio têm desconto."),
                ("Meu filho vem de outra escola. Ele vai acompanhar?",
                 "Na maior parte dos casos, sim — mas somos honestos sobre eventuais defasagens. A avaliação "
                 "diagnóstica serve justamente para mapeá-las e, quando necessário, oferecer plano de nivelamento "
                 "no primeiro semestre."),
            ]
        )
        + "</div>"
    )
    + section(
        '<div class="center reveal"><h2 style="color:var(--gold-200)">Agende sua visita</h2><hr class="rule">'
        '<p class="lede">Visitas de segunda a sexta, às 9h e às 14h, com hora marcada. '
        "Toda visita é conduzida pela coordenação da etapa de interesse.</p>"
        '<p style="margin-top:1.8rem"><a class="btn btn--gold" href="contato.html">Formulário de contato</a>'
        '<a class="btn btn--ghost" href="https://wa.me/__WA__" target="_blank" rel="noopener" style="margin-left:.6rem">WhatsApp da Secretaria</a></p></div>',
        "section--navy",
    ),
)

# ---- Contato -------------------------------------------------------------
PAGES["contato.html"] = dict(
    title=f"Contato — {SCHOOL}",
    description="Fale com a Secretaria do Colégio Nossa Senhora do Rosário: endereço, telefone, e-mail e formulário.",
    body=page_hero(
        "Contato",
        "Fale com a Secretaria, agende uma visita ou solicite informações sobre matrículas e cursos extras.",
        "Contato",
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">Envie uma mensagem</p><h2>Como podemos ajudar?</h2><hr class="rule">'
        '<form class="form" data-form data-whatsapp="__WA__" novalidate>'
        '<div class="row">'
        '<div><label for="nome">Nome completo</label><input id="nome" name="nome" type="text" required></div>'
        '<div><label for="email">E-mail</label><input id="email" name="email" type="email" required></div>'
        "</div>"
        '<div class="row">'
        '<div><label for="tel">Telefone</label><input id="tel" name="telefone" type="tel"></div>'
        '<div><label for="assunto">Assunto</label><select id="assunto" name="assunto">'
        "<option>Matrícula e admissão</option><option>Agendar visita</option>"
        "<option>Curso de Música</option><option>Ballet</option>"
        "<option>Regimento e documentos</option><option>Outro assunto</option>"
        "</select></div>"
        "</div>"
        '<div><label for="msg">Mensagem</label><textarea id="msg" name="mensagem" rows="5" required></textarea></div>'
        '<div><button class="btn btn--gold" type="submit">Enviar pelo WhatsApp</button></div>'
        '<p class="form-note">Ao enviar, abrimos o WhatsApp da Secretaria (__WA_FMT__) com os dados acima já organizados na mensagem — basta confirmar o envio.</p>'
        '<p class="form-feedback form-note" role="status" aria-live="polite"></p>'
        "</form></div>"
        '<div class="panel reveal"><h3>Secretaria</h3><ul>'
        "<li><strong>Endereço:</strong> __END_RUA__</li>"
        "<li>__END_BAIRRO__ · __END_CIDADE__ · __END_CEP__</li>"
        "<li><strong>WhatsApp:</strong> <a class=\"link-contato\" href=\"https://wa.me/__WA__\" target=\"_blank\" rel=\"noopener\">__WA_FMT__</a></li>"
        "<li><strong>E-mail:</strong> <a class=\"link-contato\" href=\"mailto:__EMAIL__\">__EMAIL__</a></li>"
        "<li><strong>Atendimento:</strong> seg. a sex., 7h30 às 17h30</li>"
        "<li><strong>CNPJ:</strong> __CNPJ__</li>"
        "</ul>"
        '<h3 style="margin-top:2rem">Visitas</h3><ul>'
        "<li>Segundas a sextas, às 9h e às 14h</li>"
        "<li>Sempre com agendamento prévio</li>"
        "<li>Duração aproximada de 1 hora</li>"
        "</ul></div></div>"
    )
    + section(
        '<div class="center reveal"><p class="eyebrow">Localização</p><h2>Onde estamos</h2><hr class="rule">'
        '<p class="lede">__END_RUA__ · __END_BAIRRO__<br>__END_CIDADE__ · __END_CEP__</p>'
        '<div style="margin-top:2.4rem;border:1px solid rgba(201,162,39,.35);border-radius:4px;overflow:hidden">'
        '<iframe title="Mapa da localização do Colégio" width="100%" height="380" style="border:0;display:block"'
        ' loading="lazy" referrerpolicy="no-referrer-when-downgrade"'
        ' src="https://www.google.com/maps?q=__END_MAPA__&output=embed"></iframe>'
        "</div></div>",
        "section--cream",
    ),
)


PAGES["curriculo-matematica.html"] = dict(
    title=f"Matemática — Currículo — {SCHOOL}",
    description="Matemática clássica: cálculo mental, desenho geométrico com régua e compasso, "
    "a geometria de Euclides e o paralelo entre demonstração matemática e raciocínio lógico.",
    body=subject_page(
        "Matemática", "Raciocínio e demonstração",
        "Da tabuada automatizada à demonstração euclidiana — a matemática ensinada como treino do "
        "raciocínio, não como coleção de fórmulas a decorar.",
        [
            "No currículo clássico, a Matemática nunca foi uma disciplina técnica isolada. Ela "
            "integrava o quadrivium justamente por ser o lugar onde o aluno aprende a demonstrar: "
            "a partir de poucos princípios evidentes, chegar por passos necessários a uma conclusão "
            "que não se pode recusar.",
            "Por isso o trabalho começa pelo domínio operatório — cálculo mental diário, tabuada "
            "automatizada, frações e proporções com segurança — mas não termina nele. A partir do "
            "Fundamental II, o aluno passa a trabalhar com a geometria de Euclides, acompanhando as "
            "proposições dos <em>Elementos</em>: enunciado, construção, demonstração, conclusão.",
            "Ao lado disso vem o desenho geométrico, feito à mão com régua e compasso. Construir uma "
            "mediatriz ou bissetar um ângulo com instrumentos não é exercício decorativo: é a "
            "verificação concreta de que a demonstração funciona, e é o que fixa no aluno a diferença "
            "entre desenhar algo que <em>parece</em> certo e construir algo que <em>é</em> certo.",
        ],
        [
            ("A", "Desenho geométrico", "Régua e compasso, à mão: mediatriz, bissetriz, polígonos regulares, "
                  "divisão de segmentos. Construção sem medida aproximada."),
            ("B", "Euclides", "Leitura e reconstrução das proposições dos <em>Elementos</em>, na ordem em que "
                  "foram escritas — do postulado à conclusão."),
            ("C", "Paralelo lógico", "A demonstração geométrica e o silogismo têm a mesma estrutura. O aluno "
                  "percebe isso e leva o raciocínio para as outras disciplinas."),
        ],
        [("Fundamental I", "6 aulas"), ("Fundamental II", "6 aulas"), ("Fundamental II — Desenho Geométrico", "1 aula")],
        [
            "Cálculo mental seguro e tabuada automatizada",
            "Domínio de frações, proporções, álgebra elementar e equações",
            "Construções geométricas exatas com régua e compasso",
            "Leitura e reconstrução de demonstrações de Euclides",
            "Reconhecimento da estrutura lógica comum à demonstração e ao silogismo",
            "Capacidade de distinguir o que foi provado do que apenas parece verdadeiro",
        ],
    ),
)


PAGES["curriculo-pre-alfabetizacao.html"] = dict(
    title=f"Pré-alfabetização — Currículo — {SCHOOL}",
    description="Pré-alfabetização na Educação Infantil: consciência fonológica, rimas, sílabas e "
    "fonemas — a base sonora que sustenta a alfabetização pelo método fônico.",
    body=subject_page(
        "Pré-alfabetização", "Educação Infantil",
        "Antes da letra vem o som. A criança aprende a ouvir a língua por dentro — e chega à "
        "alfabetização com o trabalho mais difícil já feito.",
        [
            "Alfabetizar não começa no 1º ano, começa no ouvido. Antes de associar um símbolo a um "
            "som, a criança precisa perceber que a palavra falada é feita de partes — que "
            "<em>casa</em> rima com <em>asa</em>, que <em>bola</em> começa com o mesmo som de "
            "<em>bota</em>, que <em>pato</em> tem duas sílabas e quatro sons.",
            "Isso se chama consciência fonológica, e é o melhor previsor conhecido do sucesso na "
            "alfabetização. Não se desenvolve sozinho: exige trabalho sistemático, diário e "
            "cuidadosamente graduado — das unidades maiores para as menores, da rima à sílaba, da "
            "sílaba ao fonema.",
            "Na Educação Infantil do Rosário isso é feito por meio de jogos, parlendas, cantigas e "
            "brincadeiras orais — sempre com propósito e progressão claros por trás. Não antecipamos "
            "a alfabetização formal nem transformamos o Infantil em Fundamental precoce: preparamos "
            "o terreno para que, no 1º ano, o método fônico encontre uma criança já capaz de ouvir "
            "aquilo que vai aprender a escrever.",
        ],
        [
            ("A", "Da rima ao fonema", "Progressão explícita: rima e aliteração, depois sílabas, depois os "
                  "sons individuais — nessa ordem, sem pular etapas."),
            ("B", "Oralidade e vocabulário", "Contação de histórias diária, roda de conversa e parlendas: "
                  "ninguém escreve bem uma língua que ouve pouco."),
            ("C", "Traçado e motricidade", "Coordenação fina, orientação espacial e o gesto do traçado, "
                  "preparando a escrita à mão."),
        ],
        [("Infantil III (3 anos)", "5 aulas"), ("Infantil IV (4 anos)", "6 aulas"), ("Infantil V (5 anos)", "8 aulas")],
        [
            "Identificação de rimas e aliterações em palavras faladas",
            "Segmentação de palavras em sílabas e contagem sonora",
            "Isolamento do som inicial e final das palavras",
            "Associação segura entre som e letra ao final do Infantil V",
            "Vocabulário oral amplo, construído por histórias e conversa",
            "Coordenação motora fina suficiente para o traçado das letras",
        ],
    ),
)

PAGES["curriculo-literatura-estrangeira.html"] = dict(
    title=f"Literatura Estrangeira — Currículo — {SCHOOL}",
    description="Literatura estrangeira no currículo: obras integrais das tradições inglesa, "
    "francesa e greco-latina, lidas em tradução e, progressivamente, no original.",
    body=subject_page(
        "Literatura Estrangeira", "Leitura de obras integrais",
        "As grandes obras que formaram o Ocidente, lidas por inteiro — em tradução no início, no "
        "original sempre que o aluno já puder.",
        [
            "Estudar uma língua estrangeira sem chegar à sua literatura é parar no meio do caminho. "
            "O aluno que aprende inglês apenas para pedir informação num aeroporto tem uma "
            "ferramenta; o que lê Dickens tem acesso a um mundo.",
            "Por isso a literatura estrangeira é tratada aqui como disciplina própria, e não como "
            "apêndice das aulas de idioma. Lemos obras integrais — nunca resumos, nunca fragmentos "
            "de apostila — em edições adaptadas ao nível quando necessário, e no original assim que "
            "a proficiência permite.",
            "O percurso acompanha as raízes: a épica grega e a poesia latina, que o aluno reencontra "
            "no Latim; a tradição inglesa, de Shakespeare aos vitorianos; a francesa, de La Fontaine "
            "a Saint-Exupéry. O objetivo não é cobrir um catálogo, mas ler bem um número pequeno de "
            "livros grandes.",
        ],
        [
            ("A", "Obras integrais", "O livro inteiro, do começo ao fim. Adaptações só quando o nível "
                  "linguístico ainda exige."),
            ("B", "Do traduzido ao original", "A mesma obra pode voltar anos depois, agora na língua em "
                  "que foi escrita."),
            ("C", "Discussão em aula", "Leitura acompanhada, com discussão dirigida e escrita sobre o texto — "
                  "não questionário de interpretação."),
        ],
        [("Fundamental I", "1 aula"), ("Fundamental II", "2 aulas"), ("Fundamental II — leitura dirigida", "1 aula")],
        [
            "Hábito de ler obras completas, com fôlego para textos longos",
            "Repertório das tradições grega, latina, inglesa e francesa",
            "Leitura de textos literários no original em inglês e francês",
            "Capacidade de discutir uma obra com referência ao texto, não a impressões",
            "Escrita analítica sobre literatura",
        ],
    ),
)

PAGES["curriculo-filosofia.html"] = dict(
    title=f"Filosofia Clássica — Currículo — {SCHOOL}",
    description="Filosofia clássica no Fundamental II: lógica, ética e metafísica na tradição "
    "aristotélica e tomista, com leitura de fontes e prática de argumentação.",
    body=subject_page(
        "Filosofia Clássica", "Tradição aristotélica e tomista",
        "Aristóteles e Tomás de Aquino ao alcance de um aluno do Fundamental II — não como história "
        "das ideias, mas como exercício de pensar com ordem.",
        [
            "A filosofia entra no currículo porque é ela que dá unidade ao resto. Depois de anos "
            "aprendendo a demonstrar em Matemática, a analisar em Latim e a argumentar por escrito em "
            "Português, o aluno encontra na lógica aristotélica o nome e a estrutura daquilo que já "
            "vinha fazendo.",
            "Começamos pela lógica: termo, proposição e silogismo; as formas válidas e as falácias "
            "mais comuns. É a parte mais concreta e a mais imediatamente útil — o aluno passa a "
            "reconhecer um raciocínio quebrado, inclusive nos próprios textos.",
            "Em seguida vêm as noções de ética e de metafísica, sempre a partir de fontes lidas "
            "diretamente, em trechos escolhidos e comentados: as quatro causas, a distinção entre "
            "ato e potência, a virtude como hábito, o bem como fim da ação. Tomás de Aquino entra "
            "sobretudo pela forma da <em>quaestio</em> — objeções, resposta, réplicas —, que é ao "
            "mesmo tempo um método de estudo e uma escola de honestidade intelectual: ninguém "
            "responde a uma tese sem antes formulá-la em sua versão mais forte.",
        ],
        [
            ("A", "Lógica", "Termo, proposição e silogismo; formas válidas; identificação das falácias "
                  "mais frequentes."),
            ("B", "Leitura de fontes", "Trechos de Aristóteles e de Tomás de Aquino lidos e comentados em "
                  "aula, não resumos sobre eles."),
            ("C", "Disputatio", "A quaestio tomista como exercício: formular a objeção mais forte antes de "
                  "responder a ela."),
        ],
        [("8º ano", "1 aula"), ("9º ano", "2 aulas"), ("9º ano — seminário de leitura", "1 aula")],
        [
            "Domínio das formas básicas do silogismo e reconhecimento de falácias",
            "Vocabulário filosófico preciso: causa, ato, potência, essência, virtude",
            "Leitura de trechos de Aristóteles e de Tomás de Aquino com compreensão",
            "Capacidade de expor uma posição contrária antes de refutá-la",
            "Argumentação escrita ordenada, com premissas explícitas",
            "Percepção da unidade entre as disciplinas do currículo",
        ],
    ),
)


# --------------------------------------------------------------------------
# Oficinas — trabalho manual dentro do currículo
# --------------------------------------------------------------------------
OFICINAS = [
    ("Pintura a óleo",
     "A técnica clássica da pintura ocidental. Preparação da tela, camadas, mistura de pigmentos e "
     "— sobretudo — o tempo de secagem, que impede qualquer pressa. Natureza-morta e estudo de luz."),
    ("Pintura em aquarela",
     "O oposto do óleo: a água não permite correção. Cada gesto é definitivo e o branco do papel é a "
     "única luz disponível. Ensina decisão e economia de meios."),
    ("Marcenaria",
     "Medir, marcar, serrar, encaixar e lixar, com ferramentas manuais. A madeira não perdoa erro de "
     "medida — e é justamente isso que a torna uma boa professora."),
    ("Corte e costura",
     "Do molde ao acabamento: tirar medidas, riscar o tecido, cortar, alinhavar e costurar à mão e à "
     "máquina, até a peça ficar pronta para vestir."),
    ("Agricultura",
     "A horta do Colégio. Preparo do solo, semeadura, rega, capina e colheita, acompanhando o ciclo "
     "inteiro. A única oficina em que o resultado depende de saber esperar."),
    ("Tipografia",
     "Composição com tipos móveis e impressão manual. A palavra vira objeto físico, letra por letra "
     "— e o aluno descobre por que se diz caixa-alta e caixa-baixa."),
    ("Escultura",
     "Modelagem em argila e talhe em materiais macios. Passar do desenho, que é plano, para o volume, "
     "que só se resolve girando a peça e olhando de todos os lados."),
]

_oficinas_linhas = "".join(
    f"<tr><td><strong>{nome}</strong></td><td>{desc}</td></tr>" for nome, desc in OFICINAS
)

_oficinas_pilares = cards([
    ("I", "Encontro com a matéria",
     "A madeira, a argila e o tecido impõem limites que não se negociam. Uma medida errada aparece "
     "na hora, sem intermediários."),
    ("II", "Paciência e ordem",
     "Preparar o material, respeitar o tempo de secagem, guardar a ferramenta limpa. A oficina tem "
     "um método, e ele é parte do que se ensina."),
    ("III", "A obra terminada",
     "Levar uma peça do início ao fim e mostrá-la pronta. É a experiência de ter feito algo que "
     "existe fora de si."),
])

PAGES["curriculo-oficinas.html"] = dict(
    title=f"Oficinas — Currículo — {SCHOOL}",
    description="Oficinas de trabalho manual no currículo: pintura a óleo e aquarela, marcenaria, "
    "corte e costura, agricultura, tipografia e escultura.",
    body=page_hero(
        "Oficinas",
        "Trabalho manual como parte do currículo — porque a inteligência que só opera no abstrato "
        "fica pela metade.",
        '<a href="curriculo-pre-alfabetizacao.html">Currículo</a> &nbsp;/&nbsp; Oficinas',
    )
    + section(
        text_block(
            [
                "Uma escola clássica que ensinasse apenas a ler, calcular e argumentar formaria "
                "alunos pela metade. A tradição que herdamos nunca separou a mão da inteligência: o "
                "mesmo monge que copiava manuscritos cuidava da horta, e as artes liberais conviviam "
                "com as artes mecânicas sem que ninguém achasse aquilo estranho.",
                "O trabalho manual ensina o que nenhuma prova ensina. A matéria resiste — a madeira "
                "racha, a tinta escorre, a semente não germina antes da hora — e essa resistência é "
                "uma forma de verdade objetiva com que a criança precisa se encontrar. Não adianta "
                "argumentar bem com uma tábua mal medida.",
                "Ensina também a terminar. Uma peça de marcenaria, uma camisa costurada ou uma "
                "gravura impressa ou está pronta ou não está; não existe entregar pela metade e "
                "receber nota parcial. O aluno aprende a levar uma obra até o fim e a assumi-la "
                "diante dos outros — o que forma o caráter tanto quanto uma aula sobre virtude.",
                "E devolve dignidade ao fazer com as mãos, numa cultura que aprendeu a tratá-lo como "
                "destino de quem não estudou. Aqui, o aluno que traduz Latim é o mesmo que lixa uma "
                "tábua — e não há hierarquia entre as duas coisas.",
            ],
            "Por que oficinas",
            "A mão que pensa",
        )
    )
    + section(
        intro("O que o trabalho manual forma", "Três coisas que a sala de aula não dá", "")
        + '<div style="margin-top:3rem">' + _oficinas_pilares + "</div>",
        "section--cream",
    )
    + section(
        intro("As oficinas", "O que oferecemos",
              "Cada aluno passa por todas ao longo do percurso, em rodízio, e aprofunda-se naquelas "
              "com que tiver mais afinidade.")
        + '<div class="table-wrap reveal" style="margin-top:2.6rem">'
        "<table><thead><tr><th>Oficina</th><th>O que se faz</th></tr></thead><tbody>"
        + _oficinas_linhas
        + "</tbody></table></div>"
    )
    + section(
        '<div class="split">'
        '<div class="reveal"><p class="eyebrow">Organização</p><h2>Como funcionam</h2><hr class="rule">'
        '<ul class="list-gold">'
        "<li><strong>Rodízio bimestral:</strong> a turma passa por uma oficina diferente a cada bimestre</li>"
        "<li><strong>Turmas divididas:</strong> metade da turma por vez, para o professor acompanhar cada aluno</li>"
        "<li><strong>Ferramenta de verdade:</strong> instrumentos reais, com instrução de segurança antes do uso</li>"
        "<li><strong>Material incluído:</strong> fornecido pelo Colégio, sem custo adicional</li>"
        "<li><strong>Mostra anual:</strong> as peças produzidas são expostas às famílias no fim do ano</li>"
        "</ul></div>"
        '<div class="panel reveal"><h3>Carga horária semanal</h3>'
        '<div class="table-wrap"><table><thead><tr><th>Etapa</th><th>Aulas</th></tr></thead><tbody>'
        "<tr><td>Educação Infantil</td><td>1 aula</td></tr>"
        "<tr><td>Fundamental I</td><td>2 aulas</td></tr>"
        "<tr><td>Fundamental II</td><td>2 aulas</td></tr>"
        "</tbody></table></div>"
        '<p style="margin-top:1.4rem;font-size:.92rem">Na Educação Infantil as oficinas são adaptadas: '
        "modelagem, pintura e horta, sem ferramenta cortante.</p></div></div>",
        "section--cream",
    )
    + CTA,
)


PAGES["curriculo-educacao-fisica.html"] = dict(
    title=f"Educação Física — Currículo — {SCHOOL}",
    description="Educação Física como parte da formação integral: ginástica, jogo e esporte "
    "coletivo formando o corpo, a vontade e o caráter.",
    body=subject_page(
        "Educação Física", "Formação integral",
        "O corpo não é acessório da pessoa. Educá-lo com método é parte de formar o aluno inteiro — "
        "inteligência, vontade, caráter e corpo.",
        [
            "A educação clássica sempre soube que não se forma a alma ignorando o corpo. Na paideia "
            "grega, a ginástica e a música caminhavam juntas: uma sem a outra produzia ou o rude ou "
            "o mole. Nossa Educação Física parte dessa mesma convicção — e não da ideia de que a "
            "aula seja o intervalo entre as matérias sérias.",
            "Formação integral, aqui, tem sentido preciso: o que o aluno aprende no pátio é da mesma "
            "natureza do que aprende na sala. A criança que sustenta um esforço até o fim está "
            "exercitando a mesma fortaleza que a faz terminar uma lista de exercícios difícil. A que "
            "aceita a regra do jogo quando ela a desfavorece está aprendendo justiça de um modo que "
            "nenhuma aula expositiva alcança.",
            "Por isso o trabalho é progressivo e tem conteúdo. Começa pela motricidade ampla e pelos "
            "jogos tradicionais na Educação Infantil, passa à ginástica formal e à iniciação "
            "esportiva no Fundamental I e chega, no Fundamental II, à prática regular de esportes "
            "coletivos, com regra, arbitragem e competição interna.",
            "E há o simples: criança precisa correr. Num tempo em que a infância se tornou sedentária "
            "e mediada por telas, garantir movimento diário ao ar livre é uma decisão pedagógica — "
            "e também de saúde.",
        ],
        [
            ("A", "Ginástica e motricidade", "Coordenação, equilíbrio, postura e consciência corporal, "
                  "trabalhados com progressão do Infantil ao 9º ano."),
            ("B", "Jogo e esporte coletivo", "Dos jogos tradicionais à prática regular de esportes com "
                  "regra, posição e função dentro de uma equipe."),
            ("C", "Virtudes do corpo", "Fortaleza para sustentar o esforço, temperança para conhecer o "
                  "próprio limite, justiça para aceitar a regra."),
        ],
        [("Educação Infantil", "3 aulas"), ("Fundamental I", "2 aulas"), ("Fundamental II", "2 aulas")],
        [
            "Coordenação motora, equilíbrio e postura adequados à idade",
            "Domínio dos fundamentos dos principais esportes coletivos",
            "Hábito de esforço físico regular e prazer no movimento",
            "Cooperação: saber jogar com quem se tem, não com quem se queria ter",
            "Aceitação da regra e da derrota sem ressentimento",
            "Noções de higiene, alimentação e cuidado com o próprio corpo",
        ],
    ),
)

PAGES["curriculo-cortesia-civilidade.html"] = dict(
    title=f"Cortesia e Civilidade — Currículo — {SCHOOL}",
    description="Cortesia e civilidade no currículo: como se expressar, como tratar os pais, os "
    "mais velhos, os professores e os colegas — formação diária de convivência.",
    body=subject_page(
        "Cortesia e Civilidade", "Formação do dia a dia",
        "Aprender a falar com as pessoas, a tratar os pais, os mais velhos, os professores e os "
        "colegas. A caridade nas pequenas coisas — praticada todo dia, até virar segunda natureza.",
        [
            "Cortesia não é verniz social nem afetação. É a forma visível do respeito: o modo como "
            "reconheço, em gestos pequenos e repetidos, que a pessoa diante de mim tem uma dignidade "
            "que não depende do que eu sinta por ela naquele momento. Por isso a tratamos como "
            "matéria de formação, e não como assunto de boas maneiras.",
            "O trabalho começa pela expressão. O aluno aprende a olhar nos olhos ao falar, a "
            "cumprimentar quem chega, a pedir licença antes de interromper, a agradecer de modo "
            "audível, a pedir desculpa sem constrangimento e a dizer o que pensa com clareza e sem "
            "agressão. Quem não sabe se expressar acaba se impondo ou se calando — e nenhuma das duas "
            "coisas serve.",
            "Depois vem o trato com cada um. Com os <strong>pais</strong>, a obediência e a gratidão "
            "que se traduzem em gestos concretos: atender ao ser chamado, ajudar sem que precisem "
            "pedir duas vezes, agradecer o que se recebe. Com os <strong>mais velhos</strong>, a "
            "deferência devida a quem já percorreu o caminho: ceder o lugar, ouvir sem interromper, "
            "tratar por senhor e senhora. Com os <strong>professores</strong>, o respeito que torna "
            "possível aprender: pontualidade, atenção, dirigir-se com correção e reconhecer a "
            "autoridade de quem ensina.",
            "E há o trato <strong>entre si</strong>, que é o mais difícil e o mais decisivo. É entre "
            "colegas que se aprende a discordar sem ofender, a não excluir quem está sozinho, a não "
            "rir do erro alheio, a defender quem está sendo tratado injustamente e a pedir perdão "
            "quando se erra. Uma turma em que isso é cultivado dia após dia é um lugar onde se estuda "
            "melhor — e onde nenhuma criança tem medo de chegar.",
            "Nada disso se ensina em uma aula por semana e se esquece nas outras vinte. A civilidade "
            "é cobrada e praticada o tempo inteiro: na entrada, no corredor, no refeitório, na saída. "
            "O momento semanal reservado serve para dar nome ao que se pratica e para tratar das "
            "situações concretas que apareceram na convivência.",
        ],
        [
            ("A", "Saber se expressar", "Olhar nos olhos, cumprimentar, pedir licença, agradecer, pedir "
                  "desculpa e discordar com clareza — sem agressão nem timidez."),
            ("B", "O trato com cada um", "Pais, mais velhos, professores e funcionários: a deferência "
                  "adequada a cada relação, em gestos concretos."),
            ("C", "Entre colegas", "Não excluir, não rir do erro alheio, defender quem sofre injustiça, "
                  "pedir perdão e recomeçar."),
            ("D", "A mesa e o convívio", "Postura, uso dos talheres, esperar todos serem servidos, "
                  "conversar à mesa e receber uma visita."),
        ],
        [("Educação Infantil", "1 aula"), ("Fundamental I", "1 aula"), ("Fundamental II", "1 aula")],
        [
            "Expressão oral clara, audível e dirigida ao interlocutor",
            "Tratamento correto de pais, mais velhos, professores e funcionários",
            "Hábito de cumprimentar, agradecer, pedir licença e pedir desculpa",
            "Capacidade de discordar sem ofender e de aceitar correção",
            "Convivência atenta a quem está sozinho ou sendo tratado com injustiça",
            "Postura à mesa e desenvoltura para receber e visitar",
            "Escrita de bilhetes de agradecimento e convites, à mão",
        ],
    ),
)


PAGES["curriculo-historia-geografia.html"] = dict(
    title=f"História e Geografia — Currículo — {SCHOOL}",
    description="História e Geografia ensinadas juntas: história de Goiás, do Brasil e do mundo; "
    "geografia física, fauna, flora e cartografia.",
    body=subject_page(
        "História e Geografia", "Ensinadas juntas",
        "Nenhum fato acontece fora de um lugar. História e Geografia caminham juntas no currículo "
        "porque só se entende o que aconteceu sabendo onde aconteceu.",
        [
            "Separar História de Geografia produz dois problemas conhecidos: uma sequência de datas "
            "sem chão e uma coleção de mapas sem gente. No Rosário as duas são trabalhadas de forma "
            "integrada, pelo mesmo professor e no mesmo horário, de modo que o aluno nunca estude "
            "uma bandeirada sem saber por qual rio ela subiu, nem um bioma sem saber quem o ocupou.",
            "Em <strong>História</strong>, o percurso vai do próximo ao distante. Começa pela "
            "história local — Goiás, a mineração, as cidades do ouro, a marcha para o oeste, a "
            "construção de Goiânia e de Brasília —, porque a criança entende melhor o passado quando "
            "ele deixou marcas que ela pode visitar. Segue para a história do Brasil, do "
            "descobrimento à República, e se abre para a história do mundo: a antiguidade clássica, "
            "que ela reencontra no Latim e na Filosofia, a cristandade medieval, as grandes "
            "navegações e a formação do mundo moderno.",
            "Em <strong>Geografia</strong>, a ênfase é física. Relevo, clima, solos, hidrografia e "
            "vegetação vêm antes de qualquer discussão abstrata, porque são a base concreta sobre a "
            "qual tudo o mais se assenta. Estudamos o cerrado que nos cerca com o mesmo cuidado com "
            "que estudamos a Amazônia ou os desertos: fauna e flora identificadas pelo nome, "
            "ecossistemas, ciclo da água, estações.",
            "A cartografia atravessa os dois. O aluno aprende a ler e a desenhar mapas — escala, "
            "legenda, coordenadas, curvas de nível, rosa dos ventos — e usa o mapa como instrumento "
            "de estudo, não como ilustração. Desenhar à mão o traçado de um rio ou a rota de uma "
            "expedição fixa o conhecimento de um jeito que nenhuma leitura substitui.",
        ],
        [
            ("A", "Do local ao mundo", "Goiás primeiro, depois o Brasil, depois o mundo. O passado "
                  "começa por aquilo que a criança pode visitar."),
            ("B", "Geografia física", "Relevo, clima, hidrografia, solos, fauna e flora — o chão "
                  "concreto antes de qualquer abstração."),
            ("C", "Cartografia", "Ler e desenhar mapas à mão: escala, legenda, coordenadas e curvas "
                  "de nível como ferramenta de estudo."),
        ],
        [("Fundamental I", "4 aulas"), ("Fundamental II — História", "3 aulas"), ("Fundamental II — Geografia", "3 aulas")],
        [
            "Linha do tempo segura, de Goiás ao mundo, sem decorar datas soltas",
            "Conhecimento da história local: mineração, povoamento e formação de Goiás",
            "Domínio dos marcos da história do Brasil e da história ocidental",
            "Identificação de fauna e flora brasileiras, com atenção ao cerrado",
            "Compreensão de relevo, clima, hidrografia e sua influência na ocupação humana",
            "Leitura e desenho de mapas com escala, legenda e coordenadas",
        ],
    ),
)


# --------------------------------------------------------------------------
# Materiais diversos — áudio, vídeo, imagem e texto, por série
#
# As páginas são montadas a partir do conteúdo de assets/materiais/<serie>/:
# a Escola copia o arquivo para a pasta e roda o build. O tipo é deduzido da
# extensão e o título vem de titulos.json, quando existe, ou do nome do arquivo.
# --------------------------------------------------------------------------
import json

MATERIAIS_DIR = "assets/materiais"

TIPOS = {
    "audio": {
        "rotulo": "Áudio",
        "exts": (".mp3", ".m4a", ".ogg", ".wav", ".opus", ".aac"),
    },
    "video": {
        "rotulo": "Vídeo",
        "exts": (".mp4", ".webm", ".mov", ".m4v"),
    },
    "imagem": {
        "rotulo": "Imagem",
        "exts": (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"),
    },
    "texto": {
        "rotulo": "Texto",
        "exts": (".pdf", ".txt", ".md", ".doc", ".docx", ".odt", ".rtf"),
    },
}

SERIES = [
    ("1-ano", "1º ano", "Fundamental I"),
    ("2-ano", "2º ano", "Fundamental I"),
    ("3-ano", "3º ano", "Fundamental I"),
    ("4-ano", "4º ano", "Fundamental I"),
    ("5-ano", "5º ano", "Fundamental I"),
    ("6-ano", "6º ano", "Fundamental II"),
    ("7-ano", "7º ano", "Fundamental II"),
]


def tipo_do_arquivo(nome):
    ext = os.path.splitext(nome)[1].lower()
    for tipo, dados in TIPOS.items():
        if ext in dados["exts"]:
            return tipo
    return None


def titulo_do_arquivo(nome):
    """Converte 01-ditado-de-palavras.mp3 em 'Ditado de palavras'."""
    base = os.path.splitext(nome)[0]
    base = re.sub(r"^[\s\d]+[-_.\s]*", "", base)      # prefixo numérico de ordenação
    base = re.sub(r"\s*\[[^\]]*\]\s*$", "", base)    # id entre colchetes, como o do YouTube
    base = re.sub(r"[-_]+", " ", base).strip()
    base = re.sub(r"\s{2,}", " ", base)
    return base[:1].upper() + base[1:] if base else nome


def tamanho_legivel(bytes_):
    if bytes_ < 1024:
        return f"{bytes_} B"
    if bytes_ < 1024 * 1024:
        return f"{bytes_ / 1024:.0f} KB"
    return f"{bytes_ / (1024 * 1024):.1f} MB".replace(".", ",")


_cache_materiais = {}


def materiais_da_serie(slug):
    """Lista de dicionários com arquivo, tipo, título, descrição e tamanho.

    O resultado fica em cache: a função é consultada várias vezes por build
    (índice e página da série) e sem isso o disco seria lido de novo a cada
    chamada — e um aviso de titulos.json inválido apareceria repetido.
    """
    if slug in _cache_materiais:
        return _cache_materiais[slug]

    pasta = os.path.join(ROOT, MATERIAIS_DIR, slug)
    if not os.path.isdir(pasta):
        _cache_materiais[slug] = []
        return []

    rotulos = {}
    caminho_json = os.path.join(pasta, "titulos.json")
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, encoding="utf-8") as fh:
                rotulos = json.load(fh)
        except (ValueError, OSError) as erro:
            # Um JSON inválido não pode derrubar o build inteiro: avisa e segue
            # usando os nomes dos arquivos.
            print(f"  ! {slug}/titulos.json ignorado ({erro})")

    itens = []
    for nome in sorted(os.listdir(pasta)):
        tipo = tipo_do_arquivo(nome)
        if not tipo:
            continue
        rotulo = rotulos.get(nome)
        if isinstance(rotulo, (list, tuple)):
            titulo = rotulo[0] if rotulo else titulo_do_arquivo(nome)
            descricao = rotulo[1] if len(rotulo) > 1 else ""
        elif isinstance(rotulo, str):
            titulo, descricao = rotulo, ""
        else:
            titulo, descricao = titulo_do_arquivo(nome), ""
        itens.append({
            "arquivo": nome,
            "tipo": tipo,
            "titulo": titulo,
            "descricao": descricao,
            "ext": os.path.splitext(nome)[1].lstrip(".").upper(),
            "tamanho": tamanho_legivel(os.path.getsize(os.path.join(pasta, nome))),
            "src": f"{MATERIAIS_DIR}/{slug}/{quote(nome)}",
        })
    _cache_materiais[slug] = itens
    return itens


def _cabecalho_material(m):
    sub = f'<p class="material-descricao">{m["descricao"]}</p>' if m["descricao"] else ""
    return (
        f'<div class="material-cabecalho">'
        f'<span class="material-tipo material-tipo--{m["tipo"]}">{TIPOS[m["tipo"]]["rotulo"]}</span>'
        f'<div><p class="material-titulo">{m["titulo"]}</p>{sub}</div>'
        f'<span class="material-meta">{m["ext"]} · {m["tamanho"]}</span>'
        f"</div>"
    )


def bloco_material(m):
    """Renderiza um material conforme o tipo."""
    cab = _cabecalho_material(m)
    t, src, titulo = m["tipo"], m["src"], m["titulo"]

    if t == "audio":
        corpo = (
            f'<audio class="material-fonte" preload="metadata" controls src="{src}"></audio>'
            f'<div class="audio-controles">'
            f'<button class="audio-play" type="button" aria-label="Tocar {titulo}">'
            f'<span class="audio-icone" aria-hidden="true"></span></button>'
            f'<div class="audio-info">'
            f'<div class="audio-barra" role="slider" tabindex="0" aria-label="Posição de {titulo}"'
            f' aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">'
            f'<div class="audio-progresso"></div></div></div>'
            f'<span class="audio-tempo"><time class="audio-atual">0:00</time>'
            f'<span aria-hidden="true"> / </span><time class="audio-total">--:--</time></span>'
            f"</div>"
        )
    elif t == "video":
        corpo = (
            f'<video class="material-video" controls preload="metadata" playsinline '
            f'src="{src}">Seu navegador não reproduz vídeo. '
            f'<a href="{src}">Baixar o vídeo</a>.</video>'
        )
    elif t == "imagem":
        corpo = (
            f'<a class="material-imagem" href="{src}" target="_blank" rel="noopener" '
            f'aria-label="Abrir {titulo} em tamanho original">'
            f'<img src="{src}" alt="{titulo}" loading="lazy" decoding="async"></a>'
        )
    else:
        corpo = (
            f'<a class="btn btn--navy material-abrir" href="{src}" target="_blank" '
            f'rel="noopener">Abrir {m["ext"]}</a>'
        )

    return (
        f'<li class="material-item material-item--{t} reveal" data-tipo="{t}">'
        f"{cab}{corpo}</li>"
    )


def pagina_serie(slug, nome, etapa):
    itens = materiais_da_serie(slug)

    if itens:
        presentes = [t for t in TIPOS if any(m["tipo"] == t for m in itens)]
        filtros = ""
        if len(presentes) > 1:
            botoes = '<button class="filtro-tipo is-ativo" type="button" data-filtro="todos">Todos</button>'
            botoes += "".join(
                f'<button class="filtro-tipo" type="button" data-filtro="{t}">'
                f'{TIPOS[t]["rotulo"]}</button>'
                for t in presentes
            )
            filtros = f'<div class="filtros reveal" role="group" aria-label="Filtrar por tipo">{botoes}</div>'

        plural = "materiais" if len(itens) > 1 else "material"
        lista = (
            f'<p class="eyebrow reveal">{len(itens)} {plural} disponíve'
            + ("is" if len(itens) > 1 else "l")
            + "</p>"
            + filtros
            + '<ul class="material-lista">'
            + "".join(bloco_material(m) for m in itens)
            + "</ul>"
        )
    else:
        lista = (
            '<div class="aviso-vazio reveal">'
            "<h3>Nenhum material publicado ainda</h3>"
            f"<p>Os materiais do {nome} serão disponibilizados aqui ao longo do ano letivo. "
            "Esta página fica sempre no mesmo endereço — vale guardar o link.</p>"
            "</div>"
        )

    outras = "".join(
        f'<a class="serie-atalho{" is-atual" if s == slug else ""}" href="materiais-{s}.html">{n}</a>'
        for s, n, _ in SERIES
    )

    return (
        page_hero(
            f"Materiais — {nome}",
            f"Materiais diversos do {nome} ({etapa}): áudio, vídeo, imagem e texto, "
            "para consultar em casa quantas vezes for preciso.",
            '<a href="materiais.html">Materiais</a> &nbsp;/&nbsp; ' + nome,
        )
        + section('<nav class="series-nav reveal" aria-label="Outras séries">' + outras + "</nav>"
                  + '<div style="margin-top:2.6rem">' + lista + "</div>")
        + section(
            '<div class="split">'
            '<div class="reveal"><p class="eyebrow">Como usar</p><h2>Orientações às famílias</h2>'
            '<hr class="rule">'
            '<ul class="list-gold">'
            "<li>Áudios e vídeos podem ser repetidos quantas vezes o aluno precisar</li>"
            "<li>Pausar e voltar trechos é parte do exercício</li>"
            "<li>Imagens abrem em tamanho original ao serem clicadas</li>"
            "<li>Materiais de texto abrem em nova aba e podem ser impressos</li>"
            "<li>Em caso de dúvida sobre a atividade, falar com o professor da disciplina</li>"
            "</ul></div>"
            '<div class="panel reveal"><h3>Precisa de ajuda?</h3>'
            "<p>Se algum material não abrir ou o link não funcionar, avise a Secretaria pelo "
            "WhatsApp que corrigimos rapidamente.</p>"
            '<p style="margin-top:1.2rem">'
            '<a class="btn btn--gold" href="https://wa.me/__WA__" target="_blank" rel="noopener">'
            "Falar com a Secretaria</a></p></div></div>",
            "section--cream",
        )
    )


def _resumo_serie(slug):
    itens = materiais_da_serie(slug)
    if not itens:
        return "Em breve →"
    contagem = {}
    for m in itens:
        contagem[m["tipo"]] = contagem.get(m["tipo"], 0) + 1
    partes = [f'{n} {TIPOS[t]["rotulo"].lower()}' + ("s" if n > 1 else "")
              for t, n in contagem.items()]
    return " · ".join(partes) + " →"


PAGES["materiais.html"] = dict(
    title=f"Materiais — Currículo — {SCHOOL}",
    description="Materiais diversos por série — áudio, vídeo, imagem e texto — do 1º ao 7º ano "
    "do Ensino Fundamental.",
    body=page_hero(
        "Materiais",
        "Materiais diversos organizados por série: áudio, vídeo, imagem e texto, para o aluno "
        "consultar em casa.",
        '<a href="curriculo-pre-alfabetizacao.html">Currículo</a> &nbsp;/&nbsp; Materiais',
    )
    + section(
        text_block(
            [
                "Boa parte do que se trabalha em classe pede retomada — e retomada é justamente o "
                "que o tempo de aula não permite em quantidade suficiente. Por isso reunimos aqui "
                "os materiais usados pelos professores, para que o aluno volte a eles em casa, no "
                "próprio ritmo.",
                "São de quatro tipos: <strong>áudio</strong>, para exercícios de escuta e leitura "
                "em voz alta; <strong>vídeo</strong>, para demonstrações e registros de atividades; "
                "<strong>imagem</strong>, para mapas, obras de arte e ilustrações estudadas; e "
                "<strong>texto</strong>, para roteiros, partituras, listas de exercícios e leituras.",
                "Os materiais estão organizados por série. Escolha o ano do aluno abaixo; a página "
                "de cada série mantém sempre o mesmo endereço, e novos materiais vão sendo "
                "publicados ao longo do ano letivo.",
            ],
            "Apoio ao estudo",
            "Para consultar quantas vezes for preciso",
        )
    )
    + section(
        intro("Escolha a série", "Do 1º ao 7º ano", "")
        + '<div class="grid grid--4" style="margin-top:3rem">'
        + "".join(
            f'<a class="card card--link reveal" href="materiais-{s}.html">'
            f'<div class="icon" aria-hidden="true">{n.split("º")[0]}</div>'
            f"<h3>{n}</h3><p>{etapa}</p>"
            f'<span class="more">{_resumo_serie(s)}</span></a>'
            for s, n, etapa in SERIES
        )
        + "</div>",
        "section--cream",
    )
    + CTA,
)

for _slug, _nome, _etapa in SERIES:
    PAGES[f"materiais-{_slug}.html"] = dict(
        title=f"Materiais — {_nome} — {SCHOOL}",
        description=f"Materiais diversos do {_nome} do Ensino Fundamental: áudio, vídeo, "
        "imagem e texto.",
        body=pagina_serie(_slug, _nome, _etapa),
    )


# --------------------------------------------------------------------------
# Escrita dos arquivos
# --------------------------------------------------------------------------
def build():
    footer = FOOTER.format(school=SCHOOL, site=SITE_URL.replace("https://", ""), crest_footer=crest(62))
    for slug, page in PAGES.items():
        header = HEADER.format(school=SCHOOL, nav=render_nav(slug), crest_header=crest(48))
        html = TEMPLATE.format(
            title=page["title"],
            description=page["description"],
            slug="" if slug == "index.html" else slug,
            site=SITE_URL,
            header=header,
            footer=footer,
            body=page["body"],
            css=asset_url("assets/css/style.css"),
            js=asset_url("assets/js/main.js"),
        )
        # Fonte única dos dados de contato: os marcadores são resolvidos aqui,
        # de modo que trocar o número ou o CNPJ acima atualiza o site inteiro.
        html = (html.replace("__WA_FMT__", WHATSAPP_FMT)
                    .replace("__WA__", WHATSAPP)
                    .replace("__CNPJ__", CNPJ)
                    .replace("__EMAIL__", EMAIL)
                    .replace("__END_MAPA__", quote_plus(ENDERECO_MAPA))
                    .replace("__END_RUA__", ENDERECO_RUA)
                    .replace("__END_BAIRRO__", ENDERECO_BAIRRO)
                    .replace("__END_CIDADE__", ENDERECO_CIDADE)
                    .replace("__END_CEP__", ENDERECO_CEP))
        with open(os.path.join(ROOT, slug), "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  ✓ {slug}")

    # sitemap.xml
    urls = "".join(
        f"  <url><loc>{SITE_URL}/{'' if s == 'index.html' else s}</loc>"
        f"<priority>{'1.0' if s == 'index.html' else '0.8'}</priority></url>\n"
        for s in PAGES
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n"
        )
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"\n{len(PAGES)} páginas geradas + sitemap.xml + robots.txt")


if __name__ == "__main__":
    build()
