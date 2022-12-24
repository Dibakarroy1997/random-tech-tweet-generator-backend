import json
import random
import sqlite3
from functools import cached_property
from typing import Any, Dict, List


class TweetDatabase:
    def __init__(self, db_name: str) -> None:
        self.conn = sqlite3.connect(db_name)

        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS tweets (
  id INTEGER, username TEXT, 
  tweet_id TEXT PRIMARY KEY, tweet_text TEXT, 
  tweet_media TEXT, tweet_conversation_id TEXT, 
  tweet_type TEXT, created_at DATE
)"""
        )
        self.conn.commit()

    def insert(
        self,
        username: str,
        tweet_id: int,
        tweet_text: str,
        tweet_media: List[str],
        tweet_conversation_id: int,
        tweet_type: int,
        created_at: str,
    ) -> None:
        print(
            f"""Inserting:
{username = }
{tweet_id = }
{tweet_text = }
{tweet_media = }
{tweet_conversation_id = }
{tweet_type = }
{created_at = }
"""
        )

        self.cursor.execute(
            """INSERT INTO tweets (
  id, username, tweet_id, tweet_text, 
  tweet_media, tweet_conversation_id, 
  tweet_type, created_at
) 
VALUES 
  (
    (
      SELECT 
        IFNULL(
          MAX(id), 
          0
        ) + 1 
      FROM 
        tweets
    ), 
    ?, 
    ?, 
    ?, 
    ?, 
    ?, 
    ?, 
    ?
  )""",
            (username, tweet_id, tweet_text, json.dumps(tweet_media), tweet_conversation_id, tweet_type, created_at),
        )
        self.conn.commit()

    def get_last_tweet_for_user(self, username: str) -> Dict[str, Any]:
        self.cursor.execute(
            """SELECT 
  * 
FROM 
  tweets 
WHERE 
  username = ? 
  AND tweet_id = (
    SELECT 
      MAX(tweet_id) 
    FROM 
      tweets 
    WHERE 
      username = ?
  )""",
            (username, username),
        )
        row = self.cursor.fetchone()

        if not row:
            return None

        headers = [description[0] for description in self.cursor.description]

        return dict(zip(headers, row))

    @cached_property
    def conversation_ids(self) -> List[int]:
        self.cursor.execute(
            """SELECT 
  DISTINCT tweet_conversation_id 
FROM 
  tweets"""
        )
        rows = self.cursor.fetchall()

        return [row[0] for row in rows]

    def get_random_tweet_thread(self) -> List[Dict[str, Any]]:
        random_conversation_id = random.choice(self.conversation_ids)
        self.cursor.execute(
            """SELECT 
  * 
FROM 
  tweets 
WHERE 
  tweet_conversation_id = ?""",
            (random_conversation_id,),
        )
        rows = self.cursor.fetchall()

        print(f"{rows = }")
        print(json.dumps(rows))

        data = [{column: row[i] for i, column in enumerate(self.cursor.description)} for row in rows]

        return data

    def get_all(self) -> List[Dict[str, any]]:
        self.cursor.execute(
            """SELECT 
  * 
FROM 
  tweets"""
        )
        rows = self.cursor.fetchall()

        headers = [description[0] for description in self.cursor.description]

        return [dict(zip(headers, values)) for values in rows]

    def close(self):
        self.conn.close()
