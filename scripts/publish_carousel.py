"""Publica no Instagram o rascunho aprovado de uma data.

Uso: python scripts/publish_carousel.py AAAA-MM-DD
Requer: IG_ACCESS_TOKEN (e opcionalmente IG_USER_ID), GITHUB_REPOSITORY.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
POSTED = ROOT / "data" / "posted.json"


def main(date):
    posted = json.loads(POSTED.read_text(encoding="utf-8")) if POSTED.exists() else {}
    if date in posted:
        print(f"{date} ja foi publicado ({posted[date]['media_id']}); nada a fazer.")
        return

    folder = ROOT / "drafts" / date
    slides = sorted(folder.glob("slide-*.jpg"))
    if not slides:
        sys.exit(f"Nao ha rascunho em {folder}")
    caption = (folder / "caption.txt").read_text(encoding="utf-8")

    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    urls = [f"https://raw.githubusercontent.com/{repo}/{branch}/drafts/{date}/{p.name}" for p in slides]

    user_id = ig.clean_secret(os.environ.get("IG_USER_ID", ""))
    token = ig.clean_secret(os.environ["IG_ACCESS_TOKEN"])
    user_id, token = ig.resolve_ig(user_id, token)

    media_id = ig.publish_carousel(user_id, token, urls, caption)
    posted[date] = {"media_id": media_id, "at": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds")}
    POSTED.write_text(json.dumps(posted, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Carrossel de {date} publicado: media_id={media_id}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/publish_carousel.py AAAA-MM-DD")
    main(sys.argv[1])
