"""Gera a documentação da branch do MVP: LEIAME de cada pasta, lista de compras, desenhos da elétrica,
projeto do Wokwi e o guia em HTML.

uso: python3 gerar_docs.py <pasta da branch>
(rode antes o exportar_mvp.py na mesma pasta; os renders ficam em modelo/)
"""
import base64, csv, html, json, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MVP = os.path.dirname(AQUI)
V2 = os.path.dirname(MVP)
sys.path[:0] = [AQUI, MVP, V2]
import dados_mvp as D  # noqa: E402
import svg_mvp as S  # noqa: E402

OUT = os.path.abspath(sys.argv[1])
E = html.escape


def br(x, casas=0):
    """Número no formato brasileiro."""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def escrever(rel, texto):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(texto)


def md_tabela(cab, linhas):
    o = "| " + " | ".join(cab) + " |\n| " + " | ".join("---" for _ in cab) + " |\n"
    for l in linhas:
        o += "| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in l) + " |\n"
    return o


# ----------------------------------------------------------------------------- medidas das peças (CAD)
def medir():
    import lancador as M
    import mvp
    mvp.construir_mvp(0, 15)
    med = {}
    for b, p in M.PECAS.items():
        fs = p.get("variantes") or [p["shape"]]
        lst = []
        for f in fs:
            f = f.val() if hasattr(f, "val") else f
            bb = f.BoundingBox()
            lst.append((sorted([bb.xlen, bb.ylen, bb.zlen], reverse=True), f.Volume() / 1000.0))
        med[b] = dict(label=p["label"], cat=p["cat"], qtd=p["qtd"], mat=p.get("mat", ""), formas=lst)
    cal = mvp.calibre()
    cal = cal.val() if hasattr(cal, "val") else cal
    bb = cal.BoundingBox()
    med["calibre_vao_56mm"] = dict(label="Calibre do vão de 56 mm (ferramenta)", cat="impresso", qtd=1, mat="PETG",
                                   formas=[(sorted([bb.xlen, bb.ylen, bb.zlen], reverse=True), cal.Volume() / 1000.0)])
    return med


def dims(d):
    return " × ".join(br(round(v)) for v in d)


def linhas_impressao(med):
    out, tot = [], {"PETG": 0.0, "TPU": 0.0, "h": [0.0, 0.0]}
    for cod, q, mat, ori, cfg, obs in D.IMPRESSAO:
        dd, vol = med[cod]["formas"][0]
        rho = D.DENSIDADE.get(mat, 1.27)
        f = D.FATOR_CHEIO.get(cod, 0.6 if vol > 20 else 0.8)
        g = vol * rho * f
        h0, h1 = max(0.5, g / 20), max(0.7, g / 13)
        tot["TPU" if "TPU" in mat else "PETG"] += g * q
        tot["h"][0] += h0 * q
        tot["h"][1] += h1 * q
        out.append(dict(cod=cod, q=q, mat=mat, dims=dims(dd), g=g, h=(h0, h1), ori=ori, cfg=cfg, obs=obs,
                        arq=f"{cod}.stl"))
    return out, tot


def horas(h):
    a, b = h
    if b < 1.5:
        return "< 1,5"
    return f"{br(a)}–{br(b)}"


# ----------------------------------------------------------------------------- textos
def md_raiz(med, tot):
    massa = "~9,8 kg"
    return f"""# Lançador de bolas · MVP de bancada

Esta branch tem só o que entra no MVP de bancada: a **base do andar do lançador** (alumínio 4 mm), o **giro**, a **inclinação** e a **cabeça de lançamento**. A alimentação vem de uma fonte de bancada, os comandos vêm do computador pelo USB e as bolas entram à mão no berço.

**Nada aqui é provisório.** Cada peça impressa, cortada, usinada ou comprada, cada conector e cada rabicho de fio desta lista é da máquina completa e continua nela quando o resto chegar. Só três itens são de bancada e estão marcados assim na lista: a fonte, o cabo dela com plugues banana e a caixa de botoeira da emergência.

![MVP montado](modelo/mvp_perspectiva.webp)

O guia completo, com os desenhos da elétrica e todas as tabelas, está em [`guia_mvp.html`](guia_mvp.html) (abra no navegador).

## A chapa sozinha na mesa aguenta?

**Aguenta o peso com folga, mas não deve ficar deitada direto na mesa.**

- **Peso:** o MVP tem {massa}. A chapa de 4 mm, apoiada nos 4 cantos, flete menos de 0,5 mm com isso.
- **Por que não deitada:** por baixo da chapa ficam as porcas do lazy susan, do suporte do motor do giro e do mancal do fuso. A chapa ficaria apoiada nelas, balançando.
- **Como apoiar:** use os 4 postes do andar de controle (perfil 20×20, 112 mm) como pernas, com um pé de borracha M5 embaixo de cada um. São os mesmos postes que depois ligam o andar de controle ao do lançador: nada se perde.
- **Estabilidade:** o centro de massa fica perto do meio da chapa, a 27–32 cm da mesa, dentro do retângulo de 270 × 380 mm das pernas. A máquina não tomba nem com a cabeça no giro máximo.
- **Vibração:** com as rodas a milhares de rpm ela pode "andar" na mesa. Se andar, troque os pés por uma tábua de MDF de 18 mm (~450 × 350 mm) parafusada nas pernas (M5) e prenda a tábua na mesa com 2 grampos C. É o único apoio de bancada sugerido.

## Pastas

| Pasta | O que tem |
| --- | --- |
| [`1-imprimir/`](1-imprimir/) | STL e STEP das {len(D.IMPRESSAO)} peças impressas, com orientação, configuração, massa e tempo de cada uma |
| [`2-cortar/`](2-cortar/) | DXF 1:1 das {len(D.CORTE)} chapas + pranchas em PDF para o serviço de corte a laser |
| [`3-usinar/`](3-usinar/) | STEP dos eixos e o que fazer em cada um |
| [`4-comprar/`](4-comprar/) | Lista unificada (`lista_mvp.csv`): quantas peças iguais comprar de cada item |
| [`5-eletrica/`](5-eletrica/) | Esquemas de potência e sinais, placa de controle, bancada, cabos e a simulação no Wokwi |
| [`6-firmware/`](6-firmware/) | Programa do ESP32 com comandos pelo monitor serial |
| [`7-montar/`](7-montar/) | Passo a passo da montagem mecânica, da elétrica e dos primeiros testes |
| [`modelo/`](modelo/) | Montagem em STEP, GLB e imagens |
| [`cad/`](cad/) | Código CadQuery que gera tudo isso de novo |

## Ordem sugerida

1. **Comprar** o que demora: motores 4250, ESCs, NEMA17 com fuso, servo, lazy susan, mancais, polias e correias. A lista está em `4-comprar/`.
2. **Imprimir** começando pelos núcleos das rodas (as peças mais longas). Total ≈ {br(tot['PETG']/1000, 2)} kg de PETG e {br(tot['TPU']/1000, 2)} kg de TPU, {br(tot['h'][0])}–{br(tot['h'][1])} h de impressora.
3. **Mandar cortar** as chapas e **usinar** os eixos enquanto imprime. Confira antes as furações das peças compradas (`2-cortar/LEIAME.md`).
4. **Montar a elétrica na bancada**, sem a mecânica: fonte, barramentos, bucks, placa, um motor por vez. Teste antes no Wokwi (`5-eletrica/wokwi/`).
5. **Montar a mecânica** (`7-montar/`): base e pernas, giro, garfos, cabeça.
6. **Juntar as duas** pelos conectores X1–X6 e fazer os testes da `7-montar/`, com as rodas em rotação baixa primeiro.

## O que fica para depois

""" + "".join(f"- {x}\n" for x in D.DEPOIS) + """
Tudo isso entra sem mudar nada do MVP: os pinos do ESP32, os conectores, os rabichos e os fusíveis já são os da máquina completa.

## O que o MVP mudou no projeto

Ao montar a lista do MVP apareceram correções que valem para a máquina toda. Elas já estão nos arquivos desta branch; a branch `main` ainda não tem:

""" + "".join(f"- **{a}:** {b}\n" for a, b in D.MUDANCAS_MAIN)


