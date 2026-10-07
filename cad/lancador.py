"""
Lançador de bolas de tênis — versão 2 (compacta, por andares). Modelo paramétrico em CadQuery.

Unidades: mm. Eixos do mundo:
  x = largura (0 no centro), y = profundidade (+ para a frente), z = altura (0 no chão).
Referencial da cabeça (tilt): x igual ao mundo, "u" = para a frente ao longo da linha da bola,
"v" = para cima, origem no pivô do tilt (que fica sobre o eixo do giro).

Andares (de baixo para cima), cada um com placa de base + 4 postes 20x20:
  andar_base         rodas de transporte, pés, 2 baterias Makita, caixa IP65 do controle
  andar_lancador     rolamento do giro, plataforma, garfo, cabeça, atuadores de giro e inclinação,
                     painel traseiro (tela, liga/desliga, emergência), semáforo, antenas, alça
  andar_alimentador  disco agitador, rampas, tubo de queda
  cesto_aberto / cesto_dobrado   cesto de tela com varetas
  carenagem          painéis externos (material a definir) — liga/desliga no construir()

Hierarquia do giro e da inclinação:
  andar_lancador
   └─ pan          (gira em torno do eixo vertical x=0, y=YA)
       ├─ atuador_tilt   (articula na plataforma; o visualizador aponta o fuso para a manivela)
       └─ tilt           (inclina em torno do eixo x, a ZP do chão)
           ├─ roda_sup / roda_inf
           └─ ...

Rodar:  python3 exportar.py   -> gera a pasta saida/
"""
import math

import cadquery as cq

V = cq.Vector

# ----------------------------------------------------------------------------
# PARÂMETROS (mude aqui e rode de novo)
# ----------------------------------------------------------------------------
W, D = 320.0, 430.0            # carenagem externa (sem rodas e alça)
T_CAR = 3.0                    # espessura de referência da carenagem
R_CANTO = 30.0                 # raio dos cantos verticais da carenagem
P = 20.0                       # perfil 20x20
PX, PY = W / 2 - 25, D / 2 - 25   # centro dos postes (135, 190)
YA = -116.0                    # eixo do giro (y)

Z_BASE = 45.0                  # fundo do andar de controle (folga do chão)
T_PISO = 3.0
Z1 = 160.0                     # topo do andar de controle = base do andar do lançador
T_BASE_LANC = 4.0
LAZY_H = 8.0                   # lazy susan redondo Ø150
T_PLAT = 4.0
Z_PLAT = Z1 + T_BASE_LANC + LAZY_H + T_PLAT    # 176 topo da plataforma giratória
ZP = Z_PLAT + 205.0            # 381 linha da bola / pivô do tilt
Z2 = 700.0                     # topo do andar do lançador = base do alimentador
T_ALIM = 3.0
Z3 = 785.0                     # topo do alimentador (assento do cesto)
T_ARO = 3.0

PAN_MAX = 12.5                 # giro ±
TILT_MIN, TILT_MAX = 0.0, 30.0

NIP = 215.0                    # pivô -> nip (para a frente)
WHEEL_D, WHEEL_W, GAP = 150.0, 40.0, 56.0
WC = (WHEEL_D + GAP) / 2       # 103: altura dos eixos das rodas
BALL_R = 33.5
PL_IN, PL_T = 45.0, 6.0        # placas laterais: face interna a ±45, 6 mm
PL_OUT = PL_IN + PL_T          # 51
YOKE_IN, YOKE_T = 74.0, 6.0    # garfo: 74..80

# correias HTD 3M 9 mm, polias de 20 dentes (diâmetro primitivo 19,1)
POLIA_DP = 20 * 3.0 / math.pi
CORREIA_A, CORREIA_B = 600.0, 288.0   # comprimentos padrão (roda de cima / de baixo)
V_MOTOR = -112.0                      # altura dos dois motores (abaixo da linha da bola)


def _pos_motor(v_roda, comp):
    c = (comp - math.pi * POLIA_DP) / 2
    return (NIP - math.sqrt(c * c - (v_roda - V_MOTOR) ** 2), V_MOTOR)


MOT_A = _pos_motor(WC, CORREIA_A)     # motor da roda de cima (placa +x)  ~ (51,7, -112)
MOT_B = _pos_motor(-WC, CORREIA_B)    # motor da roda de baixo (placa -x) ~ (101,4, -112)
MOT_D, MOT_L = 42.0, 50.0

X_ATU = -115.0                 # plano do fuso do tilt (lado -x, por fora da manivela, que fica em x -100..-94)
X_MAN = -100.0                 # face externa da manivela
R_MAN = 64.0                   # raio da manivela; a 15° ela aponta para baixo, então a ponta anda quase só em u
MANIVELA = (-R_MAN * math.sin(math.radians(15)), -R_MAN * math.cos(math.radians(15)))   # ponta (u, v) com a cabeça a 0°
Z_FUSO_TILT = ZP - 63.0        # fuso do tilt deitado ao longo de u, preso no garfo

PAN_BRACO = 102.0              # raio do pino do giro no braço da plataforma (lado +x); motor livre do poste
Y_MOTOR_GIRO = YA - 44.0       # face do motor do giro (corpo para trás, fuso para a frente)
Y_MANCAL_GIRO = YA + 52.0      # rolamento 608 na ponta do fuso de 100 mm
Z_FUSO_PAN = Z1 + T_BASE_LANC + 30.0   # eixo do fuso do giro (horizontal, ao longo de y)

AGIT_C = (0.0, YA + 70.0)      # centro do disco agitador (furo de saída sobre o eixo do giro)
AGIT_R, AGIT_POCKET_R, AGIT_POCKET_D = 110.0, 70.0, 74.0
TUBE_BOTTOM = ZP + 85.0        # fim do tubo de queda (acima do funil da cabeça até +30°)

CESTO_H = 260.0
CESTO_TOPO = (460.0, 540.0)

# ----------------------------------------------------------------------------
# CORES
# ----------------------------------------------------------------------------
def _c(r, g, b, a=1.0):
    return cq.Color(r, g, b, a)


COR = {
    "perfil": _c(0.70, 0.72, 0.75),
    "alu": _c(0.80, 0.82, 0.85),
    "aco": _c(0.36, 0.37, 0.40),
    "petg": _c(0.17, 0.18, 0.20),
    "petg_laranja": _c(0.95, 0.45, 0.10),
    "tpu": _c(0.10, 0.38, 0.86),
    "motor": _c(0.12, 0.12, 0.13),
    "motor_sino": _c(0.62, 0.64, 0.68),
    "latao": _c(0.82, 0.64, 0.25),
    "makita": _c(0.0, 0.58, 0.60),
    "preto": _c(0.07, 0.07, 0.08),
    "borracha": _c(0.11, 0.11, 0.12),
    "caixa": _c(0.62, 0.65, 0.70, 0.30),
    "bola": _c(0.82, 0.94, 0.20),
    "vermelho": _c(0.85, 0.10, 0.10),
    "amarelo": _c(0.98, 0.80, 0.10),
    "pcb_verde": _c(0.05, 0.40, 0.20),
    "pcb_azul": _c(0.10, 0.25, 0.65),
    "pvc": _c(0.92, 0.92, 0.90),
    "correia": _c(0.10, 0.10, 0.10),
    "carenagem": _c(0.96, 0.74, 0.08),
    "grafite": _c(0.13, 0.14, 0.16),
    "malha": _c(0.08, 0.09, 0.10, 0.42),
    "led_vermelho": _c(0.95, 0.15, 0.12),
    "led_amarelo": _c(1.0, 0.75, 0.05),
    "led_verde": _c(0.15, 0.85, 0.30),
    "tela_lcd": _c(0.05, 0.12, 0.20),
}

# ----------------------------------------------------------------------------
# REGISTRO DE PEÇAS
# ----------------------------------------------------------------------------
PECAS = {}
_contador = {}

CAT = {
    "perfil": "Perfil de alumínio (cortado sob medida)",
    "laser": "Corte a laser",
    "impresso": "Impressão 3D",
    "usinado": "Usinagem / barra cortada",
    "comprado": "Comprado pronto",
    "carenagem": "Carenagem (material a definir)",
    "visual": "Só visualização",
}


def reg(base, label, cat, mat="", nota="", arquivo=None):
    if base not in PECAS:
        PECAS[base] = dict(label=label, cat=cat, mat=mat, nota=nota, qtd=0, shape=None, arquivo=arquivo)


def put(assy, shape, base, color, loc=None, **meta):
    if base not in PECAS:
        reg(base, meta.get("label", base), meta.get("cat", "comprado"), meta.get("mat", ""), meta.get("nota", ""))
    n = _contador.get(base, 0) + 1
    _contador[base] = n
    name = f"{base}__{n}"
    PECAS[base]["qtd"] += 1
    if meta.get("espelho"):                      # cópia espelhada: vira um segundo arquivo (…_espelhada)
        PECAS[base].setdefault("espelho_shape", shape)
    elif PECAS[base]["shape"] is None:
        PECAS[base]["shape"] = shape
    if meta.get("variante"):
        PECAS[base].setdefault("variantes", []).append(shape)
    assy.add(shape, name=name, color=color, loc=loc or cq.Location())
    return name


def ploc(origin, xdir, normal):
    return cq.Location(cq.Plane(origin=V(*origin), xDir=V(*xdir), normal=V(*normal)))


def rotz(deg):
    return cq.Location(V(0, 0, 0), V(0, 0, 1), deg)


def rotx(deg):
    return cq.Location(V(0, 0, 0), V(1, 0, 0), deg)


def tr(x, y, z):
    return cq.Location(V(x, y, z))


# ----------------------------------------------------------------------------
# PRIMITIVAS
# ----------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(r).extrude(x1 - x0)


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return cq.Workplane("XZ", origin=(0, y1, 0)).center(x, z).circle(r).extrude(y1 - y0)


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(r).extrude(z1 - z0)


def tube_z(ro, ri, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(ro).circle(ri).extrude(z1 - z0)


def tube_x(ro, ri, x0, x1, y=0.0, z=0.0):
    return cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(ro).circle(ri).extrude(x1 - x0)


def tube_y(ro, ri, y0, y1, x=0.0, z=0.0):
    return cq.Workplane("XZ", origin=(0, y1, 0)).center(x, z).circle(ro).circle(ri).extrude(y1 - y0)


def chapa(outline, t, furos=(), oblongos=(), recortes=()):
    """Chapa no plano XY local, espessura +Z. furos: (x, y, d); oblongos: (x, y, comprimento, largura, ang)."""
    s = outline.extrude(t)
    porD = {}
    for x, y, d in furos:
        porD.setdefault(d, []).append((x, y))
    for d, pts in porD.items():
        s = s.cut(cq.Workplane("XY").pushPoints(pts).circle(d / 2).extrude(t))
    for x, y, ln, lg, ang in oblongos:
        s = s.cut(cq.Workplane("XY").center(x, y).slot2D(ln, lg, ang).extrude(t))
    for r in recortes:
        s = s.cut(r.extrude(t))
    return s


def ret(w, h, cx=0.0, cy=0.0):
    return cq.Workplane("XY").center(cx, cy).rect(w, h)


def ret_arred(w, h, r, cx=0.0, cy=0.0):
    return cq.Workplane("XY").sketch().push([(cx, cy)]).rect(w, h).reset().vertices().fillet(r).finalize()


def furos_anel(r, n, d, ang0=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(math.radians(ang0 + 360 * i / n)),
             cy + r * math.sin(math.radians(ang0 + 360 * i / n)), d) for i in range(n)]


