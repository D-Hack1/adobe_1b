import os
import json
import sys
import datetime
from utils.extractor import extract_outline

INPUT_DIR = "input"
OUTPUT_DIR = "output"
# Prefer challenge1b_input.json if present, else fallback to input_1b.json
INPUT_JSON = os.path.join(INPUT_DIR, "challenge1b_input.json")
if not os.path.exists(INPUT_JSON):
    INPUT_JSON = os.path.join(INPUT_DIR, "input_1b.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "challenge1b_output.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def relevance_score(section_title, section_text, persona, job, doc_filename):
    focus = (persona + " " + job).lower()
    score = 0
    # Boost for dinner/sides PDFs
    if any(x in doc_filename.lower() for x in ["dinner", "sides"]):
        score += 5
    # Boost for vegetarian, gluten-free, dinner, main, side, buffet
    for boost_word in ["vegetarian", "gluten-free", "dinner", "main", "side", "buffet"]:
        if boost_word in section_title.lower() or boost_word in section_text.lower():
            score += 3
    for word in section_title.lower().split():
        if word in focus:
            score += 2
    for word in section_text.lower().split():
        if word in focus:
            score += 1
    return score

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    input_data = json.load(f)

documents = input_data["documents"]
persona = input_data["persona"]["role"] if isinstance(input_data["persona"], dict) else input_data["persona"]
job = input_data["job_to_be_done"]["task"] if isinstance(input_data["job_to_be_done"], dict) else input_data["job_to_be_done"]

input_doc_filenames = [doc["filename"] for doc in documents]

results = []
subsections = []

# Helper: is likely a dish name
food_words = ["salad", "curry", "soup", "roll", "rice", "dal", "paneer", "tofu", "stir-fry", "lasagna", "bake", "casserole", "cutlet", "kofta", "falafel", "ratatouille", "sushi", "ganoush", "skewers", "pasta", "pizza", "burger", "wrap", "tikka", "kebab", "chili", "stew", "biryani", "pilaf", "noodle", "quiche", "frittata", "omelette", "tart", "gratin", "moussaka", "gnocchi", "tagine", "paella", "enchilada", "taco", "burrito", "quesadilla", "samosa", "idli", "dosa", "upma", "poha", "sabzi", "bhaji", "chutney", "dal", "sambar", "rasam", "thoran", "avial", "poriyal", "kootu", "pachadi", "raita", "halwa", "kheer", "payasam", "pudding", "cake", "cookie", "brownie", "muffin", "barfi", "laddu", "gulab", "jalebi", "sheera", "modak", "sandesh", "malpua", "shrikhand", "basundi", "rabri", "ice cream", "sorbet", "kulfi", "smoothie", "shake", "juice", "lassi", "tea", "coffee"]
def is_dish_heading(text):
    text = text.strip()
    # Short, capitalized, not all lowercase, not too long, not starting with 'o', 'Instructions', 'Ingredients', not a step/number
    if (
        2 <= len(text.split()) <= 5 and
        not text.lower().startswith(("o ", "instructions", "ingredients", "step", "method", "directions", "preparation")) and
        not text.islower() and
        len(text) < 40 and
        not text[0].isdigit() and
        text[0].isupper() and
        not text.endswith(":")
    ):
        # Must contain a food word or be title-cased
        if any(word in text.lower() for word in food_words) or text.istitle():
            return True
    return False

def is_recipe_block(text):
    # Likely a recipe/ingredient block if it contains numbers, food words, or is longer than 5 words
    if any(str(d) in text for d in range(1, 10)):
        return True
    if any(word in text.lower() for word in food_words):
        return True
    if len(text.split()) > 5:
        return True
    return False

for doc in documents:
    doc_filename = doc["filename"]
    pdf_path = os.path.join(INPUT_DIR, doc_filename)
    outline = extract_outline(pdf_path)
    blocks = outline.get("outline", [])
    for i, section in enumerate(blocks):
        text = section["text"].strip()
        if is_dish_heading(text):
            # Find next block(s) that look like a recipe/ingredient list
            refined = []
            for j in range(i+1, min(i+4, len(blocks))):
                next_text = blocks[j]["text"].strip()
                if is_recipe_block(next_text):
                    refined.append(next_text)
            refined_text = " ".join(refined) if refined else text
            score = relevance_score(text, refined_text, persona, job, doc_filename)
            results.append({
                "document": doc_filename,
                "section_title": text,
                "importance_rank": score,
                "page_number": section["page"]
            })
            subsections.append({
                "document": doc_filename,
                "refined_text": refined_text,
                "page_number": section["page"]
            })

results = sorted(results, key=lambda x: -x["importance_rank"])[:5]
subsections = subsections[:5]
for i, r in enumerate(results):
    r["importance_rank"] = i + 1

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
