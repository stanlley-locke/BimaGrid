# ============================================================
# Stage 1: builder — compile the Rust binary
# ============================================================
FROM rust:slim-bookworm AS builder

WORKDIR /app

ARG APT_MIRROR=cdn-fastly.deb.debian.org
RUN sed -i "s/deb.debian.org/${APT_MIRROR}/g" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        libssl-dev \
        protobuf-compiler

# Copy manifest files first to leverage Docker layer caching for dependencies
COPY oracle-node/Cargo.toml oracle-node/Cargo.lock ./
COPY oracle-node/build.rs ./
COPY protos ../protos

# Build a dummy main to cache dependencies before copying real source
RUN mkdir -p src && echo 'fn main() {}' > src/main.rs
RUN cargo build --release || true

# Copy real source and contract artifacts, then rebuild
COPY oracle-node/src ./src
COPY contracts/artifacts ../contracts/artifacts

RUN touch src/main.rs && cargo build --release

# ============================================================
# Stage 2: runtime — minimal Debian image
# ============================================================
FROM debian:bookworm-slim AS runtime

LABEL maintainer="BimaGrid Team <dev@bimagrid.io>"
LABEL org.opencontainers.image.title="BimaGrid Oracle Node"
LABEL org.opencontainers.image.description="Rust oracle service bridging on-chain data to the backend"

ARG APT_MIRROR=cdn-fastly.deb.debian.org
RUN sed -i "s/deb.debian.org/${APT_MIRROR}/g" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null || true

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        libssl3 \
        curl

RUN useradd -r -u 1003 -s /bin/false oracle

WORKDIR /app

COPY --from=builder /app/target/release/bimagrid-oracle /usr/local/bin/bimagrid-oracle
COPY --chown=oracle:oracle oracle-node/oracle-config-1.toml .
RUN chmod 500 /usr/local/bin/bimagrid-oracle

USER oracle

ENV RUST_LOG=info

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

CMD ["/usr/local/bin/bimagrid-oracle"]
