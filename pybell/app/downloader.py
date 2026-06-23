import requests
import tempfile
import os
import logging

logger = logging.getLogger('SchoolBell.Downloader')

def download_audio_to_temp(url, timeout=10):
    """
    從指定的 URL 下載音訊檔案到一個暫存檔。

    :param url: 音訊檔案的 URL
    :param timeout: request 的超時秒數
    :return: 暫存檔案的路徑，如果下載失敗則回傳 None
    """
    try:
        logger.info(f"開始下載音訊檔案: {url}")
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()  # 如果 HTTP 狀態碼是 4xx 或 5xx，則拋出異常

        # 建立一個帶有正確副檔名的暫存檔
        # 這對某些播放器很重要
        suffix = os.path.splitext(url.split('/')[-1])[1] or '.mp3'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        with temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        
        logger.info(f"音訊檔案成功下載至: {temp_file.name}")
        return temp_file.name

    except requests.exceptions.Timeout:
        logger.error(f"下載超時: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"下載音訊時發生錯誤 ({url}): {e}")
        return None
    except IOError as e:
        logger.error(f"寫入暫存檔時發生錯誤: {e}")
        return None

def cleanup_temp_file(file_path):
    """
    刪除指定的暫存檔案。

    :param file_path: 要刪除的檔案路徑
    """
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
            logger.info(f"已清理暫存檔: {file_path}")
        except OSError as e:
            logger.error(f"刪除暫存檔時發生錯誤 ({file_path}): {e}")
