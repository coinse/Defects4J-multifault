FROM nimmis/ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive

# set default java environment variable
ENV JAVA_VERSION_MAJOR=8 \
    JAVA_VERSION_MINOR=111 \
    JAVA_HOME=/usr/lib/jvm/default-jvm \
    PATH=${PATH}:/usr/lib/jvm/default-jvm/bin/

RUN add-apt-repository ppa:openjdk-r/ppa -y && \
    # update data from repositories
    apt-get update && \
    # upgrade OS
    apt-get -y dist-upgrade && \
    # Make info file about this build
    printf "Build of nimmis/java:openjdk-8-jdk, date: %s\n"  `date -u +"%Y-%m-%dT%H:%M:%SZ"` > /etc/BUILDS/java && \
    # install application
    apt-get install -y --no-install-recommends openjdk-8-jdk && \
    # fix default setting
    ln -s java-8-openjdk-amd64  /usr/lib/jvm/default-jvm && \
    # remove apt cache from image
    apt-get clean all

# Check Java version
RUN java -version && \
    javac -version

# Install linux packages
RUN apt-get update
RUN apt-get -qq -y install git curl build-essential subversion perl wget unzip vim bc

RUN cd /usr/local/ && mkdir apache-maven/ && \
      cd apache-maven/ && \
      wget http://mirror.navercorp.com/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.tar.gz && \
      tar -zxvf apache-maven-3.6.3-bin.tar.gz

# Setup Apache Maven
ENV M2_HOME="/usr/local/apache-maven/apache-maven-3.6.3"
ENV M2="$M2_HOME/bin"
ENV MAVEN_OPTS="-Xms256m -Xmx512m"
ENV PATH="$M2:$PATH"

# Check Maven version
RUN mvn -version

# Install Python
RUN add-apt-repository -y ppa:fkrull/deadsnakes
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3.6 python3.6-dev python3-pip python3-setuptools python3-wheel gcc
RUN python3.6 -m pip install pip --upgrade

WORKDIR /root

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