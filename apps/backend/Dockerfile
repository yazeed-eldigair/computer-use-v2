
# docker build -t api-computer-use-v2 .
# docker run -d -p 8000:8000 -p 5900:5900 -p 6080:6080 api-computer-use-v2

FROM docker.io/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_PRIORITY=high

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install \
    # UI Requirements
    xvfb \
    xterm \
    xdotool \
    scrot \
    imagemagick \
    sudo \
    mutter \
    x11vnc \
    # Python/pyenv reqs
    build-essential \
    libssl-dev  \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    git \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    curl \
    libffi-dev \
    liblzma-dev \
    # Network tools
    net-tools \
    netcat \
    # PPA req
    software-properties-common && \
    # Userland apps
    sudo add-apt-repository ppa:mozillateam/ppa && \
    sudo apt-get install -y --no-install-recommends \
    libreoffice \
    firefox-esr \
    tint2 \
    x11-apps \
    xpdf \
    gedit \
    xpaint \
    galculator \
    pcmanfm \
    unzip && \
    apt-get clean

# Install noVNC
RUN git clone --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# Setup user
ENV USERNAME=computer_use_v2
ENV HOME=/home/$USERNAME
RUN useradd -m -s /bin/bash -d $HOME $USERNAME
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER computer_use_v2
WORKDIR $HOME

# Setup python
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && \
    cd ~/.pyenv && src/configure && make -C src && cd .. && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc && \
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"
ENV PYENV_VERSION_MAJOR=3
ENV PYENV_VERSION_MINOR=11
ENV PYENV_VERSION_PATCH=6
ENV PYENV_VERSION=$PYENV_VERSION_MAJOR.$PYENV_VERSION_MINOR.$PYENV_VERSION_PATCH
RUN eval "$(pyenv init -)" && \
    pyenv install $PYENV_VERSION && \
    pyenv global $PYENV_VERSION && \
    pyenv rehash

ENV PATH="$HOME/.pyenv/shims:$HOME/.pyenv/bin:$HOME/.local/bin:$PATH"

RUN python -m pip install --upgrade pip==23.1.2 setuptools==58.0.4 wheel==0.40.0 && \
    python -m pip config set global.disable-pip-version-check true

# Only reinstall if requirements.txt changes
COPY --chown=$USERNAME:$USERNAME requirements.txt $HOME/requirements.txt
RUN python -m pip install -r $HOME/requirements.txt

# Setup desktop env & app
COPY --chown=$USERNAME:$USERNAME . $HOME

# Make all shell scripts in the scripts directory executable
RUN find $HOME/scripts -name "*.sh" -exec chmod +x {} \;

# Create .env file from example if it doesn't exist
RUN if [ ! -f .env ]; then cp .env.example .env; fi

ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=False
ENV ANTHROPIC_API_KEY=
ENV DATABASE_URL=computer_use_v2.db
ENV ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENV MAX_UPLOAD_SIZE=10485760
ENV UPLOAD_DIR=uploads

# Set display
ENV DISPLAY_NUM=1
ENV DISPLAY=:${DISPLAY_NUM}

# VNC port
EXPOSE 5900
# FastAPI port
EXPOSE 8000
# NoVNC port
EXPOSE 6080

CMD ["./scripts/entrypoint.sh"]
