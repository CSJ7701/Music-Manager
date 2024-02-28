import sqlite3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import os
from tqdm import tqdm

class Database:
    def __init__(self, db_file):
        self.db_file=db_file
        self.conn=None
        self.connect()
        # self.process_directory("/home/csj7701/Remote/media/music")

    def connect(self):
        try:
            self.conn=sqlite3.connect(self.db_file)
        except sqlite3.error as e:
            print(f"Error connecting to database:\n--- {e}")

    def table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS Music(
                           filepath TEXT PRIMARY KEY,
                           artist TEXT,
                           album TEXT,
                           track_title TEXT,
                           genre TEXT,
                           mb_track_id TEXT)''')
        except sqlite3.Error as e:
            print(f"Error Creating Table:\n--- {e}")

    def in_database_p(self, filepath):
        try:
            cursor=self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Music WHERE filepath=?", (filepath,))
            count=cursor.fetchone()[0]
            return count>0
        except sqlite3.Error as e:
            print(f"Error Checking File:\n--- {e}")
        return False

    def file_metadata(self, filepath):
        try:
            audio=MP3(filepath, ID3=ID3)
            artist=audio.get('TPE1').text[0] if 'TPE1' in audio else None
            album=audio.get('TALB').text[0] if 'TALB' in audio else None
            track_title=audio.get('TIT2').text[0] if 'TIT2' in audio else None
            genre=audio.get('TCON').text[0] if 'TCON' in audio else None
            if audio.get('TXXX:MusicBrainz Release Track Id'):
                mb_track_id=audio.get('TXXX:MusicBrainz Release Track Id').text[0] if 'TXXX:MusicBrainz Release Track Id' in audio else None
            else:
                mb_track_id=None
            return artist, album, track_title, genre, mb_track_id
        except Exception as e:
            print(f"Error extracting metadata from {filepath}: {e}")
            return None, None, None, None, None

    def insert_metadata(self, filepath, artist, album, track_title, genre, mb_track_id):
        try:
            cursor=self.conn.cursor()
            print(f"Updating {filepath}\n--- {artist} - {track_title}({album}) ({mb_track_id})")
            cursor.execute('''INSERT INTO Music (filepath, artist, album, track_title, genre, mb_track_id)
                           VALUES (?, ?, ?, ?, ?)''', (filepath, artist, album, track_title, genre, mb_track_id))
            self.conn.commit()
            # print(f"Saving: {artist} - {track_title} ({mb_track_id})")
        except sqlite3.Error as e:
            print(f"Error saving {artist} - {track_title}\n--- {e}")

    def update_metadata(self, filepath, artist, album, track_title, genre, mb_track_id):
        try:
            cursor=self.conn.cursor()
            cursor.execute('''UPDATE Music
                        SET artist=?, album=?, track_title=?, genre=?, mb_track_id=?
                        WHERE filepath=?''', (artist, album, track_title, genre, mb_track_id, filepath))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error Updating {filepath}: {e}")

    def get_metadata(self, filepath):
        try:
            cursor=self.conn.cursor()
            cursor.execute("SELECT artist, album, track_title, genre, mb_track_id FROM Music WHERE filepath=?", (filepath,))
            row=cursor.fetchone()
            if row:
                return row[0], row[1], row[2], row[3], row[4]
            else:
                return None, None, None, None, None
        except sqlite3.Error as e:
            print(f"Error retrieving data for {filepath} from database:\n --- {e}")
            return None, None, None, None, None

    def process_directory(self, filepath):
        if os.path.exists(filepath):
            file_count = sum(len(files) for _, _, files in os.walk(filepath) if files)
            with tqdm(total=file_count, desc="Processing MP3 files", unit="file") as pbar:
                for root, _, files in os.walk(filepath):
                    for file in files:
                        if file.endswith(".mp3"):
                            file_path = os.path.join(root, file)
                            artist, album, track_title, genre, mb_track_id = self.file_metadata(file_path)
                            if artist and album and track_title:
                                if not self.get_metadata(file_path):
                                    self.insert_metadata(file_path, artist, album, track_title, genre, mb_track_id)
                                    pbar.write(f"Processing: {artist} - {track_title}\n")
                                else:
                                    old_artist, old_album, old_track_title, old_genre, old_mb_track_id = self.get_metadata(file_path)
                                    if artist != old_artist or album != old_album or track_title != old_track_title or genre != old_genre or mb_track_id != old_mb_track_id:
                                        self.update_metadata(file_path, artist, album, track_title, genre, mb_track_id)
                                        pbar.write(f"Updating {file_path}")
                                        pbar.update(1)
                                    else:
                                        pbar.update(1)  # Update progress bar for non mp3 files
        else:
            print(f"Error: Directory {filepath} does not exist")

    