def md_imprimir(linhas, tot):
    tab = md_tabela(["Arquivo", "Qtd", "Material", "Tamanho (mm)", "Massa (g)", "Tempo (h)", "Na mesa", "Configuração", "Observação"],
                    [(f"`{l['arq']}`", l["q"], l["mat"], l["dims"], br(l["g"]), horas(l["h"]), l["ori"], l["cfg"], l["obs"]) for l in linhas])
    return f"""# Impressão 3D

{len(linhas)} arquivos, {sum(l['q'] for l in linhas)} peças. Cada peça tem o STL (para o fatiador) e o STEP (para editar).

Os arquivos saem na **posição de montagem**: gire na mesa do fatiador para a orientação da tabela. Massa e tempo são estimativas para bico de 0,4 mm e camada de 0,2 mm; o tempo real depende da impressora.

## Configuração geral

- **PETG:** 235–245 °C, mesa 75–85 °C, ventilação 30–50%. Seque o filamento se ele estalar.
- **TPU 95A:** 220–230 °C, 20–30 mm/s, retração curta (ou desligada em extrusora Bowden).
- **Sem suporte** em todas as peças, na orientação da tabela.
- **Brim** de 5 mm nas peças grandes e planas (tampas e carenagens), para não descolar.
- Peças que vão ficar ao sol podem ser feitas em **ASA** com as mesmas configurações de perímetro e preenchimento.

## Peças

{tab}
**Total:** ≈ {br(tot['PETG'])} g de PETG e {br(tot['TPU'])} g de TPU, {br(tot['h'][0])}–{br(tot['h'][1])} h. Compre 2 kg de PETG e 0,5 kg de TPU: sobra para errar e para refazer uma peça.

## Ordem de impressão

1. `nucleo_roda` ×2 e `banda_roda` ×2: as rodas são o caminho crítico.
2. `bloco_porca_giro`, `bloco_porca_tilt`, `suporte_motor_giro`, `mancal_fuso_giro`, `suporte_motor_tilt`: dão para montar e testar o giro e a inclinação antes da cabeça ficar pronta.
3. O resto da cabeça: `berco`, `suporte_trilho`, `funil_cabeca`, `suporte_servo`, `braco_empurrador`, `disco_sinal`, `suporte_hall`.
4. Por último as proteções: `tampa_correia_*` e `carenagem_roda_*`. O MVP pode girar as rodas sem elas nos primeiros testes, em rotação baixa e com ninguém do lado.

## Insertos e furos-guia

- **Insertos M4 no berço:** ferro de solda a ~230 °C com a ponta de inserto, empurre devagar até ficar rente. Deixe esfriar antes de apertar.
- **Furos de Ø2,5 nos blocos das porcas:** o parafuso M3 abre a rosca no PETG. Aperte só até encostar.
- **Ímãs dos discos de sinal:** antes de colar, marque o polo que o A3144 detecta (encoste no sensor ligado e veja a saída ir a 0). Os dois ímãs de cada disco com esse polo para fora.
"""


def md_cortar(med):
    linhas = []
    for cod, q, mat, esp, obs in D.CORTE:
        dd, _ = med[cod]["formas"][0]
        linhas.append((f"`{cod}_{esp}mm.dxf`", q, mat, f"{esp} mm", dims(dd[:2]), obs))
    return f"""# Corte a laser

Envie os DXF (1:1, em milímetros) e o `pranchas_corte_mvp.pdf`, que tem cotas gerais de cada chapa para conferência.

{md_tabela(["Arquivo", "Qtd", "Material", "Espessura", "Tamanho (mm)", "Observação"], linhas)}
## Antes de mandar cortar

Os furos das peças compradas seguem cotas de catálogo. **Confira com a peça na mão:**

- **KFL001:** 2 furos M6 a 48 mm. Na placa lateral os furos são de Ø7; os da roda de baixo são oblongos para ajustar o vão.
- **KFL08:** 2 furos M4 a 37 mm. No garfo os furos são de Ø4,5.
- **Lazy susan Ø150:** a furação varia por fabricante. Base: 4 furos a r 66, girados 45°. Plataforma: 4 furos a r 60. Se não bater, ajuste `lancador.py` ou fure na montagem.
- **Motor 4250 (X-mount):** 4 oblongos M3 a r 19, alinhados com a correia: dão ±3 mm para esticar.
- **NEMA17:** furação padrão de 31 mm, M3.
- **Furos em D:** discos de inércia (eixo Ø12, 11 mm entre faces), manivela e pivô das placas laterais (eixo Ø8, 7 mm). Peça ao serviço para não arredondar o canto do D.

## Depois do corte

- Tire as rebarbas dos dois lados e quebre os cantos vivos.
- Nenhuma chapa do MVP precisa de rosca: todos os furos são passantes, com porca.
- Os dois garfos e as duas placas laterais são peças iguais: monte uma de cada lado.
"""


def md_usinar():
    linhas = [(f"`{c.split(' ')[0]}*.step`", q, m, L, o) for c, q, m, L, o in D.USINAGEM]
    return f"""# Usinagem

Os dois tipos de eixo saem de barra retificada (eixo linear), cortada no comprimento. Dá para fazer em casa com serra, lima e macho; uma tornearia faz em minutos.

{md_tabela(["Arquivo", "Qtd", "Barra", "Comprimento", "O que fazer"], linhas)}
## Dicas

- Corte 1 mm mais longo e acerte na lima ou no esmeril, sem esquentar demais o aço retificado.
- Faça o chato com a barra presa na morsa, conferindo com paquímetro: 11,0 mm (Ø12) e 7,0 mm (Ø8). Teste no furo em D da chapa antes de terminar.
- A rosca M4 da ponta do semi-eixo de 65 mm: centro com punção, broca 3,3 mm × 12 mm, macho M4.
- `semi_eixo_1.step` é o de 50 mm (lado +x); `semi_eixo_2.step` é o de 65 mm (lado −x, com a manivela).
"""


def tabela_compras_md(grupo):
    linhas = [(i, e, q, c, o + (f" · {n}" if n else "")) for g, i, e, q, c, o, n in compras() if g == grupo]
    return md_tabela(["Item", "Especificação", "Usa", "Comprar", "Onde vai"], linhas)


_TOT = {}


def compras():
    out = []
    for g, i, e, q, c, o, n in D.COMPRAS:
        if isinstance(q, str) and "{" in q:
            q = q.format(petg=br(_TOT["PETG"] / 1000, 1), tpu=br(_TOT["TPU"] / 1000, 2))
        out.append((g, i, e, q, c, o, n))
    for desc, q, c, onde in D.FIXADORES:
        out.append((D.G_FIX, desc, "latão" if desc.startswith("Inserto") else "aço zincado ou inox A2", q, c, onde, ""))
    return out


def fabricar(med, linhas_imp):
    out = []
    for cod, q, mat, esp, obs in D.CORTE:
        out.append((D.G_FAB, f"Chapa {cod} ({esp} mm)", mat, q, q, "corte a laser", "DXF em 2-cortar"))
    for c, q, m, L, o in D.USINAGEM:
        out.append((D.G_FAB, f"Eixo {c.split(' ')[0]} ({L})", m, q, q, "usinagem", "STEP em 3-usinar"))
    for l in linhas_imp:
        out.append((D.G_FAB, f"Peça impressa {l['cod']}", l["mat"], l["q"], l["q"], "impressão 3D", "STL em 1-imprimir"))
    return out


GRUPOS = [D.G_MEC, D.G_MOT, D.G_FIX, D.G_ELE, D.G_CAB, D.G_CON, D.G_FER, D.G_FAB]


def md_comprar(med, linhas_imp):
    o = """# Lista unificada do MVP

Uma linha por item igual, somando todas as peças do MVP. **Usa** é o que vai na máquina; **Comprar** já inclui reserva e o tamanho em que o item costuma ser vendido. A mesma lista está em [`lista_mvp.csv`](lista_mvp.csv) para abrir na planilha (separador `;`).

Itens marcados **só bancada** não vão para a máquina completa. Todo o resto vai.

"""
    for g in GRUPOS[:-1]:
        o += f"## {g}\n\n" + tabela_compras_md(g) + "\n"
    o += "## Fabricar\n\nPeças feitas a partir dos arquivos desta branch (não entram na compra, mas estão aqui para a conta fechar).\n\n"
    o += md_tabela(["Item", "Material", "Qtd", "Como"], [(i, e, q, f"{o_} · {n}") for _, i, e, q, _, o_, n in fabricar(med, linhas_imp)])
    return o


