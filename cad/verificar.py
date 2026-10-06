"""Verificação de interferências: cabeça (pan/tilt) contra partes fixas em várias posições,
e todas as peças entre si na posição neutra."""
import sys, itertools, time
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import lancador as M

IGNORAR = {  # pares que se tocam/encaixam de propósito (prefixos)
    frozenset(["eixo_roda", "parafuso_m4_roda"]),
}

def walk(a, parent=cq.Location(), path=()):
    loc = parent * a.loc
    p = path + (a.name,)
    if a.obj is not None:
        sh = a.obj.val() if isinstance(a.obj, cq.Workplane) else a.obj
        yield p, sh.moved(loc)
    for c in a.children:
        yield from walk(c, loc, p)

def vol(s1, s2):
    op = BRepAlgoAPI_Common(s1.wrapped, s2.wrapped)
    op.Build()
    if not op.IsDone():
        return -1
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(op.Shape(), g)
    return g.Mass()

def base(name):
    return name.split("__")[0]

def check(pan, tilt, todos=False, limiar=2.0):
    m = M.construir(pan, tilt)
    itens = []
    for p, sh in walk(m):
        movel = "pan" in p
        bb = sh.BoundingBox()
        itens.append((p[-1], movel, sh, bb, p))
    achados = []
    for (n1, m1, s1, b1, p1), (n2, m2, s2, b2, p2) in itertools.combinations(itens, 2):
        if not todos and m1 == m2:
            continue
        if b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin or b1.zmax < b2.zmin or b2.zmax < b1.zmin:
            continue
        if frozenset([base(n1), base(n2)]) in IGNORAR or "correia_gt2" in (base(n1), base(n2)):
            continue
        if base(n1).startswith("bola_tenis") or base(n2).startswith("bola_tenis"):
            continue
        v = vol(s1, s2)
        if v > limiar or v < 0:
            achados.append((v, n1, n2))
    return sorted(achados, reverse=True)

if __name__ == "__main__":
    poses = [(0, 0), (30, 15), (30, -15), (-30, 15), (-30, -15), (0, 15), (0, -15)]
    t0 = time.time()
    r = check(0, 0, todos=True)
    print("== todas as peças, posição neutra: %d interferências (%.0fs)" % (len(r), time.time() - t0))
    for v, a, b in r:
        print("   %10.1f mm3  %s  x  %s" % (v, a, b))
    for pan, tilt in poses[1:]:
        t0 = time.time()
        r = check(pan, tilt)
        print("== pan %+d tilt %+d: %d interferências cabeça x fixo (%.0fs)" % (pan, tilt, len(r), time.time() - t0))
        for v, a, b in r:
            print("   %10.1f mm3  %s  x  %s" % (v, a, b))


def check_bola_e_atuador(tilt):
    """Caminho da bola (queda pelo tubo, berço -> nip -> saída) e atuador x módulo inclinado."""
    import math
    m = M.construir(0, tilt)
    itens = [(p, sh) for p, sh in walk(m)]
    t = math.radians(tilt)
    esferas = []
    for z in (990, 950, 900, 850, 800, 760, M.Z_PIVOT + 5):
        esferas.append(("queda z=%d" % z, cq.Solid.makeSphere(M.BALL_R - 0.5, cq.Vector(0, M.PAN_Y, z))))
    for u in (10, 40, 70, 100, 230, 280, 340):
        y = M.PAN_Y + u * math.cos(t)
        z = M.Z_PIVOT + u * math.sin(t)
        esferas.append(("rolando u=%d" % u, cq.Solid.makeSphere(M.BALL_R - 0.5, cq.Vector(0, y, z))))
    ignorar = ("bola_", "banda_roda", "trilho_guia", "berco__", "bola_tenis")
    achados = []
    for nome, esf in esferas:
        bb = esf.BoundingBox()
        for p, sh in itens:
            n = p[-1]
            if any(n.startswith(i) for i in ignorar):
                continue
            b2 = sh.BoundingBox()
            if bb.xmax < b2.xmin or b2.xmax < bb.xmin or bb.ymax < b2.ymin or b2.ymax < bb.ymin or bb.zmax < b2.zmin or b2.zmax < bb.zmin:
                continue
            v = vol(esf, sh)
            if v > 1:
                achados.append((nome, n, round(v, 1)))
    at = [(p, sh) for p, sh in itens if "atuador_tilt" in p]
    tl = [(p, sh) for p, sh in itens if "tilt" in p]
    for (p1, s1) in at:
        for (p2, s2) in tl:
            v = vol(s1, s2)
            if v > 2:
                achados.append(("atuador:" + p1[-1], p2[-1], round(v, 1)))
    return achados


if __name__ == "__main__":
    for tilt in (-15, 0, 15):
        r = check_bola_e_atuador(tilt)
        print("== tilt %+d: caminho da bola / atuador: %d" % (tilt, len(r)))
        for x in r:
            print("   ", x)
