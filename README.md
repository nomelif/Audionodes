# Audionodes

Audio generation in Blender nodes.

Lisenced under GPLv.3. (https://www.gnu.org/licenses/gpl-3.0.en.html)

## Installation

We currently support Windows, Linux and macOS.
For now Audionodes doesn't come with the required libraries on Linux and macOS. You need to install `SDL 2` (for audio output and output) and `FluidSynth` (for MIDI input, and possibly SoundFont support in the future) for it to work. The Windows version has dependencies bundled in.

### I am running Windows

Download the plugin in zip format for Windows under Releases,
and install it just like any other Blender plugin.

### I am running Linux

On Ubuntu, install the necessary packages:

```
sudo apt install libsdl2-2.0-0 libfluidsynth1
```

On Arch, this would be `sudo pacman -S sdl2 fluidsynth`.

On other distributions, try to install similar packages.

Download the plugin in zip format for Linux under Releases,
and install it just like any other Blender plugin.

### I am running macOS

You should install the necessary packages via [Homebrew](https://brew.sh/).

```
brew install sdl2 fluidsynth
```

Download the plugin in zip format for macOS under Releases,
and install it just like any other Blender plugin.

### Having trouble installing?

Please open an issue. Hopefully we can help.

## Compiling from source

### Linux dependencies

You need `GCC/g++` for compiling, the `CMake` build system, and the dependencies with header files.

```
sudo apt install cmake make gcc libsdl2-dev libfluidsynth-dev
```

Again, use similar packages with other distributions.

*Building instructions after other platforms' dependencies...*

### macOS dependencies

Here we will use `clang` for compiling, you will most likely be prompted to install the XCode packages when trying to compile.

Again, install the required dependencies (+ CMake) via [Homebrew](https://brew.sh/):

```
brew install cmake sdl2 fluidsynth
```

### Windows dependencies

This one's tricky. You will need `Visual Studio C++` for compilation (tested on 2017), and a dependency manager for it called [vcpkg](https://github.com/Microsoft/vcpkg).

Assuming Visual Studio is already installed, and that you have a working Git installation.

Start by installing [CMake](https://cmake.org/downloads).

Now, set up `vcpkg` for x64 and install the required dependencies.
Fire up PowerShell and naviage into a suitable folder, then:

```
PS> git clone https://github.com/Microsoft/vcpkg.git
PS> cd vcpkg
PS> .\bootsrap-vcpkg.bat
*takes a while*
PS> .\vcpkg install --triplet x64-windows sdl2 fluidsynth
*takes a long while*
```

### Building in Linux & macOS

Change into the repository directory. First prepare the CMake-build:

```
cmake .
```

In order to compile with debug symbols (for `gdb` or other debuggers),
you can specify the build type:

```
cmake . -DCMAKE_BUILD_TYPE=Debug
```

Revert back to normal with `-DCMAKE_BUILD_TYPE=Release`.

Now, to build only the `native` library (audio generation backend), run

```
make
```

To build the Blender-addon .zip-file, run

```
make blender
```

`Audionodes.zip` should appear at the repository root, you can now
install it into Blender.

If you are lazy, you can also build and install the addon directly
into your Blender installation, like so:

```
make blender_install
```

When running `cmake`, a message will be printed about which Blender
installation this will use or if none was found at all.
It also might simply not work on your system due to various reasons.

Oh, and to build, install and enable the addon, you can `make blender_install blender_enable`.
Conversly, you can remove the addon with `make blender_uninstall`.

### Building in Windows

Navigate to the Audionodes repository (in PowerShell) and configure CMake:

```
PS> cmake . `
-DCMAKE_TOOLCHAIN_FILE=[vcpkg]\scripts\buildsystems\vcpkg.cmake `
-DVCPKG_TARGET_TRIPLET=x64-windows `
-DCMAKE_GENERATOR_PLATFORM=x64
```

where `[vcpkg]` should be replaced with the path you installed `vcpkg` in.

And build.

```
PS> cmake --build . --target blender --config Release
```

`Audionodes.zip` should appear at the repository root and can then be installed into Blender.


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
