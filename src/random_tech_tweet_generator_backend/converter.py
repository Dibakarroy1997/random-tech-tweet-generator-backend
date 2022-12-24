import json
from pathlib import Path

from database import TweetDatabase

if __name__ == "__main__":
    root = Path(__file__).parent.parent.parent
    try:
        db = TweetDatabase(root / "db" / "tweets.db")
        tweets = db.get_all()
    finally:
        db.close()

    json_data = {"metadata": {"entries": len(tweets)}, "tweets": tweets}

    with open(root / "db.json", "w") as f:
        json.dump(json_data, f, indent=4)
