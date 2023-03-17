# 🦦 Scanning Task

## Python Libraries

---

### BeautifulSoup

- [https://beautiful-soup-4.readthedocs.io/en/latest/](https://beautiful-soup-4.readthedocs.io/en/latest/)
- It is a Python library for pulling data out of `HTML` and `XML` files.
- It works with your favourite parser to provide idiomatic ways of navigating, searching, and modifying the parse tree.

---

### Asyncio

- [https://fatmakahveci.com/python-note/concurrency/](https://fatmakahveci.com/python-note/concurrency/)
- [https://docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)

---

### Celery

- [https://docs.celeryq.dev/en/stable/getting-started/introduction.html](https://docs.celeryq.dev/en/stable/getting-started/introduction.html)
- It is a simple, flexible, and reliable distributed system to process vast amounts of messages, while providing operations with the tools required to maintain such a system.

---

### Pydantic

- [https://docs.pydantic.dev/](https://docs.pydantic.dev/)
- It is the most widely used data validation library for Python.

---

### Playwright

- [https://playwright.dev/python/docs/intro](https://playwright.dev/python/docs/intro)
- It was created specifically to accommodate the needs of end-to-end testing.

---

### Httpx

- [https://www.python-httpx.org/](https://www.python-httpx.org/)
- It is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2.

---

### Pydash

- [https://pydash.readthedocs.io/en/latest/](https://pydash.readthedocs.io/en/latest/)
- It is the kitchen sink of Python utility libraries for doing “stuff” in a functional way.

---

### Mypy

- [https://mypy.readthedocs.io/en/stable/](https://mypy.readthedocs.io/en/stable/)
- It is a static type checker for Python. Type checkers help ensure that you’re using variables and functions in your code correctly.

---

### Pytest

- [https://docs.pytest.org/en/7.2.x/](https://docs.pytest.org/en/7.2.x/)
- It makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

---

### Poetry

- [https://python-poetry.org/](https://python-poetry.org/)
- Poetry is a tool for **dependency management** and **packaging** in Python.
- It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.
- The most important file is `pyproject.toml`. It resolves the dependencies of your defined requirements, and creates the `poetry.lock` file.
- **Installation (MacOS):**

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

  Add `$HOME/.local/bin` to your `$PATH`.

  ```bash
  poetry --version # check if installed
  poetry self update # update
  ```

```bash
# start a new python project
poetry new argyle-task

# configure poetry to create virtual environments inside the project's root directory
poetry config virtualenvs.in-project true

# specify the python version for the local directory using pyenv
pyenv local 3.10.9

# add libraries
poetry add beautifulsoup4 Celery httpx

# activate the virtual environment
poetry shell

## deactivate the virtual environment
# deactivate # for later use

# run your script
poetry run python <python_file>.py

# get the latest versions of the dependencies 
poetry update

# run your test
poetry run pytest
```

---

### Pyenv

- [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)
- It is a python installation manager. It allows you to install and run multiple python installations, on the same machine.

---

### Poppler

- [https://pypi.org/project/python-poppler/](https://pypi.org/project/python-poppler/)
- It allows to read, render, or modify PDF documents.
- It reads an modify document meta data.
- It lists and reads embedded documents.
- It lists the fonts used by the document.
- It searches or extracts text on a given page of the document.
- It renders a page to a raw image.
- It gets info about transitions effects between the pages.
- It reads the table of contents of the document.

---

### PdfMiner

- [https://pypi.org/project/pdfminer/](https://pypi.org/project/pdfminer/)
- It is a text extraction tool for PDF documents.

---

## Additional libraries

### `logging`

- [logging](https://docs.python.org/3/library/logging.html?highlight=logging#module-logging) defines functions and classes which implement a flexible event logging system for applications and libraries.

### `sqlite3`

- [SQLite](https://docs.python.org/3.8/library/sqlite3.html) is a C library that provides a lightweight disk-based database that doesn't require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language.

---

## ERROR CODES

- 200 - OK Everything worked as expected.
- 201 - Created Resource has been created.
- 204 - No Content Operation has been accepted and no content in response has been sent.
- 400 - Bad Request The request was unacceptable, often due to missing required parameter.
- 401 - Unauthorized No valid API key provided.
- 402 - Request Failed The parameters were valid but the request failed.
- 403 - Forbidden The API key doesn't have permissions to perform the request.
- 404 - Not Found The requested resource doesn't exist.
- 409 - Conflict Arguments in the request are in conflict with the server state.
- 429 - Too Many Requests Too many requests hit the API too quickly. We recommend an exponential backoff of your requests.
- 500, 502, 503, 504 - Server Errors Something went wrong on Argyle's end. (These are rare.)

---

## Example profile object

```json
{
    "id": "47b216e2-d334-4235-bc1e-185d15ab18d0",
    "account": "010db8b4-a724-47fc-a17e-733b656312a2",
    "employer": "walmart",
    "created_at": "2019-11-29T09:00:16.384575Z",
    "updated_at": "2019-11-29T09:00:16.384624Z",
    "first_name": "John",
    "last_name": "Smith",
    "full_name": "John Smith",
    "email": "john.smith@email.com",
    "phone_number": null,
    "birth_date": "1990-04-28",
    "picture_url": "https://profile.picture.com/picture.jpeg",
    "address": {
        "line1": null,
        "line2": null,
        "city": null,
        "state": null,
        "postal_code": null,
        "country": null
    },
    "ssn": "***-**-**15",
    "marital_status": null,
    "gender": "male",
    "metadata": {}
}
```