def casco(pts):
    """Envoltória convexa 2D."""
    pts = sorted(set(pts))

    def giro(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    inf, sup = [], []
    for p in pts:
        while len(inf) >= 2 and giro(inf[-2], inf[-1], p) <= 0:
            inf.pop()
        inf.append(p)
    for p in reversed(pts):
        while len(sup) >= 2 and giro(sup[-2], sup[-1], p) <= 0:
            sup.pop()
        sup.append(p)
    return inf[:-1] + sup[:-1]


def circulos(lista, n=40):
    out = []
    for cx, cy, r in lista:
        out += [(round(cx + r * math.cos(2 * math.pi * i / n), 3), round(cy + r * math.sin(2 * math.pi * i / n), 3)) for i in range(n)]
    return out


def poly(pts):
    return cq.Workplane("XY").polyline(pts).close()


# ----------------------------------------------------------------------------
# PEÇAS COMPRADAS (aproximações visuais com cotas de catálogo)
# ----------------------------------------------------------------------------
def perfil2020(comp):
    sk = (cq.Sketch().rect(20, 20)
          .push([(0, 9.2), (0, -9.2)]).rect(6.2, 1.6, mode="s")
          .push([(9.2, 0), (-9.2, 0)]).rect(1.6, 6.2, mode="s")
          .push([(0, 6.6), (0, -6.6)]).rect(10, 3.6, mode="s")
          .push([(6.6, 0), (-6.6, 0)]).rect(3.6, 10, mode="s")
          .reset().push([(0, 0)]).circle(2.1, mode="s"))
    return cq.Workplane("XY").placeSketch(sk).extrude(comp)


def nema17(L=48.0, eixo=24.0, d_eixo=5.0):
    """Face de montagem em z=0, corpo para -z, eixo para +z."""
    corpo = cq.Workplane("XY").rect(42.3, 42.3).extrude(-L).edges("|Z").chamfer(4)
    return corpo.union(cyl_z(11, 0, 2)).union(cyl_z(d_eixo / 2, 2, eixo))


def kfl(L, J, Wf, H, flange, bore, d_furo, housing_d):
    fl = (cq.Workplane("XY").slot2D(L, Wf * 0.55, 0).extrude(flange)
          .union(cq.Workplane("XY").circle(Wf / 2).extrude(flange)))
    s = fl.union(cyl_z(housing_d / 2, 0, H))
    s = s.cut(cyl_z(bore / 2, -1, H + 1))
    return s.cut(cq.Workplane("XY").pushPoints([(-J / 2, 0), (J / 2, 0)]).circle(d_furo / 2).extrude(flange))


def kfl001():
    return kfl(63, 48, 38, 16, 5.5, 12, 7, 30)


def kfl08():
    return kfl(48, 37, 27, 11.5, 4.5, 8, 4.5, 21)


def motor_4250():
    """X-mount (costas) em z=0..4, estator, sino até z=54. Eixo invertido: sai pelas costas (z<0)."""
    xm = cq.Workplane("XY").rect(48, 8).extrude(4).union(cq.Workplane("XY").rect(8, 48).extrude(4))
    estator = cyl_z(MOT_D / 2 - 1, 4, 14)
    sino = tube_z(MOT_D / 2, MOT_D / 2 - 3, 14, 4 + MOT_L).union(cyl_z(MOT_D / 2, 4 + MOT_L - 3, 4 + MOT_L))
    eixo = cyl_z(2.5, -22, 4)
    return xm, estator, sino, eixo


def servo_ds3225():
    """Origem no eixo de saída. Eixo ao longo de +x (topo do corpo em x=12); comprimento ao longo de z,
    com o eixo 10 mm à frente do centro; orelhas no plano x = -1..1,5."""
    corpo = box(-28.5, 12, -10, 10, -30, 10)
    orelhas = box(-1, 1.5, -10, 10, -37, 17)
    eixo = cyl_x(3, 12, 18)
    return corpo.union(orelhas).union(eixo)


def bola():
    return cq.Workplane("XY").sphere(BALL_R)


def bateria_makita():
    base = box(-38, 38, -58, 58, 0, 45)
    topo = box(-38, 38, -58, 40, 45, 65).edges("|Y").fillet(6)
    return base, topo


def polia_htd(furo, larg=15.0):
    """Polia HTD 3M 20 dentes, eixo ao longo de Z local, flanges nas pontas."""
    s = cyl_z(POLIA_DP / 2 - 0.4, 0, larg).union(cyl_z(POLIA_DP / 2 + 2.5, 0, 1)).union(cyl_z(POLIA_DP / 2 + 2.5, larg - 1, larg))
    s = s.union(cyl_z(8, larg, larg + 7))
    return s.cut(cyl_z(furo / 2, -1, larg + 8))


def fecho_pressao():
    """Fecho de pressão inox pequeno (trava entre andares): base + alavanca, face de apoio em y=0, corpo para +y;
    o gancho (z > 6) prende no andar de cima."""
    return box(-14, 14, 0, 6, -18, 6).union(box(-10, 10, 4, 12, -14, 2)).union(box(-8, 8, 0, 4, 8, 22))


# ----------------------------------------------------------------------------
# CHAPAS (corte a laser) — geometria local 2D + espessura
# ----------------------------------------------------------------------------
IN_W, IN_D = W - 2 * T_CAR - 2, D - 2 * T_CAR - 2        # placas internas: 312 x 422
R_PLACA = R_CANTO - T_CAR - 1
FUROS_POSTE = [(sx * PX, sy * PY, 5.5) for sx in (-1, 1) for sy in (-1, 1)]
# pinos de centragem (diagonal): na base do lançador, encostados nos postes; no alimentador, atrás das travessas do topo
PINOS = [(sx * (PX - 20), sy * PY, 8.4) for sx, sy in ((1, 1), (-1, -1))]
PINOS_TOPO = [(sx * 90.0, sy * PY, 10.4) for sx, sy in ((1, 1), (-1, -1))]   # pinos-guia presos no canal de cima das travessas
FECHOS_Y = (-120.0, 120.0)
CESTO_BASE = (IN_W - 44, IN_D - 84)                # dobradiças do cesto (no aro, longe dos parafusos dos postes)
X_BATERIA, Y_BATERIA = 46.0, -D / 2 + 72          # centro dos berços das baterias (±x)
Y_PE = D / 2 - 30                                  # pés de borracha (frente)


def ch_piso():
    """Piso do andar de controle."""
    furos = list(FUROS_POSTE)
    for sx in (-1, 1):
        furos += [(sx * X_BATERIA + dx, Y_BATERIA + dy, 4.5) for dx in (-36, 36) for dy in (-55, 55)]   # berços das baterias
        furos += [(sx * 105, Y_PE, 8.5)]                                                                  # pés
        furos += [(sx * 120, D / 2 - 195 + dy, 4.5) for dy in (0, 150)]                                   # caixa IP65
    furos += [(sx * 60, sy * 60, 25) for sx in (-1, 1) for sy in (-1, 1)]                            # alívio
    return chapa(ret_arred(IN_W, IN_D, R_PLACA), T_PISO, furos)


def ch_base_lancador():
    """Base do andar do lançador: lazy susan, passagem de cabos, motor e mancal do fuso do giro."""
    furos = list(FUROS_POSTE) + [(x, y, d) for x, y, d in PINOS]
    furos += [(0, YA, 40)]
    furos += furos_anel(66, 4, 4.5, 45, 0, YA)                     # lazy susan (parte fixa)
    furos += [(PAN_BRACO + dx, Y_MOTOR_GIRO - 10, 4.5) for dx in (-16, 16)]                  # suporte do motor do giro
    furos += [(PAN_BRACO + dx, Y_MANCAL_GIRO, 4.5) for dx in (-16, 16)]                      # mancal da ponta do fuso
    furos += [(sx * 95, sy * 120, 30) for sx in (-1, 1) for sy in (-1, 1)]                    # alívio
    furos += [(-PX + 22, -PY + 40, 22), (PX - 22, -PY + 40, 22)]                               # conectores entre andares
    return chapa(ret_arred(IN_W, IN_D, R_PLACA), T_BASE_LANC, furos)


def ch_alimentador():
    ax, ay = AGIT_C
    furos = list(FUROS_POSTE) + [(x, y, d) for x, y, d in PINOS_TOPO]
    furos += [(0, YA, 76)] + furos_anel(50, 3, 4.5, 30, 0, YA)
    furos += [(ax, ay, 23)] + [(ax + dx, ay + dy, 3.4) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]
    furos += [(sx * 120, sy * 150, 4.5) for sx in (-1, 1) for sy in (-1, 1)]                   # rampas
    return chapa(ret_arred(IN_W, IN_D, R_PLACA), T_ALIM, furos)


def ch_aro_topo():
    """Aro do topo do alimentador: assento do cesto."""
    out = ret_arred(IN_W, IN_D, R_PLACA)
    furos = list(FUROS_POSTE) + [(sx * CESTO_BASE[0] / 2, sy * CESTO_BASE[1] / 2, 3.4) for sx in (-1, 1) for sy in (-1, 1)]   # dobradiças (M3)
    return chapa(out, T_ARO, furos, recortes=[ret_arred(IN_W - 60, IN_D - 60, 20)])


def ch_plataforma():
    """Plataforma giratória (referencial do giro, origem no eixo): faixa do garfo e braço do giro (+x)."""
    corpo = (cq.Workplane("XY").circle(78).extrude(T_PLAT).union(box(-81, 81, -34, 34, 0, T_PLAT))
             .intersect(cq.Workplane("XY").circle(84).extrude(T_PLAT)))      # raio máx. 84: passa pelo motor e pelo mancal do giro
    braco = box(70, PAN_BRACO, -14, 14, 0, T_PLAT).union(cyl_z(14, 0, T_PLAT, PAN_BRACO, 0))
    s = corpo.union(braco)
    furos = [(0, 0, 40)] + furos_anel(60, 4, 4.5, 0)
    furos += [(sx * 62, sy * 20, 4.5) for sx in (-1, 1) for sy in (-1, 1)]          # cantoneiras do garfo
    furos += [(PAN_BRACO, 0, 6.2)]                                                    # pino do giro
    for x, y, d in furos:
        s = s.cut(cyl_z(d / 2, -1, T_PLAT + 1, x, y))
    return s


def placa_lateral_pts():
    return casco(circulos([(NIP, WC, 52), (NIP, -WC, 52), (0, 0, 32), (MOT_A[0], MOT_A[1], 30),
                           (MOT_B[0], MOT_B[1], 30), (-50, -88, 30)], 36))


ESPACADORES = [(-62, 45), (130, 60), (130, -60), (0, -122)]


def furos_motor(mu, mv, alvo):
    """Furo do eixo + 4 oblongos M3 na direção da correia (tensionamento ±3 mm)."""
    ang = math.degrees(math.atan2(alvo[1] - mv, alvo[0] - mu))
    furos = [(mu, mv, 14)]
    obl = []
    for a in (45, 135, 225, 315):
        r = 19.0
        obl.append((mu + r * math.cos(math.radians(a)), mv + r * math.sin(math.radians(a)), 9.4, 3.4, ang))
    return furos, obl


def bossas_carenagem_roda(lado):
    """Pontos (u, v) dos tubos de fixação da carenagem da roda (lado +1: roda de cima)."""
    cv = WC * lado
    return [(NIP + 81.5 * math.cos(math.radians(a)), cv + 81.5 * math.sin(math.radians(a)))
            for a in ((180, 160) if lado > 0 else (180, 200))]


def bossas_tampa(lado):
    """Pontos (u, v) dos espaçadores da tampa da correia: dentro do laço da correia, longe das polias."""
    m = MOT_A if lado > 0 else MOT_B
    r = (NIP, WC if lado > 0 else -WC)
    return [(m[0] + t * (r[0] - m[0]), m[1] + t * (r[1] - m[1])) for t in (0.35, 0.65)]


SERVO_EIXO = (-45.0, -82.0)     # eixo do servo do empurrador (u, v)


def ch_lateral():
    """Placa lateral da cabeça (u=frente, v=cima, origem no pivô). A mesma peça nos dois lados."""
    furos = [(0, 0, 8.1),
             (NIP, WC, 16), (NIP, WC - 24, 7), (NIP, WC + 24, 7)]
    furos += [(u, v, 5.5) for u, v in ESPACADORES]
    fa, oa = furos_motor(*MOT_A, (NIP, WC))
    fb, ob = furos_motor(*MOT_B, (NIP, -WC))
    furos += fa + fb
    furos += [(-64, -70, 4.5), (-64, -108, 4.5)]                   # suporte do servo (placa -x)
    furos += [(-25, -44, 4.5), (25, -44, 4.5)]                     # berço
    furos += [(-30, 40, 4.5), (60, 40, 4.5)]                       # funil
    furos += [(125, -42, 4.5)]                                     # suporte dos trilhos
    furos += [(u, v, 4.5) for lado in (1, -1) for u, v in bossas_carenagem_roda(lado)]   # carenagens das rodas
    furos += [(NIP - 24, WC, 3.4), (NIP - 24, -WC, 3.4)]           # suportes dos sensores Hall
    furos += [(u, v, 3.4) for lado in (1, -1) for u, v in bossas_tampa(lado)]            # tampas das correias
    obl = oa + ob + [(NIP, -WC, 24, 16, 90), (NIP, -WC - 24, 15, 7, 90), (NIP, -WC + 24, 15, 7, 90)]
    return chapa(poly(placa_lateral_pts()), PL_T, furos, obl)


def ch_garfo():
    """Garfo do tilt (plano y-z local: x=u, y=altura acima da plataforma)."""
    h = ZP - Z_PLAT        # 205
    pts = casco(circulos([(0, h, 30), (-26, 4, 4), (26, 4, 4)], 40)) + [(-30, 0), (30, 0)]
    s = poly(casco(pts)).extrude(YOKE_T)
    for x, y, d in [(0, h, 12), (0, h - 18.5, 4.5), (0, h + 18.5, 4.5), (-18, 22, 4.5), (18, 22, 4.5), (0, 110, 30)]:
        s = s.cut(cyl_z(d / 2, -1, YOKE_T + 1, x, y))
    return s


def ch_manivela():
    """Manivela presa no semi-eixo -x por furo em D (eixo Ø8 com chato de 7 mm); o pino da ponta entra na porca do tilt."""
    pts = casco(circulos([(0, 0, 14), (MANIVELA[0], MANIVELA[1], 11)], 30))
    s = chapa(poly(pts), 6.0, [(MANIVELA[0], MANIVELA[1], 5.5)])
    d = cq.Workplane("XY").circle(4.05).extrude(6).intersect(cq.Workplane("XY").center(-0.5, 0).rect(7.1, 9).extrude(6))
    return s.cut(d)


def furo_d(t):
    """Furo em D para eixo Ø12 com chato (11,1 mm entre faces)."""
    return (cq.Workplane("XY").circle(6.05).extrude(t)
            .intersect(cq.Workplane("XY").center(-0.5, 0).rect(11.1, 13).extrude(t)))


def ch_disco_inercia():
    s = cq.Workplane("XY").circle(60).extrude(3)
    s = s.cut(cq.Workplane("XY").pushPoints([(x, y) for x, y, _ in furos_anel(50, 6, 4.5, 0)]).circle(2.25).extrude(3))
    return s.cut(furo_d(3))


def ch_suporte_roda():
    """Suporte da roda de transporte, parafusado na face externa do poste de trás
    (plano local: x = y do mundo a partir de y=-150, y = z do mundo a partir do piso)."""
    zr = 62.5 - (Z_BASE + T_PISO)
    pts = [(-50, 0), (20, 0), (20, 34), (-28, 100), (-50, 100)]     # -50: livre do canto arredondado da carenagem
    return chapa(poly(pts), 4.0, [(-40, 47, 5.5), (-40, 82, 5.5), (0, zr, 8.4)])


# ----------------------------------------------------------------------------
# PEÇAS IMPRESSAS
# ----------------------------------------------------------------------------
def imp_nucleo_roda():
    s = cq.Workplane("XY").circle(67).extrude(32).translate((0, 0, -16))
    s = s.cut(cyl_z(6.6, -20, 20))
    s = s.cut(cq.Workplane("XY", origin=(0, 0, -16)).pushPoints([(x, y) for x, y, _ in furos_anel(50, 6, 4.4, 0)]).circle(2.2).extrude(32))
    for i in range(8):
        s = s.cut(box(-3, 3, 63.8, 68, -16, 16).rotate((0, 0, 0), (0, 0, 1), 360 * i / 8 + 22.5))
    return s


def imp_banda_tpu():
    prof = (cq.Workplane("XY").moveTo(-20, 67).lineTo(20, 67).lineTo(20, 75).threePointArc((0, 70.83), (-20, 75)).close())
    s = prof.revolve(360, (0, 0, 0), (1, 0, 0))
    for i in range(8):
        s = s.union(box(-16, 16, -2.8, 2.8, 63.9, 67.1).rotate((0, 0, 0), (1, 0, 0), 360 * i / 8 + 22.5))
    return s.rotate((0, 0, 0), (0, 1, 0), 90)


def imp_disco_sinal():
    s = cq.Workplane("XY").circle(20).extrude(8).cut(furo_d(8))
    s = s.cut(cq.Workplane("XY", origin=(0, 0, 4.8)).pushPoints([(15, 0), (-15, 0)]).circle(3.1).extrude(3.2))
    return s.cut(cyl_x(1.4, 0, 21, 0, 4))


def imp_carenagem_roda(lado):
    """Carenagem da roda entre as placas, aberta na direção da linha da bola."""
    ri, ro = 80, 83
    a0, a1 = (0, 200) if lado > 0 else (160, 360)
    cv = WC * lado

    def p(r, a):
        return (NIP + r * math.cos(math.radians(a)), cv + r * math.sin(math.radians(a)))
    am = (a0 + a1) / 2
    wp = (cq.Workplane("YZ", origin=(-PL_IN + 0.5, 0, 0)).moveTo(*p(ro, a0)).threePointArc(p(ro, am), p(ro, a1))
          .lineTo(*p(ri, a1)).threePointArc(p(ri, am), p(ri, a0)).close())
    s = wp.extrude(2 * PL_IN - 1)
    for u, v in bossas_carenagem_roda(lado):
        s = s.union(tube_x(5, 2.25, -PL_IN + 0.5, PL_IN - 0.5, u, v))
    return s


def imp_berco():
    s = box(-45, 45, -45, 32, -55, -33)
    s = s.cut(cq.Workplane("XZ", origin=(0, 40, 0)).circle(37).extrude(90))
    s = s.cut(cyl_x(2.25, -46, 46, -25, -44)).cut(cyl_x(2.25, -46, 46, 25, -44))
    s = s.cut(box(10, 17, -50, 2, -56, -32))                       # rasgo por onde passa o braço do empurrador
    return s.cut(cyl_y(4.1, -50, 40, x=20, z=-31.7)).cut(cyl_y(4.1, -50, 40, x=-20, z=-31.7))


def imp_funil():
    """Funil da cabeça: recebe a bola do tubo fixo em qualquer inclinação de 0° a 30°."""
    def loft(dw, z_top, z_bot):
        return (cq.Workplane("XY", origin=(0, 22.5, z_top)).rect(84 + dw, 140 + dw)
                .workplane(offset=z_bot - z_top).center(0, -22.5).circle(39 + dw / 2).loft())
    s = loft(5, 52, 36).cut(loft(0, 52.01, 35.99))
    for u in (-30, 60):
        for sx in (-1, 1):
            s = s.union(box(sx * 40 if sx > 0 else -45, 45 if sx > 0 else -40, u - 7, u + 7, 33, 47))
    return s.cut(cyl_x(2.25, -46, 46, -30, 40)).cut(cyl_x(2.25, -46, 46, 60, 40))


def imp_suporte_trilho():
    s = box(-45, 45, 118, 132, -50, -36)
    for sx in (-1, 1):
        s = s.union(box(sx * 16 - 8, sx * 16 + 8, 118, 132, -36, -26))
    s = s.cut(cyl_y(4.1, 110, 140, x=20, z=-31.7)).cut(cyl_y(4.1, 110, 140, x=-20, z=-31.7))
    return s.cut(cyl_x(2.25, -46, 46, 125, -42))


def imp_suporte_servo():
    """Placa em x=-5..-1 onde apoiam as orelhas do servo (janela para o corpo), ligada à placa lateral -x
    por uma parede em u=-68..-60 com dois parafusos M4."""
    u0, v0 = SERVO_EIXO
    placa = box(-5, -1, -68, -28, -124, -60)
    placa = placa.cut(box(-6, 0, u0 - 10.5, u0 + 10.5, v0 - 30.5, v0 + 10.5))          # janela do corpo
    for du in (-5, 5):
        for dv in (-24.75, 24.75):
            placa = placa.cut(cyl_x(1.7, -6, 0, u0 + du, v0 - 10 + dv))                 # orelhas (M3)
    parede = box(-45, -5, -68, -60, -124, -60)
    s = placa.union(parede)
    return s.cut(cyl_x(2.25, -46, -4, -64, -70)).cut(cyl_x(2.25, -46, -4, -64, -108))


def imp_braco_empurrador():
    """Braço do servo: do eixo (u=-45, v=-82) até a ponta atrás da bola."""
    p0, p1 = SERVO_EIXO, (-36.0, -10.0)
    ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    arm = (cq.Workplane("YZ", origin=(12, 0, 0)).center(p0[0] + L / 2, p0[1]).rect(L, 10).extrude(3)
           .rotate((0, p0[0], p0[1]), (1, p0[0], p0[1]), ang))
    hub = cyl_x(8, 12, 15, p0[0], p0[1])
    pad = box(-12, 15, -43, -37, -16, 2)
    return arm.union(hub).union(pad).cut(cyl_x(3.05, 11, 16, p0[0], p0[1]))


X_TAMPA = PL_OUT + 27           # face externa da tampa da correia (polia de 22 mm com cubo + folga)


def imp_tampa_correia(lado):
    """Tampa da correia, por fora da placa (lado +1: correia da roda de cima, em +x). Aberta do lado da placa;
    presa por dois espaçadores M3 dentro do laço da correia."""
    m = MOT_A if lado > 0 else MOT_B
    r = (NIP, WC if lado > 0 else -WC)
    pts = casco(circulos([(m[0], m[1], 19), (r[0], r[1], 19)], 36))
    oco_pts = casco(circulos([(m[0], m[1], 17), (r[0], r[1], 17)], 36))
    x0, x1 = PL_OUT + 1, X_TAMPA
    casca_ = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts).close().extrude(x1 - x0)
    oco = cq.Workplane("YZ", origin=(x0 - 1, 0, 0)).polyline(oco_pts).close().extrude(x1 - x0 - 1)
    s = casca_.cut(oco)
    for u, v in bossas_tampa(lado):
        s = s.union(tube_x(4, 1.7, PL_OUT, x1, u, v))
    return s if lado > 0 else s.mirror("YZ")


