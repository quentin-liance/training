# ========================================
# Development Container Dockerfile
# ========================================
# Base image: Python 3.12 slim variant for smaller size
FROM python:3.12-slim

# Install essential system dependencies for development
# - git: Version control
# - curl: Command-line tool for transferring data
# - zsh: Enhanced shell
# - wget: Network downloader
# - build-essential: Compilers and build tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    zsh \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install oh-my-zsh for enhanced shell experience
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Configure zsh as the default shell for the container
SHELL ["/bin/zsh", "-c"]
ENV SHELL=/bin/zsh

# Install UV - fast Python package installer and resolver
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Starship - customizable prompt for any shell
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
ENV PATH="/usr/local/bin:${PATH}"

# Set the working directory for the container
WORKDIR /workspace

# Configure git with safe directory and user credentials
RUN git config --global --add safe.directory /workspace && \
    git config --global user.name "Quentin Liance" && \
    git config --global user.email "quentin.liance@gmail.com"

# Enable Starship prompt in zsh configuration
RUN echo 'eval "$(starship init zsh)"' >> /root/.zshrc

# Default command: start zsh shell
CMD ["/bin/zsh"]
