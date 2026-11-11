"""Parse tables out of a saved HTML file with structure preserved."""
import sys
from html.parser import HTMLParser


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.cur = None
        self.row = None
        self.cell = None
        self.in_style = False
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self.in_style = True
        elif tag == "script":
            self.in_script = True
        elif tag == "table":
            self.cur = []
        elif tag == "tr" and self.cur is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        elif tag == "script":
            self.in_script = False
        elif tag == "table" and self.cur is not None:
            self.tables.append(self.cur)
            self.cur = None
        elif tag == "tr" and self.row is not None:
            self.cur.append(self.row)
            self.row = None
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None

    def handle_data(self, data):
        if self.in_style or self.in_script:
            return
        if self.cell is not None:
            self.cell.append(data)


def main():
    text = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    p = TableParser()
    p.feed(text)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    for n, table in enumerate(p.tables[start:], start=start):
        print(f"=== TABLE {n} ({len(table)} rows) ===")
        for row in table[:60]:
            print(" | ".join(row))


if __name__ == "__main__":
    main()
