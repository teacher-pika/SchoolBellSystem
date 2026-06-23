import os
import time
import random
from app.logger import setup_logger
from app.config_manager import ConfigManager
from app.audio_manager import AudioManager
from app.scheduler import Scheduler
from app.downloader import download_audio_to_temp, cleanup_temp_file
from app.ui import App

# --- 全域變數 ---
logger = setup_logger()
config_manager = ConfigManager(config_file=os.path.join('pybell', 'config', 'settings.json'))
audio_manager = AudioManager(config_manager)
player = audio_manager.get_player()

app_instance = None # 全域變數，用來存放 App 實例

def play_alarm(alarm_type, period):
    """
    鬧鐘觸發時的回呼函式。
    負責根據鬧鐘類型與播放模式，取得對應的鈴聲並播放。
    """
    logger.info(f"接收到鬧鐘回呼: {alarm_type}-{period}")
    sound_lists = config_manager.get('sound_lists', {})
    playlist = sound_lists.get(alarm_type, [])
    
    if not playlist:
        logger.warning(f"{alarm_type} 播放清單是空的，無法播放鈴聲。")
        return
        
    # --- 根據播放模式選擇音訊 ---
    play_modes = config_manager.get('play_modes', {})
    mode = play_modes.get(alarm_type, 'sequential')
    
    sound_info = None
    sound_index = -1 # 記錄音訊在清單中的索引
    if mode == 'random':
        sound_index = random.randint(0, len(playlist) - 1)
        sound_info = playlist[sound_index]
        logger.info(f"隨機模式選擇: {sound_info['display']}")
    else: # sequential
        play_counters = config_manager.get('play_counters', {'start': 0, 'end': 0})
        current_index = play_counters.get(alarm_type, 0)
        sound_index = current_index % len(playlist)
        
        sound_info = playlist[sound_index]
        logger.info(f"循序模式選擇 (索引 {current_index}): {sound_info['display']}")
        
        # 更新並儲存計數器
        play_counters[alarm_type] = current_index + 1
        config_manager.set('play_counters', play_counters)

    if not sound_info:
        logger.error("無法根據播放模式選擇有效的音訊。")
        return

    # --- UI 提示 ---
    if app_instance:
        app_instance.after(0, lambda: app_instance.highlight_playing_sound(alarm_type, sound_index))
        app_instance.after(0, lambda: app_instance.show_triggered_indicator(alarm_type, period))

    # 處理不同來源的音訊
    temp_file_path = None
    file_to_play = None

    if sound_info['type'] == 'url':
        temp_file_path = download_audio_to_temp(sound_info['value'])
        file_to_play = temp_file_path
    elif sound_info['type'] == 'local':
        file_to_play = sound_info.get('path')
        if not os.path.exists(file_to_play):
             logger.error(f"本機檔案不存在: {file_to_play}")
             # 可以在此處觸發一個 UI 提示
             return

    if file_to_play:
        player.play(file_to_play)
    else:
        logger.error("沒有可播放的檔案來源。")
        return

    # 設定播放結束後的回呼，用來清理暫存檔
    def on_end():
        logger.info(f"鈴聲播放完畢: {sound_info.get('display')}")
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        # --- 取消 UI 提示 ---
        if app_instance:
            app_instance.after(0, lambda: app_instance.unhighlight_playing_sound(alarm_type, sound_index))

    player.set_on_end_callback(on_end)


def main():
    """應用程式主進入點"""
    global app_instance
    logger.info("應用程式啟動")
    logger.info(f"設定檔已載入: {config_manager.config_path}")
    logger.info(f"音訊播放器已載入: {type(player).__name__}")
    
    scheduler = Scheduler(config_manager, play_alarm)
    app = App(config_manager, scheduler, player) # 傳入 player
    app_instance = app # 將 App 實例存到全域變數

    def on_closing():
        """定義關閉視窗時的行為"""
        logger.info("偵測到視窗關閉，正在關閉程式...")
        scheduler.stop()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing) # 綁定關閉事件
    
    try:
        scheduler.start()
        app.mainloop() # 啟動 GUI 主迴圈
    finally:
        if scheduler.running:
             scheduler.stop()
        logger.info("應用程式正常關閉")

if __name__ == "__main__":
    main()