def imp_suporte_hall():
    """Origem na face externa da placa, no eixo da roda (lado +x). Aba presa à placa por um M3 ao longo de x;
    o sensor fica de frente para o disco de sinal, a 15 mm do eixo."""
    s = box(0, 18, -28, -20, -6, 6).union(box(15, 18, -28, -10, -6, 6))
    return s.cut(cyl_x(1.7, -1, 19, -24, 0))


def imp_bloco_porca_tilt():
    """Corre no fuso do tilt (ao longo de u). O rasgo vertical, só na face +x (do lado da manivela), recebe o pino
    da ponta da manivela sem chegar no fuso."""
    s = box(-14, 14, -12, 12, -14, 14).edges("|Y").fillet(3)
    s = s.cut(cyl_y(5.2, -13, 13, 0, 0))
    return s.cut(box(8, 15, -3.2, 3.2, -7, 7))


U_MOTOR_TILT = 40.0            # face do motor do tilt (u); corpo para a frente, fuso para trás


def imp_suporte_motor_tilt():
    """Coordenadas do referencial do giro (x, u, z). Preso na face externa do garfo -x, abaixo da
    faixa onde corre a porca; segura o NEMA17 do tilt pela face, com o fuso voltado para trás."""
    xg = -YOKE_IN - YOKE_T                       # face externa do garfo
    zf = Z_FUSO_TILT
    fixa = box(xg - 6, xg, -20, U_MOTOR_TILT, zf - 68, zf - 22)          # aba no garfo, abaixo da porca
    nervura = box(xg - 6, xg, U_MOTOR_TILT - 12, U_MOTOR_TILT, zf - 68, zf + 22)
    face = box(X_ATU - 23, xg, U_MOTOR_TILT - 6, U_MOTOR_TILT, zf - 24, zf + 22)
    s = fixa.union(nervura).union(face)
    s = s.cut(cyl_y(11.5, U_MOTOR_TILT - 7, U_MOTOR_TILT + 1, X_ATU, zf))
    s = s.cut(cq.Workplane("XZ", origin=(0, U_MOTOR_TILT + 1, 0)).pushPoints(
        [(X_ATU + dx, zf + dz) for dx in (-15.5, 15.5) for dz in (-15.5, 15.5)]).circle(1.7).extrude(8))
    return s.cut(cyl_x(2.25, xg - 7, xg + 1, 0, zf - 45)).cut(cyl_x(2.25, xg - 7, xg + 1, 25, zf - 45))


