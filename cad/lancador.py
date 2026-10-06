"""
Lançador de bolas de tênis — modelo 3D paramétrico (CadQuery).

Unidades: mm. Eixos do mundo:
  x = largura (0 no centro), y = profundidade (+ para a frente), z = altura (0 no chão).

Hierarquia da montagem:
  lancador
   ├─ estrutura   (fixo: perfis, chapas, rodas de transporte, pés, alça, pan fixo)
   ├─ telas       (fixo: chapas perfuradas de proteção)
   ├─ eletronica  (fixo: caixa IP65, baterias, chave geral, emergência)
   ├─ hopper      (fixo: reservatório, agitador, tubo de queda)
   ├─ bolas       (bolas no hopper, só para visualização)
   └─ pan         (gira em torno do eixo vertical x=0, y=-60)
       ├─ atuador_tilt (articula no pé; o visualizador aponta o fuso para a porca)
       └─ tilt    (inclina em torno do eixo x, a 720 mm do chão)
           ├─ roda_sup / roda_inf (giram em torno do próprio eixo)
           └─ ...

Rodar:  python3 lancador.py   -> gera a pasta ../saida (ver exportar())
"""
import math
import cadquery as cq

V = cq.Vector

# ----------------------------------------------------------------------------
# PARÂMETROS (mude aqui e rode de novo)
# ----------------------------------------------------------------------------
W, D = 550.0, 450.0            # estrutura: largura x profundidade (externo)
P = 30.0                       # perfil 30x30
COL_X, COL_Y = W / 2 - P / 2, D / 2 - P / 2   # 260, 210 (centro das colunas)
Z0, ZTOP = 100.0, 1000.0       # base e topo da estrutura
ANEL = {"A": 130.0, "C": 460.0, "E": 730.0, "D": 1000.0}   # topo de cada anel
CROSS_X = 165.0                # travessas internas do anel C

PAN_Y = -35.0                  # eixo do pan (atrás do centro)
Z_PAN_PLATE = ANEL["C"]        # placa base do pan 460..464
T_PAN_PLATE = 4.0
LAZY_H = 10.0                  # lazy susan 464..474
T_PLAT = 4.0                   # plataforma 474..478
Z_PLAT_TOP = Z_PAN_PLATE + T_PAN_PLATE + LAZY_H + T_PLAT   # 478
Z_PIVOT = 720.0                # linha da bola / pivô do tilt
R_PLAT = 150.0

NIP = 160.0                    # pivô -> nip (para a frente)
WHEEL_D, WHEEL_W, GAP = 150.0, 40.0, 56.0
WC = (WHEEL_D + GAP) / 2       # 103: altura dos eixos das rodas
BALL_R = 33.5
PL_IN, PL_T = 45.0, 6.0        # placas laterais: face interna a +-45, 6 mm
PL_OUT = PL_IN + PL_T          # 51
YOKE_IN, YOKE_T = 62.0, 6.0    # garfo: 62..68

# motor da roda (classe 4250): costas do X-mount em x=140
MOT_D, MOT_L = 42.0, 50.0
MOT_BACK = 140.0
MOTPL_T, MOTPL_S = 5.0, 76.0   # placa do motor 76x76x5
STANDOFF_R = 40.0              # espaçadores a 40 mm do eixo (offset 28,3)

PAN_MOTOR_ANG, PAN_MOTOR_R = 40.0, 175.0
IDLER_R = 160.0
TILT_NUT = (-90.0, -70.0)      # porca no referencial do tilt (u, v)
ACT_PIVOT_Z = 490.0            # articulação do motor do tilt (z absoluto)

HOP_Z = ZTOP                   # placa base do hopper 1000..1003
HOP_T = 3.0
HOP_IN_X, HOP_IN_Y = 232.0, 182.0   # interno das paredes
HOP_WALL_H = 220.0
AGIT_C = (-76.0, PAN_Y + 57.0)  # centro do disco agitador (95 mm do furo de saída)
AGIT_ANG = math.degrees(math.atan2(PAN_Y - AGIT_C[1], 0.0 - AGIT_C[0]))  # direção do furo de saída
AGIT_R, AGIT_POCKET_R, AGIT_POCKET_D = 140.0, 95.0, 74.0
TUBE_BOTTOM = Z_PIVOT + 75.0   # fim do tubo de queda (795)

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
    "acrilico": _c(0.82, 0.92, 1.0, 0.16),
    "tela": _c(0.55, 0.57, 0.60, 0.28),
    "caixa": _c(0.62, 0.65, 0.70, 0.30),
    "bola": _c(0.82, 0.94, 0.20),
    "vermelho": _c(0.85, 0.10, 0.10),
    "amarelo": _c(0.98, 0.80, 0.10),
    "pcb_verde": _c(0.05, 0.40, 0.20),
    "pcb_azul": _c(0.10, 0.25, 0.65),
    "pvc": _c(0.92, 0.92, 0.90),
    "correia": _c(0.10, 0.10, 0.10),
}

# ----------------------------------------------------------------------------
# REGISTRO DE PEÇAS (metadados para lista de peças, exportação e visualizador)
# ----------------------------------------------------------------------------
PECAS = {}      # base -> dict(label, cat, mat, nota, qtd, shape)
_contador = {}

CAT = {
    "perfil": "Perfil de alumínio (cortado sob medida)",
    "laser": "Corte a laser",
    "impresso": "Impressão 3D",
    "usinado": "Usinagem / barra cortada",
    "comprado": "Comprado pronto",
    "visual": "Só visualização",
}


def reg(base, label, cat, mat="", nota="", arquivo=None):
    if base not in PECAS:
        PECAS[base] = dict(label=label, cat=cat, mat=mat, nota=nota, qtd=0,
                           shape=None, arquivo=arquivo)


def put(assy, shape, base, color, loc=None, **meta):
    """Adiciona uma instância de peça na (sub)montagem."""
    if base not in PECAS:
        reg(base, meta.get("label", base), meta.get("cat", "comprado"),
            meta.get("mat", ""), meta.get("nota", ""))
    n = _contador.get(base, 0) + 1
    _contador[base] = n
    name = f"{base}__{n}"
    PECAS[base]["qtd"] += 1
    if PECAS[base]["shape"] is None:
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
    return (cq.Workplane("XY", origin=(0, 0, z0)).center(x, y).circle(ro).circle(ri)
            .extrude(z1 - z0))


def tube_x(ro, ri, x0, x1, y=0.0, z=0.0):
    return (cq.Workplane("YZ", origin=(x0, 0, 0)).center(y, z).circle(ro).circle(ri)
            .extrude(x1 - x0))


def chapa(outline, t, furos=(), oblongos=(), recortes=()):
    """Chapa no plano XY local, espessura +Z. outline: Workplane 2D fechado.
    furos: (x, y, d); oblongos: (x, y, comprimento, largura, ang); recortes: Workplanes 2D."""
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


def ret_entalhe(w, h, n):
    """Retângulo com os 4 cantos recortados n x n."""
    a, b = w / 2, h / 2
    pts = [(-a + n, -b), (a - n, -b), (a - n, -b + n), (a, -b + n), (a, b - n), (a - n, b - n),
           (a - n, b), (-a + n, b), (-a + n, b - n), (-a, b - n), (-a, -b + n), (-a + n, -b + n)]
    return cq.Workplane("XY").polyline(pts).close()


def furos_anel(r, n, d, ang0=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(math.radians(ang0 + 360 * i / n)),
             cy + r * math.sin(math.radians(ang0 + 360 * i / n)), d) for i in range(n)]


# ----------------------------------------------------------------------------
# PEÇAS COMPRADAS (aproximações visuais com cotas de catálogo)
# ----------------------------------------------------------------------------
def perfil3030(comp):
    sk = (cq.Sketch().rect(30, 30)
          .push([(0, 13.9), (0, -13.9)]).rect(8.2, 2.2, mode="s")
          .push([(13.9, 0), (-13.9, 0)]).rect(2.2, 8.2, mode="s")
          .push([(0, 10.0), (0, -10.0)]).rect(14, 5.6, mode="s")
          .push([(10.0, 0), (-10.0, 0)]).rect(5.6, 14, mode="s")
          .reset().push([(0, 0)]).circle(3.4, mode="s"))
    return cq.Workplane("XY").placeSketch(sk).extrude(comp)


