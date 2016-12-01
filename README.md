# Audionodes

Audio generation in blender nodes.

_We do not support Windows yet, but we will try to as soon as we figure how to package everything._

Lisenced under GPLv.3. (https://www.gnu.org/licenses/gpl-3.0.en.html)

## Install

For now Audionodes doesn't come with the required libraries. You need to install `PyAudio` and `NumPy` for it to work.

### I am running Linux

On Ubuntu run this command:

`sudo apt-get install python-pyaudio python3-pyaudio python3-numpy`

On Archlinux, install `pip` and `numpy` with `sudo pacman -S python-pip python-numpy`. From `pip` install pyaudio with `pip install PyAudio`.

On other systems, try to install similar packages.

### I am running macOS

With `Homebrew` installed, run `brew install python3` to (among other things) setup `pip`correctly. Then install NumPy with `sudo pip3 install numpy`. Installing `PyAudio` is more sorcerous: `brew install portaudio && pip install pyaudio`.

Then download this repository and unpack the file `audio_nodes.py`. In Blender, go to `File > User Preferences > Addons > Install from File...`. Pick the downloaded `audio_nodes.py` and then check the checkbox to enable the addon.

### It still doesn't work

Please open an issue. Hopefully we can fix it.

## How does one use this sorcery?!

We start by creating a new node setup:

<a href="http://imgur.com/pz2aQMr"><img src="http://i.imgur.com/pz2aQMr.png" title="source: imgur.com" /></a>

We will first add a `Sink` (`Shift + A > Outputs > Sink`). That is where our sound will go at the end.

<a href="http://imgur.com/vsMk0Ez"><img src="http://i.imgur.com/vsMk0Ez.png" title="source: imgur.com" /></a>

Let's try something simple: we will play a 400Hz sine wave. This is mostly to test our setup. Go add a `Inputs > Sine` and type `400` into the topmost input. Then (while aware of a possibly loud sound), hook it up to the sink:

<a href="http://imgur.com/kXsd1sT"><img src="http://i.imgur.com/kXsd1sT.png" title="source: imgur.com" /></a>

You should hear a continuous beep. Let's make it more interesting. Add another Sine and give it a frequency of `10`, a `Range` of `0.3` and an `Offset` of `0.7`. Then hook it up to the first Sine's `Range` Like here:

<a href="http://imgur.com/z77ttYf"><img src="http://i.imgur.com/z77ttYf.png" title="source: imgur.com" /></a>

What this does is change the volume of the sound we had before (that's what range does) along a smooth curve (a sine wave) ten times per second (that is: at 10Hz, 1Hz meaning basically once per second). The range means that this curve moves within `0.3` of it's default range vertically. Together with the `Offset` and knowing that by default the range is -1 to 1, that means that the volume of our sound varies between 70% + 30% = 100% and 70% - 30% = 40%.

We can even make this playable by keyboard: plug in a `Piano` input like so:

<a href="http://imgur.com/yG1n4Rf"><img src="http://i.imgur.com/yG1n4Rf.png" title="source: imgur.com" /></a>

Activate it by hitting the `Keyboard capture` button and terminate it by hitting `Esc` on your keyboard. While the `Piano` node is activated, you can play with your keyboard: the keys from `§` to `0` are one octave. MIDI keyboard support is being planned.

### Interesting setups

#### Sonar

This imitates a sonar ping:

<a href="http://imgur.com/T7KP32w"><img src="http://i.imgur.com/T7KP32w.png" title="source: imgur.com" /></a>
