# IITB Hostel & Campus Life Assistant

A RAG-powered assistant that answers questions about IIT Bombay hostel
and campus life, grounded in real institute documents. It refuses to
answer ("I don't know") when the retrieved context doesn't support
a confident answer.

## Scope covered
- Hostel allotment & room rules
- Mess menu / mess rules & fees
- Hostel facilities (gym, common room, laundry, etc.)
- Campus facilities (SAC, hospital, library, gymkhana grounds)
- Guest / curfew / visitor policies

## Project structure
iitb-hostel-assistant/
── config.py         
── ingest.py          
── build_index.py     
── rag_chain.py       
── data/               
── requirements.txt
── README.md

## Setup

1. Create and activate a virtual environment (recommended):
python -m venv venv
source venv/bin/activate     

2. Install dependencies:
pip install -r requirements.txt

3. Set your Gemini API key (get one free at https://aistudio.google.com/apikey):
setx GEMINI_API_KEY "AI..."            # Windows (restart terminal after)

4. Add your source documents (PDF/TXT/HTML/MD) into the `data/` folder.
   You need at least 5 reaal documents (6 are already included covering
   hostel allotment, mess rules, hostel facilities, campus facilities,
   and guest/curfew policies).

## Running the pipeline

1. **Check chunking** (optional sanity check):
python ingest.py

2. **Build the vector index** (run this whenever you add/change documents):
python build_index.py

3. **Ask a question from the command line**:
python rag_chain.py "What is the curfew time in the hostel?"

4. **Web UI**: not yet built — this repo currently covers the retrieval +
   LLM pipeline (Steps 1, 4–7). Wrap `rag_chain.answer_question()` in a
   Streamlit or Gradio app for the final UI (Step 9).

## How the guardrail works (Step 7)
Before calling the LLM at all, the closest retrieved chunk's distance is
checked against `MAX_DISTANCE_THRESHOLD` in `config.py`. If nothing
retrieved is close enough, the assistant returns "I don't know."
immediately without spending an LLM call. Additionally, the system
prompt instructs the model itself to say "I don't know." if the context
doesn't support an answer, as a second layer of grounding.

## Tuning
- `CHUNK_SIZE_WORDS` / `CHUNK_OVERLAP_WORDS` in `config.py` control chunk granularity.
- `TOP_K` controls how many chunks are retrieved per query.
- `MAX_DISTANCE_THRESHOLD` controls how strict the "I don't know" guardrail is —
  lower it if the assistant is answering things it shouldn't; raise it if it's
  saying "I don't know" too often on things it should know.