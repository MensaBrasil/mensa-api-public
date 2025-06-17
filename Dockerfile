FROM python:3.12

WORKDIR /app

COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH"
ENV PATH="/root/.local/bin:$PATH"


RUN poetry install --no-root


# Add Poetry to PATH for subsequent commands


CMD ["poetry", "run", "uvicorn", "people_api:app", "--host", "0.0.0.0", "--port", "5000"]
