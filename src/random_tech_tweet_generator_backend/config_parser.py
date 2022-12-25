import re
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Union

import yaml


class CategoryIdentifier:
    def __init__(self, config_file: Union[Path, str]) -> None:
        if config_file is None:
            config_file = Path(__file__).parent.parent.parent / "assets" / "watchlist.yml"
        self.config_file = config_file

    @cached_property
    def users(self) -> Dict[str, Any]:
        with open(self.config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data

    def get_category(self, username: str, text: str):
        user_categories = self.users[username]

        for category in user_categories:
            if re.search(category["category_regex"], text, re.IGNORECASE):
                return category["category_name"]
        return "Others"
