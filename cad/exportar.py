"""Gera todos os arquivos de fabricação e visualização a partir de lancador.py.

  saida/
    montagem/      lancador_montagem.step (montagem completa com cores e nomes)
    impressao_3d/  STL + STEP de cada peça impressa
    corte_laser/   DXF de cada chapa (mm, escala 1:1) + pranchas.pdf
    usinagem/      STEP das peças de barra/torno
    visualizador/  lancador.glb + pecas.json
    lista_de_pecas.csv
"""
import csv
import json
import math
import os
import shutil
import struct
import sys

import cadquery as cq
import ezdxf

import lancador as M

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "saida")

QTD_FABRICAR = {}   # base -> quantidade a pedir/imprimir (se diferente do nº de instâncias no modelo)


def srgb_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def nome_arquivo(base, p):
    mat = p["mat"].split(",")[0].replace(" ", "").replace("/", "-").replace("ç", "c")
    esp = ""
    if "mm" in p["mat"]:
        esp = "_" + p["mat"].split(",")[-1].strip().replace(" ", "")
    return base, mat, esp


def exportar_dxf(shape_wp, caminho):
    face = shape_wp.faces("<Z")
    cq.exporters.export(face, caminho)
    doc = ezdxf.readfile(caminho)
    doc.header["$INSUNITS"] = 4          # milímetros
    doc.header["$MEASUREMENT"] = 1
    if "CORTE" not in doc.layers:
        doc.layers.add("CORTE", color=1)
    for e in doc.modelspace():
        e.dxf.layer = "CORTE"
    doc.saveas(caminho)


def pos_processar_glb(caminho):
    """Ajusta materiais (metal/rugosidade, transparência) para ficar correto em qualquer visualizador."""
    b = open(caminho, "rb").read()
    jlen = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + jlen])
    resto = b[20 + jlen:]
    metal = {k for k in ("perfil", "alu", "aco", "latao", "motor_sino")}
    lin = {k: tuple(srgb_lin(x) for x in (c.toTuple()[:3])) for k, c in M.COR.items()}
    for mat in j.get("materials", []):
        pbr = mat.setdefault("pbrMetallicRoughness", {})
        bc = pbr.get("baseColorFactor", [1, 1, 1, 1])
        nome = min(lin, key=lambda k: sum((a - b_) ** 2 for a, b_ in zip(lin[k], bc[:3])))
        mat["name"] = nome
        if nome in metal:
            pbr["metallicFactor"], pbr["roughnessFactor"] = 0.55, 0.38
        else:
            pbr["metallicFactor"], pbr["roughnessFactor"] = 0.0, 0.62
        if bc[3] < 0.999:
            mat["alphaMode"] = "BLEND"
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + len(resto)
    with open(caminho, "wb") as f:
        f.write(b[:4] + struct.pack("<I", 2) + struct.pack("<I", total))
        f.write(struct.pack("<I", len(js)) + b"JSON" + js + resto)