def nema17(L=48.0, eixo=24.0, d_eixo=5.0):
    """Face de montagem em z=0, corpo para -z, eixo para +z."""
    corpo = (cq.Workplane("XY").rect(42.3, 42.3).extrude(-L)
             .edges("|Z").chamfer(4))
    boss = cyl_z(11, 0, 2)
    eixo_s = cyl_z(d_eixo / 2, 2, eixo)
    return corpo.union(boss).union(eixo_s)


def kfl(L, J, W, H, flange, bore, d_furo, housing_d):
    """Mancal de flange 2 furos. Face de apoio em z=0, caixa para +z, furos ao longo de X."""
    fl = (cq.Workplane("XY").slot2D(L, W * 0.55, 0).extrude(flange)
          .union(cq.Workplane("XY").circle(W / 2).extrude(flange)))
    caixa = cyl_z(housing_d / 2, 0, H)
    s = fl.union(caixa)
    s = s.cut(cyl_z(bore / 2, -1, H + 1))
    s = s.cut(cq.Workplane("XY").pushPoints([(-J / 2, 0), (J / 2, 0)]).circle(d_furo / 2).extrude(flange))
    return s


def kfl001():
    return kfl(63, 48, 38, 16, 5.5, 12, 7, 30)


def kfl08():
    return kfl(48, 37, 27, 11.5, 4.5, 8, 4.5, 21)


def colar(d_eixo, od, w):
    return tube_z(od / 2, d_eixo / 2, 0, w)


def acopl_garra(d1=5, d2=12, D=25, L=30):
    s = tube_z(D / 2, d1 / 2, 0, L / 2 - 1).union(tube_z(D / 2, d2 / 2, L / 2 + 1, L))
    s = s.union(tube_z(D / 2 - 2, 3, L / 2 - 1, L / 2 + 1))
    return s


def motor_4250():
    """X-mount (costas) em z=0..4, estator, sino até z=54, eixo 5 mm até z=72."""
    xm = (cq.Workplane("XY").rect(48, 8).extrude(4)
          .union(cq.Workplane("XY").rect(8, 48).extrude(4)))
    estator = cyl_z(MOT_D / 2 - 1, 4, 14)
    sino = tube_z(MOT_D / 2, MOT_D / 2 - 3, 14, 4 + MOT_L).union(cyl_z(MOT_D / 2, 4 + MOT_L - 3, 4 + MOT_L))
    eixo = cyl_z(2.5, 4 + MOT_L, 4 + MOT_L + 18)
    return xm, estator, sino, eixo


def servo_ds3225():
    corpo = box(-20.25, 20.25, -20, 20, -10, 10)
    orelhas = box(-1.25, 1.25, -27, 27, -10, 10)
    eixo = cyl_x(3, 20.25, 26, y=10, z=0)
    return corpo.union(orelhas.translate((5, 0, 0))).union(eixo)


def bola():
    return cq.Workplane("XY").sphere(BALL_R)


def bateria_makita():
    base = box(-38, 38, -58, 58, 0, 45)
    topo = box(-38, 38, -58, 40, 45, 65).edges("|Y").fillet(6)
    return base, topo


def roda_transporte():
    pneu = tube_x(100, 40, -25, 25).edges().fillet(8)
    cubo = tube_x(40, 6.2, -22, 22)
    return pneu, cubo


# ----------------------------------------------------------------------------
# CHAPAS (corte a laser) — geometria local 2D + espessura
# ----------------------------------------------------------------------------
FUROS_ANEL = ([(x, sy * COL_Y, 6.5) for x in (-200, -100, 0, 100, 200) for sy in (-1, 1)] +
              [(sx * COL_X, y, 6.5) for y in (-120, 0, 120) for sx in (-1, 1)])


def ch_piso():
    furos = list(FUROS_ANEL)
    for x0 in (-62, 62):
        furos += [(x0 - 45, -200, 4.5), (x0 + 45, -200, 4.5), (x0 - 45, -90, 4.5), (x0 + 45, -90, 4.5)]
    return chapa(ret_entalhe(W, D, P), 3.0, furos)


def pan_motor_xy():
    a = math.radians(PAN_MOTOR_ANG)
    return PAN_MOTOR_R * math.sin(a), PAN_Y + PAN_MOTOR_R * math.cos(a)


def idlers_xy():
    out = []
    for da in (-7, 7):
        a = math.radians(PAN_MOTOR_ANG + da)
        out.append((IDLER_R * math.sin(a), PAN_Y + IDLER_R * math.cos(a)))
    return out


def ch_pan():
    mx, my = pan_motor_xy()
    ang = 90 - PAN_MOTOR_ANG          # direção radial no plano
    furos = list(FUROS_ANEL)
    furos += [(sx * CROSS_X, y, 6.5) for y in (-150, 0, 150) for sx in (-1, 1)]
    furos += [(0, PAN_Y, 80)]
    furos += furos_anel(135, 4, 5.5, 45, 0, PAN_Y)
    furos += [(x, y, 5.2) for x, y in idlers_xy()]
    furos += [(sx * 212, sy * 120, 60) for sx in (-1, 1) for sy in (-1, 1)] + [(0, 150, 60)]
    furos += [(-120, -175, 30)]
    obl = [(mx, my, 30, 24, ang)]
    obl += [(mx + dx, my + dy, 9.4, 3.4, ang) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]
    return chapa(ret_entalhe(W, D, P), T_PAN_PLATE, furos, obl)


def ch_hopper():
    ax, ay = AGIT_C
    furos = [(sx * COL_X, sy * COL_Y, 8.5) for sx in (-1, 1) for sy in (-1, 1)]
    furos += [(0, PAN_Y, 76)]
    furos += furos_anel(50, 3, 4.5, 30, 0, PAN_Y)
    furos += [(ax, ay, 23)] + [(ax + dx, ay + dy, 3.4) for dx in (-15.5, 15.5) for dy in (-15.5, 15.5)]
    furos += [(sx * (HOP_IN_X - 10), sy * (HOP_IN_Y - 10), 4.5) for sx in (-1, 1) for sy in (-1, 1)]
    return chapa(ret(W, D), HOP_T, furos)


def ch_plataforma():
    furos = [(0, 0, 80)]
    furos += furos_anel(125, 4, 5.5, 0)
    furos += furos_anel(R_PLAT - 6, 8, 4.5, 22.5)
    furos += [(sx * 42, sy * 15, 5.5) for sx in (-1, 1) for sy in (-1, 1)]
    furos += [(sx * 88, sy * 15, 5.5) for sx in (-1, 1) for sy in (-1, 1)]
    furos += [(sx * 30, TILT_NUT[0], 5.5) for sx in (-1, 1)]
    return chapa(cq.Workplane("XY").circle(R_PLAT), T_PLAT, furos)


LATERAL_PTS = [(-115, -110), (-75, -150), (200, -150), (215, -135), (215, 135), (200, 150),
               (-100, 150), (-115, 135)]


def ch_lateral():
    """Placa lateral do lançador, coordenadas (u=frente, v=cima) com origem no pivô."""
    furos = [(0, 0, 8.1),
             (NIP, WC, 16), (NIP, WC - 24, 7), (NIP, WC + 24, 7),
             (-90, 118, 6.5), (-40, -125, 6.5), (-105, -25, 6.5), (40, -140, 6.5),
             (-105, TILT_NUT[1], 5.5), (-75, TILT_NUT[1], 5.5),
             (-30, -44, 4.5), (20, -44, 4.5),
             (70, -43, 4.5),
             (-105, 56, 4.5), (-85, 56, 4.5),
             (-55, 30, 4.5), (55, 30, 4.5),
             (NIP - 81.5, WC, 4.5), (NIP - 76.6, WC + 27.9, 4.5), (NIP - 81.5, -WC, 4.5), (NIP - 76.6, -WC - 27.9, 4.5)]
    o = STANDOFF_R / math.sqrt(2)
    furos += [(NIP + dx, WC + dy, 5.5) for dx in (-o, o) for dy in (-o, o)]
    obl = [(NIP, -WC, 24, 16, 90), (NIP, -WC - 24, 15, 7, 90), (NIP, -WC + 24, 15, 7, 90)]
    obl += [(NIP + dx, -WC + dy, 13.5, 5.5, 90) for dx in (-o, o) for dy in (-o, o)]
    out = cq.Workplane("XY").polyline(LATERAL_PTS).close()
    return chapa(out, PL_T, furos, obl)


