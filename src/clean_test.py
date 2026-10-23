import sqlite3

c = sqlite3.connect("data/router.db")
c.execute("delete from cache where v like '%nemotron%'")
c.execute("delete from log where fallback = 1")
c.commit()
print("done")