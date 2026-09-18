# Colégio Nossa Senhora do Rosário — site institucional

Site estático (HTML + CSS + JS puro), sem dependências e sem etapa de build obrigatória.
Domínio de destino: https://colegionsrosario.com.br

## Estrutura

```
build.py            gerador — menu, cabeçalho, rodapé e conteúdo das páginas
index.html          home
*.html              17 páginas geradas (não editar à mão — veja abaixo)
sitemap.xml         gerado
robots.txt          gerado
assets/css/style.css
assets/js/main.js
assets/img/brasao.png   recriação vetorial do brasão
```

## Como editar

Os arquivos `.html` são **gerados**. Edite `build.py` e rode:

```bash
python3 build.py
```

Isso reescreve todas as páginas, o `sitemap.xml` e o `robots.txt`.
O menu fica na constante `NAV`, no topo do arquivo; o texto de cada página,
no dicionário `PAGES`.

## Rodar localmente

```bash
python3 -m http.server 8899
# http://localhost:8899
```

## Publicação

Basta subir a pasta inteira para qualquer hospedagem estática
(Vercel, Netlify, GitHub Pages, ou um diretório em servidor Apache/Nginx).

## Paleta

Extraída do brasão — azul-marinho `#0B1B3F` / `#12295C`, ouro `#C9A227` / `#D4AF37`,
creme `#FBF7EE`. Todas definidas como variáveis CSS em `:root`.
Tipografia: Cormorant Garamond (títulos) + Lato (texto), via Google Fonts.

## Pendências para a Escola preencher

- Endereço, telefones e e-mail reais (hoje há placeholders em `build.py`: `FOOTER` e `contato.html`)
- Fotos reais do colégio (o layout hoje usa apenas cor, tipografia e o brasão)
- Arquivo original do brasão em alta resolução — o `brasao.png` é uma recriação
- Números institucionais (ano de fundação, estatísticas do hero e da Equipe Docente)
- Valores de mensalidade e o PDF do Regimento Escolar
- O formulário de Contato ainda não envia nada: precisa de um endpoint (Formspree, ou back-end próprio)
