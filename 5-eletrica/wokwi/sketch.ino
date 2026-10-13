// Lançador de bolas · MVP de bancada
// ESP32-S3-DevKitC-1U · 2 ESCs (rodas) · 2 TMC2209 (giro e inclinação) · servo do empurrador · K1 + emergência
//
// Comandos pelo monitor serial (115200, fim de linha "Nova linha"). Digite "ajuda".
// Pinos iguais aos da máquina completa: nada muda quando o resto for acrescentado.
//
// Na simulação do Wokwi, deixe a linha abaixo ativa: ela troca os TMC2209 (UART) por A4988 (só STEP/DIR).
#define SIMULACAO   // ativo só nesta cópia do Wokwi

#include <Arduino.h>
#include <ESP32Servo.h>
#include <AccelStepper.h>
#ifndef SIMULACAO
#include <TMCStepper.h>
#endif

// ---------------------------------------------------------------- pinos
const int P_ESC_A = 4, P_ESC_B = 5;          // roda de cima, roda de baixo
const int P_HALL_A = 6, P_HALL_B = 7;
const int P_EN = 10;                         // EN dos drivers: 0 = motores com corrente
const int P_TMC_TX = 11, P_TMC_RX = 47;      // UART de 1 fio dos TMC2209 (TX por 1 kΩ)
const int P_SERVO = 12;
const int P_FIM_GIRO = 13;                   // microchave NF ao GND: 1 = acionada (ou fio solto)
const int P_STEP_GIRO = 15, P_DIR_GIRO = 16;
const int P_STEP_TILT = 17, P_DIR_TILT = 18;
const int P_EMERG = 41;                      // contato NA do cogumelo ao GND: 0 = apertado
const int P_K1 = 42;                         // 1 = relé fechado (ESCs alimentados)

// ---------------------------------------------------------------- máquina (iguais ao CAD)
const float PAN_BRACO = 102.0;               // mm, pino do giro até o eixo
const float PAN_MAX = 12.5, TILT_MIN = 0.0, TILT_MAX = 30.0;
const float MAN_U = -16.564, MAN_V = -61.819; // ponta da manivela com a cabeça a 0° (mm)
const float PASSO_GIRO = 8.0, PASSO_TILT = 2.0;   // mm por volta do fuso
const int MICRO = 8;                         // micropassos (TMC2209 por UART)
const float PASSOS_VOLTA = 200.0 * MICRO;
const float PAN_REF_GRAUS = -13.0;           // ângulo em que a microchave aciona (calibre)
const int DIR_GIRO = 1, DIR_TILT = 1;        // troque para -1 se o eixo andar ao contrário

// rodas (memorial, seção 3.1)
const float ETA = 0.90, K_SPIN = 1.0, VAO = 0.056, D_RODA = 0.150;
const float KV = 450.0, V_FONTE = 24.0;      // ajuste ao seu motor e à sua fonte
const float RPM_CHEIO = KV * V_FONTE * 0.85; // RPM aproximada com acelerador a 100%
const float RPM_LIMITE = 5500.0;

// ---------------------------------------------------------------- estado
Servo escA, escB, empurrador;
AccelStepper giro(AccelStepper::DRIVER, P_STEP_GIRO, P_DIR_GIRO);
AccelStepper tilt(AccelStepper::DRIVER, P_STEP_TILT, P_DIR_TILT);
#ifndef SIMULACAO
HardwareSerial &TMC_UART = Serial1;
TMC2209Stepper drvGiro(&Serial1, 0.11f, 0b00);  // endereço 0 (MS1=0, MS2=0)
TMC2209Stepper drvTilt(&Serial1, 0.11f, 0b01);  // endereço 1 (MS1=1, MS2=0)
#endif

float rampa = 400.0;                         // rpm/s; devagar, para a fonte de bancada
float alvoA = 0, alvoB = 0, rpmCmdA = 0, rpmCmdB = 0;
bool malhaFechada = false;
float integA = 0, integB = 0;
bool armado = false, emergencia = false, giroReferenciado = false;
unsigned long armadoEm = 0, prontoDesde = 0;
const int SERVO_REPOUSO = 90, SERVO_EMPURRA = 120;  // graus; calibre com "servo <graus>"

volatile unsigned long periodoA = 0, periodoB = 0, ultimoA = 0, ultimoB = 0;

void IRAM_ATTR isrHallA() { unsigned long t = micros(); periodoA = t - ultimoA; ultimoA = t; }
void IRAM_ATTR isrHallB() { unsigned long t = micros(); periodoB = t - ultimoB; ultimoB = t; }

