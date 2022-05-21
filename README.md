# Transfer.sh helper

The idea of the script is to store your transfer.sh links and simplify its usage, so you can remember them later and know when they will expire.

## Features

- Store your Transfer.sh links in a sqlite3 file locally.
- Simplify the transfer.sh usage.
- Automatically calculates expired links.
- Upload multiple files at once (Multithreading support).
- Option to easily delete the file from their servers.

https://user-images.githubusercontent.com/49915167/169654192-993f0010-02db-4eba-812e-243f3e5a2fe2.mp4

## THIS SCRIPT IS NOT OFFICIAL.

I am not the author of the Transfer.sh service and don't have any affiliation with it.

I am just a user from their services, so I wrote this script to help me remember my links.

### Check out [Transfer.sh](https://github.com/dutchcoders/transfer.sh) on Github and give them a star.

# Installation

This is the easiest part, just go to the releases and download the [latest version](https://github.com/OLoKo64/transfer-sh-store/releases), after that you just need to execute the program inside a terminal:

```bash
./trasferhelper
```

If you get a error from not having executable permission just execute:

```bash
chmod +x transferhelper
```

You can also place the executable in your `/home/$USER/.local/bin` folder, after that just execute `transferhelper` in your terminal (This folder needs to be on PATH).

## Usage

This script has a few commands, you can use them in your terminal:

### Upload a file:

```bash
transferhelper -u <file>
```

### View your stored links:

```bash
transferhelper
```

### Delete a link:

```bash
transferhelper -d
```

After running this command it will ask you for the link you want to delete and if you want to delete from the cloud as well.

### Delete the database:

```bash
transferhelper -DD
```

After running this command it will ask for confirmation.

### View help:

```bash
transferhelper -h
```

---

## Add `.local/bin` to path

Just add this code to your `.bashrc` or `.bash_profile`

```bash
# Add local bin to path
export PATH=$PATH:/home/$USER/.local/bin
```
