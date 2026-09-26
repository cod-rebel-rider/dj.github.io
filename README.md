# Cod Rebel DJ

Site oficial do **Cod Rebel DJ** (Arthur Rodrigues): Rock, Funk, Automotivo, Industrial e
eletrônico no mesmo set.

O site reúne a apresentação do trabalho, os formatos de apresentação, os projetos, os
registros de shows, os canais de contato, a página de apoio e o **Grimório Digital**, onde
a documentação do projeto é publicada na íntegra.

Este README é documentação para quem mantém o site. Não é material de divulgação.

---

## Objetivo

Este repositório contém o site oficial do Cod Rebel DJ, hospedado no **GitHub Pages**.

O site é **estático**: HTML, CSS e um arquivo JS sem dependências. Não há backend, banco
de dados, framework nem build obrigatório. A única ferramenta é um script em Python
(biblioteca padrão) que converte os documentos de `docs/` nas páginas do Grimório.

Princípios que o código respeita:

* **nada é inventado**: só entra no site o que está registrado em `docs/`;
* **os `.md` são somente leitura** para os scripts;
* **sem dependências novas** sem necessidade real;
* site leve, acessível e legível sem JavaScript.

---

## Estrutura

```text
/
├── index.html                 home
├── sobre.html                 identidade, método e direção
├── shows.html                 agenda e registros de apresentações
├── projetos.html              status de cada frente
├── grimorio.html              índice do Grimório Digital (gerado)
├── contato.html               contratação, imprensa e parcerias
├── apoie.html                 apoio e transparência
├── 404.html                   página de erro do GitHub Pages
├── sitemap.xml                gerado
├── robots.txt                 gerado
│
├── assets/
│   ├── css/style.css          sistema visual (único CSS)
│   ├── js/main.js             menu mobile e entrada de elementos
│   ├── images/                favicon, marca, og.png e placeholders (ver README local)
│   └── presskit/              reservado para o presskit (ver README local)
│
├── docs/                      documentos-fonte do Grimório (.md), fonte de conteúdo
├── grimorio/                  documentos convertidos em HTML (gerado)
├── projetos/
│   ├── bailao-do-rock/index.html
│   └── sets/index.html
│
├── tools/
│   ├── build_grimorio.py      gerador do Grimório, sitemap e robots
│   └── README.md              detalhes do gerador
│
├── APRESENTACAO.md            apresentação artística do projeto (referência)
├── LICENSE
└── README.md
```

Os arquivos marcados como **gerado** não devem ser editados à mão: eles são sobrescritos
por `tools/build_grimorio.py`.

---

## Grimório Digital

O Grimório é a documentação do projeto publicada como páginas navegáveis do próprio site.

### O fluxo

```text
Markdown (fonte de conteúdo)   ->   HTML gerado (representação para o site)

docs/cod-rebel-dj.md                grimorio/cod-rebel-dj.html
docs/repertório.md                  grimorio/repertorio.html
docs/trajetoria.md                  grimorio/trajetoria.html
docs/shows.md                       grimorio/shows.html
docs/equipamentos.md                grimorio/equipamentos.html
docs/projetos.md                    grimorio/projetos.html
docs/fallen.md                      grimorio/fallen.html
docs/aprendizados.md                grimorio/aprendizados.html
                                    grimorio.html      (índice)
                                    sitemap.xml
                                    robots.txt
```

* **Markdown é a fonte de conteúdo.** Os documentos oficiais ficam em `docs/`. O gerador
  nunca altera nem apaga nada dentro de `docs/`.
* **O HTML gerado é a representação para o site.** As páginas em `grimorio/` são produzidas
  a partir dos `.md`, com a mesma marcação e o mesmo CSS das páginas escritas à mão.
* **Em caso de divergência, vale o `.md`.** Se uma página gerada e o documento original
  discordarem, o documento original está certo: rode o gerador de novo.

### Como atualizar o Grimório

```bash
python3 tools/build_grimorio.py
```

O script usa apenas a biblioteca padrão do Python 3.9+ (nada para instalar) e gera:

