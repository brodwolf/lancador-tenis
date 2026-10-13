"""Desenhos SVG da elétrica do MVP: potência, sinais, placa de controle e bancada.

Os desenhos usam classes CSS. A página HTML define as cores por tema; os arquivos .svg avulsos
levam um <style> próprio com cores fixas (para abrir no GitHub ou no navegador).
"""
import html

E = html.escape


# ----------------------------------------------------------------------------- helpers
def t(x, y, s, cls="lb", anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" {extra}>{E(s)}</text>'


def box(x, y, w, h, titulo, linhas=(), cls="bx", tcls="bt", r=4):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'
    o += t(x + 8, y + 17, titulo, tcls)
    for i, l in enumerate(linhas):
        o += t(x + 8, y + 33 + 14 * i, l, "sm")
    return o


def ln(pts, cls):
    return '<polyline points="' + " ".join(f"{a},{b}" for a, b in pts) + f'" class="{cls}"/>'


def fus(x, y, rot):
    o = f'<rect x="{x}" y="{y-7}" width="36" height="14" rx="7" class="fz"/>'
    o += f'<line x1="{x+6}" y1="{y}" x2="{x+30}" y2="{y}" class="fzl"/>'
    return o + t(x + 18, y - 11, rot, "val", "middle")


def dot(x, y, cls="nd"):
    return f'<circle cx="{x}" cy="{y}" r="4" class="{cls}"/>'


def gauge(x, y, s, anchor="middle"):
    return t(x, y, s, "awg", anchor)


def svg_open(W, H, label):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}">',
            f'<rect x="0" y="0" width="{W}" height="{H}" class="fundo"/>']


