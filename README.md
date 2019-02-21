# Audionodes

Audio generation in Blender nodes.

Lisenced under GPLv.3. (https://www.gnu.org/licenses/gpl-3.0.en.html)

## Installation

We currently support Windows, Linux and macOS.
For now Audionodes doesn't come with the required libraries on Linux and macOS. You need to install `SDL 2` (for audio output and output) and `FluidSynth` (for MIDI input, and possibly SoundFont support in the future) for it to work. The Windows version has dependencies bundled in.

After installing, you may want to look at the tutorial at the end of the README.

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
into your Blender installation (if one was found when running `cmake`), like so:

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


## Quick start tutorial

Open a node editor view, press on the speaker icon, and create a new node tree.

![new node tree](https://i.imgur.com/TytRPHJ.png)

The most crucial node is the output node, the `Sink`. The signal it receives will be played by your speakers. Add one with `Shift + A > Audio output > Sink`. Now let's add simple sine oscillator: `Shift + A > Generators > Oscillator`. You can adjust the frequency and the amplitude before plugging it into the sink, say `400 Hz` at `0.4` amplitude. Brace your ears.

![Oscillator -> Sink](https://imgur.com/wkY8TnR.png)

You should now hear a tone being played. If not, have a look at the console output (open Blender via a terminal or `Window > Toggle System Console`) and maybe open an issue so we can figure out what's wrong.

Oh, go ahead, play with the values, they can all be changed real-time!

Next let's explore the power of modularity.
You can plug the output of any node into any input of any node, allowing endless customization.
Create a new Oscillator (just like before), but this time let's configure it to be an LFO, a low frequency oscillator, that controls the frequency of our first oscillator.

![Oscillator -> Oscillator -> Sink](https://imgur.com/QqGlTtl.png)

You already know what frequency and amplitude do.
The offset parameter in the `Oscillator` node changes what value the oscillator oscillates around.
This one, with amplitude `50` and offset `400` would then oscillate between `350` and `450`.
The same could be accomplished with a math "Add" node.
You should now hear a sine wave that has a continuously changing frequency.

How about playing it like a conventional keyboard instrument?
You can use the `MIDI input` and `Piano` nodes (available in the `MIDI` node category) to make it playable.

![MIDI input -> Piano -> Oscillator -> Sink](https://imgur.com/uVdloUn.png)

You might need to create the `MIDI input` node after plugging in your MIDI device on Windows, or connect it properly through an interface like [QjackCtl](https://qjackctl.sourceforge.io/) on Linux. On Windows you may also need something like [loopMIDI](http://www.tobias-erichsen.de/software/loopmidi.html) in order to get MIDI input from other software.

If you don't have a MIDI keyboard lying around, try a virtual one like [VMPK](http://vmpk.sourceforge.net/).

Currently there is no envelope configured, so ends and beginnings of notes will be abrupt. The output range of the `Sink` goes from `-1` to `1`, and anything that sums to louder than that will be clipped (and not sound great depending on your taste).

That's it! Be sure to try some of the other nodes as well. There is more in-depth documentation available at the [wiki](https://github.com/nomelif/Audionodes/wiki) (work in progress).

### Interesting setups (legacy)

We have made up a gist with interesting Audionodes setups, see here: https://gist.github.com/nomelif/759d6963c3ded049268f6e6ada855d3f. They are complete with samples on SoundCloud.
