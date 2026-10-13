# Impressão 3D

19 arquivos, 23 peças. Cada peça tem o STL (para o fatiador) e o STEP (para editar).

Os arquivos saem na **posição de montagem**: gire na mesa do fatiador para a orientação da tabela. Massa e tempo são estimativas para bico de 0,4 mm e camada de 0,2 mm; o tempo real depende da impressora.

## Configuração geral

- **PETG:** 235–245 °C, mesa 75–85 °C, ventilação 30–50%. Seque o filamento se ele estalar.
- **TPU 95A:** 220–230 °C, 20–30 mm/s, retração curta (ou desligada em extrusora Bowden).
- **Sem suporte** em todas as peças, na orientação da tabela.
- **Brim** de 5 mm nas peças grandes e planas (tampas e carenagens), para não descolar.
- Peças que vão ficar ao sol podem ser feitas em **ASA** com as mesmas configurações de perímetro e preenchimento.

## Peças

| Arquivo | Qtd | Material | Tamanho (mm) | Massa (g) | Tempo (h) | Na mesa | Configuração | Observação |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nucleo_roda.stl` | 2 | PETG (ou ASA / PA-CF) | 134 × 134 × 32 | 435 | 22–33 | deitado, face plana na mesa | 0,2 mm · 6 perímetros · 60% gyroid · 5 camadas de topo e fundo | A peça mais longa: comece por ela. O furo central tem folga; quem trava no eixo são os discos de aço. |
| `banda_roda.stl` | 2 | TPU 95A | 150 × 150 × 40 | 92 | 5–7 | deitada | 0,2 mm · 4 perímetros · 50% gyroid · 20–30 mm/s · retração curta | Encaixa nas 8 chavetas do núcleo. Cola PU na junção é opcional. |
| `disco_sinal.stl` | 2 | PETG | 40 × 40 × 8 | 9 | < 1,5 | face lisa na mesa, bolsos dos ímãs para cima | 0,2 mm · 4 perímetros · 40% | 2 ímãs Ø6×3 por disco, com o mesmo polo para fora, colados com epóxi. Trava no eixo com um grub M3×6 que abre a própria rosca. |
| `berco.stl` | 1 | PETG | 90 × 77 × 22 | 103 | 5–8 | base plana na mesa | 0,2 mm · 4 perímetros · 40% | 4 insertos M4 nas faces laterais (ponta do ferro a ~230 °C). |
| `braco_empurrador.stl` | 1 | PETG | 92 × 27 × 22 | 7 | < 1,5 | deitado, face larga na mesa | 0,2 mm · 100% | Cole 2 mm de TPU ou borracha na face que toca a bola. Prenda no horn de alumínio do servo com 2 parafusos M3×8 (fure Ø3,2 no cubo, na furação do horn). |
| `funil_cabeca.stl` | 1 | PETG | 145 × 90 × 19 | 18 | < 1,5 | boca larga na mesa | 0,2 mm · 3 perímetros · 20% | Paredes finas, sem suporte. Preso por 2 varetas M4. |
| `carenagem_roda_sup.stl` | 1 | PETG ou ASA | 170 × 111 × 89 | 64 | 3–5 | em pé, com o arco na mesa | 0,2 mm · 3 perímetros · 20% | Presa por 2 varetas M4 entre as placas. |
| `carenagem_roda_inf.stl` | 1 | PETG ou ASA | 170 × 111 × 89 | 64 | 3–5 | em pé, com o arco na mesa | 0,2 mm · 3 perímetros · 20% | Igual à de cima, do outro lado da linha da bola. |
| `tampa_correia_sup.stl` | 1 | PETG | 253 × 201 × 27 | 43 | 2–3 | face externa na mesa, aberta para cima | 0,2 mm · 3 perímetros · 20% | 253 × 201 mm: precisa de mesa de 256 mm. Em mesa menor, corte em duas no fatiador e cole com epóxi. |
| `tampa_correia_inf.stl` | 1 | PETG | 152 × 47 × 27 | 22 | 1–2 | face externa na mesa, aberta para cima | 0,2 mm · 3 perímetros · 20% | Presa com 2 parafusos M3×35 + porca, como a de cima. |
| `suporte_motor_tilt.stl` | 1 | PETG | 90 × 60 × 58 | 24 | 1–2 | aba do garfo na mesa | 0,2 mm · 5 perímetros · 40% | No garfo −x com 2 parafusos M4×16; o NEMA17 do tilt entra com 4 M3×10. |
| `suporte_motor_giro.stl` | 1 | PETG | 52 × 48 × 20 | 12 | < 1,5 | base na mesa | 0,2 mm · 5 perímetros · 40% | Na chapa de base com 2 M4×12; o NEMA17 do giro entra com 4 M3×8. |
| `mancal_fuso_giro.stl` | 1 | PETG | 48 × 44 × 16 | 21 | 1–2 | base na mesa | 0,2 mm · 5 perímetros · 40% | Rolamento 608 prensado (aqueça a peça a ~60 °C se estiver duro). Na chapa com 2 M4×12. |
| `bloco_porca_tilt.stl` | 1 | PETG | 28 × 28 × 24 | 16 | < 1,5 | rasgo para cima | 0,2 mm · 6 perímetros · 50% | A flange da porca de latão entra com 4 M3×12 nos furos-guia de Ø2,5. |
| `bloco_porca_giro.stl` | 1 | PETG | 28 × 28 × 24 | 16 | < 1,5 | rasgo para cima | 0,2 mm · 6 perímetros · 50% | Igual ao do tilt; o rasgo recebe o pino do giro. |
| `suporte_servo.stl` | 1 | PETG | 64 × 44 × 40 | 20 | 1–2 | placa das orelhas na mesa | 0,2 mm · 5 perímetros · 40% | Orelhas do servo com 4 M3×12 + porca; na placa lateral com 2 M4×50. |
| `suporte_trilho.stl` | 1 | PETG | 90 × 24 × 14 | 20 | 1–2 | deitado | 0,2 mm · 5 perímetros · 40% | Segura a ponta de trás dos 2 trilhos Ø8; preso por 1 vareta M4. |
| `suporte_hall.stl` | 2 | PETG | 18 × 18 × 12 | 2 | < 1,5 | aba na mesa | 0,2 mm · 100% | A3144 colado com epóxi, de frente para o disco de sinal. M3×30 até a placa. |
| `calibre_vao_56mm.stl` | 1 | PETG | 60 × 56 × 20 | 29 | 1–2 | em pé | 0,2 mm · 3 perímetros · 20% | Ferramenta de montagem: acerta o vão de 56 mm entre as rodas antes de apertar os KFL001 de baixo. |

**Total:** ≈ 1.372 g de PETG e 185 g de TPU, 79–121 h. Compre 2 kg de PETG e 0,5 kg de TPU: sobra para errar e para refazer uma peça.

## Ordem de impressão

1. `nucleo_roda` ×2 e `banda_roda` ×2: as rodas são o caminho crítico.
2. `bloco_porca_giro`, `bloco_porca_tilt`, `suporte_motor_giro`, `mancal_fuso_giro`, `suporte_motor_tilt`: dão para montar e testar o giro e a inclinação antes da cabeça ficar pronta.
3. O resto da cabeça: `berco`, `suporte_trilho`, `funil_cabeca`, `suporte_servo`, `braco_empurrador`, `disco_sinal`, `suporte_hall`.
4. Por último as proteções: `tampa_correia_*` e `carenagem_roda_*`. O MVP pode girar as rodas sem elas nos primeiros testes, em rotação baixa e com ninguém do lado.

## Insertos e furos-guia

- **Insertos M4 no berço:** ferro de solda a ~230 °C com a ponta de inserto, empurre devagar até ficar rente. Deixe esfriar antes de apertar.
- **Furos de Ø2,5 nos blocos das porcas:** o parafuso M3 abre a rosca no PETG. Aperte só até encostar.
- **Ímãs dos discos de sinal:** antes de colar, marque o polo que o A3144 detecta (encoste no sensor ligado e veja a saída ir a 0). Os dois ímãs de cada disco com esse polo para fora.
