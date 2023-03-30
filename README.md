# 🦦 Argyle - Scanning Task

## Quick start

### Run the application with [poetry](#place1)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add `$HOME/.local/bin` to your `$PATH`.

```bash
poetry --version # check if installed
poetry self update # update

# configure poetry to create virtual environments inside the project\'s root directory
poetry config virtualenvs.in-project true

# specify the python version for the local directory using pyenv
pyenv local 3.10.9

# install libraries
poetry install

##
# activate the virtual environment and run a python file
poetry shell 
python run src/argyle_task/main.py
## equals to
# run your project without opening a shell
poetry run python src/argyle_task/main.py
##

# run your test
poetry run pytest

## deactivate the virtual environment
# deactivate # command for later use
```

### Run the application with Docker

- Install Docker on your local machine. You can download Docker from the official website: [Docker](https://docs.docker.com/desktop/install/mac-install/)

- Build your Docker image by running the following command in your Docker folder:

  ```bash
  docker build . -t <image_name>
  ```

- Once the Docker image is built, you can run it locally using the following command:

  ```bash
  docker run -it --name=<container_name> -v <database_local_dir_abs_path>:<database_docker_abs_path> -v /etc/ssl/cert.pem:<cert_file_docker_abs_path>:ro -v <user_credentials_local_file_abs_path>:<user_credentials_docker_file_abs_path>:ro <image_name> poetry run python src/argyle_task/main.py --db <database_docker_abs_path>/db.sqlite --cert <cert_file_docker_abs_path> --users <user_credentials_docker_file_abs_path>
  ```

  - `-v <database_local_dir_abs_path>:<database_docker_abs_path>`
    - Crawled user profiles are kept in a [sqlite3](#place2) database.
  - `-v <user_credentials_local_file_abs_path>:<user_credentials_docker_file_abs_path>:ro`
    - OpenSSL-based applications use the system trust store located in the `/etc/ssl/certs` directory. This directory contains trusted root CA certificates, which are used to verify the authenticity of SSL/TLS connections to remote servers. Providing the SSL certificate is a must. `/etc/ssl/cert.pem` is located locally. (ro := read-only)
  - `-v <user_credentials_local_file_abs_path>:<user_credentials_docker_file_abs_path>:ro`
    - User credentials are kept in a text file. (ro := read-only)
  - `-d`, `--db` arg
    - Database file path (local)
  - `-c`, `--cert` arg
    - SSL certificate file path (local)
  - `-u`, `--users` arg
    - User credentials file path (local)

---

## How does the application work?

- It takes an input text file that contains a list of user credentials. Each line is a json string consisting of username, password, and answer(secret key for two factor-auth). These fields correspond to `https://www.upwork.com` credentials.
- The application crawls each user's profile concurrently and saves crawled profile information to an sqlite database. For a given user, each crawl operation persists a new record.

---

## Notes

- There is a non-critical warning in testing related to the `tornado` version.
- The project's settings are MacOS-compatible.

---

## Potential future work

- We can put user credentials into a database table to fulfil the requirements of the increasing number of users.
- We can create indices on the database table to enable fast querying of crawled profiles. For instance, we can build an index for querying latest crawled profile of a given user.
- Tests should be extended. I implemented some of the test cases due to time limitations.
- Based on update frequency of user profiles, the crawler can prioritize users and may skip crawling some users on each run.

---

## TL;DR; Library glossary

### asyncio

- [asyncio](https://docs.python.org/3/library/asyncio.html) is a library to write concurrent code using the async/await syntax.
- [https://fatmakahveci.com/python-note/concurrency/](https://fatmakahveci.com/python-note/concurrency/)

### celery

- [celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) is a simple, flexible, and reliable distributed system to process vast amounts of messages, while providing operations with the tools required to maintain such a system.

### httpx

- [httpx](https://www.python-httpx.org/) is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.

### json

- [json](https://docs.python.org/3/library/json.html) is a lightweight data interchange format inspired by JavaScript object literal syntax.

### logging

- [logging](https://docs.python.org/3/library/logging.html?highlight=logging#module-logging) defines functions and classes which implement a flexible event logging system for applications and libraries.

### mypy

- [mypy](https://mypy.readthedocs.io/en/stable/) is a static type checker for Python. Type checkers help ensure that you’re using variables and functions in your code correctly.
- Run: `poetry run mypy <file_name>.py`

### pdfMiner

- [PdfMiner](https://pypi.org/project/pdfminer/) is a text extraction tool for PDF documents.

### playwright

- [playwright](https://playwright.dev/python/docs/intro) was created specifically to accommodate the needs of end-to-end testing.

### <span id="place1">poetry</span>

- [poetry](https://python-poetry.org/) is a tool for **dependency management** and **packaging** in Python.
- It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.
- The most important file is `pyproject.toml`. It resolves the dependencies of your defined requirements, and creates the `poetry.lock` file.

### poppler

- [poppler](https://pypi.org/project/python-poppler/) allows you to read, render, or modify PDF documents.
- It reads and modifies document metadata.
- It lists and reads embedded documents.
- It lists the fonts used by the document.
- It searches or extracts text on a given page of the document.
- It renders a page into a raw image.
- It gets info about transition effects between the pages.
- It reads the table of contents of the document.

### pydantic

- [pydantic](https://docs.pydantic.dev/) is the most widely used data validation library for Python.

### pydash

- [pydash](https://pydash.readthedocs.io/en/latest/) is the kitchen sink of Python utility libraries for functionally doing "stuff".

### pylint

- [pylint](https://pypi.org/project/pylint/) is a static code analyser.
  - A code linter is a software tool designed to examine your code and provide feedback on potential issues. It detects errors and offers solutions to help you ensure that your code meets standard quality guidelines. You can execute it at any time to verify code consistency.
- `pylint` handles both the following:
  - **Logical lint** detects errors and identifies potentially dangerous patterns.
  - **Statistical lint** examines the formatting to find out the issues with its style and structure.

### pytest

- [pytest](https://docs.pytest.org/en/7.2.x/) makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

### respx

- [RESPX](https://github.com/lundberg/respx) is a simple, yet powerful, utility for mocking out the HTTPX, and HTTP Core, libraries.

### <span id="place2">sqlite3</span>

- [SQLite](https://docs.python.org/3.8/library/sqlite3.html) is a C library that provides a lightweight disk-based database that doesn't require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language.
