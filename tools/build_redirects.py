"""Short links for GitHub Pages (no server redirects there).

Source of truth: redirects.txt at the repo root, one line per link:
    /b/brain-fog    /authors/claire-harmon.html?utm_source=book&utm_medium=qr&utm_campaign=brain-fog
Each line becomes <path>/index.html that forwards at once (meta refresh + location.replace) and is not indexed.
The printed QR codes point at these paths, so the destination can change here without reprinting.

    python tools/build_redirects.py
"""
import html
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "redirects.txt"
MANIFEST = ROOT / "tools" / ".redirects-generated"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Bloom Editorial</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={dest}">
<script>location.replace({dest_js});</script>
</head><body><p><a href="{dest}">Continue to Bloom Editorial</a></p></body></html>
"""


def entries():
    for line in SRC.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        src, dest = parts[0], parts[1]
        if not src.startswith("/") or ".." in src:
            raise SystemExit(f"bad source path: {src}")
        yield src.strip("/"), dest


def main():
    old = MANIFEST.read_text(encoding="utf-8").split() if MANIFEST.exists() else []
    made = []
    for src, dest in entries():
        d = ROOT / src
        d.mkdir(parents=True, exist_ok=True)
        js = '"' + dest.replace("\\", "\\\\").replace('"', '\\"') + '"'
        (d / "index.html").write_text(PAGE.format(dest=html.escape(dest, quote=True), dest_js=js), encoding="utf-8")
        made.append(src)
    for gone in set(old) - set(made):          # a link removed from redirects.txt
        p = ROOT / gone
        if p.is_dir() and (p / "index.html").exists() and len(list(p.iterdir())) == 1:
            shutil.rmtree(p)
    MANIFEST.write_text("\n".join(made) + "\n", encoding="utf-8")
    print(f"{len(made)} short links: " + ", ".join("/" + m for m in made))


if __name__ == "__main__":
    main()
