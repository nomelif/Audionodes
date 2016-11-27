# Audionodes

Audio generation in blender nodes.

_We do not support Windows yet, but we will try to as soon as we figure how to package everything._

## Install

For now Audionodes doesn't come with the required libraries. You need to install `PyAudio` and `NumPy` for it to work.

### I am running Linux

On Ubuntu run this command:

`sudo apt-get install python-pyaudio python3-pyaudio python3-numpy`

On Archlinux, install `pip` and `numpy` with `sudo pacman -S python-pip python-numpy`. From `pip` install pyaudio with `pip install PyAudio`.

On other systems, try to install similar packages.

### I am running macOS

With `Homebrew` installed, run `brew install python3` to (among other things) setup `pip`correctly. Then install NumPy with `sudo pip3 install numpy`. Installing `PyAudio` is more sorcerous: `brew install portaudio && pip install pyaudio`.

Then download the addon itself from the downloads section of this repository (or right here). In Blender, go to `File > User Preferences > Addons > Install from File...`. Pick the downloaded `audio_nodes.py` and then check the checkbox to enable the addon.

### It still doesn't work

Please open an issue. Hopefully we can fix it.

## How does one use this sorcery?!

[todo]
