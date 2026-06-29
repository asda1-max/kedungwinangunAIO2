"""
PDF Generator untuk Surat Resmi Desa Kedungwinangun
Menggunakan ReportLab untuk menghasilkan dokumen PDF profesional
"""

import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT


# ── Konfigurasi ──────────────────────────────────────────────────────────

HEADER_COLOR = colors.HexColor('#166534')  # hijau tua
ACCENT_COLOR = colors.HexColor('#166534')
BLACK = colors.black
WHITE = colors.white
LIGHT_GRAY = colors.HexColor('#f1f5f9')
BORDER_COLOR = colors.HexColor('#e2e8f0')

PAPER = A4
MARGIN_H = 2.5 * cm
MARGIN_V = 2 * cm


# ── Style Definitions ─────────────────────────────────────────────────────

def get_styles():
    """Get custom stylesheet"""
    base = getSampleStyleSheet()

    styles = {}

    styles['header_village'] = ParagraphStyle(
        'header_village',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=HEADER_COLOR,
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=20,
    )

    styles['header_sub'] = ParagraphStyle(
        'header_sub',
        fontName='Helvetica',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_CENTER,
        spaceAfter=1,
        leading=13,
    )

    styles['header_address'] = ParagraphStyle(
        'header_address',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=0,
        leading=11,
    )

    styles['doc_title'] = ParagraphStyle(
        'doc_title',
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=BLACK,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=4,
        leading=18,
    )

    styles['doc_number'] = ParagraphStyle(
        'doc_number',
        fontName='Helvetica',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_CENTER,
        spaceAfter=12,
        leading=13,
    )

    styles['body'] = ParagraphStyle(
        'body',
        fontName='Helvetica',
        fontSize=11,
        textColor=BLACK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=16,
    )

    styles['body_indent'] = ParagraphStyle(
        'body_indent',
        fontName='Helvetica',
        fontSize=11,
        textColor=BLACK,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        spaceAfter=8,
        leading=16,
    )

    styles['field_label'] = ParagraphStyle(
        'field_label',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_LEFT,
        spaceAfter=2,
        leading=13,
    )

    styles['field_value'] = ParagraphStyle(
        'field_value',
        fontName='Helvetica',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=13,
    )

    styles['signature'] = ParagraphStyle(
        'signature',
        fontName='Helvetica',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=13,
    )

    styles['signature_name'] = ParagraphStyle(
        'signature_name',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_CENTER,
        spaceAfter=0,
        leading=13,
    )

    styles['footer'] = ParagraphStyle(
        'footer',
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
        spaceBefore=20,
        leading=11,
    )

    styles['list_item'] = ParagraphStyle(
        'list_item',
        fontName='Helvetica',
        fontSize=10,
        textColor=BLACK,
        alignment=TA_LEFT,
        leftIndent=30,
        spaceAfter=4,
        leading=14,
    )

    return styles


# ── Helper Functions ──────────────────────────────────────────────────────

