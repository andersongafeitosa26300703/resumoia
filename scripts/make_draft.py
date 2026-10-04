"""Le data/today.json (escrito pela rotina do Claude), valida e gera o rascunho:
drafts/AAAA-MM-DD/slide-01..05.jpg, caption.txt e issue.md (corpo da Issue de aprovacao).

Uso: python scripts/make_draft.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_carousel import render_all  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def validate(data):
    errs = []
    if not data.get("date"):
        errs.append("falta 'date'")
    if not data.get("headline") or len(data["headline"]) > 110:
        errs.append("'headline' ausente ou com mais de 110 caracteres")
    items = data.get("items", [])
    if not 3 <= len(items) <= 5:
        errs.append(f"esperado entre 3 e 5 noticias, veio {len(items)}")
    for i, it in enumerate(items, 1):
        if not it.get("title") or len(it["title"]) > 95:
            errs.append(f"noticia {i}: titulo ausente ou longo demais (>95)")
        if not it.get("summary") or len(it["summary"]) > 300:
            errs.append(f"noticia {i}: resumo ausente ou longo demais (>300)")
        if not it.get("source"):
            errs.append(f"noticia {i}: falta a fonte")
        if not str(it.get("link", "")).startswith("http"):
            errs.append(f"noticia {i}: falta o link")
    return errs


def build_caption(data, cfg):
    lines = [data.get("intro") or f"As principais notícias de {cfg['topic']} de hoje:"]
    lines.append("")
    for i, it in enumerate(data["items"], 1):
        lines.append(f"{i}. {it['title']} ({it['source']})")
    lines += ["", "Salve para ler depois e siga para receber o resumo todo dia.", "", " ".join(cfg["hashtags"])]
    return "\n".join(lines)


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "today.json").read_text(encoding="utf-8"))
    errs = validate(data)
    if errs:
        sys.exit("today.json invalido:\n- " + "\n- ".join(errs))

    out = ROOT / "drafts" / data["date"]
    paths = render_all(data, cfg, out)
    caption = build_caption(data, cfg)
    (out / "caption.txt").write_text(caption, encoding="utf-8")

    repo = os.environ.get("GITHUB_REPOSITORY", "USUARIO/REPO")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    base = f"https://raw.githubusercontent.com/{repo}/{branch}/drafts/{data['date']}"
    md = [f"## Rascunho do carrossel de {data['date']}", ""]
    md += [f"![slide {i}]({base}/{p.name})" for i, p in enumerate(paths, 1)]
    md += ["", "### Legenda", "```", caption, "```", "", "### Fontes"]
    md += [f"- {it['source']}: {it['link']}" for it in data["items"]]
    md += ["", "---", "**Para aprovar e publicar:** adicione o rótulo **`aprovado`** a esta Issue (no app do GitHub: ícone de rótulos). Para descartar, feche a Issue sem rótulo."]
    (out / "issue.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Rascunho de {data['date']} gerado em {out} ({len(paths)} imagens)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
