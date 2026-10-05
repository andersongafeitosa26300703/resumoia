"""Interpreta a resposta de aprovacao (e-mail respondido vira comentario na Issue).

Le o texto do comentario em COMMENT_BODY e escreve em GITHUB_OUTPUT:
  decision = approve | reject | redo | remove | unknown
  card     = numero do card (slide) quando decision for redo ou remove

Vale so a primeira linha com texto (linhas citadas com ">" sao ignoradas); acentos e maiusculas nao importam.
  OK / sim / aprovado          -> approve
  NAO / reprovado              -> reject  (refaz o carrossel inteiro)
  refaca 3 / troca o card 3    -> redo, card 3
  remova 4 / tira o 4          -> remove, card 4
"""
import os
import re
import sys
import unicodedata

APPROVE = {"ok", "sim", "aprovado", "aprovar", "aprova", "publica", "publicar", "pode", "okay", "blz", "beleza"}
REJECT = {"nao", "n", "reprovado", "reprovar", "reprova", "cancelar", "cancela", "descartar", "descarta"}
REDO = {"refaca", "refaz", "refazer", "refacam", "troca", "trocar", "troque", "substituir", "substitui", "substitua", "mude", "muda", "mudar"}
REMOVE = {"remova", "remove", "remover", "tira", "tirar", "tire", "retire", "retirar", "exclua", "exclui", "excluir", "apague", "apaga", "apagar"}


def first_line(body):
    for line in (body or "").replace("\r", "").split("\n"):
        line = line.strip()
        if line and not line.startswith(">"):
            return line
    return ""


def decide(body):
    """Retorna (decision, card) com card int ou None."""
    line = first_line(body)
    if not line:
        return "unknown", None
    norm = unicodedata.normalize("NFKD", line).encode("ascii", "ignore").decode().lower()
    words = re.findall(r"[a-z]+", norm)
    nums = re.findall(r"\d+", norm)
    card = int(nums[0]) if nums else None
    if any(w in REMOVE for w in words):
        return ("remove", card) if card else ("unknown", None)
    if any(w in REDO for w in words):
        # "refaca 3" troca um card; "refaca" sem numero (ou "refaca tudo") refaz o carrossel inteiro
        return ("redo", card) if card else ("reject", None)
    if not words:
        return "unknown", None
    if words[0] in APPROVE:
        return "approve", None
    if words[0] in REJECT:
        return "reject", None
    return "unknown", None


if __name__ == "__main__":
    decision, card = decide(os.environ.get("COMMENT_BODY", ""))
    print(f"decision={decision} card={card or ''}")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"decision={decision}\ncard={card or ''}\n")
    sys.exit(0)
