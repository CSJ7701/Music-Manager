import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
import requests
import pandas as pd
import numpy as np
import PIL
from PIL import Image
from io import BytesIO

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
        Recscreen(self.main, self.db)
        
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


class Recscreen:
    def __init__(self, parent_frame, db):
        self.parent=parent_frame
        self.db=db
        self.RecVar="Track"
        self.api_key="d7e9aa7857ff7959f8d325245a59a263"
        
        self.search_frame=ctk.CTkFrame(self.parent)
        self.search_frame.pack(padx=10, pady=10, fill="both")

        self.rec_frame=ctk.CTkFrame(self.parent)
        self.rec_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.rec_tree=ttk.Treeview(self.rec_frame, columns=('Name', 'Match'))
        self.rec_tree.heading('Name', text="Name")
        self.rec_tree.heading('Match', text="Match")
        self.rec_tree['show']='headings'
        self.rec_tree.bind("<<TreeviewSelect>>", self.match_treeview)
        self.rec_tree.pack(fill="both", expand=True, side="left")
        # Treeview on select item, update image and info frame

        self.rec_info_frame=ctk.CTkFrame(self.rec_frame, width=200)
        self.rec_info_frame.pack(side="right", fill="y", expand=False)
        self.rec_info_image_frame=ctk.CTkFrame(self.rec_info_frame)
        self.rec_info_info_frame=ctk.CTkFrame(self.rec_info_frame)
        self.rec_info_image_frame.pack(side="top", fill="both", expand=True)
        self.rec_info_info_frame.pack(side="top", fill="both", expand=True)


        self.tree=ttk.Treeview(self.search_frame, columns=('Artist', 'Title', 'Album', 'Genre', 'MB Id'), height=5)
        self.tree.heading('Title', text='Track')
        self.tree.column('Title', width=100)
        self.tree.heading('Artist', text='Artist')
        self.tree.column('Artist', width=70)
        self.tree.heading('Album', text='Album')
        self.tree.column('Album', width=100)
        self.tree.heading('Genre', text='Genre')
        self.tree.column('Genre', width=70)
        self.tree.heading('MB Id', text='MB Id')
        self.tree.column('MB Id', width=200)
        self.tree['show']='headings'
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        self.entry_frame=ctk.CTkFrame(self.search_frame)
        self.entry_frame.pack(side="top", fill="x", expand=True)
        self.entry_frame_bottom=ctk.CTkFrame(self.search_frame)
        self.entry_frame_bottom.pack(side="top", fill="x", expand=True)
        self.auth_entry=ctk.CTkEntry(self.entry_frame, placeholder_text="Author")
        self.track_entry=ctk.CTkEntry(self.entry_frame, placeholder_text="Track")
        self.album_entry=ctk.CTkEntry(self.entry_frame_bottom, placeholder_text="Album")
        self.genre_entry=ctk.CTkEntry(self.entry_frame_bottom, placeholder_text="Genre")
        self.auth_entry.pack(padx=5,pady=10, side="left", fill="x", expand=True)
        self.track_entry.pack(padx=5,pady=10, side="left", fill="x", expand=True)
        self.album_entry.pack(padx=5,pady=10, side="left", fill="x", expand=True)
        self.genre_entry.pack(padx=5,pady=10, side="left", fill="x", expand=True)
        self.auth_entry.bind('<KeyRelease>', self.search_db)
        self.track_entry.bind('<KeyRelease>', self.search_db)
        self.album_entry.bind('<KeyRelease>', self.search_db)
        self.genre_entry.bind('<KeyRelease>', self.search_db)
        self.button_frame=ctk.CTkFrame(self.search_frame)
        self.button_frame.pack(fill="none", expand=False)
        
        self.rec_type_box=ctk.CTkComboBox(self.button_frame, values=["Track", "Album", "Artist"], command=self.rec_type)
        self.rec_type_box.pack(padx=10, pady=10, side="left")
        self.rec_button=ctk.CTkButton(self.button_frame, text="Recommend "+self.RecVar, command=self.get_recs)
        self.rec_button.pack(padx=10, pady=10, side="left")
        self.search_db()


    def search_db(self, event=None):
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

    def get_selected_items(self):
        selected=[]
        if self.tree.selection():
            for item in self.tree.selection():
                values=self.tree.item(item, 'values')
                selected.append(values)
        return selected

    def rec_type(self, choice):
        self.RecVar=choice

    def get_recs(self):
        type=self.RecVar
        selection=self.get_selected_items()
        list=[]
        cursor=self.db.conn.cursor()
        if not selection:
            cursor.execute(f"SELECT artist,track_title,album,genre,mb_track_id from Music")
            selection=cursor.fetchall()
        for item in selection:
            if type == "Artist":
                results=self.get_artist_recs(item)
                filter=cursor.execute("SELECT artist FROM Music")
            elif type == "Track":
                results=self.get_track_recs(item)
                filter=cursor.execute("SELECT track_title FROM Music")
            elif type == "Album":
                results=self.get_album_recs(item)
                filter=cursor.execute("SELECT album FROM Music")
            else:
                print("Error: Wrong Recommendation Type")
                results=[]
            if results:
                list.append(pd.DataFrame(results, columns=['name', 'match', 'mbid']))
            else:
                print("Error getting recommendations")
                return None
        recommendations=pd.concat(list, ignore_index=True)
        recommendations=recommendations[~recommendations['name'].isin(filter)]
        recommendations['match']=pd.to_numeric(recommendations['match'],errors='coerce')
        duplicates=recommendations[recommendations.duplicated(subset='name', keep=False)]
        if not duplicates.empty:
            merged_duplicates=duplicates.groupby('name')['match'].apply(np.sum).reset_index()
            recommendations=recommendations.drop_duplicates(subset='name', keep=False)
            recommendations=pd.concat([recommendations, merged_duplicates], ignore_index=True)
            recommendations=recommendations.sort_values(by='match', ascending=False)
        data=[tuple(row) for row in recommendations.values]
        for row in data:
            self.rec_tree.insert("", "end", values=row)
        # Fill treeview instead
        # Add extra info to dataframe
        
    def process_item(self, item):
        artist=item[0]
        track=item[1]
        album=item[2]
        genre=item[3]
        mbid=item[4]
        return artist, track, album, genre, mbid

    def lastfm_query(self, url):
        response=requests.get(url)
        if response.status_code==200:
            return response
        else:
            print("No recommendations found")
    
    def get_artist_recs(self, item):
        print(f"Artists for: {item}")
        artist, _, _, _, _=self.process_item(item)
        url=f"http://ws.audioscrobbler.com/2.0/?method=artist.getSimilar&artist={artist}&api_key={self.api_key}&format=json"
        data=self.lastfm_query(url)
        data=data.json()
        if 'similarartists' in data:
            artists=data['similarartists']['artist']
            for artist in artists:
                del artist["streamable"]
            return artists
        else:
            print(f"No recommendations for {artist}")

    def get_track_recs(self, item):
        print(f"Tracks for: {item}")
        artist, track, _, _, _=self.process_item(item)
        url=f"http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist={artist}&track={track}&api_key={self.api_key}&format=json"
        data=self.lastfm_query(url)
        print(url)
        data=data.json()
        if 'similartracks' in data:
            if 'track' in data['similartracks']:
                tracks=data['similartracks']['track']
                for track in tracks:
                    del track['streamable']
                return tracks
            else:
                print(f"No recommendations for {track}")
        else:
            print(f"Track not found: {track}")

    def get_album_recs(self, item):
        print(f"Albums for: {item}")
        artist, track, album, genre, mbid=self.process_item(item)

    def match_treeview(self, event):
        for widget in self.rec_info_image_frame.winfo_children():
            widget.destroy()
        selected_item=self.rec_tree.selection()
        if len(selected_item) == 1:
            mbid=self.rec_tree.item(selected_item, "values")[2]
        else:
            print("Too Many Items Selected")
            return None
        print(mbid)
        artist, album, genres, cover=self.get_recommendation_info(mbid)
        response=requests.get(cover)
        data=response.content
        img=None
        try:
            img=Image.open(BytesIO(data))
        except PIL.UnidentifiedImageError as e:
            print(f"No image found at {cover}:\n{e}")
        if img:
            photo=ctk.CTkImage(img, size=(150,150))
            label=ctk.CTkLabel(self.rec_info_image_frame, image=photo, text="", width=100)
            label.pack(padx=10, pady=10, fill="both", expand=True)
        else:
            label=ctk.CTkLabel(self.rec_info_image_frame, text="No Image Found")
            label.pack(padx=10, pady=10)
        

    def get_recommendation_info(self, mbid):
        mb_url=f"https://musicbrainz.org/ws/2/recording/{mbid}?inc=artists+releases+genres&fmt=json"
        mb_response=requests.get(mb_url)
        if mb_response.status_code == 200:
            mb_data=mb_response.json()
            album_name=mb_data['releases'][0]['title']
            album_id=mb_data['releases'][0]['id']
            artist_name=mb_data['artist-credit'][0]['artist']['name']
            genres=[]
            for genre in mb_data['genres']:
                genres.append(genre["name"])
            if album_id:
                ca_url=f"https://coverartarchive.org/release/{album_id}/front"
            else:
                ca_url=None
        else:
            print("Music Brainz recording not found")
            return None, None, None, None
        return artist_name, album_name, genres, ca_url

        
    # Default is to recommend based on entire library.
    # Small window at the top ot let you limit what we recommend based on (search, then multiselect, select all button)
    # Larger window at bottom that shows card view for recommendations, pulling title, artist, genre, and album cover art from spotify/musicbrainz
    # Can add to "recommendations.txt" - spotify link - for mass download


class Download:
    def __init__(self):
        print("Downloads")

    # Can search. Search results show title, artist, and album art
    # Can also download directly from recommendations.txt or downloads.txt
        # should be able to list what's currently in the txt file

        

        

