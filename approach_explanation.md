# Approach Explanation: Persona-Driven Document Intelligence Pipeline

## Overview
This solution is designed to act as an intelligent document analyst, extracting and prioritizing the most relevant sections from a collection of PDFs based on a specific persona and their job-to-be-done. The system is generic and robust, supporting a wide variety of document types (e.g., research papers, recipes, reports) and user personas (e.g., researcher, food contractor, travel planner).

## Methodology

### 1. PDF Parsing and Outline Extraction
The pipeline uses PyMuPDF (fitz) to parse each PDF and extract text blocks along with their font size, position, and page number. A custom outline extractor merges adjacent word spans into lines and then applies heuristics to identify likely section headings (e.g., H1, H2) or, in the case of recipes, dish names. This process is Unicode-aware and supports multilingual documents.

### 2. Section/Dish Detection and Filtering
For general documents, only prominent headings (H1/H2) are considered as candidate sections. For recipe/menu planning scenarios, the system uses additional heuristics to detect likely dish names: short, capitalized lines that are not instructions or ingredient lists, and that contain food-related keywords. This ensures that only meaningful sections or dishes are extracted, not every line or instruction.

### 3. Refined Text Extraction
For each detected section or dish, the pipeline attempts to extract the next block(s) of text that likely represent a summary, recipe, or ingredient list. This is done by checking for blocks that contain numbers, food words, or are longer than a threshold. The result is a concise, relevant summary for each section.

### 4. Relevance Scoring and Ranking
Each candidate section is scored for relevance based on:
- Overlap with persona/job keywords
- Presence of scenario-specific terms (e.g., "vegetarian", "gluten-free", "dinner", "side")
- Document filename (e.g., prioritizing "Dinner" or "Sides" PDFs for menu planning)
The top N (usually 5) most relevant sections are selected for output.

### 5. Output Format and Generalization
The output is a structured JSON file containing:
- Metadata (input docs, persona, job, timestamp)
- Extracted sections (document, section title, importance rank, page)
- Subsection analysis (document, refined text, page)
This format is generic and can be used for any persona, job, and document set.

### 6. Dockerization and Execution
The solution is fully containerized for reproducibility and ease of deployment. It runs on CPU only, with no internet access required, and is designed to process 3-10 PDFs in under 60 seconds. To run:
1. Place all PDFs and the input JSON in the `input/` folder.
2. Build and run the Docker container as per the provided Dockerfile and instructions.
3. The output JSON will be written to the `output/` folder.

### 7. Limitations and Future Improvements
- The system relies on heuristics for section/dish detection and may not perfectly handle all document layouts.
- Advanced semantic filtering (e.g., strict vegetarian/gluten-free detection) would require ingredient-level parsing or a small local language model.
- Future work could include improved paragraph extraction, more advanced dietary filtering, and support for additional document types. 