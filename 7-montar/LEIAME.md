# Montagem e primeiros testes

Cada etapa termina com uma conferência. Só passe para a próxima quando ela der certo.

Os parafusos e onde cada um vai estão em `4-comprar/LEIAME.md` (grupo Fixadores). Use trava-rosca média nos parafusos dos motores e das polias.

## 1. Pernas e base

1. Abra rosca M5 no furo central das duas pontas dos 4 postes de 112 mm.
1. Prenda os postes por baixo da chapa de base com 4 M5×12 vindos de cima, nos 4 furos dos cantos.
1. Rosqueie um pé de borracha M5 embaixo de cada poste.

**Confira:** a chapa fica nivelada e não balança na mesa.

## 2. Rolamento do giro

1. Prenda o anel de baixo do lazy susan na chapa: 4 M4×10 + arruela + porca autotravante, furos a r 66.
1. Gire o anel de cima até o furo de acesso alinhar com cada furo da plataforma e prenda a plataforma (4 M4×10, r 60).

**Confira:** a plataforma gira leve, sem folga vertical.

## 3. Acionamento do giro

1. NEMA17 do giro (fuso Tr8×8) no suporte com 4 M3×8; suporte na chapa com 2 M4×12.
1. Rolamento 608 prensado no mancal; mancal na chapa com 2 M4×12, com a ponta do fuso dentro do rolamento.
1. Porca de latão no bloco da porca do giro (4 M3×12); passe a porca no fuso.
1. Parafuso de ombro Ø6×30 no braço da plataforma, porca M5 por baixo; o ombro entra no rasgo do bloco.
1. Microchave com 2 M2×10 na posição do CAD, de forma que o bloco a aperte no fim do curso de −x.
1. Graxa de lítio no fuso.

**Confira:** girando o fuso à mão, a plataforma vai de −12,5° a +12,5° sem prender, e a microchave clica antes do fim.

## 4. Garfos e pivô

1. Fure as cantoneiras (Ø4,5) pela furação do garfo e da plataforma.
1. Cantoneiras na plataforma (4 M4×12) e garfos nas cantoneiras (4 M4×12), um de cada lado.
1. KFL08 por fora de cada garfo (4 M4×16).
1. Suporte do motor do tilt no garfo −x (2 M4×16) e o NEMA17 do tilt (Tr8×2) nele com 4 M3×10.
1. Porca de latão no bloco da porca do tilt (4 M3×12) e o bloco no fuso.

**Confira:** os dois garfos ficam paralelos e os KFL08 alinhados (passe uma barra de Ø8 pelos dois).

## 5. Rodas

1. Encaixe a banda de TPU no núcleo (as 8 chavetas). Cola PU na junção, se quiser.
1. Disco de aço + núcleo + disco de aço, com 6 M4×45 e porcas autotravantes; aperte em cruz.
1. Passe o eixo Ø12 pelos furos em D dos discos, com o chato alinhado.

**Confira:** a roda gira no eixo sem folga e sem bater (gire entre dois apoios e olhe de lado).

## 6. Cabeça

1. KFL001 nas placas laterais: 2 M6×20 + arruelas + porca autotravante cada. Os da roda de baixo ficam frouxos nos oblongos.
1. Rodas nos KFL001, com 2 colares Ø12 cada; polias de 12 mm e discos de sinal nas pontas, com trava-rosca no parafuso da polia.
1. 4 espaçadores M5×90 entre as placas (8 M5×12).
1. Use o calibre de 56 mm entre as rodas e aperte os KFL001 de baixo.
1. Motores 4250 nas placas pelo X-mount (8 M3×10), polias de 5 mm, correias 600-3M-9 (cima) e 288-3M-9 (baixo). Estique pelos oblongos do X-mount.
1. Berço (4 M4×10 nos insertos), trilhos Ø8 e suporte dos trilhos, funil (2 varetas M4).
1. Servo no suporte (4 M3×12 + porca), suporte na placa −x (2 M4×50), braço no horn (2 M3×8).
1. Suportes Hall (M3×30) com o A3144 a ~1 mm do disco de sinal; tampas das correias (M3×35) e carenagens das rodas (varetas M4).

**Confira:** vão de 56 mm medido nas duas pontas, correias tensas sem zumbir, o braço do servo passa sem tocar no berço.

## 7. Cabeça no garfo

1. Apresente a cabeça entre os garfos e passe os semi-eixos: o de 50 mm do lado +x, o de 65 mm do lado −x, com o chato encaixado no furo em D das placas.
1. Colares Ø8 dos dois lados de cada placa; aperte os parafusos dos KFL08 sobre o chato.
1. Manivela no semi-eixo −x (furo em D), presa com M4×10 + arruela na ponta.
1. Parafuso de ombro Ø6×6 na manivela (porca M5); o ombro entra no rasgo do bloco da porca do tilt.

**Confira:** girando o fuso do tilt à mão, a cabeça vai de 0° a 30° sem prender e sem folga no pivô.

## 8. Chicotes do lançador

1. Faça os rabichos do lançador com os comprimentos de `5-eletrica` e solde os plugues (MT60, GX16-8).
1. Prenda os cabos da cabeça com folga para o giro e a inclinação inteiros: deixe um laço perto do pivô e outro perto do lazy susan.
1. Etiquete as duas pontas de cada cabo com o código do conector.

**Confira:** com o giro e a inclinação nos extremos, nenhum cabo fica esticado.

## 9. Elétrica na bancada

1. Monte a caixa como em `5-eletrica`, testando cada etapa: potência sem carga, bucks, ESP32 sozinho, K1 e emergência.
1. Um motor de passo por vez: grave o firmware, `prende`, `ref`, `giro 5`, `tilt 10`.
1. Servo: `servo 90`, `servo 120`; ache o repouso e o empurrão.

**Confira:** os comandos movem cada eixo para o lado certo e a emergência corta tudo.

## 10. Primeiro giro das rodas

1. Sem bola, ninguém na frente, tampas e carenagens no lugar.
1. `armar`, espere 3 s, `rodas 1000 1000`. Confira o sentido (as rodas puxam a bola para a frente); troque duas fases no MT60 se precisar.
1. Suba em degraus: 2.000, 3.000 rpm. Leia a corrente na fonte e escute vibração.
1. `parar` e espere as rodas pararem sozinhas.

**Confira:** sem vibração forte nem cheiro de quente, e a emergência corta os ESCs na hora.

## 11. Primeiro tiro

1. `tiro 40 0`, espere `estado` mostrar pronto, ponha a bola no berço com a mão longe das rodas, `disparo`.
1. Depois `tiro 60 0`, `tiro 60 1500` e `tiro 60 -1500` para ver o spin.

**Confira:** a bola sai reta, sem tocar no funil nem nas carenagens.

