import os
import streamlit as st
import pandas as pd
from evidora.db import init_db, add_paper, papers, pages, remove_paper
from evidora.pdf_tools import parse_pdf
from evidora.search import search
from evidora.agent import research_agent
from evidora.ai import answer, extract_fields
from evidora.analysis import trends, concept_map, compare
from evidora.ui import theme, header, stat
import html
import re

def highlight_query(text, query):
    """Safely highlight query terms in retrieved passages."""
    import html, re
    safe = html.escape(str(text or ""))
    terms = sorted({t for t in re.findall(r"[A-Za-z0-9_-]+", query or "") if len(t) > 1}, key=len, reverse=True)
    if not terms:
        return safe
    pattern = re.compile("(" + "|".join(re.escape(t) for t in terms) + ")", re.IGNORECASE)
    return pattern.sub(r'<mark style="background:#ffe58f;color:#222;padding:1px 2px;border-radius:3px;">\1</mark>', safe)

st.set_page_config(page_title="Evidora AI", page_icon="🔎", layout="wide")
theme()
init_db()

if "chat" not in st.session_state: st.session_state.chat = []
if "compare_rows" not in st.session_state: st.session_state.compare_rows = []

with st.sidebar:
    st.markdown("## ◈ Evidora AI")
    st.caption("Research, backed by evidence.")
    page = st.radio("WORKSPACE", ["Overview", "Paper Library", "Ask Evidora", "Study Comparison", "Research Insights", "Knowledge Map", "Settings & Help"])
    st.divider()
    st.caption(f"📚 {len(papers())} paper(s) indexed")
    st.markdown("<div class='side-note'><b>Evidence first.</b><br>Verify generated answers against the original papers.</div>", unsafe_allow_html=True)

if page == "Overview":
    header("Research, made clearer.", "Explore papers, trace evidence, compare studies, and turn scientific literature into structured insights.")
    ps = papers()
    a,b,c,d = st.columns(4)
    stat(a, "Papers in library", len(ps), "Your research collection")
    stat(b, "Pages indexed", sum(p["page_count"] for p in ps), "Extracted PDF pages")
    stat(c, "Research tools", "5", "Search, ask, compare, map, export")
    stat(d, "Evidence-first", "On", "Source references included")
    st.markdown("<div class='section'>Start with a task</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    cards = [
        ("↥", "Build your library", "Upload papers and extract searchable text with page-level provenance."),
        ("⌕", "Ask your papers", "Find relevant passages and get evidence-grounded responses."),
        ("⇄", "Compare studies", "Inspect datasets, methods, metrics, and limitations side by side.")
    ]
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(f"<div class='feature'><div class='feature-icon'>{icon}</div><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='section'>Recently added</div>", unsafe_allow_html=True)
    if ps:
        st.dataframe(pd.DataFrame([{k:p.get(k) for k in ["title","filename","year","page_count","created_at"]} for p in ps[:8]]), use_container_width=True, hide_index=True)
    else:
        st.info("Your library is empty. Open Paper Library to upload your first PDF.")

elif page == "Paper Library":
    header("Paper library", "Upload, organize, and search your research collection.")
    left, right = st.columns([1,1.2], gap="large")
    with left:
        st.markdown("### Add papers")
        uploads = st.file_uploader("Upload scientific PDFs", type=["pdf"], accept_multiple_files=True)
        if uploads and st.button("Process PDFs", type="primary", use_container_width=True):
            prog = st.progress(0)
            for i, f in enumerate(uploads):
                try:
                    data = f.getvalue()
                    result = parse_pdf(data, f.name)
                    new = add_paper(f.name, data, result)
                    if new: st.success(f"Added {f.name} · {result['page_count']} pages")
                    else: st.warning(f"{f.name} is already in the library.")
                except Exception as e:
                    st.error(f"{f.name}: {e}")
                prog.progress((i+1)/len(uploads))
            st.rerun()
        st.caption("Scanned PDFs may need OCR; this version extracts embedded PDF text.")
    with right:
        st.markdown("### Search the library")
        q = st.text_input("Search titles and page text", placeholder="enter keywords, e.g. early prediction, dataset,performance")
        if q:
            found = search(q, 10)
            if not found: st.info("No matching passages found.")
            for r in found:
                with st.container(border=True):
                    st.markdown(f"**{r['title']}** · page {r['page_number']}")
                    st.caption(r["filename"])
                    st.markdown(highlight_query(r["snippet"], q), unsafe_allow_html=True)
    st.markdown("<div class='section'>Your papers</div>", unsafe_allow_html=True)
    for p in papers():
        with st.container(border=True):
            c1,c2 = st.columns([5,1])
            c1.markdown(f"**{p['title'] or p['filename']}**")
            c1.caption(f"{p['filename']} · {p.get('year') or 'Year unknown'} · {p['page_count']} pages")
            if p.get("warnings"): c1.warning(p["warnings"])
            if c2.button("Delete", key=f"del_{p['id']}"):
                remove_paper(p["id"]); st.rerun()
            with st.expander("View extracted pages"):
                for pg in pages(p["id"]):
                    st.markdown(f"**Page {pg['page_number']}**")
                    
                    page_text = pg["text"] or "[No embedded text detected]"
                    formatted_text = re.sub(r"(?<!\n)\n(?!\n)", " ", page_text)

                    st.markdown(
                        f"<div style='font-size:16px; line-height:1.8; white-space:pre-wrap;'>{html.escape(formatted_text)}</div>",
                        unsafe_allow_html=True,
                    )


