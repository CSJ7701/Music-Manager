import tkinter as tk
import customtkinter as ctk
from tkinter import ttk

class App(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db=db

        # Nav Bar
        self.NavBar=ctk.CTkFrame(self)
        self.NavBar.pack(side="left", fill="y", pady=10, padx=(10,0))

        ctk.CTkLabel(self.NavBar, text="Music Manager", font=("Helvetica", 20)).pack(side="top", pady=(60, 40), padx=20)
        ctk.CTkButton(self.NavBar, text="Home", command=self.showHome, height=40, corner_radius=30).pack(side="top", padx=10, pady=20)
        ctk.CTkButton(self.NavBar, text="Recommendations", command=self.showRecs, height=40, corner_radius=30).pack(side="top", padx=10, pady=20)
        

        # Main
        self.main=ctk.CTkFrame(self)
        self.main.pack(side="top",expand=True, fill="both", padx=10, pady=10)

        self.showHome()

    def showHome(self):
        self.showClear()
        Homescreen(self.main, self.db)

    def showRecs(self):
        self.showClear()
        print("Recs")

    def showClear(self):
        for widget in self.main.winfo_children():
            widget.destroy()


class Homescreen:
    def __init__(self, parent_frame, db):
        self.parent=parent_frame
        self.db=db
        home_label=ctk.CTkLabel(self.parent, text="Welcome", font=("Helvetica", 20))
        home_label.pack(pady=30)

        self.count_label=ctk.CTkLabel(self.parent, text=f"Songs: {self.count_songs()}   Albums: {self.count_albums()}   Artists: {self.count_artists()}")
        self.count_label.pack(side="top")

        self.search_frame=ctk.CTkFrame(self.parent)
        self.search_frame.pack(padx=20, pady=20, expand=True, fill="both")
        self.tree=ttk.Treeview(self.search_frame, columns=('Artist', 'Title', 'Album', 'Genre', 'MB Id'))
        self.tree.heading('Title', text='Track')
        self.tree.heading('Artist', text='Artist')
        self.tree.heading('Album', text='Album')
        self.tree.heading('Genre', text='Genre')
        self.tree.heading('MB Id', text='MB Id')
        self.tree['show']='headings'
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)
        self.auth_entry=ctk.CTkEntry(self.search_frame, placeholder_text="Author")
        self.track_entry=ctk.CTkEntry(self.search_frame, placeholder_text="Track")
        self.album_entry=ctk.CTkEntry(self.search_frame, placeholder_text="Album")
        self.genre_entry=ctk.CTkEntry(self.search_frame, placeholder_text="Genre")
        self.auth_entry.pack(padx=20,pady=10, side="left", fill="x", expand=True)
        self.track_entry.pack(padx=20,pady=10, side="left", fill="x", expand=True)
        self.album_entry.pack(padx=20,pady=10, side="left", fill="x", expand=True)
        self.genre_entry.pack(padx=20,pady=10, side="left", fill="x", expand=True)
        self.auth_entry.bind('<KeyRelease>', self.search)
        self.track_entry.bind('<KeyRelease>', self.search)
        self.album_entry.bind('<KeyRelease>', self.search)
        self.genre_entry.bind('<KeyRelease>', self.search)

        # Headings are out of order. Make sure this searches by more than just title (either add more search fields, or make the one field search everything
        

    def search(self, event=None):
        auth=self.auth_entry.get()
        track=self.track_entry.get()
        album=self.album_entry.get()
        genre=self.genre_entry.get()
        cursor=self.db.conn.cursor()
        query=("SELECT artist, track_title, album, genre,mb_track_id FROM Music WHERE 1=1")
        if auth:
            query+=f" AND artist like '%{auth}%'"
        if track:
            query+=f" AND track_title like '%{track}%'"
        if album:
            query+=f" AND album like '%{album}%'"
        if genre:
            query +=f" AND genre like '%{genre}%'"
        cursor.execute(query)
        results=cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for record in results:
            self.tree.insert('', 'end', values=record)

    def count_songs(self):
        cursor=self.db.conn.cursor()
        cursor.execute("SELECT COUNT (*) FROM Music")
        result=cursor.fetchone()
        return result[0]

    def count_albums(self):
        cursor=self.db.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT album) FROM Music")
        result=cursor.fetchone()
        return result[0]

    def count_artists(self):
        cursor=self.db.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT artist) FROM Music")
        result=cursor.fetchone()
        return result[0]


class Recs:
    def __init__():
        print("RECS")

    # Default is to recommend based on entire library.
    # Small window at the top ot let you limit what we recommend based on (search, then multiselect, select all button)
    # Larger window at bottom that shows card view for recommendations, pulling title, artist, genre, and album cover art from spotify/musicbrainz
    # Can add to "recommendations.txt" - spotify link - for mass download


class Download:
    def __init__():
        print("Downloads")

    # Can search. Search results show title, artist, and album art
    # Can also download directly from recommendations.txt or downloads.txt
        # should be able to list what's currently in the txt file

        

        

