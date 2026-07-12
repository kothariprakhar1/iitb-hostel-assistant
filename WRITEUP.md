# Write-up: IITB Hostel & Campus Life Assistant

## 1. Chosen Scope and Why

I chose the **Hostel & Campus Life Assistant** scope over the alternatives (Academic Assistant, Council/Club Assistant, General Insti Assistant) because this is the area where incoming students face the most confusion — more so than academics or clubs. Questions about hostel rules, mess timings, allotment, and campus facilities typically come up *before* a student even arrives on campus, at a time when there's no senior or mentor readily available to ask. A RAG-based assistant grounded in real hostel documents directly addresses this gap by giving new students an always-available, accurate source of information instead of having to guess or wait to ask someone.

## 2. Data Sources Used

The assistant is built on 5 real source documents covering the core areas a new student is most likely to have questions about:

1. **`hostel16_rules.txt`** — General hostel rules for Hostel 16 (visiting hours, guest policy, etc.)
2. **`hostel16_facilities.txt`** — Facilities available within Hostel 16
3. **`hostel_allotment_instructions.txt`** — Instructions and process for hostel room allotment
4. **`hostel_mess_rules.txt`** — Mess timings, rebate policy, guest dining, utensil rules, and mess behavior guidelines (sourced from IITB Hostel 10's official mess rules page)
5. **`hostel_discipline_rules.txt`** — General hostel discipline and conduct rules, including behavior expectations, smoking/drinking policy, pet policy, hostel accommodation overview, and DoSA administrative structure (sourced from IITB Hostel 10 and Gymkhana housing pages)

These five documents were chosen because, together, they cover most of the *general* doubts a new student has about hostel life — rules, facilities, how allotment works, mess logistics, and discipline expectations — rather than being narrowly focused on just one hostel or one topic.

## 3. Chunking Strategy and Why

The system uses a **fixed-size sliding-window chunking strategy**, implemented in `ingest.py`:

- Each source document is first cleaned (excess whitespace and blank lines collapsed) and then split into individual words.
- A window of **350 words** (`CHUNK_SIZE_WORDS`) is used per chunk.
- Successive chunks **overlap by 50 words** (`CHUNK_OVERLAP_WORDS`), meaning each new chunk starts 50 words before the previous chunk ended.
- This repeats across the document until the entire text is covered.

This approach was chosen for a few reasons:
- **Format-agnostic**: since the source documents come from a mix of formats (plain text, PDFs, scraped HTML), a word-count-based chunker doesn't depend on document structure like headings or paragraphs, which can be inconsistent or missing after text extraction.
- **Predictable chunk size**: fixed-size chunks keep embedding and retrieval behavior consistent — no single chunk is too large (which could dilute relevance in the vector search) or too small (which could cut off necessary context).
- **Overlap prevents context loss**: without overlap, a rule and its explanation could be split across two separate chunks with neither containing the full picture. The 50-word overlap acts as a buffer so information near chunk boundaries isn't lost during retrieval.

Retrieval uses cosine similarity (via ChromaDB) with `TOP_K = 4` chunks retrieved per query, and a distance threshold (`MAX_DISTANCE_THRESHOLD = 1.0`) acts as a guardrail — if even the closest retrieved chunk is too dissimilar to the query, the system skips the LLM call entirely and returns "I don't know," avoiding both hallucination and unnecessary API calls.

## 4. Known Limitations and Future Improvements

- **Incomplete hostel-specific coverage**: The assistant does not cover rules specific to every individual hostel at IITB — some documents are hostel-specific (e.g. Hostel 16, Hostel 10) rather than representing all 17 hostels, so answers for hostels not directly covered may be incomplete or generic.
- **No academic coverage**: Since the chosen scope is strictly Hostel & Campus Life, the assistant cannot answer questions about academics — course registration, grading policy, or exam rules — even though these are common student questions. This was an intentional scope decision to keep the project focused within the given timeframe.
- **Single-turn only**: The assistant currently answers each question independently and does not support multi-turn conversational memory (e.g. follow-up questions that depend on previous context).
- **Static document set**: Source documents are manually curated `.txt` files rather than being live-scraped or auto-updated, so the assistant's knowledge is only as current as the last time the `data/` folder was updated and the index rebuilt.

With more time, I would expand the data sources to cover all 17 hostels individually, add an academic-info module (or combine scopes into a general assistant), and add multi-turn memory so students can ask natural follow-up questions.
