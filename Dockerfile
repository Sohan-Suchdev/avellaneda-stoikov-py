FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

WORKDIR /app

FROM base AS builder

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM base AS runtime

COPY --from=builder /install /usr/local
COPY src ./src
COPY main.py .

ENTRYPOINT ["python", "main.py", "--batch", "--plot"]
