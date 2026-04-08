FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD sh -c "sleep 15 && python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py seed_data && python manage.py runserver 0.0.0.0:8000"