def ch_garfo():
    h = Z_PIVOT - Z_PLAT_TOP        # 242
    out = cq.Workplane("XY").center(0, h / 2).rect(80, h)
    s = out.extrude(YOKE_T).union(cq.Workplane("XY").center(0, h).circle(40).extrude(YOKE_T))
    for x, y, d in [(0, h, 12), (0, h - 18.5, 4.5), (0, h + 18.5, 4.5), (-15, 20, 5.5), (15, 20, 5.5),
                    (0, 120, 40)]:
        s = s.cut(cq.Workplane("XY").center(x, y).circle(d / 2).extrude(YOKE_T))
    return s


def ch_placa_motor():
    o = STANDOFF_R / math.sqrt(2)
    furos = [(dx, dy, 5.5) for dx in (-o, o) for dy in (-o, o)] + [(0, 0, 14)]
    obl = []
    for a in (45, 135, 225, 315):
        r = 19
        obl.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 9.4, 3.4, a))
    return chapa(ret(MOTPL_S, MOTPL_S), MOTPL_T, furos, obl)


def furo_d(t):
    """Furo em D para eixo Ø12 com chato: Ø12,1 com face plana a 5,05 mm do centro (11,1 entre faces)."""
    return (cq.Workplane("XY").circle(6.05).extrude(t)
            .intersect(cq.Workplane("XY").center(-0.5, 0).rect(11.1, 13).extrude(t)))


def ch_disco_inercia():
    s = cq.Workplane("XY").circle(60).extrude(3)
    s = s.cut(cq.Workplane("XY").pushPoints([(x, y) for x, y, _ in furos_anel(50, 6, 4.5, 0)])
              .circle(2.25).extrude(3))
    s = s.cut(furo_d(3))
    return s


def ch_suporte_eixo():
    pts = [(-195, 75), (-195, 195), (-232, 195), (-275, 140), (-275, 75)]
    out = cq.Workplane("XY").polyline(pts).close()
    return chapa(out, 4.0, [(-255, 100, 12.5), (-210, 120, 6.5), (-210, 180, 6.5)])


def ch_parede(comp):
    furos = [(sx * (comp / 2 - 10), sy * 80, 4.5) for sx in (-1, 1) for sy in (-1, 1)]
    return chapa(ret(comp, HOP_WALL_H), 3.0, furos)


def ch_tela(comp):
    h = ANEL["D"] - P - ANEL["C"] - T_PAN_PLATE        # 506
    zc_local = (ANEL["E"] - 15) - (ANEL["C"] + T_PAN_PLATE + h / 2)   # furos na altura do anel E
    furos = [(x, zc_local, 6.5) for x in (-comp / 2 + 45, 0, comp / 2 - 45)]
    s = chapa(ret(comp, h), 1.0, furos)
    return s


# ----------------------------------------------------------------------------
# PEÇAS IMPRESSAS
# ----------------------------------------------------------------------------
def imp_nucleo_roda():
    """Núcleo Ø134 x 32 (eixo Z local), 6 furos M4, 8 ranhuras para a banda."""
    s = cq.Workplane("XY").circle(67).extrude(32).translate((0, 0, -16))
    s = s.cut(cyl_z(6.6, -20, 20))
    s = s.cut(cq.Workplane("XY", origin=(0, 0, -16)).pushPoints(
        [(x, y) for x, y, _ in furos_anel(50, 6, 4.4, 0)]).circle(2.2).extrude(32))
    for i in range(8):
        g = box(-3, 3, 63.8, 68, -16, 16).rotate((0, 0, 0), (0, 0, 1), 360 * i / 8 + 22.5)
        s = s.cut(g)
    return s


def imp_banda_tpu():
    """Banda de rodagem: Ø134 interno, Ø150 externo, perfil côncavo R50 (4 mm)."""
    prof = (cq.Workplane("XY").moveTo(-20, 67).lineTo(20, 67).lineTo(20, 75)
            .threePointArc((0, 70.83), (-20, 75)).close())
    s = prof.revolve(360, (0, 0, 0), (1, 0, 0))
    # chavetas internas (encaixam nas ranhuras do núcleo), só na largura do núcleo
    for i in range(8):
        k = box(-16, 16, -2.8, 2.8, 63.9, 67.1).rotate((0, 0, 0), (1, 0, 0), 360 * i / 8 + 22.5)
        s = s.union(k)
    # deixa o eixo da banda em Z local (igual ao núcleo)
    return s.rotate((0, 0, 0), (0, 1, 0), 90)


def imp_disco_sinal():
    s = cq.Workplane("XY").circle(20).extrude(8)
    s = s.cut(furo_d(8))
    s = s.cut(cq.Workplane("XY", origin=(0, 0, 4.8)).pushPoints([(15, 0), (-15, 0)]).circle(3.1).extrude(3.2))
    s = s.cut(cyl_x(1.4, 0, 21, 0, 4))      # parafuso de trava M3
    return s


def imp_berco():
    """Berço sob a bola: entre as placas (x +-45), canaleta R37."""
    s = box(-45, 45, -45, 30, -55, -33)
    s = s.cut(cq.Workplane("XZ", origin=(0, 40, 0)).circle(37).extrude(90))
    s = s.cut(cyl_x(2.25, -46, 46, -30, -44)).cut(cyl_x(2.25, -46, 46, 20, -44))
    s = s.cut(cyl_y(4.1, -50, 40, x=20, z=-31.7)).cut(cyl_y(4.1, -50, 40, x=-20, z=-31.7))
    return s


def imp_funil():
    """Funil retangular (84 x 130) -> garganta Ø78; fica acima da bola."""
    def loft(dw, z_top, z_bot):
        return (cq.Workplane("XY", origin=(0, 0, z_top)).rect(84 + dw, 130 + dw)
                .workplane(offset=z_bot - z_top).circle(39 + dw / 2).loft())
    s = loft(5, 50, 36).cut(loft(0, 50.01, 35.99))
    for su in (-1, 1):
        for sx in (-1, 1):
            tab = box(sx * 40 if sx > 0 else -45, 45 if sx > 0 else -40, su * 55 - 7, su * 55 + 7, 22, 38)
            s = s.union(tab)
    s = s.cut(cyl_x(2.25, -46, 46, -55, 30)).cut(cyl_x(2.25, -46, 46, 55, 30))
    return s


def imp_suporte_trilho():
    s = box(-45, 45, 64, 76, -50, -36)
    for sx in (-1, 1):
        s = s.union(box(sx * 16 - 8, sx * 16 + 8, 64, 76, -36, -26))
    s = s.cut(cyl_y(4.1, 60, 80, x=20, z=-31.7)).cut(cyl_y(4.1, 60, 80, x=-20, z=-31.7))
    s = s.cut(cyl_x(2.25, -46, 46, 70, -43))
    return s


def imp_suporte_servo():
    s = box(-45, 45, -112, -78, 50, 62)
    s = s.cut(cyl_x(2.25, -46, 46, -105, 56)).cut(cyl_x(2.25, -46, 46, -85, 56))
    s = s.cut(box(-21, 21, -110, -80, 50, 53))
    return s


def imp_braco_empurrador():
    """Braço do servo: do eixo (u=-85, v=40) até a ponta atrás da bola."""
    ang = math.degrees(math.atan2(-42, 45))
    L = math.hypot(45, 42)
    arm = (cq.Workplane("YZ", origin=(26, 0, 0)).center(-85, 40)
           .rect(L, 12).extrude(3)
           .rotate((0, -85, 40), (1, -85, 40), ang)
           .translate((0, L / 2 * math.cos(math.radians(ang)), L / 2 * math.sin(math.radians(ang)))))
    hub = cyl_x(8, 26, 29, -85, 40)
    pad = box(-14, 29, -45, -38, -10, 8)
    return arm.union(hub).union(pad)


def imp_bloco_porca():
    u, v = TILT_NUT
    s = box(-45, 45, u - 22, u + 22, v - 12, v + 12)
    s = s.cut(cq.Workplane("XY", origin=(0, u, v - 13)).slot2D(30, 12, 90).extrude(26))
    s = s.cut(cyl_x(2.75, -46, 46, u - 15, v)).cut(cyl_x(2.75, -46, 46, u + 15, v))
    return s