def csv_comprar(med, linhas_imp):
    p = os.path.join(OUT, "4-comprar", "lista_mvp.csv")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Grupo", "Item", "Especificação", "Usa no MVP", "Comprar", "Onde vai", "Nota"])
        lst = compras() + fabricar(med, linhas_imp)
        lst.sort(key=lambda r: GRUPOS.index(r[0]))
        for r in lst:
            w.writerow(r)


def md_eletrica():
    con = md_tabela(["Conector", "Tipo", "Função", "Pinos", "Rabicho do lançador", "Rabicho da caixa"],
                    [(c, t_, f, " · ".join(f"{i+1} {p}" for i, p in enumerate(ps)), a, b) for c, t_, f, ps, a, b in D.CONECTORES])
    cx = md_tabela(["Código", "Trecho", "Fio", "Comprimento", "Observação"], D.CABOS_CAIXA)
    pinos = md_tabela(["GPIO", "Função", "Tipo", "Na placa"], D.PINOS)
    return f"""# Elétrica do MVP

Mesma arquitetura da máquina completa, com a fonte de bancada no lugar das baterias. Os pinos do ESP32, os conectores e os fusíveis já são os definitivos.

Abra o [`guia_mvp.html`](../guia_mvp.html) para ver os desenhos com as cores do tema. Os SVG desta pasta abrem direto no GitHub ou no navegador.

## 1. Potência

![Potência](1-potencia.svg)

- Fonte de **19 a 24 V**, nunca acima: o MP1584 aceita 28 V e o TMC2209, 29 V.
- Nos primeiros testes, limite de corrente em **0,5 A**. Para girar as rodas, 5 A ou mais com a rampa de 400 rpm/s do firmware.
- **Freio dos ESCs desligado** (BLHeli_32/AM32: *Brake on stop* = off). A fonte e o diodo ideal não aceitam corrente de volta; ao frear, a energia das rodas subiria a tensão do barramento. Sem freio, as rodas param sozinhas em alguns segundos. A 5.500 rpm o motor de 400 KV gera ~13,8 V, abaixo da fonte: soltar o acelerador é seguro.
- O fio vermelho (BEC) do cabo de sinal de cada ESC fica **isolado**: o 5 V vem do buck.
- O negativo nunca é chaveado. Todos os retornos chegam à barra GND, que é o único ponto de terra.

## 2. Sinais

![Sinais](2-sinais.svg)

{pinos}
Livres para a máquina completa: {D.PINOS_LIVRES}.

## 3. Placa de controle

![Placa de controle](3-placa.svg)

Monte nesta ordem, testando cada etapa com a fonte limitada em 0,5 A:

1. Bornes KF301 e a trilha de GND. Confira continuidade.
2. Barras de pinos fêmea do ESP32 e dos drivers (os módulos ficam removíveis).
3. Resistores e capacitores de cada entrada, junto do pino.
4. IRLZ44N, 1N4007 (catodo no lado do +12 V) e o borne do K1.
5. Conectores JST-XH de sinal e de motor.
6. Capacitores eletrolíticos: 1.000 µF no borne VM, 100 µF em cada driver, com a polaridade certa.
7. Jumper de endereço: MS1 do driver do tilt no 3V3; os outros MS no GND.

## 4. Bancada e cabos

![Bancada](4-bancada.svg)

A caixa fica a até 30 cm da chapa. Cada cabo entre os dois é feito de **dois rabichos** com o conector no meio: o do lançador (saindo do motor ou sensor) termina no plugue; o da caixa (saindo da placa pelo prensa-cabo) termina no soquete de painel. Os comprimentos são os da máquina completa: quando os andares forem montados, o soquete vai para o suporte de conectores do andar e nenhum fio é refeito.

{con}
Ligue e desligue os conectores X3 só com a fonte desligada: soltar um motor de passo com o driver energizado queima o driver.

### Dentro da caixa

{cx}
## 5. Simulação

A pasta [`wokwi/`](wokwi/) tem o projeto para o [Wokwi](https://wokwi.com), que simula o ESP32-S3 no navegador com o mesmo programa. Instruções no `LEIAME.md` dela.
"""


def md_firmware():
    cmd = md_tabela(["Comando", "O que faz"], [(f"`{a}`", b) for a, b in D.COMANDOS])
    return f"""# Firmware do MVP

`mvp_bancada/mvp_bancada.ino`: comanda as rodas, o giro, a inclinação e o empurrador pelo monitor serial. Os pinos são os da máquina completa.

## Preparar a Arduino IDE

1. Instale o pacote **esp32** da Espressif (versão 3.x) no Gerenciador de Placas.
2. Instale as bibliotecas **ESP32Servo** (Kevin Harrington, 3.x), **AccelStepper** (Mike McCauley) e **TMCStepper** (teemuatlut).
3. Placa: **ESP32S3 Dev Module** · Flash Size **8MB** · PSRAM **OPI PSRAM**.
4. Use a porta USB-C marcada **UART** da DevKitC. Se usar a marcada **USB**, ative *USB CDC On Boot*.
5. Monitor serial em **115200**, fim de linha **Nova linha**. Digite `ajuda`.

## Comandos

{cmd}
## Antes do primeiro tiro

- Confira `KV` e `V_FONTE` no topo do programa: são eles que convertem rpm em acelerador sem o Hall.
- Calibre o curso dos ESCs uma vez (1.000–2.000 µs) pelo procedimento do fabricante.
- `PAN_REF_GRAUS`: depois do primeiro `ref`, meça o ângulo em que a microchave aciona e ajuste.
- `DIR_GIRO` e `DIR_TILT`: troque o sinal se o eixo andar ao contrário.
- `SERVO_REPOUSO` e `SERVO_EMPURRA`: ache com `servo <graus>` o ponto em que o braço fica atrás da bola e o ponto em que ela entra nas rodas.
- Comece com `malha 0`. Depois de conferir o Hall com o tacômetro, `malha 1`.

## Segurança

- O botão de emergência corta a bobina do K1 por hardware (contato NF) e avisa o ESP32 (contato NA, GPIO41): os ESCs perdem a alimentação mesmo se o programa travar.
- No boot o K1 fica aberto e os motores de passo, soltos. `armar` fecha o K1; os ESCs levam 3 s para armar.
- `parar` deixa as rodas pararem sozinhas, sem freio (ver `5-eletrica`).

## Simulação

A cópia em `5-eletrica/wokwi/sketch.ino` tem `#define SIMULACAO` ativo: troca os TMC2209 (UART) por A4988 (só STEP/DIR) no simulador. Não grave essa cópia na placa de verdade.
"""


