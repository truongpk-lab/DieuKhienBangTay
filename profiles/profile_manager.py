import json
from pathlib import Path

from .profile_schema import validate_profile


class ProfileManager:
    def __init__(self, config_dir=None):
        self.config_dir = (
            Path(config_dir)
            if config_dir is not None
            else Path(__file__).resolve().parent / "configs"
        )

    def config_path(self, profile_id):
        return self.config_dir / f"{profile_id}.json"

    def load_profile(self, profile_id):
        path = self.config_path(profile_id)
        if not path.exists():
            raise FileNotFoundError(f"Khong tim thay profile '{profile_id}': {path}")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return validate_profile(data)

    def available_profile_ids(self):
        return sorted(path.stem for path in self.config_dir.glob("*.json"))
