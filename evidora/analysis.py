import re
from collections import Counter
from evidora.db import pages

CONCEPTS=["sepsis","MIMIC","PhysioNet","XGBoost","Random Forest","LSTM","Transformer","CNN","deep learning",
"machine learning","external validation","explainability","fairness","class imbalance","missing data",
"early prediction","AUROC","SHAP"]

def compare(rows):
    fields=["dataset","model","population","sample_size","target","prediction_horizon","metrics","validation","findings","limitations"]
    import pandas as pd
    frame=pd.DataFrame([{"Paper":r["paper"],**{k:r.get(k,"Not reported in extracted text") for k in fields}} for r in rows])
    warnings=[]
    for field in ["dataset","target","prediction_horizon","validation"]:
        vals={str(r.get(field,"")).strip().lower() for r in rows if r.get(field) and r.get(field)!="Not reported in extracted text"}
        if len(vals)>1: warnings.append(f"{field.replace('_',' ').title()} differs across studies; direct metric comparisons may be unfair.")
    return frame,warnings

def trends(ps):
    years=Counter(); terms=Counter(); texts=[]
    for p in ps:
        if p.get("year"): years[str(p["year"])]+=1
        text=" ".join(x["text"] for x in pages(p["id"])).lower(); texts.append(text)
        for term in CONCEPTS:
            n=len(re.findall(r"\b"+re.escape(term.lower())+r"\b",text))
            if n: terms[term]+=n
    gaps=[]
    if len(ps)<3: gaps.append("Add more papers before interpreting collection-level patterns.")
    else:
        absent=[c for c in CONCEPTS if not any(c.lower() in t for t in texts)]
        if absent: gaps.append("Topics not detected in this collection: "+", ".join(absent[:8])+". Check the wider literature.")
        if sum("external validation" in t for t in texts)<max(1,len(ps)//3):
            gaps.append("External validation was not explicitly detected in many papers; manually inspect validation sections.")
    return {"years":dict(sorted(years.items())),"terms":dict(terms.most_common(15)),"gaps":gaps}

def concept_map(ps):
    counts=Counter(); edges=[]
    for p in ps:
        text=" ".join(x["text"] for x in pages(p["id"])).lower()
        for term in CONCEPTS:
            if re.search(r"\b"+re.escape(term.lower())+r"\b",text):
                counts[term]+=1; edges.append({"paper":p.get("title") or p["filename"],"relation":"MENTIONS","concept":term})
    return [{"concept":k,"papers":v} for k,v in counts.most_common()],edges
