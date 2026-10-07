# Lançador de bolas de tênis, versão 2 (compacta, por andares)

Modelo paramétrico feito em CadQuery (Python). Unidades em milímetros.
Origem no chão, no centro da máquina: **x** = largura, **y** = profundidade (+ para a frente), **z** = altura.

A máquina tem três andares que se encaixam com pinos de centragem e travam com fechos de pressão.

- **Controle:** baterias, caixa IP65 e rodas de transporte.
- **Lançador:** giro, inclinação, cabeça, painel traseiro, semáforo e antenas.
- **Alimentador:** disco agitador e rampas.

O cesto de tela dobrável vai por cima dos três.

## Pastas

| Pasta | O que tem | Para quem |
| --- | --- | --- |
| `montagem/lancador_montagem.step` | Montagem completa **com** carenagem | Ver como fica (Fusion 360, FreeCAD, Onshape, SolidWorks) |
| `montagem/lancador_montagem_sem_carenagem.step` | Mesma montagem **sem** carenagem | Montar e conferir a estrutura |
| `corte_laser/` | DXF 1:1 em mm de cada chapa + `pranchas_corte_laser.pdf` com cotas gerais | Serviço de corte a laser |
| `impressao_3d/` | STL (fatiador) e STEP (editar) de cada peça impressa | Sua impressora |
| `usinagem/` | STEP dos eixos | Torno ou barra cortada em casa |
| `carenagem/` | STEP dos painéis externos | Quem for fazer o molde ou os painéis |
| `visualizador/` | GLB da montagem + `pecas.json` (usados pelo site) | Conferir a montagem |
| `lista_de_pecas.csv` | Todas as peças com categoria, material, quantidade e arquivo | Planilha de compras |
| `lancador.py`, `exportar.py`, `verificar.py` | Código-fonte | Mudar cotas e gerar tudo de novo |

## Carenagem: material a definir

A carenagem tem três painéis (um por andar) e a tampa das baterias. **Ela não tem DXF**, porque ainda não se sabe se será molde injetado, termoformada, impressa em partes ou chapa composta.

Os STEP têm 3 mm de parede, cantos de raio 30 e todos os recortes:

- janela da cabeça, semáforo, painel traseiro
- furos das antenas e dos eixos das rodas
- rasgos das abraçadeiras da alça

Servem de base para o molde ou para refazer os painéis no material escolhido. A estrutura não depende da carenagem: a máquina funciona sem ela.

## Antes de mandar cortar as chapas

Os furos de peças compradas seguem cotas de catálogo. **Confira com a peça na mão** antes de enviar os DXF:

- **KFL001** (mancais das rodas): 2 furos M6 a 48 mm. Na placa lateral os furos são de Ø7. A roda de baixo usa furos oblongos, para ajustar o vão.
- **KFL08** (mancais do tilt): 2 furos M4 a 37 mm. No garfo os furos são de Ø4,5.
- **Rolamento lazy susan redondo Ø150**:
  - a furação varia por fabricante; ajuste no `lancador.py` ou fure na montagem
  - base do andar: 4 furos a r 66, girados 45°
  - plataforma: 4 furos a r 60
- **Motor 4250 (X-mount)**: 4 oblongos M3 a r 19, alinhados com a correia, que dão ±3 mm para esticar.
- **Correias**: HTD 3M de 9 mm, fechadas.
  - roda de cima: **600-3M-9**
  - roda de baixo: **288-3M-9**
  - a posição dos motores sai do comprimento da correia; se mudar a correia, mude `CORREIA_A`/`CORREIA_B`
- **NEMA17**: furação padrão de 31 mm, M3.
- **Disco de inércia**: furo em D para o eixo Ø12 com chato (11,1 mm entre a face plana e o lado oposto).
- **Manivela do tilt**: furo em D para o semi-eixo Ø8 com chato de 7 mm.

O laser não faz rosca: rosqueie em casa os furos indicados no documento do projeto.

## Imprimindo

- As peças saem na **posição de montagem**: gire na mesa do fatiador para a melhor orientação.
- Use PETG em tudo, menos a banda das rodas (TPU 95A). Peças expostas ao sol podem ser em ASA.
- `nucleo_roda`: 6 perímetros, 60% gyroid. `banda_roda`: 4 perímetros, 50% gyroid, 20–30 mm/s.
- `rotor_agitador` tem Ø220 mm: cabe em mesa de 235 mm.
- As rampas do alimentador vêm em 4 partes. As duas da frente têm 155 × 256 mm: precisam de mesa de 256 mm ou de um corte a mais.
- Arquivos com `_espelhada` no nome são a cópia do outro lado. Por exemplo, a abraçadeira da alça e o suporte da antena do lado esquerdo.

## Movimentos

| Eixo | Faixa | Acionamento |
| --- | --- | --- |
| Giro (pan) | ±12,5° | NEMA17 com fuso Tr8×8 de 100 mm empurrando um pino a 102 mm do eixo |
| Inclinação (tilt) | 0° a +30° | NEMA17 com fuso Tr8×2 de 100 mm (não volta sozinho), porca com rasgo e manivela de 64 mm |
| Rodas | 2 motores 4250 | Correias HTD 3M, polias de 20 dentes (1:1) |

## Gerar de novo depois de mudar cotas

```
pip install cadquery ezdxf matplotlib
python3 exportar.py      # recria a pasta saida/
python3 verificar.py     # confere as folgas em 18 posições de giro e inclinação e o caminho da bola
```

Os parâmetros principais estão no topo de `lancador.py`: tamanho da carenagem, alturas dos andares, altura da linha da bola, rodas e vão, posição dos motores e faixas de giro e inclinação.

## Simplificações do modelo

São representações simples:

- parafusos, fiação e placas eletrônicas
- servo, tela e baterias
- tela do cesto

Rolamentos e motores têm só as dimensões externas. O fuso dos NEMA17 aparece como uma barra lisa.
