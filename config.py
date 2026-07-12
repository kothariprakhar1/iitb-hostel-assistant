"""
Step 1: Scope definition for the IITB Hostel & Campus Life Assistant.

This file documents and centralizes the scope so every other script
(chunking, embedding, retrieval) stays consistent with it.
"""

PROJECT_NAME = "IITB Hostel & Campus Life Assistant"

SCOPE_TOPICS = [
    "Hostel allotment & room rules",
    "Mess menu / mess rules & fees",
    "Hostel facilities (gym, common room, laundry, etc.)",
    "Campus facilities (SAC, hospital, library, gymkhana grounds)",
    "Guest / curfew / visitor policies",
]
DATA_DIR = "data"
CHROMA_DB_DIR = "chroma_store"
COLLECTION_NAME = "iitb_hostel_campus"
CHUNK_SIZE_WORDS = 350      
CHUNK_OVERLAP_WORDS = 50  
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  
TOP_K = 4  
MAX_DISTANCE_THRESHOLD = 1.0
GEMINI_MODEL = "gemini-flash-latest"