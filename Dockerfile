FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY src/ ./src/
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "src/monitor.py"]
