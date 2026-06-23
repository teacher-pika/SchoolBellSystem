# pybell/app/theme.py

"""
此檔案集中管理應用程式的色彩主題，方便統一修改。
顏色代碼主要參考原始 index.html 的 CSS。
"""

# 彩虹色系 - 上課 (參考 index.html)
# 順序: 紅, 橙, 黃, 綠, 青, 藍, 紫, 灰
START_COLORS = [
    {'fg': '#ff6b6b', 'text': 'white', 'hover': '#e55a5a'},
    {'fg': '#ffa500', 'text': 'white', 'hover': '#e59400'},
    {'fg': '#ffd93d', 'text': '#333333', 'hover': '#e5c336'},
    {'fg': '#6bcf7f', 'text': 'white', 'hover': '#5fb872'},
    {'fg': '#4ecdc4', 'text': 'white', 'hover': '#46b8b0'},
    {'fg': '#5e9cff', 'text': 'white', 'hover': '#548be5'},
    {'fg': '#a864fd', 'text': 'white', 'hover': '#9758e3'},
    {'fg': '#8b8b8b', 'text': 'white', 'hover': '#7c7c7c'},
]

# 彩虹色系 - 下課 (參考 index.html)
# 順序: 深紅, 深橙, 深黃, 深綠, 深青, 深藍, 深紫, 深灰
END_COLORS = [
    {'fg': '#c92a2a', 'text': 'white', 'hover': '#b22525'},
    {'fg': '#e67700', 'text': 'white', 'hover': '#cf6a00'},
    {'fg': '#fcc419', 'text': '#333333', 'hover': '#e2b016'},
    {'fg': '#2f9e44', 'text': 'white', 'hover': '#2a8e3d'},
    {'fg': '#22b8cf', 'text': 'white', 'hover': '#1fa4b8'},
    {'fg': '#1971c2', 'text': 'white', 'hover': '#1665ad'},
    {'fg': '#7048e8', 'text': 'white', 'hover': '#6540d0'},
    {'fg': '#495057', 'text': 'white', 'hover': '#41474d'},
]

# 停用狀態的顏色
INACTIVE_COLOR = "#f0f0f0"
INACTIVE_HOVER_COLOR = "#d9d9d9"
INACTIVE_TEXT_COLOR = "#a0a0a0"

# UI 其他元件顏色
HIGHLIGHT_COLOR = "#fff3cd" # 播放清單高亮
PLAYER_HIGHLIGHT_TEXT_COLOR = "#856404" # 播放清單高亮文字顏色

# 按鈕主題色
PRIMARY_COLOR = "#667eea"
SECONDARY_COLOR = "#6c757d"
SUCCESS_COLOR = "#28a745"
DANGER_COLOR = "#dc3545"
INFO_COLOR = "#17a2b8"
WARNING_COLOR = "#ffc107"
WARNING_TEXT_COLOR = "black"

# 按鈕 Hover 色
PRIMARY_HOVER = "#5a6fcf"
SECONDARY_HOVER = "#5a6268"
SUCCESS_HOVER = "#218838"
DANGER_HOVER = "#c82333"
INFO_HOVER = "#138496"
WARNING_HOVER = "#e5ad06"
