import os
import re
import json
import logging
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject
from config_manager import config_manager
from core.media_processor import MediaProcessor

class Translator(QObject):
    language_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dict = {}
        self.set_language(config_manager.get('app_language', 'tr'))

    def set_language(self, lang_code):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'lang', f'{lang_code}.json')
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.dict = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load language file {file_path}: {e}")
                self.dict = {}
        else:
            self.dict = {}
        self.language_changed.emit()

    def tr(self, key):
        return self.dict.get(key, key)

translator = Translator()

class LogSignals(QObject):
    log_msg = pyqtSignal(str, str, int, int)
    process_finished = pyqtSignal()

class QtLogHandler(logging.Handler):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.progress_pattern = re.compile(r'^(\d+)\s*/\s*(\d+)\s*(?:remaining|left)\s*-\s*(.*)', re.IGNORECASE)

    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        
        match = self.progress_pattern.search(msg)
        if match:
            total = int(match.group(1))
            remaining = int(match.group(2))
            clean_msg = match.group(3)
            current = total - remaining
            self.signals.log_msg.emit(clean_msg, level, current, total)
        else:
            self.signals.log_msg.emit(msg, level, -1, -1)

class ProcessingThread(QThread):
    def __init__(self, signals, local_m3u_path=None):
        super().__init__()
        self.signals = signals
        self.local_m3u_path = local_m3u_path
        self.processor = MediaProcessor(signals=signals)

    def run(self):
        try:
            import asyncio
            asyncio.run(self.processor.run(self.local_m3u_path))
        except Exception as e:
            logging.error(f"Kritik Hata: {str(e)}")
        finally:
            self.signals.process_finished.emit()

    def pause(self):
        if self.processor:
            self.processor.is_paused = True

    def resume(self):
        if self.processor:
            self.processor.is_paused = False

    def cancel(self):
        if self.processor:
            self.processor.is_stopped = True