def imp_suporte_motor_giro():
    """Suporte em L do NEMA17 do giro (deitado ao longo de y). Origem no centro da base, na face do motor (y=0);
    o motor fica pendurado pela face (y<0) e o fuso atravessa a parede para +y."""
    zc = Z_FUSO_PAN - Z1 - T_BASE_LANC
    s = box(-24, 24, -16, 4, 0, 4)                                   # base, 2 parafusos M4
    s = s.union(box(-24, 24, 0, 4, 0, zc + 22))                      # parede da face do motor
    s = s.union(box(21.5, 24, -16, 0, 4, 18)).union(box(-24, -21.5, -16, 0, 4, 18))   # nervuras dos lados do motor
    s = s.cut(cyl_y(11.5, -1, 5, 0, zc))
    s = s.cut(cq.Workplane("XZ", origin=(0, 5, 0)).pushPoints([(dx, zc + dz) for dx in (-15.5, 15.5) for dz in (-15.5, 15.5)]).circle(1.7).extrude(6))
    return s.cut(cyl_z(2.25, -1, 5, -16, -10)).cut(cyl_z(2.25, -1, 5, 16, -10))


def imp_bloco_porca_giro():
    """Corre no fuso do giro; o rasgo de baixo (ao longo de x) recebe o pino da plataforma."""
    s = box(-14, 14, -12, 12, -16, 12)
    s = s.cut(cyl_y(5.2, -13, 13, 0, 0))
    return s.cut(cq.Workplane("XY", origin=(0, 0, -17)).slot2D(14, 6.4, 0).extrude(9))


def imp_mancal_fuso():
    zc = Z_FUSO_PAN - Z1 - T_BASE_LANC
    s = box(-24, 24, -8, 8, 0, zc + 14)
    return s.cut(cyl_y(11.1, -9, 9, 0, zc)).cut(cyl_z(2.25, -1, 5, -16, 0)).cut(cyl_z(2.25, -1, 5, 16, 0))


def imp_rotor_agitador():
    s = cq.Workplane("XY").circle(AGIT_R).extrude(6)
    s = s.cut(cq.Workplane("XY").pushPoints([(x, y) for x, y, _ in furos_anel(AGIT_POCKET_R, 4, 0, -90)])
              .circle(AGIT_POCKET_D / 2).extrude(6))
    s = s.union(cq.Workplane("XY", origin=(0, 0, 6)).circle(30).workplane(offset=50).circle(6).loft())
    return s.cut(cyl_z(2.55, -1, 24)).cut(cyl_x(1.4, 0, 40, 0, 14))


def imp_capuz():
    """Cobertura sobre o furo de saída (fica atrás do disco, sobre o eixo do giro)."""
    ang = -90

    def sector(ri, ro, z0, z1):
        def p(r, a):
            return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
        a0, a1 = ang - 30, ang + 30
        return (cq.Workplane("XY", origin=(0, 0, z0)).moveTo(*p(ro, a0)).threePointArc(p(ro, ang), p(ro, a1))
                .lineTo(*p(ri, a1)).threePointArc(p(ri, ang), p(ri, a0)).close().extrude(z1 - z0))
    return sector(32, 116, 76, 79).union(sector(113, 116, 9, 76))


def imp_rampas():
    """Fundo inclinado do alimentador (15°) em 4 partes, em volta do disco."""
    ax, ay = AGIT_C
    hx, hy = IN_W / 2 - 1, IN_D / 2 - 1
    h = Z3 - T_ARO - Z2 - T_ALIM - 2
    bloco = box(-hx, hx, -hy, hy, 0, h)
    zdisc = 6.5
    r0 = AGIT_R + 2
    r1 = r0 + (h - zdisc) / math.tan(math.radians(15))
    cone = cq.Workplane("XY", origin=(ax, ay, zdisc)).circle(r0).workplane(offset=h - zdisc + 0.01).circle(r1).loft()
    bloco = bloco.cut(cone).cut(cyl_z(r0, -1, zdisc + 0.01, ax, ay))
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * (PX - 12), sx * (PX + 30)))
            ya, yb = sorted((sy * (PY - 12), sy * (PY + 30)))
            bloco = bloco.cut(box(xa, xb, ya, yb, -1, h + 1))
    for x, y, _ in PINOS_TOPO:
        bloco = bloco.cut(cyl_z(6.5, -1, 8, x, y))                 # bolso do pino-guia
    quads = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            quads.append(bloco.intersect(box(min(ax, sx * 400), max(ax, sx * 400), min(ay, sy * 400), max(ay, sy * 400), -2, h + 2)))
    return quads


def imp_flange_tubo():
    """Flange de 3 orelhas (a orelha de +y ficaria no motor do agitador, então não existe)."""
    furos = [(x, y) for x, y, _ in furos_anel(50, 3, 4.5, 30)]
    s = cyl_z(44, -4, 0)
    for x, y in furos:
        s = s.union(cyl_z(8, -4, 0, x, y))
    s = s.union(tube_z(42.5, 37.75, -15, -4))
    s = s.cut(cyl_z(36, -16, 1))
    return s.cut(cq.Workplane("XY", origin=(0, 0, -4)).pushPoints(furos).circle(2.25).extrude(4))


def imp_berco_bateria():
    s = box(-42.5, 42.5, -65, 65, 0, 8)
    s = s.cut(box(-39.5, 39.5, -61, 70, 3, 8.1))
    return s.cut(cq.Workplane("XY").pushPoints([(-36, -55), (36, -55), (-36, 55), (36, 55)]).circle(2.25).extrude(8))


X_BOTAO = 80.0                 # botões do painel traseiro (±x)


def imp_painel_traseiro():
    """Painel traseiro entre os postes de trás (face em y=0, para -y): tela 3,5", liga/desliga, emergência."""
    w, h = 2 * (PX - P / 2) - 1, 100.0
    s = box(-w / 2, w / 2, -4, 22, 0, h)
    s = s.cut(box(-w / 2 + 3, w / 2 - 3, 0, 23, 3, h - 3))
    s = s.cut(box(-46, 46, -5, 1, 22, 82))            # janela da tela
    s = s.cut(cyl_y(11.2, -5, 1, -X_BOTAO, 52))        # emergência
    s = s.cut(cyl_y(11.2, -5, 1, X_BOTAO, 52))         # liga/desliga
    for sx in (-1, 1):
        s = s.cut(cyl_x(2.75, sx * w / 2 - 4 if sx > 0 else -w / 2 - 1, sx * w / 2 + 1 if sx > 0 else -w / 2 + 4, 9, 20)).cut(
            cyl_x(2.75, sx * w / 2 - 4 if sx > 0 else -w / 2 - 1, sx * w / 2 + 1 if sx > 0 else -w / 2 + 4, 9, 80))
    return s


def imp_semaforo():
    """Caixa do semáforo (3 células) com pala; face em y=0 para +y."""
    s = box(-66, 66, -24, 0, -22, 22).edges("|Y").fillet(8)
    s = s.cut(box(-62, 62, -22, 1, -18, 18))
    s = s.union(box(-66, 66, 0, 16, 19, 22))
    for i in range(3):
        s = s.union(tube_y(16, 14, -19, 0, -42 + 42 * i, 0))         # células; a placa de LEDs fica atrás (y -22..-20)
    return s.union(box(-66, 66, -30, -24, -22, 22).cut(box(-30, 30, -31, -23, -10, 10)))


def imp_difusor():
    return cyl_y(14, -2, 0)


def imp_suporte_antena():
    """Lado +x. Origem no canto externo do poste (x = face externa, y = face voltada para a frente).
    Aba de 4 mm presa no canal do poste (M5) + bloco até a carenagem com o furo do conector SMA."""
    aba = box(-18, 0, 0, 4, -20, 20).cut(cyl_y(2.75, -1, 5, -10, 0))
    bloco = box(0, 11, 0, 16, -14, 14).cut(cyl_x(3.4, -1, 12, 8, 0))
    return aba.union(bloco)


def imp_abracadeira_alca():
    """Origem na face de trás do poste (lado +x, centro do poste); o tubo da alça fica 29 mm atrás, 20 mm para dentro.
    A parte de dentro (x < -10) recua 3 mm para passar atrás do painel traseiro."""
    s = box(-10, 10, -40, 0, -13, 13).union(box(-32, -10, -40, -3, -13, 13))
    s = s.cut(cyl_z(10.2, -14, 14, -20, -29))
    return s.cut(cyl_y(2.75, -41, 1, 0, 0))


def imp_pino_centragem():
    """Pino do andar de controle: rosqueia (M5 sem cabeça) no inserto do topo do bloco do pino."""
    return cyl_z(9, 0, 6).union(cq.Workplane("XY", origin=(0, 0, 6)).circle(4).workplane(offset=7).circle(2.5).loft()).cut(cyl_z(2.6, -1, 4))


def imp_bloco_pino():
    """Bloco 20x20x24 do pino: inserto M5 no topo e furo passante M5 (ao longo de x) para o canal do poste."""
    s = box(-10, 10, -10, 10, 0, 24)
    s = s.cut(cyl_z(3.2, 17, 25))
    return s.cut(cyl_x(2.75, -11, 11, 0, 7))


def imp_pino_guia_topo():
    """Pino-guia Ø10 do alimentador: preso por M4 + porca-T no canal de cima da travessa do topo; entra 3 mm na
    base do alimentador e 6 mm na rampa."""
    s = cyl_z(5, 0, 9).faces(">Z").chamfer(1.5)
    return s.cut(cyl_z(2.25, -1, 10)).cut(cyl_z(3.9, 5, 10))


