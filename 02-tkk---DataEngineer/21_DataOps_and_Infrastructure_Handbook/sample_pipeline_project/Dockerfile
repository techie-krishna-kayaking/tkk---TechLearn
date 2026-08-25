# ---- Stage 1: build/install dependencies (cached unless requirements change) ----
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: lean runtime image ----
FROM python:3.11-slim
WORKDIR /app
# copy only the installed packages from the builder (small final image)
COPY --from=builder /install /usr/local
COPY pipeline/ ./pipeline/
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# run as a non-root user (security best practice)
RUN useradd --create-home --uid 1000 appuser
USER appuser
ENTRYPOINT ["python", "-m", "pipeline.transform"]
