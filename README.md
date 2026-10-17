# Evidora AI — Research Intelligence

A Python + Streamlit starter app for scientific PDF libraries, page-level text extraction, keyword search, evidence digests, optional LLM synthesis, study attribute extraction, comparison, collection-level trend charts, a lightweight concept map, and CSV exports.

**Important:** This is a feature-rich starter, not a production-validated scientific system. AI answers and heuristic extraction can be wrong. Verify results against original papers.

## Quick start (Windows)

1. Extract the ZIP and open the `Evidora_AI` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead. Keep the terminal open while using the app. The browser opens at `http://localhost:8501`.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Optional AI configuration

Without an API key, upload, extraction, keyword search, and evidence digest work locally. To enable answer synthesis and richer extraction, set an OpenAI-compatible API key in the terminal before starting Streamlit:

```powershell
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-4o-mini"
streamlit run app.py
```

Never commit API keys to GitHub. API calls may incur costs. When enabled, retrieved passages and paper text used for extraction are sent to the configured provider. Only use documents you are authorized to process.

## How to use

1. Open **Paper Library** and upload PDFs.
2. Click **Process PDFs**.
3. Search your library or inspect extracted pages.
4. Open **Ask Evidora** and ask a question.
5. Check the displayed source passages and page numbers.
6. Use **Study Comparison** with two or more papers.
7. Explore **Research Insights** and **Knowledge Map**.
8. Export comparison or library metadata as CSV.

## Deployment to Streamlit Community Cloud

1. Create a GitHub repository and push the project code.
2. Do not upload PDFs, the `data/` folder, database files, `.env`, or secrets.
3. Visit https://share.streamlit.io/, sign in with GitHub, select the repository, branch, and `app.py`.
4. Deploy; add any API key under the app's Secrets settings.

**Persistence/security warning:** cloud app filesystems may be ephemeral. This starter does not provide user accounts, per-user isolation, durable cloud file storage, rate limits, or production-grade security. Before inviting people to store papers long-term, configure persistent storage and access controls.

## Included features

- PDF validation, duplicate detection, metadata guesses, page-level extraction
- SQLite metadata and page text store
- Keyword retrieval with source title/page references and highlighted query terms
- Retrieval-augmented generation (RAG): retrieve paper passages, ground answers in evidence, and retain source/page references; optional LLM synthesis
- Heuristic or optional LLM-based study-field extraction
- Study comparison with comparability warnings
- Collection-level trend charts and candidate-gap prompts
- Keyword-based concept map
- CSV exports, styled UI, starter tests

## Research agent and RAG workflow

Ask Evidora uses a lightweight tool-using agent: it plans one or two search queries, retrieves and deduplicates page passages, assesses evidence coverage, refines retrieval with a keyword query when useful, and synthesizes an answer from the retrieved context. Query terms are highlighted in search results and supporting passages. With no API key, the system still runs locally and returns an evidence digest; with an OpenAI-compatible API key, the retrieved context can be passed to the configured LLM for grounded synthesis. This is a small demonstrator agent, not an autonomous production agent.

## Current limitations / next milestones

- Retrieval is currently lexical/keyword-based; evaluate semantic retrieval and hybrid ranking before production use.
- Scanned PDF OCR is not included.
- Metadata and heuristic extraction can be wrong.
- Citation presence does not guarantee claim support; build and evaluate claim-level support validation.
- Gap analysis is exploratory and only reflects the uploaded collection.
- Knowledge Map uses a small keyword list, not a validated ontology.
- Add field-level source evidence, improved comparison warnings, evaluation datasets, authentication, background jobs, durable storage, and deployment hardening before production use.

## Structure

```text
Evidora_AI/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── evidora/
│   ├── config.py
│   ├── db.py
│   ├── pdf_tools.py
│   ├── search.py
│   ├── ai.py
│   ├── analysis.py
│   └── ui.py
├── tests/
├── data/
└── .streamlit/
```
