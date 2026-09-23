#!/usr/bin/env python3
"""Gerador do Grimório Digital · Cod Rebel DJ.

Fecha a ponte entre a documentação do repositório e o site publicado:

  docs/*.md  ->  grimorio/*.html  (documentos)
             ->  grimorio.html    (índice do grimório)
             ->  sitemap.xml

Regras do projeto que este script respeita:

* os arquivos `.md` em `docs/` são a **fonte de verdade** e nunca são
  alterados por este script (apenas lidos);
* nada é inventado: o HTML gerado é o documento convertido, com o caminho
  da fonte visível em cada página;
* sem dependências externas (somente biblioteca padrão do Python 3.9+);
* site estático, compatível com GitHub Pages: nenhum backend é necessário.

Uso:

    python3 tools/build_grimorio.py

Depois de editar qualquer arquivo em docs/, rode o script de novo e commite
os arquivos gerados junto com o .md.
"""

from __future__ import annotations

import html
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "grimorio"

# URL pública do site. Se um domínio próprio for configurado depois,
# troque este valor e o mesmo endereço nas páginas .html da raiz.
SITE_URL = "https://cod-rebel-rider.github.io/dj.github.io/"
REPO_URL = "https://github.com/cod-rebel-rider/dj.github.io"
REPO_BRANCH = "main"
TODAY = date.today().isoformat()

ORPHAN_PARAM = "utm_"


# ---------------------------------------------------------------------------
# Registro dos documentos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Doc:
    slug: str       # nome da página gerada (grimorio/<slug>.html)
    source: str     # caminho do .md, relativo à raiz do repositório
    title: str      # título exibido
    cat: str        # chave da categoria (ver CATEGORIES)
    summary: str    # descrição curta, usada no índice


CATEGORIES = [
    ("identidade", "Identidade", "Quem eu sou, o que eu toco e onde eu quero chegar."),
    ("som", "Som", "Gêneros, referências e formatos de apresentação."),
    ("registros", "Registros", "O que já aconteceu, com data e local."),
    ("estrutura", "Estrutura", "Equipamentos, cabos, montagem e o que falta."),
    ("projetos", "Projetos", "Projetos paralelos e experimentos."),
    ("log", "Log técnico", "Aprendizados, erros e decisões."),
]

DOCS = [
    Doc("cod-rebel-dj", "docs/cod-rebel-dj.md", "Cod Rebel DJ", "identidade",
        "Quem sou, o que eu toco, como eu penso um set, minha identidade e para onde quero ir."),
    Doc("repertorio", "docs/repertório.md", "Repertório", "som",
        "Gêneros e referências que atravessam o set, do Rock ao Funk."),
    Doc("trajetoria", "docs/trajetoria.md", "Trajetória", "registros",
        "Linha do tempo do que já aconteceu e os próximos objetivos."),
    Doc("shows", "docs/shows.md", "Shows", "registros",
        "Registros das apresentações realizadas, com local, formato e público estimado."),
    Doc("equipamentos", "docs/equipamentos.md", "Equipamentos", "estrutura",
        "Controladora, notebook, controlador MIDI, mixer, cabos e as próximas aquisições."),
    Doc("projetos", "docs/projetos.md", "Projetos", "projetos",
        "O projeto principal, sets autorais, produção e projetos paralelos."),
    Doc("fallen", "docs/fallen.md", "Fallen EV Tributo", "projetos",
        "Tributo ao Evanescence: atuação como DJ e experiência de palco."),
    Doc("aprendizados", "docs/aprendizados.md", "Aprendizados", "log",
        "Set flexível, mapeamento MIDI, roteamento de áudio e lições de palco."),
]

# Ordem de exibição no índice: identidade primeiro, depois som e registros.
CURATED_ORDER = ["cod-rebel-dj", "repertorio", "trajetoria", "shows",
                 "equipamentos", "projetos", "fallen", "aprendizados"]


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------

def clean_url(url: str) -> str:
    """Remove parâmetros de rastreamento (utm_*) copiados junto com links."""
    url = url.strip()
    parts = urlsplit(url)
    if not parts.query:
        return url
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not k.lower().startswith(ORPHAN_PARAM)]
    return urlunsplit(parts._replace(query=urlencode(kept)))


