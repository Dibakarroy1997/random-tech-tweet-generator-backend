import json
from pathlib import Path

from database import TweetDatabase

if __name__ == "__main__":
    db_root = Path(__file__).parent.parent.parent
    try:
        db = TweetDatabase(db_root / "db" / "tweets.db")
        tweets = db.get_all()
    finally:
        db.close()

    json_data = {"metadata": {"entries": len(tweets)}, "tweets": tweets}

    with open(db_root / "db" / "tweets.json", "w") as f:
        json.dump(json_data, f, indent=4)
