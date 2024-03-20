FROM ubuntu:latest
LABEL authors="aidenius"

ENTRYPOINT ["top", "-b"]