def strip_markup(text: str) -> str:
    """Remove marcações inline (negrito, código, links) para gerar ids e índices."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    return text.strip()


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", strip_markup(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text or "secao"


def br_date(iso: str | None) -> str | None:
    """2026-05-30 -> 30/05/2026"""
    if not iso:
        return None
    try:
        year, month, day = iso.split("-")
        return f"{day}/{month}/{year}"
    except ValueError:
        return iso


def git_date(rel_paths) -> str | None:
    """Data do último commit que tocou os caminhos informados."""
    if isinstance(rel_paths, str):
        rel_paths = [rel_paths]
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", *rel_paths],
            capture_output=True, text=True, timeout=15, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


# ---------------------------------------------------------------------------
# Markdown -> HTML (subconjunto usado nos documentos do projeto)
# ---------------------------------------------------------------------------

RE_INLINE_CODE = re.compile(r"`([^`]+)`")
RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
RE_ITALIC = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])")
RE_FENCE = re.compile(r"^```([\w+-]*)\s*$")
RE_FENCE_END = re.compile(r"^```\s*$")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
RE_HR = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")
RE_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
RE_ORDERED = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
RE_SEP_CELL = re.compile(r"^:?-{2,}:?$")


def inline(raw: str) -> str:
    """Converte marcação inline. O texto é escapado antes das substituições."""
    text = html.escape(raw, quote=False)

    codes: list[str] = []

    def _keep_code(match: re.Match) -> str:
        codes.append(match.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    text = RE_INLINE_CODE.sub(_keep_code, text)

    def _link(match: re.Match) -> str:
        url = html.escape(clean_url(match.group(2)), quote=True)
        return '<a href="%s">%s</a>' % (url, match.group(1))

    text = RE_LINK.sub(_link, text)
    text = RE_BOLD.sub(r"<strong>\1</strong>", text)
    text = RE_ITALIC.sub(r"<em>\1</em>", text)

    def _restore(match: re.Match) -> str:
        return "<code>%s</code>" % codes[int(match.group(1))]

    return re.sub(r"\x00(\d+)\x00", _restore, text)


def _split_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _is_table_sep(line: str) -> bool:
    if not _is_table_row(line):
        return False
    cells = _split_row(line)
    return bool(cells) and all(RE_SEP_CELL.match(cell) for cell in cells)


def _is_list_line(line: str) -> bool:
    return bool(RE_BULLET.match(line) or RE_ORDERED.match(line))


def _align_class(cell: str) -> str:
    left = cell.startswith(":")
    right = cell.endswith(":")
    if left and right:
        return ' class="ta-c"'
    if right:
        return ' class="ta-r"'
    return ""


def _render_items(items: list[list]) -> str:
    """Monta listas (com aninhamento) a partir de (nível, ordenada, texto, extras)."""
    out: list[str] = []
    stack: list[dict] = []

    for level, ordered, text, extras in items:
        tag = "ol" if ordered else "ul"

        while stack and stack[-1]["level"] > level:
            out.append("</li></%s>" % stack[-1]["tag"])
            stack.pop()

        if not stack or stack[-1]["level"] < level:
            stack.append({"level": level, "tag": tag})
            out.append("<%s>" % tag)
        else:
            out.append("</li>")
            if stack[-1]["tag"] != tag:
                out.append("</%s>" % stack[-1]["tag"])
                stack.pop()
                stack.append({"level": level, "tag": tag})
                out.append("<%s>" % tag)

        body = inline(text)
        if extras:
            body += " " + inline(" ".join(extras))
        out.append("<li>%s" % body)

    while stack:
        out.append("</li></%s>" % stack[-1]["tag"])
        stack.pop()

    return "".join(out)


def md_to_html(markdown: str, skip_first_h1: bool = False) -> tuple[str, list[tuple[int, str, str]]]:
    """Converte o Markdown do projeto em HTML.

    Devolve (html, títulos), com títulos como lista de (nível, id, texto).

    Com skip_first_h1=True, o primeiro título de nível 1 é descartado: nas páginas do
    grimório o título do documento já aparece no cabeçalho da página, e manter os dois
    criaria dois <h1> na mesma página.
    """
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    total = len(lines)
    out: list[str] = []
    headings: list[tuple[int, str, str]] = []
    used_ids: dict[str, int] = {}
    skipped_title = False
    i = 0

    def unique_id(text: str) -> str:
        base = slugify(text)
        count = used_ids.get(base, 0)
        used_ids[base] = count + 1
        return base if count == 0 else "%s-%d" % (base, count + 1)

    def starts_block(index: int) -> bool:
        if index >= total:
            return True
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            return True
        if RE_FENCE.match(stripped) or RE_HR.match(stripped):
            return True
        if RE_HEADING.match(stripped) or stripped.startswith(">"):
            return True
        if _is_list_line(line):
            return True
        return _is_table_row(line) and index + 1 < total and _is_table_sep(lines[index + 1])

    while i < total:
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue

        fence = RE_FENCE.match(stripped)
        if fence:
            lang = fence.group(1)
            i += 1
            buffer: list[str] = []
            while i < total and not RE_FENCE_END.match(lines[i].strip()):
                buffer.append(lines[i])
                i += 1
            i += 1  # fecha a cerca
            attr = ' class="language-%s"' % lang if lang else ""
            out.append("<pre><code%s>%s\n</code></pre>"
                       % (attr, html.escape("\n".join(buffer))))
            continue

        if RE_HR.match(stripped):
            out.append("<hr>")
            i += 1
            continue

        heading = RE_HEADING.match(stripped)
        if heading:
            level = len(heading.group(1))
            content = heading.group(2).strip()
            if skip_first_h1 and level == 1 and not skipped_title:
                skipped_title = True
                i += 1
                continue
            anchor = unique_id(content)
            headings.append((level, anchor, strip_markup(content)))
            out.append('<h%d id="%s">%s</h%d>' % (level, anchor, inline(content), level))
            i += 1
            continue

        if stripped.startswith(">"):
            buffer = []
            while i < total and lines[i].strip().startswith(">"):
                buffer.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", "\n".join(buffer))]
            body = "".join("<p>%s</p>" % inline(c) for c in chunks if c)
            out.append("<blockquote>%s</blockquote>" % body)
            continue

        if _is_table_row(raw) and i + 1 < total and _is_table_sep(lines[i + 1]):
            head_cells = _split_row(raw)
            aligns = [_align_class(cell) for cell in _split_row(lines[i + 1])]
            i += 2
            body_rows: list[list[str]] = []
            while i < total and _is_table_row(lines[i]):
                cells = _split_row(lines[i])
                while len(cells) < len(head_cells):
                    cells.append("")
                body_rows.append(cells[:len(head_cells)])
                i += 1

            def cell(tag: str, index: int, value: str) -> str:
                attr = aligns[index] if index < len(aligns) else ""
                return "<%s%s>%s</%s>" % (tag, attr, inline(value), tag)

            head = "".join(cell("th", pos, value) for pos, value in enumerate(head_cells))
            body = "".join(
                "<tr>%s</tr>" % "".join(cell("td", pos, value) for pos, value in enumerate(cells))
                for cells in body_rows
            )
            out.append(
                '<div class="table-scroll"><table><thead><tr>%s</tr></thead>'
                "<tbody>%s</tbody></table></div>" % (head, body)
            )
            continue

        if _is_list_line(raw):
            items: list[list] = []
            base_indent: int | None = None
            while i < total:
                current = lines[i]
                bullet = RE_BULLET.match(current)
                ordered = RE_ORDERED.match(current)
                if bullet or ordered:
                    match = bullet or ordered
                    indent = len(match.group(1))
                    if base_indent is None:
                        base_indent = indent
                    items.append([max(0, (indent - base_indent) // 2),
                                  ordered is not None,
                                  match.group(2).strip(),
                                  []])
                    i += 1
                    continue
                if not current.strip():
                    look = i + 1
                    while look < total and not lines[look].strip():
                        look += 1
                    if look < total and _is_list_line(lines[look]):
                        i = look
                        continue
                    break
                if current[:1].isspace() and items:
                    items[-1][3].append(current.strip())
                    i += 1
                    continue
                break
            out.append(_render_items(items))
            continue

        buffer = []
        while i < total and not starts_block(i):
            buffer.append(lines[i].strip())
            i += 1
        if buffer:
            out.append("<p>%s</p>" % inline(" ".join(buffer)))
        else:
            i += 1

    return "\n".join(out), headings


# ---------------------------------------------------------------------------
# Modelos de página (mesma marcação das páginas escritas à mão)
# ---------------------------------------------------------------------------

NAV = [
    ("index.html", "Início", "inicio"),
    ("sobre.html", "Sobre", "sobre"),
    ("shows.html", "Shows", "shows"),
    ("projetos.html", "Projetos", "projetos"),
    ("grimorio.html", "Grimório", "grimorio"),
    ("contato.html", "Contato", "contato"),
    ("apoie.html", "Apoie", "apoie"),
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def page_head(title: str, description: str, canonical: str, prefix: str, current: str) -> str:
    url_title = esc(title)
    url_desc = esc(description)
    og_image = SITE_URL + "assets/images/og.png"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{url_title}</title>
<meta name="description" content="{url_desc}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#08080a">
<meta name="author" content="Arthur Rodrigues">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Cod Rebel DJ">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{url_title}">
<meta property="og:description" content="{url_desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Cod Rebel DJ · Rock, Funk e Electronic">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{url_title}">
<meta name="twitter:description" content="{url_desc}">
<meta name="twitter:image" content="{og_image}">

<link rel="icon" href="{prefix}assets/images/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
<script>document.documentElement.classList.add('js');</script>
</head>
<body>

<a class="skip" href="#conteudo">Pular para o conteúdo</a>

<header class="site-head">
  <div class="wrap site-head__inner">
    <a class="brand" href="{prefix}index.html">
      <span class="brand__mark" aria-hidden="true">//</span>
      <span>Cod Rebel DJ<span class="brand__sub">Rock · Funk · Electronic</span></span>
    </a>

    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="menu">
      <span class="nav-toggle__bars" aria-hidden="true"><i></i><i></i><i></i></span>
      Menu
    </button>

    <a class="btn btn--primary head__cta" href="{prefix}contato.html#booking">Contratar</a>

    <nav class="nav" id="menu" aria-label="Navegação principal">
      <ul class="nav__list">
{nav_items(prefix, current)}      </ul>
    </nav>
  </div>
</header>
"""