# ----------------------------------------------------------------------------- 1. potência
def svg_potencia():
    W, H = 1190, 660
    o = svg_open(W, H, "Potência do MVP: fonte de bancada, fusível, diodo ideal, barramentos, relé K1, ESCs, bloco de fusíveis e conversores")
    GND_Y = 610
    o.append(f'<rect x="20" y="{GND_Y-7}" width="1160" height="14" rx="3" class="bar-gnd"/>')
    o.append(t(28, GND_Y + 32, "BARRA GND · latão, 6 bornes M5 · ponto único de terra: todos os retornos (−) chegam aqui", "bart"))
    # fonte, XT60, fusível, diodo
    o.append(box(20, 66, 140, 100, "Fonte de bancada", ["19–24 V · ≥ 5 A", "comece com limite", "de 0,5 A"], "bx bat"))
    o.append(t(150, 101, "+", "pm", "end")); o.append(t(150, 151, "−", "pm", "end"))
    o.append(ln([(160, 96), (200, 96)], "w-bat"))
    o.append(ln([(160, 146), (200, 146)], "w-gnd"))
    o.append(gauge(180, 88, "12 AWG"))
    o.append(t(20, 186, "cabo de 1,0 m: bananas 4 mm → XT60 macho", "sm"))
    o.append(f'<rect x="200" y="78" width="34" height="86" rx="4" class="bx soft"/>')
    o.append(t(217, 70, "XT60", "val", "middle"))
    o.append(ln([(234, 96), (260, 96)], "w-bat"))
    o.append(fus(260, 96, "30 A"))
    o.append(ln([(296, 96), (322, 96)], "w-bat"))
    o.append(box(322, 74, 112, 44, "Diodo ideal", ["≥ 30 A"], "bx"))
    o.append(ln([(434, 96), (474, 96)], "w-bat"))
    o.append(gauge(454, 88, "10 AWG"))
    o.append(t(20, 212, "XT60 fêmea em rabicho 12 AWG", "sm"))
    o.append(t(20, 226, "pelo prensa-cabo; o fusível e", "sm"))
    o.append(t(20, 240, "o diodo viram os da bateria A", "sm"))
    o.append(ln([(234, 146), (252, 146), (252, GND_Y)], "w-gnd"))
    o.append(gauge(260, 300, "12 AWG", "start"))
    o.append(f'<rect x="474" y="56" width="14" height="500" rx="3" class="bar-bat"/>')
    o.append(t(481, 574, "BARRA +BAT", "bart", "middle"))
    o.append(t(481, 589, "19–24 V · 4 bornes", "sm", "middle"))
    # ramo das rodas: K1, MAXI 40 A, +MOT
    o.append(ln([(488, 112), (536, 112), (536, 128), (544, 128)], "w-bat"))
    o.append(gauge(512, 104, "10 AWG"))
    o.append(f'<rect x="530" y="80" width="104" height="104" rx="4" class="bx"/>')
    o.append(t(538, 97, "K1 · relé 12 V", "bt"))
    o.append(t(538, 111, "≥ 40 A", "sm"))
    o.append('<line x1="544" y1="128" x2="568" y2="128" class="w-bat"/><line x1="568" y1="128" x2="594" y2="117" class="w-bat"/>'
             '<line x1="598" y1="128" x2="624" y2="128" class="w-bat"/>')
    o.append(t(544, 145, "30", "pin")); o.append(t(624, 145, "87", "pin", "end"))
    o.append('<rect x="556" y="156" width="54" height="16" rx="2" class="coil"/>')
    o.append(t(583, 168, "bobina", "sm", "middle"))
    o.append(t(549, 168, "86", "pin", "end")); o.append(t(616, 168, "85", "pin"))
    o.append(ln([(624, 128), (634, 128), (634, 112), (654, 112)], "w-bat"))
    o.append(fus(654, 112, "40 A"))
    o.append(t(672, 133, "MAXI", "sm", "middle"))
    o.append(ln([(690, 112), (730, 112)], "w-mot"))
    o.append(gauge(710, 104, "10 AWG"))
    o.append(f'<rect x="730" y="74" width="14" height="200" rx="3" class="bar-mot"/>')
    o.append(t(737, 292, "BARRA +MOT", "bart", "middle"))
    o.append(t(737, 307, "3 bornes", "sm", "middle"))
    for j, (cod, nome, sub, y) in enumerate((("X1", "ESC A · 60–80 A", "roda de cima · freio OFF", 114),
                                            ("X2", "ESC B · 60–80 A", "roda de baixo · freio OFF", 220))):
        o.append(ln([(744, y), (780, y)], "w-mot"))
        o.append(gauge(762, y - 8, "12 AWG"))
        o.append(box(780, y - 24, 140, 54, nome, [sub], "bx"))
        for k in range(3):
            o.append(ln([(920, y - 10 + 10 * k), (968, y - 10 + 10 * k)], "w-ph"))
            o.append(ln([(996, y - 10 + 10 * k), (1074, y - 10 + 10 * k)], "w-ph"))
        o.append(f'<rect x="968" y="{y-20}" width="28" height="40" rx="3" class="bx soft"/>')
        o.append(t(982, y - 26, cod, "gp", "middle"))
        o.append(gauge(944, y - 16, "14 AWG"))
        o.append(t(1035, y - 16, "0,50 + 0,90 m", "awg", "middle"))
        o.append(f'<circle cx="1108" cy="{y}" r="28" class="mot"/>')
        o.append(t(1108, y + 7, "M", "mt", "middle"))
        o.append(t(1108, y + 44, "4250 · U V W", "sm", "middle"))
        yg = y + 58
        o.append(ln([(840, y + 30), (840, yg), (1172, yg)], "w-gnd"))
        o.append(dot(1172, yg, "nd g"))
    o.append(ln([(1172, 172), (1172, GND_Y)], "w-gnd"))
    o.append(t(1164, 340, "(−) dos ESCs, 12 AWG", "sm", "end"))
    o.append(t(944, 160, "MT60 na saída da caixa", "sm", "middle"))
    # bobina: +12 V → NF da emergência → 85; 86 → IRLZ44N → GND
    o.append(ln([(610, 164), (652, 164), (652, 238)], "w-12"))
    o.append('<rect x="634" y="238" width="36" height="20" rx="3" class="bx soft"/>')
    o.append(t(652, 252, "NF", "pin", "middle"))
    o.append(ln([(670, 248), (712, 248)], "w-12"))
    o.append(f'<path d="M712 240 h40 l8 8 l-8 8 h-40 z" class="flag"/>')
    o.append(t(734, 252, "+12 V", "val", "middle"))
    o.append(t(652, 276, "emergência", "sm", "middle"))
    o.append(t(652, 290, "X5 · 1–2", "sm", "middle"))
    o.append(ln([(556, 164), (556, 238)], "w-sig"))
    o.append(box(510, 238, 98, 42, "IRLZ44N", ["gate ← GPIO42"], "bx soft"))
    o.append(ln([(558, 280), (558, 298)], "w-gnd"))
    o.append(t(566, 300, "GND", "sm"))
    o.append(t(506, 322, "1N4007 em paralelo com a bobina", "sm"))
    o.append(t(506, 336, "(catodo no 85); fica na placa", "sm"))
    # ramo da lógica: bloco de fusíveis e conversores
    o.append(ln([(488, 424), (520, 424)], "w-bat"))
    o.append(gauge(504, 416, "12 AWG"))
    o.append(box(520, 364, 124, 196, "Bloco de fusíveis", ["6 vias + barra (−)"], "bx"))
    linhas = (("F1", "5 A", 424, None, None, "w-bat", "19–24 V", "VM dos 2 TMC2209"),
              ("F2", "3 A", 460, "Buck 5 V · MP1584", "w-5", "w-5", "5,1 V", "ESP32 (5V), Hall"),
              ("F3", "5 A", 496, "Buck 6 V · XL4015", "w-6", "w-6", "6,0 V", "servo"),
              ("F4", "2 A", 532, "Buck 12 V · MP1584", "w-12", "w-12", "12,0 V", "bobina do K1"))
    for f, a, y, buck, _, cls, v, uso in linhas:
        o.append(t(536, y + 4, f, "pin"))
        o.append(fus(556, y, a))
        o.append(ln([(592, y), (644, y)], "w-bat"))
        if buck:
            o.append(ln([(644, y), (690, y)], "w-bat"))
            o.append(box(690, y - 15, 156, 30, buck, [], "bx soft", "sm"))
            o.append(ln([(846, y), (900, y)], cls))
        else:
            o.append(ln([(644, y), (900, y)], cls))
        o.append(t(874, y - 6, v, "val", "middle"))
    o.append(gauge(668, 416, "18 AWG"))
    o.append(ln([(582, 560), (582, GND_Y)], "w-gnd"))
    o.append(t(590, 580, "barra (−) do bloco: GND da lógica", "sm"))
    o.append(box(900, 394, 272, 176, "Placa de controle", [
        "ESP32-S3 + 2 TMC2209 (giro e tilt)",
        "VM: 1.000 µF/35 V no borne",
        "100 µF/35 V em cada driver",
        "→ X3 motores de passo",
        "→ X4 Hall ×2, servo (5 V e 6 V)",
        "→ X5 emergência (+12 V, NF, NA)",
        "→ X6 microchave",
        "ver o esquema de sinais"], "bx mcu2"))
    o.append(t(900, 590, "ajuste os bucks sem carga, antes da placa", "sm"))
    o.append('</svg>')
    return "".join(o)


