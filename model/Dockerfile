FROM python:3.8.13 as base

# Install some packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.8-dev \
    python3-pip \
    ffmpeg \
    libsm6 \
    libxext6 \
    vim \
    wget \
    curl \
    git \
    libgl1-mesa-glx

ADD requirements.txt .
RUN pip3 install -r requirements.txt

# ENV PYTHONPATH=$PYTHONPATH:src/
# ENV PYTHONPATH=$PYTHONPATH:src/utils_data

ENV PYTHONPATH=$PYTHONPATH:/src

ADD ./ /src/

WORKDIR /src

# FROM base as test
# RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["python3", "/src/ml_service.py"]