def nav_items(prefix: str, current: str) -> str:
    lines = []
    for href, label, key in NAV:
        attrs = ' aria-current="page"' if key == current else ""
        lines.append('        <li><a class="nav__link" href="%s%s"%s>%s</a></li>'
                     % (prefix, href, attrs, label))
    return "\n".join(lines) + "\n"


def site_footer(prefix: str) -> str:
    links = "\n".join(
        '          <li><a href="%s%s">%s</a></li>' % (prefix, href, label)
        for href, label, _ in NAV
    )
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-col">
        <p class="foot-brand"><span>//</span> Cod Rebel DJ</p>
        <p>Rock para bater. Funk para dançar. Industrial para pesar. Tecnologia para experimentar.</p>
        <p class="small"><span class="status-dot" aria-hidden="true"></span>Em construção, documentado em tempo real.</p>
      </div>

      <div class="foot-col">
        <h2>Navegar</h2>
        <ul class="foot-list">
{links}
        </ul>
      </div>

      <div class="foot-col">
        <h2>Fontes e registros</h2>
        <ul class="foot-list">
          <li><a href="{prefix}docs/cod-rebel-dj.md">docs/cod-rebel-dj.md</a></li>
          <li><a href="{prefix}docs/aprendizados.md">docs/aprendizados.md</a></li>
          <li><a href="{REPO_URL}" rel="noopener">Repositório no GitHub</a></li>
          <li><a href="https://github.com/cod-rebel-rider/hercules-dj-control-air-docs" rel="noopener">Mapeamento Hercules DJ Control Air</a></li>
        </ul>
      </div>
    </div>

    <div class="foot-bottom">
      <p>© 2026 Cod Rebel DJ · Arthur Rodrigues</p>
      <ul>
        <li>Código: MIT</li>
        <li>Identidade e conteúdo: todos os direitos reservados</li>
      </ul>
    </div>
  </div>