# ----------------------------------------------------------------------------- 2. sinais
ESQ = [(4, "ESC A", 96, "10 kΩ ao GND"), (5, "ESC B", 132, "10 kΩ ao GND"), (12, "SERVO", 186, "330 Ω em série"),
       (42, "K1", 240, "100 Ω · 10 kΩ ao GND"), (41, "EMERG. NA", 276, "10 kΩ ao 3V3 + 100 nF"),
       (13, "FIM giro", 330, "10 kΩ ao 3V3 + 100 nF"), (6, "HALL cima", 384, "10 kΩ ao 3V3 + 100 nF"),
       (7, "HALL baixo", 420, "10 kΩ ao 3V3 + 100 nF")]
DIR = [(10, "EN drivers", 96, "10 kΩ ao 3V3"), (11, "UART TX", 132, "1 kΩ em série"), (47, "UART RX", 168, "direto no PDN_UART"),
       (15, "STEP giro", 204, ""), (16, "DIR giro", 240, ""), (17, "STEP tilt", 276, ""), (18, "DIR tilt", 312, ""),
       (14, "DIAG tilt", 348, "opcional")]


def svg_sinais():
    W, H = 1180, 600
    X0, X1 = 476, 704
    o = svg_open(W, H, "Ligações de sinal do ESP32-S3 no MVP")
    o.append(f'<rect x="{X0}" y="40" width="{X1-X0}" height="520" rx="8" class="mcu"/>')
    o.append(t((X0 + X1) / 2, 66, "ESP32-S3-DevKitC-1U", "bt", "middle"))
    o.append(t((X0 + X1) / 2, 82, "N8R8 · antena externa U.FL", "sm", "middle"))
    for g, n, y, v in ESQ:
        o.append(ln([(232, y), (X0, y)], "w-sig"))
        o.append(t(X0 + 8, y + 4, n, "pinl"))
        o.append(t(X0 - 6, y - 5, f"{g}", "gp", "end"))
        if v:
            o.append(t(240, y - 5, v, "sm"))
    for g, n, y, v in DIR:
        o.append(ln([(X1, y), (900, y)], "w-sig"))
        o.append(t(X1 - 8, y + 4, n, "pinl", "end"))
        o.append(t(X1 + 6, y - 5, f"{g}", "gp"))
        if v:
            o.append(t(892, y - 5, v, "sm", "end"))
    for k, (n, cls, txt) in enumerate((("5V", "w-5", "5,1 V do buck (F2)"), ("3V3", "w-33", "3V3 da placa → VIO dos drivers e pull-ups"),
                                       ("GND", "w-gnd", "GND comum (barra GND, ponto único)"))):
        y = 476 + 36 * k
        o.append(ln([(232, y), (X0, y)], cls))
        o.append(t(X0 + 8, y + 4, n, "pinl"))
        o.append(t(240, y - 5, txt, "sm"))
    o.append(box(20, 70, 212, 80, "ESCs A e B", ["só sinal + GND do cabo de servo;", "fio vermelho (BEC) isolado"]))
    o.append(box(20, 166, 212, 40, "Servo empurrador · 6 V (X4)"))
    o.append(box(20, 220, 212, 76, "Relé K1 e emergência (X5)", ["GPIO42 → IRLZ44N (lado do GND)", "NA do cogumelo → GPIO41"]))
    o.append(box(20, 310, 212, 40, "Microchave do giro (X6)"))
    o.append(box(20, 364, 212, 76, "Hall A3144 a 5 V (X4)", ["saída coletor aberto:", "pull-up só para o 3V3"]))
    o.append(box(900, 70, 260, 300, "2× TMC2209 · UART de 1 fio", [
        "PDN_UART dos dois ligados juntos",
        "TX do ESP32 entra por 1 kΩ; RX direto",
        "EN comum, ativo em 0: com o pull-up,",
        "  os motores ficam soltos no boot",
        "endereço do giro: MS1=0 MS2=0",
        "endereço do tilt: MS1=1 MS2=0",
        "VIO = 3V3 · VM = 19–24 V (F1)",
        "100 µF/35 V em cada driver",
        "0,8 A RMS e 1/8 de passo por UART",
        "STEP/DIR: fio curto, < 30 cm",
        "DIAG do tilt: referência por",
        "  StallGuard (opcional)",
    ]))
    o.append(box(900, 384, 260, 76, "Saídas dos motores → X3", ["giro A1 A2 B1 B2 → pinos 1–4", "tilt A1 A2 B1 B2 → pinos 5–8"]))
    o.append(box(900, 474, 260, 86, "Livres para a máquina completa", [
        "1, 2 baterias · 3 rádio · 8 agitador", "9, 48 I²C · 21 bola · 38 semáforo", "39, 40 tela · 46 buzzer"], "bx soft"))
    o.append('</svg>')
    return "".join(o)


