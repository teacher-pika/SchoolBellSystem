import customtkinter as ctk
from datetime import datetime
import logging
from .ui_components.playlist_frame import PlaylistFrame
from . import theme

logger = logging.getLogger(__name__)

class App(ctk.CTk):
    def __init__(self, config_manager, scheduler, player):
        super().__init__()

        self.config = config_manager
        self.scheduler = scheduler
        self.player = player

        # --- 狀態追蹤 ---
        self.active_indicator = {'button': None, 'original_text': None}
        self.active_highlight = {'type': None, 'index': -1}

        self.title("學校鬧鐘系統")
        self.geometry("1200x800")
        
        # --- 資料 ---
        self.bell_buttons = {} # 用來存放按鈕物件

        # --- UI 元件 ---
        self.create_widgets()

        # --- 啟動定時更新 ---
        self.update_time()
        self.update_next_alarm()

    def create_widgets(self):
        """建立所有 UI 元件"""
        # --- 狀態列 ---
        status_frame = ctk.CTkFrame(self, height=50)
        status_frame.pack(pady=10, padx=10, fill="x")

        self.time_label = ctk.CTkLabel(status_frame, text="現在時間：--:--:--", font=("Arial", 20), width=250)
        self.time_label.pack(side="left", padx=20)

        self.next_alarm_label = ctk.CTkLabel(status_frame, text="下次鬧鐘：無", font=("Arial", 20))
        self.next_alarm_label.pack(side="right", padx=20)
        
        # --- 主內容區 (放置按鈕網格) ---
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.bell_grid = ctk.CTkFrame(main_frame)
        self.bell_grid.pack(pady=20, padx=20)

        self.create_bell_grid(8, 2) # 預設 8x2 版面

        self.create_batch_controls(main_frame)
        
        # --- 播放清單管理 ---
        playlist_container = ctk.CTkFrame(self)
        playlist_container.pack(pady=10, padx=10, fill="both", expand=True)
        playlist_container.grid_columnconfigure((0, 1), weight=1)

        self.start_playlist_frame = PlaylistFrame(
            playlist_container, 
            title="上課鈴聲", 
            config_manager=self.config, 
            playlist_type='start'
        )
        self.start_playlist_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.end_playlist_frame = PlaylistFrame(
            playlist_container, 
            title="下課鈴聲", 
            config_manager=self.config, 
            playlist_type='end'
        )
        self.end_playlist_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    def create_batch_controls(self, parent_frame):
        """建立批次控制按鈕和測試按鈕"""
        control_frame = ctk.CTkFrame(parent_frame)
        control_frame.pack(pady=10)

        ctk.CTkButton(control_frame, text="全部啟用", command=lambda: self.toggle_all(True), fg_color=theme.PRIMARY_COLOR, hover_color=theme.PRIMARY_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="全部停用", command=lambda: self.toggle_all(False), fg_color=theme.SECONDARY_COLOR, hover_color=theme.SECONDARY_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="啟用所有上課鈴", command=lambda: self.toggle_by_type('start', True), fg_color=theme.SUCCESS_COLOR, hover_color=theme.SUCCESS_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="啟用所有下課鈴", command=lambda: self.toggle_by_type('end', True), fg_color=theme.SUCCESS_COLOR, hover_color=theme.SUCCESS_HOVER).pack(side="left", padx=5)
        
        # --- 測試按鈕 ---
        ctk.CTkButton(control_frame, text="立即測試下一個鬧鐘", command=self.test_next_alarm, fg_color=theme.DANGER_COLOR, hover_color=theme.DANGER_HOVER).pack(side="left", padx=15, pady=5)
        ctk.CTkButton(control_frame, text="手動停止鈴聲", command=self.stop_sound, fg_color=theme.WARNING_COLOR, hover_color=theme.WARNING_HOVER, text_color=theme.WARNING_TEXT_COLOR).pack(side="left", padx=5, pady=5)

    def toggle_all(self, enable):
        """全部啟用或停用"""
        alarm_states = self.config.get('alarm_states')
        for key in alarm_states:
            alarm_states[key] = enable
        self.config.set('alarm_states', alarm_states)
        
        logger.info(f"批次操作: 全部 {'啟用' if enable else '停用'}")
        self.redraw_all_buttons()
        self.update_next_alarm()

    def toggle_by_type(self, alarm_type, enable):
        """按類型啟用 (上課/下課)"""
        alarm_states = self.config.get('alarm_states')
        for key in alarm_states:
            if key.startswith(alarm_type):
                alarm_states[key] = enable
        self.config.set('alarm_states', alarm_states)
        
        type_text = "上課" if alarm_type == 'start' else "下課"
        logger.info(f"批次操作: 啟用所有 {type_text} 鈴")
        self.redraw_all_buttons()
        self.update_next_alarm()

    def redraw_all_buttons(self):
        """根據目前的 alarm_states 重新繪製所有按鈕的顏色"""
        alarm_states = self.config.get('alarm_states')
        for key, button in self.bell_buttons.items():
            is_enabled = alarm_states.get(key, False)
            
            alarm_type, period_str = key.split('-')
            period = int(period_str)
            
            if is_enabled:
                color_map = theme.START_COLORS if alarm_type == 'start' else theme.END_COLORS
                colors = color_map[period]
                button.configure(
                    fg_color=colors['fg'],
                    text_color=colors['text'],
                    hover_color=colors['hover']
                )
            else:
                button.configure(
                    fg_color=theme.INACTIVE_COLOR,
                    text_color=theme.INACTIVE_TEXT_COLOR,
                    hover_color=theme.INACTIVE_HOVER_COLOR
                )


    def create_bell_grid(self, cols, rows):
        """根據指定的行列數，生成鬧鐘控制按鈕網格"""
        # 清空舊的 grid
        for widget in self.bell_grid.winfo_children():
            widget.destroy()

        schedule_times = self.config.get('schedule')
        alarm_states = self.config.get('alarm_states')

        buttons_data = []
        for i, time_str in enumerate(schedule_times['classStart']):
            buttons_data.append({'type': 'start', 'period': i, 'time': time_str})
        for i, time_str in enumerate(schedule_times['classEnd']):
            buttons_data.append({'type': 'end', 'period': i, 'time': time_str})
        
        for index, data in enumerate(buttons_data):
            key = f"{data['type']}-{data['period']}"
            type_text = "上課" if data['type'] == 'start' else "下課"
            text = f"第{data['period'] + 1}節 {type_text}\n{data['time']}"
            
            is_enabled = alarm_states.get(key, False)
            
            # 根據狀態設定顏色
            if is_enabled:
                color_map = theme.START_COLORS if data['type'] == 'start' else theme.END_COLORS
                colors = color_map[data['period']]
                fg_color = colors['fg']
                text_color = colors['text']
                hover_color = colors['hover']
            else:
                fg_color = theme.INACTIVE_COLOR
                text_color = theme.INACTIVE_TEXT_COLOR
                hover_color = theme.INACTIVE_HOVER_COLOR


            btn = ctk.CTkButton(
                self.bell_grid,
                text=text,
                fg_color=fg_color,
                text_color=text_color,
                hover_color=hover_color,
                command=lambda k=key: self.toggle_alarm(k)
            )
            
            row = index // cols
            col = index % cols
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            self.bell_buttons[key] = btn # 將按鈕物件存起來

        # 讓網格的行列可以自動伸縮
        for i in range(rows):
            self.bell_grid.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            self.bell_grid.grid_columnconfigure(i, weight=1)

    def toggle_alarm(self, key):
        """切換指定鬧鐘的啟用狀態"""
        alarm_states = self.config.get('alarm_states')
        new_state = not alarm_states.get(key, False)
        alarm_states[key] = new_state
        self.config.set('alarm_states', alarm_states)
        
        logger.info(f"使用者切換鬧鐘狀態: {key} -> {'啟用' if new_state else '停用'}")

        # 只更新被點擊的按鈕
        button_to_update = self.bell_buttons.get(key)
        if button_to_update:
            alarm_type, period_str = key.split('-')
            period = int(period_str)
            if new_state:
                color_map = theme.START_COLORS if alarm_type == 'start' else theme.END_COLORS
                colors = color_map[period]
                button_to_update.configure(
                    fg_color=colors['fg'],
                    text_color=colors['text'],
                    hover_color=colors['hover']
                )
            else:
                button_to_update.configure(
                    fg_color=theme.INACTIVE_COLOR,
                    text_color=theme.INACTIVE_TEXT_COLOR,
                    hover_color=theme.INACTIVE_HOVER_COLOR
                )
        
        # 立刻更新下次鬧鐘的顯示
        self.update_next_alarm()

    def test_next_alarm(self):
        """觸發下一個即將到來的鬧鐘"""
        logger.info("使用者點擊: 立即測試下一個鬧鐘")
        self.scheduler.trigger_next_alarm_manually()

    def stop_sound(self):
        """手動停止目前播放的音訊"""
        logger.info("使用者點擊: 手動停止鈴聲")
        self.player.stop()

    def highlight_playing_sound(self, alarm_type, sound_index):
        """高亮正在播放的鈴聲，並清除上一個高亮"""
        # 1. 清除上一個高亮
        if self.active_highlight['type'] is not None and self.active_highlight['index'] != -1:
            self.unhighlight_playing_sound(self.active_highlight['type'], self.active_highlight['index'])

        # 2. 設定新的高亮
        if alarm_type == 'start':
            self.start_playlist_frame.highlight_item(sound_index)
        else:
            self.end_playlist_frame.highlight_item(sound_index)
        
        # 3. 記錄新的高亮狀態
        self.active_highlight = {'type': alarm_type, 'index': sound_index}

    def unhighlight_playing_sound(self, alarm_type, sound_index):
        """取消高亮指定的鈴聲 (通常在播放結束時呼叫)"""
        if alarm_type == 'start':
            self.start_playlist_frame.unhighlight_item(sound_index)
        else:
            self.end_playlist_frame.unhighlight_item(sound_index)
        
        # 如果取消的是當前記錄的高亮，則清除狀態
        if self.active_highlight['type'] == alarm_type and self.active_highlight['index'] == sound_index:
            self.active_highlight = {'type': None, 'index': -1}

    def show_triggered_indicator(self, alarm_type, period):
        """在觸發的按鈕上顯示指示器，並清除上一個"""
        # 1. 清除上一個指示器
        if self.active_indicator['button'] and self.active_indicator['original_text']:
            self.active_indicator['button'].configure(text=self.active_indicator['original_text'])

        # 2. 設定新的指示器
        key = f"{alarm_type}-{period}"
        button = self.bell_buttons.get(key)
        if button:
            original_text = button.cget("text")
            button.configure(text=f"▶ {original_text}")
            
            # 3. 記錄新的指示器狀態
            self.active_indicator = {'button': button, 'original_text': original_text}

    def update_time(self):
        """每秒更新一次時間顯示"""
        now_str = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"現在時間：{now_str}")
        self.after(1000, self.update_time)

    def update_next_alarm(self):
        """每秒更新一次下次鬧鐘的顯示"""
        next_alarm_text = self.scheduler.get_next_alarm_info()
        
        if next_alarm_text:
            self.next_alarm_label.configure(text=f"下次鬧鐘：{next_alarm_text}")
        else:
            self.next_alarm_label.configure(text="下次鬧鐘：無 (全部停用)")

        self.after(1000, self.update_next_alarm)
