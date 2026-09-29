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
assets/img/
  image.png         brasão original recebido (fundo cinza) — arquivo-fonte
  brasao-full.png   brasão com fundo removido, 977x1220 — para impressão/alta
  brasao.png        versão web usada no site, 272x340
  brasao-icon.png   192x192 quadrado, favicon e apple-touch-icon
tools/remove-bg.py  script que gerou os PNGs transparentes a partir de image.png
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

Automática: todo push na `main` dispara `.github/workflows/deploy.yml`, que
regenera o site, confere se o HTML commitado bate com o `build.py` e envia os
arquivos por FTPS para `public_html/` na hospedagem.

Para funcionar, cadastre em *Settings → Secrets and variables → Actions*:

| Segredo | Onde encontrar no cPanel da GoDaddy |
|---|---|
| `FTP_SERVER` | Contas de FTP → Configurar Cliente de FTP → servidor |
| `FTP_USERNAME` | usuário de FTP (geralmente `usuario@colegionsrosario.com.br`) |
| `FTP_PASSWORD` | senha definida ao criar a conta de FTP |

Sem os segredos, o workflow roda, avisa e não publica nada.

Não vão para o servidor: `build.py`, `README.md`, `tools/`, `.github/`, os ZIPs
e as imagens de origem (`image.png`, `brasao-full.png`).

Manualmente, se preferir: suba os `.html`, `assets/`, `robots.txt` e `sitemap.xml`
para qualquer hospedagem estática.

## Brasão

O fundo cinza do arquivo original (`assets/img/image.png`) foi removido com
`tools/remove-bg.py`: flood fill a partir das bordas sobre pixels de baixo croma,
matte suave numa faixa de 2 px junto à silhueta (preserva o antialias da borda)
e descarte dos resíduos da sombra projetada.

Para regerar, com Pillow e numpy instalados:

```bash
python3 tools/remove-bg.py assets/img/image.png assets/img/brasao-full.png
```

Depois redimensione para `brasao.png` (340 px de altura) e `brasao-icon.png` (192x192).

### Trocar o brasão

Basta substituir `assets/img/brasao.png` e rodar `python3 build.py`. Os atributos
`width`/`height` de cada `<img>` são calculados a partir do arquivo real (função
`crest()` em `build.py`, que lê o IHDR do PNG), e o CSS aplica `height: auto` —
um arquivo com proporção diferente não é achatado nem provoca salto de layout.
Recorte a margem transparente antes: sobra de margem faz o brasão renderizar
menor do que a largura pedida.

## Materiais (áudio, vídeo, imagem e texto, por série)

`assets/materiais/<serie>/` guarda os arquivos; `build.py` varre as pastas e monta
`materiais.html` e `materiais-1-ano.html` … `materiais-7-ano.html`. O tipo é
deduzido pela extensão do arquivo — não é preciso indicar nada além de colocar
o arquivo na pasta certa.

Dentro de cada série, subpastas separam por matéria:
`assets/materiais/<serie>/ingles/` e `.../frances/` aparecem no site como
seções "Inglês" e "Francês". Um arquivo solto na raiz da série (fora dessas
subpastas) cai numa seção "Geral". Outras matérias podem ser adicionadas
criando uma nova subpasta — o rótulo sai do nome dela.

Para publicar: copie o arquivo para a subpasta certa e rode `python3 build.py`.
Instruções completas em `assets/materiais/LEIA-ME.txt`.

| Tipo | Extensões aceitas | Como aparece |
|---|---|---|
| Áudio | `.mp3` `.m4a` `.ogg` `.wav` `.opus` `.aac` | player com play, barra e tempo |
| Vídeo | `.mp4` `.webm` `.mov` `.m4v` | player de vídeo com controles nativos |
| Imagem | `.jpg` `.png` `.webp` `.gif` `.svg` | exibida na página, abre em tamanho real ao clicar |
| Texto | `.pdf` `.txt` `.md` `.doc` `.docx` `.odt` `.rtf` | cartão com botão "Abrir" em nova aba |

- Título: vem do nome do arquivo (`01-ditado-de-palavras.mp3` → "Ditado de
  palavras"); prefixo numérico e IDs entre colchetes (ex. do YouTube) não aparecem
- Para outro título ou uma descrição, crie `titulos.json` na pasta da série
- Série sem material exibe aviso de "em breve" — não quebra nada
- Uma série com mais de um tipo ganha filtro (Todos / Áudio / Vídeo / Imagem / Texto)

O player de áudio tem botão de play, título, barra de progresso clicável (com
navegação por teclado) e tempo. Sem JavaScript, o `<audio controls>` nativo
aparece no lugar.

**A hospedagem precisa aceitar requisições Range** (`Accept-Ranges: bytes`) para
o usuário conseguir arrastar a posição de áudio ou vídeo. Apache e Nginx fazem
isso por padrão; o `python -m http.server` não, então localmente a barra não
busca posição.

## Cache dos assets

O `<link>` do CSS e o `<script>` recebem um sufixo `?v=<hash do conteúdo>`,
gerado por `asset_url()` em `build.py`. Alterar o arquivo muda o hash e força
o navegador a baixar a versão nova; sem isso, quem já visitou o site continua
vendo o CSS antigo.

## Paleta

Extraída do brasão — azul-marinho `#0B1B3F` / `#12295C`, ouro `#C9A227` / `#D4AF37`,
creme `#FBF7EE`. Todas definidas como variáveis CSS em `:root`.
Tipografia: Cormorant Garamond (títulos) + Lato (texto), via Google Fonts.

## Pendências para a Escola preencher

- Número do lote no endereço — o dado recebido terminava em "QUADRA12 LT", sem o número
- Fotos reais do colégio (o layout hoje usa apenas cor, tipografia e o brasão)
- Estatísticas do hero e da Equipe Docente (turmas, % de pós-graduados, horas de formação)
- Valores de mensalidade e o PDF do Regimento Escolar
- Textos institucionais foram escritos a partir do que foi informado (fundação em 2022,
  por famílias) — revisar antes de publicar

## Dados institucionais

Ficam no topo de `build.py`, como fonte única — alterá-los ali atualiza o site inteiro:

| Constante | Valor |
|---|---|
| `CNPJ` | 66.154.330/0001-40 |
| `WHATSAPP` | 5562991957333 (formato de link) |
| `WHATSAPP_FMT` | (62) 99195-7333 (exibição) |
| `ENDERECO_RUA` | Rua 255, nº 678 — Quadra 12 |
| `ENDERECO_BAIRRO` | Setor Coimbra |
| `ENDERECO_CIDADE` | Goiânia — GO |
| `ENDERECO_CEP` | CEP 74533-150 |
| `ENDERECO_MAPA` | string usada na busca do Google Maps |
| `EMAIL` | colegionsrgo@gmail.com |

## Formulário de contato

Não depende de back-end. Ao enviar, o JavaScript monta uma mensagem formatada
com nome, e-mail, telefone, assunto e texto, e abre `wa.me` com a conversa da
Secretaria já preenchida — a pessoa só confirma o envio no WhatsApp.
O número vem do atributo `data-whatsapp` no `<form>`, não do JS.