# ----------------------------------------------------------------------------- 3. placa perfurada (vista de cima, mm)
def svg_placa():
    S, OX, OY = 5.0, 70, 70             # px/mm, origem do canto da placa
    W, H = int(OX * 2 + 150 * S + 150), int(OY + 100 * S + 110)
    o = svg_open(W, H, "Arranjo da placa de controle em placa perfurada de 10 × 15 cm")

    def R(x, y, w, h, cls, rot="", sub="", tc="bt", rx=2):
        X, Y = OX + x * S, OY + y * S
        s = f'<rect x="{X}" y="{Y}" width="{w*S}" height="{h*S}" rx="{rx}" class="{cls}"/>'
        if rot:
            s += t(X + 6, Y + 16, rot, tc)
        if sub:
            s += t(X + 6, Y + 30, sub, "sm")
        return s

    def P(x, y):
        return (OX + x * S, OY + y * S)

    def tl(x, y, s, cls="sm", anchor="start"):
        X, Y = P(x, y)
        return t(X, Y, s, cls, anchor)

    o.append(R(0, 0, 150, 100, "pcb", rx=6))
    # malha de furos (a cada 2,54 mm, só para dar a ideia)
    pts = []
    for i in range(1, 59):
        for j in range(1, 39):
            x, y = P(i * 2.54, j * 2.54)
            pts.append(f"M{x:.1f} {y:.1f}h0.1")
    o.append(f'<path d="{" ".join(pts)}" class="furos"/>')
    # trilhas principais
    o.append(ln([P(146, 45), P(116, 45), P(116, 31), P(92, 31)], "w-bat"))      # VM até os drivers
    o.append(ln([P(116, 31), P(142, 31)], "w-bat"))
    o.append(ln([P(146, 59), P(84, 59), P(84, 56), P(74, 56)], "w-5"))          # 5 V até o ESP32
    o.append(ln([P(84, 59), P(84, 12), P(48, 12)], "w-5"))                       # 5 V até os Hall
    o.append(ln([P(146, 73), P(80, 73), P(80, 14), P(27, 14)], "w-6"))           # 6 V até o servo
    o.append(ln([P(146, 87), P(114, 87), P(114, 8.5), P(74, 8.5)], "w-12"))     # 12 V até a emergência (X5)
    o.append(ln([P(4, 96), P(146, 96)], "w-gnd"))                                # GND ao longo da borda
    for x in (100, 126):
        o.append(ln([P(x, 30), P(x, 34)], "w-33"))
    # ESP32
    o.append(R(6, 58, 64, 26, "mod"))
    o.append(tl(9, 67, "ESP32-S3-DevKitC-1U", "bt"))
    o.append(tl(9, 71.5, "em barras de pinos fêmea", "sm"))
    for k in range(22):
        for yy in (59.3, 82.7):
            X, Y = P(10 + k * 2.54, yy)
            o.append(f'<circle cx="{X}" cy="{Y}" r="2.2" class="pino"/>')
    o.append(R(-6, 66, 10, 9, "usb"))
    o.append(tl(-7, 90, "USB-C → computador", "sm"))
    o.append(R(68, 68, 6, 6, "ufl"))
    o.append(tl(70, 89.5, "U.FL → antena", "sm", "end"))
    # drivers
    for k, (x, nome, end) in enumerate(((92, "TMC2209 giro", "MS1=0 MS2=0"), (118, "TMC2209 tilt", "MS1=1 MS2=0"))):
        o.append(R(x, 10, 16, 21, "mod drv"))
        o.append(tl(x + 8, 18, nome.split()[0], "awg", "middle"))
        o.append(tl(x + 8, 22, nome.split()[1], "bt", "middle"))
        o.append(tl(x + 8, 39.5, end, "awg", "middle"))
        o.append(R(x + 1, 2.5, 14, 4, "jst"))
        o.append(f'<circle cx="{P(x + 13, 33.5)[0]}" cy="{P(x + 13, 33.5)[1]}" r="{3.2*S/2}" class="cap"/>')
    o.append(tl(100, 45, "100 µF em cada VM", "sm", "middle"))
    o.append(tl(113, -3, "X3: motores (JST-XH 4 vias)", "sm", "middle"))
    # bornes de potência
    for k, (y, nome, cls) in enumerate(((42, "VM 19–24 V (F1)", "w-bat"), (56, "5,1 V (F2)", "w-5"),
                                        (70, "6,0 V (F3)", "w-6"), (84, "12 V (F4)", "w-12"))):
        o.append(R(140, y, 9, 7, "kf"))
        o.append(tl(152, y + 4.6, nome, "sm"))
    o.append(tl(152, 38, "bornes KF301 (+ e GND)", "awg"))
    o.append(f'<circle cx="{P(128, 48)[0]}" cy="{P(128, 48)[1]}" r="{10*S/2}" class="cap"/>')
    o.append(tl(128, 49.6, "1000 µF", "awg", "middle"))
    # K1: MOSFET, diodo, borne
    o.append(R(84, 77, 10, 14, "mos"))
    o.append(tl(82, 85, "IRLZ44N", "sm", "end"))
    o.append(R(96, 82, 8, 3, "dio"))
    o.append(tl(100, 80.5, "1N4007", "awg", "middle"))
    o.append(R(102, 86, 9, 7, "kf"))
    o.append(tl(106.5, 81, "K1", "sm", "middle"))
    # conectores de sinal na borda de cima
    jst = [(3, 2, "ESC A"), (13, 2, "ESC B"), (23, 3, "SERVO"), (35, 3, "HALL A"), (47, 3, "HALL B"),
           (59, 2, "FIM"), (67, 4, "X5")]
    for x, n, nome in jst:
        o.append(R(x, 2.5, n * 2.5 + 1, 4, "jst"))
        o.append(tl(x + (n * 2.5 + 1) / 2, -1.5, nome, "awg", "middle"))
    o.append(tl(40, -6, "sinais (JST-XH) · HALL A = roda de cima · X5 = emergência", "sm", "middle"))
    # zona dos passivos
    o.append(R(6, 17, 70, 38, "zona"))
    o.append(tl(9, 23, "pull-ups, pull-downs e filtros, junto de cada pino:", "sm"))
    o.append(tl(9, 27, "10 kΩ ×8 · 1 kΩ (UART) · 330 Ω (servo) · 100 Ω (gate)", "sm"))
    o.append(tl(9, 31, "100 nF ×4 nas entradas, ×4 de desacoplamento", "sm"))
    for k in range(8):
        X, Y = P(10 + k * 8, 38)
        o.append(f'<rect x="{X}" y="{Y}" width="{6*S}" height="{1.8*S}" rx="3" class="res"/>')
    for k in range(4):
        X, Y = P(12 + k * 14, 46)
        o.append(f'<rect x="{X}" y="{Y}" width="{4*S}" height="{2*S}" rx="2" class="cer"/>')
    o.append(tl(9, 52.5, "UART: 1 kΩ do GPIO11 até o PDN_UART dos dois drivers; GPIO47 direto", "awg"))
    # legenda e cotas
    yl = OY + 100 * S + 34
    o.append(t(OX, yl, "Placa perfurada ilhada 150 × 100 mm, vista de cima (componentes). Escala 5 px/mm.", "sm"))
    leg = [("w-bat", "VM 19–24 V"), ("w-5", "5,1 V"), ("w-6", "6,0 V"), ("w-12", "12 V"), ("w-33", "3V3"), ("w-gnd", "GND")]
    for k, (cls, nome) in enumerate(leg):
        x = OX + k * 120
        o.append(ln([(x, yl + 22), (x + 28, yl + 22)], cls))
        o.append(t(x + 36, yl + 26, nome, "sm"))
    o.append(t(OX, yl + 52, "Fios de alimentação por baixo (trilha de fio 18–22 AWG); os de sinal, 22 AWG, por cima.", "sm"))
    o.append('</svg>')
    return "".join(o)


