"""MVP de bancada: só a base do andar do lançador, o giro, a inclinação e a cabeça.

A chapa de base fica sobre os 4 postes do andar de controle (112 mm), que servem de pernas na bancada
e depois voltam para o andar de controle. Tudo aqui é peça da máquina completa.
"""
import os
import sys

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lancador as M  # noqa: E402

Z_MESA = M.Z_BASE + M.T_PISO - 8     # tampo da mesa (os pés de borracha têm 8 mm)


def construir_mvp(pan_deg=0.0, tilt_deg=15.0):
    M.PECAS.clear()
    M._contador.clear()
    raiz = cq.Assembly(name="mvp")
    a = cq.Assembly(name="andar_lancador")
    M.montar_base_giro(a, pan_deg)
    pan = cq.Assembly(name="pan", loc=M.tr(0, M.YA, 0) * M.rotz(pan_deg))
    M.montar_pan(pan, tilt_deg)
    a.add(pan)
    raiz.add(a)
    pernas = cq.Assembly(name="pernas")
    M.postes(pernas, M.Z_BASE + M.T_PISO, M.Z1, "poste_base",
             "Poste do andar de controle (perfil 20x20, 112 mm) · perna no MVP")
    for sx in (-1, 1):
        for sy in (-1, 1):
            M.put(pernas, M.cyl_z(12, Z_MESA, Z_MESA + 8, sx * M.PX, sy * M.PY), "pe_borracha_m5", M.COR["borracha"],
                  label="Pé de borracha Ø25 com parafuso M5 (embaixo de cada perna)", cat="comprado")
    raiz.add(pernas)
    return raiz


def calibre():
    """Calibre do vão de 56 mm entre as rodas (ferramenta de montagem)."""
    return M.imp_calibre()


if __name__ == "__main__":
    import time
    t0 = time.time()
    construir_mvp()
    print("MVP:", len(M.PECAS), "peças distintas,", sum(p["qtd"] for p in M.PECAS.values()), "instâncias, %.1fs" % (time.time() - t0))
    for cat in ("laser", "impresso", "usinado", "comprado", "perfil"):
        print(cat, sorted((b, p["qtd"]) for b, p in M.PECAS.items() if p["cat"] == cat))
