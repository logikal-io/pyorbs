ARG TAG
FROM ubuntu:${TAG}

ENV SHELL /bin/bash
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install pyorbs

CMD ["/bin/bash"]