# ----------------------------------------------------------------------------- 4. bancada (vista de cima)
def svg_bancada():
    S = 0.62                     # px por mm
    OX, OY = 40, 40
    W, H = 1200, 600
    o = svg_open(W, H, "Arranjo da bancada vista de cima: lançador, caixa da eletrônica, fonte, emergência e cabos")

    def P(x, y):
        return (OX + x * S, OY + y * S)

    def R(x, y, w, h, cls, rx=4):
        X, Y = P(x, y)
        return f'<rect x="{X:.1f}" y="{Y:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" rx="{rx}" class="{cls}"/>'

    def T(x, y, s_, cls="sm", anchor="start", dy=0):
        X, Y = P(x, y)
        return t(round(X, 1), round(Y + dy, 1), s_, cls, anchor)

    o.append(R(0, 0, 1800, 840, "mesa", 8))
    o.append(T(1790, 22, "BANCADA · 1,8 × 0,84 m (vista de cima)", "zt", "end"))
    # lançador: chapa 312 (x) × 422 (y), frente para cima
    lx, ly = 120, 250
    o.append(R(lx - 70, 20, 452, 200, "perigo", 6))
    o.append(T(lx + 156, 110, "ninguém na frente das rodas", "aviso", "middle"))
    o.append(T(lx + 156, 110, "aponte para uma rede ou parede, ≥ 3 m livres", "sm", "middle", 16))
    o.append(R(lx, ly, 312, 422, "chapa"))
    for sx in (0, 1):
        for sy in (0, 1):
            X, Y = P(lx + 21 + sx * 270, ly + 21 + sy * 380)
            o.append(f'<rect x="{X-6:.1f}" y="{Y-6:.1f}" width="12" height="12" class="poste"/>')
    cx, cy = lx + 156, ly + 211 + 116        # eixo do giro, 116 mm atrás do centro da chapa
    X, Y = P(cx, cy)
    o.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{75*S:.1f}" class="lazy"/>')
    o.append(R(cx - 61, cy - 210, 12, 300, "placa"))
    o.append(R(cx + 49, cy - 210, 12, 300, "placa"))
    o.append(R(cx - 49, cy - 180, 98, 60, "roda"))
    o.append(T(cx, ly + 60, "↑ frente: a bola sai aqui", "lb", "middle"))
    o.append(T(lx + 156, ly + 452, "Lançador · chapa 312 × 422 mm", "bt", "middle"))
    o.append(T(lx + 156, ly + 452, "4 pernas de 112 mm, pés de borracha", "sm", "middle", 16))
    # caixa a 300 mm da chapa
    bx, by = lx + 312 + 300, ly + 150
    xm = lx + 312 + 125                         # acoplamentos na mesa
    cabos = [("X1", "w-ph"), ("X2", "w-ph"), ("X3", "w-sig"), ("X4", "w-5"), ("X5", "w-12"), ("X6", "w-sig")]
    for k, (nome, cls) in enumerate(cabos):
        ya = ly + 170 + k * 40
        yb = by + 25 + k * 30
        o.append(ln([P(lx + 300, ya), P(xm, ya)], cls + " cabo"))
        o.append(ln([P(xm + 30, ya), P(bx, yb)], cls + " cabo"))
        o.append(R(xm, ya - 9, 30, 18, "conn", 3))
        o.append(T(xm + 15, ya, nome, "gp", "middle", -9))
    o.append(T(lx + 322, ly + 430, "← lançador: 0,40–0,90 m", "sm"))
    o.append(T(xm + 60, ly + 430, "caixa: 0,50 m →", "sm", "start", 16))
    o.append(T(xm + 15, ly + 105, "conectores na mesa", "sm", "middle"))
    o.append(T(xm + 15, ly + 105, "(depois: no suporte)", "sm", "middle", 14))
    o.append(R(bx, by, 250, 200, "caixa", 6))
    o.append(T(bx + 125, by + 95, "Caixa IP65", "bt", "middle"))
    o.append(T(bx + 125, by + 95, "250 × 200 × 100 mm", "sm", "middle", 16))
    X1_, Y1_ = P(lx + 312, ly + 500)
    X2_, _ = P(bx, ly + 500)
    o.append(f'<line x1="{X1_:.1f}" y1="{Y1_:.1f}" x2="{X2_:.1f}" y2="{Y1_:.1f}" class="cota"/>')
    o.append(t(round((X1_ + X2_) / 2, 1), round(Y1_ - 6, 1), "≤ 300 mm", "val", "middle"))
    # fonte de bancada
    fx, fy = bx + 20, by - 280
    o.append(R(fx, fy, 210, 130, "fonte", 6))
    o.append(T(fx + 105, fy + 60, "Fonte de bancada", "bt", "middle"))
    o.append(T(fx + 105, fy + 60, "19–24 V · ≥ 5 A", "sm", "middle", 16))
    o.append(ln([P(fx + 105, fy + 130), P(fx + 105, by)], "w-bat cabo"))
    o.append(T(fx + 115, fy + 205, "12 AWG, 1,0 m → XT60", "sm"))
    # emergência
    ex, ey = bx + 360, by + 260
    X, Y = P(ex, ey)
    o.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="18" class="emerg"/>')
    o.append(ln([P(bx + 250, by + 170), P(ex - 25, ey - 22)], "w-12 cabo"))
    o.append(T(ex + 45, ey, "Emergência", "bt", "start", -4))
    o.append(T(ex + 45, ey, "caixa de botoeira, à mão", "sm", "start", 12))
    o.append(T(ex + 45, ey, "X5 · 4 × 0,3 mm², 0,90 m", "sm", "start", 26))
    # computador
    px, py = bx + 520, by - 10
    o.append(R(px, py, 300, 190, "pc", 6))
    o.append(T(px + 150, py + 95, "Computador", "bt", "middle"))
    o.append(T(px + 150, py + 95, "monitor serial 115.200", "sm", "middle", 16))
    o.append(ln([P(bx + 250, by + 60), P(px, by + 60)], "w-33 cabo"))
    o.append(T(bx + 385, by + 50, "USB-C, 2 m", "sm", "middle"))
    o.append('</svg>')
    return "".join(o)


