FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py app.py slide_image.py ./
COPY static/ ./static/

# /photos は Render の Persistent Disk または Docker volume にマウントされる
RUN mkdir -p /photos
VOLUME ["/photos"]

# Render は PORT 環境変数でポートを渡す（デフォルト 10000）
EXPOSE ${PORT:-10000}

CMD ["python", "app.py"]
