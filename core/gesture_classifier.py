import json

import joblib


class GestureClassifier:
    def __init__(self, model_path, label_map_path):
        self.model_path = model_path
        self.label_map_path = label_map_path

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Chua tim thay model: {self.model_path}. Hay chay train_model.py truoc."
            )
        if not self.label_map_path.exists():
            raise FileNotFoundError(
                f"Chua tim thay label map: {self.label_map_path}. Hay chay train_model.py truoc."
            )

        self.model = joblib.load(self.model_path)
        self.id_to_label = self.load_id_to_label()
        self.expected_feature_count = self.get_expected_feature_count()

    def load_id_to_label(self):
        with self.label_map_path.open("r", encoding="utf-8") as file:
            label_to_id = json.load(file)
        return {int(idx): label for label, idx in label_to_id.items()}

    def get_expected_feature_count(self):
        if hasattr(self.model, "n_features_in_"):
            return int(self.model.n_features_in_)

        classifier = getattr(self.model, "named_steps", {}).get("classifier")
        if classifier is not None and hasattr(classifier, "n_features_in_"):
            return int(classifier.n_features_in_)

        return None

    def predict(self, features):
        pred_id = int(self.model.predict(features)[0])
        return self.id_to_label.get(pred_id, f"class_{pred_id}")
