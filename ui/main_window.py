import os
import logging
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QApplication, QStyle
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, setTheme, Theme, SubtitleLabel
)
from qfluentwidgets import FluentIcon as FIF
from config_manager import config_manager
from ui.helpers import translator
from ui.settings_tab import SettingsInterface
from ui.engine_tab import ProcessingInterface

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        # Apply theme
        theme = config_manager.get('theme')
        if theme == 'Light':
            setTheme(Theme.LIGHT)
        elif theme == 'Dark':
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.AUTO)
            
        self.setWindowTitle(translator.tr('title_main_window'))
        self.resize(900, 700)
        
        self.processing_interface = ProcessingInterface(self)
        self.settings_interface = SettingsInterface(self)
        
        self.initNavigation()
        translator.language_changed.connect(self.update_texts)
        
        self.setup_system_tray()
        self.setup_cron_timer()

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        show_action = QAction("Göster", self)
        show_action.triggered.connect(self.show)
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def quit_app(self):
        self._is_quitting = True
        if self.processing_interface.thread and self.processing_interface.thread.isRunning():
            self.processing_interface.thread.cancel()
            self.processing_interface.thread.wait()
        QApplication.instance().quit()

    def setup_cron_timer(self):
        self.cron_timer = QTimer(self)
        self.cron_timer.timeout.connect(self.check_cron)
        self.cron_timer.start(60000) # Check every 60 seconds

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def closeEvent(self, event):
        if hasattr(self, '_is_quitting') and self._is_quitting:
            event.accept()
            return
            
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Arka Planda Çalışıyor",
            "Uygulama sistem tepsisine küçültüldü.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def check_cron(self):
        config_manager.load_config()
        auto_sync = config_manager.get('auto_sync', False)
        sync_time = config_manager.get('sync_time', '04:00')
        
        if auto_sync:
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            if current_time_str == sync_time:
                if not hasattr(self, 'last_sync_time') or self.last_sync_time != current_time_str:
                    self.last_sync_time = current_time_str
                    if self.processing_interface.start_btn.isEnabled():
                        logging.info(f"Cron triggered at {current_time_str}. Starting auto-sync...")
                        self.processing_interface.start_processing()
                    else:
                        logging.warning(f"Cron triggered at {current_time_str} but processing is already running.")

    def initNavigation(self):
        self.addSubInterface(self.processing_interface, FIF.PLAY, translator.tr('title_processing'))
        self.addSubInterface(self.settings_interface, FIF.SETTING, translator.tr('title_settings'))

    def update_texts(self):
        self.setWindowTitle(translator.tr('title_main_window'))
        try:
            item_processing = self.navigationInterface.widget(self.processing_interface.objectName())
            if item_processing:
                item_processing.setText(translator.tr('title_processing'))
                
            item_settings = self.navigationInterface.widget(self.settings_interface.objectName())
            if item_settings:
                item_settings.setText(translator.tr('title_settings'))
        except Exception as e:
            logging.error(f"Navigation translation failed: {e}")
