# Lançador de Bolas de Tênis

Máquina de treino portátil, montada em três andares que se separam. Tem duas rodas de velocidade independente para controlar o spin, cabeça com giro e inclinação motorizados, cesto de tela dobrável e baterias Makita 18 V. Projeto aberto, pensado para ser construído com impressão 3D, corte a laser e peças de prateleira.

**Apresentação do projeto:** https://brodwolf.github.io/lancador-tenis/

![Demonstração do site](assets/img/demo.mp4)

![Montagem completa](assets/img/perspectiva.webp)

| Especificação | Valor |
| --- | --- |
| Velocidade da bola | 30–120 km/h |
| Spin | −2.500 rpm (slice) a +3.000 rpm (topspin) |
| Giro / inclinação | ±12,5° / 0° a +30° (máquina no centro da linha de fundo) |
| Cesto | Tela dobrável, ~120 bolas |
| Autonomia | 2,3–4,5 h com 2 baterias Makita 5,0 Ah |
| Dimensões | 32 × 43 cm de base; ~82 cm de altura com o cesto dobrado, 104,5 cm aberto; ~20 kg sem carenagem |
| Carenagem | Material a definir; só STEP de referência |
| Custo estimado | R$ 4,6–8,1 mil, sem baterias e sem carenagem |

## O que tem aqui

| Pasta | Conteúdo |
| --- | --- |
| `index.html`, `assets/` | Página de apresentação: modelo 3D interativo (com e sem carenagem) e simulação na quadra com vento (GitHub Pages) |
| `PROJETO.md` | Memorial técnico em Markdown (sem preços e sem próximos passos) |
| `cad/montagem/` | Montagem em STEP com e sem carenagem (Fusion 360, FreeCAD, Onshape, SolidWorks) |
| `cad/impressao_3d/` | STL e STEP das peças impressas (as `_espelhada` são a cópia do outro lado) |
| `cad/corte_laser/` | DXF das 10 chapas (mm, 1:1) e pranchas em PDF |
| `cad/carenagem/` | STEP dos painéis externos, material a definir |
| `cad/usinagem/` | Eixos em STEP |
| `cad/lista_de_pecas.csv` | Todas as peças com categoria, material e quantidade |
| `cad/lancador.py` | Modelo paramétrico em CadQuery |

A versão anterior, uma estrutura única de 55 × 45 × 120 cm, está no branch [`v1`](../../tree/v1).

## Gerar os arquivos de novo

```
pip install cadquery ezdxf matplotlib
cd cad
python3 exportar.py      # recria STEP, STL, DXF, GLB e a lista de peças em cad/saida/
python3 verificar.py     # confere folgas em 18 posições de giro e inclinação, o caminho da bola e todas as peças entre si
```

Os parâmetros principais ficam no topo de `cad/lancador.py`: tamanho da carenagem, alturas dos andares, linha da bola, rodas e vão, motores e faixas de giro e inclinação.

## Antes de mandar cortar

Os furos de peças compradas seguem cotas de catálogo. Confira com a peça na mão:

- KFL001: 48 mm entre furos, M6
- KFL08: 37 mm entre furos, M4
- lazy susan Ø150: a furação varia por fabricante
- X-mount do motor 4250

Detalhes em `cad/LEIAME.md`.
