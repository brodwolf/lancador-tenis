# Firmware do MVP

`mvp_bancada/mvp_bancada.ino`: comanda as rodas, o giro, a inclinação e o empurrador pelo monitor serial. Os pinos são os da máquina completa.

## Preparar a Arduino IDE

1. Instale o pacote **esp32** da Espressif (versão 3.x) no Gerenciador de Placas.
2. Instale as bibliotecas **ESP32Servo** (Kevin Harrington, 3.x), **AccelStepper** (Mike McCauley) e **TMCStepper** (teemuatlut).
3. Placa: **ESP32S3 Dev Module** · Flash Size **8MB** · PSRAM **OPI PSRAM**.
4. Use a porta USB-C marcada **UART** da DevKitC. Se usar a marcada **USB**, ative *USB CDC On Boot*.
5. Monitor serial em **115200**, fim de linha **Nova linha**. Digite `ajuda`.

## Comandos

| Comando | O que faz |
| --- | --- |
| `ajuda` | lista os comandos |
| `estado` | mostra rodas, giro, inclinação, microchave e emergência |
| `armar / desarmar` | fecha / abre o K1; os ESCs armam em 3 s |
| `tiro <km/h> <spin>` | calcula a RPM das duas rodas (ex.: tiro 60 0 · tiro 80 1500 · tiro 70 -1500) |
| `rodas <rpm> <rpm>` | rotação da roda de cima e de baixo, até 5.500 |
| `parar` | rodas a zero, sem freio: param sozinhas |
| `ref` | procura a microchave e zera o giro |
| `giro <graus>` | −12,5 a +12,5 |
| `tilt <graus>` | 0 a 30 |
| `solta / prende` | tira / põe corrente nos motores de passo |
| `zero` | a inclinação atual passa a ser 0° |
| `disparo` | empurra a bola, só com as rodas na rotação |
| `servo <graus>` | posiciona o empurrador, para calibrar |
| `rampa <rpm/s>` | aceleração das rodas (padrão 400) |
| `malha <0\|1>` | controle de RPM pelo Hall |

## Antes do primeiro tiro

- Confira `KV` e `V_FONTE` no topo do programa: são eles que convertem rpm em acelerador sem o Hall.
- Calibre o curso dos ESCs uma vez (1.000–2.000 µs) pelo procedimento do fabricante.
- `PAN_REF_GRAUS`: depois do primeiro `ref`, meça o ângulo em que a microchave aciona e ajuste.
- `DIR_GIRO` e `DIR_TILT`: troque o sinal se o eixo andar ao contrário.
- `SERVO_REPOUSO` e `SERVO_EMPURRA`: ache com `servo <graus>` o ponto em que o braço fica atrás da bola e o ponto em que ela entra nas rodas.
- Comece com `malha 0`. Depois de conferir o Hall com o tacômetro, `malha 1`.

## Segurança

- O botão de emergência corta a bobina do K1 por hardware (contato NF) e avisa o ESP32 (contato NA, GPIO41): os ESCs perdem a alimentação mesmo se o programa travar.
- No boot o K1 fica aberto e os motores de passo, soltos. `armar` fecha o K1; os ESCs levam 3 s para armar.
- `parar` deixa as rodas pararem sozinhas, sem freio (ver `5-eletrica`).

## Simulação

A cópia em `5-eletrica/wokwi/sketch.ino` tem `#define SIMULACAO` ativo: troca os TMC2209 (UART) por A4988 (só STEP/DIR) no simulador. Não grave essa cópia na placa de verdade.
