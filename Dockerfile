FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Many hosts set PORT; 8000 is the default.
ENV PORT=8000
EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:$PORT app:app
