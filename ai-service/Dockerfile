FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV CEREBRAS_MODEL=qwen-3-235b-a22b-instruct-2507
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
