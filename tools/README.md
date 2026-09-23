# tools

Ferramentas do site. Hoje existe uma só.

O panorama do projeto (estrutura, Grimório, publicação, manutenção) está no
[`README.md`](../README.md) da raiz. Este arquivo detalha o script.

## `build_grimorio.py`

Converte os documentos Markdown de `docs/` nas páginas HTML do **Grimório Digital** e
gera `sitemap.xml` e `robots.txt`.

```bash
python3 tools/build_grimorio.py
```

Não precisa instalar nada: usa apenas a biblioteca padrão do Python 3.9+.

### O que ele gera

| Saída | Origem |
| --- | --- |
| `grimorio/<slug>.html` | cada arquivo `.md` registrado em `DOCS` |
| `grimorio.html` | índice montado a partir de `DOCS` e `CATEGORIES` |
| `sitemap.xml` | todas as páginas do site que existem no disco |
| `robots.txt` | aponta para o sitemap |

### Regras que o script respeita

* **os `.md` são somente leitura**: o script nunca altera `docs/`;
* **nada é inventado**: a página gerada é o documento convertido, com o caminho da
  fonte visível no cabeçalho;
* sem dependências externas, sem backend: o site continua estático.

### Adicionar um documento novo

1. crie o arquivo em `docs/`;
2. registre-o em `DOCS` (e em `CURATED_ORDER`) dentro de `tools/build_grimorio.py`;
3. rode o script;
4. commite o `.md`, as páginas geradas e o `sitemap.xml` juntos.

Se um `.md` existir em `docs/` e não estiver registrado, o script avisa no terminal.

### Markdown suportado

Títulos (`#` a `####`), parágrafos, negrito, itálico, links, código inline, blocos de
código cercados, listas ordenadas e não ordenadas (com aninhamento), tabelas com
alinhamento, citações e linhas horizontais: o subconjunto usado pelos documentos do
projeto. Ao usar algo fora disso, confira o resultado depois de gerar.

### O que cada página gerada traz

* o primeiro título `#` do `.md` é descartado (`skip_first_h1`), porque o título já aparece
  no cabeçalho da página;
* cabeçalho com o caminho da fonte, a data do último commit que tocou o `.md` e a estimativa
  de leitura;
* índice de seções (quando o documento tem 3 ou mais títulos de nível 2);
* navegação anterior/próximo entre os documentos, na ordem de `CURATED_ORDER`.

## Regra de interface

As páginas geradas são lidas por visitantes. Portanto:

* **não** publicar comando de manutenção, nome de script ou explicação de como o HTML é
  produzido (Markdown, geração, pipeline). Isso vive aqui e no `README.md` da raiz;
* links para o `.md` original são permitidos, fazem parte da transparência do site;
* texto novo segue a voz do site: primeira pessoa, sem travessão longo (U+2014) e sem
  linguagem institucional.

## Endereço do site

`SITE_URL`, no topo do script, e as URLs `canonical`/`og:` das páginas escritas à mão
apontam para `https://cod-rebel-rider.github.io/dj.github.io/`.

Se um domínio próprio for configurado:

1. troque `SITE_URL` no script e rode-o de novo;
2. busque e substitua `https://cod-rebel-rider.github.io/dj.github.io/` nos arquivos
   `.html` da raiz, em `projetos/` e em `grimorio/`;
3. troque o prefixo `/dj.github.io/` usado nos links absolutos de `404.html`.

## Imagem de compartilhamento

`assets/images/og.png` é gerada a partir de `assets/images/og.svg`:

```bash
rsvg-convert -w 1200 -h 630 -b '#08080a' assets/images/og.svg -o assets/images/og.png
```
