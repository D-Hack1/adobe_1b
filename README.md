# Persona-Driven Document Intelligence Pipeline

## Overview
This solution acts as an intelligent document analyst, extracting and prioritizing the most relevant sections from a collection of PDFs based on a specific persona and their job-to-be-done. It is generic and robust, supporting a wide variety of document types (e.g., research papers, recipes, reports) and user personas (e.g., researcher, food contractor, travel planner).

## Methodology
1. **PDF Parsing and Outline Extraction:**
   - Uses PyMuPDF (fitz) to parse PDFs, extracting text blocks with font size, position, and page number.
   - Custom outline extractor merges word spans into lines and applies heuristics to identify section headings (H1, H2) or dish names. Unicode-aware and supports multilingual documents.
2. **Section/Dish Detection and Filtering:**
   - For general documents, only prominent headings are considered as candidate sections.
   - For recipes, heuristics detect dish names (short, capitalized, food-related lines), filtering out instructions or ingredient lists.
3. **Refined Text Extraction:**
   - For each section/dish, extracts the next relevant text block (summary, recipe, or ingredient list) using heuristics (numbers, food words, length).
4. **Relevance Scoring and Ranking:**
   - Scores each section based on overlap with persona/job keywords, scenario-specific terms, and document filename.
   - Selects the top N (usually 5) most relevant sections.
5. **Output Format and Generalization:**
   - Outputs a structured JSON with metadata, extracted sections (title, rank, page), and subsection analysis.
   - The format is generic for any persona, job, and document set.
6. **Dockerization and Execution:**
   - Fully containerized for reproducibility and ease of deployment.
   - CPU-only, no internet required, processes 3-10 PDFs in under 60 seconds.
   - Usage: Place PDFs and input JSON in `input/`, build and run Docker container, output JSON appears in `output/`.
7. **Limitations and Future Improvements:**
   - Heuristic-based section/dish detection may not handle all layouts.
   - Advanced filtering (e.g., strict dietary needs) would require ingredient-level parsing or a local language model.
   - Future work: improved paragraph extraction, advanced dietary filtering, more document types.

---

## Dockerfile
```dockerfile
FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## Execution Instructions

1. **Prepare Input:**
   - Place all PDF files and the required input JSON (e.g., `input_1b.json`) in the `input/` directory.

2. **Build the Docker Image:**
   - Open a terminal in the `adobe_1b` directory.
   - Run:
     ```
     docker build -t adobe_1b .
     ```

3. **Run the Docker Container:**
   - Execute:
     ```
     docker run --rm -v "$PWD/input:/app/input" -v "$PWD/output:/app/output" adobe_1b
     ```
   - On Windows PowerShell, you may need to use:
     ```
     docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output adobe_1b
     ```

4. **Check Output:**
   - The processed JSON output will be available in the `output/` directory. 