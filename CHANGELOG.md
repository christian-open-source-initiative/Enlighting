# CHANGELOG: Enlighting
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

## v2.1.0

- Added collage mode to generate a collage of images for looking at multiple images.
- Fixed README typo.

## v2.0.0

- Added `auto` mode which supports AI models via `--ai-model-file`.
- Added `enlighten.ai` which containers data generators and infer classes.
- Added `tests` for testing data generators.
- Added `examples/svm_scripture_dataset_train` for AI training.
- Changed README to introduce AI changes.

## v1.0.0

- Added brandnew render engine using `Pillow`
- Changed CLI API. See `python enlighten.py --help` for more info.
- Removed old engine rendered.
- Removed `numpy` and `imgkit` requirements.

## v0.1.0

- Added working renderer using HTML and `wkhtmltopdf` backend.
