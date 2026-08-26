FROM python:3.12-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install \
    --no-cache-dir -r requirements.txt


COPY . .

# Never run the API/worker/MCP processes as root in deployed images.
RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/storage \
    && chown -R app:app /app
USER app

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)" || exit 1


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
