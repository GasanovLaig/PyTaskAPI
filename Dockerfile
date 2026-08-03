FROM python:3.13-alpine AS builder

WORKDIR /build

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13-alpine AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

WORKDIR /code

COPY --from=builder /root/.local /root/.local

COPY . /code/

EXPOSE 8000
