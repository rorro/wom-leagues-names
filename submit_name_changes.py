#!/usr/bin/env python3

import asyncio
import logging
import sys
import typing as t
import requests
import wom
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler

#########################################################
# START Configuration
#########################################################

LOG_LEVEL: t.Final[int] = logging.DEBUG
"""The logging level to use, either DEBUG or INFO."""

LEAGUE_URL: t.Final[str] = "https://api.wiseoldman.net/league"

MAIN_URL: t.Final[str] = "https://api.wiseoldman.net/v2"

WOM_USER_AGENT: t.Final[str] = "WOM Leagues Name submitter"
"""The user agent to send with requests to the WOM API."""


SUBMITTED_NAMES_FILE = "submitted_names.json"
""" The file where all previously submitted name changes are stored """

#########################################################
# END Configuration
#########################################################

#########################################################
# START Logging
#########################################################


def setup_logging() -> logging.Logger:
    """Sets up and returns the logger to use in the script."""
    logger = logging.getLogger(__file__)
    logger.setLevel(LOG_LEVEL)

    sh = logging.StreamHandler(sys.stdout)
    rfh = RotatingFileHandler(
        "./wom-league-name-submitter.log",
        maxBytes=1048576,  # 1MB
        encoding="utf-8",
        backupCount=20,
    )

    ff = logging.Formatter(
        f"[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    rfh.setFormatter(ff)
    sh.setFormatter(ff)
    logger.addHandler(rfh)
    logger.addHandler(sh)
    return logger


LOGGER: t.Final[logging.Logger] = setup_logging()

#########################################################
# END Logging
#########################################################


async def main():
    # Fetch previously stored name changes, if any
    if (Path(SUBMITTED_NAMES_FILE).is_file()):
        with open(SUBMITTED_NAMES_FILE, "r") as f:
            submitted_names = json.load(f)
    else:
        submitted_names = []

    wom_client = wom.Client(user_agent=WOM_USER_AGENT)
    await wom_client.start()
    wom_client.set_api_base_url(LEAGUE_URL)

    # Fetch most recent name changes from league API
    league_response = await wom_client.names.search_name_changes(limit=50)
    if league_response.is_ok:
        league_name_changes = league_response.unwrap()
        data = [{"oldName": name_change.old_name, "newName": name_change.new_name} for name_change in list(filter(
            lambda change: {"oldName": change.old_name, "newName": change.new_name} not in submitted_names, league_name_changes))]

        if len(data) == 0:
            LOGGER.info(f"No new name changes found to submit.")
            await wom_client.close()
            return

        LOGGER.info(f"Found '{len(data)}' new name changes to submit.")

        # Submit name changes to main site
        response = requests.post(f"{MAIN_URL}/names/bulk", json=data)

        # If the submission was successful, store the newly submitted names locally.
        # 400 is when all name changes that were submitted are either pending or already approved.
        if response.status_code == 201 or response.status_code == 400:
            with open(SUBMITTED_NAMES_FILE, "w") as f:
                f.write(json.dumps(submitted_names + data, indent=2))
        else:
            LOGGER.info(
                f"Something went wrong while submitting name changes. {response.status_code, response.text}")
    else:
        LOGGER.info(
            f"Something went wrong while fetching league name changes {league_response.unwrap_err()}")

    await wom_client.close()

if __name__ == "__main__":
    LOGGER.info("*" * 64)
    LOGGER.info("WOM Leagues name change submitter starting...")
    asyncio.run(main())
    LOGGER.info("Name submitter complete.")
    LOGGER.info("*" * 64)
