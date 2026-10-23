"""
PHP Shield -- signed-agreement PDF (reportlab, pure Python).
Rendered entirely from the stored `authorizations` row, so the PDF can be regenerated
at any time and always shows exactly what was signed.
"""
import io
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _para(line: str, style: ParagraphStyle) -> Paragraph:
    indent = len(line) - len(line.lstrip(" "))
    return Paragraph("&nbsp;" * indent + escape(line.strip()), style)


def signed_agreement_pdf(auth: dict, order: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                            topMargin=0.9 * inch, bottomMargin=0.9 * inch, invariant=1,
                            title="Site Owner Authorization and Consent Agreement", author="PHP Shield")
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10, textColor=colors.HexColor("#444444"))
    head = ParagraphStyle("head", parent=ss["Heading2"], spaceBefore=6, spaceAfter=4)

    story = []
    for i, line in enumerate(auth["agreement_text"].splitlines()):
        if not line.strip():
            story.append(Spacer(1, 5))
        elif i == 0:
            story.append(Paragraph(escape(line.strip()), ss["Title"]))
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(escape(line.strip()), head))
        else:
            story.append(_para(line, body))

    story += [Spacer(1, 12), Paragraph("ELECTRONIC SIGNATURE RECORD", head)]
    rows = [
        ["Signed by (typed name)", auth["typed_name"]],
        ["Signed at (UTC)", str(auth["signed_at"])],
        ["Site / domain", auth["domain"]],
        ["Order ID", order["id"]],
        ["Agreement version", auth["agreement_version"]],
        ["SHA-256 of agreement text", auth["agreement_hash"]],
        ["IP address", auth["ip"]],
        ["Browser / user agent", auth["user_agent"][:200]],
    ]
    table = Table([[Paragraph(escape(k), small), Paragraph(escape(str(v)), small)] for k, v in rows],
                  colWidths=[1.9 * inch, 4.8 * inch])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0"))]))
    story.append(table)

    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(0.9 * inch, 0.5 * inch,
                          f"DRAFT - attorney review required  |  Order {order['id']}  |  page {_doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
