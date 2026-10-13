# Lista unificada do MVP

Uma linha por item igual, somando todas as peças do MVP. **Usa** é o que vai na máquina; **Comprar** já inclui reserva e o tamanho em que o item costuma ser vendido. A mesma lista está em [`lista_mvp.csv`](lista_mvp.csv) para abrir na planilha (separador `;`).

Itens marcados **só bancada** não vão para a máquina completa. Todo o resto vai.

## Mecânica

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Rolamento lazy susan redondo Ø150 (6") | furação: confira com o CAD antes do corte | 1 | 1 | giro |
| Mancal KFL001 | Ø12, 2 furos M6 a 48 mm | 4 | 4 | rodas |
| Mancal KFL08 | Ø8, 2 furos M4 a 37 mm | 2 | 2 | pivô do tilt |
| Rolamento 608ZZ | 8 × 22 × 7 | 1 | 2 | ponta do fuso do giro |
| Polia HTD 3M 20 dentes, furo 5 mm | para correia de 9 mm (largura 15) | 2 | 2 | motores 4250 |
| Polia HTD 3M 20 dentes, furo 12 mm | para correia de 9 mm (largura 15) | 2 | 2 | eixos das rodas |
| Correia HTD 600-3M-9 fechada | 600 mm, 9 mm | 1 | 1 | roda de cima |
| Correia HTD 288-3M-9 fechada | 288 mm, 9 mm | 1 | 1 | roda de baixo |
| Colar de trava Ø12 | com parafuso | 4 | 4 | eixos das rodas |
| Colar de trava Ø8 | com parafuso | 4 | 4 | semi-eixos |
| Eixo linear retificado Ø12 h6, barra de 300 mm | rende os 2 eixos de 134 mm | 1 | 1 | rodas · ver 3-usinar |
| Eixo linear retificado Ø8, barra de 150 mm | rende os semi-eixos de 50 e 65 mm | 1 | 1 | pivô do tilt · ver 3-usinar |
| Vareta de alumínio Ø8, barra de 500 mm | rende os 2 trilhos de 215 mm | 1 | 1 | guia da bola |
| Espaçador de alumínio M5 × 90, fêmea-fêmea |  | 4 | 4 | entre as placas laterais |
| Cantoneira de alumínio 40 × 40 × 3, peça de 300 mm | rende as 2 de 60 mm | 1 | 1 | garfos na plataforma · furos Ø4,5 na montagem |
| Perfil de alumínio 20 × 20 canal 6, 500 mm | rende os 4 postes de 112 mm | 1 | 1 | pernas no MVP, postes do andar de controle depois · rosca M5 no furo central das duas pontas |
| Pé de borracha Ø25 com parafuso M5 |  | 4 | 4 | embaixo das pernas |
| Parafuso de ombro Ø6 × 30, rosca M5 (ISO 7379) |  | 1 | 1 | pino do giro |
| Parafuso de ombro Ø6 × 6, rosca M5 (ISO 7379) |  | 1 | 1 | pino da manivela do tilt |
| Ímã de neodímio Ø6 × 3 |  | 4 | 10 | discos de sinal |

## Motores e sensores

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Motor brushless outrunner 4250, 400–500 KV | eixo de 5 mm, montado invertido (atravessa a placa) | 2 | 2 | rodas |
| NEMA17 com fuso Tr8×8 integrado de 100 mm | com porca de latão flangeada | 1 | 1 | giro |
| NEMA17 com fuso Tr8×2 integrado de 100 mm | com porca de latão flangeada; passo 2 mm não volta sozinho | 1 | 1 | tilt |
| Servo 20–25 kg·cm, ≤ 0,07 s/60°, tamanho padrão | como o DS3225; com horn redondo de alumínio 25T | 1 | 1 | empurrador |
| Sensor Hall A3144 (TO-92, avulso) | se vier em módulo, tire o resistor de pull-up para 5 V | 2 | 5 | RPM das rodas |
| Microchave fim de curso com alavanca | KW12 / V-156, contato NF usado | 1 | 2 | referência do giro |

## Fixadores

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Parafuso M3 × 8 cabeça cilíndrica (Allen) | aço zincado ou inox A2 | 6 | 10 | NEMA17 do giro (4), braço no horn do servo (2) |
| Parafuso M3 × 10 cabeça cilíndrica | aço zincado ou inox A2 | 12 | 20 | X-mount dos motores 4250 (8), NEMA17 do tilt (4) |
| Parafuso M3 × 12 cabeça cilíndrica | aço zincado ou inox A2 | 12 | 20 | orelhas do servo (4), flanges das porcas Tr8 (8) |
| Parafuso M3 × 30 cabeça cilíndrica | aço zincado ou inox A2 | 2 | 5 | suportes Hall |
| Parafuso M3 × 35 cabeça cilíndrica | aço zincado ou inox A2 | 4 | 5 | tampas das correias |
| Parafuso sem cabeça (grub) M3 × 6 | aço zincado ou inox A2 | 2 | 5 | discos de sinal no eixo |
| Porca M3 autotravante | aço zincado ou inox A2 | 18 | 30 | servo, Hall, tampas, X-mount |
| Arruela M3 | aço zincado ou inox A2 | 20 | 30 | geral |
| Parafuso M4 × 10 cabeça cilíndrica | aço zincado ou inox A2 | 13 | 20 | lazy susan (8), ponta do semi-eixo (1), berço nos insertos (4) |
| Parafuso M4 × 12 cabeça cilíndrica | aço zincado ou inox A2 | 12 | 20 | garfo–cantoneira (4), cantoneira–plataforma (4), suporte do motor do giro (2), mancal do fuso (2) |
| Parafuso M4 × 16 cabeça cilíndrica | aço zincado ou inox A2 | 6 | 10 | KFL08 (4), suporte do motor do tilt (2) |
| Parafuso M4 × 45 cabeça cilíndrica | aço zincado ou inox A2 | 12 | 15 | rodas: 6 por roda, atravessam disco + núcleo + disco |
| Parafuso M4 × 50 cabeça cilíndrica | aço zincado ou inox A2 | 2 | 5 | suporte do servo |
| Barra roscada M4 × 1 m | aço zincado ou inox A2 | 1 | 1 | 7 varetas de 110 mm: carenagens das rodas (4), funil (2), suporte dos trilhos (1) |
| Porca M4 autotravante | aço zincado ou inox A2 | 54 | 60 | todas as uniões M4 acima |
| Arruela M4 | aço zincado ou inox A2 | 90 | 100 | geral (duas por vareta, uma por parafuso) |
| Inserto roscado M4 para plástico (Ø5,6–6 × 8 mm) | latão | 4 | 10 | berço |
| Parafuso M2 × 10 + porca | aço zincado ou inox A2 | 2 | 4 | microchave do giro |
| Parafuso M5 × 12 cabeça cilíndrica | aço zincado ou inox A2 | 12 | 15 | espaçadores entre placas (8), pernas na chapa (4) |
| Porca M5 | aço zincado ou inox A2 | 2 | 5 | pinos de ombro do giro e da manivela |
| Parafuso M6 × 20 cabeça sextavada | aço zincado ou inox A2 | 8 | 10 | KFL001 nas placas laterais |
| Porca M6 autotravante | aço zincado ou inox A2 | 8 | 10 | KFL001 |
| Arruela M6 | aço zincado ou inox A2 | 16 | 20 | KFL001 |

## Eletrônica

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Fonte de bancada 19–24 V, ≥ 5 A, com limite de corrente | a sua; se for comprar, chaveada 24 V 10 A | 1 | 1 | alimentação · só bancada |
| ESP32-S3-DevKitC-1U-N8R8 | versão U = antena externa | 1 | 1 | placa de controle |
| Antena 2,4 GHz + cabo U.FL → SMA |  | 1 | 1 | Wi-Fi |
| Driver TMC2209 (módulo UART) com dissipador | como o BTT TMC2209 v1.3 | 2 | 3 | giro e tilt · o 3º vai para o agitador depois |
| ESC 60–80 A, 2–6S, freio desligável | BLHeli_32 ou AM32 | 2 | 2 | rodas · freio OFF |
| Módulo diodo ideal ≥ 30 A, até 30 V |  | 1 | 1 | entrada (vira o da bateria A) |
| Relé automotivo 12 V ≥ 40 A + soquete |  | 1 | 1 | K1, corta os ESCs |
| Porta-fusível MAXI + fusível 40 A |  | 1 | 1 | ramo das rodas · +1 fusível de reserva |
| Porta-fusível lâmina em linha 12 AWG + fusível 30 A |  | 1 | 1 | entrada · +1 fusível de reserva |
| Bloco de fusíveis lâmina 6 vias com barra negativa |  | 1 | 1 | ramo da lógica |
| Fusíveis lâmina ATO 2 A / 3 A / 5 A | F4 / F2 / F1 e F3 | 4 | 8 | bloco de fusíveis · 2 de cada |
| Conversor buck MP1584EN | 28 V máx. na entrada | 2 | 3 | 5,1 V (F2) e 12 V (F4) |
| Conversor buck XL4015 5 A |  | 1 | 1 | 6,0 V do servo (F3) |
| Barramento de latão, 4 bornes M5 |  | 1 | 1 | +BAT |
| Barramento de latão, 3 bornes M5 |  | 1 | 1 | +MOT |
| Barramento de latão, 6 bornes M5 |  | 1 | 1 | GND |
| Botão de emergência 22 mm, cogumelo com trava, 1NA + 1NF |  | 1 | 1 | emergência |
| Caixa de botoeira 1 furo 22 mm |  | 1 | 1 | emergência na bancada · só bancada |
| Caixa IP65 ~250 × 200 × 100 mm |  | 1 | 1 | eletrônica |
| Prensa-cabo PG7 / PG9 / PG11 (kit) |  | 8 | 10 | entradas da caixa |
| Placa perfurada ilhada 10 × 15 cm | dupla face | 1 | 2 | placa de controle |
| Barra de pinos fêmea 1 × 40 |  | 2 | 2 | ESP32 e TMC2209 removíveis |
| Barra de pinos macho 1 × 40 |  | 1 | 1 | jumpers de endereço |
| Borne KF301 2 vias (5,08 mm) |  | 7 | 10 | entradas de potência da placa e K1 |
| Conectores JST-XH 2, 3 e 4 vias (kit com crimpagem) |  | 1 | 1 | sinais na placa |
| MOSFET IRLZ44N (TO-220) | nível lógico | 1 | 2 | bobina do K1 |
| Diodo 1N4007 |  | 1 | 5 | roda-livre da bobina do K1 |
| Resistor 10 kΩ 1/4 W |  | 8 | 20 | pull-ups e pull-downs |
| Resistor 1 kΩ 1/4 W |  | 1 | 5 | UART dos drivers |
| Resistor 330 Ω 1/4 W |  | 1 | 5 | sinal do servo |
| Resistor 100 Ω 1/4 W |  | 1 | 5 | gate do IRLZ44N |
| Capacitor cerâmico 100 nF |  | 8 | 10 | filtros e desacoplamento |
| Capacitor eletrolítico 100 µF / 35 V |  | 2 | 3 | VM de cada driver |
| Capacitor eletrolítico 1.000 µF / 35 V |  | 1 | 2 | entrada VM da placa |
| Cabo USB-C de dados, 2 m |  | 1 | 1 | computador → ESP32 |

## Fios e conectores

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Par MT60 (macho + fêmea) |  | 2 | 2 | X1, X2 (fases das rodas) |
| Par GX16-8 (plugue de cabo + soquete de painel) |  | 4 | 4 | X3, X4, X5, X6 |
| Par XT60 |  | 1 | 2 | entrada de força |
| Plugue banana 4 mm (vermelho + preto) |  | 2 | 2 | cabo da fonte · só bancada |
| Terminal olhal M5 para 10–12 AWG |  | 10 | 20 | barramentos |
| Terminal faston 6,3 mm isolado para 10–12 AWG |  | 5 | 10 | relé K1 |
| Ponteiras (ilhós) 0,5–2,5 mm², kit |  | 1 | 1 | bornes |
| Fio de silicone 10 AWG vermelho |  | 0,5 m | 1 m | +BAT, K1, +MOT |
| Fio de silicone 12 AWG vermelho |  | 1,9 m | 2 m | entrada, ESCs, bloco de fusíveis, cabo da fonte |
| Fio de silicone 12 AWG preto |  | 2,0 m | 2 m | retornos ao GND, cabo da fonte |
| Fio de silicone 14 AWG, 3 cores (fases) |  | 3 × 2,8 m | 3 × 3 m | X1 e X2, lado do lançador e lado da caixa |
| Fio de silicone 18 AWG vermelho e preto |  | 1 m de cada | 1 m de cada | bloco de fusíveis → bucks e placa |
| Fio de silicone 22 AWG, kit de 6 cores |  | ~8 m | 10 m | ligações dentro da caixa |
| Cabo multivias 4 × 0,3 mm² |  | 2,6 m | 3 m | lado do lançador de X3, X5, X6 |
| Cabo multivias 8 × 0,3 mm² |  | 1,5 m | 2 m | lado da caixa de X3, X5, X6 |
| Cabo multivias 8 × 0,5 mm² |  | 1,4 m | 2 m | X4 (cabeça), os dois lados |
| Termorretrátil (kit), etiquetas, abraçadeiras, malha |  | 1 | 1 | acabamento |

## Consumíveis

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Filamento PETG |  | ≈ 1,4 kg | 2 kg | peças impressas · inclui sobras e erros |
| Filamento TPU 95A |  | ≈ 0,18 kg | 0,5 kg | bandas das rodas |
| Trava-rosca média (azul) |  | 1 | 1 | parafusos de motor e polias |
| Graxa de lítio |  | 1 | 1 | fusos Tr8 |
| Cola PU e epóxi 5 min |  | 1 | 1 | bandas, ímãs, Hall |
| Solda, fluxo e malha dessoldadora |  | 1 | 1 | placa e conectores |

## Ferramentas

| Item | Especificação | Usa | Comprar | Onde vai |
| --- | --- | --- | --- | --- |
| Macho M5 + desandador |  | 1 | 1 | pontas dos postes |
| Macho M4 |  | 1 | 1 | ponta do semi-eixo |
| Brocas 3,2 / 4,5 mm |  | 1 | 1 | horn do servo, cantoneiras |
| Ferro de solda com ponta para inserto |  | 1 | 1 | insertos e placa |
| Alicate de crimpar (olhal, ponteira, JST-XH) |  | 1 | 1 | chicotes |
| Multímetro |  | 1 | 1 | testes |
| Tacômetro óptico |  | 1 | 1 | conferir o Hall · opcional |

## Fabricar

Peças feitas a partir dos arquivos desta branch (não entram na compra, mas estão aqui para a conta fechar).

| Item | Material | Qtd | Como |
| --- | --- | --- | --- |
| Chapa chapa_base_lancador (4 mm) | Alumínio 5052 ou 6061 | 1 | corte a laser · DXF em 2-cortar |
| Chapa plataforma (4 mm) | Alumínio 5052 ou 6061 | 1 | corte a laser · DXF em 2-cortar |
| Chapa placa_lateral (6 mm) | Alumínio 6061 | 2 | corte a laser · DXF em 2-cortar |
| Chapa garfo (6 mm) | Alumínio 6061 | 2 | corte a laser · DXF em 2-cortar |
| Chapa manivela_tilt (6 mm) | Alumínio 6061 | 1 | corte a laser · DXF em 2-cortar |
| Chapa disco_inercia (3 mm) | Aço 1020 | 4 | corte a laser · DXF em 2-cortar |
| Eixo eixo_roda (134 mm) | Ø12 h6 retificado (eixo linear), aço 1045 | 2 | usinagem · STEP em 3-usinar |
| Eixo semi_eixo (50 mm (+x) e 65 mm (−x)) | Ø8 retificado (eixo linear) | 2 | usinagem · STEP em 3-usinar |
| Peça impressa nucleo_roda | PETG (ou ASA / PA-CF) | 2 | impressão 3D · STL em 1-imprimir |
| Peça impressa banda_roda | TPU 95A | 2 | impressão 3D · STL em 1-imprimir |
| Peça impressa disco_sinal | PETG | 2 | impressão 3D · STL em 1-imprimir |
| Peça impressa berco | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa braco_empurrador | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa funil_cabeca | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa carenagem_roda_sup | PETG ou ASA | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa carenagem_roda_inf | PETG ou ASA | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa tampa_correia_sup | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa tampa_correia_inf | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa suporte_motor_tilt | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa suporte_motor_giro | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa mancal_fuso_giro | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa bloco_porca_tilt | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa bloco_porca_giro | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa suporte_servo | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa suporte_trilho | PETG | 1 | impressão 3D · STL em 1-imprimir |
| Peça impressa suporte_hall | PETG | 2 | impressão 3D · STL em 1-imprimir |
| Peça impressa calibre_vao_56mm | PETG | 1 | impressão 3D · STL em 1-imprimir |