</footer>
"""


def page(title: str, description: str, canonical: str, current: str,
         prefix: str, content: str) -> str:
    return "\n".join([
        page_head(title, description, canonical, prefix, current),
        '<main id="conteudo">',
        content,
        "</main>",
        site_footer(prefix),
        '<script src="%sassets/js/main.js" defer></script>' % prefix,
        "</body>",
        "</html>",
        "",
    ])


def crumbs(prefix: str, title: str) -> str:
    return f"""<nav aria-label="Trilha de navegação">
  <ol class="crumbs">
    <li><a href="{prefix}index.html">Início</a></li>
    <li><a href="{prefix}grimorio.html">Grimório</a></li>
    <li>{esc(title)}</li>
  </ol>
</nav>"""


def build_page_index(ordered: list[Doc]) -> str:
    """Índice gerado a partir do registro de documentos (docs/*.md)."""
    groups = []
    for key, name, description in CATEGORIES:
        docs = [doc for doc in ordered if doc.cat == key]
        if not docs:
            continue
        cards = []
        for pos, doc in enumerate(docs, start=1):
            cards.append(f"""        <article class="row">
          <p class="row__index">/{pos:02d}</p>
          <h3 class="row__title"><a href="grimorio/{doc.slug}.html">{esc(doc.title)}</a></h3>
          <p class="row__text">{esc(doc.summary)}</p>
          <p class="row__meta">Fonte: {esc(doc.source)}</p>
        </article>""")
        groups.append(f"""      <section style="margin-bottom: clamp(2rem, 5vw, 3rem);">
        <h2 class="label">// {esc(name)}</h2>
        <p class="muted small" style="margin: -.4rem 0 1rem;">{esc(description)}</p>
        <div class="rows rows--2">
{chr(10).join(cards)}
        </div>
      </section>""")

    listing = "\n".join(
        "            <p class=\"terminal__line\"><a href=\"grimorio/%s.html\">%s</a>"
        "<span class=\"c\">  %s</span></p>" % (doc.slug, esc(Path(doc.source).name), esc(doc.title))
        for doc in ordered
    )

    content = f"""  <section class="section">
    <div class="wrap">
{crumbs("", "Grimório")}

      <div class="section__head">
        <p class="label">// Grimório <span>· caderno de campo</span></p>
        <h1 class="section__title">Caderno de campo, aberto</h1>
        <p class="lede" style="margin-top: 1rem;">
          Aqui está o que eu escrevo sobre o trabalho, do jeito que eu escrevi: identidade,
          repertório, shows, equipamentos, projetos e o que eu aprendi apanhando. Não é bastidor
          editado, inclusive nas partes que ainda estão em branco.
        </p>
      </div>

      <div class="split">
        <div class="terminal">
          <div class="terminal__bar">
            <span>ls -1 docs/</span>
            <span>{len(ordered)} arquivos</span>
          </div>
          <div class="terminal__body">
{listing}
          </div>
        </div>

        <div class="note">
          <p class="note__title">O que tem aqui dentro</p>
          <p>
            Identidade, repertório, trajetória, shows, equipamentos, projetos e os aprendizados
            técnicos. Também tem espaço em branco: parte disso ainda está sendo preenchida.
          </p>
          <p class="small">
            Nada foi inventado para ficar bonito. Se a informação não existe, o buraco aparece.
          </p>
        </div>
      </div>

      <div style="margin-top: clamp(2.5rem, 6vw, 4rem);">
{chr(10).join(groups)}
      </div>
    </div>
  </section>"""

    return page(
        "Grimório · documentação aberta do Cod Rebel DJ",
        "Documentação do trabalho do Cod Rebel DJ: identidade, repertório, trajetória, shows, "
        "equipamentos, projetos e aprendizados, publicados sem filtro.",
        SITE_URL + "grimorio.html",
        "grimorio",
        "",
        content,
    )


def build_pager(ordered: list[Doc], position: int) -> str:
    items = []
    if position > 0:
        prev = ordered[position - 1]
        items.append('    <li><a href="%s.html"><span class="pager__dir">&#8592; Anterior</span>'
                     '<span class="pager__name">%s</span></a></li>' % (prev.slug, esc(prev.title)))
    if position + 1 < len(ordered):
        nxt = ordered[position + 1]
        items.append('    <li class="pager--next"><a href="%s.html">'
                     '<span class="pager__dir">Pr&#243;ximo &#8594;</span>'
                     '<span class="pager__name">%s</span></a></li>' % (nxt.slug, esc(nxt.title)))
    if not items:
        return ""
    return '      <ul class="pager">\n%s\n      </ul>' % "\n".join(items)


def build_doc_page(doc: Doc, markdown: str, position: int, ordered: list[Doc]) -> str:
    body, headings = md_to_html(markdown, skip_first_h1=True)
    cat_name = dict((key, name) for key, name, _ in CATEGORIES).get(doc.cat, doc.cat)
    updated = br_date(git_date(doc.source)) or "não registrada"
    words = len(re.findall(r"\S+", strip_markup(markdown)))
    minutes = max(1, round(words / 200))

    sections = [(anchor, text) for level, anchor, text in headings if level == 2]
    toc = ""
    if len(sections) >= 3:
        links = "\n".join(
            '            <li><a href="#%s">%s</a></li>' % (anchor, esc(text))
            for anchor, text in sections
        )
        toc = ('      <nav class="note" aria-label="Seções deste documento"'
               ' style="margin-bottom: clamp(1.75rem, 4vw, 2.5rem);">\n'
               '        <p class="note__title">Neste documento</p>\n'
               '        <ol class="foot-list">\n'
               + links +
               '\n        </ol>\n      </nav>\n')

    content = f"""  <section class="section">
    <div class="wrap">
{crumbs("../", doc.title)}

      <header class="doc-head">
        <p class="label">// Grimório <span>· {esc(cat_name)}</span></p>
        <h1 class="section__title section__title--mono">{esc(doc.title)}</h1>
        <p class="lede" style="margin-top: 1rem;">{esc(doc.summary)}</p>
        <ul class="doc-head__meta">
          <li><b>Fonte</b> <a href="../{esc(doc.source)}">{esc(doc.source)}</a></li>
          <li><b>Atualizado</b> {esc(updated)}</li>
          <li><b>Leitura</b> ~{minutes} min</li>
        </ul>
      </header>

{toc}      <article class="prose">
{body}
      </article>

{build_pager(ordered, position)}
    </div>
  </section>"""

    return page(
        "%s · Grimório Cod Rebel DJ" % doc.title,
        doc.summary,
        "%sgrimorio/%s.html" % (SITE_URL, doc.slug),
        "grimorio",
        "../",
        content,
    )


# ---------------------------------------------------------------------------
# sitemap.xml e robots.txt
# ---------------------------------------------------------------------------

STATIC_PAGES = [
    ("index.html", ""),
    ("sobre.html", "sobre.html"),
    ("shows.html", "shows.html"),
    ("projetos.html", "projetos.html"),
    ("projetos/bailao-do-rock/index.html", "projetos/bailao-do-rock/"),
    ("projetos/sets/index.html", "projetos/sets/"),
    ("grimorio.html", "grimorio.html"),
    ("contato.html", "contato.html"),
    ("apoie.html", "apoie.html"),
]


def build_sitemap(ordered: list[Doc]) -> str:
    urls = []

    def add(file_path: str, loc_path: str) -> None:
        urls.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n  </url>"
                    % (SITE_URL, loc_path, git_date(file_path) or TODAY))

    for file_path, loc_path in STATIC_PAGES:
        if (ROOT / file_path).is_file():
            add(file_path, loc_path)
    for doc in ordered:
        add("grimorio/%s.html" % doc.slug, "grimorio/%s.html" % doc.slug)

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def build_robots() -> str:
    return "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % SITE_URL


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def main() -> int:
    by_slug = {doc.slug: doc for doc in DOCS}
    ordered = [by_slug[slug] for slug in CURATED_ORDER if slug in by_slug]

    missing = [doc.source for doc in ordered if not (ROOT / doc.source).is_file()]
    if missing:
        print("AVISO: documentos registrados mas ausentes: %s" % ", ".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for position, doc in enumerate(ordered):
        source_path = ROOT / doc.source
        if not source_path.is_file():
            continue
        markdown = source_path.read_text(encoding="utf-8")
        target = OUT_DIR / ("%s.html" % doc.slug)
        target.write_text(build_doc_page(doc, markdown, position, ordered), encoding="utf-8")
        written.append(target.relative_to(ROOT))

    index_target = ROOT / "grimorio.html"
    index_target.write_text(build_page_index(ordered), encoding="utf-8")
    written.append(index_target.relative_to(ROOT))

    (ROOT / "sitemap.xml").write_text(build_sitemap(ordered), encoding="utf-8")
    (ROOT / "robots.txt").write_text(build_robots(), encoding="utf-8")
    written.append(Path("sitemap.xml"))
    written.append(Path("robots.txt"))

    registered = {Path(doc.source).name for doc in ordered}
    for name in sorted(path.name for path in DOCS_DIR.glob("*.md")):
        if name not in registered:
            print("AVISO: docs/%s ainda não está no grimório "
                  "(adicione em DOCS e CURATED_ORDER neste script)." % name)

    print("%d arquivos gerados:" % len(written))
    for item in written:
        print("  %s" % item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())





