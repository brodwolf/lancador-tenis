"""Confere o MVP: todas as peças contra todas, nas pontas do giro e da inclinação."""
import itertools, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import verificar as V  # noqa: E402
import mvp  # noqa: E402

ok = True
for pan, tilt in [(0, 15), (-12.5, 0), (12.5, 0), (-12.5, 30), (12.5, 30)]:
    it = V.achatar(mvp.construir_mvp(pan, tilt))
    bbs = [(n, s, s.BoundingBox()) for n, c, s in it]
    prob = [n for n, s, b in bbs if s.Volume() <= 0]
    for (na, sa, ba), (nb, sb, bb) in itertools.combinations(bbs, 2):
        if frozenset((V.base(na), V.base(nb))) in V.PREVISTO:
            continue
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        v = sa.intersect(sb).Volume()
        if v > 0.5:
            prob.append(f"{na} × {nb} {v:.0f} mm³")
    print(f"giro {pan:+5.1f}°  inclinação {tilt:+5.1f}°:", "ok" if not prob else prob)
    ok &= not prob
# folga entre a cabeça e a chapa de base em toda a faixa
menor = 1e9
for pan in (-12.5, 0, 12.5):
    for tilt in (0, 10, 20, 30):
        it = V.achatar(mvp.construir_mvp(pan, tilt))
        cab = V.grupo(it, lambda n, c: "tilt" in c)
        base = V.grupo(it, lambda n, c: V.base(n) in ("chapa_base_lancador", "lazy_susan", "motor_giro", "suporte_motor_giro", "mancal_fuso_giro", "microchave", "poste_base"))
        menor = min(menor, V.folga(cab, base))
print("menor folga cabeça × base e giro fixo: %.1f mm" % menor)
print("resultado:", "sem interferência" if ok and menor > 0 else "HÁ INTERFERÊNCIA")
