# Level editing scripts
Some scripts for the more convenient level creation. For the v0.6 there are:

- **Uniter** unites two or more XML location files into the one file. May be used to update location files, concatenate rooms from different people etc.

- **Cutter/copier/remover** can save rooms specified by name info different file and remove them from the input file. May be used to detach the room templates. Understands the back layer rooms.

- **Sorter** sorts XML content in place by name or like in the default FoER level editor. Also can automatically remove the "test=1" option tag from rooms, useful for releases.

- **Info** prints statistics about objects and decorations (the object name or room name regex filters may be passed). May be used to compare your levels content with the default pack


### Requirements

1. [Python version 3](https://www.python.org/downloads/) or above.

2. Library [libfoerrooms.py](libfoerrooms.py) from this repo.

3. Python libs `xml.dom.minidom`, `re`, `argparse` and `contextlib` (all of them are usually already preinstalled with Python)


### Usage and examples

Examples quick access:
* [Unite](README.md#uniter)
* [Cut/copy/remove](README.md#cuttercopierremover)
* [Sort](README.md#sorter)
* [Number statistics](README.md#statistics)



Every script have clear (I hope so :D) help page when the `--help` or `-h` is passed. Like this:
```
$ python FoER_rooms_unite.py --help

usage: 
  FoER_rooms_unite.py file1.xml file2.xml [file3.xml ...] [-o OUTFILE] [-afsSv]
  FoER_rooms_unite.py --help|--version

FoER locations room uniter v0.6. (c) Keirlex

positional arguments:
  file1.xml file2.xml [file3.xml ...]
                        Files to unite. Lastest room files has higher priority, their rooms will rewrite previous with the same
                        names (if no "-a" argument provided).

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --output OUTFILE
                        Output file to write. If name set to "-", output to stdout. If whole "-o" is omitted, will be used name
                        "outrooms_united.xml". Note that output file will be overwritten!
  -a, --append-only, --safe-concat
                        Terminate with message when trying to overwrite some previous room. Output file will not be created or
                        updated.
  -s, --sort            Sort output by room names like in the default level editor.
  -S, --sort-abc        Sort output by room names in lexicographic order.
  -v, --verbose         Be verbose and print more info (including processed room names).
  -V, --version         Print out version of the script and exit.
```

Also some scripts supports the text regular expressions for different purposes. You can find the explanation on many sites, like https://regex101.com/, https://docs.python.org/3/howto/regex.html#regex-howto or https://regexr.com/


#### Uniter

Concatenate "rooms_mbase.xml" and "mbase_room.template.xml" to the file "united_rooms.xml"
```
python FoER_rooms_unite.py rooms_mbase.xml mbase_room_template.xml
```

Concatenate "rooms_mbase.xml" and "mbase_room_template.xml" and write to the file "rooms_mbase.xml"
```
python FoER_rooms_unite.py rooms_mbase.xml mbase_room_template.xml -o rooms_mbase.xml
```

Show what will be united without modifying anything (without writing to file)
```
# On Linux and macOS:
python FoER_rooms_unite.py --verbose rooms_mbase.xml mbase_room_template.xml > /dev/null
# On Windows:
python FoER_rooms_unite.py -v rooms_mbase.xml mbase_room_template.xml >NUL
```

---

#### Cutter/copier/remover

Cut the room named "вертикаль" into file "cutted_rooms.xml" and remove this level from the original file
```
python FoER_rooms_cut.py rooms_mbase.xml вертикаль
```

Show rooms to cut without modifying anything (without writing to files, automatically detect back layer rooms)
```
python FoER_rooms_cut.py --verbose --back-layers --dry-run rooms_mbase.xml вертикаль управление камеры кабинеты
 -- OR --
python FoER_rooms_cut.py -v -b -d rooms_mbase.xml вертикаль управление камеры кабинеты
```

Copy rooms with names containing "forcopy" to the "newfile.xml" (automatically detect back layer rooms)
```
python FoER_rooms_cut.py rooms_mbase.xml --copy -o newfile.xml --back-layers --regex "forcopy"
```

Remove the rooms which names starts with a "Text"
```
python FoER_rooms_cut.py rooms_mbase.xml -o rooms_mbase.xml --delete --regex "^Text"
```

---

#### Sorter

Sort like the default level does in its rooms list
```
python FoER_rooms_sort.py rooms_mbase.xml --sort
```

Sort by name and remove the "test=1" option tags (with the info what is happening at the moment)
```
python FoER_rooms_sort.py rooms_mbase.xml --remove-test --sort-abc --verbose
  -- OR --
python FoER_rooms_sort.py rooms_mbase.xml -t -S -v
```

---

#### Statistics

Count the number of objects and background decorations for all rooms in the file
```
python FoER_rooms_info.py rooms_mbase.xml
```

Count the number of objects for all rooms in the file
```
python FoER_rooms_info.py rooms_mbase.xml --objects
  -- OR ---
python FoER_rooms_info.py rooms_mbase.xml -o
```

Count the number of background decorations "mcrate2" and "light6" for all rooms in the file
```
python FoER_rooms_info.py rooms_mbase.xml -b mcrate2 light6
```

Count the number of background decorations containing the "light" (like "light6", "stlight1" etc) for all rooms in the file
```
python FoER_rooms_info.py rooms_mbase.xml -b light --regex-stat
```

Count the the TOTAL number of objects in rooms NOT containing "Text" in their name (useful for comparing your levels with the default pack):
```
python FoER_rooms_info.py rooms_mbase.xml Text --objects --total --regex-rooms --regex-rooms-invert
  -- OR --
python FoER_rooms_info.py rooms_mbase.xml Text -o -t -R -I
```
