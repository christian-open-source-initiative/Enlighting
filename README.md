# Quote Image Generator

This program converts a list of CSV quotes into image backgrounds. Useful for mass producing quotes into motivational images.
The project was written roughly in a span of a weekend's worth of work. As a result, the codebase is suboptimal but folks were interested in looking at the source code.
There are some optimizations that can still be done. See [optimizations](#Optimizations) sections for more details.

There are no commandline options. Direct modification of the program is required.

## How to Use

Supply a bunch of `.png` or `.jpg` images into the `images` folder inside the program root.
Provide a `input.csv` file where there is atleast two columns: one for the name of the person who spoke the quote and the quote itself.
Then first run:

> python main.py

The program will then generate a `blurred` folder for images compiled with a blur effect and then a bunch of html files should be generated inside `render_html`.
You can then open up each html file to do some final edits before converting them into `jpg` images. A useful `sample.html` is also generated inside `render_html` which 
contains all rendered quotes on the same page for easier review of the generated data. (Note that `sample.html` will not be converted into an image.)

Once rendered html is reviewed and potentially modified run the following:

> python convert.py

This will take some time but afterwards your html files should be generated into `jpg` images inside the `img_render` folder.

## Platform Support

Tested on Windows 10 should work on Linux.
## Setup

> pip install -r requirements.txt

Makesure to have `wkhtmltopdf` installed and available inside your `PATH` variable.
Binaries and more instructions can be found at [wkhtmltopdf.org](https://wkhtmltopdf.org/).

## Optimizations

- Optimize smarter image selection, right now we randomly sample images until a image with height constraints matches the text.
- Better usage of `images` and `blurred` directories. Right now they are just copied into the `render_html` folder everytime.
- Use commandline options instead of modifying variables.