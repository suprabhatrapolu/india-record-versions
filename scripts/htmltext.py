"""Extract readable text from a saved HTML file (strip tags, collapse whitespace)."""
import re
import html
import sys


def extract(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    body = re.sub(r"<script.*?</script>", " ", t, flags=re.S | re.I)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", body)
    text = html.unescape(text)
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


if __name__ == "__main__":
    text = extract(sys.argv[1])
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else len(text)
    print(text[start:end])
