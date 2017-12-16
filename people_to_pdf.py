import json

from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.units import cm, mm, inch, pica
import labels

BORDER=False

specs = labels.Specification(216, 279, 3, 10, 66, 25,
        corner_radius=2,
        left_margin=6,
        right_margin=4,
        column_gap=4,
        top_margin=15,
        bottom_margin=14,
        row_gap=0,
        )

def load_people(filename='people.json'):
    with open('people.json', 'r') as infile:
        return json.load(infile)

# 215.9 by 279.4
def write_label(label, width, height, person):
    text = "\n".join((person['name'], person['addresses'][0]))
    lab = Label()
    lab.setOrigin(8, height - 5)
    lab.fontSize = 14
    lab.setText(text)
    lab.boxAnchor = 'nw'
    label.add(lab)

if __name__ == '__main__':
    people = load_people()
    for person in people:
        if len(person['addresses']) > 1:
            print "WARNING: {} has too many addresses!".format(person['name'])
        elif not person['addresses']:
            print "WARNING: {} has NO addresses!".format(person['name'])
    people = [ person for person in people if len(person['addresses']) == 1 ]

    OUT_FILENAME = 'labels.pdf'
    sheet = labels.Sheet(specs, write_label, border=BORDER)
    sheet.add_labels(people)
    with open(OUT_FILENAME, 'wb') as outfile:
        sheet.save(outfile)
    print "Wrote {}".format(OUT_FILENAME)
