# Transfer.sh store

The idea of the script is to store your transfer.sh links, so you can remember them later and know when they will expire.

# Installation

This is the easiest part, just go to the releases and download the [latest version](https://github.com/OLoKo64/transfer-sh-store/releases), after that you just need to execute the program inside a terminal:

```bash
./trasfershstore
```

If you get a error from not having executable permission just execute:

```bash
chmod +x transfershstore
```

You can also place the executable in your `/home/$USER/.local/bin` folder, after that just execute `transfershstore` in your terminal (This folder needs to be on PATH).


## Add `.local.bin` to path

Just add this code to your `.bashrc` or `.bash_profile`

```bash
# Add local bin to path
export PATH=$PATH:/home/$USER/.local/bin
```