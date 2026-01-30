FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    zsh \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install oh-my-zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Set zsh as default shell
SHELL ["/bin/zsh", "-c"]
ENV SHELL=/bin/zsh

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Create workspace directory
WORKDIR /workspace

# Configure git safe directory
RUN git config --global --add safe.directory /workspace

# Set up oh-my-zsh theme and plugins
RUN sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' /root/.zshrc && \
    echo 'plugins=(git python docker docker-compose)' >> /root/.zshrc

CMD ["/bin/zsh"]
