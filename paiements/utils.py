import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generer_recu_pdf(paiement):
    reservation = paiement.reservation
    locataire = reservation.locataire
    proprietaire = reservation.logement.proprietaire
    logement = reservation.logement

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=0, leftMargin=0,
        topMargin=0, bottomMargin=0
    )

    NAVY       = colors.HexColor('#1B2B4B')
    GOLD       = colors.HexColor('#C9A84C')
    WHITE      = colors.HexColor('#FFFFFF')
    LIGHT_BG   = colors.HexColor('#F7F8FC')
    LIGHT_BG2  = colors.HexColor('#EDEEF5')
    GRAY       = colors.HexColor('#7A8099')
    DARK       = colors.HexColor('#1B2B4B')
    SUCCESS    = colors.HexColor('#1A7A5E')
    SUCCESS_BG = colors.HexColor('#E8F5F1')
    BORDER     = colors.HexColor('#D0D4E8')
    BLUE_LIGHT = colors.HexColor('#A0B0CC')

    PW  = 21*cm
    PAD = 1.8*cm
    CW  = PW - 2*PAD

    def p(text, size=9, color=None, bold=False, align=TA_LEFT, space_before=0, space_after=0):
        if color is None:
            color = DARK
        fn = 'Helvetica-Bold' if bold else 'Helvetica'
        return Paragraph(text, ParagraphStyle('_',
            fontName=fn, fontSize=size, textColor=color,
            alignment=align, leading=size*1.4,
            spaceBefore=space_before, spaceAfter=space_after
        ))

    def padded(content, left=PAD, right=PAD, top=0, bottom=0):
        return Table([[content]], colWidths=[PW], style=[
            ('LEFTPADDING',   (0,0), (-1,-1), left),
            ('RIGHTPADDING',  (0,0), (-1,-1), right),
            ('TOPPADDING',    (0,0), (-1,-1), top),
            ('BOTTOMPADDING', (0,0), (-1,-1), bottom),
        ])

    def section_header(text):
        t = Table([[p(text, size=8.5, color=WHITE, bold=True)]],
                  colWidths=[PW])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), NAVY),
            ('LEFTPADDING',   (0,0), (-1,-1), PAD),
            ('RIGHTPADDING',  (0,0), (-1,-1), PAD),
            ('TOPPADDING',    (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LINEBELOW',     (0,0), (-1,-1), 2.5, GOLD),
        ]))
        return t

    def data_table(rows):
        t = Table(rows, colWidths=[5.5*cm, CW-5.5*cm])
        t.setStyle(TableStyle([
            ('FONTNAME',       (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME',       (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE',       (0,0), (-1,-1), 8.5),
            ('TEXTCOLOR',      (0,0), (0,-1), GRAY),
            ('TEXTCOLOR',      (1,0), (1,-1), DARK),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, LIGHT_BG2]),
            ('PADDING',        (0,0), (-1,-1), 10),
            ('LINEBELOW',      (0,0), (-1,-2), 0.5, BORDER),
            ('BOX',            (0,0), (-1,-1), 1, BORDER),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return padded(t, top=0, bottom=0)

    elements = []

    # ══════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════
    logo_cell = Table([
        [p('<font color="#FFFFFF" size="24"><b>Location</b></font>'
           '<font color="#C9A84C" size="24"><b>Maroc</b></font>')],
    ], colWidths=[10*cm])

    info_cell = Table([
        [p('REÇU DE PAIEMENT', size=16, color=WHITE, bold=True, align=TA_RIGHT)],
        [p(f'Réf : <b>{paiement.reference}</b>',
           size=8, color=GOLD, align=TA_RIGHT, space_before=4)],
        [p(f'Date : {paiement.date_paiement.strftime("%d/%m/%Y")}',
           size=8, color=BLUE_LIGHT, align=TA_RIGHT, space_before=2)],
    ], colWidths=[9*cm])

    header = Table([[logo_cell, info_cell]], colWidths=[11*cm, 10*cm])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('PADDING',    (0,0), (-1,-1), 22),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW',  (0,0), (-1,-1), 3.5, GOLD),
    ]))
    elements.append(header)

    # ══════════════════════════════════════
    # BADGE STATUT
    # ══════════════════════════════════════
    badge = Table([[
        p('✓   PAIEMENT CONFIRMÉ ET VALIDÉ',
          size=11, color=SUCCESS, bold=True, align=TA_LEFT),
        p(f'<b>{paiement.montant} DH</b>',
          size=20, color=SUCCESS, align=TA_RIGHT),
    ]], colWidths=[12*cm, PW-12*cm])
    badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SUCCESS_BG),
        ('PADDING',    (0,0), (-1,-1), 16),
        ('LINEBELOW',  (0,0), (-1,-1), 2, SUCCESS),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(badge)
    elements.append(Spacer(1, 18))

    # ══════════════════════════════════════
    # RÉSERVATION
    # ══════════════════════════════════════
    elements.append(section_header('DÉTAILS DE LA RÉSERVATION'))
    elements.append(Spacer(1, 8))
    elements.append(data_table([
        ['Logement',     logement.titre],
        ['Type',         logement.get_type_logement_display()],
        ['Adresse',      f'{logement.adresse}, {logement.ville}'],
        ['Date arrivée', reservation.date_arrivee.strftime('%d/%m/%Y')],
        ['Date départ',  reservation.date_depart.strftime('%d/%m/%Y')],
        ['Durée',        f'{reservation.nombre_nuits} nuit(s)'],
        ['Prix / nuit',  f'{logement.prix_par_nuit} DH'],
    ]))

    # Total
    total = Table([[
        p('MONTANT TOTAL', size=9, color=GRAY, bold=True),
        p(f'<b>{reservation.prix_total} DH</b>',
          size=17, color=NAVY, align=TA_RIGHT, bold=True),
    ]], colWidths=[5.5*cm, CW-5.5*cm])
    total.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG2),
        ('PADDING',    (0,0), (-1,-1), 12),
        ('LINEABOVE',  (0,0), (-1,0), 2, NAVY),
        ('LINEBELOW',  (0,0), (-1,-1), 2.5, GOLD),
        ('BOX',        (0,0), (-1,-1), 1, BORDER),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(padded(total, top=0, bottom=0))
    elements.append(Spacer(1, 18))

    # ══════════════════════════════════════
    # PARTIES
    # ══════════════════════════════════════
    elements.append(section_header('PARTIES CONCERNÉES'))
    elements.append(Spacer(1, 8))

    def partie_card(titre, user, accent):
        nom   = user.get_full_name() or user.username
        email = user.email or '—'
        tel   = user.telephone or '—'
        cin   = user.cin or '—'

        rows = [
            [p(titre, size=8.5, color=WHITE, bold=True, align=TA_CENTER)],
            [p(f'<b>{nom}</b>', size=11, color=DARK, align=TA_CENTER, space_before=8)],
            [p(email, size=8, color=GRAY, align=TA_CENTER, space_before=2)],
            [p(f'Tél : {tel}', size=8, color=DARK, align=TA_CENTER, space_before=2)],
            [p(f'CIN : {cin}', size=9, color=accent, bold=True,
               align=TA_CENTER, space_before=6, space_after=4)],
        ]
        t = Table(rows, colWidths=[(CW/2)-0.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0),  accent),
            ('BACKGROUND', (0,1), (0,-1), LIGHT_BG),
            ('PADDING',    (0,0), (-1,-1), 10),
            ('BOX',        (0,0), (-1,-1), 1.5, accent),
            ('LINEBELOW',  (0,0), (0,0),  3, accent),
            ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    parties = Table([[
        partie_card('LOCATAIRE',    locataire,    NAVY),
        partie_card('PROPRIÉTAIRE', proprietaire, GOLD),
    ]], colWidths=[CW/2, CW/2])
    parties.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('RIGHTPADDING',  (0,0), (0,-1), 8),
    ]))
    elements.append(padded(parties, top=0, bottom=8))
    elements.append(Spacer(1, 18))

    # ══════════════════════════════════════
    # PAIEMENT
    # ══════════════════════════════════════
    elements.append(section_header('INFORMATIONS DE PAIEMENT'))
    elements.append(Spacer(1, 8))
    methode = getattr(paiement, 'methode', 'carte') or 'carte'
    pay_t = Table([
        ['Référence', paiement.reference],
        ['Date',      paiement.date_paiement.strftime('%d/%m/%Y à %H:%M')],
        ['Méthode',   methode.capitalize()],
        ['Statut',    'PAYÉ ✓'],
        ['Montant',   f'{paiement.montant} DH'],
    ], colWidths=[5.5*cm, CW-5.5*cm])
    pay_t.setStyle(TableStyle([
        ('FONTNAME',       (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',       (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',       (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR',      (0,0), (0,-1), GRAY),
        ('TEXTCOLOR',      (1,0), (1,-1), DARK),
        ('TEXTCOLOR',      (1,3), (1,3),  SUCCESS),
        ('FONTNAME',       (1,3), (1,3),  'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, LIGHT_BG2]),
        ('PADDING',        (0,0), (-1,-1), 10),
        ('LINEBELOW',      (0,0), (-1,-2), 0.5, BORDER),
        ('BOX',            (0,0), (-1,-1), 1, BORDER),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(padded(pay_t, top=0, bottom=0))
    elements.append(Spacer(1, 28))

    # ══════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════
    gold_bar = Table([['']], colWidths=[PW], rowHeights=[3])
    gold_bar.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), GOLD)]))
    elements.append(gold_bar)

    footer = Table([[
        Table([
            [p('Document officiel • LocationMaroc',
               size=8, color=GOLD, bold=True)],
            [p(f'Ce reçu constitue une preuve légale de votre transaction.\n'
               f'Référence unique : {paiement.reference}',
               size=7.5, color=BLUE_LIGHT, space_before=3)],
        ], colWidths=[13*cm]),
        Table([
            [p('locationmaroc.ma', size=8, color=GOLD, bold=True, align=TA_RIGHT)],
            [p(paiement.date_paiement.strftime('%d/%m/%Y à %H:%M'),
               size=7.5, color=BLUE_LIGHT, align=TA_RIGHT, space_before=3)],
        ], colWidths=[8*cm]),
    ]], colWidths=[13*cm, 8*cm])
    footer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('PADDING',    (0,0), (-1,-1), 16),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer