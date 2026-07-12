IIT Bombay Hostel and Campus Life Assistant
This is a RAG-powered assistant designed to answer questions about IIT Bombay hostel and campus life using real instetute documents. It is built to refuse answers ("I don't know") if the retrieved context does not support a confident response.

Scope Covered
Hostel allotment and room rules

Mess menu, mess rules, and fees

Hostel facilities like gym, common room, and laundry

Campus facilities including SAC, hospital, library, and gymkana grounds

Guest, curfew, and visitor policies

Project Structure
Plaintext
iitb-hostel-assistant/
├── config.py
├── ingest.py
├── build_index.py
├── rag_chain.py
├── data/
├── requirements.txt
└── README.md
Setup
First, create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate
Next, install the required dependencies:

Bash
pip install -r requirements.txt
Set your Gemini API key. You can get one for free at the Google AI Studio website:

Bash
setx GEMINI_API_KEY "your_api_key_here"


Now, add your source documents in PDF, TXT, HTML, or MD format into the data folder. You need at least 5 real documents. The setup already includes 6 documents covering hostel allotment, mess rules, hostel facilities, campus facilities, and guest or curfew policies.

Running the Pipeline
To check the chunking and do a quick sanity check, run:

Bash
python ingest.py
To build the vector index, run the following command. Make sure to run this whenever you add or change documents:

Bash
python build_index.py
To ask a question directly from the command line, use:

Bash
python rag_chain.py "What is the curfew time in the hostel?"
The web UI is not built yet. This repository currently covers the retrieval and LLM pipeline. You can wrap the answer question function in a Streamlit or Gradio app if you want to build the final UI later.

How the Guardrail Works
Before the system calls the LLM, it checks the distance of the closest retrieved chunk against the maximum distance threshold set in the config file. If the retrieved content is not close enough to the question, the assistant returns "I don't know" right avay. This saves an LLM call.

As a second layer of safety, the system prompt also tells the model itself to say "I don't know" if the provided text does not have the answer.

Tuning
You can adjust the settings in the config file to change how the system behaves:

CHUNK_SIZE_WORDS and CHUNK_OVERLAP_WORDS control how big or small the text pieces are.

TOP_K controls how many text pieces the system pulls for each qustion.

MAX_DISTANCE_THRESHOLD controls how strict the "I don't know" guardrail is. You can lower this number if the assistant answers things it should not. You can raise it if the assistant says "I don't know" too often for questions it should actually answer.
