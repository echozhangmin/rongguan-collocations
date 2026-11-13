"""Clean the raw wikitext of 續資治通鑑長編 (四庫全書本).

The 四庫 transcription is unpunctuated continuous prose. Per juan:
 - main text   -> data/changbian_main.txt  (one line per juan, juan order)
 - 李燸's own notes ({{SK notes|...}}, the small-character annotations that
   give the work much of its value) -> data/changbian_notes.txt
   (one note per line, prefixed with the juan number)
 - data/manifest.json maps line numbers to juan numbers.

Template handling: {{YL|X}} -> X (era-year); {{SKchar|N}}/{{SKchar2|N}}
-> □ (character not in the transcription); {{SK anchor|...}},
{{SKQS header/footer}}, {{PD-old}} removed; [[a|b]] -> b.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw_pages.json"

POEM = re.compile(r"<onlyinclude>\s*<poem>(.*?)</poem>\s*</onlyinclude>", re.S)


def find_template_end(text, start):
    """start points at the '{' of '{{'. Return index after the matching '}}'
    (handles nested {{...}})."""
    depth, i = 0, start
    while i < len(text) - 1:
        if text[i:i + 2] == "{{":
            depth += 1
            i += 2
        elif text[i:i + 2] == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return i
        else:
            i += 1
    return len(text)


def inner_of(text):
    """Content of one template call 'text' (including braces), split at the
    first top-level '|'."""
    body = text[2:-2]
    depth, buf = 0, ""
    for ch in body:
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        if ch == "|" and depth == 0:
            return buf, body[len(buf) + 1:]
        buf += ch
    return buf, ""


def render(content):
    """Recursively render wikitext fragment: keep YL years, drop anchors
    and header/footer templates, SKchar -> □, wikilinks -> display text."""
    out, i = [], 0
    while i < len(content):
        if content[i:i + 2] == "{{":
            end = find_template_end(content, i)
            tpl = content[i:end]
            name, rest = inner_of(tpl)
            name = name.strip()
            if name in ("YL",):
                out.append(rest.strip())
            elif name in ("SKchar", "SKchar2"):
                out.append("□")
            elif name in ("SK anchor", "SKQS header", "SKQS footer",
                          "PD-old"):
                pass
            else:  # unknown template: render its first argument
                out.append(rest.strip())
            i = end
        elif content[i:i + 2] == "[[":
            end = content.find("]]", i)
            end = len(content) if end == -1 else end + 2
            link = content[i + 2:end - 2]
            out.append(link.split("|")[-1])
            i = end
        elif content[i:i + 4] == "<!--":
            end = content.find("-->", i)
            i = len(content) if end == -1 else end + 3
        else:
            out.append(content[i])
            i += 1
    return "".join(out)


def clean_juan(wikitext):
    m = POEM.search(wikitext)
    content = m.group(1) if m else wikitext

    main_parts, notes = [], []
    i = 0
    while i < len(content):
        if content[i:i + 2] == "{{":
            end = find_template_end(content, i)
            tpl = content[i:end]
            name, rest = inner_of(tpl)
            name = name.strip()
            if name == "SK notes":
                notes.append(render(rest))
            else:
                main_parts.append(render(tpl))
            i = end
        elif content[i:i + 2] == "[[":
            end = content.find("]]", i)
            end = len(content) if end == -1 else end + 2
            link = content[i + 2:end - 2]
            main_parts.append(link.split("|")[-1])
            i = end
        elif content[i:i + 4] == "<!--":
            end = content.find("-->", i)
            i = len(content) if end == -1 else end + 3
        else:
            main_parts.append(content[i])
            i += 1

    text = "".join(main_parts)
    text = text.replace("　", "")
    # drop the per-juan Siku page header
    for drop in ("欽定四庫全書", "宋李燾撰", "宋李燾撰"):
        text = text.replace(drop, "")
    text = re.sub(r"\s+", "", text)

    notes = [re.sub(r"\s+", "", n).replace("　", "") for n in notes]
    return text, [n for n in notes if n]


def main():
    pages = json.loads(RAW.read_text(encoding="utf-8"))
    titles = sorted(pages, key=lambda t: int(re.search(r"卷(\d+)$", t).group(1)))

    main_lines, note_lines, manifest = [], [], []
    for t in titles:
        juan = int(re.search(r"卷(\d+)$", t).group(1))
        text, notes = clean_juan(pages[t])
        manifest.append(juan)
        main_lines.append(text)
        note_lines += [f"卷{juan}\t{n}" for n in notes]

    (HERE / "data" / "changbian_main.txt").write_text(
        "\n".join(main_lines), encoding="utf-8")
    (HERE / "data" / "changbian_notes.txt").write_text(
        "\n".join(note_lines) + "\n", encoding="utf-8")
    (HERE / "data" / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8")

    n_main = sum(len(l) for l in main_lines)
    n_notes = sum(len(l.split("\t", 1)[-1]) for l in note_lines)
    print(f"juan: {len(main_lines)}")
    print(f"main text chars: {n_main}")
    print(f"notes: {len(note_lines)} lines, {n_notes} chars")
    print(f"main 冗官 hits: {sum(l.count('冗官') for l in main_lines)}")
    print(f"notes 冗官 hits: "
          f"{sum(l.count('冗官') for l in note_lines)}")


if __name__ == "__main__":
    main()
