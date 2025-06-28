from tkinter import  *
from tkinter.messagebox import *
from tkinter.simpledialog import *

from filework import *
from musicwork import *
import keyboard
from threading import Thread




class MusicAPP(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Music player")
        self.geometry("1000x600")

        self.playlists = {name: Paylist(name) for name in ["All tracks 🔄", "Favorites ❤"]}
        self.playlists = reorder_dict({name:Paylist(name) for name in  [x[:-4] for x in os.listdir("meta/playlist/")]},("All tracks 🔄", "Favorites ❤"))
        self.playlists_var = Variable(value=list(self.playlists))

        self.opened_playlist = "All tracks 🔄"

        self.curent_playlist = MediaPlayer("All tracks 🔄",self.playlists[self.opened_playlist].songs_path_list(),start_index=0)
        self.columns = ("№", "Name","Author", "Album", "duration")




        self.grid_rowconfigure(0, weight=1)  # Основная строка с контентом
        self.grid_rowconfigure(1, weight=0)  # Строка плеера (фиксированная высота)
        self.grid_columnconfigure(0, weight=0)  # Боковая панель (фиксированная ширина)
        self.grid_columnconfigure(1, weight=1)  # Основная область (растягивается)


        self.side_panel()
        self.main_panel()
        self.lower_panel()

        self.curent_playlist.subscribe(self.update_song_display)


        hotkey_thread = Thread(target=self.setup_global_hotkeys, daemon=True)
        hotkey_thread.start()

    def delete_playlist(self):
        playlist_to_delete = self.playlists_list.get(self.playlists_list.curselection())
        if not playlist_to_delete.startswith(("🚹", "💽", "💿", "⭐", "All tracks 🔄", "Favorites ❤")):
            if askyesno("Delete playlist", f"Are you sure you want to delete the playlist '{playlist_to_delete}'?"):
                os.remove(f"meta/playlist/{playlist_to_delete}.txt")
                del self.playlists[playlist_to_delete]

                self.playlists_var = Variable(value=list(self.playlists))
                self.playlists_list.configure(listvariable=self.playlists_var)
                self.open_playlist(name="All tracks 🔄")
        else:
            showerror("Error", f"You can`t delete playlist '{playlist_to_delete}'")

    def create_playlist(self):
        playlist_name = askstring("Create new playlist", "Enter new playlist name:")

        if (playlist_name not in list(self.playlists) and not playlist_name.startswith(("🚹", "💽", "💿", "⭐", "All tracks 🔄", "Favorites ❤"))) and playlist_name :
            self.playlists[playlist_name] = Paylist(playlist_name)
            self.playlists_var = Variable(value=reorder_list(sorted(list(self.playlists)), ["All tracks 🔄", "Favorites ❤"]))
            self.playlists_list.configure(listvariable=self.playlists_var)
            self.open_playlist(name=playlist_name)


        elif playlist_name is None:
            pass
        elif not playlist_name or playlist_name.startswith(("🚹", "💽", "💿", "⭐", "All tracks 🔄", "Favorites ❤")):
            showerror("Error", "Wrong playlist name")
        else:
            showerror("Error", "Playlist with this name already exist")

    def setup_global_hotkeys(self):

        while True:
            event = keyboard.read_event().name

            if event == 'play/pause media':
                self.curent_playlist.play_pause()
            elif event == 'next track':
                self.curent_playlist.next_song()
            elif event == 'previous track':
                self.curent_playlist.previous_song()
            else:
                pass

            time.sleep(0.5)

    def add_to_quen(self):
        item = self.songs.selection()
        self.curent_playlist.add_to_queue(f'meta/music/{self.songs.item(item)["values"][1]}.mp3')
        self.open_playlist(name=self.curent_playlist.title)
        self.update_song_display(self.curent_playlist.get_current_song())

    def add_song_to_playlists(self):
        song = self.curent_playlist.get_current_song()
        song_info = get_mp3_metadata("meta/music/" + song)
        playlists = [x for x in list(self.playlists) if song_info["title"] not in self.playlists[x].songs_list() and not x.startswith(("🚹", "💽", "💿", "⭐", "All tracks 🔄"))]

        for pl in MultiChoiceDialog.askchoices(self, "Add song to playlists", f"With playlist you want to add '{song_info["title"]}'?", playlists):
            self.playlists[pl].add_to_playlist(song_info["title"])

    def add_songs_to_playlist(self):
        playlist = self.opened_playlist
        if not playlist.startswith(("🚹", "💽", "💿", "⭐", "All tracks 🔄")):
            all_songs = [x for x in self.playlists["All tracks 🔄"].songs_list() if x not in self.playlists[playlist].songs_list()]

            for song in MultiChoiceDialog.askchoices(self, "Add songs to playlist", f"With songs you want to add to '{playlist}'?", all_songs):
                self.playlists[playlist].add_to_playlist(song)
                self.open_playlist(name=playlist)
        else:
            showerror("Error", "Unable to add songs to generated playlist")

    def update_song_display(self, song_name):
        """Обработчик события - вызывается при смене песни"""
        try:
            song_info =get_mp3_metadata("meta/music/"+song_name)
            self.song_name_lab.configure(text=song_info["title"])
            self.author_lab.configure(text=song_info["artist"])



            if self.opened_playlist == self.curent_playlist.title:
                for item in self.songs.get_children():
                    if self.songs.item(item, 'values')[1] == song_info["title"]:
                        self.songs.selection_set(item)  # Выделить элемент
                        self.songs.focus(item)  # Установить фокус (опционально)
                        self.songs.see(item)  # Прокрутить к элементу (опционально)
                        break



        except Exception:
                pass

    def click_music_event(self, event):
        item = self.songs.selection()

        region = self.songs.identify_region(event.x, event.y)

        if region == "cell":
            if self.curent_playlist.title == self.opened_playlist:
                self.curent_playlist.play_song(self.songs.item(item)["values"][0]-1)
            else:
                self.curent_playlist.change_playlist(self.opened_playlist,self.playlists[self.opened_playlist].songs_path_list(), start_index=self.songs.item(item)["values"][0]-1)
                self.curent_playlist.play_pause()

    def main_panel(self):
        # Основной контейнер с правильным распределением веса
        self.main_label = ttk.LabelFrame(
            text=self.opened_playlist,
            padding=(10, 5),
            style='Main.TLabelframe'
        )
        self.main_label.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Настройка весов строк и столбцов для растягивания
        self.main_label.columnconfigure(0, weight=1)
        self.main_label.rowconfigure(1, weight=1)  # Основной вес для строки с треками

        # Заголовок плейлиста
        header_frame = ttk.Frame(self.main_label)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        # Левая часть заголовка
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky="w")

        playlist_title = ttk.Label(
            title_frame,
            text=self.opened_playlist,
            font=("Segoe UI", 16, "bold"),
            foreground="#2c3e50"
        )
        playlist_title.grid(row=0, column=0, sticky="w")

        songs_count = ttk.Label(
            title_frame,
            text=f"{len(self.playlists[self.opened_playlist].songs_list())} songs",
            font=("Segoe UI", 10),
            foreground="#7f8c8d"
        )
        songs_count.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # Правая часть заголовка - кнопки управления
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.grid(row=0, column=1, sticky="e")

        # Кнопка "Add to Playlist"
        add_to_playlist_btn = ttk.Button(
            buttons_frame,
            text="➕ Add songs to Playlist",
            style="Secondary.TButton",
            command= lambda: self.add_songs_to_playlist()

        )
        add_to_playlist_btn.grid(row=0, column=0, padx=(0, 5))

        # Кнопка "Add to Queue"
        add_to_queue_btn = ttk.Button(
            buttons_frame,
            text="📥 Add to Queue",
            style="Secondary.TButton",
            command= lambda : self.add_to_quen()
        )
        add_to_queue_btn.grid(row=0, column=1, padx=(0, 5))

        # Кнопка "Play All"
        play_btn = ttk.Button(
            buttons_frame,
            text="▶ Play All",
            style="Accent.TButton",
            command=lambda: (
                self.curent_playlist.change_playlist(
                    self.opened_playlist,
                    self.playlists[self.opened_playlist].songs_path_list()
                ),
                self.curent_playlist.play_pause()
            )
        )
        play_btn.grid(row=0, column=2)

        # Контейнер для таблицы треков (занимает всё оставшееся пространство)
        table_container = ttk.Frame(self.main_label)
        table_container.grid(row=1, column=0, sticky="nsew")

        # Настройка весов для растягивания
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Таблица треков
        self.songs = ttk.Treeview(
            table_container,
            columns=self.columns,
            show="headings",
            selectmode="browse",
            yscrollcommand=scrollbar.set,
            style="Custom.Treeview"
        )
        self.songs.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.songs.yview)

        self.songs.bind("<Double-1>", self.click_music_event)

        # Настройка колонок
        col_widths = {"#": 50, "Title": 250, "Artist": 150, "Album": 150, "Duration": 80}
        for head in self.columns:
            self.songs.heading(head, text=head, anchor=W)
            self.songs.column(
                head,
                width=col_widths.get(head, 100),
                anchor=W,
                stretch=False
            )

        # Заполнение данными
        n = 1
        for song_path in self.playlists[self.opened_playlist].songs_path_list():
            song = get_mp3_metadata(song_path)
            try:
                self.songs.insert("", END, values=(
                    n,
                    song.get("title", "Unknown Title"),
                    song.get("artist", "Unknown Artist"),
                    song.get("album", "Unknown Album"),
                    song.get("duration", "0:00")
                ))
                n += 1
            except Exception as e:
                print(f"Error loading metadata for {song_path}: {e}")

    def side_panel(self):
        # Основной контейнер боковой панели
        self.side_label = ttk.LabelFrame(
            text="Playlists",
            padding=(5, 10),
            borderwidth=0
        )
        self.side_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Настройка весов для растягивания
        self.side_label.columnconfigure(0, weight=1)
        self.side_label.rowconfigure(1, weight=1)  # Основной вес для списка плейлистов

        # Панель кнопок управления
        buttons_frame = ttk.Frame(self.side_label)
        buttons_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        # Кнопка добавления плейлиста
        add_button = ttk.Button(
            buttons_frame,
            text="+ Add Playlist",
            style="Accent.TButton",
            command=lambda : self.create_playlist()
        )
        add_button.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        # Кнопка удаления плейлиста
        remove_button = ttk.Button(
            buttons_frame,
            text="− Remove",
            style="Danger.TButton",
            command=lambda : self.delete_playlist()
        )
        remove_button.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        # Контейнер для списка плейлистов
        list_container = ttk.Frame(self.side_label)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Список плейлистов с современным стилем
        self.playlists_list = Listbox(
            list_container,
            listvariable=self.playlists_var,
            bg="#ffffff",
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 10),
            selectbackground="#e0f0ff",
            selectforeground="#000000",
            activestyle="none",
            yscrollcommand=scrollbar.set
        )
        self.playlists_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.playlists_list.yview)

        # Привязка двойного клика
        self.playlists_list.bind("<Double-1>", self.open_playlist)

        # Добавляем отступ внизу
        ttk.Label(self.side_label, text="").grid(row=2, column=0, pady=5)

    def lower_panel(self):
        # Основной контейнер нижней панели
        self.lower_label = ttk.LabelFrame(style='Bottom.TLabelframe')
        self.lower_label.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)

        # Контейнер для информации о треке
        track_info_frame = ttk.Frame(self.lower_label)
        track_info_frame.grid(row=0, column=0, sticky="w", padx=10)

        # Название трека с переносом текста
        self.song_name_lab = ttk.Label(
            track_info_frame,
            text="...",
            font=("Segoe UI", 9, "bold"),
            width=25,
            anchor="w"
        )
        self.song_name_lab.grid(row=0, column=0, sticky="w")

        # Автор с серым цветом текста
        self.author_lab = ttk.Label(
            track_info_frame,
            text="...",
            font=("Segoe UI", 8),
            foreground="#555555",
            anchor="w"
        )
        self.author_lab.grid(row=1, column=0, sticky="w", pady=(0, 3))

        # Контейнер для кнопок управления
        controls_frame = ttk.Frame(self.lower_label)
        controls_frame.grid(row=0, column=1, padx=10)

        # Современные плоские кнопки управления
        control_buttons = [
            ("⏮", self.curent_playlist.previous_song),
            ("⏯", self.curent_playlist.play_pause),
            ("⏭", self.curent_playlist.next_song)
        ]

        for i, (symbol, cmd) in enumerate(control_buttons):
            btn = Button(
                controls_frame,
                borderwidth=0,
                text=symbol,
                width=2,
                command=cmd,
            )
            btn.grid(row=0, column=i, padx=3)

        # Контейнер для регулировки громкости
        volume_frame = ttk.Frame(self.lower_label)
        volume_frame.grid(row=0, column=2, sticky="e", padx=(0, 10))

        # Иконка громкости
        volume_icon = ttk.Label(volume_frame, text="🔊", font=("Arial", 10))
        volume_icon.grid(row=0, column=0, padx=(0, 5))

        # Стилизованный слайдер громкости
        self.volume_slider = ttk.Scale(
            volume_frame,
            length=120,
            from_=0,
            to=100,
            value=100,
            command=self.curent_playlist.set_volume,
        )
        self.volume_slider.grid(row=0, column=1)

        add_to_playlist_btn = ttk.Button(
            self.lower_label,
            text="➕",
            style="Secondary.TButton",
            command=lambda: self.add_song_to_playlists()

        )
        add_to_playlist_btn.grid(row=0, column=3, padx=(0, 5))

    def open_playlist(self, event=None, name=None):
        name = reorder_list(sorted(list(self.playlists)), ["All tracks 🔄", "Favorites ❤"])[self.playlists_list.curselection()[0]] if name is None else name
        self.opened_playlist = name

        self.main_label.destroy()
        self.main_panel()
        self.update_song_display(self.curent_playlist.get_current_song())
        return


if __name__ == "__main__":
    app = MusicAPP()
    app.mainloop()