MONTAGEM = [
    ("Pernas e base", [
        "Abra rosca M5 no furo central das duas pontas dos 4 postes de 112 mm.",
        "Prenda os postes por baixo da chapa de base com 4 M5×12 vindos de cima, nos 4 furos dos cantos.",
        "Rosqueie um pé de borracha M5 embaixo de cada poste.",
    ], "a chapa fica nivelada e não balança na mesa."),
    ("Rolamento do giro", [
        "Prenda o anel de baixo do lazy susan na chapa: 4 M4×10 + arruela + porca autotravante, furos a r 66.",
        "Gire o anel de cima até o furo de acesso alinhar com cada furo da plataforma e prenda a plataforma (4 M4×10, r 60).",
    ], "a plataforma gira leve, sem folga vertical."),
    ("Acionamento do giro", [
        "NEMA17 do giro (fuso Tr8×8) no suporte com 4 M3×8; suporte na chapa com 2 M4×12.",
        "Rolamento 608 prensado no mancal; mancal na chapa com 2 M4×12, com a ponta do fuso dentro do rolamento.",
        "Porca de latão no bloco da porca do giro (4 M3×12); passe a porca no fuso.",
        "Parafuso de ombro Ø6×30 no braço da plataforma, porca M5 por baixo; o ombro entra no rasgo do bloco.",
        "Microchave com 2 M2×10 na posição do CAD, de forma que o bloco a aperte no fim do curso de −x.",
        "Graxa de lítio no fuso.",
    ], "girando o fuso à mão, a plataforma vai de −12,5° a +12,5° sem prender, e a microchave clica antes do fim."),
    ("Garfos e pivô", [
        "Fure as cantoneiras (Ø4,5) pela furação do garfo e da plataforma.",
        "Cantoneiras na plataforma (4 M4×12) e garfos nas cantoneiras (4 M4×12), um de cada lado.",
        "KFL08 por fora de cada garfo (4 M4×16).",
        "Suporte do motor do tilt no garfo −x (2 M4×16) e o NEMA17 do tilt (Tr8×2) nele com 4 M3×10.",
        "Porca de latão no bloco da porca do tilt (4 M3×12) e o bloco no fuso.",
    ], "os dois garfos ficam paralelos e os KFL08 alinhados (passe uma barra de Ø8 pelos dois)."),
    ("Rodas", [
        "Encaixe a banda de TPU no núcleo (as 8 chavetas). Cola PU na junção, se quiser.",
        "Disco de aço + núcleo + disco de aço, com 6 M4×45 e porcas autotravantes; aperte em cruz.",
        "Passe o eixo Ø12 pelos furos em D dos discos, com o chato alinhado.",
    ], "a roda gira no eixo sem folga e sem bater (gire entre dois apoios e olhe de lado)."),
    ("Cabeça", [
        "KFL001 nas placas laterais: 2 M6×20 + arruelas + porca autotravante cada. Os da roda de baixo ficam frouxos nos oblongos.",
        "Rodas nos KFL001, com 2 colares Ø12 cada; polias de 12 mm e discos de sinal nas pontas, com trava-rosca no parafuso da polia.",
        "4 espaçadores M5×90 entre as placas (8 M5×12).",
        "Use o calibre de 56 mm entre as rodas e aperte os KFL001 de baixo.",
        "Motores 4250 nas placas pelo X-mount (8 M3×10), polias de 5 mm, correias 600-3M-9 (cima) e 288-3M-9 (baixo). Estique pelos oblongos do X-mount.",
        "Berço (4 M4×10 nos insertos), trilhos Ø8 e suporte dos trilhos, funil (2 varetas M4).",
        "Servo no suporte (4 M3×12 + porca), suporte na placa −x (2 M4×50), braço no horn (2 M3×8).",
        "Suportes Hall (M3×30) com o A3144 a ~1 mm do disco de sinal; tampas das correias (M3×35) e carenagens das rodas (varetas M4).",
    ], "vão de 56 mm medido nas duas pontas, correias tensas sem zumbir, o braço do servo passa sem tocar no berço."),
    ("Cabeça no garfo", [
        "Apresente a cabeça entre os garfos e passe os semi-eixos: o de 50 mm do lado +x, o de 65 mm do lado −x, com o chato encaixado no furo em D das placas.",
        "Colares Ø8 dos dois lados de cada placa; aperte os parafusos dos KFL08 sobre o chato.",
        "Manivela no semi-eixo −x (furo em D), presa com M4×10 + arruela na ponta.",
        "Parafuso de ombro Ø6×6 na manivela (porca M5); o ombro entra no rasgo do bloco da porca do tilt.",
    ], "girando o fuso do tilt à mão, a cabeça vai de 0° a 30° sem prender e sem folga no pivô."),
    ("Chicotes do lançador", [
        "Faça os rabichos do lançador com os comprimentos de `5-eletrica` e solde os plugues (MT60, GX16-8).",
        "Prenda os cabos da cabeça com folga para o giro e a inclinação inteiros: deixe um laço perto do pivô e outro perto do lazy susan.",
        "Etiquete as duas pontas de cada cabo com o código do conector.",
    ], "com o giro e a inclinação nos extremos, nenhum cabo fica esticado."),
    ("Elétrica na bancada", [
        "Monte a caixa como em `5-eletrica`, testando cada etapa: potência sem carga, bucks, ESP32 sozinho, K1 e emergência.",
        "Um motor de passo por vez: grave o firmware, `prende`, `ref`, `giro 5`, `tilt 10`.",
        "Servo: `servo 90`, `servo 120`; ache o repouso e o empurrão.",
    ], "os comandos movem cada eixo para o lado certo e a emergência corta tudo."),
    ("Primeiro giro das rodas", [
        "Sem bola, ninguém na frente, tampas e carenagens no lugar.",
        "`armar`, espere 3 s, `rodas 1000 1000`. Confira o sentido (as rodas puxam a bola para a frente); troque duas fases no MT60 se precisar.",
        "Suba em degraus: 2.000, 3.000 rpm. Leia a corrente na fonte e escute vibração.",
        "`parar` e espere as rodas pararem sozinhas.",
    ], "sem vibração forte nem cheiro de quente, e a emergência corta os ESCs na hora."),
    ("Primeiro tiro", [
        "`tiro 40 0`, espere `estado` mostrar pronto, ponha a bola no berço com a mão longe das rodas, `disparo`.",
        "Depois `tiro 60 0`, `tiro 60 1500` e `tiro 60 -1500` para ver o spin.",
    ], "a bola sai reta, sem tocar no funil nem nas carenagens."),
]


def md_montar():
    o = """# Montagem e primeiros testes

Cada etapa termina com uma conferência. Só passe para a próxima quando ela der certo.

Os parafusos e onde cada um vai estão em `4-comprar/LEIAME.md` (grupo Fixadores). Use trava-rosca média nos parafusos dos motores e das polias.

"""
    for i, (tit, passos, ok) in enumerate(MONTAGEM, 1):
        o += f"## {i}. {tit}\n\n" + "".join(f"1. {p}\n" for p in passos) + f"\n**Confira:** {ok}\n\n"
    return o


def md_modelo():
    return """# Modelo do MVP

- `mvp_montagem.step`: montagem completa com a cabeça a 0°, para abrir no Fusion 360, FreeCAD, Onshape ou SolidWorks.
- `mvp.glb`: a mesma montagem a 15°, para visualizadores 3D (por exemplo, arraste em https://gltf-viewer.donmccurdy.com).
- `pecas_mvp.json`: nome, categoria e material de cada peça do GLB.
- Imagens:

![Perspectiva](mvp_perspectiva.webp)
![Lado](mvp_lado.webp)
![Traseira](mvp_traseira.webp)
![Giro e inclinação no máximo](mvp_giro.webp)
"""


def md_cad():
    return """# Código-fonte do CAD

- `lancador.py`: modelo paramétrico da máquina completa (CadQuery).
- `exportar.py`, `verificar.py`: exportação e conferência da máquina completa.
- `mvp/mvp.py`: monta só o MVP (base do andar do lançador, giro, tilt, cabeça e as pernas).
- `mvp/exportar_mvp.py`: gera `1-imprimir`, `2-cortar`, `3-usinar`, `modelo` e `pecas_do_modelo_mvp.csv`.
- `mvp/verificar_mvp.py`: confere a interferência entre todas as peças do MVP nos extremos de giro e inclinação.
- `mvp/docs/`: gera os LEIAME, a lista de compras, os desenhos da elétrica, o projeto do Wokwi e o guia HTML.

```
pip install cadquery ezdxf matplotlib playwright pillow
cd cad/mvp
python3 exportar_mvp.py ../..          # arquivos de fabricação na raiz da branch
python3 verificar_mvp.py               # folgas
python3 docs/gerar_docs.py ../..       # documentação
```
"""


