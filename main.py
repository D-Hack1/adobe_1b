import os
import json
import sys
import datetime
from utils.extractor import extract_outline

INPUT_DIR = "input"
OUTPUT_DIR = "output"
INPUT_JSON = os.path.join(INPUT_DIR, "input_1b.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "challenge1b_output.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Helper: Simple relevance score (string overlap) ---
def relevance_score(section_title, section_text, persona, job):
    focus = (persona + " " + job).lower()
    score = 0
    for word in section_title.lower().split():
        if word in focus:
            score += 2
    for word in section_text.lower().split():
        if word in focus:
            score += 1
    return score

# --- Read input_1b.json ---
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    input_data = json.load(f)

documents = input_data["documents"]
persona = input_data["persona"]["role"] if isinstance(input_data["persona"], dict) else input_data["persona"]
job = input_data["job_to_be_done"]["task"] if isinstance(input_data["job_to_be_done"], dict) else input_data["job_to_be_done"]

input_doc_filenames = [doc["filename"] for doc in documents]

# --- Main processing ---
results = []
subsections = []

for doc in documents:
    doc_filename = doc["filename"]
    pdf_path = os.path.join(INPUT_DIR, doc_filename)
    outline = extract_outline(pdf_path)
    # Only consider H1 and H2 headings
    filtered_sections = [s for s in outline.get("outline", []) if s.get("level") in ("H1", "H2")]
    # For each heading, try to extract the first paragraph after the heading (if available)
    # For now, use the heading text as refined text (improvement: extract from PDF if needed)
    for section in filtered_sections:
        section_title = section["text"]
        page = section["page"]
        refined_text = section_title  # Placeholder: ideally, extract the first paragraph after heading
        score = relevance_score(section_title, refined_text, persona, job)
        results.append({
            "document": doc_filename,
            "section_title": section_title,
            "importance_rank": score,
            "page_number": page
        })
        subsections.append({
            "document": doc_filename,
            "refined_text": refined_text,
            "page_number": page
        })

# --- Sort by importance_rank descending and take top 5 ---
results = sorted(results, key=lambda x: -x["importance_rank"])[:5]
subsections = subsections[:5]

# --- Add importance_rank as rank order (1 = most important) ---
for i, r in enumerate(results):
    r["importance_rank"] = i + 1

# --- Output JSON ---
output = {
    "metadata": {
        "input_documents": input_doc_filenames,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.datetime.now().isoformat()
    },
    "extracted_sections": results,
    "subsection_analysis": subsections
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Challenge 1B output written to {OUTPUT_FILE}")
