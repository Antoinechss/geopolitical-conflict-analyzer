from storage.refresh_db import refresh_db
from storage.db import get_connection
import json


def show_first_rows(n=5):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT %s;", (n,))
            rows = cur.fetchall()
            for row in rows:
                print(row)
    conn.close()


if __name__ == '__main__':
    refresh_db()
    show_first_rows()
    with open("clean_posts.json", "w", encoding="utf-8") as f:
        json.dump(clean_posts, f, ensure_ascii=False, indent=2)
    print("Saved clean posts to clean_posts.json")
