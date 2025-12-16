#######################################################################
#  ЭТАП 1: BUILDER
#######################################################################
FROM nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
ENV CONDA_ACCEPT_LICENSE=yes
ENV DLIB_USE_CUDA=1

RUN apt-get update && \
    apt-get install -y \
        cmake \
        build-essential \
        libboost-all-dev \
        libopenblas-dev \
        liblapack-dev \
        wget \
        python3.10 \
        python3.10-dev \
        python3.10-distutils \
        python3.10-venv \
        python3-pip \
        libopenblas0 \
        liblapack3 \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py310_24.7.1-0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:$PATH"

RUN conda config --set channel_priority strict
RUN conda install mamba -n base -c conda-forge -y
RUN mamba install python=3.10 -y

RUN python -m pip install --upgrade pip

WORKDIR /app

#  PyTorch
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt

# dlib
RUN rm -f /usr/local/bin/cmake
RUN ln -s /usr/bin/cmake /usr/local/bin/cmake
RUN python -m pip install dlib==19.24.4

# clip
RUN python -m pip install git+https://github.com/openai/CLIP.git

RUN python -m pip cache purge

#######################################################################
#  ЭТАП 2: RUNTIME
#######################################################################
FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_ACCEPT_LICENSE=yes
ENV DLIB_USE_CUDA=1

RUN apt-get update && \
    apt-get install -y \
        python3.10 \
        python3.10-distutils \
        python3-pip \
        libopenblas0 \
        liblapack3 \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /opt/conda /opt/conda
COPY --from=builder /app /app

ENV PATH="/opt/conda/bin:$PATH"
RUN ln -sf /opt/conda/bin/python /usr/bin/python

# Модель spaCy (можно заменить на md или lg)
RUN python -m spacy download ru_core_news_md

ENV PYTHON_CMD="python"
CMD ["python", "shorts.py", "--help"]


#######################################################################
#  ЭТАП 3: настраиваем ipynb и git
#######################################################################
FROM runtime AS jupyter

# устанавливаем git
USER root
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# создать юзера с теми же UID, что и на локальной машине
# создаём пользователя с UID/GID хоста
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER=devuser

RUN getent group devuser || groupadd -g ${GROUP_ID} devuser && \
    id -u devuser || useradd -m -u ${USER_ID} -g devuser devuser

# даём права на запись
RUN mkdir -p /app/main_repo && chown -R devuser:devuser /app/main_repo

RUN python -m pip install --upgrade pip && \
    python -m pip install jupyter ipykernel

# установка ядра для всех пользователей
RUN python -m ipykernel install --user --name=kion-python --display-name "Python 3.10 (kion)"

RUN git config --global user.name "msalena_docker_kion" && \
    git config --global user.email "lina.stof@mail.ru"
