"""
Infers a given feature.1
"""

import torch

# hugging_face
from transformers import BeitFeatureExtractor, BeitModel

# sklearn
from sklearn import svm
from sklearn.multioutput import MultiOutputClassifier

class StyleInferer:
    """
    Basic SVM based inferer for images using
    models from HG for feature extraction.
    """

    def __init__(self, classes):
        self.classes = classes
        self.classes_encoded = {k: i for i, k in enumerate(classes)}

    def calculate_image_feature_vector(self, img):
        # feature extract
        feature_extractor = BeitFeatureExtractor.from_pretrained("microsoft/beit-base-patch16-224-pt22k")
        inputs = feature_extractor(img.convert("RGB"), return_tensors="pt")

        model = BeitModel.from_pretrained("microsoft/beit-base-patch16-224-pt22k")
        with torch.no_grad():
            return model(**inputs).last_hidden_state

    def train(self, imgs, quote_srcs, quotes, styles):
        """Trains the given style."""
        clf = svm.SVC(decision_function_shape="ovo")
        multilabel_classifier = MultiOutputClassifier(clf, n_jobs=-1)
        X = [self.calculate_image_feature_vector(img) for img in imgs]
        Y = [self.classes_encoded[s] for s in styles]
        return multilabel_classifier.fit(X, Y)

    def infer(self, img, quote_src, quote, model):
        """
        Infers a style given image metadata.
        """
        return model.predict(self.calculate_image_feature_vector(img))
