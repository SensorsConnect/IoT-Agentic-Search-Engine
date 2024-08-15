FROM mcr.microsoft.com/devcontainers/universal:2-linux
# Install the xz-utils package
ENV TZ=America/Toronto

RUN apt-get update && \
apt-get install -y xz-utils 

RUN conda create -n IoT-engine python=3.11.5 -y