float rpmMedida(volatile unsigned long &periodo, volatile unsigned long &ultimo) {
  noInterrupts(); unsigned long p = periodo, u = ultimo; interrupts();
  if (p == 0 || micros() - u > 500000UL) return 0;   // parada
  return 60.0e6f / (p * 2.0f);                        // 2 ímãs por volta
}

// ---------------------------------------------------------------- conversões
long passosGiro(float graus) {
  return lround(DIR_GIRO * PAN_BRACO * sin(radians(graus)) / PASSO_GIRO * PASSOS_VOLTA);
}
float uManivela(float graus) { float t = radians(graus); return MAN_U * cos(t) - MAN_V * sin(t); }
long passosTilt(float graus) {
  return lround(DIR_TILT * (uManivela(graus) - uManivela(0)) / PASSO_TILT * PASSOS_VOLTA);
}
void rpmsDoTiro(float kmh, float spin, float &cima, float &baixo) {
  float v = kmh / 3.6, w = spin * 2 * PI / 60.0, m = v / ETA, d = w * VAO / (2 * K_SPIN);
  cima = 60.0 * (m + d) / (PI * D_RODA);
  baixo = 60.0 * (m - d) / (PI * D_RODA);
}
int usDoRpm(float rpm) { return constrain(1000 + (int)(1000.0 * rpm / RPM_CHEIO), 1000, 2000); }

// ---------------------------------------------------------------- segurança
void desarmar(const char *motivo) {
  alvoA = alvoB = rpmCmdA = rpmCmdB = 0;
  escA.writeMicroseconds(1000); escB.writeMicroseconds(1000);
  digitalWrite(P_K1, LOW); armado = false;
  empurrador.write(SERVO_REPOUSO);
  if (motivo) { Serial.print("desarmado: "); Serial.println(motivo); }
}
void checarEmergencia() {
  bool apertado = digitalRead(P_EMERG) == LOW;
  if (apertado && !emergencia) {
    emergencia = true;
    desarmar("EMERGÊNCIA apertada");
    digitalWrite(P_EN, HIGH);                 // motores de passo sem corrente
    giro.stop(); tilt.stop();
  } else if (!apertado && emergencia) {
    emergencia = false;
    Serial.println("emergência solta: use 'prende' e 'armar' para continuar");
  }
}

// ---------------------------------------------------------------- rodas
unsigned long ultimoCiclo = 0;
void atualizarRodas() {
  unsigned long agora = millis();
  if (agora - ultimoCiclo < 20) return;
  float dt = (agora - ultimoCiclo) / 1000.0; ultimoCiclo = agora;
  if (!armado || agora - armadoEm < 3000) {    // ESC precisa de 3 s em 1.000 µs para armar
    escA.writeMicroseconds(1000); escB.writeMicroseconds(1000); return;
  }
  float passo = rampa * dt;
  rpmCmdA += constrain(alvoA - rpmCmdA, -passo, passo);
  rpmCmdB += constrain(alvoB - rpmCmdB, -passo, passo);
  float usA = usDoRpm(rpmCmdA), usB = usDoRpm(rpmCmdB);
  if (malhaFechada) {                         // PI simples sobre a leitura Hall
    float eA = rpmCmdA - rpmMedida(periodoA, ultimoA), eB = rpmCmdB - rpmMedida(periodoB, ultimoB);
    integA = constrain(integA + eA * dt, -2000, 2000); integB = constrain(integB + eB * dt, -2000, 2000);
    usA += (0.02 * eA + 0.01 * integA) * 1000.0 / RPM_CHEIO * 10;
    usB += (0.02 * eB + 0.01 * integB) * 1000.0 / RPM_CHEIO * 10;
  }
  escA.writeMicroseconds(constrain((int)usA, 1000, 2000));
  escB.writeMicroseconds(constrain((int)usB, 1000, 2000));
}
bool rodasProntas() {
  if (!armado || alvoA <= 0) return false;
  bool rampaOk = fabs(rpmCmdA - alvoA) < 1 && fabs(rpmCmdB - alvoB) < 1;
  bool hallOk = true;
  if (malhaFechada) {
    hallOk = fabs(rpmMedida(periodoA, ultimoA) - alvoA) < 0.02 * alvoA &&
             fabs(rpmMedida(periodoB, ultimoB) - alvoB) < 0.02 * max(alvoB, 1.0f);
  }
  if (!(rampaOk && hallOk)) { prontoDesde = 0; return false; }
  if (prontoDesde == 0) prontoDesde = millis();
  return millis() - prontoDesde > (malhaFechada ? 300 : 2000);
}

