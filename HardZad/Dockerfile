# ==================== STAGE 1: RUST BUILDER ====================
FROM rust:1.76-slim-bookworm AS rust-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    python3 \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN cargo new --lib rust_extension
WORKDIR /build/rust_extension

COPY Cargo.toml ./
RUN echo "pub fn dummy() {}" > src/lib.rs
RUN cargo build --release || (cat target/release/build/my_rust_core-*/output 2>/dev/null || echo "No detailed build log found" && false)

RUN rm -rf src
COPY src ./src
RUN cargo build --release || (cat target/release/build/my_rust_core-*/output 2>/dev/null || echo "No detailed build log found" && false)

# ==================== STAGE 2: PYTHON WHEEL BUILDER ====================
FROM python:3.12-slim AS wheel-builder

# Устанавливаем системные зависимости, maturin И RUST
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir maturin==1.5.1

# Устанавливаем Rust (нужен для maturin build)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app

# Копируем манифесты Python
COPY pyproject.toml ./

# Создаем структуру для Python пакета
RUN mkdir -p src && touch src/__init__.py

# Копируем скомпилированную Rust библиотеку из первого этапа
COPY --from=rust-builder /build/rust_extension/target/release/libmy_rust_core.so ./target/release/
COPY --from=rust-builder /build/rust_extension/target/release/libmy_rust_core.a ./target/release/
COPY --from=rust-builder /build/rust_extension/Cargo.toml ./

# Копируем исходники Rust
COPY src/lib.rs ./src/

# Проверяем наличие cargo
RUN cargo --version && rustc --version

# Сборка wheel В dist/
RUN echo "=== Запуск maturin build ===" && \
    maturin build --release --out dist --interpreter python3.12 -v 2>&1 | tee build.log || \
    (echo "=== ОШИБКА СБОРКИ ===" && \
     tail -50 build.log && \
     exit 1)

# Проверяем dist
RUN echo "=== Проверка dist ===" && \
    ls -la dist/ && \
    echo "=== Wheel файлы ===" && \
    ls -la dist/*.whl

# ==================== STAGE 3: FINAL RUNTIME ====================
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# ✅ Копируем wheel ИЗ dist/ (а не из target/wheels)
COPY --from=wheel-builder /app/dist/*.whl /tmp/

COPY requirements.txt .
RUN pip install --no-cache-dir /tmp/*.whl && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/*.whl requirements.txt

COPY src/main.py .

USER appuser

EXPOSE 8080
CMD ["python", "main.py"]