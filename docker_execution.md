# Dockerfile
```dockerfile
FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

# Execution Instructions

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