def imp_suporte_conectores():
    s = box(-22, 22, -12, 12, 0, 3).union(box(-22, 22, 9, 12, 0, 30))
    return s.cut(cyl_y(8.1, 8, 13, -10, 18)).cut(box(5, 17, 8, 13, 10, 26))


def imp_dobradica_cesto():
    """Base com M3 no centro e duas orelhas; a ponta da vareta (amassada e furada) gira num pino M3 entre elas."""
    s = box(-12, 12, -12, 12, 0, 5).union(box(3, 6, -6, 6, 5, 20)).union(box(-6, -3, -6, 6, 5, 20))
    return s.cut(cyl_x(1.7, -7, 7, 0, 14)).cut(cyl_z(1.7, -1, 6, 0, 0))


def vareta_dir():
    """Direção unitária da vareta do canto (+x, +y) do cesto aberto."""
    w0, d0 = CESTO_BASE
    w1, d1 = CESTO_TOPO
    return (V(w1 / 2, d1 / 2, Z3 + CESTO_H) - V(w0 / 2, d0 / 2, Z3 + 14)).normalized()


def imp_canto_cesto():
    """Canto (+x, +y): recebe as varetas do aro (vindo de -x e de -y) e a vareta inclinada (vindo de baixo).
    Os cantos (+x,-y) e (-x,+y) são a peça espelhada."""
    n = vareta_dir()
    s = cq.Workplane("XY").sphere(11).cut(cyl_x(4.1, -12, 0)).cut(cyl_y(4.1, -12, 0))
    furo = cq.Workplane(cq.Plane(origin=V(0, 0, 0), xDir=n.cross(V(0, 0, 1)).normalized(), normal=-n)).circle(4.1).extrude(12)
    return s.cut(furo)


def imp_calibre():
    s = box(-30, 30, -10, 10, 0, 56).edges("|Z").fillet(3)
    return s.cut(box(-20, 20, -11, 11, 10, 46))


# ----------------------------------------------------------------------------
# CARENAGEM (material a definir)
# ----------------------------------------------------------------------------
def caixa_arred(w, d, z0, z1, r, cx=0.0, cy=0.0):
    return cq.Workplane("XY", origin=(0, 0, z0)).center(cx, cy).rect(w, d).extrude(z1 - z0).edges("|Z").fillet(r)


def casca(z0, z1):
    return caixa_arred(W, D, z0, z1, R_CANTO).cut(caixa_arred(W - 2 * T_CAR, D - 2 * T_CAR, z0 - 1, z1 + 1, R_CANTO - T_CAR))


Z_JANELA = (ZP - 52, ZP + 245)
Z_SEMAFORO = Z_JANELA[1] + 30
Z_PAINEL = Z2 - P - 20 - 100          # topo do painel 2 mm abaixo das cantoneiras do quadro do topo
Y_ANTENA, Z_ANTENA = -PY + 18, Z2 - 50
Z_ALCA = (Z1 + 60, Z2 - 60)           # abraçadeiras da alça


def car_base():
    s = casca(Z_BASE - 2, Z1 - 1)
    s = s.cut(box(-90, 90, -D / 2 - 1, -D / 2 + T_CAR + 1, Z_BASE + 12, Z1 - 15))       # abertura da tampa das baterias
    for sx in (-1, 1):
        s = s.cut(cyl_x(5, sx * W / 2 - 5 if sx > 0 else -W / 2 - 1, sx * W / 2 + 1 if sx > 0 else -W / 2 + 5, -150, 62.5))   # eixos das rodas
    return s


def car_lancador():
    s = casca(Z1 + 1, Z2 - 1)
    zj0, zj1 = Z_JANELA
    jan = cq.Workplane("XZ", origin=(0, D / 2 + 5, 0)).center(0, (zj0 + zj1) / 2).rect(232, zj1 - zj0).extrude(20).edges("|Y").fillet(40)
    s = s.cut(jan)
    s = s.cut(cq.Workplane("XZ", origin=(0, D / 2 + 5, 0)).center(0, Z_SEMAFORO).rect(136, 46).extrude(20))
    s = s.cut(cq.Workplane("XZ", origin=(0, -D / 2 + 5, 0)).center(0, Z_PAINEL + 50).rect(2 * (PX - P / 2) - 8, 94).extrude(20))
    for sx in (-1, 1):
        s = s.cut(cyl_x(3.5, sx * W / 2 - 5 if sx > 0 else -W / 2 - 1, sx * W / 2 + 1 if sx > 0 else -W / 2 + 5, Y_ANTENA, Z_ANTENA))
        for zc in Z_ALCA:
            s = s.cut(box(sx * PX - 34 if sx > 0 else -PX - 12, sx * PX + 12 if sx > 0 else -PX + 34, -D / 2 - 1, -D / 2 + 14, zc - 15, zc + 15))
    return s


# ----------------------------------------------------------------------------
# GRUPOS
# ----------------------------------------------------------------------------
def postes(a, z0, z1, base, label):
    reg(base, label, "perfil", "Alumínio 20x20 canal 6")
    p = perfil2020(z1 - z0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, p, base, COR["perfil"], tr(sx * PX, sy * PY, z0))


def fechos(a, z):
    reg("fecho_pressao", "Fecho de pressão inox pequeno (trava entre andares)", "comprado", "Inox")
    for sx in (-1, 1):
        for y in FECHOS_Y:
            # local y -> para fora (sx), local z -> para cima
            put(a, fecho_pressao(), "fecho_pressao", COR["aco"], ploc((sx * W / 2, y, z), (0, -sx, 0), (0, 0, 1)))


def montar_base(a):
    reg("chapa_piso", "Piso do andar de controle (Al 3 mm)", "laser", "Alumínio 5052, 3 mm")
    put(a, ch_piso(), "chapa_piso", COR["alu"], tr(0, 0, Z_BASE))
    postes(a, Z_BASE + T_PISO, Z1, "poste_base", f"Poste do andar de controle (perfil 20x20, {Z1 - Z_BASE - T_PISO:.0f} mm)")
    reg("pino_centragem", "Pino de centragem entre andares", "impresso", "PETG")
    for x, y, _ in PINOS:
        put(a, imp_pino_centragem(), "pino_centragem", COR["petg"], tr(x, y, Z1 - 6))
        put(a, imp_bloco_pino(), "bloco_pino", COR["petg"], tr(x, y, Z1 - 30),
            label="Bloco do pino (preso na face do poste)", cat="impresso", mat="PETG")
    # baterias deitadas, saindo por trás
    reg("bateria_makita", "Bateria Makita 18 V 5,0 Ah", "comprado", "")
    reg("bateria_makita_topo", "Bateria Makita (topo)", "visual", "")
    reg("soquete_makita", "Adaptador/soquete de bateria Makita 18 V", "comprado", "")
    reg("berco_bateria", "Berço do soquete de bateria", "impresso", "PETG")
    b, t = bateria_makita()
    for sx in (-1, 1):
        x0, y0 = sx * X_BATERIA, Y_BATERIA
        put(a, imp_berco_bateria(), "berco_bateria", COR["petg"], tr(x0, y0, Z_BASE + T_PISO))
        put(a, b, "bateria_makita", COR["makita"], tr(x0, y0, Z_BASE + T_PISO + 3))
        put(a, t, "bateria_makita_topo", COR["preto"], tr(x0, y0, Z_BASE + T_PISO + 3))
        put(a, box(-40, 40, -60, 60, 0, 22), "soquete_makita", COR["preto"], tr(x0, y0, Z_BASE + T_PISO + 68))
    # caixa IP65 com o controle
    reg("caixa_ip65", "Caixa ABS IP65 ~220x170x100", "comprado", "ABS")
    zc0 = Z_BASE + T_PISO
    y0, y1 = D / 2 - 215, D / 2 - 45
    put(a, box(-110, 110, y0, y1, zc0, zc0 + 100).cut(box(-107, 107, y0 + 3, y1 - 3, zc0 + 3, zc0 + 98)), "caixa_ip65", COR["caixa"])
    ym = (y0 + y1) / 2
    put(a, box(-100, 100, y0 + 8, y1 - 8, zc0 + 3, zc0 + 6), "placa_montagem", COR["petg"], label="Placa de montagem interna", cat="impresso", mat="PETG")
    put(a, box(-95, -40, ym - 14, ym + 14, zc0 + 8, zc0 + 21), "esp32_s3", COR["preto"], label="ESP32-S3-DevKitC-1U (antena externa)", cat="comprado")
    for i in range(3):
        put(a, box(-95 + 22 * i, -80 + 22 * i, ym - 60, ym - 40, zc0 + 8, zc0 + 20), "driver_tmc2209", COR["pcb_azul"], label="Driver TMC2209", cat="comprado")
    for sy in (-1, 1):
        put(a, box(20, 90, ym + sy * 45 - 15, ym + sy * 45 + 15, zc0 + 8, zc0 + 22), "esc_60a", COR["vermelho"], label="ESC brushless 60-80 A", cat="comprado")
    put(a, box(-30, 0, ym + 40, ym + 70, zc0 + 8, zc0 + 33), "rele_k1", COR["preto"], label="Relé automotivo 40 A (K1)", cat="comprado")
    put(a, box(-95, -60, ym + 35, ym + 75, zc0 + 8, zc0 + 22), "porta_fusiveis", COR["preto"], label="Porta-fusíveis", cat="comprado")
    for i in range(3):
        put(a, box(-25, 15, ym - 30 + 22 * i, ym - 12 + 22 * i, zc0 + 8, zc0 + 18), "conversor_buck", COR["pcb_azul"], label="Conversor buck", cat="comprado")
    put(a, box(-50, -32, ym + 20, ym + 35, zc0 + 8, zc0 + 14), "receptor_433", COR["pcb_verde"], label="Receptor 433 MHz RXB6 (controle remoto)", cat="comprado")
    put(a, cyl_z(9, zc0 + 8, zc0 + 40, 75, ym - 70), "capacitor_1000uf", COR["preto"], label="Capacitor 1000 µF / 35 V", cat="comprado")
    for sx in (-1, 1):
        put(a, box(sx * 110 - 18, sx * 110 + 18, -D / 2 + 50, -D / 2 + 80, zc0, zc0 + 14), "diodo_ideal", COR["pcb_azul"], label="Módulo diodo ideal ≥30 A", cat="comprado")
    put(a, box(-25, 25, -D / 2 + 140, -D / 2 + 170, zc0, zc0 + 18), "chave_eletronica", COR["pcb_azul"], label="Chave eletrônica anti-faísca ≥60 A (liga/desliga)", cat="comprado")
    # rodas de transporte Ø125, pés
    reg("suporte_roda", "Suporte da roda de transporte (Al 4 mm)", "laser", "Alumínio 5052, 4 mm")
    reg("roda_transporte", "Roda Ø125 x 24 com rolamentos 608 (patins inline)", "comprado", "PU")
    reg("eixo_roda_transporte", "Eixo da roda de transporte Ø8 x 60 (parafuso de ombro)", "usinado", "Aço")
    for sx in (-1, 1):
        put(a, ch_suporte_roda(), "suporte_roda", COR["alu"], ploc((sx * (PX + P / 2) + (0 if sx > 0 else -4), -150, Z_BASE + T_PISO), (0, 1, 0), (1, 0, 0)))
        put(a, tube_x(62.5, 11, -12, 12).edges().fillet(4), "roda_transporte", COR["borracha"], tr(sx * (W / 2 + 15), -150, 62.5))
        put(a, cyl_x(4, 0, 45) if sx > 0 else cyl_x(4, -45, 0), "eixo_roda_transporte", COR["aco"], tr(sx * (PX + P / 2), -150, 62.5))
        put(a, cyl_z(16, 0, 6, sx * 105, Y_PE).union(cyl_z(4, 6, Z_BASE, sx * 105, Y_PE)), "pe_borracha", COR["borracha"],
            label="Pé de borracha M8 regulável", cat="comprado")
    fechos(a, Z1 - 12)
    # conectores entre o controle e o lançador
    reg("suporte_conectores", "Suporte dos conectores entre andares", "impresso", "PETG")
    for sx in (-1, 1):
        put(a, imp_suporte_conectores(), "suporte_conectores", COR["petg"], tr(sx * (PX - 22), -PY + 40, Z1 - 30))


