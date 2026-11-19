"""Response letter for the CMT camera-ready ZIP, built from response_to_reviewers.md.

    <repo>/venv/Scripts/python make_response_letter.py   -> PIC2026_Paper325_response_letter.docx (then to PDF)

The markdown stays the single source: headings (##), tables (| ... |), bullets (- ) and paragraphs are copied
over; the internal "Status of this file" line is left out.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[2] / "PIC 2026 camera-ready"   # outputs stay outside git
sys.path.insert(0, str(HERE.parents[2] / "SN Computer Science submission" / ".pylib"))

import docx  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

SRC = HERE / "response_to_reviewers.md"
OUT = WORK / "PIC2026_Paper325_response_letter.docx"
TITLE = "AI-Assisted Dispute Adjudication for D2C Delivery Operations: An SLA-Grounded LLM Pipeline"
AUTHORS = "Arnav Mundra, Pallavi Hiwarkar, Kartikey Bisen, Piyush Pariwakam, Ishwar Paradkar, Krunal Narad"

D = docx.Document()
sec = D.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.8)
normal = D.styles["Normal"]
normal.font.name, normal.font.size = "Times New Roman", Pt(10.5)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.space_after = Pt(4)
for name in ("Heading 1", "Heading 2"):
    st = D.styles[name]
    st.font.name, st.font.color.rgb = "Times New Roman", None
    fonts = st.element.rPr.rFonts
    fonts.set(qn("w:eastAsia"), "Times New Roman")
    for theme in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):  # theme fonts override the name
        fonts.attrib.pop(qn(theme), None)
D.styles["Heading 1"].font.size, D.styles["Heading 2"].font.size = Pt(14), Pt(12)
D.core_properties.title = f"Response to reviewers: {TITLE}"
D.core_properties.author = AUTHORS.replace(", ", "; ")


def para(text, bold=False, italic=False, size=None, after=None):
    p = D.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


D.add_heading("Response to Reviewers and Summary of Revisions", level=1)
para("IEEE PIC 2026 · Paper ID 325 · Camera-ready submission", italic=True, after=2)
para(f"Title: {TITLE}", after=2)
para(f"Authors: {AUTHORS}", after=2)
para("Date: 19 November 2026", after=10)
para("Dear PIC 2026 Organizing Committee and Reviewers,")
para("Thank you for accepting our paper and for the detailed reviews. This letter summarises how the camera-ready "
     "version responds to each comment. All results in the revised paper are computed from saved experiment runs.")

lines = SRC.read_text(encoding="utf-8").splitlines()
i = 0
while i < len(lines):
    line = lines[i].rstrip()
    if not line or line.startswith("# ") or line.startswith("Paper:") or line.startswith("Status of this file"):
        i += 1
        continue
    if line.startswith("## "):
        D.add_heading(line[3:], level=2)
        i += 1
        continue
    if line.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r"-+", c) for c in cells):
                rows.append(cells)
            i += 1
        t = D.add_table(rows=len(rows), cols=len(rows[0]))
        t.style, t.alignment, t.autofit = "Table Grid", WD_TABLE_ALIGNMENT.CENTER, False
        for k, cells in enumerate(rows):
            for j, text in enumerate(cells):
                cell = t.cell(k, j)
                cell.width = Inches(2.1 if j == 0 else 4.6)
                cell.paragraphs[0].text = ""
                run = cell.paragraphs[0].add_run(text)
                run.font.size, run.bold = Pt(9.5), k == 0
        D.add_paragraph()
        continue
    if line.startswith("- "):
        text = line[2:]
        while i + 1 < len(lines) and lines[i + 1].startswith("  "):  # wrapped bullet
            i += 1
            text += " " + lines[i].strip()
        D.add_paragraph(text, style="List Bullet")
        i += 1
        continue
    text = line  # paragraph: join wrapped lines
    while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|\||- )", lines[i + 1]):
        i += 1
        text += " " + lines[i].strip()
    para(text)
    i += 1

para("")
para("We are grateful for the reviewers' suggestions, which substantially strengthened the evaluation.")
para("Sincerely,", after=2)
para("Arnav Mundra, on behalf of all authors", after=2)
para("Department of Computer Science and Engineering, G. H. Raisoni College of Engineering and Management, "
     "Nagpur, India")

D.save(str(OUT))
print("wrote", OUT)