def imp_carenagem(lado):
    """lado=+1: roda de cima (0..200°); -1: roda de baixo (160..360°). Fica entre as placas
    (x +-44,5) e aparafusa nelas por duas buchas transversais."""
    ri, ro = 80, 83
    a0, a1 = (0, 200) if lado > 0 else (160, 360)
    cv = WC * lado

    def p(r, a):
        return (NIP + r * math.cos(math.radians(a)), cv + r * math.sin(math.radians(a)))
    am = (a0 + a1) / 2
    wp = (cq.Workplane("YZ", origin=(-PL_IN + 0.5, 0, 0)).moveTo(*p(ro, a0)).threePointArc(p(ro, am), p(ro, a1))
          .lineTo(*p(ri, a1)).threePointArc(p(ri, am), p(ri, a0)).close())
    s = wp.extrude(2 * PL_IN - 1)
    for ang in (180, 160 if lado > 0 else 200):
        u, v = p(81.5, ang)
        s = s.union(tube_x(5, 2.25, -PL_IN + 0.5, PL_IN - 0.5, u, v))
    return s


def imp_gaiola_motor():
    """Gaiola sobre o sino do motor; 4 pés a 45° encostam na placa do motor (z=56 local)."""
    s = tube_z(27, 25, 0, 50)
    for i in range(6):
        s = s.cut(box(-4, 4, 20, 30, 10, 40).rotate((0, 0, 0), (0, 0, 1), 60 * i))
    for i in range(4):
        s = s.union(box(25.5, 34, -3, 3, 40, 56).rotate((0, 0, 0), (0, 0, 1), 45 + 90 * i))
    return s


def imp_aro():
    """Aro da plataforma (12 mm de largura x 10), 4 segmentos de 90°."""
    segs = []
    for i in range(4):
        seg = (cq.Workplane("XY").circle(R_PLAT).circle(R_PLAT - 12).extrude(10)
               .intersect(cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.pi / 2 - 1e-3), 300)])
                          .close().extrude(10)))
        seg = seg.rotate((0, 0, 0), (0, 0, 1), 90 * i)
        segs.append(seg)
    furos = [(x, y) for x, y, _ in furos_anel(R_PLAT - 6, 8, 4.5, 22.5)]
    out = []
    for seg in segs:
        out.append(seg.cut(cq.Workplane("XY").pushPoints(furos).circle(2.25).extrude(10)))
    return out


def imp_grampo_correia():
    s = box(-8, 8, 0, 6, 0, 16)
    return s


def imp_suporte_atuador():
    base = box(-47, 47, -15, 15, -12, -8)
    for sx in (-1, 1):
        base = base.union(box(sx * 40 - 3, sx * 40 + 3, -12, 12, -8, 12))
    base = base.cut(cyl_x(2.6, -50, 50, 0, 0))
    return base


def imp_rotor_agitador():
    """Disco Ø280 x 6 com 4 bolsões + cúpula cônica, cubo para eixo 5 mm (eixo Z local)."""
    s = cq.Workplane("XY").circle(AGIT_R).extrude(6)
    s = s.cut(cq.Workplane("XY").pushPoints([(x, y) for x, y, _ in furos_anel(AGIT_POCKET_R, 4, 0, AGIT_ANG)])
              .circle(AGIT_POCKET_D / 2).extrude(6))
    cone = (cq.Workplane("XY", origin=(0, 0, 6)).circle(56).workplane(offset=60).circle(8).loft())
    s = s.union(cone)
    s = s.cut(cyl_z(2.55, -1, 24))
    s = s.cut(cyl_x(1.4, 0, 60, 0, 14))
    return s


def imp_capuz():
    """Cobertura sobre o furo de saída: teto + parede externa, aberto embaixo e nas pontas."""
    a0, a1 = AGIT_ANG - 28, AGIT_ANG + 28

    def sector(ri, ro, z0, z1):
        def p(r, a):
            return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
        return (cq.Workplane("XY", origin=(0, 0, z0)).moveTo(*p(ro, a0)).threePointArc(p(ro, AGIT_ANG), p(ro, a1))
                .lineTo(*p(ri, a1)).threePointArc(p(ri, AGIT_ANG), p(ri, a0)).close().extrude(z1 - z0))
    teto = sector(55, 146, 78, 81)
    parede = sector(143, 146, 9, 78)
    return teto.union(parede)


def imp_rampas():
    """Fundo inclinado do hopper (15°) dividido em 4 quadrantes em torno do disco."""
    ax, ay = AGIT_C
    h = 57.0
    bloco = box(-HOP_IN_X, HOP_IN_X, -HOP_IN_Y, HOP_IN_Y, 0, h)
    zdisc = 6.5
    r0 = AGIT_R + 2
    r1 = r0 + (h - zdisc) / math.tan(math.radians(15))
    cone = (cq.Workplane("XY", origin=(ax, ay, zdisc)).circle(r0).workplane(offset=h - zdisc + 0.01)
            .circle(r1).loft())
    bloco = bloco.cut(cone).cut(cyl_z(r0, -1, zdisc + 0.01, ax, ay))
    # cantos dos postes
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * (HOP_IN_X - 20.2), sx * (HOP_IN_X + 10)))
            ya, yb = sorted((sy * (HOP_IN_Y - 20.2), sy * (HOP_IN_Y + 10)))
            bloco = bloco.cut(box(xa, xb, ya, yb, -1, h + 1))
    quads = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = bloco.intersect(box(min(ax, sx * 400), max(ax, sx * 400), min(ay, sy * 400), max(ay, sy * 400), -2, h + 2))
            quads.append(q)
    return quads


def imp_poste_canto():
    s = box(-10, 10, -10, 10, 0, HOP_WALL_H)
    s = s.cut(cyl_z(1.8, 0, 15))
    return s


def imp_flange_tubo():
    s = cyl_z(55, -4, 0).union(tube_z(42.5, 37.75, -15, -4))
    s = s.cut(cyl_z(36, -16, 1))
    s = s.cut(cq.Workplane("XY", origin=(0, 0, -4)).pushPoints(
        [(x, y) for x, y, _ in furos_anel(50, 3, 4.5, 30)]).circle(2.25).extrude(4))
    return s


def imp_berco_bateria():
    s = box(-50, 50, -65, 65, 0, 8)
    s = s.cut(box(-41, 41, -61, 70, 3, 8.1))
    s = s.cut(cq.Workplane("XY").pushPoints([(-45, -55), (45, -55), (-45, 55), (45, 55)]).circle(2.25).extrude(8))
    return s


def imp_console_emergencia():
    s = box(-35, 35, -45, 0, -55, 0).edges("|Y").fillet(5)
    s = s.cut(box(-31, 31, -41, -4, -51, -4))
    s = s.cut(cyl_y(11.2, -46, -40, x=0, z=-27))
    return s


def imp_abracadeira_alca():
    s = box(-15, 15, -24, 0, -13, 13)
    s = s.cut(cyl_z(10.2, -14, 14, 0, -10))
    return s


def imp_calibre():
    s = box(-30, 30, -10, 10, 0, 56).edges("|Z").fillet(3)
    s = s.cut(box(-20, 20, -11, 11, 10, 46))
    return s


def imp_suporte_hall():
    s = box(-8, 8, 0, 17, 0, 7).union(box(-8, 8, 13, 17, -13, 0))
    s = s.cut(cyl_y(3.6, -1, 18, 0, 3.5))
    return s