def montar_roda(a, lado):
    """Roda de lançamento (gira). Origem no centro, eixo ao longo de x.
    lado=+1: roda de cima (polia em +x, disco de sinal em -x); -1: o contrário."""
    reg("nucleo_roda", "Núcleo da roda Ø134 x 32", "impresso", "PETG / ASA / PA-CF")
    reg("banda_roda", "Banda de rodagem TPU Ø150 x 40", "impresso", "TPU 95A")
    reg("disco_inercia", "Disco de inércia Ø120 (aço 3 mm)", "laser", "Aço 1020, 3 mm")
    reg("eixo_roda", "Eixo da roda Ø12 x 140 com chato", "usinado", "Aço 1045 retificado")
    reg("colar_12", "Colar de trava Ø12", "comprado", "Aço")
    reg("polia_roda", "Polia HTD 3M 20 dentes, furo 12, 15 mm", "comprado", "Alumínio")
    reg("disco_sinal", "Disco de sinal (2 ímãs)", "impresso", "PETG")
    rx = ploc((0, 0, 0), (0, 1, 0), (1, 0, 0))
    put(a, imp_nucleo_roda(), "nucleo_roda", COR["petg"], rx)
    put(a, imp_banda_tpu(), "banda_roda", COR["tpu"], rx)
    put(a, ch_disco_inercia(), "disco_inercia", COR["aco"], ploc((16, 0, 0), (0, 1, 0), (1, 0, 0)))
    put(a, ch_disco_inercia(), "disco_inercia", COR["aco"], ploc((-19, 0, 0), (0, 1, 0), (1, 0, 0)))
    for x, y, _ in furos_anel(50, 6, 4.4, 0):
        put(a, cyl_x(2, -21, 21, x, y).union(cyl_x(3.5, 19, 22, x, y)).union(cyl_x(3.5, -22, -19, x, y)),
            "parafuso_m4_roda", COR["aco"], label="Parafuso M4 x 45 + porca autotravante", cat="comprado")
    x0, x1 = (-64, 70) if lado > 0 else (-70, 64)
    put(a, cyl_x(6, x0, x1).intersect(box(x0 - 1, x1 + 1, -7, 5.0, -7, 7)), "eixo_roda", COR["aco"])
    for sx in (-1, 1):
        put(a, tube_x(11, 6, 19.5, 28.5) if sx > 0 else tube_x(11, 6, -28.5, -19.5), "colar_12", COR["aco"])
    s = 1 if lado > 0 else -1
    put(a, polia_htd(12), "polia_roda", COR["alu"], ploc((s * (PL_OUT + 2), 0, 0), (0, 1, 0), (s, 0, 0)))
    put(a, imp_disco_sinal(), "disco_sinal", COR["petg_laranja"], ploc((-s * (PL_OUT + 2) - (8 if s > 0 else 0), 0, 0), (0, 1, 0), (1, 0, 0)))


def correia(p1, p2, x0, x1):
    r = POLIA_DP / 2
    ext = cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(casco(circulos([(p1[0], p1[1], r + 1.5), (p2[0], p2[1], r + 1.5)], 48))).close().extrude(x1 - x0)
    inn = cq.Workplane("YZ", origin=(x0 - 1, 0, 0)).polyline(casco(circulos([(p1[0], p1[1], r), (p2[0], p2[1], r)], 48))).close().extrude(x1 - x0 + 2)
    return ext.cut(inn)


def montar_tilt(a):
    """Tudo que inclina. Origem no pivô; x lateral, y (=u) frente, z (=v) cima."""
    reg("placa_lateral", "Placa lateral da cabeça (Al 6 mm)", "laser", "Alumínio 6061, 6 mm")
    for sx in (-1, 1):
        put(a, ch_lateral(), "placa_lateral", COR["alu"], ploc((PL_IN if sx > 0 else -PL_OUT, 0, 0), (0, 1, 0), (1, 0, 0)))
    reg("espacador_placas", "Espaçador entre placas M5 x 90", "comprado", "Alumínio")
    for u, v in ESPACADORES:
        put(a, tube_x(5, 2.6, -PL_IN, PL_IN, u, v), "espacador_placas", COR["alu"])
    reg("mancal_kfl001", "Mancal KFL001 (Ø12)", "comprado", "Zamak / aço")
    for lado in (1, -1):
        for sx in (-1, 1):
            put(a, kfl001(), "mancal_kfl001", COR["motor_sino"], ploc((sx * PL_IN, NIP, lado * WC), (0, 0, 1), (-sx, 0, 0)))
    for lado, nome in ((1, "roda_sup"), (-1, "roda_inf")):
        r = cq.Assembly(name=nome, loc=tr(0, NIP, lado * WC))
        montar_roda(r, lado)
        a.add(r)
    # motores entre as placas, eixo invertido atravessando a placa até a polia
    reg("motor_roda", "Motor brushless outrunner 4250, 400-500 KV (eixo invertido)", "comprado", "")
    reg("motor_roda_sino", "Sino do motor (gira)", "visual", "")
    reg("polia_motor", "Polia HTD 3M 20 dentes, furo 5, 15 mm", "comprado", "Alumínio")
    reg("correia_htd", "Correia HTD 3M 9 mm fechada", "comprado", "Borracha / fibra")
    xm, est, sino, eixo = motor_4250()
    for (u, v), s, vr, comp in ((MOT_A, 1, WC, CORREIA_A), (MOT_B, -1, -WC, CORREIA_B)):
        lm = ploc((s * PL_IN, u, v), (0, 1, 0), (-s, 0, 0))
        put(a, xm.union(est).union(eixo), "motor_roda", COR["motor"], lm)
        put(a, sino, "motor_roda_sino", COR["motor_sino"], lm)
        put(a, polia_htd(5), "polia_motor", COR["alu"], ploc((s * (PL_OUT + 2), u, v), (0, 1, 0), (s, 0, 0)))
        x0, x1 = (PL_OUT + 4, PL_OUT + 13) if s > 0 else (-PL_OUT - 13, -PL_OUT - 4)
        put(a, correia((u, v), (NIP, vr), x0, x1), "correia_htd", COR["correia"], label=f"Correia HTD {comp:.0f}-3M-9", variante=True)
    PECAS["correia_htd"]["label"] = f"Correia HTD 3M 9 mm fechada ({CORREIA_A:.0f}-3M-9 e {CORREIA_B:.0f}-3M-9)"
    reg("tampa_correia_sup", "Tampa da correia da roda de cima", "impresso", "PETG")
    reg("tampa_correia_inf", "Tampa da correia da roda de baixo", "impresso", "PETG")
    put(a, imp_tampa_correia(1), "tampa_correia_sup", COR["petg"])
    put(a, imp_tampa_correia(-1), "tampa_correia_inf", COR["petg"])
    # sensores Hall (lado oposto à polia, de frente para o disco de sinal)
    reg("suporte_hall", "Suporte do sensor Hall", "impresso", "PETG")
    for lado in (1, -1):
        sxs = -1 if lado > 0 else 1          # lado do disco de sinal
        cv = lado * WC
        sup, sen = imp_suporte_hall(), box(12, 15, -17, -13, -2, 2)
        if sxs < 0:
            sup, sen = sup.mirror("YZ"), sen.mirror("YZ")
        loc = tr(sxs * PL_OUT, NIP, cv)
        put(a, sup, "suporte_hall", COR["petg"], loc)
        put(a, sen, "sensor_hall", COR["preto"], loc, label="Sensor Hall A3144 (módulo)", cat="comprado")
    # pivô: semi-eixos (o de -x leva a manivela) e colares
    reg("semi_eixo", "Semi-eixo do tilt Ø8 (lado +x 50 mm; lado -x 65 mm com chato na ponta)", "usinado", "Aço retificado")
    reg("colar_8", "Colar de trava Ø8", "comprado", "Aço")
    put(a, cyl_x(4, 37, 87), "semi_eixo", COR["aco"])
    put(a, cyl_x(4, X_MAN - 2, -37).cut(box(X_MAN - 3, X_MAN + 8, 3.05, 5, -5, 5)), "semi_eixo", COR["aco"], variante=True)
    for xa, xb in ((36, 45), (51, 60), (-45, -36), (-60, -51)):
        put(a, tube_x(8, 4, xa, xb), "colar_8", COR["aco"])
    reg("manivela_tilt", "Manivela do tilt (Al 6 mm)", "laser", "Alumínio 6061, 6 mm")
    put(a, ch_manivela(), "manivela_tilt", COR["alu"], ploc((X_MAN, 0, 0), (0, 1, 0), (1, 0, 0)))
    mu, mv = MANIVELA
    pino = (cyl_x(3, X_ATU + 9, X_MAN, mu, mv)                    # ombro Ø6 no rasgo da porca
            .union(cyl_x(2.5, X_MAN, X_MAN + 10, mu, mv))         # rosca M5 pela manivela
            .union(cyl_x(4.6, X_MAN + 6, X_MAN + 10, mu, mv).cut(cyl_x(2.5, X_MAN + 5, X_MAN + 11, mu, mv))))   # porca
    put(a, pino, "pino_manivela", COR["aco"], label="Pino da manivela: parafuso de ombro Ø6 x 6, M5 + porca", cat="comprado")
    # berço, funil, trilhos, servo, carenagens das rodas
    reg("berco", "Berço da bola", "impresso", "PETG")
    put(a, imp_berco(), "berco", COR["petg_laranja"])
    reg("funil_cabeca", "Funil da cabeça (84x140 -> Ø78)", "impresso", "PETG")
    put(a, imp_funil(), "funil_cabeca", COR["petg"])
    reg("trilho_guia", "Trilho-guia da bola Ø8 x 215 (vareta de alumínio)", "comprado", "Alumínio")
    for sx in (-1, 1):
        put(a, cyl_y(4, -40, 175, x=sx * 20, z=-31.7), "trilho_guia", COR["alu"])
    reg("suporte_trilho", "Suporte dos trilhos", "impresso", "PETG")
    put(a, imp_suporte_trilho(), "suporte_trilho", COR["petg"])
    reg("servo", "Servo rápido 20-25 kg·cm, ≤ 0,07 s/60° (tamanho padrão, como o DS3225)", "comprado", "")
    put(a, servo_ds3225(), "servo", COR["preto"], tr(0, *SERVO_EIXO))
    reg("suporte_servo", "Suporte do servo", "impresso", "PETG")
    put(a, imp_suporte_servo(), "suporte_servo", COR["petg"])
    reg("braco_empurrador", "Braço do empurrador", "impresso", "PETG + ponta TPU")
    put(a, imp_braco_empurrador(), "braco_empurrador", COR["petg_laranja"])
    reg("carenagem_roda_sup", "Carenagem da roda de cima", "impresso", "PETG / ASA")
    reg("carenagem_roda_inf", "Carenagem da roda de baixo", "impresso", "PETG / ASA")
    put(a, imp_carenagem_roda(1), "carenagem_roda_sup", COR["petg"])
    put(a, imp_carenagem_roda(-1), "carenagem_roda_inf", COR["petg"])
    put(a, bola(), "bola_berco", COR["bola"], label="Bola no berço", cat="visual")
    put(a, cyl_z(0.01, 0, 0.02), "alvo_manivela", COR["latao"], tr(X_ATU, MANIVELA[0], MANIVELA[1]), label="(referência)", cat="visual")