elif page == "Ask Evidora":
    header("Ask Evidora", "Ask questions about your uploaded papers. Inspect the source passages before relying on the answer.")
    if not papers(): st.info("Upload papers in Paper Library first.")
    else:
        q = st.text_area("Research question", placeholder="Which datasets and models are used, and what limitations are reported?", height=100)
        use_ai = st.toggle("Use configured LLM for synthesis", value=bool(os.getenv("OPENAI_API_KEY")))
        if st.button("Find evidence & answer", type="primary", disabled=not q.strip()):
            with st.spinner("Research agent: planning, retrieving, and checking evidence…"):
                agent_result = research_agent(q, use_ai=use_ai)
                st.session_state.chat.append({"q":q,"response":agent_result["response"],"results":agent_result["results"],"steps":agent_result["steps"]})
        for item in reversed(st.session_state.chat[-5:]):
            st.markdown("#### " + item["q"])
            with st.expander("Research agent workflow", expanded=False):
                for step in item.get("steps", []): st.markdown(f"- {step}")
            st.write(item["response"]["answer"])
            if item["response"].get("notice"): st.info(item["response"]["notice"])
            st.markdown("**Supporting passages (highlighted query terms)**")
            if not item["results"]: st.warning("No supporting passages found.")
            for r in item["results"]:
                with st.container(border=True):
                    st.markdown(f"**{r['title']}** · page {r['page_number']}")
                    st.caption(r["filename"]); st.markdown(highlight_query(r["snippet"], item["q"]), unsafe_allow_html=True)
            st.divider()

elif page == "Study Comparison":
    header("Study comparison", "Compare study attributes and notice where a direct comparison may be unfair.")
    ps = papers()
    if len(ps) < 2: st.info("Upload at least two papers.")
    else:
        by_title = {p["title"] or p["filename"]:p for p in ps}
        selected = st.multiselect("Select papers", list(by_title), default=list(by_title)[:min(3,len(by_title))], max_selections=6)
        if selected and st.button("Extract & compare", type="primary"):
            rows = []
            bar = st.progress(0)
            for i, name in enumerate(selected):
                p = by_title[name]
                full = "\n".join(x["text"] for x in pages(p["id"]))
                details = extract_fields(full, bool(os.getenv("OPENAI_API_KEY")))
                details.update({"paper":name,"source":p["filename"]})
                rows.append(details); bar.progress((i+1)/len(selected))
            st.session_state.compare_rows = rows
        if st.session_state.compare_rows:
            frame, warnings = compare(st.session_state.compare_rows)
            st.dataframe(frame, use_container_width=True, hide_index=True)
            for warning in warnings: st.warning(warning)
            st.caption("“Not reported” means the field was not detected in extracted text, not necessarily absent from the paper.")
            st.download_button("Download comparison CSV", frame.to_csv(index=False).encode(), "evidora_comparison.csv", "text/csv")
            with st.expander("Raw extracted fields"): st.json(st.session_state.compare_rows)

elif page == "Research Insights":
    header("Research insights", "Explore patterns in your current collection. Signals are exploratory, not proof of global research novelty.")
    ps = papers()
    if not ps: st.info("Upload papers to generate insights.")
    else:
        result = trends(ps)
        left,right = st.columns(2)
        with left:
            st.markdown("### Papers by publication year")
            if result["years"]: st.bar_chart(result["years"])
            else: st.info("No publication years detected.")
        with right:
            st.markdown("### Frequently mentioned concepts")
            if result["terms"]: st.bar_chart(result["terms"])
            else: st.info("No concepts detected.")
        st.markdown("### Candidate research directions")
        st.warning("These are only collection-level clues. Check the wider literature before claiming a research gap.")
        for g in result["gaps"]: st.markdown("- " + g)

elif page == "Knowledge Map":
    header("Knowledge map", "A lightweight concept map based on detected terms in your uploaded papers.")
    ps = papers()
    if not ps: st.info("Upload papers first.")
    else:
        nodes, edges = concept_map(ps)
        st.markdown(f"**{len(nodes)} concepts** · **{len(edges)} paper-to-concept links**")
        st.caption("Keyword-based map for navigation; not a validated scientific ontology.")
        if edges:
            st.dataframe(pd.DataFrame(edges), use_container_width=True, hide_index=True)
            st.markdown("### Concept frequency")
            st.bar_chart({x["concept"]:x["papers"] for x in nodes})
        else: st.info("No known concepts detected.")

else:
    header("Settings & help", "Configuration, privacy, and limitations.")
    st.markdown("### Optional AI setup")
    st.write("Without an API key, search and a passage-based evidence digest still work. To enable generated answers and richer extraction, set these environment variables before starting Streamlit:")
    st.code('OPENAI_API_KEY="your-key"\nOPENAI_MODEL="gpt-4o-mini"')
    st.warning("API usage may cost money. Retrieved passages and paper text sent for extraction are processed by your configured AI provider.")
    st.markdown("### Important limitations")
    st.markdown("""
- AI answers may be wrong. Check every cited passage in the original PDF.
- Retrieval is keyword-based in this starter version; semantic embeddings are a future enhancement.
- Scanned PDF OCR is not included.
- Heuristic extraction may miss or misclassify research fields.
- Research trends and candidate gaps reflect only your uploaded collection.
- Authentication, per-user isolation, durable cloud storage, and production security are not implemented.
- Do not upload confidential or copyrighted material unless you have permission and understand data handling.
""")
    ps = papers()
    if ps:
        meta = pd.DataFrame([{k:p.get(k) for k in ["id","filename","title","authors","year","page_count","created_at"]} for p in ps])
        st.download_button("Export library metadata CSV", meta.to_csv(index=False).encode(), "evidora_library.csv", "text/csv")
