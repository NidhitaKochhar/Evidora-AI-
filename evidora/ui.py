import streamlit as st

def theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
    .stApp{background:#F6F8FC;color:#192D49}
    [data-testid="stSidebar"]{background:#10243A}
    [data-testid="stSidebar"] *{color:#F4F8FC!important}
    .hero{padding:30px 34px;border-radius:22px;background:linear-gradient(120deg,#10243A,#1A4960 60%,#197D80);color:white;margin:4px 0 24px;box-shadow:0 12px 30px #10243A12}
    .hero h1{font-family:'Manrope',sans-serif;font-size:2.15rem;font-weight:800;margin:0 0 8px;color:white;letter-spacing:-.04em}
    .hero p{margin:0;color:#D7E8F0;max-width:800px}
    .eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:.72rem;font-weight:700;color:#70DED1;margin-bottom:10px}
    .stat{background:white;border:1px solid #E5EBF2;border-radius:16px;padding:18px;min-height:118px}
    .stat-label{color:#718198;font-size:.82rem;font-weight:600}.stat-value{font-family:'Manrope';color:#172B48;font-size:1.8rem;font-weight:800;margin:5px 0}.stat-sub{color:#8492A5;font-size:.76rem}
    .section{font-family:'Manrope';font-size:1.2rem;font-weight:800;margin:28px 0 14px;color:#1A2D49}
    .feature{background:white;border:1px solid #E5EBF2;border-radius:16px;padding:22px;min-height:180px}
    .feature-icon{width:42px;height:42px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:#E8F8F5;color:#0A8D80;font-size:1.4rem;font-weight:800}
    .feature h3{color:#1A2D49;font-size:1.05rem;margin:14px 0 6px}.feature p{color:#718198;font-size:.88rem;line-height:1.55}
    .side-note{padding:14px;border:1px solid #36516B;background:#18334D;border-radius:12px;color:#C7D6E3;font-size:.8rem;line-height:1.6}
    .stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:650}
    .stButton>button[kind="primary"],.stDownloadButton>button{background:#087F78;color:white;border:0}
    [data-testid="stFileUploader"]{background:white;border:1px dashed #B7C8D8;border-radius:14px}
    </style>""",unsafe_allow_html=True)

def header(title,subtitle):
    st.markdown(f"<div class='hero'><div class='eyebrow'>EVIDORA AI · RESEARCH INTELLIGENCE</div><h1>{title}</h1><p>{subtitle}</p></div>",unsafe_allow_html=True)

def stat(col,label,value,sub):
    col.markdown(f"<div class='stat'><div class='stat-label'>{label}</div><div class='stat-value'>{value}</div><div class='stat-sub'>{sub}</div></div>",unsafe_allow_html=True)