def montar_pan(a, tilt_deg=0.0):
    """Tudo que gira. Origem em (0, YA, 0) do mundo."""
    reg("plataforma", "Plataforma giratória (Al 4 mm)", "laser", "Alumínio 5052/6061, 4 mm")
    put(a, ch_plataforma(), "plataforma", COR["alu"], tr(0, 0, Z_PLAT - T_PLAT))
    reg("garfo", "Garfo do tilt (Al 6 mm)", "laser", "Alumínio 6061, 6 mm")
    reg("cantoneira_garfo", "Cantoneira de alumínio 40x40x3 x 60", "comprado", "Alumínio")
    reg("mancal_kfl08", "Mancal KFL08 (Ø8)", "comprado", "Zamak / aço")
    for sx in (-1, 1):
        x0 = YOKE_IN if sx > 0 else -YOKE_IN - YOKE_T
        put(a, ch_garfo(), "garfo", COR["alu"], ploc((x0, 0, Z_PLAT), (0, 1, 0), (1, 0, 0)))
        put(a, kfl08(), "mancal_kfl08", COR["motor_sino"], ploc((sx * (YOKE_IN + YOKE_T), 0, ZP), (0, 0, 1), (sx, 0, 0)))
        xv = YOKE_IN - 3
        ang = box(xv, xv + 3, -30, 30, Z_PLAT, Z_PLAT + 40).union(box(xv - 37, xv + 3, -30, 30, Z_PLAT, Z_PLAT + 3))
        put(a, ang if sx > 0 else ang.mirror("YZ"), "cantoneira_garfo", COR["alu"])
    # pino do giro (no braço +x)
    put(a, cyl_z(3, Z_PLAT - T_PLAT, Z_FUSO_PAN - 9, PAN_BRACO, 0).union(cyl_z(5, Z_PLAT, Z_PLAT + 1.5, PAN_BRACO, 0)),
        "pino_giro", COR["aco"], label="Pino do giro M6 x 30 (parafuso de ombro)", cat="comprado")
    # atuador do tilt: NEMA17 com fuso de 100 mm deitado ao longo de u, preso no garfo -x;
    # a porca corre no fuso e o rasgo dela recebe o pino da manivela
    at = cq.Assembly(name="atuador_tilt")
    put(at, imp_suporte_motor_tilt(), "suporte_motor_tilt", COR["petg"], label="Suporte do motor do tilt (no garfo)", cat="impresso", mat="PETG")
    reg("motor_tilt", "NEMA17 com fuso Tr8x2 integrado 100 mm (tilt; passo de 2 mm, não volta sozinho)", "comprado", "")
    put(at, nema17(40, 0.1), "motor_tilt", COR["motor"], ploc((X_ATU, U_MOTOR_TILT, Z_FUSO_TILT), (1, 0, 0), (0, -1, 0)))
    put(at, cyl_y(4, U_MOTOR_TILT - 100, U_MOTOR_TILT, x=X_ATU, z=Z_FUSO_TILT), "fuso_tilt", COR["aco"], label="Fuso Tr8x2 (parte do motor)", cat="visual")
    a.add(at)
    t = math.radians(tilt_deg)
    mu, mv = MANIVELA
    ue = mu * math.cos(t) - mv * math.sin(t)
    pt = cq.Assembly(name="porca_tilt", loc=tr(X_ATU, ue, Z_FUSO_TILT))
    reg("bloco_porca_tilt", "Bloco da porca do tilt (rasgo para o pino da manivela)", "impresso", "PETG")
    put(pt, imp_bloco_porca_tilt(), "bloco_porca_tilt", COR["petg_laranja"])
    a.add(pt)
    tl = cq.Assembly(name="tilt", loc=tr(0, 0, ZP) * rotx(tilt_deg))
    montar_tilt(tl)
    a.add(tl)


def montar_lancador(a, pan_deg, tilt_deg):
    reg("chapa_base_lancador", "Base do andar do lançador (Al 4 mm)", "laser", "Alumínio 5052/6061, 4 mm")
    put(a, ch_base_lancador(), "chapa_base_lancador", COR["alu"], tr(0, 0, Z1))
    put(a, tube_z(75, 40, Z1 + T_BASE_LANC, Z1 + T_BASE_LANC + LAZY_H, 0, YA), "lazy_susan", COR["aco"],
        label="Rolamento lazy susan redondo Ø150 (6\")", cat="comprado", mat="Aço")
    zp0, zp1 = Z1 + T_BASE_LANC, Z2
    postes(a, zp0, zp1, "poste_lancador", f"Poste do andar do lançador (perfil 20x20, {zp1 - zp0:.0f} mm)")
    # quadro do topo (perfis 20x20) e cantoneiras
    reg("perfil_topo_lado", f"Travessa lateral do topo (perfil 20x20, {2 * PY - P:.0f} mm)", "perfil", "Alumínio 20x20 canal 6")
    reg("perfil_topo_frente", f"Travessa frente/trás do topo (perfil 20x20, {2 * PX - P:.0f} mm)", "perfil", "Alumínio 20x20 canal 6")
    zc = Z2 - P / 2
    for sx in (-1, 1):
        put(a, perfil2020(2 * PY - P), "perfil_topo_lado", COR["perfil"], cq.Location(V(sx * PX, -(PY - P / 2), zc), V(1, 0, 0), -90))
    for sy in (-1, 1):
        put(a, perfil2020(2 * PX - P), "perfil_topo_frente", COR["perfil"], cq.Location(V(-(PX - P / 2), sy * PY, zc), V(0, 1, 0), 90))
    reg("cantoneira_2020", "Cantoneira 20x20 para perfil canal 6", "comprado", "Alumínio")
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, box(-9, 9, -9, 9, 0, 18), "cantoneira_2020", COR["alu"], tr(sx * (PX - 19), sy * (PY - 19), Z2 - P - 18))
    # acionamento do giro: NEMA17 com fuso, deitado ao longo de y no lado +x; porca com rasgo no pino da plataforma
    reg("motor_giro", "NEMA17 com fuso Tr8x8 integrado 100 mm (giro)", "comprado", "")
    lm = ploc((PAN_BRACO, Y_MOTOR_GIRO, Z_FUSO_PAN), (1, 0, 0), (0, 1, 0))
    put(a, nema17(40, 0.1), "motor_giro", COR["motor"], lm)
    put(a, cyl_y(4, Y_MOTOR_GIRO + 2, Y_MOTOR_GIRO + 100, x=PAN_BRACO, z=Z_FUSO_PAN), "fuso_giro", COR["aco"], label="Fuso Tr8x8 (parte do motor)", cat="visual")
    put(a, imp_suporte_motor_giro(), "suporte_motor_giro", COR["petg"], tr(PAN_BRACO, Y_MOTOR_GIRO, Z1 + T_BASE_LANC),
        label="Suporte do motor do giro", cat="impresso", mat="PETG")
    put(a, imp_mancal_fuso(), "mancal_fuso_giro", COR["petg"], tr(PAN_BRACO, Y_MANCAL_GIRO, Z1 + T_BASE_LANC),
        label="Mancal da ponta do fuso do giro (rolamento 608)", cat="impresso", mat="PETG")
    put(a, imp_bloco_porca_giro(), "bloco_porca_giro", COR["petg_laranja"], tr(PAN_BRACO, YA + PAN_BRACO * math.sin(math.radians(pan_deg)), Z_FUSO_PAN),
        label="Bloco da porca do giro (rasgo para o pino)", cat="impresso", mat="PETG")
    put(a, box(PAN_BRACO + 16, PAN_BRACO + 36, YA - 30, YA - 10, Z1 + T_BASE_LANC, Z1 + T_BASE_LANC + 12), "microchave", COR["preto"],
        label="Microchave fim de curso (referência do giro)", cat="comprado")
    # painel traseiro: tela 3,5", liga/desliga e emergência
    reg("painel_traseiro", "Painel traseiro (tela, liga/desliga, emergência)", "impresso", "PETG / ASA")
    yp = -PY - P / 2 + 2
    put(a, imp_painel_traseiro(), "painel_traseiro", COR["grafite"], tr(0, yp, Z_PAINEL))
    put(a, box(-46, 46, yp - 1, yp + 12, Z_PAINEL + 22, Z_PAINEL + 82), "tela_touch", COR["tela_lcd"],
        label="Tela touch 3,5\" IPS com ESP32-S3 (controle sem app)", cat="comprado")
    zb = Z_PAINEL + 52
    put(a, cyl_y(20, yp - 24, yp - 12, x=-X_BOTAO, z=zb).union(cyl_y(14, yp - 12, yp - 4, x=-X_BOTAO, z=zb))
        .union(cyl_y(11, yp - 4, yp + 40, x=-X_BOTAO, z=zb)),
        "botao_emergencia", COR["vermelho"], label="Botão de emergência cogumelo 22 mm 1NA+1NF", cat="comprado")
    put(a, cyl_y(13, yp - 10, yp - 4, x=X_BOTAO, z=zb).union(cyl_y(11, yp - 4, yp + 30, x=X_BOTAO, z=zb)),
        "botao_liga", COR["aco"], label="Botão liga/desliga 22 mm com retenção e anel de LED", cat="comprado")
    put(a, cyl_y(9, yp - 13, yp - 10, x=X_BOTAO, z=zb), "botao_liga_led", COR["led_verde"], label="Anel de LED", cat="visual")
    # semáforo na frente, preso à travessa da frente
    reg("semaforo", "Caixa do semáforo com pala", "impresso", "PETG / ASA preto")
    reg("difusor", "Difusor do semáforo", "impresso", "PETG natural (translúcido)")
    ys = D / 2 - T_CAR - 1
    put(a, imp_semaforo(), "semaforo", COR["grafite"], tr(0, ys, Z_SEMAFORO))
    for i, cor in enumerate(("led_vermelho", "led_amarelo", "led_verde")):
        put(a, imp_difusor(), "difusor", COR[cor], tr(42 - 42 * i, ys, Z_SEMAFORO))
    put(a, box(-60, 60, ys - 22, ys - 20, Z_SEMAFORO - 12, Z_SEMAFORO + 12), "leds_ws2812", COR["pcb_verde"],
        label="LEDs WS2812B (3 grupos de 4)", cat="comprado")
    # antenas nas laterais, perto do topo de trás
    reg("suporte_antena", "Suporte da antena", "impresso", "PETG")
    for sx, comp, base, label in ((-1, 175, "antena_433", "Antena 433 MHz articulada SMA (controle remoto)"),
                                  (1, 120, "antena_wifi", "Antena Wi-Fi 2,4 GHz articulada SMA (app)")):
        sup = imp_suporte_antena()
        put(a, sup if sx > 0 else sup.mirror("YZ"), "suporte_antena", COR["petg"], tr(sx * (PX + P / 2), -PY + P / 2, Z_ANTENA),
            espelho=sx < 0)
        xe = sx * W / 2                                       # face externa da carenagem
        sma = cyl_x(3.2, PX + P / 2, W / 2).union(cyl_x(6, W / 2, W / 2 + 3))
        put(a, (sma if sx > 0 else sma.mirror("YZ")).translate((0, Y_ANTENA, Z_ANTENA)), "conector_sma", COR["aco"],
            label="Conector SMA de painel + cabo U.FL", cat="comprado")
        d = V(sx * 0.42, -0.25, 0.87).normalized()
        c0 = V(xe + sx * 15, Y_ANTENA, Z_ANTENA)              # articulação da antena
        haste = cq.Workplane(cq.Plane(origin=c0, xDir=d.cross(V(0, 0, 1)).normalized(), normal=d)).circle(5).extrude(comp)
        base_ = cyl_x(5, min(xe + sx * 3, xe + sx * 12), max(xe + sx * 3, xe + sx * 12), Y_ANTENA, Z_ANTENA)
        put(a, haste.union(base_).union(cq.Workplane("XY").sphere(6).translate(c0)), base, COR["preto"], label=label, cat="comprado")
    # alça telescópica atrás (recolhida)
    reg("alca_luva", "Alça telescópica: tubo externo", "comprado", "Alumínio")
    reg("alca_haste", "Alça telescópica: tubo interno", "comprado", "Alumínio")
    reg("alca_pegador", "Alça telescópica: pegador", "comprado", "Plástico")
    reg("abracadeira_alca", "Abraçadeira da alça", "impresso", "PETG")
    ya_ = -PY - P / 2 - 29
    for sx in (-1, 1):
        put(a, tube_z(10, 8.5, Z1 + 20, Z2 - 10, sx * (PX - 20), ya_), "alca_luva", COR["preto"])
        put(a, cyl_z(8, Z2 - 10, Z3 + 18, sx * (PX - 20), ya_), "alca_haste", COR["alu"])
        for zc_ in Z_ALCA:
            ab = imp_abracadeira_alca()
            put(a, ab if sx > 0 else ab.mirror("YZ"), "abracadeira_alca", COR["petg"], tr(sx * PX, -PY - P / 2, zc_), espelho=sx < 0)
    put(a, cyl_x(11, -125, 125, ya_, Z3 + 30).union(cyl_x(13, -70, 70, ya_, Z3 + 30)), "alca_pegador", COR["preto"])
    fechos(a, Z2 - 12)
    reg("pino_guia_topo", "Pino-guia Ø10 do alimentador (no canal da travessa)", "impresso", "PETG")
    for x, y, _ in PINOS_TOPO:
        put(a, imp_pino_guia_topo(), "pino_guia_topo", COR["petg"], tr(x, y, Z2))
    put(a, imp_suporte_conectores(), "suporte_conectores", COR["petg"], tr(PX - 34, -PY + 42, Z2 - 30))
    # giro (com a cabeça)
    pan = cq.Assembly(name="pan", loc=tr(0, YA, 0) * rotz(pan_deg))
    montar_pan(pan, tilt_deg)
    a.add(pan)


