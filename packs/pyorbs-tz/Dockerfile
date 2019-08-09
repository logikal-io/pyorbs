FROM wbrp/pyorbs:ubuntu-16.04

RUN apt-get update && apt-get install -y tzdata \
  && rm -rf /var/lib/apt/lists/*

RUN ln -snf /usr/share/zoneinfo/Europe/Zurich /etc/localtime \
  && dpkg-reconfigure -f noninteractive tzdata

CMD ["/bin/bash"]
