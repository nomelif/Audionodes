# Audionodes

Audio generation in blender nodes under Linux.

Lisenced under GPLv.3. (https://www.gnu.org/licenses/gpl-3.0.en.html)

## Installation

For now Audionodes doesn't come with the required libraries. You need to install `SDL 2` and `FluidSynth` for it to work.
We currently support Linux and macOS.

### I am running Linux

#### Basic setup

On Ubuntu, install the necessary packages:

```
sudo apt install libsdl2-2.0-0 libfluidsynth
```

On Arch, this would be `sudo pacman -S sdl2 fluidsynth`.

On other systems, try to install similar packages.

Download the plugin in zip format for your appropriate platform under Releases,
and install it just like any other Blender plugin.

### I am running macOS

You should install the necessary packages via [Homebrew](https://brew.sh/).

```
brew install sdl2 fluidsynth
```

Download the plugin in zip format for your appropriate platform under Releases,
and install it just like any other blender plugin.

#### Having trouble installing?

Please open an issue. Hopefully we can help.

## Compiling from source

### Linux

You need `gcc/g++` for compiling, and the dependencies with header files.

```
sudo apt install gcc libsdl2-dev libfluidsynth-dev
```

Again, use similar packages with other distributions.

Then run the compile script `./compile.sh`. After that you can zip the folder up and install it into Blender.

### macOS

Here we will use `clang` for compiling, you will most likely be prompted to install the XCode packages when trying to compile.

Again, install the required dependencies via [Homebrew](https://brew.sh/) first, then run `./compile.sh`.
After that you can zip the folder up and install it into Blender.

## How does one use this sorcery?!
**Note: This guide is fairly outdated, but you should get the idea.**
We are going to update it.

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
