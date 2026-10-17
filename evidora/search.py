import re
from collections import Counter
from evidora.db import papers, pages
STOP=set("a an the and or but if in on at to from for of with by as is are was were be been this that these those it its we our they their using used based paper study method results data".split())

def tokens(text):
    return [x for x in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]+",text.lower()) if len(x)>1 and x not in STOP]

def search(query, limit=8):
    terms=set(tokens(query))
    if not terms: return []
    out=[]
    for p in papers():
        title=p.get("title") or p["filename"]
        for pg in pages(p["id"]):
            txt=pg["text"]; words=tokens(txt); counts=Counter(words)
            overlap=terms.intersection(counts)
            if not overlap: continue
            clean=re.sub(r"\s+"," ",txt).strip(); low=clean.lower()
            pos=[low.find(t) for t in terms if low.find(t)>=0]
            start=max(0,min(pos)-150) if pos else 0
            snippet=("…" if start else "")+clean[start:start+650]+("…" if start+650<len(clean) else "")
            out.append({"title":title,"filename":p["filename"],"page_number":pg["page_number"],
                        "snippet":snippet,"score":len(overlap)*2+sum(min(counts[t],3) for t in overlap)*.3})
    return sorted(out,key=lambda x:x["score"],reverse=True)[:limit]
