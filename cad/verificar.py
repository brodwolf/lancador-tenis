"""Confere folgas da versão 2 em todas as combinações de giro e inclinação:
cabeça × partes fixas, cabeça × garfo e atuadores, partes do giro × partes fixas, e o caminho da bola.
Depois confere todas as peças contra todas (sobreposição de volume) em 5 posições.

uso: python3 verificar.py            (18 posições + todas as peças em 5 posições)
     python3 verificar.py 12.5,30    (posições escolhidas: giro,inclinação)
"""
import itertools
import sys

import cadquery as cq

import lancador as M


def achatar(assy, loc=None, caminho=()):
    loc = loc * assy.loc if loc is not None else assy.loc
    caminho = caminho + (assy.name,)
    out = []
    if assy.obj is not None:
        sh = assy.obj.val() if hasattr(assy.obj, "val") else assy.obj
        out.append((assy.name, caminho, sh.moved(loc)))
    for ch in assy.children:
        out += achatar(ch, loc, caminho)
    return out


def base(nome):
    return nome.rsplit("__", 1)[0]


def grupo(itens, pred):
    shs = [s for n, c, s in itens if pred(n, c)]
    return cq.Compound.makeCompound(shs) if shs else None


def folga(a, b):
    if a is None or b is None:
        return float("nan")
    d = a.distance(b)
    if d < 1e-6:
        return -a.intersect(b).Volume()
    return d


CONTATO_PREVISTO = {"semi_eixo", "colar_8", "manivela_tilt", "pino_manivela"}   # passam pelo KFL08 / rasgo da porca


def checar(pan, tilt):
    m = M.construir(pan, tilt, carenagem=True, cesto="aberto", bolas=False)
    it = achatar(m)
    na_cabeca = lambda n, c: "tilt" in c
    no_giro = lambda n, c: "pan" in c and "tilt" not in c
    fixo = lambda n, c: "pan" not in c
    cab = grupo(it, na_cabeca)
    cab_sem_eixo = grupo(it, lambda n, c: na_cabeca(n, c) and base(n) not in CONTATO_PREVISTO)
    giro = grupo(it, lambda n, c: no_giro(n, c) and base(n) not in ("mancal_kfl08", "bloco_porca_tilt"))
    giro_todo = grupo(it, no_giro)
    alvos = {
        "tubo de queda": grupo(it, lambda n, c: base(n) == "tubo_queda"),
        "alimentador": grupo(it, lambda n, c: base(n) in ("chapa_alimentador", "motor_agitador", "sensor_tubo")),
        "carenagem": grupo(it, lambda n, c: c[1:2] == ("andar_lancador",) and "car_lancador" in c),
        "postes e travessas": grupo(it, lambda n, c: base(n) in ("poste_lancador", "perfil_topo_lado", "perfil_topo_frente", "cantoneira_2020")),
        "painel, semáforo, antenas, alça": grupo(it, lambda n, c: base(n) in ("painel_traseiro", "tela_touch", "botao_emergencia", "botao_liga",
                                                                           "semaforo", "leds_ws2812", "suporte_antena", "abracadeira_alca", "suporte_conectores", "bloco_pino", "pino_centragem", "pino_guia_topo")),
        "base do andar e giro": grupo(it, lambda n, c: fixo(n, c) and c[1:2] == ("andar_lancador",) and base(n) in (
            "chapa_base_lancador", "lazy_susan", "motor_giro", "fuso_giro", "suporte_motor_giro", "mancal_fuso_giro", "microchave")),
    }
    linhas = []
    for nome, alvo in alvos.items():
        linhas.append((f"cabeça × {nome}", folga(cab, alvo)))
    linhas.append(("cabeça × garfo, plataforma e atuador", folga(cab_sem_eixo, giro)))
    linhas.append(("pino da manivela × porca do tilt", folga(grupo(it, lambda n, c: base(n) == "pino_manivela"),
                                                          grupo(it, lambda n, c: base(n) == "bloco_porca_tilt"))))
    for nome in ("carenagem", "postes e travessas", "painel, semáforo, antenas, alça"):
        linhas.append((f"giro × {nome}", folga(giro_todo, alvos[nome])))
    linhas.append(("giro × fuso e motor do giro", folga(grupo(it, lambda n, c: no_giro(n, c) and base(n) != "pino_giro"),
                                                        grupo(it, lambda n, c: base(n) in ("motor_giro", "fuso_giro", "suporte_motor_giro", "mancal_fuso_giro", "bloco_porca_giro")))))
    # caminho da bola: do berço até antes das rodas, e da saída até a frente da carenagem
    t, p = M.math.radians(tilt), pan
    def trecho(u0, u1):
        c = cq.Workplane("XZ", origin=(0, u1, 0)).circle(M.BALL_R + 0.5).extrude(u1 - u0).val()
        loc = M.tr(0, M.YA, 0) * M.rotz(p) * M.tr(0, 0, M.ZP) * M.rotx(tilt)
        return c.moved(loc)
    guias = ("berco", "trilho_guia", "funil_cabeca", "braco_empurrador", "bola_berco", "suporte_trilho", "carenagem_roda_sup", "carenagem_roda_inf",
             "banda_roda", "nucleo_roda")
    linhas.append(("bola (berço → rodas) × cabeça", folga(trecho(5, M.NIP - 70), grupo(it, lambda n, c: na_cabeca(n, c) and base(n) not in guias))))
    linhas.append(("bola (saída) × carenagem e frente", folga(trecho(M.NIP + 45, 420), grupo(it, lambda n, c: fixo(n, c) and base(n) in (
        "carenagem_lancador", "semaforo", "difusor", "perfil_topo_frente", "poste_lancador")))))
    return linhas


