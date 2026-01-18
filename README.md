# Pianable

Why buy a piano when you can print a piano?

<img src="https://github.com/Relay-py/pianable/blob/main/Screenshot%202026-01-18%20102823.png" />

## Description

Pianos can be expensive, occupy a large space, and are difficult to maintain. Why deal with all that hassle when you can use a computer application while also having the full piano experience?

Pianable takes constant video of two viewpoints, a top-down view to check which note is being played and a front-view which checks if the note is being played. These two videos are displayed on the left side of  your screen with a soundfont interface on the right which can be used to play the piano in different soundfonts similarly to an electric piano.

## Usage

Before Pianable can run, a few things must be done.

- A paper piano consisting of multiple octaves must be laid out on a flat surface.
- A top-down camera should be placed above the piano so that all keys can be seen. The front view camera should likewise be placed at a distance so that it can recognize the edge of the table and contain the edges of the paper piano.
- These two cameras’ inputs need to be able to be read by the computer, likely through an external app such as Iriun.

Once these have all been set up, Pianable can be run.

Upon running, the top-down view should appear, if instead the front view appears, switch the position of the two cameras either in the external app or physically.
On the top-down view, click the four corners of the paper piano. This creates the borders of the of piano and automatically scales the keys to its size. Click again to confirm and switch to the front view.

On the front view, click twice, one on each edge of the table the paper piano is currently placed on. This will define when the key is being “pressed”. Click again to confirm and finish the setup. This should take you to a video feed of the two cameras as well as an interface to choose a soundfont.
Once the setup is completed, you should be able to play the piano.

Notes are considered “played” when your finger is above the note in the top-down view and touching the table in the front view. A synthesia bar will appear in the top-down video feed above the note currently being played

You can click on a different soundfont to change the sound the piano plays (the default is Piano 1).

### Requirements:
| Requirement | Notes |
| --- | --- |
| [Python3](https://www.python.org/) | Version 3.12 |
| 2 External Webcams | We recommend [Iriun Webcam](https://iriun.com/) |

To install the necessary Python dependencies, run:
```console
$ pip install -r requirements.txt
```

It is highly recommended to print out the file “SingleOctavePiano.pdf” several times and then cutting and taping the pages together. This allows Pianable to more accurately map a piano and for the user to more accurately see what they are playing.

### Credits:
ZFont by Zalka downloaded from musical-artifacts.com



