"""
Run this program after main.py
"""

import os
import sys
import pickle
import argparse

# PIL
from PIL import Image

# pandas
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_DIR, os.pardir, os.pardir))

# enlighten
from enlight.ai.infer import StyleInferer
from enlight.utils import RENDER_STYLE

# sklearn
from sklearn import svm
from sklearn.multioutput import MultiOutputClassifier

def parse_args():
    parser = argparse.ArgumentParser(description="Train scripture quote model.")
    parser.add_argument("--output-fpath", default="output", help="Output folder.")
    parser.add_argument("--images-fpath", help="Default images folder", default="images")
    parser.add_argument("--fonts-fpath", default="fonts", help="Folder container valid fonts.")
    parser.add_argument("--test-data-csv", default="enlighten.csv", help="CSV containing test data.")
    return parser.parse_args()

def load_images(args, data):
    return [Image.open(os.path.join(args.images_fpath, fpath)) for fpath in data["image"]]

def calculate_accuracy(predictions, test_data):
    label_predictions = [RENDER_STYLE[p[0]] for p in predictions]

    test_labels = test_data[["image", "style"]]
    label_pred = test_labels.copy()
    label_pred.loc[:, "style"] = label_predictions

    print("\nPREDICTIONS")
    print(label_pred)
    common_data = pd.merge(label_pred, test_labels)
    print("\nCOMMON")
    print(common_data)
    accuracy = len(common_data) / len(test_labels)
    print(f"Accuracy: {accuracy}")
    return accuracy


def model_function(model_name):
    def f(func):
        filename = model_name + ".pickle"

        def wrapper(*args, **kwargs):
            if os.path.exists(filename):
                print(f"Loading {filename}")
                with open(filename, "r+b") as f:
                    return pickle.load(f)

            print(f"Generating {filename}")
            result = func(*args, **kwargs)

            with open(filename, "w+b") as f:
                pickle.dump(result, f)
            return result
        return wrapper
    return f


@model_function("svm_train_in_group_only")
def svm_train_in_group_only(args, inferer, train_data, test_data):
    model = inferer.train(load_images(args, train_data), [], [], train_data["style"], None)
    predictions = inferer.infer(load_images(args, test_data), [], [], model)
    calculate_accuracy(predictions, test_data)
    return model

@model_function("svm_poly_train_in_group_only")
def svm_poly_train_in_group_only(args, inferer, train_data, test_data):
    clf = svm.SVC(decision_function_shape="ovo", kernel="poly")
    multilabel_classifier = MultiOutputClassifier(clf, n_jobs=-1)
    model = inferer.train(load_images(args, train_data), [], [], train_data["style"], multilabel_classifier)
    predictions = inferer.infer(load_images(args, test_data), [], [], model)
    calculate_accuracy(predictions, test_data)
    return model

@model_function("svm_linear_train_in_group_only")
def svm_linear_train_in_group_only(args, inferer, train_data, test_data):
    clf = svm.SVC(decision_function_shape="ovo", kernel="linear")
    multilabel_classifier = MultiOutputClassifier(clf, n_jobs=-1)
    model = inferer.train(load_images(args, train_data), [], [], train_data["style"], multilabel_classifier)
    predictions = inferer.infer(load_images(args, test_data), [], [], model)
    calculate_accuracy(predictions, test_data)
    return model

def main():
    args = parse_args()

    training_data = {}
    with open("look_table.pickle", "r+b") as f:
        training_data = pickle.load(f)

    expanded = [(*k.split(".jpg"), v) for k, v in training_data.items()]
    expanded = [(e[0] + ".jpg", *e[1:]) for e in expanded]

    test_data = pd.read_csv(args.test_data_csv)
    df = pd.DataFrame.from_records(expanded, columns=["image", "style", "in"])

    # Comment out to save time
    svm_train_in_group_only(args, StyleInferer(RENDER_STYLE[:-1]), df.copy(), test_data)
    svm_poly_train_in_group_only(args, StyleInferer(RENDER_STYLE[:-1]), df.copy(), test_data)
    svm_linear_train_in_group_only(args, StyleInferer(RENDER_STYLE[:-1]), df.copy(), test_data)

if __name__ == "__main__":
    main()