def pranchas_pdf(itens, caminho):
    """Uma página por chapa: contorno em escala, cotas gerais, material e quantidade."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(caminho) as pdf:
        for base, p, dxf in itens:
            doc = ezdxf.readfile(dxf)
            fig, ax = plt.subplots(figsize=(11.69, 8.27))
            xs, ys = [], []
            furos = {}
            for e in doc.modelspace():
                if e.dxftype() == "CIRCLE":
                    c, r = e.dxf.center, e.dxf.radius
                    ax.add_patch(plt.Circle((c.x, c.y), r, fill=False, lw=0.8, color="#222"))
                    furos[round(2 * r, 1)] = furos.get(round(2 * r, 1), 0) + 1
                    xs += [c.x - r, c.x + r]; ys += [c.y - r, c.y + r]
                elif e.dxftype() == "LINE":
                    a_, b_ = e.dxf.start, e.dxf.end
                    ax.plot([a_.x, b_.x], [a_.y, b_.y], lw=0.8, color="#222")
                    xs += [a_.x, b_.x]; ys += [a_.y, b_.y]
                else:
                    try:
                        pts = [(v.x, v.y) for v in e.flattening(0.05)]
                    except Exception:
                        continue
                    ax.plot([q[0] for q in pts], [q[1] for q in pts], lw=0.8, color="#222")
                    xs += [q[0] for q in pts]; ys += [q[1] for q in pts]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            w, h = x1 - x0, y1 - y0
            pad = max(w, h) * 0.12
            ax.set_xlim(x0 - pad, x1 + pad); ax.set_ylim(y0 - pad, y1 + pad)
            ax.set_aspect("equal"); ax.axis("off")
            ax.annotate("", (x0, y0 - pad * 0.45), (x1, y0 - pad * 0.45),
                        arrowprops=dict(arrowstyle="<->", lw=0.8))
            ax.text((x0 + x1) / 2, y0 - pad * 0.38, f"{w:.1f} mm", ha="center", va="bottom", fontsize=10)
            ax.annotate("", (x1 + pad * 0.45, y0), (x1 + pad * 0.45, y1),
                        arrowprops=dict(arrowstyle="<->", lw=0.8))
            ax.text(x1 + pad * 0.52, (y0 + y1) / 2, f"{h:.1f} mm", rotation=90, ha="left", va="center", fontsize=10)
            qtd = QTD_FABRICAR.get(base, p["qtd"])
            ax.set_title(f"{p['label']}\n{p['mat']}  ·  quantidade: {qtd}  ·  arquivo: {os.path.basename(dxf)}",
                         fontsize=11, loc="left")
            leg = "Furos: " + ", ".join(f"{n}× Ø{d:g}" for d, n in sorted(furos.items()))
            fig.text(0.02, 0.03, leg + "\nCotas em mm. Furos oblongos e recortes no DXF. Rosqueie em casa os furos marcados na seção 16 do documento.",
                     fontsize=8, color="#444")
            pdf.savefig(fig); plt.close(fig)


def exportar():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    pastas = {k: os.path.join(OUT, k) for k in ("montagem", "impressao_3d", "corte_laser", "usinagem", "visualizador")}
    for p in pastas.values():
        os.makedirs(p)

    m = M.construir()
    print("montagem:", len(M.PECAS), "peças distintas")
    m.export(os.path.join(pastas["montagem"], "lancador_montagem.step"))
    glb = os.path.join(pastas["visualizador"], "lancador.glb")
    m.export(glb, tolerance=0.25, angularTolerance=0.2)
    pos_processar_glb(glb)
    import base64, gzip
    with open(glb, "rb") as f:
        dados = gzip.compress(f.read(), 9)
    with open(os.path.join(pastas["visualizador"], "lancador_glb_gz.txt"), "wb") as f:
        f.write(base64.b64encode(dados))
    print("GLB: %.1f MB (compactado %.1f MB)" % (os.path.getsize(glb) / 1e6, len(dados) / 1e6))

    dxfs = []
    linhas = []
    for base, p in sorted(M.PECAS.items(), key=lambda kv: (kv[1]["cat"], kv[0])):
        arquivos = []
        if p["cat"] == "impresso":
            formas = p.get("variantes") or [p["shape"]]
            for i, f in enumerate(formas, 1):
                suf = f"_{i}" if len(formas) > 1 else ""
                stl = os.path.join(pastas["impressao_3d"], f"{base}{suf}.stl")
                cq.exporters.export(f, stl, tolerance=0.02, angularTolerance=0.08)
                cq.exporters.export(f, stl.replace(".stl", ".step"))
                arquivos.append(os.path.relpath(stl, OUT))
        elif p["cat"] == "laser":
            import re
            mm = re.search(r"(\d+(?:,\d+)?)\s?mm", p["mat"])
            esp = (mm.group(1) + "mm") if mm else "chapa"
            dxf = os.path.join(pastas["corte_laser"], f"{base}_{esp}.dxf")
            exportar_dxf(p["shape"], dxf)
            dxfs.append((base, p, dxf))
            arquivos.append(os.path.relpath(dxf, OUT))
        elif p["cat"] == "usinado":
            st = os.path.join(pastas["usinagem"], f"{base}.step")
            cq.exporters.export(p["shape"], st)
            arquivos.append(os.path.relpath(st, OUT))
        p["arquivos"] = arquivos
        if p["cat"] != "visual":
            linhas.append([M.CAT[p["cat"]], p["label"], p["mat"], QTD_FABRICAR.get(base, p["qtd"]), base,
                           " ".join(arquivos)])

    pranchas_pdf(dxfs, os.path.join(pastas["corte_laser"], "pranchas_corte_laser.pdf"))

    with open(os.path.join(OUT, "lista_de_pecas.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Categoria", "Peça", "Material", "Qtd no modelo", "Código", "Arquivo(s)"])
        w.writerows(linhas)

    meta = {base: dict(label=p["label"], cat=M.CAT[p["cat"]], tipo=p["cat"], mat=p["mat"], qtd=p["qtd"],
                       arquivos=p.get("arquivos", [])) for base, p in M.PECAS.items()}
    params = dict(PAN_Y=M.PAN_Y, Z_PIVOT=M.Z_PIVOT, TILT_NUT=M.TILT_NUT, ACT_PIVOT_Z=M.ACT_PIVOT_Z,
                  NIP=M.NIP, WC=M.WC, BALL_R=M.BALL_R, WHEEL_D=M.WHEEL_D)
    with open(os.path.join(pastas["visualizador"], "pecas.json"), "w", encoding="utf-8") as f:
        json.dump(dict(pecas=meta, params=params), f, ensure_ascii=False)
    shutil.copy(os.path.join(AQUI, "LEIAME.md"), os.path.join(OUT, "LEIAME.md"))
    shutil.copy(os.path.join(AQUI, "lancador.py"), os.path.join(OUT, "lancador.py"))
    shutil.copy(os.path.join(AQUI, "exportar.py"), os.path.join(OUT, "exportar.py"))
    shutil.copy(os.path.join(AQUI, "verificar.py"), os.path.join(OUT, "verificar.py"))
    print("ok:", sum(len(fs) for _, _, fs in os.walk(OUT)), "arquivos")


if __name__ == "__main__":
    exportar()
