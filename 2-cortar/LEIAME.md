# Corte a laser

Envie os DXF (1:1, em milímetros) e o `pranchas_corte_mvp.pdf`, que tem cotas gerais de cada chapa para conferência.

| Arquivo | Qtd | Material | Espessura | Tamanho (mm) | Observação |
| --- | --- | --- | --- | --- | --- |
| `chapa_base_lancador_4mm.dxf` | 1 | Alumínio 5052 ou 6061 | 4 mm | 422 × 312 | Base do andar do lançador. No MVP fica sobre as 4 pernas. |
| `plataforma_4mm.dxf` | 1 | Alumínio 5052 ou 6061 | 4 mm | 197 × 156 | Plataforma giratória sobre o lazy susan. |
| `placa_lateral_6mm.dxf` | 2 | Alumínio 6061 | 6 mm | 347 × 310 | As duas placas da cabeça são a mesma peça. Pivô com furo em D para o semi-eixo; a roda de baixo usa furos oblongos para o vão. |
| `garfo_6mm.dxf` | 2 | Alumínio 6061 | 6 mm | 235 × 60 | Os dois garfos do tilt são a mesma peça. |
| `manivela_tilt_6mm.dxf` | 1 | Alumínio 6061 | 6 mm | 87 × 42 | Furo em D para o semi-eixo Ø8 com chato de 7 mm. |
| `disco_inercia_3mm.dxf` | 4 | Aço 1020 | 3 mm | 120 × 120 | Furo em D para o eixo Ø12 com chato (11 mm). 2 por roda. |

## Antes de mandar cortar

Os furos das peças compradas seguem cotas de catálogo. **Confira com a peça na mão:**

- **KFL001:** 2 furos M6 a 48 mm. Na placa lateral os furos são de Ø7; os da roda de baixo são oblongos para ajustar o vão.
- **KFL08:** 2 furos M4 a 37 mm. No garfo os furos são de Ø4,5.
- **Lazy susan Ø150:** a furação varia por fabricante. Base: 4 furos a r 66, girados 45°. Plataforma: 4 furos a r 60. Se não bater, ajuste `lancador.py` ou fure na montagem.
- **Motor 4250 (X-mount):** 4 oblongos M3 a r 19, alinhados com a correia: dão ±3 mm para esticar.
- **NEMA17:** furação padrão de 31 mm, M3.
- **Furos em D:** discos de inércia (eixo Ø12, 11 mm entre faces), manivela e pivô das placas laterais (eixo Ø8, 7 mm). Peça ao serviço para não arredondar o canto do D.

## Depois do corte

- Tire as rebarbas dos dois lados e quebre os cantos vivos.
- Nenhuma chapa do MVP precisa de rosca: todos os furos são passantes, com porca.
- Os dois garfos e as duas placas laterais são peças iguais: monte uma de cada lado.
