# assets/images

Registros visuais do projeto.

## O que existe hoje

| Arquivo | Uso |
| --- | --- |
| `favicon.svg` | ícone do site (`//_`) |
| `favicon.png` | ícone do site em PNG, usado por navegadores que não leem SVG |
| `logo.png` | marca rasterizada, 1254×1254 (usada no topo da home) |
| `logo-cod-rebel-dj.svg` | marca escrita em SVG, para presskit e divulgação |
| `sinal.svg` | gráfico decorativo de sinal/onda (usado no terminal da home) |
| `cod-rebel-dj-01.png` | primeiro registro visual real publicado (home, seção 03) |
| `registro-placeholder.svg` | moldura de **registro visual pendente** |
| `og.png` | imagem de compartilhamento (Open Graph), 1200×630 |

Há duas marcas no projeto, com propósitos diferentes: `logo.png` é a imagem
usada na interface e `logo-cod-rebel-dj.svg` é a versão vetorial para
divulgação. As duas devem receber o mesmo desenho.

`og.png` é **gerado** a partir de `og.svg` (o SVG é a fonte, o PNG é o arquivo
usado pelas redes sociais, que não leem SVG). Para regerar:

```bash
rsvg-convert -w 1200 -h 630 -b '#08080a' assets/images/og.svg -o assets/images/og.png
```

`registro-placeholder.svg` **não é um registro**: é um espaço reservado, marcado
como pendente. Ele deve ser substituído quando existirem fotos e vídeos reais.

## O que deve entrar aqui (quando existir)

- fotos de apresentações (com crédito do fotógrafo);
- registros de palco, mesa, controladora e estrutura;
- flyers e artes de eventos;
- frames/prints de VS, se forem materiais próprios.

## Regras

- **não** inserir fotos de terceiros sem autorização;
- **não** usar banco de imagens genérico para representar o artista;
- otimizar antes de commitar (JPG/WebP, largura máxima ~2000px);
- nomear em minúsculas, sem espaços e com data quando fizer sentido
  (ex.: `2026-moto-rock-cia-01.jpg`);
- toda imagem precisa de `alt` descritivo no HTML (ou `alt=""` se for decorativa).