# ----------------------------------------------------------------------------- estilos
CSS_SVG = """
svg text { fill: var(--ink); white-space: pre; }
svg .fundo { fill: transparent; }
svg .lb { font: 500 13px var(--f-body); } svg .sm { font: 400 11.5px var(--f-body); fill: var(--muted); }
svg .bt { font: 600 13.5px var(--f-disp); } svg .bart { font: 600 12.5px var(--f-mono); fill: var(--accent); letter-spacing: .04em; }
svg .val { font: 600 11.5px var(--f-mono); } svg .awg { font: 500 10.5px var(--f-mono); fill: var(--muted); }
svg .pin { font: 600 11px var(--f-mono); } svg .pinl { font: 500 12px var(--f-mono); } svg .gp { font: 700 11.5px var(--f-mono); fill: var(--accent); }
svg .pm { font: 700 16px var(--f-mono); } svg .mt { font: 700 20px var(--f-disp); } svg .zt { font: 700 13px var(--f-mono); letter-spacing: .1em; fill: var(--accent); }
svg .aviso { font: 600 13px var(--f-body); fill: var(--w-bat); }
svg .bx { fill: var(--paper); stroke: var(--ink); stroke-width: 1.4; }
svg .bx.soft { stroke: var(--muted); } svg .bx.bat { fill: var(--accent-soft); } svg .bx.mcu2 { fill: var(--pcb); stroke: var(--pcb-line); stroke-width: 2; }
svg .mcu { fill: var(--pcb); stroke: var(--pcb-line); stroke-width: 2; }
svg polyline, svg line { fill: none; stroke-linecap: round; stroke-linejoin: round; }
svg .w-bat { stroke: var(--w-bat); stroke-width: 4; } svg .w-mot { stroke: var(--w-mot); stroke-width: 4; } svg .w-gnd { stroke: var(--w-gnd); stroke-width: 3; }
svg .w-12 { stroke: var(--w-12); stroke-width: 2.4; } svg .w-6 { stroke: var(--w-6); stroke-width: 2.4; } svg .w-5 { stroke: var(--w-5); stroke-width: 2.4; }
svg .w-33 { stroke: var(--w-33); stroke-width: 2.2; } svg .w-sig { stroke: var(--w-sig); stroke-width: 1.5; } svg .w-ph { stroke: var(--w-ph); stroke-width: 2.4; }
svg .cabo { stroke-width: 3.2; }
svg .fz { fill: var(--paper); stroke: var(--ink); stroke-width: 1.3; } svg .fzl { stroke: var(--ink); stroke-width: 1.3; }
svg .nd { fill: var(--w-bat); } svg .nd.g { fill: var(--w-gnd); } svg .coil { fill: var(--paper); stroke: var(--w-12); stroke-width: 2; }
svg .flag { fill: var(--paper); stroke: var(--w-12); stroke-width: 1.6; }
svg .mot { fill: var(--paper); stroke: var(--w-ph); stroke-width: 2.2; }
svg .bar-bat { fill: var(--w-bat); } svg .bar-mot { fill: var(--w-mot); } svg .bar-gnd { fill: var(--w-gnd); }
svg .pcb { fill: var(--pcb); stroke: var(--pcb-line); stroke-width: 1.6; } svg .furos { stroke: var(--pcb-line); stroke-width: 2.2; stroke-linecap: round; opacity: .35; }
svg .mod { fill: var(--paper); stroke: var(--pcb-line); stroke-width: 1.4; } svg .mod.drv { fill: var(--zone-l); }
svg .pino { fill: var(--ink); opacity: .55; }
svg .usb, svg .ufl { fill: var(--muted); } svg .jst { fill: var(--paper); stroke: var(--ink); stroke-width: 1.2; }
svg .kf { fill: var(--w-33); opacity: .85; } svg .mos { fill: var(--ink); } svg .dio { fill: var(--ink); }
svg .cap { fill: var(--paper); stroke: var(--w-5); stroke-width: 1.6; } svg .res { fill: var(--accent-soft); stroke: var(--accent); stroke-width: 1; }
svg .cer { fill: var(--paper); stroke: var(--w-12); stroke-width: 1.2; }
svg .zona { fill: none; stroke: var(--muted); stroke-width: 1; stroke-dasharray: 4 3; }
svg .mesa { fill: var(--zone-p); stroke: var(--line); stroke-width: 1.5; }
svg .chapa { fill: var(--paper); stroke: var(--ink); stroke-width: 2; } svg .poste { fill: var(--ink); }
svg .lazy { fill: none; stroke: var(--muted); stroke-width: 1.4; stroke-dasharray: 4 3; }
svg .placa { fill: var(--muted); } svg .roda { fill: var(--w-5); opacity: .55; }
svg .perigo { fill: none; stroke: var(--w-bat); stroke-width: 1.5; stroke-dasharray: 6 4; }
svg .caixa { fill: var(--zone-l); stroke: var(--ink); stroke-width: 2.4; } svg .fonte { fill: var(--paper); stroke: var(--ink); stroke-width: 1.6; }
svg .pc { fill: var(--paper); stroke: var(--muted); stroke-width: 1.4; }
svg .emerg { fill: var(--w-bat); stroke: var(--ink); stroke-width: 2; }
svg .conn { fill: var(--paper); stroke: var(--accent); stroke-width: 1.6; }
svg .cota { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 2 3; }
"""

