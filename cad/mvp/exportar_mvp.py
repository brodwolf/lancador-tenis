"""Gera os arquivos de fabricação do MVP numa pasta (padrão: ../saida_mvp).

uso: python3 exportar_mvp.py [pasta]
"""
import csv, json, os, re, shutil, sys

import cadquery as cq

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import exportar as E  # noqa: E402
import lancador as M  # noqa: E402
import mvp  # noqa: E402

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(AQUI), "saida_mvp"))


def main():
    pastas = {k: os.path.join(OUT, k) for k in ("1-imprimir", "2-cortar", "3-usinar", "modelo")}
    for k, p in pastas.items():
        if os.path.isdir(p) and k != "modelo":      # modelo/ guarda também as imagens e o LEIAME
            shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
    mvp.construir_mvp(0, 0).export(os.path.join(pastas["modelo"], "mvp_montagem.step"))
    m = mvp.construir_mvp(0, 15)
    glb = os.path.join(pastas["modelo"], "mvp.glb")
    m.export(glb, tolerance=0.25, angularTolerance=0.2)
    E.pos_processar_glb(glb)
    dxfs, linhas = [], []
    for base, p in sorted(M.PECAS.items(), key=lambda kv: (kv[1]["cat"], kv[0])):
        arqs = []
        formas = p.get("variantes") or [p["shape"]]
        if p["cat"] == "impresso":
            for i, f in enumerate(formas, 1):
                suf = f"_{i}" if len(formas) > 1 else ""
                stl = os.path.join(pastas["1-imprimir"], f"{base}{suf}.stl")
                cq.exporters.export(f, stl, tolerance=0.02, angularTolerance=0.08)
                cq.exporters.export(f, stl.replace(".stl", ".step"))
                arqs.append(os.path.basename(stl))
        elif p["cat"] == "laser":
            mm = re.search(r"(\d+(?:,\d+)?)\s?mm", p["mat"])
            dxf = os.path.join(pastas["2-cortar"], f"{base}_{mm.group(1) if mm else ''}mm.dxf")
            E.exportar_dxf(p["shape"], dxf)
            dxfs.append((base, p, dxf))
            arqs.append(os.path.basename(dxf))
        elif p["cat"] == "usinado":
            for i, f in enumerate(formas, 1):
                suf = f"_{i}" if len(formas) > 1 else ""
                st = os.path.join(pastas["3-usinar"], f"{base}{suf}.step")
                cq.exporters.export(f, st)
                arqs.append(os.path.basename(st))
        if p["cat"] != "visual":
            linhas.append([M.CAT[p["cat"]], p["label"], p["mat"], p["qtd"], base, " ".join(arqs)])
    # calibre do vão (ferramenta, não fica na máquina)
    cal = mvp.calibre()
    cq.exporters.export(cal, os.path.join(pastas["1-imprimir"], "calibre_vao_56mm.stl"), tolerance=0.02, angularTolerance=0.08)
    cq.exporters.export(cal, os.path.join(pastas["1-imprimir"], "calibre_vao_56mm.step"))
    linhas.append([M.CAT["impresso"], "Calibre do vão de 56 mm entre as rodas (ferramenta)", "PETG", 1, "calibre_vao_56mm", "calibre_vao_56mm.stl"])
    E.pranchas_pdf(dxfs, os.path.join(pastas["2-cortar"], "pranchas_corte_mvp.pdf"))
    with open(os.path.join(OUT, "pecas_do_modelo_mvp.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Categoria", "Peça", "Material", "Qtd", "Código", "Arquivo(s)"])
        w.writerows(linhas)
    meta = {b: dict(label=p["label"], cat=M.CAT[p["cat"]], tipo=p["cat"], mat=p["mat"], qtd=p["qtd"]) for b, p in M.PECAS.items()}
    json.dump(dict(pecas=meta), open(os.path.join(pastas["modelo"], "pecas_mvp.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("ok:", OUT, sum(len(fs) for _, _, fs in os.walk(OUT)), "arquivos")


if __name__ == "__main__":
    main()