# ----------------------------------------------------------------------------
# GRUPOS
# ----------------------------------------------------------------------------
def montar_estrutura(a):
    reg("perfil_coluna", "Coluna (perfil 30x30, 900 mm)", "perfil", "Alumínio 30x30 canal 8")
    reg("perfil_travessa_490", "Travessa frente/trás (perfil 30x30, 490 mm)", "perfil", "Alumínio 30x30 canal 8")
    reg("perfil_travessa_390", "Travessa lateral (perfil 30x30, 390 mm)", "perfil", "Alumínio 30x30 canal 8")
    reg("perfil_travessa_interna", "Travessa interna do anel C (perfil 30x30, 390 mm)", "perfil", "Alumínio 30x30 canal 8")
    col = perfil3030(ZTOP - Z0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, col, "perfil_coluna", COR["perfil"], tr(sx * COL_X, sy * COL_Y, Z0))
    lx = W - 2 * P      # 490
    ly = D - 2 * P      # 390
    bx = perfil3030(lx)
    by = perfil3030(ly)
    for nome, zt in ANEL.items():
        zc = zt - P / 2
        for sy in (-1, 1):
            if nome == "E" and sy > 0:
                continue  # janela frontal
            put(a, bx, "perfil_travessa_490", COR["perfil"],
                cq.Location(V(-lx / 2, sy * COL_Y, zc), V(0, 1, 0), 90))
        for sx in (-1, 1):
            put(a, by, "perfil_travessa_390", COR["perfil"],
                cq.Location(V(sx * COL_X, -ly / 2, zc), V(1, 0, 0), -90))
    zc = ANEL["C"] - P / 2
    for sx in (-1, 1):
        put(a, by, "perfil_travessa_interna", COR["perfil"],
            cq.Location(V(sx * CROSS_X, -ly / 2, zc), V(1, 0, 0), -90))

    reg("chapa_piso", "Piso da base (Al 3 mm)", "laser", "Alumínio 5052, 3 mm")
    put(a, ch_piso(), "chapa_piso", COR["alu"], tr(0, 0, ANEL["A"]))
    reg("chapa_base_pan", "Placa base do pan (Al 4 mm)", "laser", "Alumínio 5052/6061, 4 mm")
    put(a, ch_pan(), "chapa_base_pan", COR["alu"], tr(0, 0, Z_PAN_PLATE))

    # lazy susan (parte fixa + parte girante aproximadas como um anel)
    reg("lazy_susan", "Rolamento lazy susan 300 mm", "comprado", "Aço")
    ls = tube_z(150, 110, 0, LAZY_H)
    put(a, ls, "lazy_susan", COR["aco"], tr(0, PAN_Y, Z_PAN_PLATE + T_PAN_PLATE))

    # motor do pan, polia e polias lisas
    mx, my = pan_motor_xy()
    reg("motor_pan", "Motor de passo NEMA17 48 mm (pan)", "comprado", "")
    put(a, nema17(48, 26), "motor_pan", COR["motor"], tr(mx, my, Z_PAN_PLATE))
    reg("polia_gt2_20", "Polia GT2 20 dentes, furo 5 mm", "comprado", "Alumínio")
    put(a, tube_z(8, 2.5, 0, 16).union(tube_z(6.4, 2.5, 4, 11)), "polia_gt2_20", COR["alu"],
        tr(mx, my, Z_PAN_PLATE + T_PAN_PLATE + 6))
    reg("polia_lisa", "Polia lisa (idler) GT2, furo 5 mm", "comprado", "Alumínio")
    for x, y in idlers_xy():
        put(a, tube_z(9, 2.5, 0, 10), "polia_lisa", COR["alu"], tr(x, y, Z_PLAT_TOP + 0.5))
        put(a, cyl_z(2.5, -T_PAN_PLATE - 3, 12), "parafuso_m5_idler", COR["aco"],
            tr(x, y, Z_PLAT_TOP), label="Parafuso M5 x 30 (eixo do idler)", cat="comprado")

    # rodas de transporte, eixo e suportes
    reg("suporte_eixo_roda", "Suporte do eixo das rodas (aço 4 mm)", "laser", "Aço 1020, 4 mm")
    for sx in (-1, 1):
        x0 = (W / 2) if sx > 0 else -(W / 2) - 4
        put(a, ch_suporte_eixo(), "suporte_eixo_roda", COR["aco"], ploc((x0, 0, 0), (0, 1, 0), (1, 0, 0)))
    reg("eixo_transporte", "Eixo das rodas de transporte Ø12 x 700", "usinado", "Aço")
    put(a, cyl_x(6, -350, 350, -255, 100), "eixo_transporte", COR["aco"])
    reg("roda_transporte", "Roda maciça Ø200 com rolamento", "comprado", "Borracha / PP")
    reg("roda_transporte_cubo", "Cubo da roda de transporte", "visual", "")
    pneu, cubo = roda_transporte()
    for sx in (-1, 1):
        put(a, pneu, "roda_transporte", COR["borracha"], tr(sx * 308, -255, 100))
        put(a, cubo, "roda_transporte_cubo", COR["motor_sino"], tr(sx * 308, -255, 100))

    # pés niveladores
    reg("pe_nivelador", "Pé nivelador articulado M8, haste 80 mm", "comprado", "Aço / borracha")
    pe = cyl_z(25, 0, 12).union(cyl_z(4, 12, Z0)).union(
        cq.Workplane("XY", origin=(0, 0, 60)).polygon(6, 14).extrude(6))
    for sx in (-1, 1):
        put(a, pe, "pe_nivelador", COR["borracha"], tr(sx * COL_X, COL_Y, 0))

    # alça telescópica
    reg("alca_haste", "Alça telescópica: haste Ø16", "comprado", "Alumínio")
    reg("alca_luva", "Alça telescópica: luva Ø20", "comprado", "Alumínio")
    reg("alca_pegador", "Alça telescópica: pegador", "comprado", "Plástico")
    reg("abracadeira_alca", "Abraçadeira da alça", "impresso", "PETG")
    for sx in (-1, 1):
        put(a, tube_z(10, 8.5, 430, 830, sx * 200, -235), "alca_luva", COR["preto"])
        put(a, cyl_z(8, 600, 1159, sx * 200, -235), "alca_haste", COR["alu"])
        for zc in (ANEL["C"] - 15, ANEL["E"] - 15):
            put(a, imp_abracadeira_alca(), "abracadeira_alca", COR["petg"], tr(sx * 200, -D / 2, zc))
    put(a, cyl_x(11, -215, 215, -235, 1170).union(cyl_x(13, -80, 80, -235, 1170)), "alca_pegador", COR["preto"])


def montar_telas(a):
    reg("tela_lateral", "Tela de proteção lateral (chapa perfurada 1 mm)", "laser", "Alumínio perfurado, 1 mm")
    reg("tela_traseira", "Tela de proteção traseira (chapa perfurada 1 mm)", "laser", "Alumínio perfurado, 1 mm")
    h = ANEL["D"] - P - ANEL["C"] - T_PAN_PLATE
    zc = ANEL["C"] + T_PAN_PLATE + h / 2
    lt = D - 2 * P
    for sx in (-1, 1):
        x0 = sx * (W / 2 - P) - (0 if sx > 0 else -0) - (1 if sx > 0 else 0)
        put(a, ch_tela(lt), "tela_lateral", COR["tela"],
            ploc((x0 if sx > 0 else -(W / 2 - P), 0, zc), (0, 1, 0), (1, 0, 0)))
    put(a, ch_tela(W - 2 * P - 2), "tela_traseira", COR["tela"],
        ploc((0, -(D / 2 - P), zc), (1, 0, 0), (0, 1, 0)))


