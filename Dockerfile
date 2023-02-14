FROM mcr.microsoft.com/vscode/devcontainers/anaconda:0-3
LABEL org.opencontainers.image.source=https://github.com/ziyixi/EARA2023-Figures

ENV POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

RUN conda config --prepend channels conda-forge \
    && conda install -y python=3.9 gmt \
    && curl -sSL https://install.python-poetry.org | python - \
    && echo 'export PATH="/opt/poetry/bin:$PATH"' >> /root/.bashrc

COPY pyproject.toml /
RUN poetry config virtualenvs.create false \
    && poetry install