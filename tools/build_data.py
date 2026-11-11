"""Extrai os dados da planilha SKYTALE (xlsx exportado) para data.json da dashboard."""
import json, sys, datetime
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else "data/sky.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data.json"
wb = openpyxl.load_workbook(SRC, data_only=True)


def d(v):
    """Normaliza datas para AAAA-MM-DD."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime.datetime):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    if len(s) == 10 and s[2] == "/":  # dd/mm/aaaa
        return f"{s[6:]}-{s[3:5]}-{s[:2]}"
    return s[:10]


def n(v):
    if v in (None, "", "–", "-"):
        return 0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0


def rows(name, start=2):
    ws = wb[name]
    for r in ws.iter_rows(min_row=start, values_only=True):
        if r and any(x not in (None, "") for x in r):
            yield r


SH = ["Raident", "Transparo", "Murki", "Devine", "Celesto"]
cfg = {r[0]: r[1] for r in rows("CONFIG")}
comp = str(cfg.get("Competência ativa", "2026-11"))

# Membros
members = []
for r in rows("MEMBROS"):
    if not r[0]:
        continue
    members.append({"id": r[0], "nick": r[1], "classe": r[2] or "", "cla": r[3] or "",
                    "situacao": r[4] or "", "obs": r[5] or ""})
mem_by_id = {m["id"]: m for m in members}

# Obrigações da competência
obrig = []
for r in rows("OBRIGACOES"):
    if not r[1] or str(r[0]) != comp:
        continue
    o = {"id": r[1], "nick": r[2], "cla": r[3], "status": r[18],
         "gold_dev": n(r[4]), "sh_dev": [n(x) for x in r[5:10]], "coins_dev": n(r[10]),
         "gold_rec": n(r[11]), "sh_rec": [n(x) for x in r[12:17]], "coins_rec": n(r[17])}
    o["falta_gold"] = max(0, o["gold_dev"] - o["gold_rec"])
    o["falta_sh"] = [max(0, a - b) for a, b in zip(o["sh_dev"], o["sh_rec"])]
    o["falta_coins"] = max(0, o["coins_dev"] - o["coins_rec"])
    m = mem_by_id.get(o["id"], {})
    o["classe"] = m.get("classe", "")
    o["cla_atual"] = m.get("cla", "")
    o["situacao"] = m.get("situacao", "")
    obrig.append(o)

# Recebimentos
receb = []
for r in rows("RECEBIMENTOS"):
    if not r[2]:
        continue
    receb.append({"data": d(r[0]), "comp": str(r[1]), "id": r[2], "nick": r[3],
                  "gold": n(r[4]), "sh": [n(x) for x in r[5:10]], "coins": n(r[10]), "obs": r[11] or ""})

# Caixas
gold = []
for r in rows("CAIXA GOLD"):
    if not r[1]:
        continue
    gold.append({"data": d(r[0]), "tipo": r[1], "desc": r[2], "valor": n(r[3]), "resp": r[4] or "",
                 "cat": r[5] or "", "obs": r[6] or "", "saldo": n(r[7])})
coins = []
for r in rows("CAIXA COINS"):
    if not r[1]:
        continue
    coins.append({"data": d(r[0]), "tipo": r[1], "desc": r[2], "valor": n(r[3]), "resp": r[4] or "",
                  "obs": r[5] or "", "saldo": n(r[6])})

# Saídas de Sheltons
saidas = []
for r in rows("SAÍDAS SHELTONS"):
    if not r[1]:
        continue
    saidas.append({"data": d(r[0]), "tipo": r[1], "id": r[2] or "", "nick": r[3],
                   "sh": [n(x) for x in r[4:9]], "fim": r[10] or "", "obs": r[11] or ""})

# Bless Castle
bc = []
for r in rows("BC RESULTADOS"):
    if not r[0] or not r[1]:
        continue
    bc.append({"data": d(r[0]), "nick": r[1], "classe": r[2] or "", "pontos": n(r[3]),
               "pos": int(n(r[4])), "cla": r[5] or "", "id": r[7] or "", "chave": r[9] or r[1]})

# Dungeon
dg = []
for r in rows("DG REGISTROS"):
    if not r[0]:
        continue
    dg.append({"data": d(r[0]), "cla": r[1], "nick": r[2], "id": r[3] or "", "chave": r[4] or r[2]})

out = {
    "gerado_em": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M"),
    "competencia": comp,
    "config": {"gold": n(cfg.get("Gold por player (kk)")), "sheltons": n(cfg.get("Sheltons por tipo")),
               "coins_phoenix": n(cfg.get("Coins PHOENIX"))},
    "sheltons": SH,
    "membros": members, "obrigacoes": obrig, "recebimentos": receb,
    "caixa_gold": gold, "caixa_coins": coins, "saidas_sheltons": saidas,
    "bc": bc, "dg": dg,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

# Conferência rápida
st = {}
for o in obrig:
    st[o["status"]] = st.get(o["status"], 0) + 1
print("competência", comp, "| obrigações", len(obrig), st)
print("gold saldo", gold[-1]["saldo"], "| coins saldo", coins[-1]["saldo"])
print("sheltons rec (comp)", sum(sum(min(a, b) for a, b in zip(o["sh_rec"], o["sh_dev"])) for o in obrig),
      "| sh rec bruto", sum(sum(o["sh_rec"]) for o in obrig))
print("membros ativos", sum(1 for m in members if m["situacao"] == "Ativo"))
print("bc linhas", len(bc), "| dg linhas", len(dg), "| saídas", len(saidas))
