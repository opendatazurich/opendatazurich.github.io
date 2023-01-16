import os
import json
import csv
import difflib
from wasabi import color

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def diff_strings(a, b):
    output = []
    matcher = difflib.SequenceMatcher(None, a, b)
    changed = False
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.append(a[a0:a1])
        elif opcode == "insert":
            changed = True
            output.append(color(b[b0:b1], fg=16, bg="green"))
        elif opcode == "delete":
            changed = True
            output.append(color(a[a0:a1], fg=16, bg="red"))
        elif opcode == "replace":
            changed = True
            output.append(color(b[b0:b1], fg=16, bg="green"))
            output.append(color(a[a0:a1], fg=16, bg="red"))

    output.append(" ")
    if not changed:
        return ""

    return "".join(output)


csv_path = os.path.join(__location__, 'ckan_attributes.csv')
with open(csv_path, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_attr = json.loads(row['csv_attributes'])
        ckan_attr = json.loads(row['ckan_attributes'])
        csv_attr.sort()
        ckan_attr.sort()

        #ckan_attr.pop()
        #ckan_attr.pop()

        diff = diff_strings(",".join(csv_attr), ",".join(ckan_attr))
        if diff:
            print(diff)
            #print("\n".join(csv_attr))
            #print("\n".join(ckan_attr))
        else:
            print("No diff.")