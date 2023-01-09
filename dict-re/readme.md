# Custom Dictionary reverse engineering

Trying to figure out how the dictionary file is implemented.

The dictionary format seems to be a simple "one word per line" format and the last line is a checksum.

The checksum is too short to be sha* family so Let's assume MD5?

Starting with a simple dictionary file:

```shell
❯ cat ~/.var/app/md.obsidian.Obsidian/config/obsidian/Custom\ Dictionary.txt
TechIngredients
ws5
checksum_v1 = ddfa4be02617bed6e29a41a9c744b454%
```

Making a copy and dropping the last line:

```shell
❯ hexdump -C cust.txt
00000000  54 65 63 68 49 6e 67 72  65 64 69 65 6e 74 73 0a  |TechIngredients.|
00000010  77 73 35 0a                                       |ws5.|
00000014
❯ hexdump -C cust.txt.ORIG
00000000  54 65 63 68 49 6e 67 72  65 64 69 65 6e 74 73 0a  |TechIngredients.|
00000010  77 73 35 0a 63 68 65 63  6b 73 75 6d 5f 76 31 20  |ws5.checksum_v1 |
00000020  3d 20 64 64 66 61 34 62  65 30 32 36 31 37 62 65  |= ddfa4be02617be|
00000030  64 36 65 32 39 61 34 31  61 39 63 37 34 34 62 34  |d6e29a41a9c744b4|
00000040  35 34                                             |54|
00000042
```

Checking the hash of `cust.txt`:

```shell
❯ md5sum cust.txt
ddfa4be02617bed6e29a41a9c744b454  cust.txt
```

Perfect! We have a match with `ddfa4be02617bed6e29a41a9c744b454`.

The dictionary is one word per line, terminated with newline char.
The words are ordered in basic ASCII order, descending. E.G.: `A` (`0x41`) comes before `a` (`0x61`). The default `sorted()` method will work perfectly :).

The last line of the file contains the string `checksum_v1 = $checksumHere` and has no termination character.

## Live reload?

After some testing, it appears that the running obsidian process does NOT respect or respond to any modifications to the file made externally.

Using _just_ obsidian and an empty dictionary file, I added `aa` to the dictionary, made a copy of the file and restarted.
I then added `AA` to the dictionary and went into the Settings -> editor -> Spell check which has a rudimentary way to see the words in the dictionary.

I confirmed that the dictionary had both `aa` and `AA` on it and then went back to the main editor window for an empty note.
I copied in the custom dictionary with JUST `aa` on it and then went back to settings to see if the spell check would show JUST `aa` on the list now. It did not.

So it's an unfortunate conclusion but it looks like any changes to the dictionary file must be made while obsidian is closed if they're to be effective.