def montar_alimentador(a):
    reg("chapa_alimentador", "Base do alimentador (Al 3 mm)", "laser", "Alumínio 5052, 3 mm")
    put(a, ch_alimentador(), "chapa_alimentador", COR["alu"], tr(0, 0, Z2))
    z1 = Z2 + T_ALIM
    postes(a, z1, Z3 - T_ARO, "poste_alimentador", f"Poste do alimentador (perfil 20x20, {Z3 - T_ARO - z1:.0f} mm)")
    reg("aro_topo", "Aro do topo (assento do cesto, Al 3 mm)", "laser", "Alumínio 5052, 3 mm")
    put(a, ch_aro_topo(), "aro_topo", COR["alu"], tr(0, 0, Z3 - T_ARO))
    reg("rampa_alimentador", "Rampa do fundo do alimentador (1/4)", "impresso", "PETG")
    for q in imp_rampas():
        put(a, q, "rampa_alimentador", COR["petg"], tr(0, 0, z1), variante=True)
    ax, ay = AGIT_C
    put(a, tube_z(AGIT_R, 12, 0, 0.5, ax, ay).cut(cyl_z(39, -1, 2, 0, YA)), "deslizante_ptfe", COR["pvc"], tr(0, 0, z1),
        label="Folha de PTFE/UHMW 0,5 mm sob o disco", cat="comprado", mat="PTFE")
    reg("rotor_agitador", "Rotor do agitador (disco Ø220 + cúpula)", "impresso", "PETG")
    put(a, imp_rotor_agitador(), "rotor_agitador", COR["petg_laranja"], tr(ax, ay, z1 + 0.5))
    reg("capuz_saida", "Capuz sobre o furo de saída", "impresso", "PETG")
    put(a, imp_capuz(), "capuz_saida", COR["petg"], tr(ax, ay, z1))
    reg("motor_agitador", "Motor de passo NEMA17 34 mm (agitador)", "comprado", "")
    put(a, nema17(34, 24), "motor_agitador", COR["motor"], tr(ax, ay, Z2))
    reg("flange_tubo", "Flange do tubo de queda", "impresso", "PETG")
    put(a, imp_flange_tubo(), "flange_tubo", COR["petg"], tr(0, YA, Z2))
    reg("tubo_queda", f"Tubo de queda PVC DN75 x {Z2 - 4 - TUBE_BOTTOM:.0f}", "comprado", "PVC esgoto DN75")
    put(a, tube_z(37.5, 35.8, TUBE_BOTTOM, Z2 - 4, 0, YA), "tubo_queda", COR["pvc"])
    put(a, cyl_x(9, 0, 45, 0, 0), "sensor_tubo", COR["preto"], tr(37.5, YA, Z2 - 90),
        label="Sensor infravermelho E18-D80NK (tubo)", cat="comprado")


def montar_cesto(aberto):
    c = cq.Assembly(name="cesto_aberto" if aberto else "cesto_dobrado")
    w0, d0 = CESTO_BASE
    reg("dobradica_cesto", "Dobradiça do cesto (fixa no aro)", "impresso", "PETG")
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(c, imp_dobradica_cesto(), "dobradica_cesto", COR["petg"], tr(sx * w0 / 2, sy * d0 / 2, Z3))
    if aberto:
        w1, d1 = CESTO_TOPO
        z0, z1 = Z3 + 14, Z3 + CESTO_H
        e = 16                                                 # tela 8 mm para dentro das varetas
        ext = cq.Workplane("XY", origin=(0, 0, z0)).rect(w0 - e, d0 - e).workplane(offset=z1 - z0).rect(w1 - e, d1 - e).loft()
        inn = (cq.Workplane("XY", origin=(0, 0, z0 - 0.01)).rect(w0 - e - 2, d0 - e - 2).workplane(offset=z1 - z0 + 0.02)
               .rect(w1 - e - 2, d1 - e - 2).loft())
        put(c, ext.cut(inn), "tela_cesto", COR["malha"], label="Tela do cesto: 4 painéis de tela de PVC costurados", cat="comprado", mat="Tela de PVC/poliéster")
        reg("vareta_cesto", "Vareta do cesto (alumínio Ø8, ponta de baixo amassada e furada)", "comprado", "Alumínio Ø8")
        for sx in (-1, 1):
            for sy in (-1, 1):
                p0 = V(sx * w0 / 2, sy * d0 / 2, z0)
                p1 = V(sx * w1 / 2, sy * d1 / 2, z1)
                n = (p1 - p0).normalized()
                a0, a1 = p0 + n * 10, p1 - n * 6                   # sai acima das orelhas da dobradiça, entra 5 mm no canto
                vara = cq.Workplane(cq.Plane(origin=a0, xDir=n.cross(V(0, 0, 1)).normalized(), normal=n)).circle(4).extrude((a1 - a0).Length)
                put(c, vara, "vareta_cesto", COR["aco"])
        reg("aro_cesto", "Aro de cima do cesto (varetas Ø8)", "comprado", "Alumínio Ø8")
        for sy in (-1, 1):
            put(c, cyl_x(4, -w1 / 2 + 6, w1 / 2 - 6, sy * d1 / 2, z1), "aro_cesto", COR["preto"])
        for sx in (-1, 1):
            put(c, cyl_y(4, -d1 / 2 + 6, d1 / 2 - 6, x=sx * w1 / 2, z=z1), "aro_cesto", COR["preto"])
        reg("canto_cesto", "Canto de cima do cesto (2 + 2 espelhados)", "impresso", "PETG")
        for sx in (-1, 1):
            for sy in (-1, 1):
                k = imp_canto_cesto()
                if sx < 0:
                    k = k.mirror("YZ")
                if sy < 0:
                    k = k.mirror("XZ")
                put(c, k, "canto_cesto", COR["petg"], tr(sx * w1 / 2, sy * d1 / 2, z1), espelho=sx * sy < 0)
    else:
        put(c, caixa_arred(w0, d0, Z3 + 5, Z3 + 30, 14), "cesto_dobrado_pacote", COR["malha"], label="Cesto dobrado (tela + varetas)", cat="visual")
    return c


def montar_bolas():
    b = cq.Assembly(name="bolas")
    reg("bola_tenis", "Bola de tênis", "visual", "")
    camadas = [(IN_W - 90, IN_D - 90, Z3 + 50), (IN_W - 20, IN_D - 10, Z3 + 112), (IN_W + 60, IN_D + 70, Z3 + 174)]
    for k, (ww, dd, zz) in enumerate(camadas):
        nx, ny = int(ww // 70), int(dd // 70)
        for i in range(nx):
            for j in range(ny):
                x = -ww / 2 + 35 + i * (ww - 70) / max(1, nx - 1) + (12 if k % 2 else 0)
                y = -dd / 2 + 35 + j * (dd - 70) / max(1, ny - 1)
                put(b, bola(), "bola_tenis", COR["bola"], tr(x, y, zz))
    return b


def montar_carenagem(base, lanc, alim):
    for nome, z0, z1, alvo in (("car_base", Z_BASE - 2, Z1 - 1, base), ("car_lancador", None, None, lanc), ("car_alimentador", Z2 + 1, Z3, alim)):
        g = cq.Assembly(name=nome)
        if nome == "car_lancador":
            put(g, car_lancador(), "carenagem_lancador", COR["carenagem"], label="Carenagem do andar do lançador", cat="carenagem", mat="A definir (molde injetado, termoformado, ABS/PETG ou ACM)")
        elif nome == "car_base":
            put(g, car_base(), "carenagem_base", COR["grafite"], label="Carenagem do andar de controle", cat="carenagem", mat="A definir")
            put(g, box(-89, 89, -D / 2, -D / 2 + T_CAR, Z_BASE + 13, Z1 - 16), "tampa_baterias", COR["preto"],
                label="Tampa das baterias", cat="carenagem", mat="A definir")
        else:
            put(g, casca(z0, z1), "carenagem_alimentador", COR["grafite"], label="Carenagem do alimentador", cat="carenagem", mat="A definir")
        alvo.add(g)


# ----------------------------------------------------------------------------
def construir(pan_deg=0.0, tilt_deg=15.0, carenagem=True, cesto="aberto", bolas=True):
    """cesto: 'aberto', 'dobrado' ou 'ambos' (o visualizador alterna)."""
    PECAS.clear()
    _contador.clear()
    raiz = cq.Assembly(name="lancador")
    base = cq.Assembly(name="andar_base")
    montar_base(base)
    lanc = cq.Assembly(name="andar_lancador")
    montar_lancador(lanc, pan_deg, tilt_deg)
    alim = cq.Assembly(name="andar_alimentador")
    montar_alimentador(alim)
    if carenagem:
        montar_carenagem(base, lanc, alim)
    for g in (base, lanc, alim):
        raiz.add(g)
    if cesto in ("aberto", "ambos"):
        raiz.add(montar_cesto(True))
    if cesto in ("dobrado", "ambos"):
        raiz.add(montar_cesto(False))
    if bolas and cesto != "dobrado":
        raiz.add(montar_bolas())
    return raiz


if __name__ == "__main__":
    import time
    t0 = time.time()
    m = construir()
    print("peças distintas:", len(PECAS), "instâncias:", sum(p["qtd"] for p in PECAS.values()), "tempo: %.1fs" % (time.time() - t0))
    print("motores:", [round(c, 1) for c in MOT_A], [round(c, 1) for c in MOT_B])
