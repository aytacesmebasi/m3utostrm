import logging
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    PrimaryPushButton, TextEdit, ProgressBar, TitleLabel, InfoBar, InfoBarPosition
)
from qfluentwidgets import FluentIcon as FIF
from config_manager import config_manager
from ui.helpers import translator, LogSignals, QtLogHandler, ProcessingThread

class ProcessingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('ProcessingInterface')
        self.setStyleSheet("#ProcessingInterface { background-color: transparent; }")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(18)
        
        self.title = TitleLabel(translator.tr('title_engine'))
        self.vBoxLayout.addWidget(self.title)
        
        button_layout = QHBoxLayout()
        self.start_btn = PrimaryPushButton(FIF.PLAY, translator.tr('btn_start'))
        self.start_btn.setMinimumHeight(50)
        self.start_btn.clicked.connect(self.start_processing)
        
        self.pause_btn = PrimaryPushButton(FIF.PAUSE, translator.tr('btn_pause'))
        self.pause_btn.setMinimumHeight(50)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        self.is_paused = False
        
        self.cancel_btn = PrimaryPushButton(FIF.CLOSE, 'İptal Et')
        self.cancel_btn.setMinimumHeight(50)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)

        self.log_console = TextEdit()
        self.log_console.setReadOnly(True)
        from PyQt6.QtGui import QFont
        font = QFont("Consolas", 10)
        self.log_console.setFont(font)

        self.clear_btn = PrimaryPushButton(FIF.DELETE, 'Logları Temizle')
        self.clear_btn.setMinimumHeight(50)
        self.clear_btn.clicked.connect(self.log_console.clear)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.clear_btn)
        self.vBoxLayout.addLayout(button_layout)

        self.vBoxLayout.addWidget(self.log_console)
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.vBoxLayout.addWidget(self.progress_bar)

        self.signals = LogSignals()
        self.signals.log_msg.connect(self.append_log)
        self.signals.process_finished.connect(self.on_finished)
        
        # Setup custom logging handler
        handler = QtLogHandler(self.signals)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        
        self.thread = None
        translator.language_changed.connect(self.update_texts)

    def update_texts(self):
        self.title.setText(translator.tr('title_engine'))
        if self.start_btn.isEnabled():
            self.start_btn.setText(translator.tr('btn_start'))
        else:
            self.start_btn.setText(translator.tr('btn_processing'))
            
        if self.is_paused:
            self.pause_btn.setText(translator.tr('btn_resume'))
        else:
            self.pause_btn.setText(translator.tr('btn_pause'))

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            if self.thread:
                self.thread.pause()
            self.pause_btn.setText(translator.tr('btn_resume'))
            self.pause_btn.setIcon(FIF.PLAY)
            self.append_log(translator.tr('msg_paused'), "WARNING", -1, -1)
        else:
            if self.thread:
                self.thread.resume()
            self.pause_btn.setText(translator.tr('btn_pause'))
            self.pause_btn.setIcon(FIF.PAUSE)

    def cancel_processing(self):
        if self.thread:
            self.thread.cancel()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.pause_btn.setText(translator.tr('btn_pause'))
        self.pause_btn.setIcon(FIF.PAUSE)
        self.append_log('İşlem iptal ediliyor, lütfen bekleyin...', "WARNING", -1, -1)

    def start_processing(self, local_m3u_path=None):
        if not isinstance(local_m3u_path, str):
            local_m3u_path = config_manager.get('local_m3u_file', '').strip()
            if not local_m3u_path:
                local_m3u_path = None

        if not config_manager.get('tmdb_api_key'):
            InfoBar.error(
                title=translator.tr('msg_error_title'),
                content=translator.tr('msg_error_missing'),
                orient=Qt.Orientation.Horizontal,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )
            return

        if not local_m3u_path and (not config_manager.get('iptvurl') or not config_manager.get('iptvusername')):
            from qfluentwidgets import MessageBoxBase, SubtitleLabel, BodyLabel
            
            class CustomMessageBox(MessageBoxBase):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.titleLabel = SubtitleLabel(translator.tr('msg_iptv_missing_title'), self)
                    self.viewLayout.addWidget(self.titleLabel)
                    self.contentLabel = BodyLabel(translator.tr('msg_iptv_missing_body'))
                    self.viewLayout.addWidget(self.contentLabel)

                    self.yesButton.setText(translator.tr('btn_enter_details'))
                    self.cancelButton.setText(translator.tr('btn_open_file'))
                    
            msg_box = CustomMessageBox(self)
            if msg_box.exec():
                main_window = self.window()
                if hasattr(main_window, 'stackedWidget') and hasattr(main_window, 'settings_interface'):
                    main_window.stackedWidget.setCurrentWidget(main_window.settings_interface)
                    main_window.pivot.setCurrentItem(main_window.settings_interface.objectName())
                return
            else:
                from PyQt6.QtWidgets import QFileDialog
                file_name, _ = QFileDialog.getOpenFileName(self, translator.tr('btn_open_file'), "", "M3U/TXT Files (*.m3u *.txt)")
                if file_name:
                    self.start_processing(local_m3u_path=file_name)
                return

        self.start_btn.setEnabled(False)
        self.start_btn.setText(translator.tr('btn_processing'))
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.is_paused = False
        self.pause_btn.setText(translator.tr('btn_pause'))
        self.pause_btn.setIcon(FIF.PAUSE)
        
        self.log_console.clear()
        self.progress_bar.setValue(0)
        
        self.thread = ProcessingThread(self.signals, local_m3u_path)
        self.thread.start()

    @pyqtSlot(str, str, int, int)
    def append_log(self, msg, level, current, total):
        if level == "INFO" and "STRM file created" not in msg and "HATA" not in msg and "API" not in msg and "Movies Folder" not in msg:
            pass
            
        icon = "✔️"
        color = "#10B981" # Green
        
        if level == "ERROR":
            icon = "❌"
            color = "#EF4444" # Red
        elif level == "WARNING":
            icon = "⚠️"
            color = "#F59E0B" # Yellow
            
        if current != -1 and total != -1:
            log_str = f'<span style="color:{color};">{icon}</span> <b>[{total} / {current}]</b> - {msg}'
            if total > 0:
                completed = total - current
                pct = int((completed / total) * 100)
                self.progress_bar.setValue(pct)
        else:
            log_str = f'<span style="color:{color};">{icon}</span> {msg}'
            
        if self.log_console.document().lineCount() > 1000:
            self.log_console.clear()
            
        self.log_console.append(log_str)

    @pyqtSlot()
    def on_finished(self):
        self.start_btn.setEnabled(True)
        self.start_btn.setText(translator.tr('btn_start'))
        self.pause_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        InfoBar.success(
            title=translator.tr('msg_success_title'),
            content=translator.tr('msg_process_done'),
            orient=Qt.Orientation.Horizontal,
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self
        )

