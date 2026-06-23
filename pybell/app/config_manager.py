import json
import os

class ConfigManager:
    """負責管理設定檔的讀取與寫入"""

    def __init__(self, config_file='config/settings.json'):
        self.config_path = config_file
        self.config = {}
        self._ensure_config_dir_exists()
        self.load_config()

    def _ensure_config_dir_exists(self):
        """確保設定檔所在的目錄存在"""
        dir_name = os.path.dirname(self.config_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def get_default_config(self):
        """回傳預設設定"""
        return {
            'schedule': {
                'classStart': ['08:20', '09:15', '10:15', '11:10', '13:20', '14:15', '15:15', '16:10'],
                'classEnd': ['09:10', '10:05', '11:05', '12:00', '14:10', '15:05', '16:05', '17:00']
            },
            'alarm_states': {f'start-{i}': True for i in range(8)} | {f'end-{i}': True for i in range(8)},
            'sound_lists': {
                'start': [{
                    'type': 'url',
                    'value': 'https://www.desh.hc.edu.tw/ischool/public/resource_view/open.php?file=1845edb62d768bb482efa8e2d80769b7.mp3',
                    'display': '預設上課鈴聲'
                }],
                'end': [{
                    'type': 'url',
                    'value': 'https://www.desh.hc.edu.tw/ischool/public/resource_view/open.php?file=90f0daff67f12a99970436a11b43095a.mp3',
                    'display': '預設下課鈴聲'
                }]
            },
            'play_modes': {
                'start': 'sequential',
                'end': 'sequential'
            },
            'play_counters': {
                'start': 0,
                'end': 0
            },
            'audio_backend': 'pygame',
            'version': '1.0'
        }

    def load_config(self):
        """載入設定檔，若不存在則建立預設設定"""
        default_config = self.get_default_config()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # 簡單的版本檢查與合併，未來可擴充
                if 'version' not in self.config or self.config['version'] != default_config['version']:
                    # 這裡可以加入更複雜的遷移邏輯
                    self.config = {**default_config, **self.config}
                    self.config['version'] = default_config['version']
                    self.save_config()
            except (json.JSONDecodeError, IOError):
                self.config = default_config
                self.save_config()
        else:
            self.config = default_config
            self.save_config()
        return self.config

    def save_config(self):
        """將目前設定寫入檔案"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError:
            return False

    def get(self, key, default=None):
        """取得特定設定值"""
        return self.config.get(key, default)

    def set(self, key, value):
        """設定特定值並儲存"""
        self.config[key] = value
        self.save_config()
