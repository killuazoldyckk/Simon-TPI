FROM python:3.11-slim

WORKDIR /app

# Menginstal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin kode sumber
COPY . .
EXPOSE 8000

# Perintah produksi menggunakan Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]