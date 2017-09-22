# Audionodes

Audio generation in blender nodes under Linux.

Lisenced under GPLv.3. (https://www.gnu.org/licenses/gpl-3.0.en.html)

## Install

For now Audionodes doesn't come with the required libraries. You need to install `pyalsaaudio` and `NumPy` for it to work.

### I am running Linux

We have found that Audio Nodes has a greater chance of working (especially with MIDI setups) on versions of Blender that are installed through a package manager. We speculate that this is due to them using a standard Python 3 release.

### Basic setup

On Ubuntu run this command:

```
sudo apt-get install python3-numpy python3-pip
```

On Archlinux, install `pip` and `numpy` with `sudo pacman -S python-pip python-numpy`.


Regardless of your distribution, install `pyalsaaudio` from `pip` with `pip3 install PyGame --user`.

On other systems, try to install similar packages.

### Aside on MIDI input

You can use a MIDI keyboard with Audio Nodes. It is possible that it may work out of the box, but we recommend installing Alsaseq. It is available through `pip`, but I never got it to build right. This slightly modified version of an older release seems to work fine, though. Download [this](https://drive.google.com/file/d/0B0nfZWGohnB7MG4wMnZ6RzUyb0E/view?usp=sharing) zip file and unpack it where you want. Navigate into it and run:

```
sudo python3 setup.py build
sudo python3 setup.py install
```

The archive is an old version (only one that I got to build) of alsaseq, see here: [Alsaseq home site](http://pp.com.mx/python/alsaseq/)

To connect to a midi keyboard, add a `Piano` node and hit `Keyboard capture`. This should create an alsa socket to connect a MIDI device to. A nice GUI tool to do this is QjackCtl. After launching it go to `Connect > Alsa [tab]` and hook up the USB midi on the left to Audionodes on the right. To kill the sound from the piano node quickly, hit escape on the keyboard.

### Main installation

Download this repository as a zip and load that zip into Blender through `User Preferences > Addons > Install from File...`. Then enable the addon by checking the checkbox.

### Troubleshooting

If there is an error when activating the addon, you are probably not using the right Python installation. To remedy this, open a terminal and run `python3`. There type:

```python
import sys
sys.path
```

On my machine the output looks like:

```python
['', '/usr/local/lib/python3.5/dist-packages/alsaseq-0.4-py3.5-linux-x86_64.egg', '/usr/lib/python3/dist-packages', '/usr/lib/python35.zip', '/usr/lib/python3.5', '/usr/lib/python3.5/plat-x86_64-linux-gnu', '/usr/lib/python3.5/lib-dynload', '/usr/local/lib/python3.5/dist-packages']
```

Copy the output of the command. In Blender go to `Scripting` (from the dropdown in the very upper bar that says `Default`) and write the following into the console:

```python
import sys
sys.path.extend(whatever your output was)
```

This terminal lets you copy and paste using Ctrl + C and Ctrl + V.

Now go and enable the addon, it should work.

### Troubleshooting

If there is an error when enabling the addon, you are probably not using the right Python installation. To remedy this, open a terminal and run `python3`. There type:

```python
import sys
sys.path
```

On my machine the output looks like:

```python
['', '/usr/local/lib/python3.5/dist-packages/alsaseq-0.4-py3.5-linux-x86_64.egg', '/usr/lib/python3/dist-packages', '/usr/lib/python35.zip', '/usr/lib/python3.5', '/usr/lib/python3.5/plat-x86_64-linux-gnu', '/usr/lib/python3.5/lib-dynload', '/usr/local/lib/python3.5/dist-packages']
```

Copy the output of the command. In Blender go to `Scripting` (from the dropdown in the very upper bar that says `Default`) and write the following into the console:

```python
import sys
sys.path.extend(whatever your output was)
```

This terminal lets you copy and paste using Ctrl + C and Ctrl + V.

Now go and enable the addon, it should work.

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

Activate it by hitting the `Keyboard capture` button and terminate it by hitting `Esc` on your keyboard. While the `Piano` node is activated, you can play with a MIDI keyboard. Windows should jump on the first one that moves. Linux with the alsaseq module installed should be hand-configured with QJackCTL (GUI) or aconnect (CLI). Linux without alsaseq installed should try to autoconfigure itself like Windows.

### Interesting setups

We have made up a gist with interesting Audionodes setups, see here: https://gist.github.com/nomelif/759d6963c3ded049268f6e6ada855d3f. They are complete with samples on SoundCloud.

#### Sonar [TODO: Move to the Gist]

This imitates a sonar ping:

<a href="http://imgur.com/T7KP32w"><img src="http://i.imgur.com/T7KP32w.png" title="source: imgur.com" /></a>
