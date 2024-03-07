# Install system dependencies for pyodbc
FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:3.9.10-slim-buster

# ARG AY_AZURE_SQL_PASSWORD
# ARG AY_AZURE_SQL_USERNAME

# ENV AY_AZURE_SQL_PASSWORD=$AY_AZURE_SQL_PASSWORD
# ENV AY_AZURE_SQL_USERNAME=$AY_AZURE_SQL_USERNAME

# Install system dependencies for pyodbc
# Install Microsoft ODBC Driver for SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 \
    curl \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /video
COPY . /video
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000

# Define environment variable
ENV FLASK_APP api/app.py
CMD ["flask", "run", "--host=0.0.0.0"]
