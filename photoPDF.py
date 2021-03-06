from typing import Dict
from fpdf import FPDF
import json
import sys

INPUT_FILE = sys.argv[1]

# dimensions for the PDF is A4 in points - these values correspond to that
PDF_W=210/0.35
PDF_H=297/0.35

def list_get(l, i, default=""):
    if i >= len(l):
        return default
    return l[i]

def parse_shotlog(shotlog_content: str) -> Dict:
    output = {}
    current_category = None

    lines = shotlog_content.strip().replace("\n\n", "\n").splitlines()

    for line in lines:

        sp = line.strip().split(" ")
        operand, rest = sp[0], sp[1:]
        if operand.endswith(":"): 
            operand = operand.strip(":")
        
        rest = [x.rstrip(":") for x in rest]
        
        if operand.lower() == "category":
            date, notes = rest[0], " ".join(rest[1:]).rstrip(":")
            if current_category is None:    
                output["data"] = []
                current_category = 0
            else:
                current_category += 1
            output["data"].append({"date": date, "notes": notes, "data": []})
        elif operand.lower() == "shot":

            if current_category is None:
                raise ValueError("no category declaration before shot declaration")

            output["data"][current_category]["data"].append({
                "shot_number": list_get(rest, 0),
                "exposure": list_get(rest, 1),
                "shutter_speed": list_get(rest, 2),
                "aperture": list_get(rest, 3),
                "notes": " ".join(rest[4:])
            })
        else:
            output[operand] = " ".join(rest).replace("\\n", "\n")

    return output

class PDF(FPDF):

    def __init__(self, *args, **kwargs):
        self.lens = []
        super().__init__(*args, **kwargs)

    def reset_lengths(self):
        self.lens = []

    def get_max_text_len(self):
        return max(self.lens)

    def write_text(self, text, x=0, y=0):
        self.lens.append(pdf.get_string_width(text) + 4)
        self.cell(x, y, text)

    pass

FONT="Helvetica"

def draw_info_box(pdf, classifier, film_stock, shots, camera, load_date, locations):
    BOX_PADDING = 5 # used for the box around the label

    pdf.reset_lengths()

    start_x, start_y = pdf.get_x() - 5, pdf.get_y()

    pdf.set_font(FONT, size=22)
    pdf.write_text(classifier, 5, 35)
    pdf.ln()

    pdf.set_font(FONT, size=13)
    pdf.write_text(f"{film_stock} ({shots} shots)")
    pdf.ln(h=13)
    pdf.write_text(f"{camera} - load {load_date}")

    pdf.ln(h=18) # equivalent to a 6pt line break

    pdf.set_font(FONT, size=10)
    for location in locations:
        pdf.write_text(location)
        pdf.ln(h=10)

    end_x, end_y = pdf.get_x() + pdf.get_max_text_len() + BOX_PADDING, pdf.get_y()

    pdf.set_line_width(0.5)
    pdf.set_draw_color(r=0, g=0, b=0)
    dashed_line = lambda a, b, c, d: pdf.dashed_line(x1=a, y1=b, x2=c, y2=d, dash_length=2, space_length=3)

    dashed_line(start_x, start_y, start_x, end_y)
    dashed_line(start_x, start_y, end_x, start_y)
    dashed_line(end_x, start_y, end_x, end_y)
    dashed_line(start_x, end_y, end_x, end_y)

def draw_table(pdf, data):
    pdf.set_font(FONT, style="B", size=10)
    line_height = pdf.font_size * 1.2
    one_eigth = pdf.epw / 8

    def draw_row(single_cell, data, **kwargs):
        for (item, width) in data:
            pdf.multi_cell(single_cell * width, line_height, item, ln=3, max_line_height=pdf.font_size, **kwargs)
        pdf.ln(h=line_height)

    start_x, start_y = pdf.get_x(), pdf.get_y()
    draw_row(one_eigth, [("Film ID", 3), ("Film type", 2)])
    draw_row(one_eigth, [("Camera", 3), ("Lab", 2)])
    draw_row(one_eigth, [("Load date", 3), ("Dev date", 2)])

    pdf.set_font(FONT, size=10)

    pdf.set_xy(start_x, start_y)
    draw_row(one_eigth, [("", 1), (data["classifier"], 3), (data["film_stock"], 2)])
    draw_row(one_eigth, [("", 1), (data["camera"], 3), (data["lab"], 2)])
    draw_row(one_eigth, [("", 1), (data["load_date"], 3), (data["dev_date"], 2)])

    pdf.ln()

    pdf.set_font(FONT, style="B", size=10)

    draw_row(one_eigth, [("Shot #", 1), ("Exposure", 1), ("Shutter spd.", 1), ("Aperture", 1), ("Notes", 4)], border="B")
    
    pdf.set_font(FONT, size=10)

    for x in data["data"]:
        pdf.set_font(FONT, style="B", size=10)
        draw_row(one_eigth, [(x["date"], 1), (x["notes"], 7)], border="T")
        pdf.set_font(FONT, size=10)
        for y in x["data"]:
            draw_row(one_eigth, [(y["shot_number"], 1), (y["exposure"], 1), (y["shutter_speed"], 1), (y["aperture"], 1), (y["notes"], 4)])

    notes = data.get("notes")
    if notes is not None:
        pdf.ln(h=15)
        for line in notes.split("\n"):
            pdf.cell(0, 0, line)
            pdf.ln(h=10)

pdf = PDF(unit="pt")
pdf.add_page()

from_file = None

with open(INPUT_FILE) as f:
    if INPUT_FILE.endswith("json"):
        from_file = json.load(f)
    else:
        from_file = parse_shotlog(f.read())

draw_table(pdf, from_file)

pdf.ln(h=40)

y = pdf.get_y()
pdf.dashed_line(x1=0, y1=y, x2=PDF_W, y2=y, dash_length=2, space_length=5)

pdf.ln(h=40)

locations = []
seen = []
for x in from_file["data"]:
    y = x["notes"]
    if y == "":
        continue
    if y.lower() not in seen:
        locations.append(y)
        seen.append(y.lower())

draw_info_box(pdf, from_file["classifier"], from_file["film_stock"], from_file["shots"], from_file["camera"], from_file["load_date"], locations)

filename = sys.argv[1]
if filename.endswith(".json"):
    filename = ".".join(filename.split(".")[:-1]) + ".pdf"
elif not filename.endswith(".pdf"):
    filename += ".pdf"

pdf.output(filename)