def montar_eletronica(a):
    reg("caixa_ip65", "Caixa ABS IP65 ~300x200x130", "comprado", "ABS")
    cx = box(-145, 145, -100, 100, 270, 400).cut(box(-142, 142, -97, 97, 273, 397))
    put(a, cx, "caixa_ip65", COR["caixa"])
    reg("suporte_caixa", "Cantoneira de alumínio (fixa a caixa nas travessas)", "comprado", "Alumínio 40x40x3")
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, box(-2, 0, -15, 15, 320, 430).union(box(-2, 18, -15, 15, 427, 430)).mirror("YZ") if sx < 0
                else box(0, 2, -15, 15, 320, 430).union(box(-18, 2, -15, 15, 427, 430)),
                "suporte_caixa", COR["alu"], tr(sx * (CROSS_X - 15) + sx * 0, sy * 60, 0))
    # componentes internos
    put(a, box(-120, 120, -80, 80, 274, 277), "placa_montagem", COR["petg"],
        label="Placa de montagem interna", cat="impresso", mat="PETG")
    put(a, box(-110, -55, -10, 18, 280, 293), "esp32_s3", COR["preto"],
        label="ESP32-S3-DevKitC-1", cat="comprado")
    put(a, box(-115, -45, -70, -20, 278, 280), "placa_controle", COR["pcb_verde"],
        label="Placa de controle (perfurada)", cat="comprado")
    for i in range(3):
        put(a, box(-110 + 22 * i, -95 + 22 * i, -60, -40, 280, 292), "driver_tmc2209", COR["pcb_azul"],
            label="Driver TMC2209", cat="comprado")
    for sy in (-1, 1):
        put(a, box(10, 80, sy * 45 - 15, sy * 45 + 15, 278, 292), "esc_60a", COR["vermelho"],
            label="ESC brushless 60-80 A", cat="comprado")
    put(a, box(95, 125, -75, -45, 278, 303), "rele_k1", COR["preto"], label="Relé automotivo 40 A (K1)", cat="comprado")
    put(a, box(95, 130, 20, 75, 278, 293), "porta_fusiveis", COR["preto"], label="Porta-fusíveis", cat="comprado")
    for i in range(3):
        put(a, box(-40, 5, -35 + 25 * i, -13 + 25 * i, 278, 290),
            "conversor_buck", COR["pcb_azul"], label="Conversor buck", cat="comprado")
    put(a, cyl_z(9, 278, 310, 110, -10), "capacitor_1000uf", COR["preto"], label="Capacitor 1000 µF / 35 V", cat="comprado")
    # diodos ideais (ao lado das baterias)
    for sx in (-1, 1):
        put(a, box(sx * 140 - 20, sx * 140 + 20, -180, -150, 133, 148), "diodo_ideal", COR["pcb_azul"],
            label="Módulo diodo ideal ≥30 A", cat="comprado")
    # baterias e soquetes
    reg("bateria_makita", "Bateria Makita 18 V 5,0 Ah", "comprado", "")
    reg("bateria_makita_topo", "Bateria Makita (topo)", "visual", "")
    reg("soquete_makita", "Adaptador/soquete de bateria Makita 18 V", "comprado", "")
    reg("berco_bateria", "Berço do soquete de bateria", "impresso", "PETG")
    base, topo = bateria_makita()
    for sx in (-1, 1):
        x0, y0 = sx * 62, -145
        put(a, imp_berco_bateria(), "berco_bateria", COR["petg"], tr(x0, y0, ANEL["A"] + 3))
        put(a, box(-40, 40, -60, 60, 0, 22), "soquete_makita", COR["preto"], tr(x0, y0, ANEL["A"] + 6))
        put(a, base, "bateria_makita", COR["makita"], tr(x0, y0, ANEL["A"] + 28))
        put(a, topo, "bateria_makita_topo", COR["preto"], tr(x0, y0, ANEL["A"] + 28))
    # chave geral (pendurada sob o anel C, atrás)
    put(a, box(-25, 25, -40, 0, -50, 0), "chave_geral", COR["preto"], tr(-150, -D / 2, ANEL["C"] - P),
        label="Chave geral de bateria ≥100 A", cat="comprado")
    put(a, cyl_y(15, -55, -40, x=0, z=-25), "chave_geral_manopla", COR["vermelho"], tr(-150, -D / 2, ANEL["C"] - P),
        label="Manopla da chave geral", cat="visual")
    # botão de emergência
    put(a, imp_console_emergencia(), "console_emergencia", COR["amarelo"], tr(0, -D / 2, ZTOP - P),
        label="Console do botão de emergência", cat="impresso", mat="PETG/ASA amarelo")
    put(a, cyl_y(20, -66, -45, x=0, z=-27).union(cyl_y(11, -46, -44, x=0, z=-27)), "botao_emergencia",
        COR["vermelho"], tr(0, -D / 2, ZTOP - P),
        label="Botão de emergência cogumelo 22 mm 1NA+1NF", cat="comprado")


def montar_hopper(a):
    reg("chapa_base_hopper", "Placa base do hopper (Al 3 mm)", "laser", "Alumínio 5052, 3 mm")
    put(a, ch_hopper(), "chapa_base_hopper", COR["alu"], tr(0, 0, HOP_Z))
    z1 = HOP_Z + HOP_T
    reg("parede_hopper_frente", "Parede do hopper frente/trás 470x220", "laser", "Acrílico 3 mm ou PC 2 mm")
    reg("parede_hopper_lado", "Parede do hopper lateral 364x220", "laser", "Acrílico 3 mm ou PC 2 mm")
    zc = z1 + HOP_WALL_H / 2
    for sy in (-1, 1):
        put(a, ch_parede(2 * (HOP_IN_X + 3)), "parede_hopper_frente", COR["acrilico"],
            ploc((0, sy * HOP_IN_Y, zc), (1, 0, 0), (0, sy, 0)))
    for sx in (-1, 1):
        put(a, ch_parede(2 * HOP_IN_Y), "parede_hopper_lado", COR["acrilico"],
            ploc((sx * HOP_IN_X, 0, zc), (0, 1, 0), (sx, 0, 0)))
    reg("poste_canto_hopper", "Poste de canto do hopper", "impresso", "PETG")
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(a, imp_poste_canto(), "poste_canto_hopper", COR["petg"],
                tr(sx * (HOP_IN_X - 10), sy * (HOP_IN_Y - 10), z1))
    reg("rampa_hopper", "Rampa do fundo do hopper (1/4)", "impresso", "PETG")
    for q in imp_rampas():
        put(a, q, "rampa_hopper", COR["petg"], tr(0, 0, z1), variante=True)
    ax, ay = AGIT_C
    reg("deslizante_ptfe", "Folha de PTFE/UHMW 0,5 mm sob o disco", "comprado", "PTFE")
    ptfe = tube_z(AGIT_R, 12, 0, 0.5, ax, ay).cut(cyl_z(39, -1, 2, 0, PAN_Y))
    put(a, ptfe, "deslizante_ptfe", COR["pvc"], tr(0, 0, z1))
    reg("rotor_agitador", "Rotor do agitador (disco Ø280 + cúpula)", "impresso", "PETG")
    put(a, imp_rotor_agitador(), "rotor_agitador", COR["petg_laranja"], tr(ax, ay, z1 + 0.5))
    reg("capuz_saida", "Capuz sobre o furo de saída", "impresso", "PETG")
    put(a, imp_capuz(), "capuz_saida", COR["petg"], tr(ax, ay, z1))
    reg("motor_agitador", "Motor de passo NEMA17 34 mm (agitador)", "comprado", "")
    put(a, nema17(34, 24), "motor_agitador", COR["motor"], tr(ax, ay, HOP_Z))
    reg("flange_tubo", "Flange do tubo de queda", "impresso", "PETG")
    put(a, imp_flange_tubo(), "flange_tubo", COR["petg"], tr(0, PAN_Y, HOP_Z))
    reg("tubo_queda", "Tubo de queda PVC DN75", "comprado", "PVC esgoto DN75")
    put(a, tube_z(37.5, 35.8, TUBE_BOTTOM, HOP_Z - 4), "tubo_queda", COR["pvc"], tr(0, PAN_Y, 0))
    put(a, cyl_x(9, 0, 45, 0, 0), "sensor_tubo", COR["preto"], tr(37.5, PAN_Y, 900),
        label="Sensor infravermelho E18-D80NK (tubo)", cat="comprado")