# ----------------------------------------------------------------------------- Wokwi
def wokwi():
    pasta = os.path.join(OUT, "5-eletrica", "wokwi")
    os.makedirs(pasta, exist_ok=True)
    fw = open(os.path.join(MVP, "firmware", "mvp_bancada", "mvp_bancada.ino"), encoding="utf-8").read()
    assert "// #define SIMULACAO" in fw
    fw = fw.replace("// #define SIMULACAO", "#define SIMULACAO   // ativo só nesta cópia do Wokwi")
    open(os.path.join(pasta, "sketch.ino"), "w", encoding="utf-8").write(fw)
    open(os.path.join(pasta, "libraries.txt"), "w").write("ESP32Servo\nAccelStepper\n")
    parts = [
        dict(type="board-esp32-s3-devkitc-1", id="esp", top=0, left=0, attrs={}),
        dict(type="wokwi-a4988", id="drvGiro", top=-10, left=-230, rotate=0, attrs={}),
        dict(type="wokwi-a4988", id="drvTilt", top=150, left=-230, attrs={}),
        dict(type="wokwi-stepper-motor", id="motGiro", top=-190, left=-470, attrs={"size": "17", "arrow": "orange", "value": "giro"}),
        dict(type="wokwi-stepper-motor", id="motTilt", top=110, left=-470, attrs={"size": "17", "arrow": "orange", "value": "tilt"}),
        dict(type="wokwi-servo", id="escA", top=-200, left=280, attrs={"hornColor": "#c62f28"}),
        dict(type="wokwi-servo", id="escB", top=-80, left=280, attrs={"hornColor": "#c62f28"}),
        dict(type="wokwi-servo", id="empurrador", top=40, left=280, attrs={"hornColor": "#2563b8"}),
        dict(type="wokwi-relay-module", id="k1", top=180, left=280, attrs={}),
        dict(type="wokwi-led", id="ledMot", top=160, left=460, attrs={"color": "orange", "label": "+MOT"}),
        dict(type="wokwi-resistor", id="rLed", top=250, left=440, rotate=90, attrs={"value": "330"}),
        dict(type="wokwi-pushbutton", id="emerg", top=290, left=290, attrs={"color": "red", "label": "EMERGÊNCIA", "bounce": "0"}),
        dict(type="wokwi-slide-switch", id="fim", top=300, left=-190, attrs={"value": "0"}),
    ]
    w = []

    def L(a, b, cor="green"):
        w.append([a, b, cor, []])
    L("esp:TX", "$serialMonitor:RX", ""); L("esp:RX", "$serialMonitor:TX", "")
    L("esp:4", "escA:PWM", "orange"); L("esp:5", "escB:PWM", "orange"); L("esp:12", "empurrador:PWM", "blue")
    for s_ in ("escA", "escB", "empurrador"):
        L(f"{s_}:V+", "esp:5V", "red"); L(f"{s_}:GND", "esp:GND.1", "black")
    for d, st, di in (("drvGiro", "15", "16"), ("drvTilt", "17", "18")):
        L(f"esp:{st}", f"{d}:STEP", "green"); L(f"esp:{di}", f"{d}:DIR", "violet"); L("esp:10", f"{d}:ENABLE", "gray")
        L(f"{d}:RESET", f"{d}:SLEEP", "gray"); L(f"{d}:VDD", "esp:3V3.1", "red"); L(f"{d}:GND.1", "esp:GND.2", "black")
        L(f"{d}:MS1", "esp:3V3.1", "red"); L(f"{d}:MS2", "esp:3V3.1", "red")       # 1/8 de passo, como o MICRO = 8 do firmware
    for d, m in (("drvGiro", "motGiro"), ("drvTilt", "motTilt")):
        L(f"{d}:1B", f"{m}:A-", "black"); L(f"{d}:1A", f"{m}:A+", "green"); L(f"{d}:2A", f"{m}:B+", "blue"); L(f"{d}:2B", f"{m}:B-", "red")
    L("k1:VCC", "esp:5V", "red"); L("k1:GND", "esp:GND.3", "black"); L("k1:IN", "esp:42", "gold")
    L("k1:COM", "esp:5V", "red"); L("k1:NO", "ledMot:A", "orange"); L("ledMot:C", "rLed:1", "black"); L("rLed:2", "esp:GND.3", "black")
    L("emerg:1.l", "esp:41", "red"); L("emerg:2.l", "esp:GND.4", "black")
    L("fim:2", "esp:13", "gold"); L("fim:1", "esp:GND.4", "black")
    diag = dict(version=1, author="Lançador MVP", editor="wokwi", parts=parts, connections=w, dependencies={})
    json.dump(diag, open(os.path.join(pasta, "diagram.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(os.path.join(pasta, "LEIAME.md"), "w", encoding="utf-8").write("""# Simulação no Wokwi

O Tinkercad não tem ESP32; o [Wokwi](https://wokwi.com) tem o ESP32-S3 e roda o mesmo programa do MVP no navegador, de graça.

## Abrir

1. Entre em https://wokwi.com/projects/new/esp32-s3 (não precisa de conta para testar).
2. Na aba `sketch.ino`, apague o que tiver e cole o `sketch.ino` desta pasta.
3. Na aba `diagram.json`, cole o `diagram.json` desta pasta.
4. Crie o arquivo `libraries.txt` (botão **+** ao lado das abas, ou *Library Manager*) e cole o conteúdo do daqui.
5. Clique em ▶. No monitor serial, digite `ajuda`.

## O que cada peça representa

| No simulador | Na máquina | Como usar |
| --- | --- | --- |
| Servos `escA` e `escB` (ponteiro vermelho) | ESCs das rodas de cima e de baixo | o ponteiro mostra o acelerador: ~45° parado, ~135° no máximo |
| Servo `empurrador` (ponteiro azul) | servo do empurrador | `servo 120`, `disparo` |
| `drvGiro` e `drvTilt` (A4988) | TMC2209 do giro e do tilt | no simulador não há UART; o passo de 1/8 vem do MS1 e MS2 no 3V3 |
| Motores `giro` e `tilt` | NEMA17 com fuso | a seta mostra o ângulo do fuso |
| Módulo de relé + LED `+MOT` | K1 e a barra +MOT | o LED acende com `armar` e apaga com a emergência |
| Botão vermelho | emergência (contato NA, GPIO41) | segure para simular o cogumelo apertado |
| Chave deslizante | microchave do giro (NF, GPIO13) | à esquerda = livre; à direita = acionada |

## Roteiro de teste

1. `estado`: tudo parado, microchave em 0.
2. `prende`, depois `ref`: o motor do giro começa a andar; passe a chave deslizante para a direita. O giro se referencia e volta ao centro. Volte a chave para a esquerda.
3. `giro 10`, `giro -10`, `tilt 30`, `tilt 0`.
4. `armar`: o LED acende. `tiro 60 1500`: os dois ponteiros dos ESCs sobem devagar (rampa de 400 rpm/s), o de cima mais que o de baixo.
5. `disparo` quando `estado` mostrar `pronto 1` (2 s depois de chegar na rotação, com a malha aberta).
6. Aperte o botão vermelho: o LED apaga, os ponteiros voltam e os motores de passo param.

## Limites da simulação

- A emergência de verdade também corta a bobina do K1 por hardware (contato NF), sem depender do programa. O simulador só mostra o lado do programa.
- Os sensores Hall não estão no simulador: use `malha 0`.
- Os TMC2209 só existem na placa real (é o que o `#define SIMULACAO` troca).
""")


# ----------------------------------------------------------------------------- guia HTML
CSS = """
:root {
  --bg: #f3f5f7; --paper: #ffffff; --ink: #18212b; --muted: #5b6774; --line: #d5dce3; --grid: #e7ecf0;
  --accent: #a24a1f; --accent-soft: #f4e3d8;
  --w-bat: #c62f28; --w-mot: #d97706; --w-gnd: #262c33; --w-12: #a8830b; --w-6: #7c4dbd; --w-5: #2563b8; --w-33: #23854e; --w-sig: #7b8794; --w-ph: #8a5a2b;
  --zone-p: #fbefe8; --zone-l: #eef4fb; --pcb: #e3efe6; --pcb-line: #5d8f6c;
  --f-disp: "Barlow Semi Condensed", "Arial Narrow", sans-serif; --f-body: "Barlow", "Segoe UI", sans-serif; --f-mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #11161c; --paper: #171e26; --ink: #e3e9ef; --muted: #98a4b1; --line: #2c3743; --grid: #1f2831;
  --accent: #e08a5a; --accent-soft: #3a261b;
  --w-bat: #ff6b5e; --w-mot: #f5a33a; --w-gnd: #c6ced6; --w-12: #e2bd3a; --w-6: #b28cf0; --w-5: #6aa6f2; --w-33: #4cc583; --w-sig: #8794a3; --w-ph: #d39a62;
  --zone-p: #2a1d17; --zone-l: #172231; --pcb: #16291e; --pcb-line: #5fae7b; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #11161c; --paper: #171e26; --ink: #e3e9ef; --muted: #98a4b1; --line: #2c3743; --grid: #1f2831;
  --accent: #e08a5a; --accent-soft: #3a261b;
  --w-bat: #ff6b5e; --w-mot: #f5a33a; --w-gnd: #c6ced6; --w-12: #e2bd3a; --w-6: #b28cf0; --w-5: #6aa6f2; --w-33: #4cc583; --w-sig: #8794a3; --w-ph: #d39a62;
  --zone-p: #2a1d17; --zone-l: #172231; --pcb: #16291e; --pcb-line: #5fae7b; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 400 15.5px/1.55 var(--f-body); margin: 0; }
.pag { max-width: 1240px; margin: 0 auto; padding-inline: 20px; padding-block: 32px 64px; display: grid; gap: 44px; }
header.topo { display: grid; gap: 10px; padding-bottom: 20px; border-bottom: 2px solid var(--ink); }
.rot { font: 600 12px/1 var(--f-mono); letter-spacing: .08em; color: var(--accent); text-transform: uppercase; }
h1 { font: 600 clamp(28px, 4vw, 42px)/1.05 var(--f-disp); margin: 0; letter-spacing: -.01em; text-wrap: balance; }
.lede { max-width: 72ch; margin: 0; color: var(--muted); }
.fatos { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); margin-top: 8px; }
.fatos div { background: var(--paper); padding: 10px 12px; display: grid; gap: 2px; }
.fatos b { font: 500 16px/1.2 var(--f-mono); font-variant-numeric: tabular-nums; }
.fatos span { font-size: 12.5px; color: var(--muted); }
nav.ind { display: flex; flex-wrap: wrap; gap: 6px 16px; margin-top: 14px; font: 500 13px var(--f-mono); }
nav.ind a { color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--line); }
nav.ind a:hover, nav.ind a:focus-visible { border-color: var(--accent); color: var(--accent); }
section { display: grid; gap: 16px; min-width: 0; }
section > h2 { font: 600 26px/1.15 var(--f-disp); margin: 0; display: flex; gap: 12px; align-items: baseline; text-wrap: balance; }
section > h2 i { font: 500 13px var(--f-mono); color: var(--accent); font-style: normal; }
h3 { font: 600 18px/1.2 var(--f-disp); margin: 8px 0 0; }
p, ul, ol { margin: 0; max-width: 80ch; }
li + li { margin-top: 4px; }
code { font: 500 .88em var(--f-mono); background: var(--grid); padding: 1px 5px; border-radius: 3px; }
a { color: var(--accent); }
.fig { background: var(--paper); border: 1px solid var(--line); border-radius: 6px; overflow-x: auto;
  background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px); background-size: 20px 20px; }
.fig svg { display: block; width: 100%; min-width: 900px; height: auto; }
.fotos { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.fotos figure { margin: 0; background: #fff; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
.fotos img { display: block; width: 100%; height: auto; }
.fotos figcaption { font-size: 12.5px; color: #5b6774; padding: 6px 10px; background: #fff; }
.dois { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 24px; align-items: start; }
@media (max-width: 860px) { .dois { grid-template-columns: 1fr; } }
.resp { background: var(--paper); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 6px; padding: 16px 18px; display: grid; gap: 10px; }
.resp > p:first-child { font: 600 18px/1.35 var(--f-disp); }
.tab { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--paper); }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font: 600 11.5px var(--f-mono); letter-spacing: .04em; color: var(--muted); text-transform: uppercase; background: var(--bg); position: sticky; top: 0; }
tr:last-child td { border-bottom: 0; }
td.n { font-family: var(--f-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.c { font-family: var(--f-mono); color: var(--accent); white-space: nowrap; }
tr.g td { background: var(--accent-soft); font: 600 12px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--accent); }
.tag { font: 600 10.5px var(--f-mono); color: var(--accent); border: 1px solid var(--accent); border-radius: 3px; padding: 0 4px; margin-left: 6px; white-space: nowrap; }
.regras { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
.cartao { background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px; min-width: 0; display: grid; gap: 6px; align-content: start; }
.cartao h4 { font: 600 16px var(--f-disp); margin: 0; }
.cartao p { font-size: 14px; color: var(--muted); }
.conns { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.conn { background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; display: grid; gap: 4px; align-content: start; }
.conn header { display: flex; justify-content: space-between; align-items: baseline; font-family: var(--f-mono); }
.conn header b { color: var(--accent); font-size: 15px; } .conn header span { font-size: 12px; color: var(--muted); }
.conn h4 { margin: 0; font: 600 15px var(--f-disp); }
.conn ol { margin: 4px 0 0; padding-left: 22px; font: 400 12.5px var(--f-mono); }
.conn .lado { margin: 6px 0 0; font-size: 12px; color: var(--muted); display: grid; gap: 2px; }
.etapas { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; counter-reset: e; max-width: none; }
.etapas > li { counter-increment: e; background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 14px 16px 14px 62px; position: relative; }
.etapas > li::before { content: counter(e, decimal-leading-zero); position: absolute; left: 16px; top: 13px; font: 700 20px var(--f-mono); color: var(--accent); }
.etapas h4 { margin: 0 0 6px; font: 600 17px var(--f-disp); }
.etapas ol { padding-left: 20px; font-size: 14.5px; }
.etapas .ok { margin-top: 8px; font-size: 13.5px; color: var(--muted); }
.etapas .ok b { color: var(--w-33); }
.leg { display: flex; flex-wrap: wrap; gap: 6px 18px; font: 500 12.5px var(--f-mono); color: var(--muted); }
.leg span::before { content: ""; display: inline-block; width: 22px; height: 4px; border-radius: 2px; margin-right: 6px; vertical-align: middle; background: var(--c); }
.nota { font-size: 13.5px; color: var(--muted); }
footer { font-size: 13px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; }
"""


def h_tab(cab, linhas, cls_cols=None):
    cls_cols = cls_cols or {}
    o = '<div class="tab"><table><thead><tr>' + "".join(f"<th>{E(c)}</th>" for c in cab) + "</tr></thead><tbody>"
    for l in linhas:
        if isinstance(l, tuple) and len(l) == 2 and l[0] == "__grupo__":
            o += f'<tr class="g"><td colspan="{len(cab)}">{E(l[1])}</td></tr>'
            continue
        o += "<tr>" + "".join(f'<td class="{cls_cols.get(i, "")}">{c if str(c).startswith("<") else E(str(c))}</td>' for i, c in enumerate(l)) + "</tr>"
    return o + "</tbody></table></div>"


def img64(p, larg=1000):
    from PIL import Image
    import io
    im = Image.open(p).convert("RGB")
    im.thumbnail((larg, larg))
    b = io.BytesIO()
    im.save(b, "WEBP", quality=80, method=6)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()


def guia_html(med, linhas_imp, tot):
    fotos = ""
    for nome, leg in (("mvp_perspectiva", "Perspectiva, cabeça a 15°"), ("mvp_lado", "Lado, cabeça a 25°"),
                      ("mvp_traseira", "Traseira: giro e tilt"), ("mvp_giro", "Giro +12,5° e tilt 28°")):
        p = os.path.join(OUT, "modelo", nome + ".webp")
        if os.path.exists(p):
            fotos += f'<figure><img src="{img64(p, 900)}" alt="{E(leg)}" width="900" height="675"><figcaption>{E(leg)}</figcaption></figure>'
    imp = h_tab(["Arquivo", "Qtd", "Material", "Tamanho (mm)", "Massa", "Tempo", "Na mesa", "Configuração", "Observação"],
                [(l["arq"], l["q"], l["mat"], l["dims"], br(l["g"]) + " g", horas(l["h"]) + " h", l["ori"], l["cfg"], l["obs"]) for l in linhas_imp],
                {0: "c", 1: "n", 3: "n", 4: "n", 5: "n"})
    corte = h_tab(["Arquivo", "Qtd", "Material", "Esp.", "Tamanho (mm)", "Observação"],
                  [(f"{c}_{e}mm.dxf", q, m, f"{e} mm", dims(med[c]["formas"][0][0][:2]), o) for c, q, m, e, o in D.CORTE],
                  {0: "c", 1: "n", 3: "n", 4: "n"})
    usi = h_tab(["Peça", "Qtd", "Barra", "Comprimento", "O que fazer"], D.USINAGEM, {0: "c", 1: "n", 3: "n"})
    pinos = h_tab(["GPIO", "Função", "Tipo", "Na placa"], D.PINOS, {0: "c"})
    cx = h_tab(["Código", "Trecho", "Fio", "Compr.", "Observação"], D.CABOS_CAIXA, {0: "c", 3: "n"})
    cmd = h_tab(["Comando", "O que faz"], [(f"<code>{E(a)}</code>", b) for a, b in D.COMANDOS])
    conns = '<div class="conns">' + "".join(
        f'<article class="conn"><header><b>{E(c)}</b><span>{E(t_)}</span></header><h4>{E(f)}</h4><ol>'
        + "".join(f"<li>{E(p)}</li>" for p in ps) + f'</ol><p class="lado"><span>lançador: {E(a)}</span><span>caixa: {E(b)}</span></p></article>'
        for c, t_, f, ps, a, b in D.CONECTORES) + "</div>"
    lst = compras()
    bom = []
    for g in GRUPOS[:-1]:
        bom.append(("__grupo__", g))
        for _, i, e, q, c, o, n in [r for r in lst if r[0] == g]:
            tag = f' <span class="tag">{E(n)}</span>' if n else ""
            bom.append((f"{E(i)}{tag}" if tag else i, e, q, c, o))
    bom_h = h_tab(["Item", "Especificação", "Usa", "Comprar", "Onde vai"],
                  [tuple(("<span>" + x + "</span>") if (j == 0 and "<span" in str(x)) else x for j, x in enumerate(r)) if r[0] != "__grupo__" else r for r in bom],
                  {2: "n", 3: "n"})
    etapas = '<ol class="etapas">' + "".join(
        f'<li><h4>{E(tit)}</h4><ol>' + "".join(f"<li>{E(p)}</li>" for p in passos) + f'</ol><p class="ok"><b>Confira:</b> {E(ok)}</p></li>'
        for tit, passos, ok in MONTAGEM) + "</ol>"
    leg = '<div class="leg">' + "".join(f'<span style="--c: var({c})">{E(n)}</span>' for c, n in (
        ("--w-bat", "+BAT 19–24 V"), ("--w-mot", "+MOT (depois do K1)"), ("--w-ph", "fases dos motores"), ("--w-12", "12 V"),
        ("--w-6", "6 V servo"), ("--w-5", "5 V"), ("--w-33", "3V3"), ("--w-sig", "sinal"), ("--w-gnd", "GND"))) + "</div>"
    regras = "".join(f'<div class="cartao"><h4>{E(a)}</h4><p>{E(b)}</p></div>' for a, b in (
        ("Fonte de 19 a 24 V", "Nunca acima de 24 V: o MP1584 aceita 28 V e o TMC2209, 29 V. Comece com limite de 0,5 A; para as rodas, 5 A ou mais."),
        ("Freio dos ESCs desligado", "A fonte e o diodo ideal não aceitam corrente de volta. Ao frear, a energia das rodas subiria a tensão do barramento. Sem freio, as rodas param sozinhas; a 5.500 rpm o motor gera ~13,8 V, abaixo da fonte."),
        ("Emergência por hardware", "O contato NF do cogumelo está em série com a bobina do K1: apertado, os ESCs perdem a alimentação mesmo com o programa travado. O NA avisa o ESP32."),
        ("Um ponto de terra", "Todos os retornos chegam à barra GND. O negativo nunca é chaveado. O fio vermelho (BEC) do cabo de sinal dos ESCs fica isolado."),
        ("Motor de passo só desligado", "Ligue e solte o X3 só com a fonte desligada: soltar um motor com o driver energizado queima o driver."),
        ("Bucks antes da placa", "Ajuste 5,1 V, 6,0 V e 12,0 V no trimpot, sem carga, antes de ligar a placa e o servo."),
    ))
    mud = "".join(f"<li><b>{E(a)}:</b> {E(b)}</li>" for a, b in D.MUDANCAS_MAIN)
    depois = "".join(f"<li>{E(x)}</li>" for x in D.DEPOIS)
    nimp = sum(l["q"] for l in linhas_imp)
    return f"""<title>Lançador MVP de bancada</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@600&family=JetBrains+Mono:wght@500;600;700&display=swap">
<style>{CSS}{S.CSS_SVG}</style>
<div class="pag">
<header class="topo">
  <span class="rot">Lançador de bolas · branch mvp</span>
  <h1>MVP de bancada: base do lançador, giro, inclinação e cabeça</h1>
  <p class="lede">Só o que entra no primeiro teste, com fonte de bancada e bolas à mão. Cada peça, conector e rabicho de fio daqui é da máquina completa e continua nela; só a fonte, o cabo dela e a caixa da emergência são de bancada.</p>
  <div class="fatos">
    <div><b>{nimp}</b><span>peças impressas ({len(linhas_imp)} arquivos)</span></div>
    <div><b>{sum(q for _, q, *_ in D.CORTE)}</b><span>chapas a laser ({len(D.CORTE)} DXF)</span></div>
    <div><b>~9,8 kg</b><span>massa do MVP</span></div>
    <div><b>19–24 V</b><span>fonte de bancada, ≥ 5 A</span></div>
    <div><b>X1–X6</b><span>2 MT60 + 4 GX16-8</span></div>
    <div><b>{br(tot['h'][0])}–{br(tot['h'][1])} h</b><span>de impressora</span></div>
  </div>
  <nav class="ind" aria-label="Seções">
    <a href="#chapa">A chapa na mesa</a><a href="#ordem">Ordem</a><a href="#imprimir">Imprimir</a><a href="#cortar">Cortar e usinar</a>
    <a href="#eletrica">Elétrica</a><a href="#cabos">Cabos</a><a href="#simular">Simular</a><a href="#firmware">Firmware</a>
    <a href="#montar">Montar</a><a href="#lista">Lista unificada</a><a href="#mudou">O que mudou</a>
  </nav>
</header>

<section id="chapa">
  <h2><i>01</i>A chapa sozinha na mesa aguenta?</h2>
  <div class="dois">
    <div class="resp">
      <p>Aguenta o peso com folga, mas não deve ficar deitada direto na mesa.</p>
      <ul>
        <li><b>Peso:</b> o MVP tem ~9,8 kg. A chapa de 4 mm, apoiada nos 4 cantos, flete menos de 0,5 mm.</li>
        <li><b>Por que não deitada:</b> por baixo dela ficam as porcas do lazy susan, do suporte do motor do giro e do mancal do fuso; a chapa balançaria sobre elas.</li>
        <li><b>Como apoiar:</b> os 4 postes do andar de controle (perfil 20×20, 112 mm) viram pernas, com um pé de borracha M5 em cada. Depois eles voltam para o andar de controle.</li>
        <li><b>Estabilidade:</b> o centro de massa fica perto do meio, a 27–32 cm da mesa, dentro do retângulo de 270 × 380 mm das pernas. Não tomba nem no giro máximo.</li>
        <li><b>Vibração:</b> se a máquina "andar" com as rodas rápidas, parafuse as pernas numa tábua de MDF de 18 mm (~450 × 350) e prenda a tábua na mesa com 2 grampos C.</li>
      </ul>
    </div>
    <div class="fotos">{fotos}</div>
  </div>
</section>

<section id="ordem">
  <h2><i>02</i>Ordem sugerida</h2>
  <ol>
    <li><b>Comprar</b> o que demora: motores 4250, ESCs, NEMA17 com fuso, servo, lazy susan, mancais, polias e correias.</li>
    <li><b>Imprimir</b> começando pelos núcleos das rodas: ≈ {br(tot['PETG']/1000, 2)} kg de PETG e {br(tot['TPU']/1000, 2)} kg de TPU.</li>
    <li><b>Cortar e usinar</b> enquanto imprime, depois de conferir as furações das peças compradas.</li>
    <li><b>Elétrica na bancada</b>, sem a mecânica, um módulo por vez. Teste antes no Wokwi.</li>
    <li><b>Mecânica:</b> pernas, giro, garfos, rodas, cabeça.</li>
    <li><b>Juntar</b> pelos conectores X1–X6 e testar com as rodas devagar primeiro.</li>
  </ol>
</section>

<section id="imprimir">
  <h2><i>03</i>Impressão 3D</h2>
  <p>As peças saem na posição de montagem: gire no fatiador para a orientação da tabela. PETG a 235–245 °C e mesa a 75–85 °C; TPU a 20–30 mm/s. Sem suporte em todas. Massa e tempo são estimativas para bico 0,4 e camada 0,2.</p>
  {imp}
  <p class="nota">Total ≈ {br(tot['PETG'])} g de PETG e {br(tot['TPU'])} g de TPU. Compre 2 kg de PETG e 0,5 kg de TPU. Ordem: rodas, depois giro e tilt, depois o resto da cabeça, por último tampas e carenagens.</p>
</section>

<section id="cortar">
  <h2><i>04</i>Corte a laser e usinagem</h2>
  {corte}
  <p class="nota">Confira com a peça na mão: KFL001 (M6 a 48 mm), KFL08 (M4 a 37 mm), lazy susan (base r 66 girados 45°, plataforma r 60), X-mount do 4250 (oblongos M3 a r 19). Nenhuma chapa precisa de rosca.</p>
  {usi}
</section>

<section id="eletrica">
  <h2><i>05</i>Elétrica</h2>
  <p>Mesma arquitetura da máquina completa, com a fonte de bancada no lugar das baterias. O XT60 de entrada, o fusível de 30 A e o diodo ideal viram os da bateria A depois.</p>
  {leg}
  <h3>Potência</h3>
  <div class="fig">{S.svg_potencia()}</div>
  <div class="regras">{regras}</div>
  <h3>Sinais</h3>
  <div class="fig">{S.svg_sinais()}</div>
  {pinos}
  <p class="nota">Livres para a máquina completa: {E(D.PINOS_LIVRES)}.</p>
  <h3>Placa de controle</h3>
  <div class="fig">{S.svg_placa()}</div>
  <p class="nota">Monte na ordem: bornes e GND, barras de pinos, resistores e capacitores de cada entrada, IRLZ44N e 1N4007, JST-XH, eletrolíticos, jumper de endereço (MS1 do tilt no 3V3).</p>
</section>

<section id="cabos">
  <h2><i>06</i>Bancada e cabos</h2>
  <div class="fig">{S.svg_bancada()}</div>
  <p>Cada cabo entre o lançador e a caixa é feito de dois rabichos com o conector no meio. Os comprimentos já são os da máquina completa: quando os andares forem montados, o soquete vai para o suporte do andar e nenhum fio é refeito.</p>
  {conns}
  <h3>Dentro da caixa</h3>
  {cx}
</section>

<section id="simular">
  <h2><i>07</i>Simulação no Wokwi</h2>
  <div class="dois">
    <div class="cartao">
      <h4>Abrir</h4>
      <ol>
        <li>Entre em <a href="https://wokwi.com/projects/new/esp32-s3">wokwi.com/projects/new/esp32-s3</a>.</li>
        <li>Cole <code>sketch.ino</code> e <code>diagram.json</code> da pasta <code>5-eletrica/wokwi</code> nas abas de mesmo nome.</li>
        <li>Crie <code>libraries.txt</code> com <code>ESP32Servo</code> e <code>AccelStepper</code>.</li>
        <li>▶ e digite <code>ajuda</code> no monitor serial.</li>
      </ol>
      <p>O Tinkercad não tem ESP32; o Wokwi roda o mesmo programa, com <code>#define SIMULACAO</code> trocando os TMC2209 por A4988.</p>
    </div>
    {h_tab(["No simulador", "Na máquina"], [("Servos vermelhos escA e escB", "ESCs das rodas (o ponteiro é o acelerador)"), ("Servo azul", "empurrador"), ("A4988 + motores", "TMC2209 + NEMA17 do giro e do tilt"), ("Relé + LED +MOT", "K1 e barra +MOT"), ("Botão vermelho", "emergência (NA, GPIO41)"), ("Chave deslizante", "microchave do giro: direita = acionada")])}
  </div>
  <p class="nota">Roteiro: <code>prende</code>, <code>ref</code> (passe a chave para a direita durante o movimento), <code>giro 10</code>, <code>tilt 30</code>, <code>armar</code>, <code>tiro 60 1500</code>, <code>disparo</code>, e o botão vermelho para ver tudo parar.</p>
</section>

<section id="firmware">
  <h2><i>08</i>Firmware</h2>
  <p>Arduino IDE com o pacote esp32 3.x; bibliotecas ESP32Servo, AccelStepper e TMCStepper; placa ESP32S3 Dev Module, Flash 8MB, PSRAM OPI. Monitor serial a 115.200 com “Nova linha”.</p>
  {cmd}
</section>

<section id="montar">
  <h2><i>09</i>Montagem e primeiros testes</h2>
  <p>Cada etapa termina com uma conferência; só siga quando ela der certo.</p>
  {etapas}
</section>

<section id="lista">
  <h2><i>10</i>Lista unificada do MVP</h2>
  <p>Uma linha por item igual, somando todas as peças do MVP. <b>Usa</b> é o que vai na máquina; <b>Comprar</b> inclui reserva e o tamanho de venda. Itens marcados <span class="tag">só bancada</span> não vão para a máquina completa. A mesma lista está em <code>4-comprar/lista_mvp.csv</code>.</p>
  {bom_h}
</section>

<section id="mudou">
  <h2><i>11</i>O que o MVP mudou no projeto</h2>
  <p>Correções que valem para a máquina toda. Já estão nos arquivos da branch <code>mvp</code>; a <code>main</code> ainda não tem.</p>
  <ul>{mud}</ul>
  <h3>Fica para depois</h3>
  <ul>{depois}</ul>
</section>
<footer>Gerado de <code>cad/mvp/docs/gerar_docs.py</code> na branch <code>mvp</code>. Medidas e massas saem do modelo CadQuery.</footer>
</div>
"""


# ----------------------------------------------------------------------------- principal
def main():
    med = medir()
    linhas_imp, tot = linhas_impressao(med)
    _TOT.update(tot)
    escrever("README.md", md_raiz(med, tot))
    escrever("1-imprimir/LEIAME.md", md_imprimir(linhas_imp, tot))
    escrever("2-cortar/LEIAME.md", md_cortar(med))
    escrever("3-usinar/LEIAME.md", md_usinar())
    escrever("4-comprar/LEIAME.md", md_comprar(med, linhas_imp))
    csv_comprar(med, linhas_imp)
    escrever("5-eletrica/LEIAME.md", md_eletrica())
    for i, n in enumerate(("potencia", "sinais", "placa", "bancada"), 1):
        escrever(f"5-eletrica/{i}-{n}.svg", S.avulso(getattr(S, "svg_" + n)()))
    wokwi()
    fw = os.path.join(OUT, "6-firmware", "mvp_bancada")
    os.makedirs(fw, exist_ok=True)
    shutil.copy(os.path.join(MVP, "firmware", "mvp_bancada", "mvp_bancada.ino"), fw)
    escrever("6-firmware/LEIAME.md", md_firmware())
    escrever("7-montar/LEIAME.md", md_montar())
    escrever("modelo/LEIAME.md", md_modelo())
    # código-fonte
    cad = os.path.join(OUT, "cad")
    if os.path.isdir(cad):
        shutil.rmtree(cad)
    os.makedirs(os.path.join(cad, "mvp", "docs"))
    for f in ("lancador.py", "exportar.py", "verificar.py"):
        shutil.copy(os.path.join(V2, f), cad)
    for f in ("mvp.py", "exportar_mvp.py", "verificar_mvp.py"):
        shutil.copy(os.path.join(MVP, f), os.path.join(cad, "mvp"))
    for f in ("dados_mvp.py", "svg_mvp.py", "gerar_docs.py"):
        shutil.copy(os.path.join(AQUI, f), os.path.join(cad, "mvp", "docs"))
    os.makedirs(os.path.join(cad, "mvp", "firmware", "mvp_bancada"))
    shutil.copy(os.path.join(MVP, "firmware", "mvp_bancada", "mvp_bancada.ino"), os.path.join(cad, "mvp", "firmware", "mvp_bancada"))
    escrever("cad/LEIAME.md", md_cad())
    escrever("guia_mvp.html", guia_html(med, linhas_imp, tot))
    print("docs ok:", OUT, f"PETG {tot['PETG']:.0f} g, TPU {tot['TPU']:.0f} g, {tot['h'][0]:.0f}-{tot['h'][1]:.0f} h")


if __name__ == "__main__":
    main()
