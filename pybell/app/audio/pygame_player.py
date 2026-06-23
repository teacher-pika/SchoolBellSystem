import pygame
import threading
from .base import BasePlayer

class PygamePlayer(BasePlayer):
    """使用 Pygame 實現的音訊播放器"""

    def __init__(self):
        pygame.mixer.init()
        self.on_end_callback = None
        self.stop_event = threading.Event()

    def play(self, file_path):
        """播放音訊，並在背景線程中監聽播放結束事件"""
        if self.is_playing():
            self.stop()

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.stop_event.clear()
            
            # 啟動一個線程來監聽播放結束
            monitor_thread = threading.Thread(target=self._monitor_playback)
            monitor_thread.daemon = True
            monitor_thread.start()

        except pygame.error as e:
            print(f"Pygame 播放錯誤: {e}")

    def stop(self):
        """停止播放"""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.stop_event.set()

    def is_playing(self):
        """檢查是否正在播放"""
        return pygame.mixer.music.get_busy()

    def _monitor_playback(self):
        """在背景監聽，直到播放結束或被手動停止"""
        while self.is_playing() and not self.stop_event.is_set():
            pygame.time.wait(100)
        
        # 確保不是因為手動停止才觸發回呼
        if not self.stop_event.is_set() and self.on_end_callback:
            self.on_end_callback()
