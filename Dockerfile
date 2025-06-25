FROM python:3.12.10-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /flea

# Включаем компиляцию байт-кода для ускорения загрузки модулей
ENV UV_COMPILE_BYTECODE=1

# Используем копирование вместо линковки для монтируемых томов
ENV UV_LINK_MODE=copy

# Отключаем создание байткода (.pyc, __pycache__/)
ENV PYTHONDONTWRITEBYTECODE=1

# Отключаем буферизацию вывода
ENV PYTHONUNBUFFERED=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ENV PATH="/flea/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y \
    mime-support \
    && rm -rf /var/lib/apt/lists/*

ADD . /flea
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
