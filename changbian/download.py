"""Download all extant juan of 續資治通鑑長編 (四庫全書本) from
Chinese Wikisource via the MediaWiki API, and cache the raw wikitext.

513 of 520 juan exist (missing 25, 141, 180, 302, 359, 366, 383, lost
already in the transmitted edition). Output: data/raw_pages.json.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "data" / "raw_pages.json"
PREFIX = "續資治通鑑長編 (四庫全書本)/卷"
UA = {"User-Agent": "DH-research/1.0 (student collocation analysis)"}


def api(params):
    url = "https://zh.wikisource.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req))


def list_titles():
    titles, apfrom = [], None
    while True:
        p = {"action": "query", "list": "allpages", "aplimit": 500,
             "format": "json", "apprefix": PREFIX}
        if apfrom:
            p["apfrom"] = apfrom
        d = api(p)
        titles += [x["title"] for x in d["query"]["allpages"]]
        if "continue" in d:
            apfrom = d["continue"]["apcontinue"]
        else:
            return titles


def fetch(titles):
    pages = {}
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        d = api({"action": "query", "prop": "revisions", "rvprop": "content",
                 "rvslots": "main", "format": "json",
                 "titles": "|".join(batch)})
        for _, p in d["query"]["pages"].items():
            if "revisions" in p:
                pages[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
        print(f"{min(i+50, len(titles))}/{len(titles)} juan fetched",
              flush=True)
        time.sleep(1)
    return pages


def main():
    titles = sorted(
        (t for t in list_titles() if re.search(r"卷\d+$", t)),
        key=lambda t: int(re.search(r"卷(\d+)$", t).group(1)),
    )
    print("juan pages:", len(titles))
    pages = fetch(titles)
    OUT.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    chars = sum(len(w) for w in pages.values())
    print(f"wrote {OUT}: {len(pages)} juan, {chars} wikitext chars")


if __name__ == "__main__":
    main()
