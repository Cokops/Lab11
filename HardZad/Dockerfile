# ==================== STAGE 1:   BUILDER ====================
FROM rust:1.80-slim-bookworm AS rust-builder

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

# Устанавливаем системные зависимости и maturin
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir maturin==1.5.1

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

# Собираем wheel-файл
RUN maturin build --release --out dist --interpreter python3.12

# ==================== STAGE 3: FINAL RUNTIME ====================
FROM python:3.12-slim AS runtime

# Устанавливаем минимальные системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libc6 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Создаем непривилегированного пользователя
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Копируем wheel из второго этапа
COPY --from=wheel-builder /app/dist/*.whl ./dist/

# Копируем файл с зависимостями и устанавливаем всё сразу
COPY requirements.txt .
RUN pip install --no-cache-dir dist/*.whl && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf dist requirements.txt

# Копируем основной код приложения (самый изменяемый слой - ПОСЛЕДНИМ)
COPY src/main.py .

# Переключаемся на непривилегированного пользователя
USER appuser

EXPOSE 8080
CMD ["python", "main.py"]