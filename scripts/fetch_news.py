"""Coleta as noticias recentes dos feeds RSS configurados e grava data/candidates.json."""
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; noticias-ia/1.0)"


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(s):
    try:
        dt = parsedate_to_datetime(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


ATOM = "{http://www.w3.org/2005/Atom}"


def parse_iso(s):
    try:
        dt = datetime.fromisoformat((s or "").replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def strip_source(title, source):
    """O Google Noticias termina o titulo com ' - Veiculo'."""
    for suffix in (f" - {source}", f" | {source}"):
        if title.endswith(suffix):
            return title[: -len(suffix)].strip()
    return re.sub(r"\s+-\s+[^-]{2,40}$", "", title).strip() if feed_is_google(title) else title


def feed_is_google(_title):
    return False


def fetch_feed(feed):
    req = urllib.request.Request(feed["url"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):  # RSS
        source = clean(it.findtext("source")) or feed["name"]
        title = strip_source(clean(it.findtext("title")), source)
        link = (it.findtext("link") or "").strip()
        pub = parse_date(it.findtext("pubDate"))
        desc = clean(it.findtext("description"))
        if feed["name"] == "Google Notícias":
            desc = ""  # a descricao do Google so repete titulo e veiculo
        if title and link and pub:
            items.append({"title": title, "link": link, "published": pub, "summary": desc[:500], "source": source, "feed": feed["name"]})
    for it in root.iter(ATOM + "entry"):  # Atom (The Verge)
        title = clean(it.findtext(ATOM + "title"))
        link_el = it.find(ATOM + "link")
        link = (link_el.get("href") if link_el is not None else "") or ""
        pub = parse_iso(it.findtext(ATOM + "published") or it.findtext(ATOM + "updated"))
        desc = clean(it.findtext(ATOM + "summary") or it.findtext(ATOM + "content"))
        if title and link and pub:
            items.append({"title": title, "link": link, "published": pub, "summary": desc[:500], "source": feed["name"], "feed": feed["name"]})
    return items


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=cfg["max_age_hours"])
    seen, out = set(), []
    for feed in cfg["feeds"]:
        try:
            items = fetch_feed(feed)
        except Exception as e:
            print(f"[aviso] feed '{feed['name']}' falhou: {e}", file=sys.stderr)
            continue
        for it in items:
            key = re.sub(r"\W+", "", it["title"].lower())[:60]
            if it["published"] < cutoff or key in seen:
                continue
            seen.add(key)
            it["published"] = it["published"].isoformat()
            out.append(it)
    out.sort(key=lambda x: x["published"], reverse=True)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(out)} noticias candidatas gravadas em data/candidates.json")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
