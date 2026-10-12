"""Atualiza a pasta POSTS/ com um subdiretorio por dia (slides + legenda), para publicar na mao.

Uso: python scripts/sync_posts.py   (faz git pull antes)
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "POSTS"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    subprocess.run(["git", "pull", "-q", "--rebase", "--autostash", "origin", "main"], cwd=ROOT)
    OUT.mkdir(exist_ok=True)
    n = 0
    for d in sorted((ROOT / "drafts").iterdir()):
        slides = sorted(d.glob("slide-*.jpg"))
        if not slides:
            continue
        dest = OUT / d.name
        dest.mkdir(exist_ok=True)
        for s in slides:
            shutil.copy2(s, dest / s.name)
        cap = d / "caption.txt"
        if cap.exists():
            shutil.copy2(cap, dest / "legenda.txt")
        n += 1
        print(f"{d.name}: {len(slides)} imagens + legenda")
    print(f"Pronto: {n} dias em {OUT}")


if __name__ == "__main__":
    main()
