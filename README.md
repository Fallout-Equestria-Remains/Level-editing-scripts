# Level editing scripts
Some scripts for the more convenient level creation. At the moment includes rooms uniter (by name) and rooms cutter.

**Uniter** unites two or more XML location files into the one file. Might be used to update location files, concatenate rooms from different people etc.

**Cutter** saves rooms specified by name info different file, removing them from the input file. Might be used to detach the room templates.

_Current scripts version is really young! Make backups before operations!_


### Requirements

1. [Python 3](https://www.python.org/downloads/) and above.

2. Library "FoER_rooms_lib.py" in this repo.


### Examples

#### Uniter
```
python FoER_rooms_unite.py --help
```
🠕 Show help for the uniter.

```
python FoER_rooms_unite.py rooms_mbase.xml mbase_room_template.xml
```
🠕 Concatenate "rooms_mbase.xml" and "mbase_room.template.xml" to the file "united_rooms.xml".

```
python FoER_rooms_unite.py rooms_mbase.xml mbase_room_template.xml -o rooms_mbase.xml
```
🠕 Concatenate "rooms_mbase.xml" and "mbase_room.template.xml" and writes back to the file "rooms_mbase.xml".

```
python FoER_rooms_unite.py --verbose --dry-run rooms_mbase.xml mbase_room_template.xml
```
```
python FoER_rooms_unite.py -v -d rooms_mbase.xml mbase_room_template.xml
```
🠕 Show what will be united without modifying anything (without writing to file).


---

#### Cutter
```
python3 FoER_rooms_cut.py --help
```
🠕 Show help for the cutter.

```
python FoER_rooms_cut.py rooms_mbase.xml вертикаль
```
🠕 Cut the room named "вертикаль" into file "cutted_rooms.xml" and remove this level from the original file.

```
python FoER_rooms_cut.py --verbose --dry-run rooms_mbase.xml вертикаль управление камеры кабинеты
```
```
python FoER_rooms_cut.py -v -d rooms_mbase.xml вертикаль управление камеры кабинеты
```
🠕 Show rooms to remove without modifying anything (without writing to files).

