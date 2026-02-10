import re
from datetime import datetime
import spacy

nlp = spacy.load("en_core_web_sm")

# ---------------- HELPERS ----------------

def normalize_date(date_str):
    formats = [
        "%m/%d/%y", "%m/%d/%Y",
        "%d/%m/%y", "%d/%m/%Y",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%d/%m/%Y")
        except:
            continue
    return "N/A"


def normalize_time(time_str):
    formats = ["%I:%M %p", "%H:%M"]
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).strftime("%I:%M %p")
        except:
            continue
    return "N/A"


def safe_float(match_list, default=0.0):
    try:
        return float(match_list[0])
    except:
        return default


# ---------------- MAIN PARSER ----------------

def parse_receipt(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    store = "Unknown"
    date = "N/A"
    time = "N/A"
    payment = "N/A"

    subtotal = 0.0
    tax = 0.0
    total = 0.0
    items = []
    seen = set()

    # ---------- STORE ----------
    for l in lines[:5]:
        if not re.search(r"\d", l) and len(l) > 3:
            store = l
            break

    # ---------- DATE & TIME (REGEX FIRST) ----------
    date_pattern = r"(\d{1,2}/\d{1,2}/\d{2,4})"
    time_pattern = r"(\d{1,2}:\d{2}\s?(AM|PM|am|pm))"

    for l in lines[:10]:
        if date == "N/A":
            d = re.search(date_pattern, l)
            if d:
                date = normalize_date(d.group(1))

        if time == "N/A":
            t = re.search(time_pattern, l)
            if t:
                time = normalize_time(t.group(1))

    # ---------- spaCy FALLBACK ----------
    if date == "N/A" or time == "N/A":
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DATE" and date == "N/A":
                date = normalize_date(ent.text)
            if ent.label_ == "TIME" and time == "N/A":
                time = normalize_time(ent.text)

    # ---------- PAYMENT ----------
    lower = text.lower()
    if "cash" in lower:
        payment = "Cash"
    elif any(x in lower for x in ["visa", "master", "credit", "debit"]):
        payment = "Card"

    # ---------- TOTALS & ITEMS ----------
    for l in lines:
        low = l.lower()

        if "subtotal" in low:
            subtotal = safe_float(re.findall(r"\d+\.\d{2}", l))
            continue

        if "tax" in low:
            tax += safe_float(re.findall(r"\d+\.\d{2}", l))
            continue

        if re.search(r"\b(total|grand total)\b", low):
            total = safe_float(re.findall(r"\d+\.\d{2}", l))
            continue

        # Item line
        m = re.match(r"(.+?)\s+(\d+\.\d{2})$", l)
        if m:
            name = m.group(1).strip()
            price = float(m.group(2))

            if any(x in name.lower() for x in ["tax", "total", "subtotal", "change"]):
                continue

            key = f"{name}-{price}"
            if key not in seen:
                seen.add(key)
                items.append({"name": name, "price": round(price, 2)})

    # ---------- SAFETY FIX ----------
    if subtotal == 0.0 and items:
        subtotal = round(sum(i["price"] for i in items), 2)

    if total == 0.0:
        total = round(subtotal + tax, 2)

    return {
        "store": store,
        "date": date,
        "time": time,
        "payment": payment,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total": round(total, 2),
        "items": items
    }