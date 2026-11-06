from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

root = Path(__file__).resolve().parent
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
sec.top_margin = sec.bottom_margin = Inches(.7)
sec.left_margin = sec.right_margin = Inches(.65)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Heading 3']:
    s = doc.styles[name]
    s.font.name = 'Calibri'
    s.font.color.rgb = RGBColor(0, 0, 0)
doc.styles['Normal'].font.size = Pt(11)
doc.styles['Normal'].paragraph_format.space_after = Pt(6)
doc.styles['Normal'].paragraph_format.line_spacing = 1.08
for name, size in [('Title', 25), ('Heading 1', 19), ('Heading 2', 14), ('Heading 3', 12)]:
    doc.styles[name].font.size = Pt(size)
    doc.styles[name].paragraph_format.keep_with_next = True
code = doc.styles.add_style('Code Manual', 1)
code.font.name = 'Consolas'
code.font.size = Pt(8)
code.paragraph_format.space_after = Pt(0)
code.paragraph_format.line_spacing = 1

def inline(p, text):
    for chunk in re.split(r'(`[^`]+`|\*\*.+?\*\*|\[[^\]]+\]\([^)]+\))', text):
        if chunk.startswith('`') and chunk.endswith('`'):
            r = p.add_run(chunk[1:-1]); r.font.name = 'Consolas'; r.font.size = Pt(9)
        elif chunk.startswith('**'):
            p.add_run(chunk[2:-2]).bold = True
        elif re.match(r'\[[^\]]+\]\([^)]+\)', chunk):
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', chunk)
            label, url = m.groups()
            if not url.startswith('http'):
                p.add_run(label)
            else:
                h = OxmlElement('w:hyperlink')
                h.set(qn('r:id'), p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True))
                r = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = label; r.append(t); h.append(r); p._p.append(h)
        else:
            p.add_run(chunk)

def table(rows):
    rows = [r for r in rows if not re.match(r'^\|[\s:|\-]+\|$', r)]
    cells = [[x.strip() for x in r.strip().strip('|').split('|')] for r in rows]
    t = doc.add_table(rows=0, cols=len(cells[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    n = len(cells[0]); width = 6.97 / n
    for col in t.columns: col.width = Inches(width)
    for i, values in enumerate(cells):
        row = t.add_row()
        for j, txt in enumerate(values):
            c = row.cells[j]; c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            inline(c.paragraphs[0], txt)
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.space_before = Pt(4)
                for r in p.runs: r.font.size = Pt(9)
            pr = c._tc.get_or_add_tcPr()
            borders = OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); borders.append(e)
            pr.append(borders)
            if i == 0:
                shade=OxmlElement('w:shd'); shade.set(qn('w:fill'),'DCE6F1'); pr.append(shade)
                for r in c.paragraphs[0].runs: r.bold=True
        if i == 0:
            repeat=OxmlElement('w:tblHeader'); row._tr.get_or_add_trPr().append(repeat)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

def markdown(text):
    lines=text.splitlines(); i=0
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                p=doc.add_paragraph(style='Code Manual'); p.add_run(lines[i] or ' '); i+=1
            doc.add_paragraph().paragraph_format.space_after=Pt(0)
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'): rows.append(lines[i]); i+=1
            table(rows); continue
        elif line.startswith('#'):
            m=re.match(r'^(#+)\s+(.*)',line)
            title=m.group(2).replace('—',' ')
            title=re.sub(r'^(\d+)\.\s*',r'\1 ',title)
            title=title.replace(' — ',' ').replace(' – ',' ')
            doc.add_heading(title, min(len(m.group(1)),3))
        elif line.strip():
            style=None
            if line.startswith('- '): style='List Bullet'; line=line[2:]
            elif re.match(r'^\d+\. ',line): style='List Number'; line=re.sub(r'^\d+\. ','',line)
            inline(doc.add_paragraph(style=style),line)
        i+=1

doc.add_paragraph('Hướng dẫn thực hành xây dựng API ESAPAPI', 'Title')
doc.add_paragraph('ASP.NET Core 10 và Entity Framework Core với SQLite', 'Subtitle')
doc.add_paragraph('Tài liệu dành cho người thực hành xây dựng API dựa trên cấu trúc ESAPAPI. Nội dung hướng dẫn chạy ứng dụng hiện có, đọc mã nguồn và xây dựng project thực hành có đầy đủ CRUD.')
doc.add_paragraph('Ngày khảo sát mã nguồn 23/10/2026')
doc.add_heading('Nội dung tài liệu',1)
for x in ['Tổng quan và kết quả khảo sát','1 Cấu trúc project','2 Chạy project và kiểm thử','3 Xây dựng API từ đầu','4 Xử lý lỗi và hướng phát triển','Phụ lục mẫu request HTTP']:
    doc.add_paragraph(x)
files=['README.md','01-Cau-truc-project.md','02-Chay-va-kiem-thu.md','03-Xay-dung-API.md','04-Xu-ly-loi.md']
for name in files:
    doc.add_page_break()
    text=(root/name).read_text(encoding='utf-8')
    if name=='README.md':
        text=text.replace('# Hướng dẫn thực hành ASP.NET Core Web API — ESAPAPI','# Tổng quan và kết quả khảo sát')
    markdown(text)
doc.add_page_break(); doc.add_heading('Phụ lục mẫu request HTTP',1)
doc.add_paragraph('Nội dung file ESAPAPI-Practice.http. Đổi URL và Id theo môi trường thực hành trước khi gửi request ghi hoặc xóa dữ liệu.')
for line in (root/'ESAPAPI-Practice.http').read_text(encoding='utf-8').splitlines():
    doc.add_paragraph(line or ' ',style='Code Manual')
footer=sec.footer.paragraphs[0]; footer.alignment=2
footer.add_run('ESAPAPI  |  ')
field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); footer._p.append(field)
doc.core_properties.title='Hướng dẫn thực hành xây dựng API ESAPAPI'
doc.core_properties.subject='ASP.NET Core 10 EF Core SQLite và CRUD'
out=root/'Huong-dan-thuc-hanh-ESAPAPI.docx'; doc.save(out)
print(out)
print('Paragraphs',len(doc.paragraphs),'Tables',len(doc.tables))