// ---------------------------------------------------------------- giro e inclinação
void irGiro(float graus) {
  if (!giroReferenciado) { Serial.println("faça 'ref' antes de mover o giro"); return; }
  graus = constrain(graus, -PAN_MAX, PAN_MAX);
  giro.moveTo(passosGiro(graus));
  Serial.print("giro → "); Serial.println(graus, 1);
}
void irTilt(float graus) {
  graus = constrain(graus, TILT_MIN, TILT_MAX);
  tilt.moveTo(passosTilt(graus));
  Serial.print("inclinação → "); Serial.println(graus, 1);
}
void referenciarGiro() {
  if (emergencia) return;
  Serial.println("referência do giro: indo até a microchave...");
  digitalWrite(P_EN, LOW);
  giro.setMaxSpeed(800);
  giro.move(-DIR_GIRO * passosGiro(30));       // no máximo um curso inteiro
  unsigned long t0 = millis();
  while (digitalRead(P_FIM_GIRO) == LOW && giro.distanceToGo() != 0 && millis() - t0 < 20000) {
    giro.run(); checarEmergencia(); if (emergencia) return;
  }
  if (digitalRead(P_FIM_GIRO) == LOW) { Serial.println("microchave não acionou: confira a ligação"); giro.stop(); return; }
  giro.setCurrentPosition(passosGiro(PAN_REF_GRAUS));
  giro.setMaxSpeed(4000);
  giroReferenciado = true;
  giro.moveTo(0);
  Serial.println("giro referenciado, voltando ao centro");
}

// ---------------------------------------------------------------- disparo
void disparar() {
  if (emergencia) { Serial.println("emergência apertada"); return; }
  if (!rodasProntas()) { Serial.println("rodas ainda não estão na rotação pedida"); return; }
  if (giro.distanceToGo() != 0 || tilt.distanceToGo() != 0) { Serial.println("giro/inclinação ainda andando"); return; }
  empurrador.write(SERVO_EMPURRA);
  unsigned long t0 = millis();
  while (millis() - t0 < 200) { atualizarRodas(); checarEmergencia(); }
  empurrador.write(SERVO_REPOUSO);
  Serial.println("disparo!");
}

// ---------------------------------------------------------------- drivers
void configurarDrivers() {
#ifndef SIMULACAO
  TMC_UART.begin(115200, SERIAL_8N1, P_TMC_RX, P_TMC_TX);
  TMC2209Stepper *d[2] = {&drvGiro, &drvTilt};
  const char *nome[2] = {"giro", "tilt"};
  for (int i = 0; i < 2; i++) {
    d[i]->begin();
    d[i]->toff(4);
    d[i]->rms_current(800);                   // mA RMS
    d[i]->microsteps(MICRO);
    d[i]->pwm_autoscale(true);
    d[i]->en_spreadCycle(false);              // StealthChop: silencioso
    uint8_t r = d[i]->test_connection();
    Serial.print("TMC2209 "); Serial.print(nome[i]); Serial.println(r == 0 ? ": ok" : ": SEM RESPOSTA (confira UART e endereço)");
  }
#endif
}

