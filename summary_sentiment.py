"""Print sentiment summary from the SQLite database."""
import sqlite3, os
path = 'sentiment/sentiment.sqlite'
if not os.path.exists(path):
    print('no sentiment data yet')
    exit(0)
conn = sqlite3.connect(path)
for t in ['fng','gdelt_tone','reddit_posts']:
    try:
        n = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        print(f'- {t}: {n} rows')
    except Exception as e:
        print(f'- {t}: {e}')
conn.close()
