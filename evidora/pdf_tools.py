import fitz, hashlib, re
from io import BytesIO

def parse_pdf(data, filename):
    if not data or not data.startswith(b"%PDF"): raise ValueError("File does not appear to be a valid PDF.")
    doc = fitz.open(stream=BytesIO(data), filetype="pdf")
    if doc.is_encrypted: raise ValueError("PDF is password-protected; upload an unlocked copy.")
    pages, warnings = [], []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if len(text) < 30: warnings.append(f"Page {i+1} has little embedded text; OCR may be needed.")
        pages.append({"page_number":i+1,"text":text})
    full = "\n".join(p["text"] for p in pages)
    meta = doc.metadata or {}
    title = _clean(meta.get("title")) or _guess_title(full, filename)
    authors = _clean(meta.get("author"))
    years = re.findall(r"\b(?:19|20)\d{2}\b", str(meta) + " " + full[:5000])
    year = int(years[0]) if years else None
    m = re.search(r"(?is)\babstract\b\s*[:\-]?\s*(.{100,1600}?)(?=\n\s*(?:keywords|index terms|introduction)\b)",full)
    abstract = re.sub(r"\s+"," ",m.group(1)).strip() if m else ""
    return {"file_hash":hashlib.sha256(data).hexdigest(),"title":title,"authors":authors,"year":year,
            "abstract":abstract,"page_count":len(doc),"pages":pages,"warnings":" ".join(dict.fromkeys(warnings))}

def _clean(x):
    x = re.sub(r"\s+"," ",str(x or "")).strip()
    return "" if x.lower() in {"unknown","untitled","none"} else x

def _guess_title(text, filename):
    for line in text.splitlines():
        line = re.sub(r"\s+"," ",line).strip()
        if 12 <= len(line) <= 180 and not line.lower().startswith(("abstract","keywords","doi","http")): return line
    return filename.rsplit(".",1)[0]