// ---------------------------------------------------------------- comandos
void ajuda() {
  Serial.println(F(
    "comandos:\n"
    "  estado                 mostra tudo\n"
    "  armar / desarmar       fecha / abre o relé K1 (alimenta os ESCs)\n"
    "  tiro <km/h> <spin>     ex.: tiro 60 0  ·  tiro 80 1500 (topspin)  ·  tiro 70 -1500 (slice)\n"
    "  rodas <rpm> <rpm>      rotação da roda de cima e de baixo\n"
    "  parar                  rodas a zero (sem freio: elas param sozinhas)\n"
    "  ref                    referência do giro na microchave\n"
    "  giro <graus>           -12.5 a 12.5\n"
    "  tilt <graus>           0 a 30\n"
    "  solta / prende         tira / põe corrente nos motores de passo\n"
    "  zero                   a inclinação atual passa a ser 0° (ponha a cabeça a 0° com 'solta')\n"
    "  disparo                empurra a bola (só com as rodas prontas)\n"
    "  servo <graus>          posiciona o empurrador (para calibrar)\n"
    "  rampa <rpm/s>          aceleração das rodas (padrão 400)\n"
    "  malha <0|1>            controle de RPM pelo sensor Hall"));
}
void estado() {
  Serial.printf("armado %d · emergência %d · rodas alvo %.0f/%.0f cmd %.0f/%.0f medido %.0f/%.0f rpm · pronto %d\n",
                armado, emergencia, alvoA, alvoB, rpmCmdA, rpmCmdB, rpmMedida(periodoA, ultimoA), rpmMedida(periodoB, ultimoB), rodasProntas());
  Serial.printf("giro %ld/%ld passos (ref %d) · tilt %ld/%ld passos · microchave %d\n", giro.currentPosition(), giro.targetPosition(),
                giroReferenciado, tilt.currentPosition(), tilt.targetPosition(), digitalRead(P_FIM_GIRO));
}
void definirRodas(float a, float b) {
  if (!armado) { Serial.println("use 'armar' primeiro"); return; }
  if (a > RPM_LIMITE || b > RPM_LIMITE || a < 0 || b < 0) { Serial.println("fora do limite (0 a 5500 rpm)"); return; }
  alvoA = a; alvoB = b; prontoDesde = 0;
  Serial.printf("rodas → cima %.0f rpm, baixo %.0f rpm\n", a, b);
}
void comando(String l) {
  l.trim(); l.toLowerCase();
  if (!l.length()) return;
  int sp = l.indexOf(' ');
  String c = sp < 0 ? l : l.substring(0, sp), r = sp < 0 ? "" : l.substring(sp + 1);
  r.trim();
  float a = r.toFloat(); int sp2 = r.indexOf(' '); float b = sp2 < 0 ? 0 : r.substring(sp2 + 1).toFloat();
  if (c == "ajuda") ajuda();
  else if (c == "estado") estado();
  else if (c == "armar") {
    if (emergencia) { Serial.println("solte a emergência primeiro"); return; }
    digitalWrite(P_K1, HIGH); armado = true; armadoEm = millis(); Serial.println("K1 fechado; ESCs armando (3 s)");
  }
  else if (c == "desarmar") desarmar("pedido");
  else if (c == "tiro") { float x, y; rpmsDoTiro(a, b, x, y); definirRodas(x, y); }
  else if (c == "rodas") definirRodas(a, b);
  else if (c == "parar") { alvoA = alvoB = 0; Serial.println("rodas → 0"); }
  else if (c == "ref") referenciarGiro();
  else if (c == "giro") irGiro(a);
  else if (c == "tilt") irTilt(a);
  else if (c == "solta") { digitalWrite(P_EN, HIGH); Serial.println("motores de passo soltos"); }
  else if (c == "prende") { if (!emergencia) { digitalWrite(P_EN, LOW); Serial.println("motores de passo com corrente"); } }
  else if (c == "zero") { tilt.setCurrentPosition(0); Serial.println("inclinação atual = 0°"); }
  else if (c == "disparo") disparar();
  else if (c == "servo") { empurrador.write(constrain((int)a, 0, 180)); Serial.printf("servo → %d°\n", (int)a); }
  else if (c == "rampa") { rampa = constrain(a, 50, 3000); Serial.printf("rampa %.0f rpm/s\n", rampa); }
  else if (c == "malha") { malhaFechada = a > 0; integA = integB = 0; Serial.printf("malha %s\n", malhaFechada ? "fechada (Hall)" : "aberta"); }
  else { Serial.print("não entendi: "); Serial.println(l); }
}

// ---------------------------------------------------------------- setup / loop
void setup() {
  pinMode(P_K1, OUTPUT); digitalWrite(P_K1, LOW);
  pinMode(P_EN, OUTPUT); digitalWrite(P_EN, HIGH);      // drivers soltos até o primeiro 'prende'
  pinMode(P_EMERG, INPUT_PULLUP);
  pinMode(P_FIM_GIRO, INPUT_PULLUP);
  pinMode(P_HALL_A, INPUT_PULLUP); pinMode(P_HALL_B, INPUT_PULLUP);
  Serial.begin(115200);
  delay(300);
  escA.setPeriodHertz(50); escB.setPeriodHertz(50); empurrador.setPeriodHertz(50);
  escA.attach(P_ESC_A, 1000, 2000); escB.attach(P_ESC_B, 1000, 2000); empurrador.attach(P_SERVO, 500, 2500);
  escA.writeMicroseconds(1000); escB.writeMicroseconds(1000); empurrador.write(SERVO_REPOUSO);
  attachInterrupt(digitalPinToInterrupt(P_HALL_A), isrHallA, FALLING);
  attachInterrupt(digitalPinToInterrupt(P_HALL_B), isrHallB, FALLING);
  configurarDrivers();
  giro.setMaxSpeed(4000); giro.setAcceleration(8000);
  tilt.setMaxSpeed(8000); tilt.setAcceleration(12000);
  Serial.println("Lançador MVP pronto. Digite 'ajuda'.");
  checarEmergencia();
}

String linha;
void loop() {
  checarEmergencia();
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n' || ch == '\r') { comando(linha); linha = ""; }
    else if (linha.length() < 80) linha += ch;
  }
  if (!emergencia) { giro.run(); tilt.run(); }
  atualizarRodas();
}
