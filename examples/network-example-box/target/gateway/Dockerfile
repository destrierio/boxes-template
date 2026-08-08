FROM python:3.12-slim

RUN useradd --create-home --shell /usr/sbin/nologin web

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000
USER web
CMD ["python", "app.py"]
