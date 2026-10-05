"""Revisao do rascunho a pedido do dono (por resposta de e-mail).

  python scripts/revise.py remove AAAA-MM-DD CARD   remove o card (slide) CARD
  python scripts/revise.py prep   AAAA-MM-DD ESCOPO prepara a troca: ESCOPO = all | capa | card:N
                                                    (guarda as noticias descartadas em rejected.json)

Escreve em GITHUB_OUTPUT: ok=true|false, msg=<mensagem para o dono> e, no prep, scope=<texto para o editor>.
Card 1 e a capa; os cards 2..N+1 sao as noticias 1..N.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def out(**kw):
    path = os.environ.get("GITHUB_OUTPUT")
    lines = "".join(f"{k}={str(v).replace(chr(10), ' ')}\n" for k, v in kw.items())
    print(lines, end="")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(lines)


def load(date):
    p = ROOT / "drafts" / date / "data.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8")), p
    t = ROOT / "data" / "today.json"
    if t.exists():
        d = json.loads(t.read_text(encoding="utf-8"))
        if d.get("date") == date:
            return d, p
    out(ok="false", msg=f"Nao achei os dados do rascunho de {date}.")
    sys.exit(0)


def main():
    cmd, date = sys.argv[1], sys.argv[2]
    arg = sys.argv[3] if len(sys.argv) > 3 else ""
    data, path = load(date)
    items = data["items"]

    if cmd == "remove":
        card = int(arg)
        if not 2 <= card <= len(items) + 1:
            return out(ok="false", msg=f"Card {card} invalido. Use de 2 a {len(items) + 1} (o 1 e a capa).")
        if len(items) <= 3:
            return out(ok="false", msg="O carrossel precisa de pelo menos 3 noticias; nao da para remover mais.")
        gone = items.pop(card - 2)
        rej = ROOT / "drafts" / date / "rejected.json"
        old = json.loads(rej.read_text(encoding="utf-8")) if rej.exists() else []
        rej.write_text(json.dumps(old + [gone["link"]], ensure_ascii=False, indent=2), encoding="utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return out(ok="true", msg=f"Removi o card {card}: {gone['title']}")

    if cmd == "prep":
        if arg == "all":
            gone, scope = [it["link"] for it in items], "TODAS as noticias, a manchete (headline) e a intro"
        elif arg == "capa":
            gone, scope = [], "SOMENTE a manchete (headline) e a intro (capa); mantenha as noticias como estao"
        else:
            card = int(arg.split(":")[1])
            if not 2 <= card <= len(items) + 1:
                return out(ok="false", msg=f"Card {card} invalido. Use de 1 a {len(items) + 1}.")
            it = items[card - 2]
            gone, scope = [it["link"]], f"SOMENTE a noticia {card - 1} (card {card}): a de titulo \"{it['title']}\"; mantenha as demais"
        rej = ROOT / "drafts" / date / "rejected.json"
        old = json.loads(rej.read_text(encoding="utf-8")) if rej.exists() else []
        rej.parent.mkdir(parents=True, exist_ok=True)
        rej.write_text(json.dumps(old + gone, ensure_ascii=False, indent=2), encoding="utf-8")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return out(ok="true", scope=scope, msg="ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
