# Lançador de Bolas de Tênis — Projeto Detalhado

Revisão de 6 de outubro de 2026 · [apresentação com o modelo 3D](https://brodwolf.github.io/lancador-tenis/) · [repositório](https://github.com/brodwolf/lancador-tenis). Esta versão traz o memorial técnico completo; preços, custos e próximos passos ficam de fora.

## 1. Visão geral e decisões de projeto

A v2 tem um objetivo: portabilidade. A máquina ficou no menor tamanho possível (32 × 43 cm de base, ~82 cm de altura com o cesto dobrado), montada em três andares empilhados que se separam sem ferramenta.

Ela trabalha sempre no centro da linha de fundo: dali, ±10° de giro cobrem os cantos do fundo e ±12,5° os da área de saque. A ideia central continua: **só a "cabeça" se move**, e a bola desce por um tubo fixo sobre o eixo do giro. Não mudaram: duas rodas Ø150 independentes com sensor Hall, ESP32‑S3, baterias Makita com diodos ideais, disco agitador e empurrador a servo.

| # | Na v1 | Na v2 | Por quê |
| --- | --- | --- | --- |
| 1 | Uma estrutura alta com os níveis presos nela | Três andares empilhados, centrados por pinos e travados por fechos de pressão | Encolhe e se separa em partes para levar no carro |
| 2 | Perfil 30×30, ~11 m | Perfil 20×20 em cada andar, ~4,1 m | Andares baixos e chapas grossas dão a rigidez; perfis com ~1 kg em vez de 6–9 kg |
| 3 | Giro ±30° | ±12,5° | Basta para a máquina no centro da linha de fundo; menos espaço em volta da cabeça |
| 4 | Inclinação −15° a +15° | 0° a +30° | Lobs e bolas lentas; com a máquina no fundo, ângulo negativo não serve |
| 5 | Linha da bola a 720 mm | 381 mm | Máquina baixa; a altura de saída muda a inclinação necessária só +1 a 2,5° |
| 6 | Motor no eixo da roda, por fora das placas | Correias HTD 3M (1:1), motores entre as placas | Cabeça com 156 mm de largura; a correia isola o motor do choque do disparo |
| 7 | Hopper rígido, 80–100 bolas | Cesto de tela dobrável, ~120 bolas | Dobrado, a altura de transporte cai para ~815 mm |
| 8 | Lazy susan de 300 mm | Lazy susan redondo Ø150 | Giro pequeno e cabeça estreita; cabe na base |
| 9 | Giro por correia GT2 num aro de Ø300 | Fuso Tr8 empurrando um pino a 102 mm do eixo | Sem aro grande; resolução de ~0,0014° |
| 10 | Chave geral náutica; controle só pelo celular | Painel traseiro (tela touch, emergência, liga/desliga com chave anti-faísca), semáforo na frente, antenas de 433 MHz e Wi‑Fi | Usa sem celular; quem está na quadra vê a próxima bola e pausa pelo controle remoto |
| 11 | Telas perfuradas | Carenagem como conjunto separado, material a definir (talvez plástico injetado), só em STEP | A estrutura funciona sem ela; o material decide processo e custo |

Este memorial define dimensões, componentes, ligações e firmware. Os arquivos de CAD (STEP, STL e DXF) seguem estas cotas e estão em [Arquivos do projeto](#arquivos).

## 2. Especificações-alvo

A máquina lança de 30 a 120 km/h com até 3.000 rpm de spin, cobrindo aquecimento, drives, topspin, slice, lobs e bolas rápidas.

| Parâmetro | Alvo | Observação |
| --- | --- | --- |
| Velocidade da bola | 30–120 km/h | Calibrada por fator de eficiência no firmware |
| Spin | −2.500 rpm (slice) a +3.000 rpm (topspin) | Diferença de velocidade entre as rodas |
| RPM máxima da roda | 5.500 rpm | Limite de projeto (roda Ø150 mm) |
| Cadência | 1 bola a cada 1,5–10 s | Só dispara quando as duas rodas estão na RPM alvo |
| Giro horizontal (pan) | ±12,5° | Resolução de ~0,0014° |
| Inclinação (tilt) | 0° a +30° | Resolução de ~0,0006° |
| Altura de lançamento | 381 mm | Igual em qualquer inclinação (o pivô fica na linha da bola) |
| Capacidade do cesto | ~120 bolas | Cesto de tela dobrável, ~40 L |
| Alimentação | 2× Makita 18 V LXT, hot swap | Entrada AC opcional (fase 2) |
| Autonomia | 2,3–4,5 h com 2× 5,0 Ah | Ver cálculo na seção 3 |
| Dimensões em uso | 37,4 × 43 × 104,5 cm | Com as rodas; cesto aberto |
| Dimensões de transporte | 37,4 × ~45,5 × ~81,5 cm | Cesto dobrado, alça recolhida |
| Peso | ~20 kg sem carenagem e sem bolas | Carenagem em ABS: +~3 kg; 120 bolas: ~6,9 kg |
| Controle | Celular (Wi‑Fi), tela touch e controle remoto 433 MHz | Botão de emergência físico |

## 3. Física e dimensionamento

Com rodas de Ø150 mm, a bola mais exigente (110 km/h com 3.000 rpm de topspin) pede 5.443 rpm na roda de cima, por isso o limite de projeto é 5.500 rpm.

### 3.1 Velocidade e spin

A bola sai com a média das velocidades periféricas das rodas, menos as perdas por compressão e escorregamento. O spin vem da diferença entre as rodas.

```math
v_{bola} \approx \eta \cdot \frac{v_{sup} + v_{inf}}{2} \qquad \omega_{bola} \approx k \cdot \frac{v_{sup} - v_{inf}}{g}
```

Para o firmware, a conta é invertida (o usuário escolhe velocidade e spin, a máquina calcula as RPMs):

```math
v_{sup,inf} = \frac{v_{bola}}{\eta} \pm \frac{\omega_{bola} \cdot g}{2k} \qquad RPM = \frac{60 \cdot v_{roda}}{\pi \cdot D_{roda}}
```

Onde g = vão entre as rodas (56 mm), D = diâmetro da roda (150 mm), η ≈ 0,90 e k ≈ 1,0 são fatores de calibração ajustados na prática. Spin positivo = topspin (roda de cima mais rápida).

| Tipo de bola | Velocidade (km/h) | Spin (rpm) | Roda superior (rpm) | Roda inferior (rpm) |
| --- | --- | --- | --- | --- |
| Aquecimento | 40 | 0 | 1.572 | 1.572 |
| Voleio | 60 | 0 | 2.358 | 2.358 |
| Slice | 70 | −1.500 | 2.191 | 3.310 |
| Drive plano | 80 | 0 | 3.143 | 3.143 |
| Topspin médio | 80 | +1.500 | 3.704 | 2.583 |
| Topspin pesado | 90 | +2.500 | 4.470 | 2.604 |
| Bola rápida plana | 120 | 0 | 4.716 | 4.716 |
| Limite de projeto | 110 | +3.000 | 5.443 | 3.203 |

### 3.2 Inércia da roda e consistência

A bola a 120 km/h leva ~32 J de energia cinética (m = 57,5 g). Cada roda cede ~15–25 J por disparo, contando as perdas.

Cada roda tem I ≈ 2,6 × 10⁻³ kg·m² (núcleo impresso + 2 discos de aço + banda de TPU, ~1 kg; a polia soma pouco). A 3.500 rpm ela guarda ~175 J, então cai só 5–7% de RPM por disparo. O firmware espera a RPM voltar (< 0,5 s) antes do próximo disparo.

### 3.3 Motores e correias

- **KV:** para chegar a 5.500 rpm com carga e bateria no fim (16 V), KV ≥ 5.500 / (0,85 × 16) ≈ 400. Faixa recomendada: **400–500 KV**.
- **Torque de partida:** acelerar de 0 a 3.500 rpm em 5 s exige ~0,19 N·m (~9 A por motor). Rampas mais rápidas somam corrente; o firmware limita a rampa para manter o total abaixo de 25 A.
- **Recuperação:** repor 20 J em 0,5 s = ~40 W por motor, uma fração da capacidade.
- **Classe:** outrunner 4250 (Ø42 × 50 mm), ≥ 500 W: é o tamanho que cabe entre as placas. A potência média é baixa; a folga é térmica e de durabilidade.
- **Transmissão:** correia HTD 3M 1:1 (RPM do motor = RPM da roda). Ela só leva o torque do motor (~0,2–0,4 N·m na aceleração); o choque do disparo fica com a inércia da roda e os mancais.

### 3.4 Autonomia

Uma Makita 18 V 5,0 Ah tem 90 Wh, dos quais ~80 Wh são úteis até 15 V. Duas baterias dão ~160 Wh.

| Situação | Consumo médio | Autonomia (2× 5,0 Ah) |
| --- | --- | --- |
| Rodas girando, sem disparar | ~25 W | ~6 h |
| Treino típico (80 km/h, 1 bola a cada 4 s) | ~35–45 W | ~3,5–4,5 h |
| Treino pesado (120 km/h, 1 bola a cada 2 s) | ~60–70 W | ~2,3–2,7 h |

São estimativas. O firmware mede a tensão de cada bateria; com um sensor de corrente opcional (INA226) você mede o consumo real.

### 3.5 Trajetória e simulação na quadra

A aba **Quadra**, ao lado do modelo 3D, mostra onde a bola quica. A máquina fica no centro, com a frente da carenagem encostada na linha de fundo (ou na linha de saque), e a bola sai logo depois do ponto de contato das rodas, a ~0,38 m do chão com a cabeça a 0° (~0,51 m a +30°), na direção dada pelo giro e pela inclinação. Também dá para tocar num ponto da quadra adversária: a página calcula o giro e a inclinação para a bola quicar ali. Há ainda vento, com velocidade de 0 a 40 km/h e direção; com a mira ativa, a página corrige giro e inclinação para compensar.

[Abrir a simulação na quadra](https://brodwolf.github.io/lancador-tenis/#quadra)

Em voo, a bola sofre o peso, o arrasto do ar e a força de Magnus causada pelo spin. As duas forças do ar dependem da velocidade da bola **em relação ao ar**, v_r = v − v_vento:

```math
m\,\frac{d\vec v}{dt} = m\,\vec g \;-\; \tfrac{1}{2}\,\rho A\,C_D\,|\vec v_r|\,\vec v_r \;+\; \tfrac{1}{2}\,\rho A\,C_L\,|\vec v_r|^2\,(\hat\omega \times \hat v_r) \qquad \vec v_r = \vec v - \vec v_{vento}
```

Os coeficientes vêm do ajuste empírico de Goodwill, Chin e Haake (2004), medido em túnel de vento com bolas girando, em função da razão entre a velocidade da bola em relação ao ar, v, e a velocidade periférica do spin, v_s = r·ω:

```math
C_D = 0{,}55 + \frac{1}{\left[\,22{,}5 + 4{,}2\,(v/v_s)^{2{,}5}\right]^{0{,}4}} \qquad C_L = \frac{1}{2 + v/v_s}
```

No quique, a velocidade vertical volta multiplicada pelo coeficiente de restituição e, e o atrito freia o ponto de contato até a bola parar de escorregar e começar a rolar (modelo de R. Cross). O mesmo atrito muda o spin: o topspin sai do quique mais rápido para a frente, e o slice freia e fica baixo.

```math
v_y' = -e\,v_y \qquad J_t = \min\!\left(\mu\,(1+e)\,|v_y|,\; \frac{\alpha}{1+\alpha}\,|u_c|\right) \qquad I = \alpha\, m\, r^2
```

Onde u_c é a velocidade do ponto de contato com o chão e J_t é o impulso de atrito por unidade de massa. A trajetória é integrada por Runge‑Kutta de 4ª ordem com passo de 2 ms.

| Parâmetro | Valor usado |
| --- | --- |
| Bola | 57 g, Ø67 mm, α = 0,55 |
| Ar | ρ = 1,21 kg/m³ (nível do mar, 20 °C); vento opcional de 0 a 40 km/h, em qualquer direção, uniforme |
| Quadra rápida | e = 0,78, μ = 0,65 |
| Saibro | e = 0,80, μ = 0,80 |
| Rede | 0,914 m no centro, 1,07 m nos postes |
| Bola dentro | 1º quique na quadra de simples do adversário; a linha conta como dentro |

Inclinação que põe o 1º quique dentro e onde ele cai (distância depois da rede), em quadra rápida, com a máquina no centro e inclinação de 0° a +30°:

| Bola | Velocidade e spin | Da linha de saque | Da linha de fundo |
| --- | --- | --- | --- |
| Aquecimento | 40 km/h, sem spin | +22° a +30° → 2,2–3,6 m | não cai dentro |
| Voleio | 60 km/h, sem spin | +11,9° a +27,7° → 4,9–11,9 m | +17,7° a +30° → 2,5–7,0 m |
| Drive plano | 80 km/h, sem spin | +8,8° a +12,9° → 8,0–11,8 m | +10,8° a +20,3° → 4,4–11,9 m |
| Topspin médio | 80 km/h, +1.500 rpm | +10° a +18° → 6,3–11,8 m | +13,4° a +30° → 3,4–11,6 m |
| Slice | 70 km/h, −1.500 rpm | +8,9° a +15,6° → 7,1–11,9 m | +11,5° a +30° → 3,7–11,6 m |
| Topspin pesado | 90 km/h, +2.500 rpm | +9,5° a +15,8° → 6,9–11,9 m | +12,3° a +25,4° → 3,8–11,8 m |
| Bola rápida plana | 120 km/h, sem spin | não cai dentro | +6,2° a +7,8° → 8,9–11,9 m |

**O que isso diz sobre o projeto:** da linha de fundo, onde a máquina fica, a faixa de 0° a +30° põe drive, topspin e slice em qualquer profundidade, de ~3,5–4,5 m da rede até a linha de fundo. O voleio de 60 km/h chega a ~7 m da rede e a bola rápida de 120 km/h só cai no fundo (~9–12 m). O aquecimento a 40 km/h não chega à quadra adversária saindo da linha de fundo: para ele, ponha a máquina na linha de saque. "Não cai dentro" quer dizer que, naquela posição, a bola ou bate na rede ou sai longa.


Quanto o vento desloca o quique: máquina na linha de fundo, inclinação ajustada para a bola quicar a 8 m da rede sem vento; "da esquerda" é o vento que vem da esquerda de quem está atrás da máquina.

| Bola | Inclinação | 10 km/h a favor | 10 km/h contra | 10 km/h da esquerda | 20 km/h a favor | 20 km/h contra | 20 km/h da esquerda |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Drive plano (80 km/h, sem spin) | +14,9° | 9,2 m | 6,8 m | 0,6 m para a direita | 10,3 m | 5,5 m | 1,3 m para a direita |
| Topspin médio (80 km/h, +1.500 rpm) | +21° | 9,9 m | 6,2 m | 0,9 m para a direita | 11,9 m | 4,4 m | 1,8 m para a direita |
| Slice (70 km/h, −1.500 rpm) | +18,6° | 9,1 m | 6,6 m | 1,0 m para a direita | 10,0 m | 5,0 m | 2,1 m para a direita |

Um vento de 20 km/h contra encurta o topspin médio de 8 m para 4,4 m da rede; a favor, alonga para 11,9 m. De lado, os mesmos 20 km/h desviam a bola 1,3–2,1 m; o slice, mais lento e mais tempo no ar, é o que mais deriva.

São aproximações. Bola gasta, altitude (em São Paulo o ar é ~7% menos denso, e a bola vai um pouco mais longe), rajadas (o simulador usa vento constante e igual em toda a quadra) e os valores reais de η e k mudam o quique em alguns decímetros. A calibração do protótipo (seção 19) acerta os números.

## 4. Arquitetura e cotas

A linha da bola fica a 381 mm do chão, e o pivô do tilt fica nela, exatamente sobre o eixo do giro, 116 mm atrás do centro da máquina.

![Vista lateral esquemática com as cotas de altura](assets/diagramas/arquitetura.svg)

Como o recuo do disparo age ao longo da linha da bola, e essa linha cruza os dois eixos, o tiro não gera torque que desvie a mira. O tubo de queda fica parado enquanto a cabeça gira e inclina embaixo dele.

**Referência de cotas:** z = altura a partir do chão; x = largura (0 no centro); y = profundidade (positivo para a frente, 0 no centro). Na cabeça: u = para a frente ao longo da linha da bola, v = para cima, origem no pivô.

- **Eixo do giro:** x = 0, y = −116 mm. Sobre ele ficam o furo de saída, o tubo de queda (z 466–696) e o pivô do tilt (z 381, 205 mm acima da plataforma).
- **Nip:** 215 mm à frente do pivô, na linha da bola.

## 5. Estrutura em andares

Três andares de chapa de alumínio e perfil 20×20 canal 6, empilhados e centrados por pinos; todas as chapas internas medem 312 × 422 mm.

### 5.1 Andares

| Andar | Base | Postes 20×20 | Topo | O que leva |
| --- | --- | --- | --- | --- |
| Controle | Piso Al 3 mm em z = 45 | 4 × 112 mm | z = 160 | Baterias, eletrônica, rodas de transporte, pés |
| Lançador | Al 4 mm em z = 160 | 4 × 536 mm + quadro do topo | z = 700 | Giro, garfo, cabeça, atuadores, painel traseiro, semáforo, antenas, alça |
| Alimentador | Al 3 mm em z = 700 | 4 × 79 mm | Aro Al 3 mm em z = 785 | Disco agitador, rampas, tubo de queda |
| Cesto | Aro do alimentador | 4 varetas Ø8 | z = 1.045 (dobrado ~815) | ~120 bolas |

### 5.2 Lista de corte (perfil 20×20 canal 6)

| Peça | Qtd | Comprimento (mm) |
| --- | --- | --- |
| Poste do andar de controle | 4 | 112 |
| Poste do andar do lançador | 4 | 536 |
| Poste do alimentador | 4 | 79 |
| Travessa lateral do quadro do topo | 2 | 360 |
| Travessa frente/trás do quadro do topo | 2 | 250 |
| **Total** | **16** | **~4,1 m** |

Peça os cortes no esquadro (±0,3 mm) e rosqueie M5 o furo central nas duas pontas de cada poste.

### 5.3 Chapas e fixação

- **Postes:** centros a ±135 mm (x) e ±190 mm (y), cada um preso nas chapas por um parafuso M5 no furo central. Nas bases do lançador e do alimentador, que apoiam sobre os postes de baixo, use parafuso escareado.
- **Quadro do topo do lançador:** travessas de 360 e 250 mm entre os postes, em z = 680–700, com 4 cantoneiras 20×20. O alimentador apoia nele.

### 5.4 União entre andares

- **Centragem:** 2 pinos em diagonal por junta. Controle → lançador: pinos impressos em blocos presos na face dos postes, que entram em furos Ø8,4 da base do lançador. Lançador → alimentador: pinos-guia Ø10 presos por M4 + porca-T no canal de cima das travessas.
- **Travamento:** 8 fechos de pressão inox, 4 por junta (2 de cada lado), na carenagem: controle/lançador e lançador/alimentador. O cesto só assenta no aro do topo. Sem carenagem, os pinos centram e o peso segura; para transportar montada, prenda os fechos em chapinhas nos postes ou passe uma cinta.
- **Cabos:** 3 suportes impressos de conectores (2 na junta de baixo, 1 na de cima). Desconecte antes de separar os andares.

## 6. Módulo de lançamento

Duas rodas de Ø150 mm, uma sobre a outra com vão de 56 mm, cada uma no seu eixo de Ø12 mm com dois mancais e acionada por um motor brushless através de uma correia HTD.

**Referência da cabeça:** origem no pivô do tilt (sobre o eixo do giro); u para a frente ao longo da linha da bola, v para cima. O nip fica em u = 215 mm, v = 0. Os centros das rodas ficam em (215, +103) e (215, −103).

### 6.1 Geometria

| Item | Valor | Nota |
| --- | --- | --- |
| Diâmetro externo da roda | 150 mm | Com banda de rodagem |
| Largura da roda | 40 mm | Perfil côncavo, centraliza a bola |
| Vão entre rodas | 56 mm (ajuste 52–60) | Comprime a bola ~11 mm no total |
| Distância entre eixos | 206 mm | 150 + 56 |
| Distância pivô → nip | 215 mm | Cabem o berço e os dois motores entre o pivô e as rodas |
| Distância interna entre placas | 90 mm | Roda, colares, mancais KFL001 e motores |
| Largura da cabeça | 156 mm | Placas de 6 mm (347 × 310) + tampas das correias; 4 espaçadores M5 × 90 |

### 6.2 Construção da roda

1. **Núcleo** impresso em PETG (ou ASA/PA‑CF): Ø134 × 32 mm, 6 perímetros, 60% gyroid, furo central Ø12,2 mm.
2. **Dois discos de aço** 3 mm, Ø120 mm (corte a laser), um em cada face: dão inércia e uma espinha metálica à roda.
3. **Seis parafusos M4** passantes prendem discos e núcleo; os discos têm **furo em D** que encaixa no chato do eixo e transmite o torque direto, sem cubo.
4. **Banda de rodagem** em TPU 95A impressa: Ø134 → Ø150, 40 mm de largura, com chavetas internas que encaixam em ranhuras do núcleo, mais cola PU. As chavetas impedem que ela solte com a força centrífuga.
5. **Polia** HTD 3M de 20 dentes (furo 12 mm) na ponta do eixo, por fora da placa; parafuso sem cabeça sobre o chato, com trava-rosca.
6. **Balanceamento estático:** apoie o eixo sobre duas réguas retas niveladas; a roda deve parar em posições aleatórias. Corrija com arruelas M3 coladas no lado leve.

### 6.3 Eixos, mancais, correias e motores

- **Eixo:** aço Ø12 h6 × 140 mm, com um chato de 1 mm em todo o comprimento. Pode ser barra retificada cortada ou peça usinada.
- **Mancais:** 4× KFL001 (Ø12, 2 furos M6 a 48 mm), por dentro das placas. Confirme rotação limite ≥ 6.000 rpm. Os furos da roda de baixo são **oblongos (±4 mm)** para ajustar o vão; colares Ø12 dos dois lados da roda.
- **Motores:** 2× outrunner 4250, 400–500 KV, com **eixo invertido** (em muitos modelos basta soltar o anel de trava e empurrar o eixo), cada um por dentro de uma placa com o eixo atravessando-a até a polia. Roda de cima: placa +x, em (u 51,7; v −112); roda de baixo: placa −x, em (u 101,4; v −112).
- **Correias:** HTD 3M de 9 mm, fechadas: **600‑3M‑9** na roda de cima e **288‑3M‑9** na de baixo. A posição dos motores sai do comprimento da correia.
- **Tensionamento:** oblongos M3 no X‑mount (±3 mm). Estique até a correia ceder ~1/64 do vão com força leve: ~4 mm na de cima, ~2 mm na de baixo.
- **Tampas das correias:** impressas, presas por 2 espaçadores M3 cada, dentro do laço da correia.

### 6.4 Sensor de RPM

No lado oposto à polia, o eixo sobra além da placa. Ali entra um disco impresso Ø40 com 2 ímãs Ø6 × 3 mm opostos (2 pulsos por volta). Um módulo Hall A3144 fica a 2–4 mm, num suporte impresso.

### 6.5 Guia da bola e proteções

- **Guia:** dois trilhos de alumínio Ø8 × 215 mm do berço até perto do nip. A bola chega centrada e com velocidade repetível.
- **Carenagens das rodas:** duas peças impressas (PETG ou ASA) que cobrem cada roda por cima, por trás e pelos lados.

## 7. Módulo de inclinação (tilt)

A cabeça pivota sobre dois semi-eixos de Ø8 mm, e um NEMA17 com fuso Tr8×2 integrado, ligado a uma manivela, a inclina de 0° a +30° em ~1,7 s.

### 7.1 Pivô

- **Garfo:** duas chapas de alumínio 6061 de 6 mm, presas na plataforma por 2 cantoneiras 40 × 40 × 3; pivô 205 mm acima da plataforma.
- **Semi-eixos:** o berço fica no pivô, e um eixo inteiro bloquearia a bola. Lado +x: Ø8 × 50 mm; lado −x: Ø8 × 65 mm com chato para a manivela. 4 colares Ø8.
- **Mancais:** 2× KFL08 (flange, Ø8, 2 furos M4 a 37 mm) nas chapas do garfo.

### 7.2 Atuador

| Item | Valor |
| --- | --- |
| Motor | NEMA17 com fuso trapezoidal Tr8×2 integrado (passo de 2 mm), 100 mm, porca de latão |
| Montagem | Deitado ao longo da linha da bola, preso no garfo −x por suporte impresso |
| Transmissão | Porca num bloco impresso com rasgo, onde entra o pino da manivela (parafuso de ombro Ø6, M5) |
| Manivela | Alumínio 6 mm, raio 64 mm, furo em D no semi-eixo −x |
| Curso da porca | ~33 mm para 0–30° (~16,5 voltas) |
| Resolução | 0,000625 mm por micropasso (1/16) = ~0,0006° |
| Tempo de 0° a +30° | ~1,7 s a 600 rpm |

A 15° a manivela aponta para baixo: a ponta anda quase só ao longo do fuso e o curso fica quase linear com o ângulo.

A cabeça tem ~6 kg e é pesada na frente (~8–10 N·m em torno do pivô), o que dá ~130–150 N na porca. Com passo de 2 mm isso pede só ~0,13 N·m no motor, um terço do torque de um NEMA17 de 40 mm. Por isso o tilt usa o fuso de 2 mm e não o de 8 mm: com 8 mm o motor ficaria no limite e a cabeça cairia sem corrente.

### 7.3 Referência e limites

- **Referência:** no limite de 0°, por microchave ou pela detecção de travamento do TMC2209 (StallGuard). Na partida, o tilt desce até a referência e vai para a posição pedida.
- **Limites:** 0° a +30° no firmware; em toda a faixa, a menor folga entre cabeça e garfo é 2,7 mm.
- **Repouso:** o fuso de 2 mm por volta não é reversível: sem corrente, a cabeça fica onde está. Um batente de borracha no garfo, logo abaixo de 0°, protege contra erro de referência.
- **Calibração do zero:** inclinômetro do celular sobre a placa lateral; grave o desvio no firmware.

## 8. Módulo de giro (pan)

A plataforma giratória roda sobre um lazy susan redondo de Ø150; um NEMA17 com fuso Tr8 move um bloco com rasgo que empurra um pino a 102 mm do eixo. Os ±22 mm de curso dão ±12,5°.

### 8.1 Rolamento e placas

- **Rolamento:** lazy susan redondo Ø150 (6"), centrado no eixo do giro. A furação varia por fabricante: no DXF são 4 furos a r 66 (girados 45°) na base e 4 a r 60 na plataforma; confira com a peça na mão.
- **Plataforma giratória:** alumínio 4 mm, 197 × 156 mm (raio de até 84 mm, mais o braço do pino), furo central Ø40; o garfo é preso nela (seção 7.1).

### 8.2 Transmissão

| Item | Valor |
| --- | --- |
| Motor | NEMA17 com fuso Tr8×8 integrado de 100 mm, deitado ao longo de y no lado +x, em suporte impresso em L |
| Ponta do fuso | Mancal impresso com rolamento 608 |
| Pino | Parafuso de ombro M6 no braço da plataforma, a 102 mm do eixo; entra no rasgo do bloco-porca |
| Curso | ±22 mm para ±12,5° |
| Resolução | 0,0025 mm / 102 mm = ~0,0014° |
| Velocidade | 300 rpm no motor = 40 mm/s = ~22°/s; de um lado ao outro em ~1,1 s |

O fuso não escorrega, e o recuo do disparo quase não gera torque no eixo do giro, porque a linha da bola passa por ele. Se houver folga visível na porca, use uma porca anti-folga (com mola).

### 8.3 Cabos, referência e limites

- **Cabos:** pelo furo central Ø40 da base, com um laço de ~15–20 cm preso com abraçadeiras. Com ±12,5°, não precisa de anel coletor.
- **Fim de curso:** microchave na base. Na partida, o giro vai até ela e volta ao centro.
- **Limites:** ±12,5° no firmware. A menor folga é 2,0 mm, entre a parte que gira e o motor do giro: não force além dos limites nem com a mão.

## 9. Alimentador e cesto

Um disco com 4 bolsões, girado por um NEMA17, solta exatamente uma bola por comando num tubo fixo sobre o eixo do giro; a bola cai no berço da cabeça e um servo a empurra para as rodas.

### 9.1 Cesto dobrável

- **Tamanho:** base 268 × 338 mm, topo 460 × 540 mm, 246 mm de altura: ~40 L, ~120 bolas soltas.
- **Varetas:** 4 varetas de alumínio Ø8 inclinadas, com a ponta de baixo amassada e furada, giram em dobradiças impressas no aro do topo (pino M3). O aro de cima tem 4 varetas Ø8 unidas por 4 cantos impressos.
- **Tela:** PVC/poliéster em 4 painéis costurados, presos nas varetas.
- **Dobrado:** as varetas deitam sobre o aro e a tela fica por cima; a máquina fica com ~815 mm de altura.

### 9.2 Andar do alimentador

- **Base:** alumínio 3 mm em z = 700 (teto do andar do lançador); postes de 79 mm; aro do topo em z = 785, onde assenta o cesto.
- **Furo de saída:** Ø76 exatamente sobre o eixo do giro.
- **Rampas:** 4 peças impressas com 15° de queda levam as bolas até o disco.

### 9.3 Disco agitador

| Item | Valor |
| --- | --- |
| Disco | PETG, Ø220 com cúpula, 4 bolsões Ø74 a 70 mm do centro |
| Posição | Centro 70 mm à frente do eixo do giro (y = −46): um bolsão por vez fica sobre o furo de saída |
| Motor | NEMA17 curto (~34 mm) pendurado embaixo da base; o eixo atravessa a base até o rotor |
| Passo | 90° por bola = 800 micropassos (1/16) |
| Capuz | Sobre o furo de saída: só a bola do bolsão passa por baixo |
| Deslizante | Folha de PTFE ou UHMW 0,5 mm sob o disco |
| Antitravamento | Sem bola detectada no tubo → recua 30° e tenta de novo; 4 bolsões vazios seguidos → aviso "cesto vazio" |

### 9.4 Tubo de queda e funil

- Tubo de PVC esgoto DN75 (interno ~72 mm), 230 mm, preso na base do alimentador por um flange impresso.
- Termina a 466 mm do chão, 85 mm acima da linha da bola: fica acima do funil da cabeça em qualquer inclinação de 0 a 30°.
- O funil da cabeça tem boca de 84 × 140 mm (mais comprida para a frente, porque recua quando a cabeça inclina) e afunila até Ø78 mm.
- Sensor infravermelho E18‑D80NK atravessando o tubo: confirma que a bola caiu.

### 9.5 Berço e empurrador

- **Berço:** peça impressa no pivô, entre os dois trilhos; segura a bola em qualquer inclinação.
- **Empurrador:** servo rápido de 20–25 kg·cm (tamanho padrão, engrenagens metálicas, ≤ 0,07 s/60°), eixo em u = −45, v = −82. O braço impresso (~73 mm, ponta de TPU) passa por um rasgo no berço e lança a bola pelos trilhos; ela entra sempre com a mesma velocidade.
- **Até as rodas:** elas pegam a bola ~180 mm à frente do berço. A +30°, a bola sobe ~90 mm nesse caminho e precisa sair do empurrador a ~1,5 m/s. Um DS3225 comum (~0,13 s/60°) dá ~0,6 m/s na ponta do braço, o que basta só até ~15°; por isso o servo rápido. Confira no protótipo que a bola chega às rodas em toda a faixa (teste 6 da seção 19); se não chegar, alongue o braço.

### 9.6 Ciclo de um disparo

1. Disco gira 90° → bola cai pelo tubo → sensor do tubo confirma.
2. Firmware espera: RPM das duas rodas dentro de ±1,5% por 300 ms, giro e tilt parados na posição.
3. Semáforo amarelo piscando: contagem para a próxima bola.
4. Semáforo verde, servo empurra → bola sai → servo volta.
5. Próxima bola é liberada (o tempo mínimo do ciclo é ~1,5 s).

## 10. Base, transporte e carenagem

O andar de controle é a base; para mover, inclina-se a máquina para trás e puxa-se pela alça, como uma mala de rodinhas.

### 10.1 Base

- **Piso:** alumínio 3 mm a 45 mm do chão; postes de 112 mm.
- **Baterias:** 2 Makita deitadas em berços impressos na metade de trás; saem por trás, pela tampa das baterias. Caixa IP65 na metade da frente; diodos ideais e chave anti-faísca ao lado das baterias.
- **Rodas de transporte:** 2 rodas de patins inline Ø125 × 24 com rolamentos 608, por fora da largura (374 mm no total), 65 mm à frente da traseira. Eixo Ø8 × 60 (pode ser parafuso de ombro) em suportes de alumínio 4 mm.
- **Pés:** 2 pés de borracha M8 reguláveis na frente, para nivelar.

### 10.2 Alça e transporte

- **Alça:** telescópica de mala (2 tubos), presa nos postes de trás por 4 abraçadeiras impressas. Recolhida, o pegador fica a ~815 mm.
- **Para puxar:** incline ~30° para trás. Acima de ~45°, a borda de trás do piso encosta no chão.
- **Transporte:** cesto dobrado e alça recolhida: 374 × ~455 × ~815 mm, ~20 kg (~23 kg com carenagem de 3 mm em ABS). Para carregar em partes, desconecte os conectores entre andares, abra os fechos e tire o alimentador (com o cesto) e depois o andar do lançador.

### 10.3 Carenagem (material a definir)

- **O que é:** um conjunto separado de 3 painéis (um por andar) e a tampa das baterias, por fora dos postes. O material ainda não foi definido; plástico injetado está sendo considerado (opções na seção 16.4).
- **O que o projeto entrega:** só STEP de referência, sem DXF, com parede de 3 mm, cantos verticais R30 e todos os recortes: janela da cabeça (232 × 297 mm), semáforo, painel traseiro, furos das antenas, eixos das rodas de transporte, rasgos das abraçadeiras da alça e tampa das baterias. A menor folga até a cabeça é 6,9 mm.
- **Sem carenagem:** a máquina funciona igual. As proteções mínimas são as carenagens impressas das rodas e as tampas das correias (seção 20).

## 11. Sistema de potência

Duas baterias Makita alimentam um barramento de 15–21 V através de diodos ideais; uma chave eletrônica anti-faísca, comandada pelo botão liga/desliga do painel traseiro, liga e desliga tudo, e um relé comandado pelo botão de emergência corta os motores das rodas.

![Caminho da energia das baterias até cada carga](assets/diagramas/potencia.svg)

Cada fonte entra por seu próprio diodo ideal, e só o ramo das rodas passa pelo relé comandado pelo botão de emergência.

### 11.1 Baterias e hot swap

- **Baterias:** Makita LXT 18 V, 5,0 Ah (BL1850B) ou 6,0 Ah (BL1860B), que dá ~20% mais autonomia no mesmo espaço.
- **Soquetes:** 2 adaptadores de bateria Makita 18 V com fios 12 AWG. Cada um passa por um **fusível de 30 A** e por um **módulo diodo ideal** (≥ 30 A) antes da chave.
- **Por que diodo ideal:** a bateria com tensão mais alta alimenta, e não passa corrente de uma bateria para a outra. Dá para tirar uma bateria com a máquina ligada.
- **Corte por subtensão no firmware:** adaptadores simples não têm proteção contra descarga profunda; a [PartsBuilt](https://partsbuilt.com/makita-18v-battery-adapter) vende adaptadores com uma placa extra só para isso. Aqui, o ESP32 mede cada bateria e para de disparar a 15,5 V; abaixo de 15,0 V desliga as rodas.

### 11.2 Entrada AC (opcional, fase 2)

- **Caminho:** tomada IEC C14 com fusível e chave → fonte fechada **Mean Well LRS‑350‑24** → terceiro diodo ideal → barramento. A v2 não tem espaço para a fonte (215 × 115 × 30 mm): monte-a numa caixa externa, ligada à máquina por XT60.
- **Ajuste:** a saída dessa fonte vai de 21,6 a 28,8 V ([folha de dados Mean Well](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF)). Ajuste no mínimo (21,6 V): fica acima da bateria cheia, então a fonte alimenta e as baterias descansam. Ela **não** carrega as baterias.
- **Chave de tensão de entrada:** 90–132 ou 180–264 VAC, escolhida por chave na fonte. Em 127 V use 115; em 220 V use 230. Posição errada queima a fonte.
- **Limite de 350 W:** a fonte aguenta 150% de pico por até 1 s. Com AC, o firmware alonga a rampa de partida das rodas.
- **Aterramento:** terra da tomada na caixa da fonte, bornes cobertos; peça a um eletricista para revisar antes de ligar.

### 11.3 Distribuição, proteção e bitolas

| Circuito | Proteção | Fio | Observação |
| --- | --- | --- | --- |
| Bateria A/B → diodo ideal | Fusível lâmina 30 A | 12 AWG (4 mm²) | Porta-fusível junto do soquete |
| Diodos → chave anti-faísca → barramento | Chave eletrônica ≥ 60 A | 12 AWG | Comandada pelo botão liga/desliga |
| Relé K1 → ESC superior | Fusível 25 A | 14 AWG (2,5 mm²) |  |
| Relé K1 → ESC inferior | Fusível 25 A | 14 AWG |  |
| ESC → motor | — | 14 AWG silicone | Conector MT60 (3 vias) entre andares |
| Drivers TMC2209 (×3) | Fusível 5 A | 18 AWG (1 mm²) | Capacitor 1.000 µF / 35 V no barramento dos drivers |
| Buck 5 V / 3 A | Fusível 3 A | 20 AWG | ESP32, tela touch, sensores, receptor 433 MHz e semáforo |
| Buck 6 V / 5 A (XL4015) | Fusível 5 A | 18 AWG | Servo do empurrador |
| Buck 12 V / 1 A | Fusível 2 A | 22 AWG | Bobina do relé K1, LED do botão liga/desliga e ventoinha da caixa, se usar |
| Sinais | — | 24–26 AWG | Motores de passo: cabo 4 × 22 AWG; antenas: coaxial com SMA |

### 11.4 Parada e intertravamentos

- **Liga/desliga:** botão 22 mm com retenção e anel de LED no painel traseiro; comanda a chave anti-faísca, que corta toda a máquina. A chave é eletrônica: para mexer na fiação, tire as baterias.
- **Botão de emergência** tipo cogumelo, 1NF + 1NA, no painel traseiro. O contato NF alimenta a bobina do **relé K1 (40 A)** dos ESCs; o NA avisa o ESP32.
- **Desarme por software:** o ESP32 também abre K1 por um MOSFET (falha de sensor, perda do app em treino iniciado pelo app, bateria baixa).
- **Inércia:** sem energia, as rodas ainda giram 10–30 s. Na parada normal o firmware zera o acelerador com freio do ESC ligado antes de abrir o relé.
- **Diodo de roda livre** (1N4007) na bobina de K1.

## 12. Eletrônica de controle

Um ESP32‑S3 comanda 2 ESCs, 3 drivers TMC2209, 1 servo e o semáforo, lê os sensores, as 2 baterias e o receptor de 433 MHz e conversa com a tela touch por UART, usando 26 GPIOs; tudo fica numa caixa IP65 no andar de controle.

### 12.1 Componentes

- **Controlador:** ESP32‑S3‑DevKitC‑1U‑N8R8 (conector U.FL para antena externa). Os pinos 35–37 ficam com a PSRAM; 19 e 20 são o USB nativo.
- **ESCs:** 2× ESC brushless 60–80 A, 2–6S. Ligue só sinal e GND (o fio vermelho do BEC fica isolado). Configure: freio ligado, partida suave, corte de bateria no mínimo (quem corta é o firmware).
- **Drivers:** 3× TMC2209 em modo UART num único fio, endereços por MS1/MS2: giro = 0, tilt = 1, agitador = 2. Correntes: giro 0,8 A RMS, tilt 0,8 A, agitador 0,6 A.
- **Sensores:** 2× Hall A3144 (pull-up 10 kΩ para 3,3 V + 100 nF); 1× E18‑D80NK no tubo (5 V, saída NPN com pull-up para 3,3 V); microchave do giro ligada como NF para GND (fio rompido = fim de curso acionado). O tilt usa o DIAG do TMC2209 (StallGuard) ou uma segunda microchave.
- **Receptor 433 MHz:** RXB6 (5 V) com controle de chaveiro de 4 botões (código fixo, tipo EV1527); saída por divisor 10 kΩ / 20 kΩ. A antena SMA vai soldada no pino ANT por cabo coaxial.
- **Tela touch:** placa com ESP32‑S3 próprio e tela IPS 3,5", alimentada em 5 V, ligada ao controlador por UART (115.200 bps).
- **Semáforo:** 12 LEDs WS2812B (3 células de 4) num pino, com 330 Ω em série; se piscar errado, use um 74AHCT125 como conversor de nível.
- **Divisores das baterias:** 100 kΩ / 12 kΩ + 100 nF, medidos antes dos diodos ideais (21,6 V → 2,3 V no ADC).
- **Relé K1:** acionado por módulo MOSFET de nível lógico (AO3400 ou IRLZ44N) no lado de GND da bobina.

### 12.2 Pinagem do ESP32‑S3

| GPIO | Função | Direção | Nota |
| --- | --- | --- | --- |
| 1 | Tensão bateria A | ADC | ADC1 (funciona com Wi‑Fi ligado) |
| 2 | Tensão bateria B | ADC | ADC1 |
| 3 | Receptor 433 MHz | Entrada | Interrupção, decodificado no firmware |
| 4 | ESC roda superior | Saída PWM | 50 Hz, 1.000–2.000 µs |
| 5 | ESC roda inferior | Saída PWM | 50 Hz, 1.000–2.000 µs |
| 6 | Hall roda superior | Entrada | Contador de pulsos (PCNT) |
| 7 | Hall roda inferior | Entrada | Contador de pulsos (PCNT) |
| 8 | STEP agitador | Saída | Direção invertida via UART |
| 9 | Buzzer | Saída | Bip antes de cada treino |
| 10 | ENABLE drivers | Saída | Comum aos 3, ativo em nível baixo |
| 11 | UART drivers | Bidirecional | 1 kΩ em série até o PDN\_UART |
| 12 | Servo empurrador | Saída PWM | 50 Hz |
| 13 | Fim de curso giro | Entrada | Pull-up interno, NF |
| 14 | Referência do tilt | Entrada | DIAG do TMC2209 ou microchave NF |
| 15 | STEP giro | Saída |  |
| 16 | DIR giro | Saída |  |
| 17 | STEP tilt | Saída |  |
| 18 | DIR tilt | Saída |  |
| 21 | Sensor bola no tubo | Entrada |  |
| 38 | Semáforo WS2812B | Saída | 330 Ω em série |
| 39 | UART da tela (TX) | Saída | 115.200 bps |
| 40 | UART da tela (RX) | Entrada |  |
| 41 | Estado do botão de emergência | Entrada | Contato NA do cogumelo |
| 42 | Relé K1 | Saída | Via MOSFET |
| 47 | I²C SDA | — | Opcional |
| 48 | I²C SCL | — | Opcional |

O LED RGB da DevKitC‑1 fica no GPIO 38 (placa v1.1) ou 48 (v1.0) e pisca junto com o sinal desse pino; é só visual.

### 12.3 Placa, caixa e conectores

- **Placa de controle:** placa perfurada ilhada 10 × 15 cm com soquetes para o ESP32 e os 3 drivers, bornes KF301 e JST‑XH, sobre a placa de montagem impressa. Uma PCB própria (KiCad) é uma boa evolução.
- **Caixa:** ABS IP65 ~220 × 170 × 100 mm no andar de controle, com ESP32, drivers, ESCs, relé, fusíveis, conversores, receptor 433 MHz e capacitor; entradas por prensa-cabos.
- **Conectores entre andares** (nos suportes impressos): GX16‑4 para cada motor de passo, GX16‑8 para os sinais da cabeça e para o painel traseiro com o semáforo, GX16‑3 para o servo e o sensor do tubo; 2× MT60 para as fases das rodas.
- **Antenas:** cabo U.FL → SMA de painel. O ESP32 e o RXB6 ficam embaixo e as antenas no alto do andar do lançador: use uma extensão coaxial SMA (RG174, ~50 cm), solta antes de separar os andares.

## 13. Firmware e app

O firmware roda no ESP32‑S3 (Arduino via PlatformIO) e serve uma página web pelo próprio Wi‑Fi da máquina; a tela touch e o controle remoto permitem usar sem celular.

### 13.1 Bibliotecas

| Função | Biblioteca |
| --- | --- |
| Motores de passo (aceleração, posição) | FastAccelStepper |
| Configuração dos TMC2209 | TMCStepper |
| PWM dos ESCs e do servo | LEDC nativo do ESP32 (ou ESP32Servo) |
| Servidor web e tempo real | ESPAsyncWebServer + AsyncTCP (WebSocket) |
| Mensagens (app e tela) | ArduinoJson |
| Controle remoto 433 MHz | rc-switch |
| Semáforo | Adafruit NeoPixel (ou FastLED) |
| Calibração salva | Preferences (NVS) |
| Página do app | LittleFS |
| Atualização sem cabo | ElegantOTA |
| Tela (no ESP32‑S3 da própria tela) | LVGL + LovyanGFX |

### 13.2 Tarefas

1. **Controle de RPM (100 Hz, núcleo 1):** mede o período entre pulsos Hall (2 por volta), calcula o acelerador de cada ESC e sinaliza "pronto".
2. **Sequenciador de disparos:** máquina de estados que posiciona giro e tilt, libera a bola, espera "pronto", faz a contagem no semáforo e aciona o empurrador.
3. **Segurança (50 Hz):** botão de emergência, tensão das baterias, tempos-limite de sensores e sinal de vida do app.
4. **Comunicação e interface (núcleo 0):** Wi‑Fi, página web, WebSocket, tela, controle remoto e semáforo.

### 13.3 Controle de RPM

```math
acel = FF(RPM_{alvo}, V_{bat}) + K_p \cdot e + K_i \int e\,dt
```

- **Feedforward (FF):** tabela acelerador → RPM levantada automaticamente na calibração (varre de 10% a 80% e grava), corrigida pela tensão da bateria. Faz o grosso do trabalho; o PI só corrige o resto.
- **Antiwindup:** o integrador congela quando o acelerador satura.
- **Rampa:** no máximo ~1.500 rpm/s, para manter a corrente total abaixo de 25 A e poupar as correias (mais lenta com fonte AC).
- **Pronto:** erro < 1,5% nas duas rodas por 300 ms seguidos.
- **Conversão do pedido do usuário:** velocidade e spin viram RPMs pelas fórmulas da seção 3, com η e k gravados na calibração.

### 13.4 Modos de treino

- **Manual:** velocidade, spin, direção, altura e intervalo; botão grande de iniciar/parar.
- **Predefinidos:** aquecimento, drive, topspin, slice, voleio, lob, bola rápida.
- **Programa (exercício):** lista de até 20 bolas, cada uma com velocidade, spin, giro, tilt e intervalo; repetir em ordem ou sortear. O controle remoto percorre os programas salvos.
- **Aleatório:** sorteia direção e/ou altura dentro de faixas escolhidas (treino de deslocamento).
- **Estacionar:** rodas a 0, giro ao centro e cabeça a 0°, antes de desligar e transportar.

### 13.5 App no celular

- A máquina cria a rede **Lancador‑XXXX**; a página abre em 192.168.4.1. Opcionalmente entra no Wi‑Fi do clube e responde em lancador.local.
- Telas: Controle, Programas, Calibração e Status (baterias, RPMs medidas, bolas lançadas, alarmes).
- A simulação da quadra no app considera também o vento (velocidade e direção); veja a seção 3.5.
- **Sinal de vida:** se o treino começou pelo app, o celular manda um ping por segundo; sem ping por 3 s, a máquina pausa a alimentação e só retoma com novo comando.

### 13.6 Tela, controle remoto e semáforo

- **Tela touch (sem o app):** os mesmos ajustes do modo manual, escolha do exercício, baterias e alarmes. Roda firmware próprio (LVGL) e só manda pedidos em JSON pela UART; quem verifica as condições de disparo é o controlador. Sem resposta por 1 s, a tela bloqueia os comandos.
- **Controle remoto 433 MHz:** A = iniciar/retomar; B = pausar; C = próximo exercício; D = configurável (padrão: estacionar). Pareamento pela tela ou pelo app (aperte um botão em até 10 s); outros códigos são ignorados. Código fixo pode ser copiado: o controle é conveniência, não segurança.
- **Semáforo:** vermelho fixo = parado ou rodas acelerando; amarelo piscando = próxima bola em breve (contagem); verde = disparo; tudo vermelho piscando = emergência ou falha. Brilho ajustável (mais alto ao sol).

### 13.7 Condições para disparar

Todas precisam ser verdadeiras: botão de emergência solto e relé K1 fechado; bola no tubo confirmada; giro e tilt na posição; as duas rodas "prontas"; baterias acima de 15,5 V; contagem do semáforo concluída; app conectado (só se o treino começou pelo app).

## 14. Lista de materiais — itens comprados

São ~70 linhas de compra, quase todas encontráveis no Mercado Livre, AliExpress ou em lojas de perfil de alumínio; a coluna "Especificação" é o termo de busca.

### 14.1 Estrutura e mecânica

| Item | Especificação | Qtd |
| --- | --- | --- |
| Perfil de alumínio | 20×20 canal 6, cortado conforme a lista da seção 5.2 (~4,1 m) | 16 peças |
| Cantoneira | Cantoneira 20×20 para perfil canal 6 | 4 |
| Porca-T | Porca-T M4 e M5 para canal 6 | 20 |
| Fechos | Fecho de pressão inox pequeno (tipo caixa de ferramentas) | 8 |
| Rolamento do giro | Lazy susan redondo Ø150 (6"), de esferas | 1 |
| Cantoneiras do garfo | Cantoneira de alumínio 40×40×3 (2 × 60 mm) | 1 barra 0,2 m |
| Mancal das rodas | KFL001 flange 2 furos, eixo 12 mm | 4 |
| Mancal do tilt | KFL08 flange, eixo 8 mm | 2 |
| Colar Ø8 | Colar trava eixo 8 mm | 4 |
| Colar Ø12 | Colar trava eixo 12 mm | 4 |
| Eixo das rodas de lançamento | Eixo retificado Ø12 h6 (2 × 140 mm) ou usinado (seção 16) | 1 barra 300 mm |
| Semi-eixos do tilt | Eixo retificado Ø8 (50 + 65 mm) | 1 barra 150 mm |
| Correias das rodas | Correia HTD 3M 9 mm fechada: 600‑3M‑9 e 288‑3M‑9 | 1 de cada |
| Polias dos motores | Polia HTD 3M 20 dentes, furo 5 mm, para correia de 9 mm | 2 |
| Polias das rodas | Polia HTD 3M 20 dentes, furo 12 mm, para correia de 9 mm | 2 |
| Espaçadores da cabeça | Espaçador de alumínio M5 × 90 mm | 4 |
| Pinos | Parafuso de ombro M6 × 30 (giro) e Ø6 × 6 rosca M5 (manivela) | 2 |
| Rolamento 608 | Ponta do fuso do giro | 1 |
| Tubo de queda | Cano PVC esgoto DN75 | 0,3 m |
| Trilhos-guia | Vareta de alumínio Ø8 (2 × 215 mm) | 0,5 m |
| Rodas de transporte | Roda de patins inline Ø125 × 24 + rolamentos 608 | 2 + 4 |
| Pés | Pé de borracha M8 regulável | 2 |
| Alça | Alça telescópica de mala (reposição, 2 tubos) | 1 |
| Varetas do cesto | Vareta ou tubo de alumínio Ø8 (4 × ~285 mm + aro de ~1,95 m) | ~3,1 m |
| Tela do cesto | Tela de PVC/poliéster (tipo tela de cadeira), ~0,5 m², costurada em 4 painéis | 1 |
| Ímãs | Neodímio 6 × 3 mm | 10 |
| Microchaves | Fim de curso com alavanca (giro; tilt opcional) | 2 |
| Deslizante do agitador | Folha de PTFE ou UHMW 0,5 mm | 1 |
| Batentes | Batente de borracha M5 (repouso do tilt) | 4 |

### 14.2 Motores e eletrônica

| Item | Especificação | Qtd |
| --- | --- | --- |
| Motor das rodas | Brushless outrunner 4250 (Ø42 × 50 mm), 400–500 KV, eixo 5 mm invertível, ≥ 600 W | 2 |
| ESC | ESC brushless 60–80 A, 2–6S | 2 |
| Motor do giro | NEMA17 com fuso trapezoidal Tr8×8 integrado, 100 mm, com porca | 1 |
| Motor do tilt | NEMA17 com fuso trapezoidal Tr8×2 integrado (passo de 2 mm), 100 mm, com porca | 1 |
| Motor do agitador | NEMA17 curto (~34 mm) | 1 |
| Drivers | TMC2209 (módulo stepstick) | 3 |
| Microcontrolador | ESP32‑S3‑DevKitC‑1U‑N8R8 (conector U.FL) | 1 |
| Tela touch | Placa ESP32‑S3 com tela IPS 3,5" touch | 1 |
| Servo | Servo rápido 20–25 kg·cm, ≤ 0,07 s/60°, engrenagem metálica, tamanho padrão | 1 |
| Sensor de RPM | Módulo Hall A3144 | 2 |
| Sensor de bola | E18‑D80NK | 1 |
| Controle remoto | Receptor RXB6 433 MHz + controle chaveiro 4 botões 433 MHz | 1 + 1 |
| Antenas | Antena articulada SMA 433 MHz e 2,4 GHz | 1 de cada |
| Cabos de antena | Conector SMA fêmea de painel com cabo U.FL + extensão SMA RG174 ~50 cm | 2 + 2 |
| Semáforo | LEDs WS2812B (fita 60 LED/m, 12 LEDs) | 1 |
| Conversor 5 V | Buck LM2596 ou MP1584, 3 A | 1 |
| Conversor 6 V | Buck XL4015, 5 A | 1 |
| Conversor 12 V | Buck 1 A | 1 |
| Relé K1 | Relé automotivo 12 V 40 A + soquete | 1 |
| Acionador do relé | Módulo MOSFET nível lógico (AO3400 / IRLZ44N) | 1 |
| Buzzer | Buzzer ativo 5 V | 1 |
| Opcional | INA226 + shunt 50 A | 1 |

### 14.3 Potência, conectores e fiação

| Item | Especificação | Qtd |
| --- | --- | --- |
| Baterias (se ainda não tiver) | Makita BL1850B 18 V 5,0 Ah | 2 |
| Soquete de bateria | Adaptador para bateria Makita 18 V com fios 12 AWG | 2 |
| Diodo ideal | Módulo diodo ideal ≥ 30 A, 12–24 V | 2 (+1 com AC) |
| Chave liga/desliga | Chave eletrônica anti-faísca ≥ 60 A, 2–6S, com fio para chave externa | 1 |
| Botão liga/desliga | Botão 22 mm com retenção e anel de LED 12 V, 1NA | 1 |
| Botão de emergência | Cogumelo 22 mm, 1NA + 1NF (de painel) | 1 |
| Fusíveis | Porta-fusível lâmina inline + kit de fusíveis (2–30 A) | 8 |
| Conectores de potência | XT90, XT60, MT60 (3 vias), bullets 4 mm | kit |
| Conectores entre andares | Aviação GX16 (3, 4 e 8 pinos), pares | 7 |
| Fio | Silicone 12 AWG (1,5 m vermelho + 1,5 m preto), 14 AWG (2 m de cada), 18 e 22 AWG | — |
| Cabo de motor de passo | Cabo manga 4 × 22 AWG | 3 m |
| Caixa | Caixa ABS IP65 ~220 × 170 × 100 mm | 1 |
| Prensa-cabos | PG7 / PG9 / PG11 | 10 |
| Placa | Placa perfurada ilhada 10 × 15 cm, bornes KF301, JST‑XH, barras de pinos | kit |
| Passivos | Resistores 330/1 k/10 k/12 k/20 k/100 k, capacitores 100 nF e 1.000 µF/35 V, diodo 1N4007 | kit |
| Acabamento | Termorretrátil, malha trançada, abraçadeiras | kit |

### 14.4 Entrada AC (opcional, fase 2)

| Item | Especificação | Qtd |
| --- | --- | --- |
| Fonte | Mean Well LRS‑350‑24 | 1 |
| Tomada | IEC C14 com porta-fusível e chave | 1 |
| Cabo de força | Cabo IEC C13, 3 m | 1 |

## 15. Peças impressas em 3D

São 35 tipos de peça (41 arquivos STL, contando as 4 partes da rampa e as 3 versões espelhadas), ~2,5–3 kg de PETG e ~0,4 kg de TPU; nada em PLA, porque na quadra, ao sol, o PLA amolece a partir de ~55 °C.

**Padrão (salvo indicação):** PETG, bico 0,4 mm, camada 0,2 mm, 4 perímetros, 30% gyroid, insertos de latão M3/M4/M5 colocados a quente onde houver parafuso. Peças expostas ao sol direto podem ser em ASA. As peças saem na posição de montagem: gire no fatiador para a melhor orientação.

| Peça | Material | Qtd | Notas |
| --- | --- | --- | --- |
| Núcleo da roda Ø134 × 32 mm | PETG, ASA ou PA‑CF | 2 | 6 perímetros, 60% gyroid, 5 camadas sólidas; ranhuras para a banda |
| Banda de rodagem Ø150 × 40 mm, perfil côncavo | TPU 95A | 2 + 2 reserva | 4 perímetros, 50% gyroid, 20–30 mm/s, extrusora direta |
| Disco de sinal Ø40 × 8 mm (2 ímãs) | PETG | 2 | Preso no eixo, fora da placa |
| Suportes do sensor Hall, dos trilhos e do servo | PETG | 2 + 1 + 1 | Hall com ajuste de 2–4 mm até o disco |
| Berço da bola 90 × 77 × 22 mm | PETG | 1 | Rasgo do empurrador e furos dos trilhos |
| Funil da cabeça 90 × 145 × 19 mm | PETG | 1 | Boca 84 × 140 → Ø78 |
| Braço do empurrador | PETG + ponta em TPU | 1 | 100% infill no cubo do servo |
| Carenagens das rodas 89 × 170 × 111 mm | PETG ou ASA | 1 + 1 | De cima e de baixo |
| Tampas das correias | PETG | 1 + 1 | 27 × 201 × 253 mm (de cima) e 27 × 152 × 47 mm (de baixo); 2 espaçadores M3 cada |
| Suportes dos motores do giro (em L) e do tilt (no garfo −x) | PETG | 1 + 1 |  |
| Mancal da ponta do fuso do giro | PETG | 1 | Rolamento 608 |
| Blocos das porcas do giro e do tilt 28 × 24 × 28 mm | PETG | 1 + 1 | Rasgo para o pino |
| Rotor do agitador Ø220 × 56 mm | PETG | 1 | Disco com cúpula e 4 bolsões; cabe em mesa de 235 mm |
| Capuz do furo de saída 116 × 88 × 70 mm | PETG | 1 |  |
| Rampas do alimentador | PETG | 4 partes | As 2 da frente têm 155 × 256 mm: mesa de 256 mm ou um corte a mais |
| Flange do tubo de queda 103 × 102 × 15 mm | PETG | 1 |  |
| Dobradiças e cantos do cesto | PETG | 4 + 4 | Cantos: 2 espelhados; dobradiças presas no aro por M3 |
| Pinos de centragem e blocos dos pinos | PETG | 2 + 2 | Pino rosqueado (M5) no bloco; bloco preso no canal do poste |
| Pino-guia Ø10 do alimentador | PETG | 2 | M4 + porca-T na travessa do topo |
| Suporte dos conectores entre andares | PETG | 3 |  |
| Abraçadeira da alça 42 × 40 × 26 mm | PETG | 4 (2 espelhadas) |  |
| Berço do soquete de bateria 85 × 130 × 8 mm | PETG | 2 | Com guia de encaixe |
| Placa de montagem 200 × 154 × 3 mm | PETG | 1 | Dentro da caixa IP65 |
| Painel traseiro 249 × 26 × 100 mm | PETG ou ASA | 1 | Janela da tela e 2 furos de 22 mm |
| Semáforo: caixa com pala 132 × 46 × 44 mm e difusores Ø28 × 2 mm | ASA ou PETG preto; difusores em PETG natural | 1 + 3 |  |
| Suporte da antena | PETG | 2 (1 espelhado) | Leva o conector SMA de painel |

## 16. Peças metálicas terceirizadas

Todas as chapas saem de um único pedido de corte a laser (alumínio e aço, 10 arquivos DXF); os eixos podem ser barra retificada cortada em casa ou peça de torno.

### 16.1 Corte a laser

| Peça | Material | Espessura | Qtd | Dimensões aprox. | Notas |
| --- | --- | --- | --- | --- | --- |
| Piso do andar de controle | Alumínio 5052 | 3 mm | 1 | 312 × 422 mm | Berços das baterias, pés, caixa IP65 |
| Base do andar do lançador | Alumínio 5052 ou 6061 | 4 mm | 1 | 312 × 422 mm | Lazy susan, furo Ø40, pinos, giro, conectores |
| Base do alimentador | Alumínio 5052 | 3 mm | 1 | 312 × 422 mm | Furo de saída Ø76 em (0, −116), agitador, rampas |
| Aro do topo | Alumínio 5052 | 3 mm | 1 | 312 × 422 mm | Moldura de 30 mm |
| Placa lateral da cabeça | Alumínio 6061 | 6 mm | 2 | 347 × 310 mm | Mesma peça nos dois lados; oblongos na roda de baixo e nos motores |
| Garfo do tilt | Alumínio 6061 | 6 mm | 2 | 60 × 235 mm |  |
| Manivela do tilt | Alumínio 6061 | 6 mm | 1 | 42 × 87 mm | Furo em D para o semi-eixo |
| Plataforma giratória | Alumínio 5052 ou 6061 | 4 mm | 1 | 197 × 156 mm | Pino do giro a 102 mm |
| Suporte da roda de transporte | Alumínio 5052 | 4 mm | 2 | 70 × 100 mm |  |
| Discos de inércia | Aço 1020 | 3 mm | 4 | Ø120 mm | Furo em D + 6 × Ø4,4; zincar ou pintar |

O PDF de pranchas traz as cotas gerais de cada peça. Antes de enviar, confira com a peça na mão a furação de KFL001 (M6 a 48 mm), KFL08 (M4 a 37 mm), lazy susan e motor 4250.

### 16.2 Usinagem (opcional)

| Peça | Material | Qtd | Especificação |
| --- | --- | --- | --- |
| Eixo da roda de lançamento | Aço 1045 retificado | 2 | Ø12 h6 × 140 mm, chato de 1 mm em todo o comprimento |
| Semi-eixo do tilt | Aço retificado Ø8 | 2 | Lado +x: 50 mm; lado −x: 65 mm com chato (7 mm entre faces) na ponta |
| Eixo da roda de transporte | Aço | 2 | Ø8 × 60 mm; pode ser um parafuso de ombro Ø8 |

Se preferir não terceirizar: compre barra retificada Ø12 e Ø8, corte com serra de metal e faça os chatos com lima ou esmerilhadeira.

### 16.3 O que enviar ao fornecedor

- **DXF em escala 1:1, em milímetros**, uma peça por arquivo, só com contornos fechados.
- **Planilha do pedido:** peça, material, espessura e quantidade. Nenhuma chapa da v2 é dobrada.
- **Furos:** diâmetro mínimo = espessura da chapa. O laser não faz rosca: marque os furos a rosquear (M4, M5, M6) e rosqueie em casa com macho.
- **Tolerância:** ±0,2 mm é o normal do laser e basta, porque os mancais são parafusados (não há encaixe sob pressão).
- **Acabamento:** peça rebarbação. Anodizar ou pintar é opcional.
- **Fornecedor:** serviços brasileiros com orçamento por upload de DXF, ou metalúrgica local com laser de fibra. Compare 2–3 orçamentos; agrupar tudo num pedido reduz bastante o custo. Serviços do exterior somam frete e imposto de importação.

### 16.4 Carenagem (só STEP, material a definir)

A carenagem não vai no pedido de laser. Os 4 STEP (três painéis e a tampa das baterias) são a referência de forma e de recortes para o material escolhido:

- **Molde injetado (ABS ou PP):** melhor acabamento e resistência; o molde só compensa em lote.
- **Termoformagem** em chapa de ABS ou PETG: molde simples, bom para poucas unidades; recortes feitos depois.
- **Impressão em partes** (PETG ou ASA), unidas por parafuso ou cola: sem molde, muitas horas de impressão.
- **ACM ou chapa composta:** painéis planos; os cantos R30 viram cantos vivos ou peças de canto impressas.

Ajuste a espessura de parede ao material e confira de novo a folga até a cabeça.

## 17. Fixadores e consumíveis

Compre um kit de parafusos allen inox M3–M6 e os itens abaixo; tudo que gira ou vibra leva trava-rosca.

| Item | Qtd aprox. | Uso |
| --- | --- | --- |
| Parafusos M6 × 20 + porcas autotravantes | 8 | KFL001 nas placas laterais (48 mm entre furos) |
| Parafusos M4 × 16 + porcas autotravantes | 4 | KFL08 no garfo (37 mm entre furos) |
| Parafusos M4 × 45 + porcas autotravantes | 12 | Discos de aço + núcleo das rodas |
| Parafusos M5 × 12 (cilíndrica e escareada) | 40 | Postes nas chapas; espaçadores da cabeça |
| Parafusos M5 e M4 para porca-T | 20 | Blocos dos pinos, pinos-guia, suportes das antenas |
| Parafusos M4 × 10–16 + porcas | 40 | Lazy susan, cantoneiras do garfo, peças impressas nas chapas |
| Parafusos M3 × 8 / × 10 | 40 | NEMA17 (31 mm), X‑mount dos 4250 (r 19 mm), sensores |
| Espaçadores M3 (~20 mm) | 4 | Tampas das correias |
| Parafusos M3 × 25 + porcas autotravantes | 4 | Pinos das dobradiças do cesto |
| Parafusos M3 ou rebites 3 mm | 32 | Fechos de pressão |
| Porcas M8 + arruelas | 4 | Pés de borracha no piso |
| Insertos de latão M3, M4 e M5 (colocação a quente) | 30 de cada | Peças impressas |
| Arruelas lisas e de pressão M3–M8 | kit |  |
| Trava-rosca média (azul) | 1 | Todo parafuso em peça que gira ou vibra |
| Cola PU ou adesivo instantâneo flexível | 1 | Banda de TPU no núcleo |
| Graxa branca de lítio | 1 | Fusos do giro e do tilt, lazy susan |
| Fita dupla face VHB | 1 rolo | Sensores e chicotes |
| Estanho 60/40 ou sem chumbo + fluxo | 1 | Solda da eletrônica |
| Macho de rosca M3, M4, M5 e M6 + desandador | 1 jogo | Furos das chapas e pontas dos perfis |

## 18. Sequência de montagem

Monte e teste a eletrônica na bancada antes de instalar, e a cabeça antes de colocá-la no garfo; depois monte um andar de cada vez, de baixo para cima.

1. **Preparação**
   - Imprima as peças, receba as chapas, rebarbe todas as bordas.
   - Rosqueie os furos marcados nas chapas e o furo central (M5) nas pontas de todos os postes; escareie os furos das bases do lançador e do alimentador.
2. **Eletrônica na bancada**
   - Solde a placa de controle e monte a caixa IP65 com conversores, ESCs, relé, fusíveis, receptor 433 MHz e conectores.
   - **Ajuste a saída dos conversores (5 V, 6 V, 12 V) antes de ligar qualquer carga.**
   - Teste cada subsistema com uma bateria (seção 19, passos 1–4), incluindo a tela e o pareamento do controle remoto.
3. **Andar de controle:** piso, postes de 112 mm, blocos e pinos de centragem, pés, suportes, eixos e rodas de transporte, berços e soquetes das baterias, diodos ideais, chave anti-faísca, caixa IP65 e suportes de conectores.
4. **Rodas de lançamento**
   - Núcleo + discos de aço + parafusos M4 (trava-rosca) + banda de TPU; polia no eixo.
   - Balanceamento estático (seção 6.2).
5. **Cabeça**
   - Placas laterais com espaçadores e KFL001; eixos, rodas e colares.
   - Motores por dentro das placas, polias por fora, correias esticadas pelos oblongos.
   - Ajuste o vão em 56 mm (um bloco de 56 mm serve de calibre) e aperte os mancais de baixo.
   - Sensores Hall, berço, funil, trilhos, servo e braço, carenagens das rodas, tampas das correias.
   - Gire cada roda à mão: livre, sem bater em nada e sem a correia pular dente.
6. **Andar do lançador**
   - Base, lazy susan, plataforma e garfo; atuador do giro (suporte, mancal 608, bloco-porca, pino) e microchave.
   - KFL08, cabeça com semi-eixos e colares, manivela, atuador do tilt.
   - Postes de 536 mm e quadro do topo; painel traseiro, semáforo, suportes das antenas, alça.
   - À mão: giro ±12,5° e tilt 0–30° sem prender e sem tocar em nada.
7. **Andar do alimentador:** base, motor do agitador por baixo, PTFE, rotor, capuz, rampas, postes de 79 mm, aro do topo, flange e tubo com sensor.
8. **Cesto:** dobradiças, varetas, cantos e aro de cima, tela. Confira que dobra e abre sem forçar a tela.
9. **Empilhar:** controle → lançador (pinos de centragem) → alimentador (pinos-guia); ligue os conectores entre andares.
10. **Fiação final**
    - Chicote da cabeça pelo furo central com laço de 15–20 cm.
    - Potência: soquetes → fusíveis → diodos ideais → chave anti-faísca → barramento → relé → ESCs.
    - Sem bateria: confira polaridade e continuidade de cada ligação.
11. **Proteções:** carenagens das rodas e tampas das correias; carenagem externa e fechos, se houver.
12. **Comissionamento:** seção 19 completa.

## 19. Testes e comissionamento

São 13 testes em ordem, cada um com critério de aprovação; só avance quando o anterior passar.

| # | Teste | Como | Passa se |
| --- | --- | --- | --- |
| 1 | Inspeção sem energia | Multímetro entre + e − do barramento; fusíveis no lugar | Sem curto (a resistência sobe enquanto os capacitores carregam) |
| 2 | Primeira energia | Bateria com fusível temporário de 5 A no lugar do de 30 A | Botão liga e desliga a chave anti-faísca; 5,0 / 6,0 / 12 V corretos; nada esquenta |
| 3 | Leituras e interfaces | Firmware de teste mostra tensões e sensores na tela e no app | Baterias ±0,1 V do multímetro; cada sensor muda de estado; controle pareado; semáforo acende |
| 4 | Motores de passo | Comunicação UART, sentido, referência (homing) e limites | Giro e tilt voltam ao mesmo ponto em 10 referências seguidas; giro −12,5° a +12,5° e tilt 0° a +30° sem tocar em nada |
| 5 | Agitador | Liberar 20 bolas | 20 bolas, nenhuma dupla, nenhum travamento; detecta cesto vazio |
| 6 | Empurrador (rodas paradas) | 50 ciclos em 0°, 15° e 30° | A bola chega sempre até as rodas |
| 7 | ESCs | Calibrar a faixa do acelerador de cada ESC; conferir sentido | Nas duas rodas, a superfície que toca a bola anda para a frente (se não, troque 2 fases) |
| 8 | RPM em degraus | 1.000 → 2.000 → 3.000 rpm, 5 min a 3.000 | Hall = tacômetro óptico ±1%; sem vibração anormal nem salto de dente; motores e mancais < 50 °C |
| 9 | Rotação máxima | 5.500 rpm por 2 min, ninguém na lateral das rodas | Banda, parafusos, correias e carenagens intactos depois |
| 10 | Tabela de feedforward | Rotina automática de calibração | RPM alvo atingida em < 3 s, erro final < 1% |
| 11 | Primeiros disparos | 40 km/h, spin 0, tilt 0, em quadra vazia | Saída limpa, sem a bola raspar na carenagem da roda nem na janela |
| 12 | Calibração de η e k | Velocidade: app de radar ou vídeo em câmera lenta com distância marcada. Spin: bola riscada filmada em câmera lenta | Velocidade e spin medidos ±5% do pedido |
| 13 | Repetibilidade e segurança | 20 bolas iguais; botão de emergência com rodas girando; derrubar o Wi‑Fi num treino do app; pausar pelo controle | Dispersão < 1 m a 20 m; relé abre na hora; alimentação pausa em 3 s; controle pausa em < 0,5 s |

Depois disso, faça um treino completo com bateria cheia e anote a autonomia real para conferir a seção 3.4.

## 20. Segurança

Os dois riscos sérios desta máquina são as rodas a 5.500 rpm e a bola a 120 km/h; o resto é cuidado elétrico normal.

- **Plano das rodas:** se uma banda ou roda soltar, ela sai para os lados e para cima, no plano de giro. Nos testes de rotação alta, ninguém fica ao lado da cabeça.
- **Inspeção:** a cada ~10 h de uso, procure trincas no núcleo e desgaste na banda, confira o aperto dos parafusos M4 e a tensão e o desgaste das correias. O firmware nunca passa de 5.500 rpm.
- **Mãos fora da cabeça:** as rodas giram 10–30 s depois de desligar. Só mexa quando o app ou a tela mostrar 0 rpm. O modo manutenção bloqueia giro, tilt e empurrador.
- **Sem carenagem externa:** nunca rode sem as carenagens impressas das rodas e as tampas das correias, e mantenha as mãos fora do andar do lançador com a máquina ligada (giro e tilt prensam dedos).
- **Bola:** a 120 km/h machuca, principalmente olhos. Use óculos nos testes, mantenha crianças e curiosos atrás da máquina e nunca mire em pessoas fora do treino.
- **Controle remoto:** serve para pausar de longe, mas não é dispositivo de segurança; o botão de emergência fica na traseira.
- **Baterias:** fusível perto de cada fonte de energia; tire as baterias antes de mexer na fiação (a chave anti-faísca é eletrônica); não deixe a máquina com baterias ao sol sem uso; carregue só no carregador Makita.
- **AC (fase 2):** só com fonte fechada, terra ligado e revisão de um eletricista. Nunca abra a caixa da fonte com o cabo na tomada.
- **Peso:** ~20 kg sem carenagem. Para pôr no carro, levante em duas pessoas ou separe os andares.
- **Oficina:** bordas de chapa cortada a laser são afiadas (rebarbe); solde em local ventilado.

## Fontes

- [Goodwill, Chin & Haake (2004), Aerodynamics of spinning and non-spinning tennis balls](https://shura.shu.ac.uk/634/): arrasto e sustentação de bolas de tênis girando, base do simulador da seção 3.5.
- [Mean Well LRS‑350, folha de dados](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF): faixa de ajuste, seleção de entrada e pico de carga.
- [PartsBuilt, adaptador Makita com corte de subtensão](https://partsbuilt.com/makita-18v-battery-adapter): exemplo de proteção extra contra descarga profunda.
