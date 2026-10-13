# Simulação no Wokwi

O Tinkercad não tem ESP32; o [Wokwi](https://wokwi.com) tem o ESP32-S3 e roda o mesmo programa do MVP no navegador, de graça.

## Abrir

1. Entre em https://wokwi.com/projects/new/esp32-s3 (não precisa de conta para testar).
2. Na aba `sketch.ino`, apague o que tiver e cole o `sketch.ino` desta pasta.
3. Na aba `diagram.json`, cole o `diagram.json` desta pasta.
4. Crie o arquivo `libraries.txt` (botão **+** ao lado das abas, ou *Library Manager*) e cole o conteúdo do daqui.
5. Clique em ▶. No monitor serial, digite `ajuda`.

## O que cada peça representa

| No simulador | Na máquina | Como usar |
| --- | --- | --- |
| Servos `escA` e `escB` (ponteiro vermelho) | ESCs das rodas de cima e de baixo | o ponteiro mostra o acelerador: ~45° parado, ~135° no máximo |
| Servo `empurrador` (ponteiro azul) | servo do empurrador | `servo 120`, `disparo` |
| `drvGiro` e `drvTilt` (A4988) | TMC2209 do giro e do tilt | no simulador não há UART; o passo de 1/8 vem do MS1 e MS2 no 3V3 |
| Motores `giro` e `tilt` | NEMA17 com fuso | a seta mostra o ângulo do fuso |
| Módulo de relé + LED `+MOT` | K1 e a barra +MOT | o LED acende com `armar` e apaga com a emergência |
| Botão vermelho | emergência (contato NA, GPIO41) | segure para simular o cogumelo apertado |
| Chave deslizante | microchave do giro (NF, GPIO13) | à esquerda = livre; à direita = acionada |

## Roteiro de teste

1. `estado`: tudo parado, microchave em 0.
2. `prende`, depois `ref`: o motor do giro começa a andar; passe a chave deslizante para a direita. O giro se referencia e volta ao centro. Volte a chave para a esquerda.
3. `giro 10`, `giro -10`, `tilt 30`, `tilt 0`.
4. `armar`: o LED acende. `tiro 60 1500`: os dois ponteiros dos ESCs sobem devagar (rampa de 400 rpm/s), o de cima mais que o de baixo.
5. `disparo` quando `estado` mostrar `pronto 1` (2 s depois de chegar na rotação, com a malha aberta).
6. Aperte o botão vermelho: o LED apaga, os ponteiros voltam e os motores de passo param.

## Limites da simulação

- A emergência de verdade também corta a bobina do K1 por hardware (contato NF), sem depender do programa. O simulador só mostra o lado do programa.
- Os sensores Hall não estão no simulador: use `malha 0`.
- Os TMC2209 só existem na placa real (é o que o `#define SIMULACAO` troca).
