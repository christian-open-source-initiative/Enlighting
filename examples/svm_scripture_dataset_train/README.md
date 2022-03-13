# SVM Quotable Scripture Training Scripts

An example project on how to use to show how a model can be trained and used as part of the Enlighten scripts.
These scripts train on the position of the quote relative to the image. `BEiT` is used as feature extractors.

## Usage

First, you will need a set of images to train on. These images can be from many repository so long as they are images that you
desire for the inspirational quotes.

Then run the following script

> generate_data.py --images-fpath <path_to_images> --fonts-fpath <path_to_your_fonts>

By default `generate_data.py` produces fake text. However for more context-aware dataset, a `converter.py` is provided which can fetch
Bible verses as training data. It will generate an `enlighten.csv` which can be fed to `generate_data.py` instead as the text generator.

```
A list of images have been generated at:
C:\Users\starw\AppData\Local\Temp\tmp9rwt09s9
Delete the ones you don't want.
Type y, e to exit:
```

A temporary folder of images will be generated from `generate_data.py` and it is your job to delete all images that don't work.
Then close the folder and type `y`.

The program will do a diff to determine which images worked and which did not. At which point a `look_table.pickle` is generated.
The program will continue to loop until you quit. You can do this process as many times as you like, as `look_table.pickle` will be appended.

Once complete, run the following in the same folder to train the AI:

> train.py

`train.py` to train the network model on the dataset. It will train three different SVM models and output their accuracy (if you give it testing
data.)

You can optionally comment out SVMs kernels that don't make sense for your dataset:

```python
svm_train_in_group_only(...)
svm_poly_train_in_group_only(...)
svm_linear_train_in_group_only(...)
```

That's it! From our emperical testing, convergence on 700 images took about 1000 data points, roughly an hour of hand labeling using the `BEiT` feature extractor.

## Q/A

### What if I want to modify the feature extractor?

By default, enlighten uses a transformer as a feature extractor via the `StyleInferer`. Since this was sufficiently good for our use-case, no code is created
for accepting other `StyleInferer` class instances. Please file an issue and we can work out a solution to extend feature extraction. A workaround
would be to modify `StyleInferer` directly for your extractor.

### Why was `BEiT` selected as feature extractor?

No particular reason. It was mainly a POC and it turned out to work for our use-case. Better more efficient methods can probably be found via
segementation or visual queues. However due to ease of access to downloading and using `BEiT`, this was used instead.

### What if I want to use something other than an SVM?

Similar to the "What if I want to modify the feature extractor?" please file an issue. A work around is to modify `StyleInferer` to  use your
custom AI model.

### I want to re-use the generated training set (`look_table.pickle`) but it doesn't seem to work?

`look_table.pickle` is re-usable as long as your image dataset is the same or a super set as it hashes by image name. To transfer your `look_table.pickle`
consider loading and modify keys to remove outdated image names.
