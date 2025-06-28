import pygame
import os
import time
from threading import Thread


class MediaPlayer:
    def __init__(self, title: str, songs: list, start_index: int = 0):
        pygame.mixer.init()
        self.playlist = songs
        self.queue = []  # Очередь на основе списка
        self.current_index = start_index
        self.is_playing = False
        self.has_loaded = False
        self.volume = 0.5
        self.position = 0
        self.active = True
        self.title = title
        self._callbacks = []
        self.next_from_queue = False  # Флаг для перехода к очереди

        self._start_monitor()

    def _get_song_name(self, index):
        if not self.playlist or index >= len(self.playlist):
            return "Нет трека"
        return os.path.basename(self.playlist[index])

    def _start_monitor(self):
        self.active = True
        monitor_thread = Thread(target=self._monitor_playback, daemon=True)
        monitor_thread.start()

    def _monitor_playback(self):
        while self.active:
            if self.is_playing and not pygame.mixer.music.get_busy():
                # Обрабатываем переход к следующему треку
                self._handle_next_track()
            time.sleep(0.1)

    def _handle_next_track(self):
        """Обработка перехода к следующему треку"""
        if self.next_from_queue and self.queue:
            # Если нужно перейти к очереди, берем первый трек из очереди
            song = self.queue.pop(0)
            self._play_song_directly(song)
            self.next_from_queue = False
            return

        # Переходим к следующему треку в плейлисте
        next_index = self.current_index + 1

        if next_index < len(self.playlist):
            # Воспроизводим следующий трек из плейлиста
            self.current_index = next_index
            self.position = 0
            self._play_current()
        elif self.queue:
            # Если достигли конца плейлиста, но есть очередь
            song = self.queue.pop(0)
            self._play_song_directly(song)
        else:
            # Нет треков для воспроизведения
            self.is_playing = False

    def _play_song_directly(self, song_path):
        """Воспроизводит песню напрямую без изменения плейлиста"""
        if not os.path.exists(song_path):
            return

        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume)
            self.has_loaded = True
            # Уведомляем подписчиков с именем файла
            song_name = os.path.basename(song_path)
            self._notify_subscribers(song_name)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def _play_current(self):
        if not self.playlist or self.current_index >= len(self.playlist):
            return

        song = self.playlist[self.current_index]
        if not os.path.exists(song):
            return

        try:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(start=self.position / 1000)
            pygame.mixer.music.set_volume(self.volume)
            self.has_loaded = True
            self.set_current_song(song)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def play_pause(self, *args):
        # Автовоспроизведение при первом запуске
        if not self.is_playing and not self.has_loaded:
            if not self.playlist and self.queue:
                # Если плейлист пуст, но есть очередь - берем первый трек из очереди
                song = self.queue.pop(0)
                self._play_song_directly(song)
                self.is_playing = True
                return
            elif self.playlist:
                self._play_current()
                self.is_playing = True
                return

        if pygame.mixer.music.get_busy() and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
        else:
            if self.has_loaded:
                pygame.mixer.music.unpause()
            self.is_playing = True

    def next_song(self, *args):
        if not self.playlist and not self.queue:
            return

        # Если есть треки в очереди, устанавливаем флаг для перехода к очереди
        if self.queue:
            self.next_from_queue = True

        # Останавливаем текущее воспроизведение
        pygame.mixer.music.stop()
        self.is_playing = True
        self.position = 0

    def previous_song(self, *args):
        if not self.playlist:
            return

        self.position = 0
        self.current_index = max(0, self.current_index - 1)
        self.is_playing = True
        self._play_current()

    def play_song(self, index: int):
        if not self.playlist or index < 0 or index >= len(self.playlist):
            return

        self.position = 0
        self.current_index = index
        self.is_playing = True
        self._play_current()

    def set_volume(self, volume: int):
        self.volume = max(0, min(1.0, float(volume) / 100))
        if self.has_loaded:
            pygame.mixer.music.set_volume(self.volume)

    def change_playlist(self, title, new_songs: list, start_index: int = 0):
        self.is_playing = False
        pygame.mixer.music.stop()
        self.title = title
        self.playlist = new_songs
        self.queue = []  # Очищаем очередь
        self.current_index = start_index
        self.position = 0
        self.has_loaded = False
        self.next_from_queue = False

    def add_to_queue(self, song: str):
        """Добавление трека в очередь воспроизведения"""
        if not os.path.exists(song):
            return

        self.queue.append(song)

        # Автозапуск если плеер остановлен и нет треков в плейлисте
        if not self.is_playing and not self.playlist:
            self._play_song_directly(song)
            self.is_playing = True
            # Удаляем добавленный трек из очереди
            if self.queue and self.queue[0] == song:
                self.queue.pop(0)

    def add_multiple_to_queue(self, songs: list):
        added = False
        for song in songs:
            if os.path.exists(song):
                self.queue.append(song)
                added = True

        # Автозапуск при добавлении в пустой плеер
        if added and not self.is_playing and not self.playlist:
            song = self.queue.pop(0)
            self._play_song_directly(song)
            self.is_playing = True

    def clear_queue(self):
        self.queue = []  # Очищаем очередь

    def get_current_song(self) -> str:
        return self._get_song_name(self.current_index)

    def get_current_index(self) -> int:
        return self.current_index

    def get_playlist(self) -> list:
        return [f"{i}: {os.path.basename(song)}" for i, song in enumerate(self.playlist)]

    def get_queue(self) -> list:
        return [os.path.basename(song) for song in self.queue]

    def seek(self, position_ms: int):
        if not self.playlist or not self.is_playing:
            return

        self.position = position_ms
        self._play_current()

    def skip_to_queue(self):
        """Перейти к первому треку в очереди"""
        if not self.queue:
            return

        # Устанавливаем флаг для перехода к очереди
        self.next_from_queue = True
        # Останавливаем текущее воспроизведение
        pygame.mixer.music.stop()
        self.is_playing = True
        self.position = 0

    def close(self):
        self.active = False
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.is_playing = False

    def subscribe(self, callback):
        self._callbacks.append(callback)

    def set_current_song(self, song):
        if song != self.get_current_song():
            self._notify_subscribers()

    def _notify_subscribers(self, song_name=None):
        current_song = song_name if song_name else self.get_current_song()
        for callback in self._callbacks:
            callback(current_song)