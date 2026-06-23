import customtkinter as ctk
from customtkinter import filedialog
import os
from .. import theme

class PlaylistFrame(ctk.CTkFrame):
    def __init__(self, master, title, config_manager, playlist_type):
        super().__init__(master)
        
        self.config = config_manager
        self.playlist_type = playlist_type # 'start' or 'end'

        # --- 佈局 ---
        self.grid_columnconfigure(0, weight=1)

        # --- 元件 ---
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(controls_frame, text="新增 URL", command=self.add_sound_from_url, fg_color=theme.PRIMARY_COLOR, hover_color=theme.PRIMARY_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="新增本機檔案", command=self.add_sound_from_local, fg_color=theme.PRIMARY_COLOR, hover_color=theme.PRIMARY_HOVER).pack(side="left", padx=5)
        
        # --- 播放模式切換 ---
        play_modes = ["順序播放", "隨機播放"]
        self.play_mode_var = ctk.StringVar(value=self.get_mode_display_name())
        
        mode_switch = ctk.CTkSegmentedButton(
            controls_frame,
            values=play_modes,
            variable=self.play_mode_var,
            command=self.on_mode_change
        )
        mode_switch.pack(side="left", padx=10)

        # 測試播放按鈕未來加入
        
        # 播放清單列表
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="播放清單")
        self.scrollable_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.update_playlist_display()

    def get_mode_display_name(self):
        """根據設定檔中的模式 (sequential/random) 回傳顯示名稱"""
        mode = self.config.get('play_modes', {}).get(self.playlist_type, 'sequential')
        return "順序播放" if mode == 'sequential' else "隨機播放"

    def on_mode_change(self, selected_display_name):
        """當使用者切換播放模式時呼叫"""
        new_mode = 'sequential' if selected_display_name == "順序播放" else 'random'
        
        play_modes = self.config.get('play_modes')
        play_modes[self.playlist_type] = new_mode
        self.config.set('play_modes', play_modes)
        print(f"Playlist {self.playlist_type} mode changed to {new_mode}")


    def add_sound_from_url(self):
        """從 URL 新增音訊"""
        dialog = ctk.CTkInputDialog(text="請輸入音訊 URL:", title="新增 URL")
        url = dialog.get_input()
        
        if url:
            new_sound = {'type': 'url', 'value': url, 'display': url}
            self._add_sound_to_config(new_sound)

    def add_sound_from_local(self):
        """從本機檔案新增音訊"""
        filepath = filedialog.askopenfilename(
            title="請選擇音訊檔案",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        if filepath:
            filename = os.path.basename(filepath)
            new_sound = {'type': 'local', 'path': filepath, 'display': filename}
            self._add_sound_to_config(new_sound)

    def _add_sound_to_config(self, new_sound):
        """將新的 sound 物件加入設定檔並更新 UI"""
        sound_lists = self.config.get('sound_lists')
        sound_lists[self.playlist_type].append(new_sound)
        self.config.set('sound_lists', sound_lists)
        self.update_playlist_display()

    def remove_sound(self, index_to_remove):
        sound_lists = self.config.get('sound_lists')
        
        if 0 <= index_to_remove < len(sound_lists[self.playlist_type]):
            removed = sound_lists[self.playlist_type].pop(index_to_remove)
            self.config.set('sound_lists', sound_lists)
            self.update_playlist_display()
            print(f"Removed sound: {removed.get('display')}")

    def update_playlist_display(self):
        # 清空現有列表
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # 重新生成列表
        playlist = self.config.get('sound_lists', {}).get(self.playlist_type, [])
        self.item_frames = {} 
        for i, sound in enumerate(playlist):
            item_frame = ctk.CTkFrame(self.scrollable_frame)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            label_text = sound.get('display', '未知鈴聲')
            # 加上路徑提示
            if sound.get('type') == 'local':
                 label_text += f" ({sound.get('path', 'N/A')})"
            
            ctk.CTkLabel(item_frame, text=label_text, wraplength=300).pack(side="left", padx=5, pady=2, expand=True, fill="x")
            
            remove_btn = ctk.CTkButton(
                item_frame, text="刪除", width=60,
                fg_color=theme.DANGER_COLOR,
                hover_color=theme.DANGER_HOVER,
                command=lambda index=i: self.remove_sound(index)
            )
            remove_btn.pack(side="right", padx=5, pady=2)
            
            # 將 frame 存起來以便後續操作
            self.item_frames[i] = item_frame

    def highlight_item(self, index):
        """高亮指定索引的項目"""
        if index in self.item_frames:
            self.item_frames[index].configure(fg_color=theme.HIGHLIGHT_COLOR)
            # 同時修改 label 的文字顏色以確保可讀性
            for widget in self.item_frames[index].winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=theme.PLAYER_HIGHLIGHT_TEXT_COLOR)


    def unhighlight_item(self, index):
        """取消高亮指定索引的項目"""
        if index in self.item_frames:
            # 恢復成 customtkinter 的預設 frame 顏色
            default_fg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            default_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            self.item_frames[index].configure(fg_color=default_fg_color)
            # 恢復 label 的文字顏色
            for widget in self.item_frames[index].winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=default_text_color)
