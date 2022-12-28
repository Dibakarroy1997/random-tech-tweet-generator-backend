import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Union

import tweepy
from config_parser import CategoryIdentifier
from database import TweetDatabase


class TweetScrapper:
    def __init__(self, bearer: str, config_file: Union[Path, str] = None, db_file: Union[Path, str] = None) -> None:
        self.client = tweepy.Client(
            bearer,
            return_type=dict,
            wait_on_rate_limit=True,
        )
        self.category_identifier = CategoryIdentifier(config_file)
        if db_file is None:
            db_file = Path(__file__).parent.parent.parent / "db" / "tweets.db"
        self.db_file = db_file

    def get_tweet_data_for_db(self, tweet_id: int) -> Dict[str, Any]:
        print(f"Getting information for tweet with id {tweet_id}")
        response = self.client.get_tweet(
            tweet_id,
            tweet_fields=["conversation_id", "attachments", "created_at"],
            expansions=["attachments.media_keys", "author_id"],
            media_fields=["url", "alt_text", "duration_ms", "preview_image_url", "public_metrics", "variants"],
        )

        medias = []

        for media in response.get("includes").get("media", []):
            if media["type"] == "photo":
                medias.append(media["url"])
            elif media["type"] in ["video", "animated_gif"]:
                variants = media["variants"]
                sorted_variants = sorted(variants, key=lambda x: x.get("bit_rate", 0))
                medias.append(sorted_variants.pop()["url"])

        username = response.get("includes").get("users")[0]["username"]
        tweet_text = response["data"]["text"]

        return {
            "username": username,
            "tweet_type": self.category_identifier.get_category(username=username, text=tweet_text),
            "tweet_id": tweet_id,
            "tweet_text": tweet_text,
            "tweet_conversation_id": response["data"]["conversation_id"],
            "created_at": response["data"]["created_at"],
            "tweet_media": medias,
        }

    def insert_into_tweet_db_for_user_using_api(self, username: str) -> None:
        try:
            db = TweetDatabase(self.db_file)
            last_tweet = db.get_last_tweet_for_user(username)
            last_tweet_id = None if last_tweet is None else last_tweet.get("tweet_id")
            user_data = self.client.get_user(username=username)
            paginator = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_data["data"]["id"],
                max_results=100,
                exclude=["replies", "retweets"],
                since_id=last_tweet_id,
            )

            for tweet in paginator.flatten(limit=3200):
                db.insert(**self.get_tweet_data_for_db(tweet["id"]))
        finally:
            db.close()

    def update_existing_tweet_db_for_user_using_api(self) -> None:
        try:
            db = TweetDatabase(self.db_file)
            tweets = db.get_all()

            for tweet in tweets:
                tweet_data = self.get_tweet_data_for_db(tweet["tweet_id"])
                db.update(
                    tweet_id=tweet_data["tweet_id"],
                    tweet_media=tweet_data["tweet_media"],
                    tweet_type=tweet_data["tweet_type"],
                )
        finally:
            db.close()

    def update_tweet_db_for_user_using_json(self, username: str) -> None:
        try:
            db = TweetDatabase(self.db_file)
            last_tweet = db.get_last_tweet_for_user(username)
            tweet_json_file = Path(__file__).parent.parent.parent / "assets" / f"{username}.json"

            if not tweet_json_file.exists():
                print(f"No {tweet_json_file} found. Please try updating using API...")
                return

            tweets = json.loads(tweet_json_file.read_text())
            skip_existing_json_entry = True

            for tweet in tweets:
                if (
                    last_tweet
                    and str(tweet["data"]["id"]) != str(last_tweet.get("tweet_id"))
                    and skip_existing_json_entry
                ):
                    continue
                if last_tweet and str(tweet["data"]["id"]) == str(last_tweet.get("tweet_id")):
                    skip_existing_json_entry = False
                    last_tweet = None
                    continue

                db.insert(**self.get_tweet_data_for_db(tweet["data"]["id"]))
        finally:
            db.close()


if __name__ == "__main__":
    twitter_api_bearer_token = os.environ.get("TWITTER_API_BEARER_TOKEN")

    if twitter_api_bearer_token is None:
        raise ValueError("A valid Twitter API key is required!")

    scrapper = TweetScrapper(bearer=twitter_api_bearer_token)

    if len(sys.argv) < 2:
        raise SystemExit("Need at least 1 argument i.e. 'new' or 'update'")

    argument = sys.argv[1].strip().lower()
    if argument == "new":
        category_identifier = CategoryIdentifier(None)
        for user in category_identifier.users.keys():
            print(f"Scrapping tweets for @{user}...")
            scrapper.insert_into_tweet_db_for_user_using_api(user)
    elif argument == "update":
        scrapper.update_existing_tweet_db_for_user_using_api()
    else:
        raise SystemExit("Only support new or update")