# contatos previstos na checagem peça × peça (o fuso faz parte do motor; a haste da alça corre dentro da luva)
PREVISTO = {frozenset(p) for p in [("motor_giro", "fuso_giro"), ("motor_tilt", "fuso_tilt"),
                                   ("alca_haste", "alca_luva"), ("alca_haste", "alca_pegador")]}


def todas_as_pecas(pan, tilt):
    """Lista pares de peças que se sobrepõem (> 0,5 mm³) e peças com volume inválido."""
    it = achatar(M.construir(pan, tilt, carenagem=True, cesto="aberto", bolas=False))
    bbs = [(n, s, s.BoundingBox()) for n, c, s in it]
    problemas = [(f"{n}: volume inválido", 0) for n, s, b in bbs if s.Volume() <= 0]

    def perto(a, b):
        return not (a.xmax < b.xmin or b.xmax < a.xmin or a.ymax < b.ymin or b.ymax < a.ymin or a.zmax < b.zmin or b.zmax < a.zmin)
    for (na, sa, ba), (nb, sb, bb) in itertools.combinations(bbs, 2):
        if frozenset((base(na), base(nb))) in PREVISTO or not perto(ba, bb):
            continue
        v = sa.intersect(sb).Volume()
        if v > 0.5:
            problemas.append((f"{na} × {nb}", v))
    return problemas


def main(poses):
    piores = {}
    for pan, tilt in poses:
        linhas = checar(pan, tilt)
        print(f"giro {pan:+5.1f}°  inclinação {tilt:+5.1f}°")
        for k, f in linhas:
            print(f"   {k:42s} {'%7.1f mm' % f if f >= 0 else 'SOBREPÕE %.0f mm³' % -f}")
            piores[k] = min(piores.get(k, 1e9), f)
        sys.stdout.flush()
    print("\nmenor folga em todas as posições:")
    ok = True
    for k, f in piores.items():
        print(f"   {k:42s} {'%7.1f mm' % f if f >= 0 else 'SOBREPÕE'}")
        ok &= f >= 0
    print("\ntodas as peças contra todas:")
    for pan, tilt in [(0.0, 15.0), (-M.PAN_MAX, 0.0), (M.PAN_MAX, 0.0), (-M.PAN_MAX, 30.0), (M.PAN_MAX, 30.0)]:
        pr = todas_as_pecas(pan, tilt)
        print(f"   giro {pan:+5.1f}°  inclinação {tilt:+5.1f}°: " + ("nenhuma sobreposição" if not pr else f"{len(pr)} problema(s)"))
        for k, v in pr:
            print(f"      {k}  {v:.0f} mm³")
        sys.stdout.flush()
        ok &= not pr
    print("\nresultado:", "sem interferência" if ok else "HÁ INTERFERÊNCIA")


if __name__ == "__main__":
    poses = list(itertools.product((-M.PAN_MAX, 0.0, M.PAN_MAX), (0.0, 5.0, 10.0, 20.0, 25.6, 30.0)))
    if len(sys.argv) > 1:
        poses = [tuple(map(float, a.split(","))) for a in sys.argv[1:]]
    main(poses)
