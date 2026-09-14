FROM python:3.12-alpine AS builder
WORKDIR /build
RUN apk add --no-cache gcc musl-dev libffi-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN adduser -D -u 10001 appuser
USER appuser
WORKDIR /app
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app:app"]
