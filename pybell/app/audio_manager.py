from .audio.pygame_player import PygamePlayer
# from .audio.vlc_player import VlcPlayer # 未來擴充用

class AudioManager:
    """音訊播放管理器，根據設定選擇並提供播放器實例"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.player = self._create_player()

    def _create_player(self):
        """根據設定檔中的 audio_backend 建立對應的播放器"""
        backend = self.config.get('audio_backend', 'pygame')
        
        if backend == 'vlc':
            # return VlcPlayer()
            print("VLC backend is not implemented yet. Falling back to pygame.")
            return PygamePlayer()
        elif backend == 'pygame':
            return PygamePlayer()
        else:
            raise ValueError(f"未知的音訊後端: {backend}")

    def get_player(self):
        """回傳當前的播放器實例"""
        return self.player
