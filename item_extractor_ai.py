import re

def extract_items(text):
    items = []
    for line in text.split("\n"):
        if re.search(r"\$\d+\.\d{2}", line):
            items.append(line.strip())
    return items