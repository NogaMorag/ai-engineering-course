# Chapter 25 optional box: the same job in a container. Build once, run anywhere with the key as an env var.
#   docker build -t morning-brief .
#   docker run --rm -e GEMINI_API_KEY -v "$PWD/out:/app/out" morning-brief
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PYTHONUTF8=1
CMD ["uv", "run", "--no-sync", "python", "-m", "ch25.daily_job", "--out", "out", "--items", "5"]
