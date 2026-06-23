import schedule
import time
import threading
import logging
from datetime import datetime

logger = logging.getLogger('SchoolBell.Scheduler')

class Scheduler:
    """鬧鐘排程器，在背景線程中執行"""

    def __init__(self, config_manager, alarm_callback):
        self.config = config_manager
        self.alarm_callback = alarm_callback  # 當鬧鐘觸發時要呼叫的函式
        self.running = False
        self.thread = None
        self._setup_schedule()

    def get_next_alarm_info(self):
        """
        計算並回傳下一個即將觸發的、且為啟用狀態的鬧鐘資訊。
        :return: 一個包含 'time_str' 和 'key' 的字典，或 None
        """
        now = datetime.now()
        
        # 取得所有啟用的鬧鐘
        enabled_alarms = []
        alarm_states = self.config.get('alarm_states', {})
        schedule_times = self.config.get('schedule', {})
        
        for key, is_enabled in alarm_states.items():
            if is_enabled:
                alarm_type, period_str = key.split('-')
                period = int(period_str)
                
                if alarm_type == 'start':
                    time_str = schedule_times.get('classStart', [])[period]
                else:
                    time_str = schedule_times.get('classEnd', [])[period]
                
                hour, minute = map(int, time_str.split(':'))
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 如果鬧鐘時間已過，則計算明天的時間
                if alarm_time < now:
                    alarm_time = alarm_time.replace(day=alarm_time.day + 1)
                    
                enabled_alarms.append({'time': alarm_time, 'key': key, 'time_str': time_str})

        if not enabled_alarms:
            return None
            
        # 找到時間最接近的鬧鐘
        next_alarm = min(enabled_alarms, key=lambda x: x['time'])
        
        alarm_type, period_str = next_alarm['key'].split('-')
        type_text = "上課" if alarm_type == 'start' else "下課"
        display_text = f"第{int(period_str) + 1}節{type_text} ({next_alarm['time_str']})"

        return display_text

    def trigger_next_alarm_manually(self):
        """
        手動觸發下一個即將到來的鬧鐘。
        """
        now = datetime.now()
        enabled_alarms = []
        alarm_states = self.config.get('alarm_states', {})
        schedule_times = self.config.get('schedule', {})
        
        for key, is_enabled in alarm_states.items():
            if is_enabled:
                alarm_type, period_str = key.split('-')
                period = int(period_str)
                time_str = schedule_times.get('classStart' if alarm_type == 'start' else 'classEnd', [])[period]
                hour, minute = map(int, time_str.split(':'))
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if alarm_time < now:
                    alarm_time = alarm_time.replace(day=alarm_time.day + 1)
                enabled_alarms.append({'time': alarm_time, 'type': alarm_type, 'period': period})

        if not enabled_alarms:
            logger.info("手動觸發失敗: 沒有已啟用的鬧鐘")
            return
            
        next_alarm = min(enabled_alarms, key=lambda x: x['time'])
        logger.info(f"手動觸發下一個鬧鐘: {next_alarm['type']}-{next_alarm['period']}")
        
        # 在新的背景線程中觸發，以模仿 schedule 的行為且不阻塞 UI
        thread = threading.Thread(target=self._trigger_alarm, args=(next_alarm['type'], next_alarm['period']))
        thread.daemon = True
        thread.start()


    def _setup_schedule(self):
        """根據設定檔來設定所有鬧鐘任務"""
        schedule.clear()
        
        alarm_times = self.config.get('schedule', {})
        class_starts = alarm_times.get('classStart', [])
        class_ends = alarm_times.get('classEnd', [])
        
        for i, time_str in enumerate(class_starts):
            schedule.every().day.at(time_str).do(self._trigger_alarm, alarm_type='start', period=i)
            
        for i, time_str in enumerate(class_ends):
            schedule.every().day.at(time_str).do(self._trigger_alarm, alarm_type='end', period=i)
            
        logger.info(f"已設定 {len(schedule.get_jobs())} 個鬧鐘任務")

    def _trigger_alarm(self, alarm_type, period):
        """觸發鬧鐘的中介函式，會檢查鬧鐘是否啟用"""
        alarm_key = f"{alarm_type}-{period}"
        alarm_states = self.config.get('alarm_states', {})
        
        if alarm_states.get(alarm_key, False):
            time_str = datetime.now().strftime("%H:%M:%S")
            logger.info(f"鬧鐘觸發: {alarm_key} at {time_str}")
            self.alarm_callback(alarm_type, period)
        else:
            logger.info(f"鬧鐘已停用，跳過: {alarm_key}")

    def _run_pending(self):
        """排程迴圈，由背景線程執行"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
        logger.info("排程器執行緒已停止")

    def start(self):
        """啟動排程器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_pending)
            self.thread.daemon = True
            self.thread.start()
            logger.info("排程器已啟動")

    def stop(self):
        """停止排程器"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join() # 等待線程結束
            logger.info("排程器已停止")

    def reload_schedule(self):
        """重新載入設定並更新排程"""
        logger.info("正在重新載入排程...")
        self._setup_schedule()