def montar_bolas(a):
    """Bolas no hopper, empilhadas em camadas sobre o fundo inclinado — só visual."""
    ax, ay = AGIT_C
    z1 = HOP_Z + HOP_T
    topo = z1 + HOP_WALL_H - 4
    r = BALL_R

    def piso(x, y):
        d = math.hypot(x - ax, y - ay)
        ang = math.degrees(math.atan2(y - ay, x - ax))
        if d < 75:
            return 9e9                      # cúpula do agitador
        if d < 175 and abs((ang - AGIT_ANG + 180) % 360 - 180) < 40:
            return 9e9                      # capuz sobre o furo de saída
        if d < AGIT_R:
            return z1 + 6.5
        return z1 + 6.5 + (max(0.0, d - AGIT_R - 2) * math.tan(math.radians(15))
                           + r * (1 / math.cos(math.radians(15)) - 1) + 0.5)
    pos = []
    passo = 2 * r + 1.5
    for camada in range(4):
        off = (camada % 2) * passo / 2
        ys = [-HOP_IN_Y + r + 3 + off + j * passo for j in range(12)]
        xs = [-HOP_IN_X + r + 3 + off + i * passo for i in range(12)]
        for y in ys:
            for x in xs:
                if abs(x) > HOP_IN_X - r - 2 or abs(y) > HOP_IN_Y - r - 2:
                    continue
                if abs(x) > HOP_IN_X - 24 - r and abs(y) > HOP_IN_Y - 24 - r:
                    continue                # postes de canto
                z = piso(x, y) + r
                apoio = [p for p in pos if (x - p[0]) ** 2 + (y - p[1]) ** 2 < (2 * r) ** 2]
                for p in apoio:
                    z = max(z, p[2] + math.sqrt((2 * r) ** 2 - (x - p[0]) ** 2 - (y - p[1]) ** 2))
                if z + r > topo or z > 9e8:
                    continue
                if any((x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2 < (2 * r - 0.5) ** 2 for p in pos):
                    continue
                pos.append((x, y, z))
                if len(pos) >= 70:
                    break
            if len(pos) >= 70:
                break
    reg("bola_tenis", "Bola de tênis", "visual", "")
    b = bola()
    for x, y, z in pos:
        put(a, b, "bola_tenis", COR["bola"], tr(x, y, z))
    return len(pos)


def montar_roda(a, lado):
    """Roda de lançamento completa (gira). lado=+1 roda de cima (motor à direita),
    -1 roda de baixo (motor à esquerda). Origem: centro da roda; eixo ao longo de X."""
    s_motor = 1 if lado > 0 else -1
    reg("nucleo_roda", "Núcleo da roda Ø134 x 32", "impresso", "PETG / ASA / PA-CF")
    reg("banda_roda", "Banda de rodagem TPU Ø150 x 40", "impresso", "TPU 95A")
    reg("disco_inercia", "Disco de inércia Ø120 (aço 3 mm)", "laser", "Aço 1020, 3 mm")
    reg("eixo_roda", "Eixo da roda Ø12 x 128 com chato", "usinado", "Aço 1045 retificado")
    reg("colar_12", "Colar de trava Ø12", "comprado", "Aço")
    reg("acoplamento", "Acoplamento elástico tipo garra 5 x 12", "comprado", "Alumínio")
    reg("disco_sinal", "Disco de sinal (2 ímãs)", "impresso", "PETG")
    rx = ploc((0, 0, 0), (0, 1, 0), (1, 0, 0))  # Z local -> X
    put(a, imp_nucleo_roda(), "nucleo_roda", COR["petg"], rx)
    put(a, imp_banda_tpu(), "banda_roda", COR["tpu"], rx)
    put(a, ch_disco_inercia(), "disco_inercia", COR["aco"], ploc((16, 0, 0), (0, 1, 0), (1, 0, 0)))
    put(a, ch_disco_inercia(), "disco_inercia", COR["aco"], ploc((-19, 0, 0), (0, 1, 0), (1, 0, 0)))
    for x, y, _ in furos_anel(50, 6, 4.4, 0):
        put(a, cyl_x(2, -21, 21, x, y).union(cyl_x(3.5, 19, 22, x, y)).union(cyl_x(3.5, -22, -19, x, y)),
            "parafuso_m4_roda", COR["aco"], label="Parafuso M4 x 45 + porca autotravante", cat="comprado")
    x0, x1 = (-62, 66) if lado > 0 else (-66, 62)
    eixo = cyl_x(6, x0, x1).intersect(box(x0 - 1, x1 + 1, -7, 5.0, -7, 7))
    put(a, eixo, "eixo_roda", COR["aco"])
    for sx in (-1, 1):
        put(a, tube_x(11, 6, 19.5, 28.5) if sx > 0 else tube_x(11, 6, -28.5, -19.5), "colar_12", COR["aco"])
    ac = acopl_garra(d1=12, d2=5)
    if s_motor > 0:
        put(a, ac, "acoplamento", COR["alu"], ploc((PL_OUT + 2, 0, 0), (0, 1, 0), (1, 0, 0)))
        put(a, imp_disco_sinal(), "disco_sinal", COR["petg_laranja"], ploc((-PL_OUT - 10, 0, 0), (0, 1, 0), (1, 0, 0)))
    else:
        put(a, ac, "acoplamento", COR["alu"], ploc((-PL_OUT - 2, 0, 0), (0, 1, 0), (-1, 0, 0)))
        put(a, imp_disco_sinal(), "disco_sinal", COR["petg_laranja"], ploc((PL_OUT + 2, 0, 0), (0, 1, 0), (1, 0, 0)))


def montar_tilt(a):
    """Tudo que inclina. Coordenadas: origem no pivô; x lateral, y (=u) frente, z (=v) cima."""
    reg("placa_lateral", "Placa lateral do lançador (Al 6 mm)", "laser", "Alumínio 6061, 6 mm")
    for sx in (-1, 1):
        x0 = PL_IN if sx > 0 else -PL_OUT
        put(a, ch_lateral(), "placa_lateral", COR["alu"], ploc((x0, 0, 0), (0, 1, 0), (1, 0, 0)))
    reg("espacador_placas", "Espaçador entre placas M6 x 90", "comprado", "Alumínio")
    for u, v in [(-90, 118), (-40, -125), (-105, -25), (40, -140)]:
        put(a, tube_x(5, 3.2, -PL_IN, PL_IN, u, v), "espacador_placas", COR["alu"])
    # mancais das rodas (por dentro das placas)
    reg("mancal_kfl001", "Mancal KFL001 (Ø12)", "comprado", "Zamak / aço")
    for lado in (1, -1):
        for sx in (-1, 1):
            put(a, kfl001(), "mancal_kfl001", COR["motor_sino"],
                ploc((sx * PL_IN, NIP, lado * WC), (0, 0, 1), (-sx, 0, 0)))
    # rodas (sub-montagens que giram)
    for lado, nome in ((1, "roda_sup"), (-1, "roda_inf")):
        r = cq.Assembly(name=nome, loc=tr(0, NIP, lado * WC))
        montar_roda(r, lado)
        a.add(r)
    # motores, placas de motor, espaçadores, gaiolas
    reg("motor_roda", "Motor brushless outrunner classe 4250, 400-500 KV", "comprado", "")
    reg("motor_roda_sino", "Sino do motor (gira)", "visual", "")
    reg("placa_motor", "Placa do motor 76x76 (Al 5 mm)", "laser", "Alumínio 5052, 5 mm")
    reg("espacador_motor", "Espaçador do motor M5 x 89", "comprado", "Alumínio")
    reg("gaiola_motor", "Gaiola de proteção do motor", "impresso", "PETG")
    o = STANDOFF_R / math.sqrt(2)
    xm, est, sino, eixo = motor_4250()
    for lado in (1, -1):
        sx = 1 if lado > 0 else -1
        cv = lado * WC
        lm = ploc((sx * MOT_BACK, NIP, cv), (0, 1, 0), (-sx, 0, 0))
        put(a, xm.union(est).union(eixo), "motor_roda", COR["motor"], lm)
        put(a, sino, "motor_roda_sino", COR["motor_sino"], lm)
        put(a, ch_placa_motor(), "placa_motor", COR["alu"],
            ploc((sx * MOT_BACK if sx > 0 else -MOT_BACK - MOTPL_T, NIP, cv), (0, 1, 0), (1, 0, 0)))
        for du in (-o, o):
            for dv in (-o, o):
                x0, x1 = (PL_OUT, MOT_BACK) if sx > 0 else (-MOT_BACK, -PL_OUT)
                put(a, tube_x(5, 2.6, x0, x1, NIP + du, cv + dv), "espacador_motor", COR["alu"])
        put(a, imp_gaiola_motor(), "gaiola_motor", COR["petg"],
            ploc((sx * (MOT_BACK - 54 - 2), NIP, cv), (0, 1, 0), (sx, 0, 0)))
    # sensores Hall (lado oposto ao motor, de frente para o disco de sinal)
    reg("suporte_hall", "Suporte do sensor Hall", "impresso", "PETG")
    for lado in (1, -1):
        sxs = -1 if lado > 0 else 1
        cv = lado * WC
        sup = box(PL_OUT, 69, NIP - 8, NIP + 8, 22, 28).union(box(66, 69, NIP - 8, NIP + 8, 13, 28))
        sen = box(63, 66, NIP - 2, NIP + 2, 13, 17)
        if lado < 0:
            sup, sen = sup.mirror("XY"), sen.mirror("XY")
        if sxs < 0:
            sup, sen = sup.mirror("YZ"), sen.mirror("YZ")
        put(a, sup, "suporte_hall", COR["petg"], tr(0, 0, cv))
        put(a, sen, "sensor_hall", COR["preto"], tr(0, 0, cv), label="Sensor Hall A3144 (módulo)", cat="comprado")
    # pivô: semi-eixos e colares
    reg("semi_eixo", "Semi-eixo do tilt Ø8 x 45", "usinado", "Aço retificado")
    reg("colar_8", "Colar de trava Ø8", "comprado", "Aço")
    for sx in (-1, 1):
        put(a, cyl_x(4, 37, 80) if sx > 0 else cyl_x(4, -80, -37), "semi_eixo", COR["aco"])
        for xa, xb in ((36, 45), (51, 60)):
            put(a, tube_x(8, 4, xa, xb) if sx > 0 else tube_x(8, 4, -xb, -xa), "colar_8", COR["aco"])
    # berço, funil, trilhos, servo, porca, carenagens
    reg("berco", "Berço da bola", "impresso", "PETG")
    put(a, imp_berco(), "berco", COR["petg_laranja"])
    reg("funil_cabeca", "Funil da cabeça (84x130 -> Ø78)", "impresso", "PETG")
    put(a, imp_funil(), "funil_cabeca", COR["petg"])
    reg("trilho_guia", "Trilho-guia da bola Ø8 (vareta de alumínio)", "comprado", "Alumínio")
    for sx in (-1, 1):
        put(a, cyl_y(4, -40, 125, x=sx * 20, z=-31.7), "trilho_guia", COR["alu"])
    reg("suporte_trilho", "Suporte dos trilhos", "impresso", "PETG")
    put(a, imp_suporte_trilho(), "suporte_trilho", COR["petg"])
    reg("servo", "Servo DS3225 25 kg·cm", "comprado", "")
    put(a, servo_ds3225(), "servo", COR["preto"], tr(0, -95, 40))
    reg("suporte_servo", "Suporte do servo", "impresso", "PETG")
    put(a, imp_suporte_servo(), "suporte_servo", COR["petg"])
    reg("braco_empurrador", "Braço do empurrador", "impresso", "PETG + ponta TPU")
    put(a, imp_braco_empurrador(), "braco_empurrador", COR["petg_laranja"], tr(0, 0, 0))
    reg("bloco_porca", "Bloco da porca do tilt", "impresso", "PETG")
    put(a, imp_bloco_porca(), "bloco_porca", COR["petg"])
    reg("porca_tr8", "Porca de latão Tr8x8 com flange", "comprado", "Latão")
    u, v = TILT_NUT
    put(a, cyl_z(11, -2, 1.5).union(cyl_z(5.1, -14, 0)).cut(cyl_z(4, -15, 2)), "porca_tr8", COR["latao"], tr(0, u, v + 14))
    reg("carenagem_sup", "Carenagem da roda de cima", "impresso", "PETG / ASA")
    reg("carenagem_inf", "Carenagem da roda de baixo", "impresso", "PETG / ASA")
    put(a, imp_carenagem(1), "carenagem_sup", COR["petg"])
    put(a, imp_carenagem(-1), "carenagem_inf", COR["petg"])
    # bola no berço
    put(a, bola(), "bola_berco", COR["bola"], label="Bola no berço", cat="visual")
    # marcador da porca (para o visualizador)
    put(a, cyl_z(0.01, 0, 0.02), "alvo_porca", COR["latao"], tr(0, u, v), label="(referência)", cat="visual")


def montar_pan(a, tilt_deg=0.0):
    """Tudo que gira. Coordenadas: origem em (0, PAN_Y, 0) do mundo."""
    reg("plataforma", "Plataforma giratória Ø300 (Al 4 mm)", "laser", "Alumínio 5052/6061, 4 mm")
    put(a, ch_plataforma(), "plataforma", COR["alu"], tr(0, 0, Z_PLAT_TOP - T_PLAT))
    reg("aro_plataforma", "Aro da plataforma (1/4)", "impresso", "PETG")
    for seg in imp_aro():
        put(a, seg, "aro_plataforma", COR["petg"], tr(0, 0, Z_PLAT_TOP), variante=True)
    # correia (arcos presos ao aro)
    reg("correia_gt2", "Correia GT2 6 mm (aberta)", "comprado", "Borracha / fibra")
    for a1, a2 in ((PAN_MOTOR_ANG - 71, PAN_MOTOR_ANG - 11), (PAN_MOTOR_ANG + 11, PAN_MOTOR_ANG + 71)):
        span = a2 - a1
        arc = (cq.Workplane("XZ").moveTo(R_PLAT + 0.75, Z_PLAT_TOP + 4).rect(1.5, 6)
               .revolve(span, (0, 0, 0), (0, 1, 0)))
        arc = arc.rotate((0, 0, 0), (0, 0, 1), 90 - a2)
        put(a, arc, "correia_gt2", COR["correia"])
    reg("grampo_correia", "Grampo da correia", "impresso", "PETG")
    for ang in (PAN_MOTOR_ANG - 71, PAN_MOTOR_ANG + 71):
        put(a, imp_grampo_correia(), "grampo_correia", COR["petg"],
            cq.Location(V(R_PLAT * math.sin(math.radians(ang)), R_PLAT * math.cos(math.radians(ang)), Z_PLAT_TOP),
                        V(0, 0, 1), -ang))
    # garfo
    reg("garfo", "Garfo do tilt (Al 6 mm)", "laser", "Alumínio 6061, 6 mm")
    reg("cantoneira_garfo", "Cantoneira de alumínio 40x40x3 x 60", "comprado", "Alumínio")
    reg("mancal_kfl08", "Mancal KFL08 (Ø8)", "comprado", "Zamak / aço")
    for sx in (-1, 1):
        x0 = YOKE_IN if sx > 0 else -YOKE_IN - YOKE_T
        put(a, ch_garfo(), "garfo", COR["alu"], ploc((x0, 0, Z_PLAT_TOP), (0, 1, 0), (1, 0, 0)))
        xo = YOKE_IN + YOKE_T
        put(a, kfl08(), "mancal_kfl08", COR["motor_sino"],
            ploc((sx * xo, 0, Z_PIVOT), (0, 0, 1), (sx, 0, 0)))
        for lado in (-1, 1):   # cantoneira interna e externa
            xv = (YOKE_IN - 3) if lado < 0 else (YOKE_IN + YOKE_T)
            vert = box(xv, xv + 3, -30, 30, Z_PLAT_TOP, Z_PLAT_TOP + 40)
            hx0 = xv - 37 if lado < 0 else xv
            hor = box(hx0, hx0 + 40, -30, 30, Z_PLAT_TOP, Z_PLAT_TOP + 3)
            ang = vert.union(hor)
            if sx < 0:
                ang = ang.mirror("YZ")
            put(a, ang, "cantoneira_garfo", COR["alu"])
    # atuador do tilt (sub-montagem articulada)
    u, v = TILT_NUT
    reg("suporte_atuador", "Suporte articulado do motor do tilt", "impresso", "PETG")
    put(a, imp_suporte_atuador(), "suporte_atuador", COR["petg"], tr(0, u, ACT_PIVOT_Z))
    # ângulo do fuso para apontar para a porca na inclinação atual
    tr_ = math.radians(tilt_deg)
    nu = u * math.cos(tr_) - v * math.sin(tr_)
    nv = u * math.sin(tr_) + v * math.cos(tr_) + Z_PIVOT
    ang_at = -math.degrees(math.atan2(nu - u, nv - ACT_PIVOT_Z))
    at = cq.Assembly(name="atuador_tilt", loc=tr(0, u, ACT_PIVOT_Z) * rotx(ang_at))
    reg("motor_tilt", "NEMA17 com fuso Tr8x8 integrado 150 mm", "comprado", "")
    put(at, nema17(40, 0.1).translate((0, 0, 44)), "motor_tilt", COR["motor"])
    put(at, cyl_z(4, 46.1, 194), "fuso_tilt", COR["aco"], label="Fuso Tr8x8 (parte do motor)", cat="visual")
    put(at, cyl_x(2.5, -40, -33.5, 0, 0).union(cyl_x(2.5, 33.5, 40, 0, 0)).union(tube_z(34, 31, -6, 6)), "anel_articulacao", COR["petg"],
        label="Anel de articulação do motor do tilt", cat="impresso", mat="PETG")
    a.add(at)
    # tilt
    t = cq.Assembly(name="tilt", loc=tr(0, 0, Z_PIVOT) * rotx(tilt_deg))
    montar_tilt(t)
    a.add(t)


def construir(pan_deg=0.0, tilt_deg=0.0):
    PECAS.clear()
    _contador.clear()
    raiz = cq.Assembly(name="lancador")
    g = {}
    for nome in ("estrutura", "telas", "eletronica", "hopper", "bolas"):
        g[nome] = cq.Assembly(name=nome)
    montar_estrutura(g["estrutura"])
    montar_telas(g["telas"])
    montar_eletronica(g["eletronica"])
    montar_hopper(g["hopper"])
    montar_bolas(g["bolas"])
    pan = cq.Assembly(name="pan", loc=tr(0, PAN_Y, 0) * rotz(pan_deg))
    montar_pan(pan, tilt_deg)
    for nome in ("estrutura", "telas", "eletronica", "hopper", "bolas"):
        raiz.add(g[nome])
    raiz.add(pan)
    return raiz


if __name__ == "__main__":
    import time
    t0 = time.time()
    m = construir()
    print("peças distintas:", len(PECAS), "instâncias:", sum(p["qtd"] for p in PECAS.values()),
          "tempo: %.1fs" % (time.time() - t0))