def format_date_indonesian(date_str):
    """Convert date string to Indonesian format"""
    if not date_str:
        return '-'
    try:
        if isinstance(date_str, datetime):
            d = date_str
        else:
            d = datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
        bulan = [
            '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        return f"{d.day} {bulan[d.month]} {d.year}"
    except Exception:
        return str(date_str)


def draw_header(canvas, doc, village_info=None):
    """Draw letterhead on each page"""
    canvas.saveState()
    width, height = A4

    # Top border line
    canvas.setStrokeColor(HEADER_COLOR)
    canvas.setLineWidth(2)
    canvas.line(MARGIN_H, height - 1.5*cm, width - MARGIN_H, height - 1.5*cm)

    # Village name
    canvas.setFont('Helvetica-Bold', 16)
    canvas.setFillColor(HEADER_COLOR)
    canvas.drawCentredString(width / 2, height - 2.3*cm, 'PEMERINTAH KABUPATEN KEBUMEN')

    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(BLACK)
    canvas.drawCentredString(width / 2, height - 3.0*cm, 'KECAMATAN KLIRONG')

    canvas.setFont('Helvetica-Bold', 11)
    canvas.setFillColor(HEADER_COLOR)
    canvas.drawCentredString(width / 2, height - 3.8*cm, 'DESA KEDUNGWINANGUN')

    # Address
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748b'))
    canvas.drawCentredString(width / 2, height - 4.5*cm, 'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, Jawa Tengah 54361')

    # Bottom border line
    canvas.setLineWidth(2)
    canvas.line(MARGIN_H, 1.5*cm, width - MARGIN_H, 1.5*cm)

    # Footer text
    canvas.setFont('Helvetica-Oblique', 8)
    canvas.setFillColor(colors.HexColor('#94a3b8'))
    canvas.drawCentredString(width / 2, 0.8*cm, 'Sistem Informasi Desa Kedungwinangun')

    canvas.restoreState()


def build_header_section(styles):
    """Build the letterhead content block"""
    elements = []

    elements.append(Paragraph('PEMERINTAH KABUPATEN KEBUMEN', styles['header_village']))
    elements.append(Paragraph('KECAMATAN KLIRONG', styles['header_sub']))
    elements.append(Paragraph('<b>DESA KEDUNGWINANGUN</b>', styles['header_sub']))
    elements.append(Paragraph('Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, Jawa Tengah 54361', styles['header_address']))

    elements.append(HRFlowable(width='100%', thickness=2, color=HEADER_COLOR, spaceAfter=6, spaceBefore=6))

    return elements


def build_field_table(fields, styles):
    """Build a table of label:value pairs"""
    data = []
    for label, value in fields:
        data.append([
            Paragraph(f'<b>{label}</b>', styles['field_label']),
            Paragraph(':  ' + str(value), styles['field_value']),
        ])

    t = Table(data, colWidths=[4.5*cm, 12*cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t


def build_signature_block(styles, village='Kedungwinangun', date=None, location='Kedungwinangun'):
    """Build signature block"""
    elements = []

    elements.append(Spacer(1, 0.5*cm))

    if date:
        elements.append(Paragraph(f'{location}, {date}', styles['body']))

    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph('Kepala Desa Kedungwinangun,', styles['signature']))

    elements.append(Spacer(1, 2.2*cm))

    elements.append(Paragraph('<b>MOH BAEDUNI</b>', styles['signature_name']))
    elements.append(Paragraph('NIP. XXXXXXXX', styles['signature']))

    return elements


# ── Letter-Specific Templates ─────────────────────────────────────────────

def generate_sku(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Usaha"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    # Header
    story.extend(build_header_section(styles))

    # Title
    story.append(Paragraph('SURAT KETERANGAN USAHA', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    # Body
    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan bahwa:',
        styles['body']
    ))

    # Data fields
    fields = [
        ('Nama', data.get('nama', '-')),
        ('NIK', data.get('nik', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir', '-')}, {data.get('tanggal_lahir', '-')}"),
        ('Alamat', data.get('alamat', '-')),
        ('Pekerjaan', data.get('pekerjaan', '-')),
        ('Jenis Usaha', data.get('jenis_usaha', '-')),
        ('Nama Usaha', data.get('nama_usaha', '-')),
        ('Alamat Usaha', data.get('alamat_usaha', '-')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        f'Bahwa benar-benar menjalankan usaha <b>{data.get("jenis_usaha", "-")}</b> '
        f'atas nama <b>{data.get("nama_usaha", "-")}</b> di alamat tersebut di atas.',
        styles['body']
    ))

    story.append(Paragraph(
        'Surat Keterangan Usaha ini dibuat untuk keperluan:',
        styles['body']
    ))
    story.append(Paragraph(f'<b>{data.get("keperluan", "-")}</b>', styles['body_indent']))

    story.append(Paragraph(
        'Demikian Surat Keterangan Usaha ini dibuat dengan sebenar-benarnya dan dapat '
        'dipergunakan sebagaimana mestinya.',
        styles['body']
    ))

    # Signature
    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_sktm(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Tidak Mampu"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT KETERANGAN TIDAK MAMPU', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan bahwa:',
        styles['body']
    ))

    fields = [
        ('Nama', data.get('nama', '-')),
        ('NIK', data.get('nik', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir', '-')}, {data.get('tanggal_lahir', '-')}"),
        ('Alamat', data.get('alamat', '-')),
        ('Pekerjaan', data.get('pekerjaan', '-')),
        ('Jumlah Tanggungan', data.get('jumlah_tanggungan', '-')),
        ('Penghasilan Per Bulan', data.get('penghasilan', '-')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        f'Bahwa nama tersebut di atas adalah benar warga yang termasuk dalam keluarga '
        f'<b>tidak mampu</b> berdasarkan hasil pengamatan dan pemeriksaan kami.',
        styles['body']
    ))

    story.append(Paragraph(
        'Surat Keterangan Tidak Mampu ini dibuat untuk keperluan:',
        styles['body']
    ))
    story.append(Paragraph(f'<b>{data.get("keperluan", "-")}</b>', styles['body_indent']))

    story.append(Paragraph(
        'Demikian Surat Keterangan Tidak Mampu ini dibuat dengan sebenar-benarnya dan dapat '
        'dipergunakan sebagaimana mestinya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_skck(data, nomor_surat, tanggal_surat):
    """Generate Surat Pengantar SKCK"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT PENGANTAR SKCK', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini memberikan pengantar '
        f'kepada:',
        styles['body']
    ))

    fields = [
        ('Nama', data.get('nama', '-')),
        ('NIK', data.get('nik', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir', '-')}, {data.get('tanggal_lahir', '-')}"),
        ('Jenis Kelamin', data.get('jenis_kelamin', '-')),
        ('Alamat', data.get('alamat', '-')),
        ('Pekerjaan', data.get('pekerjaan', '-')),
        ('Agama', data.get('agama', '-')),
        ('Kewarganegaraan', data.get('kewarganegaraan', 'Indonesia')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        'Bahwa orang tersebut di atas adalah benar-benar penduduk/warga kami dan '
        'berkelakuan baik, tidak pernah tersangkut perkara pidana.',
        styles['body']
    ))

    story.append(Paragraph(
        'Surat Pengantar ini dibuat untuk keperluan:',
        styles['body']
    ))
    story.append(Paragraph(f'<b>{data.get("keperluan", "Membuat SKCK")}</b>', styles['body_indent']))

    story.append(Paragraph(
        'Demikian Surat Pengantar ini dibuat dengan sebenar-benarnya untuk dapat '
        'dipergunakan sebagaimana mestinya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_domisili(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Domisili"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT KETERANGAN DOMISILI', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan bahwa:',
        styles['body']
    ))

    fields = [
        ('Nama', data.get('nama', '-')),
        ('NIK', data.get('nik', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir', '-')}, {data.get('tanggal_lahir', '-')}"),
        ('Jenis Kelamin', data.get('jenis_kelamin', '-')),
        ('Alamat KTP', data.get('alamat_ktp', '-')),
        ('Alamat Domisili', data.get('alamat_domisili', '-')),
        ('Pekerjaan', data.get('pekerjaan', '-')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        f'Bahwa orang tersebut di atas saat ini berdomisili di <b>{data.get("alamat_domisili", "-")}</b>, '
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen.',
        styles['body']
    ))

    story.append(Paragraph(
        'Surat Keterangan Domisili ini dibuat untuk keperluan:',
        styles['body']
    ))
    story.append(Paragraph(f'<b>{data.get("keperluan", "-")}</b>', styles['body_indent']))

    story.append(Paragraph(
        'Demikian Surat Keterangan Domisili ini dibuat dengan sebenar-benarnya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_belum_nikah(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Belum Menikah"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT KETERANGAN BELUM MENIKAH', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan bahwa:',
        styles['body']
    ))

    fields = [
        ('Nama', data.get('nama', '-')),
        ('NIK', data.get('nik', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir', '-')}, {data.get('tanggal_lahir', '-')}"),
        ('Jenis Kelamin', data.get('jenis_kelamin', '-')),
        ('Agama', data.get('agama', '-')),
        ('Alamat', data.get('alamat', '-')),
        ('Pekerjaan', data.get('pekerjaan', '-')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        'Bahwa nama tersebut di atas adalah benar-benar warga kami dan sampai saat ini '
        '<b>belum pernah menikah</b> baik secara agama, hukum adat, maupun secara hukum negara.',
        styles['body']
    ))

    story.append(Paragraph(
        'Surat Keterangan Belum Menikah ini dibuat untuk keperluan:',
        styles['body']
    ))
    story.append(Paragraph(f'<b>{data.get("keperluan", "-")}</b>', styles['body_indent']))

    story.append(Paragraph(
        'Demikian Surat Keterangan Belum Menikah ini dibuat dengan sebenar-benarnya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_lahir(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Kelahiran"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT KETERANGAN KELAHIRAN', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan '
        f'bahwa telah terjadi kelahiran:',
        styles['body']
    ))

    story.append(Paragraph('<b>Data Bayi:</b>', styles['field_label']))
    fields_bayi = [
        ('Nama Bayi', data.get('nama_bayi', '-')),
        ('Jenis Kelamin', data.get('jk_bayi', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir_bayi', '-')}, {data.get('tanggal_lahir_bayi', '-')}"),
        ('Pukul', data.get('pukul_lahir', '-')),
        ('Berat', data.get('berat_bayi', '-')),
        ('Panjang', data.get('panjang_bayi', '-')),
    ]
    story.append(build_field_table(fields_bayi, styles))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('<b>Data Orang Tua:</b>', styles['field_label']))
    fields_ortu = [
        ('Nama Ayah', data.get('nama_ayah', '-')),
        ('NIK Ayah', data.get('nik_ayah', '-')),
        ('Tempat / Tgl. Lahir Ayah', f"{data.get('tempat_lahir_ayah', '-')}, {data.get('tanggal_lahir_ayah', '-')}"),
        ('Alamat Ayah', data.get('alamat_ayah', '-')),
        ('Nama Ibu', data.get('nama_ibu', '-')),
        ('NIK Ibu', data.get('nik_ibu', '-')),
        ('Tempat / Tgl. Lahir Ibu', f"{data.get('tempat_lahir_ibu', '-')}, {data.get('tanggal_lahir_ibu', '-')}"),
        ('Alamat Ibu', data.get('alamat_ibu', '-')),
    ]
    story.append(build_field_table(fields_ortu, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        f'Kelahiran tersebut di atas dicatat dan dibukukan pada '
        f'<b>Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen</b>.',
        styles['body']
    ))

    story.append(Paragraph(
        'Demikian Surat Keterangan Kelahiran ini dibuat dengan sebenar-benarnya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


def generate_mati(data, nomor_surat, tanggal_surat):
    """Generate Surat Keterangan Kematian"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph('SURAT KETERANGAN KEMATIAN', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    story.append(Paragraph(
        f'Desa Kedungwinangun, Kec. Klirong, Kab. Kebumen, dengan ini menyatakan '
        f'bahwa telah terjadi kematian:',
        styles['body']
    ))

    story.append(Paragraph('<b>Data Almarhum/Almarhumah:</b>', styles['field_label']))
    fields = [
        ('Nama', data.get('nama_alm', '-')),
        ('NIK', data.get('nik_alm', '-')),
        ('Tempat / Tgl. Lahir', f"{data.get('tempat_lahir_alm', '-')}, {data.get('tanggal_lahir_alm', '-')}"),
        ('Jenis Kelamin', data.get('jk_alm', '-')),
        ('Alamat', data.get('alamat_alm', '-')),
        ('Hari / Tgl. Meninggal', f"{data.get('hari_mati', '-')}, {data.get('tanggal_mati', '-')}"),
        ('Pukul', data.get('pukul_mati', '-')),
        ('Tempat Meninggal', data.get('tempat_mati', '-')),
        ('Penyebab', data.get('penyebab', '-')),
    ]
    story.append(build_field_table(fields, styles))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph('<b>Data Pelapor:</b>', styles['field_label']))
    fields_pelapor = [
        ('Nama Pelapor', data.get('nama_pelapor', '-')),
        ('NIK Pelapor', data.get('nik_pelapor', '-')),
        ('Hubungan', data.get('hubungan', '-')),
    ]
    story.append(build_field_table(fields_pelapor, styles))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        'Demikian Surat Keterangan Kematian ini dibuat dengan sebenar-benarnya.',
        styles['body']
    ))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf


# ── Main Generator Function ───────────────────────────────────────────────

GENERATORS = {
    'SKU': generate_sku,
    'SKTM': generate_sktm,
    'SKCK': generate_skck,
    'DOMISILI': generate_domisili,
    'BELUM_NIKAH': generate_belum_nikah,
    'LAHIR': generate_lahir,
    'MATI': generate_mati,
}


def generate_surat_pdf(kode_surat, data, nomor_surat, tanggal_surat):
    """
    Generate PDF for a letter based on type kode.
    Returns BytesIO buffer containing the PDF.
    """
    generator = GENERATORS.get(kode_surat.upper())

    if generator:
        return generator(data, nomor_surat, tanggal_surat)

    # Fallback: generic letter
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=PAPER,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V + 1.5*cm, bottomMargin=MARGIN_V + 0.5*cm
    )
    styles = get_styles()
    story = []

    story.extend(build_header_section(styles))
    story.append(Paragraph(f'SURAT KETERANGAN ({kode_surat})', styles['doc_title']))
    story.append(Paragraph(f'Nomor: {nomor_surat}', styles['doc_number']))
    story.append(HRFlowable(width='100%', thickness=1, color=BORDER_COLOR, spaceAfter=12))

    for key, value in data.items():
        story.append(Paragraph(f'<b>{key.replace("_", " ").title()}</b>: {value}', styles['body']))

    story.extend(build_signature_block(styles, date=format_date_indonesian(tanggal_surat)))

    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
    buf.seek(0)
    return buf
