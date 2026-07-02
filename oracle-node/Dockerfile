# ============================================================
# Stage 1: builder — compile the Rust binary
# ============================================================
FROM rust:1.78-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        libssl-dev \
        protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Copy manifest files first to leverage Docker layer caching for dependencies
COPY oracle-node/Cargo.toml oracle-node/Cargo.lock ./
COPY oracle-node/build.rs ./

# Build a dummy main to cache dependencies before copying real source
RUN mkdir -p src && echo 'fn main() {}' > src/main.rs
RUN cargo build --release || true

# Copy real source and proto definitions, then rebuild
COPY oracle-node/src ./src
COPY protos ../protos

RUN touch src/main.rs && cargo build --release

# ============================================================
# Stage 2: runtime — minimal Debian image
# ============================================================
FROM debian:bookworm-slim AS runtime

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid Oracle Node"
LABEL org.opencontainers.image.description="Rust oracle service bridging on-chain data to the backend"

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        libssl3 \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -u 1003 -s /bin/false oracle

COPY --from=builder /app/target/release/bimagrid-oracle /usr/local/bin/bimagrid-oracle
RUN chmod 500 /usr/local/bin/bimagrid-oracle

USER oracle

ENV RUST_LOG=info

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

CMD ["/usr/local/bin/bimagrid-oracle"]
