from abc import ABC, abstractmethod

class BasePlayer(ABC):
    """音訊播放器的抽象基礎類別"""

    @abstractmethod
    def play(self, file_path):
        """播放指定的音訊檔案"""
        pass

    @abstractmethod
    def stop(self):
        """停止目前播放的音訊"""
        pass

    @abstractmethod
    def is_playing(self):
        """檢查目前是否有音訊正在播放"""
        pass

    def set_on_end_callback(self, callback):
        """設定播放結束時的回呼函式"""
        self.on_end_callback = callback
