"""
Converts bible source csv to enlighten csv.
"""

import re
import os
import sys
from subprocess import run, PIPE

import pandas as pd

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SAMPLE_DIR, "bible"))

# ext
import bible

RE_FORMAT = r"(.+) \((\w+)\)"

def fetch_verse(verse: bible.Verse):
    passage_formatted = verse.format("B C:V")
    cmd = [
        "python",
        os.path.join("bible-fetch", "bible"),
        f"{passage_formatted}",
        "--version",
        verse.translation,
        "--ascii"
    ]
    return run(cmd, stdout=PIPE, cwd=SAMPLE_DIR).stdout

def convert(input_fpath: str, output_fpath: str) -> pd.DataFrame:
    """
    Converts a csv file of "image", "verse", and "style" to
    a csv that enlighten can parse. Uses APIs to fetch verses.
    """
    if os.path.exists(output_fpath):
        print("Converted file already exists. Remove to re-fetch.")
        return pd.read_csv(output_fpath)

    bible_csv = pd.read_csv(input_fpath)

    verse_column = 1
    bible_passage = []
    for _, row in bible_csv.iterrows():
        passage = row[verse_column]
        parsed = re.match(RE_FORMAT, passage)
        assert parsed is not None, "Invalid formatting of bible passage."
        assert len(parsed.group(1)) > 0, "Must have valid passage."
        assert len(parsed.group(2)) > 0, "Must have valid translation."

        verse_format = bible.Verse(parsed.group(1))
        verse_format.translation = parsed.group(2)

        print(f"Fetching: {verse_format.format('B C:V')}")
        result = fetch_verse(verse_format)


        if len(result.strip()) == 0:
            print(f"Translation does not exist? {verse_format.translation}")
            verse_format.translation = "ESV"
            result = fetch_verse(verse_format)
            assert len(result.strip()) != 0, "Invalid passage given."

        bible_passage.append(result.decode("utf-8").replace("\r\n", "\n"))

    bible_csv.loc[:, "quote"] =  bible_passage
    bible_csv.rename(columns={"verse": "quote_src"}, inplace=True)
    print(bible_csv)
    bible_csv.to_csv(output_fpath, index=False, columns=["image", "quote_src", "quote", "style"])

    return bible_csv

if __name__=="__main__":
    convert("example.csv", "processed.csv")
