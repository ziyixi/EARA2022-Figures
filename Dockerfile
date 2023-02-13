FROM mcr.microsoft.com/devcontainers/miniconda:0-3
LABEL org.opencontainers.image.source=https://github.com/ziyixi/EARA2023-Figures

RUN conda config --prepend channels conda-forge \
    && conda install -y python=3.9 gmt \
    && curl -sSL https://install.python-poetry.org | python - \
    && echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc

ENV PATH="/root/.local/bin:$PATH"
RUN poetry install