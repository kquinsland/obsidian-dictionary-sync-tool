#!/usr/bin/env python3
"""
Unfortunately, Obsidian no longer bothers to do dictionary sync :(.
See: https://forum.obsidian.md/t/where-is-the-user-spell-check-dictionary-file-located/35714/2

This is a very simple script that attempts to solve this.
For each known dictionary file location, pull the words out of it and merge with a master dictionary.
Then replace the dictionary file(s) on disk with a copy of the master list.

The master list is the only file that needs to be kept in sync with each host.
Either add a new word to a local dictionary and then run this script to update the master list or just start with
 adding the new word to the master list.

It's crude, but the `remove_words` list can be used to remove any words from the Obsidian dictionary as well.

MAKE SURE THAT OBSIDIAN IS NOT RUNNING BEFORE RUNNING THIS SCRIPT!
Changes to the dictionary while Obsidian is running will not be respected!

TODO:
    - CLI for add/remove word from master list.
"""

from yaml import safe_load
from typing import Union
from pathlib import Path, PosixPath

from hashlib import md5

import logging.config

# We need a global for the yet-to-be initialized logger instance
log = None

# The authoritative file containing all the words from all dictionaries.
master_dictionary_file = './master_dictionary.txt'

# List of locations to check for dictionary files.
_dict_file_locations = [
    master_dictionary_file,
    # For *nix installation. This path is with the Flatpak installer, you may need to adjust the path depending on your
    #   install method.
    "~/.var/app/md.obsidian.Obsidian/config/obsidian/Custom Dictionary.txt",
    # Windows, but the \ needs to be escaped...
    # C:\Users\kquin\AppData\Roaming\obsidian\Custom Dictionary.txt
    'C:\\Users\\kquin\\AppData\\Roaming\\obsidian\\Custom Dictionary.txt'
    # Not currently a Mac user so this is not tested
    # "~/Library/Application Support/obsidian/Custom Dictionary.txt",
]

# TODO: better interface for this.
# Note: A newline will be added for you, dont include here.
remove_words = [
    "aa",
    "ZZ",
    "AA"
]


def _setup_logging() -> logging.Logger:
    """
    Loads logging config
    :return:
    """
    global log
    # Pull log cfg
    # TODO: handle exceptions
    with open('logging.yaml') as _log_cfg:
        log_cfg = safe_load(_log_cfg)
        logging.config.dictConfig(log_cfg)

    # We have a root logger, get child for __name__ and call it a day
    logging.debug("log_cfg loaded...")
    log = logging.getLogger(__name__)
    log.debug("Logging is configured.")
    return log


def get_dict_words(dict_file: Path) -> Union[None, list[str]]:
    log.debug(f"dict_file: '{dict_file}'")

    if not dict_file.exists():
        log.warning(f"No dictionary file found at '{dict_file}'")
        return None

    # See notes in dict-re.
    # One word per line, the last line should be a checksum line that we ignore
    with open(dict_file, 'r') as df:
        lines = df.readlines()

    # Basic sanity check
    ##
    checksum_line = lines[-1:][0]
    _tokens: list[str] = checksum_line.split('=')
    assert len(_tokens) == 2, "Dictionary file seems to be invalid?"
    # Otherwise dump the md5
    log.debug(f"Dictionary file: {_tokens[0]} = {_tokens[1]}")

    # Return all but the last line
    return lines[:-1]


def write_dictionary_file(dict_file: Path, words: set):
    # Sort to make life easier
    _words = "".join(sorted(words))
    checksum = md5(_words.encode()).hexdigest()

    checksum_line = f"checksum_v1 = {checksum}"
    log.debug(f"{dict_file} ->checksum:{checksum}")
    with open(dict_file, 'w') as mdf:
        mdf.writelines(_words)
        mdf.writelines(checksum_line)


if __name__ == "__main__":
    log = _setup_logging()
    log.info("Alive!")

    # Create the master dictionary if it does not yet exist
    if not Path(master_dictionary_file).exists():
        log.debug(f"Creating '{master_dictionary_file}'...")
        write_dictionary_file(Path(master_dictionary_file), set())

    # Set does the de-dupe for us :)
    all_words = set()

    # We need to keep track of all the dictionary files that we read words from. Every entry in this list
    #   will be overwritten once we have merged everything.
    ##
    found_files = []

    log.debug(f"Checking '{len(_dict_file_locations)}' dictionary files...")
    for d in _dict_file_locations:
        # The user will provide a list of paths as a STRING.
        # We need to turn that into a more useful Path() so we get useful things like ~ resolution
        ##
        log.debug(f"Checking '{d}'...")
        _path = Path(d).expanduser()
        # ~ resolution, on the platforms that support it
        if isinstance(_path, PosixPath):
            dict_file = _path

        words = get_dict_words(_path)
        if words is None:
            continue
        found_files.append(_path)
        all_words.update(words)
        log.info(f"... got '{len(words)}' words! all_words: '{len(all_words)}'.")

    # Remove any words that the user explicitly does not want in their dictionary (if present)
    ##
    # We add a `\n` to each remove word so the user doesn't have to.
    remove_words = set([f"{x}\n" for x in remove_words])
    log.debug(f"remove_words has '{len(remove_words)}' words, all_words has '{len(all_words)}' words.")
    all_words = all_words.difference(remove_words)
    log.debug(f"all_words now has' {len(all_words)}' words.")

    log.info(f"Writing out '{len(all_words)}' words to the'{len(found_files)}' dictionary files on host...")
    for source in found_files:
        write_dictionary_file(source, all_words)
