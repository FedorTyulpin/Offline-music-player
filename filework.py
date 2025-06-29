import os
import eyed3
import tkinter as tk
from tkinter import ttk, simpledialog
import tkinter as tk
from tkinter import Listbox, Frame, Button, Label, MULTIPLE, END, Scrollbar
from collections import OrderedDict

def seconds_to_minutes_seconds(seconds):
  """
  Преобразует секунды в минуты и секунды.

  Args:
    seconds: Количество секунд (целое число).

  Returns:
    Строка, представляющая время в формате "минуты:секунды".
  """
  minutes = int(seconds // 60)
  remaining_seconds = int(seconds % 60)
  return f"{minutes}:{remaining_seconds}"

def get_mp3_metadata(file_path):
    audio = eyed3.load(file_path)

    if not audio.tag:
        return {"error": "No ID3 tag found"}


    return {
        "title": audio.tag.title,
        "artist": audio.tag.artist,
        "album": audio.tag.album,
        "album_artist": audio.tag.album_artist,
        "year": audio.tag.recording_date,
        "genre": audio.tag.genre.name if audio.tag.genre else None,
        "duration": seconds_to_minutes_seconds(audio.info.time_secs if audio.info is not None else 0) ,
        "lyrics": audio.tag.lyrics[0].text if audio.tag.lyrics else None,
        "album_art": "Yes" if audio.tag.images else "No"
    }


from collections import OrderedDict


def reorder_dict(original_dict, first_keys):
    unique_keys = []
    seen = set()
    for key in first_keys:
        if key not in seen:
            seen.add(key)
            unique_keys.append(key)

    new_dict = OrderedDict()
    # Добавляем выбранные ключи
    for key in unique_keys:
        if key in original_dict:
            new_dict[key] = original_dict[key]

    # Добавляем остальные
    for key, value in original_dict.items():
        if key not in seen:  # используем то же множество seen
            new_dict[key] = value

    return dict(new_dict)

def reorder_list(original_list, first_elements):
    temp = original_list.copy()  # Создаем копию списка
    result = []
    for element in first_elements:
        if element in temp:
            result.append(element)
            temp.remove(element)  # Удаляем только первое вхождение
    return result + temp

class Paylist:
    def __init__(self, text):
            if not os.path.exists("meta/playlist/" + text + ".txt"):
                with open("meta/playlist/" + text + ".txt", 'w') as __:
                    pass
            self.title = text
            self.playlist_dic = "meta/playlist/"
            self.music_dic = "meta/music/"
            self.playlist_path = os.path.abspath(self.playlist_dic+self.title+".txt")



    def add_to_playlist(self, song_name):
        with open(self.playlist_path, mode="a+") as playlist:
            if song_name+"\n" not in open(self.playlist_path, mode="r+").readlines():
                playlist.write(song_name+"\n")
                playlist.close()

    def delete_from_playlist(self,song_name):
        with open(self.playlist_path, mode="r+") as playlist:
            lines = playlist.readlines()
            lines.remove(song_name + '\n')

            playlist.close()
        with open(self.playlist_path, mode="w") as playlist:
            playlist.write("".join(lines))
            playlist.close()


    def songs_list(self):
        with open(self.playlist_path, mode="r+") as playlist:
            songs = [x[:-1] for x  in playlist.readlines()]
            return songs
    def songs_path_list(self):
        with open(self.playlist_path, mode="r+") as playlist:
            songs = ["meta/music/"+x[:-1]+".mp3" for x  in playlist.readlines()]
            return songs





class MultiChoiceDialog:
    def __init__(self, parent, title, prompt, choices):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.transient(parent)
        self.top.grab_set()

        self.result = []

        Label(self.top, text=prompt).pack(padx=15, pady=5)

        frame = Frame(self.top)
        frame.pack(padx=15, pady=5, expand=True, fill=tk.BOTH)

        scrollbar = Scrollbar(frame, orient=tk.VERTICAL)
        self.listbox = Listbox(
            frame,
            selectmode=MULTIPLE,
            yscrollcommand=scrollbar.set,
            height=10,
            width=30
        )
        scrollbar.config(command=self.listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        for item in choices:
            self.listbox.insert(END, item)

        button_frame = Frame(self.top)
        button_frame.pack(padx=15, pady=10)

        Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.top.bind("<Return>", lambda e: self.on_ok())
        self.top.bind("<Escape>", lambda e: self.on_cancel())

        parent.wait_window(self.top)

    def on_ok(self):
        selected_indices = self.listbox.curselection()
        self.result = [self.listbox.get(i) for i in selected_indices]
        self.top.destroy()

    def on_cancel(self):
        self.result = []
        self.top.destroy()

    @staticmethod
    def askchoices(parent, title, prompt, choices):
        dialog = MultiChoiceDialog(parent, title, prompt, choices)
        return dialog.result



all_tr = Paylist("All tracks 🔄")
song_authors = {}
albums = {}


for song in os.listdir("meta/music"):
    all_tr.add_to_playlist(song[:-4])

    try:
        song_info = get_mp3_metadata(f"meta/music/{song}")
        for authors in song_info["artist"].split("/"):

            if authors in song_authors:
                song_authors[authors].append(song_info['title'])
            else:
                song_authors[authors] = []
                song_authors[authors].append(song_info['title'])

        if song_info["album"] in albums:
            albums[song_info["album"]].append(song_info['title'])
        else:
            albums[song_info["album"]] = []
            albums[song_info["album"]].append(song_info['title'])
    except:
        pass

for artist in song_authors.keys():
    songs = song_authors[artist]
    pl = Paylist(f"🚹 {artist}")
    for song in songs:
        pl.add_to_playlist(song)

for album in albums.keys():
    songs = albums[album]
    for sumb in "/\\*:|<>?":
        album = album.replace(sumb, "")

    if len(songs) < 4:
        pl = Paylist(f"⭐ {album}")
    elif 4 <= len(songs) <= 8:
        pl = Paylist(f"💽 {album}")
    else:
        pl = Paylist(f"💿 {album}")

    for song in songs:
        pl.add_to_playlist(song)


if __name__ == "__main__":
    print("hello!")



