# 1. Match your local Conda environment's Python version
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the actual code, documentation, and the trained model into the container
COPY src/ /app/src/
COPY models/ /app/models/
COPY docs/ /app/docs/

# 5. Expose the port the app runs on
EXPOSE 8000

# 6. The command to start the FastAPI server
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]