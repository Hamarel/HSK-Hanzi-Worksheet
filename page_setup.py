# importing modules
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def process_line(line, line_break):
    # word
    line = line.split("\t")
    word = line[0]

    extract_from_line = line[2].replace("\"", "").replace("<br><br><b>", "§").replace("<br><br>", "; ").replace("<br>",
                                                                                                                "").replace(
        "<b>", "").replace("<strong>", "").replace("</strong>", "§").replace("</b>", "§").replace("§;", "§").split("§")
    pinyin = extract_from_line[0]
    trans = extract_from_line[1]
    if line_break:
        trans_len = len(trans)
        split_trans = 150
        split_index = split_trans
        prev_split_index = 0
        trans_br = []
        while trans_len // split_trans > 0:
            br_trans_index = trans.find(";", split_index - 10)
            if br_trans_index < 0:
                br_trans_index = trans.find(" ", split_index - 10)
            if br_trans_index < split_index + 10:
                trans_br.append(trans[prev_split_index:br_trans_index + 1].lstrip())
            split_index = split_index + split_trans
            trans_len = trans_len - split_trans
            prev_split_index = br_trans_index + 1
        if len(trans_br) == 0:
            trans_br.append(trans.lstrip())
        else:
            trans_br.append(trans[prev_split_index:])
        classifier_index = trans_br[-1].find("CL")
        if classifier_index >= 1:
            classifier = trans_br[-1][classifier_index:]
            trans_br[-1] = trans_br[-1][:classifier_index]
            trans_br.append(classifier)
        trans = trans_br

    hsk = line[-1]
    return word, pinyin, trans, hsk


def two_hanzi(c, word, pinyin, trans, hsk):
    word_length = len(word)
    height = 735
    cell_width = 48
    cell_width_half = cell_width / 2
    margin_left = 10

    # header
    h_cell_width = cell_width + cell_width_half
    h_cell_width_half = h_cell_width / 2
    height = height - cell_width_half
    c.roundRect(margin_left, height, h_cell_width * word_length, h_cell_width, 0, stroke=1, fill=0)
    c.roundRect(word_length * h_cell_width + margin_left, height, ((8 - word_length) * h_cell_width), h_cell_width, 0,
                stroke=1, fill=0)

    c.setFont("Kaiti", 10)
    c.drawString(10 * cell_width + cell_width + margin_left + 20, height + 3, hsk)

    # pinyin
    c.setFont("Kaiti", 15)
    c.drawString(word_length * h_cell_width + 2 * margin_left + 5, height + 6, pinyin)

    # words
    c.setFont("Kaiti", 70)
    for hanzi in range(0, word_length):
        c.drawString(hanzi * h_cell_width + margin_left - 2, height + 15, word[hanzi])
    c.setFont("StrokeOrder", 50)
    for hanzi in range(0, word_length):
        c.drawString((word_length * h_cell_width) + hanzi * cell_width + margin_left + 5, height + 25, word[hanzi])

    # translation
    height = height - cell_width
    c.setFont("Kaiti", 10)
    c.roundRect(margin_left, height, cell_width * 12, cell_width, 0, stroke=1, fill=0)
    string_height = height
    for lines in trans:
        c.drawString(margin_left + 2, string_height + 35, lines)
        string_height = string_height - 12

    # worksheet
    c.setFont("Kaiti", 45)
    for r in range(1, 14):
        height_o = height - 1
        height_u = height - 47
        for i in range(0, 12):
            c.setStrokeColorRGB(0, 0, 0, 1)
            c.roundRect(i * cell_width + margin_left, height_u - 1, cell_width, cell_width, 0, stroke=1, fill=0)
            c.setStrokeColorRGB(0, 0, 0, 0.15)
            c.line(i * cell_width + 1 + margin_left, height - cell_width_half, (i + 1) * cell_width - 1 + margin_left,
                   height - cell_width_half)  # waagerecht
            c.line(i * cell_width + cell_width_half + margin_left, height_o,
                   i * cell_width + cell_width_half + margin_left, height_u)  # senkrecht
            c.line(i * cell_width + 1 + margin_left, height_u, (i + 1) * cell_width - 1 + margin_left, height_o)
            c.line((i + 1) * cell_width - 1 + margin_left, height_u, i * cell_width + 1 + margin_left, height_o)
        height = height - cell_width
        c.setFillColorRGB(0, 0, 0, 0.3)
        if r < 5:
            hanzi_to_print = 0
            for hanzi in range(0, 12):
                c.drawString(hanzi * cell_width + margin_left, height + 10, word[hanzi_to_print])
                hanzi_to_print = hanzi_to_print + 1
                if hanzi_to_print >= word_length:
                    hanzi_to_print = 0
        else:
            for hanzi in range(0, word_length):
                c.drawString(hanzi * cell_width + margin_left, height + 10, word[hanzi])


hsk_level = "1"

pdf = canvas.Canvas("HSK "+hsk_level+" Worksheet.pdf")
pdf.setTitle("HSK "+hsk_level+" Worksheet")
pdfmetrics.registerFont(
    TTFont('Kaiti', os.path.join(os.getcwd(), 'STKaiti.ttf'))
)
pdfmetrics.registerFont(
    TTFont('StrokeOrder', os.path.join(os.getcwd(), 'CNstrokeorder.ttf'))
)
# txt_file = []
with open("Vocabulary_HSK1.txt", encoding="utf8") as file:
    index = 0
    for lines in file:
        word, pinyin, trans, hsk = process_line(lines, True)
        print(index, ": ", word)
        # txt_file.append(word+"\t"+ trans+"\n")

        two_hanzi(pdf, word, pinyin, trans, hsk)
        pdf.showPage()
        index = index + 1
# with open("import_Chinese_hsk"+hsk_level+".txt", "w", encoding="utf8") as file:
#     for item in txt_file:
#         file.write(item)
#
pdf.save()