| Saída | Origem |
| --- | --- |
| `grimorio/<slug>.html` | cada `.md` registrado em `DOCS` |
| `grimorio.html` | índice montado a partir de `DOCS` e `CATEGORIES` |
| `sitemap.xml` | páginas do site que existem no disco |
| `robots.txt` | aponta para o sitemap |

O registro de documentos (`DOCS`), a ordem exibida (`CURATED_ORDER`), as categorias
(`CATEGORIES`) e as descrições curtas de cada documento estão no topo de
`tools/build_grimorio.py`. Detalhes, Markdown suportado e o passo a passo para incluir um
documento novo estão em `tools/README.md`.

### Regra de interface

A explicação técnica do Grimório (Markdown, script, geração de HTML, comandos de
manutenção) **não aparece para o visitante**. Quem visita o site lê os documentos; quem
mantém o site lê este README e `tools/README.md`.

Ao editar os templates de `tools/build_grimorio.py`, mantenha a separação: nada de
comandos, caminhos de script, nomes de arquivos `.md` ou explicação de pipeline no HTML
publicado. Os links do Grimório devem apontar para outras páginas do site.

---

## Desenvolvimento local

O site é estático, mas **precisa ser servido por HTTP a partir da raiz do repositório**:
os caminhos de CSS, JS, imagens e páginas são relativos.

```bash
cd dj.github.io
python3 -m http.server 8000
# abra http://localhost:8000/
```

Não abra os arquivos via `file://`: menu mobile, caminhos relativos e páginas do Grimório
não se comportam corretamente desse jeito.

Qualquer servidor estático serve (`npx serve`, `php -S localhost:8000` e afins). O projeto
não exige porta específica: `8000` é apenas o padrão usado nos testes.

Antes de publicar qualquer alteração:

1. rode o gerador: `python3 tools/build_grimorio.py`;
2. confira `git diff` nos arquivos gerados (diff aparecendo sem mudança em `docs/` indica
   que algo ficou fora de sincronia);
3. sirva o site localmente e navegue pelas páginas, incluindo o Grimório;
4. confira os links do rodapé, as âncoras (`contato.html#booking`, `index.html#situacao`)
   e a página 404;
5. valide `sitemap.xml`, que o gerador escreve a partir das páginas existentes no disco.

### A página 404

`404.html` é entregue automaticamente pelo GitHub Pages em rotas inexistentes. É o único
arquivo que usa **caminhos absolutos** (`/dj.github.io/...`), porque pode ser exibido em
qualquer profundidade de URL. Testando localmente, os links dela não funcionam a partir de
`http://localhost:8000/`. Isso é esperado.

---

## GitHub Pages

* **URL:** `https://cod-rebel-rider.github.io/dj.github.io/`
* **Tipo:** site de projeto, servido a partir da **raiz** do branch publicado.
* **Publicação:** feita pelo GitHub Pages a partir da raiz do repositório, usando a branch
  configurada nas *Settings › Pages* do próprio repositório. Este checkout não contém
  workflow ou configuração local de publicação;
* **404:** o `404.html` da raiz é usado automaticamente.
* **`CNAME`:** não existe. Sem domínio próprio, a URL do Pages é a oficial, e é ela que
  aparece em `canonical`, `og:url` e no `sitemap.xml`.

### Cuidados com caminhos

* Páginas da raiz usam caminhos relativos à raiz (`assets/css/style.css`).
* Páginas em `projetos/<slug>/` e em `grimorio/` usam `../../` e `../`. Nas páginas do
  Grimório esse prefixo é definido pelo gerador (parâmetro `prefix`).
* Evite nome de arquivo com acento ou espaço em páginas novas. `docs/repertório.md` só
  funciona bem porque o gerador cria `grimorio/repertorio.html` (slug sem acento).
  O caminho do Markdown fica apenas na documentação de manutenção, não no HTML público.
* Se a URL do site mudar: troque `SITE_URL` em `tools/build_grimorio.py`, rode o gerador e
  ajuste `canonical`/`og:url` das páginas escritas à mão e o prefixo absoluto do `404.html`.

### Testar antes de publicar

Sirva o site localmente, percorra as páginas e confira o resultado. Depois de publicar,
abra a URL de produção e verifique se o CSS carregou: erro de caminho aparece como site
sem estilo.

---

## Atualização de conteúdo

### Onde alterar textos

| O que | Onde |
| --- | --- |
| Home | `index.html` |
| Identidade, método e direção | `sobre.html` |
| Agenda e registros de shows | `shows.html` |
| Status dos projetos | `projetos.html` |
| Páginas de projeto | `projetos/bailao-do-rock/index.html`, `projetos/sets/index.html` |
| Contratação, imprensa e parcerias | `contato.html` |
| Apoio e transparência | `apoie.html` |
| Erro 404 | `404.html` |
| Índice e registro dos documentos | `tools/build_grimorio.py` (`DOCS`, `CATEGORIES`) |
| Documentos em si | `docs/*.md` (e rodar o gerador depois) |

Pontos que valem para qualquer edição:

* **cabeçalho e rodapé se repetem** em todas as páginas. Nas páginas da raiz eles são
  escritos à mão; no Grimório vêm de `page_head()` e `site_footer()` em
  `tools/build_grimorio.py`. Mudança de rodapé pede as duas pontas;
* os `id` de seção (`#booking`, `#situacao`, `#projetos`, `#fechar`) são usados em links
  internos. Não renomeie sem atualizar quem aponta para eles;
* cada página tem **um único `<h1>`**, além de `<title>`, `description` e `canonical`
  próprios. Mantenha o padrão ao criar página nova;
* a lista de navegação existe em dois lugares: `NAV`, no gerador, e o bloco `<nav>` das
  páginas escritas à mão. As duas precisam continuar iguais.

### Tom dos textos

O site fala em **primeira pessoa**, como o artista falando de si. Regras práticas:

* **sem travessão longo** (U+2014) em texto, título, descrição, card, rodapé ou no Grimório.
  Use vírgula, dois pontos, parênteses ou quebra de frase;
* evitar linguagem institucional ("o objetivo deste projeto é", "a proposta consiste em");
* usar "projeto" só quando ajudar a explicar algo. Prefira "meu trabalho", "meus sets",
  "minha caminhada", "o que eu venho fazendo";
* nenhum dado inventado: número, data, local e canal de contato que não esteja em `docs/`
  não entram no site.

### Imagens e presskit

* imagens em `assets/images/`. Regras de uso, nomes e otimização no README do diretório;
* `assets/images/og.png` é gerado a partir de `og.svg`. O comando está no README do
  diretório;
* `assets/images/registro-placeholder.svg` é moldura de "registro pendente" e sai quando
  existirem fotos reais;
* presskit em `assets/presskit/`. O README do diretório lista o que deve entrar nele.

### Pendências conhecidas

Ficam como espaço reservado, marcado no próprio site, até existir informação real:

* canais de contato em `contato.html`: resolvido. E-mail para booking e imprensa
  (`cod-rebel@proton.me`), Transmissão Piara no WhatsApp como canal de avisos e Instagram para
  conversa direta;
* forma de apoio financeiro em `apoie.html`;
* presskit em `assets/presskit/`;
* fotos reais de apresentações e do setup (`registro-placeholder.svg`).

---

## Branches

* `tarefa/site`: desenvolvimento do site.
* `main`: branch principal do repositório; não deve receber merge automático nesta etapa.

O desenvolvimento acontece em `tarefa/site`. A branch efetivamente publicada é a configurada no
GitHub Pages; este repositório não contém essa configuração. Qualquer merge para `main` é uma
decisão manual, depois de revisão.

---

## Licença

* **Código:** MIT. Veja `LICENSE`.
* **Identidade e conteúdo artístico** (textos, marca, artes, imagens, gravações): todos os
  direitos reservados. A licença do código não se aplica a eles.

---

## Referências internas

* `tools/README.md`: comportamento do gerador, Markdown suportado, como adicionar documento.
* `assets/images/README.md`: imagens, placeholders e imagem de compartilhamento.
* `assets/presskit/README.md`: o que o presskit precisa ter.
* `APRESENTACAO.md`: apresentação artística do projeto, mantida como referência.
