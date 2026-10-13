# Usinagem

Os dois tipos de eixo saem de barra retificada (eixo linear), cortada no comprimento. Dá para fazer em casa com serra, lima e macho; uma tornearia faz em minutos.

| Arquivo | Qtd | Barra | Comprimento | O que fazer |
| --- | --- | --- | --- | --- |
| `eixo_roda*.step` | 2 | Ø12 h6 retificado (eixo linear), aço 1045 | 134 mm | Chato de 1 mm (11 mm entre a face plana e o lado oposto) no comprimento todo, para os discos de aço, as polias e o disco de sinal. Lima, esmeril ou fresa. |
| `semi_eixo*.step` | 2 | Ø8 retificado (eixo linear) | 50 mm (+x) e 65 mm (−x) | Os dois levam chato de 1 mm (7 mm entre faces) no comprimento todo: o chato encaixa no furo em D das placas laterais e da manivela, e é por ele que o torque do tilt chega à cabeça. O de 65 mm leva rosca M4 × 10 mm na ponta: um M4×10 com arruela segura a manivela. |

## Dicas

- Corte 1 mm mais longo e acerte na lima ou no esmeril, sem esquentar demais o aço retificado.
- Faça o chato com a barra presa na morsa, conferindo com paquímetro: 11,0 mm (Ø12) e 7,0 mm (Ø8). Teste no furo em D da chapa antes de terminar.
- A rosca M4 da ponta do semi-eixo de 65 mm: centro com punção, broca 3,3 mm × 12 mm, macho M4.
- `semi_eixo_1.step` é o de 50 mm (lado +x); `semi_eixo_2.step` é o de 65 mm (lado −x, com a manivela).
