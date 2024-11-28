FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

ENV PYTHON_VERSION 3.9.1
ENV JAVA_8_VERSION 8.0.302-open
ENV JAVA_11_VERSION 11.0.12-open

# Set of all dependencies needed for pyenv to work on Ubuntu
RUN apt-get update \
    && apt-get install -y --no-install-recommends make build-essential tar \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget \
    ca-certificates curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev liblzma-dev mecab-ipadic-utf8 git vim bc unzip \
    subversion perl zip locales

# Locale & Language Setting
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


WORKDIR /root
ENV HOME /root

# Set-up necessary ENV vars for pyenv
ENV PYENV_ROOT /root/.pyenv
ENV PATH ${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

# Install pyenv (Python version control system)
RUN set -ex \
    && curl https://pyenv.run | bash \
    && pyenv update \
    && pyenv install ${PYTHON_VERSION} \
    && pyenv global ${PYTHON_VERSION} \
    && pyenv rehash

RUN python -m pip install setuptools numpy requests pandas scipy urllib3 python-dateutil

# Install sdkman (Java version control system)
RUN curl -s "https://get.sdkman.io" | bash

# Install Java 8
RUN bash -c "source $HOME/.sdkman/bin/sdkman-init.sh && sdk install java ${JAVA_8_VERSION} && sdk default java ${JAVA_8_VERSION}"
ENV JAVA_HOME "$HOME/.sdkman/candidates/java/current"

# Setup Defects4J
COPY resources/install_defects4j.sh install_defects4j.sh
RUN chmod +x install_defects4j.sh
RUN ./install_defects4j.sh

ENV TZ="America/Los_Angeles"
ENV D4J_HOME="/defects4j"
ENV PATH="${PATH}:/defects4j/framework/bin"
ENV JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8"
ENV TMP_DIR="/tmp"

# Setup Apache Maven
RUN cd /usr/local/ && mkdir apache-maven/ && \
      cd apache-maven/ && \
      wget https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.6.3/apache-maven-3.6.3-bin.tar.gz && \
      tar -zxvf apache-maven-3.6.3-bin.tar.gz

ENV M3_HOME="/usr/local/apache-maven/apache-maven-3.6.3"
ENV M3="$M3_HOME/bin"
ENV MAVEN_OPTS="-Xms256m -Xmx512m"
ENV PATH="$M3:$PATH"

# Install Defects4j
COPY resources/install_defects4j.sh install_defects4j.sh
RUN chmod +x install_defects4j.sh

ENV TZ="America/Los_Angeles"
ENV D4J_HOME="/root/defects4j"
ENV PATH="${PATH}:/root/defects4j/framework/bin"
RUN ./install_defects4j.sh

COPY resources/vimrc .vimrc
ENV JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8"
ENV TMP_DIR="/tmp"
ENV COVERAGE_DIR="/root/fault_data"
RUN mkdir /root/fault_data

COPY resources/java_analyzer /root/java_analyzer
RUN cd /root/java_analyzer; mvn clean install
ENV RANGE_ANALYZER="/root/java_analyzer/target/java-analyzer-1.0-SNAPSHOT-shaded.jar"

ENV PYTHONIOENCODING=utf-8
