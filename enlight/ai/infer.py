"""
Infers a given feature.1
"""

import torch

from transformers import BeitFeatureExtractor, BeitModel

class StyleInferer:
    def infer_style(img, quote_src, quote):
        """
        Infers a style given image metadata.
        """
        # feature extract
        feature_extractor = BeitFeatureExtractor.from_pretrained("microsoft/beit-base-patch16-224-pt22k")
        inputs = feature_extractor(img.convert("RGB"), return_tensors="pt")

        model = BeitModel.from_pretrained("microsoft/beit-base-patch16-224-pt22k")
        with torch.no_grad():
            outputs = model(**inputs).last_hidden_state
            print(outputs)
            print(outputs.shape)
            exit(1)
