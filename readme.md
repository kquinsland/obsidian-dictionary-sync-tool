# Archive/EoL/Deprecated.

Please see/use the rust re-write [here](https://github.com/kquinsland/obsidian-dict-sync)


-----

# Obsidian Dictionary Sync tool

I use obsidian on both windows and linux machines.
In the early days, Obsidian managed the user dictionary inside of the `.obsidian` folder which meant that the dictionary would be synced across all hosts.
This is no longer the case :(.

Now, every time I add a word to the custom dictionary on one host, I need to add it to the dictionary on all the other hosts.  Annoying!

This is a super simple script that's meant to make that less of a problem.

## Using

> **Warning**
> Make sure that obsidian is CLOSED before running this script.
> This tool makes changes to files on disk that obsidian does not expect so it must be closed

There is no CLI; all options are configured _in_ the script. See the various notes/comments in the script for more.

Add the path(s) to your custom dictionary file(s) on each host that you use Obsidian on and just run this script.
As you run the script on each host, the `master_dictionary.txt` should get all of the unique whitelisted words from each host.

The content of the master dictionary is then written BACK into each custom dictionary file so the master dictionary and the custom dictionary file eventually become consistent.

Re run the script on any host where you add a new word to the dictionary to get the new word copied from the local custom dictionary into the master dictionary. Once the updated master has synced to every other host, re-run the script on those hosts to copy the new word(s) from the master into the local dictionaries.

## Installing

Any standard python 3.10 install should be sufficient.
The only non `stdlib` dependency is `pyyaml` for the logging config. Admittedly that's overkill for such a small script but I use `logging` extensively and did so here for consistency.

I am using `poetry` for dependency management but you could skip this and just go with a basic `pip install pyyaml`.

Download or `git clone` the repo and place inside of a folder that is included in your obsidian sync solution.

You want something that looks like this:

```shell
SyncFolderRoot/
├── dict-sync/
│   ├── master_dictionary.txt
│   ├── sync.py
│   └── ...
└── Vaults/
    ├── someVaultNameHere/
    │   ├── .obsidian/
    │   └── some_note.md
    └── someOtherVaultNameHere/
        ├── .obsidian/
        └── some_note.md
```

Technically, only the `master_dictionary.txt` needs to be part of your sync solution but it's easier to put the full script in the sync dir.

### Windows

I have not sworn this much at a computer in a _long time_.
What a nightmare it was to get this up and running ... and I still don't have `poetry env use` working properly with the `%PATH%` env var.

My notes on getting this set up are more swearing and passive aggressive comments about why windows isn't taken seriously as a developers OS or a server host OS than actually useful instructions so I'm omitting them here.

If somebody that knows how to make python3 and windows and `poetry` play nice wants to give some instructions on how to set this up, I will happily merge your PR!
