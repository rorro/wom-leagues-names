# WOM Leagues Names

A script that fetches the most recent name changes submitted to the [league](https://league.wiseoldman.net) version of [wiseoldman.net](https://wiseoldman.net) and submits them to the main site.

## Setup

Python 3.8 or higher is required to use the `wom.py` dependency. This shouldn't be
an issue as I think ubuntu ships with 3.8 by default.

- Clone the repo if you plan to only run the script
- Fork the repo if you plan to contribute to it

Create a virtual environment and activate it

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install dependencies

```bash
$ pip3 install -r requirements.txt
```

Run the script

```bash
$ python3 main.py
```
