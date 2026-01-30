import json
import uuid
from preprocessing.text_cleaner import process_raw_text


def preprocess_batch(batch: list):
    processed = []
    for idx, post in enumerate(batch, start=1):
        post["event_id"] = str(uuid.uuid4())
        text_clean, hashtags, emojis = process_raw_text(post['text_raw'])
        post["text_processed"] = text_clean
        post["hashtags"] = json.dumps(hashtags)
        post["emojis"] = json.dumps(emojis)
        processed.append(post)
    return processed

