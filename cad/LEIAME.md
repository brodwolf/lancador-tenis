# Lançador de bolas de tênis — modelo 3D

Modelo paramétrico feito em CadQuery (Python). Unidades em milímetros.
Origem no chão, no centro da estrutura: **x** = largura, **y** = profundidade (+ para a frente), **z** = altura.

## Pastas

| Pasta | O que tem | Para quem |
| --- | --- | --- |
| `montagem/lancador_montagem.step` | Montagem completa com cores e nomes de peça | Abra no Fusion 360, FreeCAD, Onshape, SolidWorks |
| `impressao_3d/` | STL (para o fatiador) e STEP (para editar) de cada peça impressa | Sua impressora |
| `corte_laser/` | DXF 1:1 em mm de cada chapa + `pranchas_corte_laser.pdf` com cotas gerais | Serviço de corte a laser |
| `usinagem/` | STEP dos eixos | Torno ou barra cortada em casa |
| `visualizador/` | GLB da montagem (abre no visualizador 3D do Windows ou em gltf-viewer.donmccurdy.com) | Conferir a montagem |
| `lista_de_pecas.csv` | Todas as peças com categoria, material, quantidade e arquivo | Planilha de compras |
| `lancador.py`, `exportar.py`, `verificar.py` | Código-fonte | Mudar cotas e gerar tudo de novo |

## Antes de mandar cortar as chapas

Os furos de peças compradas seguem cotas de catálogo. **Confira com a peça na mão** antes de enviar os DXF:

- **KFL001** (mancal das rodas): 2 furos M6, entre centros 48 mm. Na placa lateral: furos Ø7.
- **KFL08** (mancal do tilt): 2 furos M4, entre centros 37 mm. No garfo: furos Ø4,5.
- **Lazy susan 300 mm**: a furação varia por fabricante. Os furos da placa do pan (r 135) e da plataforma (r 125) são sugestões; ajuste no `lancador.py` ou fure na montagem.
- **Motor 4250 (X-mount)**: a placa do motor tem 4 furos oblongos de r 16 a 22 mm, que cobrem os X-mounts comuns.
- **NEMA17**: padrão 31 mm entre furos, M3 (já no modelo).
- **Disco de inércia**: furo em D para o eixo Ø12 com chato (11,1 mm entre a face plana e o lado oposto).

O laser não faz rosca: rosqueie em casa os furos indicados no documento do projeto (seção 16).

## Imprimindo

- As peças saem na **posição de montagem**: gire na mesa do fatiador para a melhor orientação.
- PETG em tudo, menos a banda das rodas (TPU 95A). Peças expostas ao sol podem ser em ASA.
- `nucleo_roda`: 6 perímetros, 60% gyroid. `banda_roda`: 4 perímetros, 50% gyroid, 20–30 mm/s.
- `rotor_agitador` tem Ø280 mm: precisa de mesa ≥ 280 mm (ou corte o disco em acrílico 6 mm e imprima só a cúpula).
- `aro_plataforma` e `rampa_hopper` já vêm em 4 partes para caber em mesas de 220–250 mm.

## Mudanças em relação ao documento do projeto

O modelo verificou todas as posições de pan (±30°) e tilt (±15°) sem nenhuma interferência. Para isso, algumas cotas mudaram:

- Eixo do pan a **35 mm** atrás do centro (era 60). Plataforma **Ø300** (era Ø320), redução da correia ~23:1.
- Mancais KFL001 **por dentro** das placas laterais; vão interno entre placas **90 mm**.
- Motores da classe **4250** (Ø42 × 50 mm), presos numa placa 76 × 76 × 5 com 4 espaçadores de 89 mm. Um 5055 também serve, mas a cabeça fica 20 mm mais larga de cada lado.
- Rodas sem cubo flange: os discos de aço têm furo em D e o eixo Ø12 × 128 tem um chato.
- Pivô do tilt com semi-eixos Ø8 × 45 presos por 2 colares cada (sem SHF8).
- Agitador com disco Ø280 e motor **embaixo** da placa do hopper; hopper preso por 4 manípulos M8 no topo das colunas.
- Paredes do hopper 470 × 220 e 364 × 220; telas de proteção 390 × 506 e 488 × 506.
- Suportes do eixo das rodas de transporte em chapa plana de aço 4 mm (sem dobra).

## Gerar de novo depois de mudar cotas

```
pip install cadquery ezdxf matplotlib
python3 exportar.py      # recria a pasta saida/
python3 verificar.py     # confere interferências em 7 posições e o caminho da bola
```

Os parâmetros principais estão no topo de `lancador.py` (tamanho da estrutura, altura do pivô, diâmetro e vão das rodas, posição do eixo do pan etc.).

## Simplificações do modelo

Cantoneiras e parafusos da estrutura, fiação, polias da correia ômega e o servo são representações simples. Os rolamentos e motores têm só as dimensões externas.
