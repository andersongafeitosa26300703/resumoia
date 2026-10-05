"""Interpreta a resposta de aprovacao (e-mail respondido vira comentario na Issue).

Le o texto do comentario em COMMENT_BODY e escreve decision=approve|reject|unknown em GITHUB_OUTPUT.
Vale so a primeira linha com texto; acentos e maiusculas sao ignorados.
"""
import os
import re
import sys
import unicodedata

APPROVE = {"ok", "sim", "aprovado", "aprovar", "aprova", "publica", "publicar", "pode", "okay", "blz", "beleza"}
REJECT = {"nao", "n", "reprovado", "reprovar", "reprova", "cancelar", "cancela", "descartar", "descarta"}


def decide(body):
    for line in (body or "").replace("\r", "").split("\n"):
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        norm = unicodedata.normalize("NFKD", line).encode("ascii", "ignore").decode().lower()
        words = re.findall(r"[a-z]+", norm)
        if not words:
            return "unknown"
        first = words[0]
        if first in APPROVE:
            return "approve"
        if first in REJECT:
            return "reject"
        return "unknown"
    return "unknown"


if __name__ == "__main__":
    result = decide(os.environ.get("COMMENT_BODY", ""))
    print(f"decision={result}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"decision={result}\n")
    sys.exit(0)