TOKENS_CLARO = {
    "--paper": "#ffffff", "--ink": "#18212b", "--muted": "#5b6774", "--line": "#d5dce3",
    "--accent": "#a24a1f", "--accent-soft": "#f4e3d8",
    "--w-bat": "#c62f28", "--w-mot": "#d97706", "--w-gnd": "#262c33", "--w-12": "#a8830b", "--w-6": "#7c4dbd",
    "--w-5": "#2563b8", "--w-33": "#23854e", "--w-sig": "#7b8794", "--w-ph": "#8a5a2b",
    "--zone-p": "#fbefe8", "--zone-l": "#eef4fb", "--pcb": "#e3efe6", "--pcb-line": "#5d8f6c",
    "--f-disp": "'Arial Narrow', Arial, sans-serif", "--f-body": "'Segoe UI', Arial, sans-serif", "--f-mono": "Menlo, Consolas, monospace",
}


def avulso(svg):
    """SVG para abrir sozinho: cores fixas (tema claro) e fundo branco."""
    css = CSS_SVG
    for k in sorted(TOKENS_CLARO, key=len, reverse=True):
        css = css.replace(f"var({k})", TOKENS_CLARO[k])
    css = css.replace("svg .fundo { fill: transparent; }", "svg .fundo { fill: #ffffff; }")
    i = svg.index(">") + 1
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + svg[:i] + f"<style>{css}</style>" + svg[i:]
