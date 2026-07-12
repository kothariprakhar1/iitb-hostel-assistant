Chosen Scope and Why
I picked the Hostel and Campus Life Assistant because this is where new students get confused the most. It is usually a bigger headache than academics or clubs. Most questions about hostel rules, food timings, room allotment, and campus facilities come up before a student even gets to campus. At that time, they do not have a senior or mentor around to ask. Using a RAG system with real hostel documents solves this issue. It gives new students a reliable way to get correct information anytime instead of just guessing or waiting to find someone to ask.

Data Sources Used
The assistant uses 5 real files that cover the main things a new student would ask about:

hostel16_rules.txt — Basic rules for Hostel 16 like visiting hours and guest policies.

hostel16_facilities.txt — Services and facilities inside Hostel 16.

hostel_allotment_instructions.txt — The steps and process for getting a hostel room.

hostel_mess_rules.txt — Mess timings, how to get refunds for missed meals, guest charges, rules for utensils, and behavior guidelines. This comes from the official IITB Hostel 10 mess page.

hostel_discipline_rules.txt — General discipline and behavior rules. It covers smoking and drinking policies, pet rules, housing overviews, and the DoSA structure. This comes from the IITB Hostel 10 and Gymkhana housing pages.

These five files cover most general doubts about hostel life. They focus on overall rules, facilities, room allotment, mess setup, and behavior, instead of looking at just one tiny topic.

Chunking Strategy and Why
The system splits text using a fixed size with a sliding window inside the ingest file:

The system cleans each document by removing extra empty lines and spaces, then breaks it down into words.

Each chunk is exactly 350 words long.

Every new chunk overlaps with the previous one by 50 words. This means each chunk begins 50 words before the last one ends.

The syystem keeps doing this until it covers the whole document.

This method helps for a few reasons:

Works with any file type: Since the files are a mix of text, PDFs, and web pages, counting words means we do not have to rely on headings or paragraphs. Those can easily break or disappear when you extract text.

Preedictable sizes: Keeping the chunks the same size makes searching the database reliable. A chunk will never be too big, which ruins the search match, or too small, which cuts off useful info.

No lost context: If you do not overlap the chunks, a rule might end up in one chunk and its explnation in another. The 50 word overlap acts as a safety buffer so information at the edges does not get separated.

When you ask a question, the system finds the top 4 chunks using cosine similarity in ChromaDB. There is a maximum distance threshold set to 1.0 as a gurdrail. If the best mat ch in the database is still too different from your question, the system stops. It skips the LLM completely and just tells you "I don't know." This stops the AI from making things up and saves API costs.

Limitations and Future Improvements
Missing details for other hostels: The assistant does not have specific rules for every single hostel at IITB. Some files only talk about Hostel 16 or Hostel 10, so answers for other hostels might be too generic.

No study or course info: Since this only covers hostel and campus life, the assistant cannot answer anything about academics, registering for courses, grading, or exams. I chose to leave this out on purpose to keep the project focused.



If I had more time, I would add files for all 17 hostels, add a section for acedemic info, and give the AI a memory so students can have a normal back-and-forth conversation.

No follow-up questions: The assistant only answers one question at a time. It does not remember the conversation, so you cannot ask follow-up questions that rely on what you just talked about.

Manual updates only: The files are just text documents inside a folder. They do not update automatically from the website. The assistant only knows what is in the folder from the last time the index was built.
