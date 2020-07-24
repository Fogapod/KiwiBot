FROM python:3.8-slim

# enables proper stdout flushing
ENV PYTHONUNBUFFERED=yes

# pip optimizations
ENV PIP_NO_CACHE_DIR=yes
ENV PIP_DISABLE_PIP_VERSION_CHECK=yes

WORKDIR /code


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      git \
      openssh-client \
# discord voice features
      ffmpeg \
# espeak-ng runtime deps
      libsonic-dev \
      libpcaudio-dev \
# screenshot command
      chromium \
# ping command
      iputils-ping \
# gif commands
      gifsicle \
# espeak-ng for tts command
    && espeak_deps='gcc make autoconf automake libtool pkg-config' \
    && apt-get install -y --no-install-recommends $espeak_deps \
    && git clone https://github.com/espeak-ng/espeak-ng.git --depth=1 && cd espeak-ng \
    && ./autogen.sh \
    && ./configure --with-extdict-ru \
    && make \
    && make install \
    && cd .. && rm -rf espeak-ng \
# screenshot command
    && arsenic_deps='unzip wget' \
    && apt-get install -y --no-install-recommends $arsenic_deps \
    && CHROMIUM_VERSION=$(chromium --version | cut -d' ' -f2 | rev | cut -d. -f2- | rev) \
    && CHROMEDRIVER_VERSION=$(wget -qO - https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROMIUM_VERSION}) \
    && wget -qO chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver.zip \
    && chmod +x chromedriver \
    && mv chromedriver /usr/local/bin \
    && rm -f chromedriver.zip \
# cleanup
    && apt-get purge -y --auto-remove $espeak_deps $arsenic_deps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip_deps='gcc make libc6-dev' \
    && apt-get update && apt-get install -y --no-install-recommends $pip_deps \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -Ur requirements.txt \
    && apt-get purge -y --auto-remove $pip_deps

COPY . .

RUN addgroup kiwi \
    && useradd -mg kiwi kiwi \
    && chown -R kiwi:kiwi /code

USER kiwi

RUN git config --global url.ssh://git@github.com/.insteadOf https://github.com/ \
    && mkdir ~/.ssh \
    && ssh-keyscan -H github.com >> ~/.ssh/known_hosts

ENTRYPOINT ["python3.8", "main.py"]
