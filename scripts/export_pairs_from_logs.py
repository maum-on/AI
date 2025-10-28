import csv, os, sqlite3, json
from datetime import datetime

DB = os.getenv("DATABASE_URL", "sqlite:///./app.db")
assert DB.startswith("sqlite"), "현재 스크립트는 sqlite만 지원"

PATH = DB.split("///",1)[1]

def main():
    conn = sqlite3.connect(PATH)
    cur = conn.cursor()
    cur.execute("SELECT text, reply_normal, valence, emotions, summary FROM diary_logs ORDER BY id DESC")
    rows = cur.fetchall()
    out_path = f"exports/pairs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    os.makedirs("exports", exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["input_text","target_reply","valence","emotions","summary"])
        for t, r, v, e, s in rows:
            try:
                if isinstance(e, str) and e and e.strip().startswith("["):
                    e2 = ",".join(json.loads(e))
                else:
                    e2 = ",".join(e or [])
            except Exception:
                e2 = ""
            if t and r:
                w.writerow([t, r, v or "", e2, s or ""])
    print("✅ export:", out_path)

if __name__ == "__main__":
    main()
