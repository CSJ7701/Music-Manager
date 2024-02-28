from database import Database
from app import App

db_file="music_database.db"
DB=Database(db_file)
DB.connect()
app=App(DB)
app.mainloop()
