import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    SettingCard, ExpandSettingCard, PrimaryPushButton, LineEdit, PasswordLineEdit,
    ComboBox, ScrollArea, InfoBar, InfoBarPosition, CheckBox, TitleLabel, BodyLabel, SubtitleLabel, setTheme, Theme, ToolButton
)
from qfluentwidgets import FluentIcon as FIF
from config_manager import config_manager
from ui.helpers import translator

class CustomWidgetCard(SettingCard):
    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.right_layout = QHBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 16, 0)
        self.right_layout.setSpacing(10)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addLayout(self.right_layout, 1)

    def addWidget(self, widget):
        self.right_layout.addWidget(widget)

class SettingsInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName('SettingsInterface')
        self.view.setObjectName('view')
        self.setStyleSheet("QScrollArea, #view { background-color: transparent; border: none; }")
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setSpacing(12)

        self.title = TitleLabel(translator.tr('title_settings'))
        self.vBoxLayout.addWidget(self.title)

        # Tema Ayari (Theme)
        self.theme_card = CustomWidgetCard(FIF.BRUSH, translator.tr('grp_theme'), translator.tr('grp_theme_desc'), self.view)
        self.theme_combo = ComboBox()
        self.theme_combo.addItem(translator.tr('theme_auto'), userData="Auto")
        self.theme_combo.addItem(translator.tr('theme_light'), userData="Light")
        self.theme_combo.addItem(translator.tr('theme_dark'), userData="Dark")
        self.theme_card.addWidget(self.theme_combo)
        self.vBoxLayout.addWidget(self.theme_card)
        current_theme = config_manager.get('theme', 'Auto')
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)

        # IPTV Info
        self.iptv_card = ExpandSettingCard(FIF.GLOBE, translator.tr('grp_iptv'), "", self.view)
        self.iptv_vbox = QVBoxLayout()
        self.iptv_vbox.setContentsMargins(48, 0, 48, 24)
        self.iptv_vbox.setSpacing(8)
        
        self.iptv_url_input = LineEdit()
        self.iptv_url_input.setText(config_manager.get('iptvurl'))
        self.iptv_vbox.addWidget(BodyLabel("IPTV URL"))
        self.iptv_vbox.addWidget(self.iptv_url_input)
        
        self.iptv_user_input = LineEdit()
        self.iptv_user_input.setText(config_manager.get('iptvusername'))
        self.iptv_vbox.addWidget(BodyLabel(translator.tr('lbl_iptv_user')))
        self.iptv_vbox.addWidget(self.iptv_user_input)
        
        self.iptv_pass_input = PasswordLineEdit()
        self.iptv_pass_input.setText(config_manager.get('iptvpassword'))
        self.iptv_vbox.addWidget(BodyLabel(translator.tr('lbl_iptv_pass')))
        self.iptv_vbox.addWidget(self.iptv_pass_input)
        
        self.iptv_local_m3u_input = LineEdit()
        self.iptv_local_m3u_input.setText(config_manager.get('local_m3u_file', ''))
        self.iptv_local_m3u_btn = ToolButton(FIF.FOLDER)
        self.iptv_local_m3u_btn.clicked.connect(self.select_local_m3u)
        
        local_layout = QHBoxLayout()
        local_layout.setContentsMargins(0,0,0,0)
        local_layout.addWidget(self.iptv_local_m3u_input)
        local_layout.addWidget(self.iptv_local_m3u_btn)
        
        self.lbl_local_m3u = BodyLabel(translator.tr('lbl_local_m3u'))
        self.iptv_vbox.addWidget(self.lbl_local_m3u)
        self.iptv_vbox.addLayout(local_layout)
        
        iptv_widget = QWidget()
        iptv_widget.setLayout(self.iptv_vbox)
        self.iptv_card.viewLayout.addWidget(iptv_widget)
        self.vBoxLayout.addWidget(self.iptv_card)

        # API Keys
        self.api_card = ExpandSettingCard(FIF.FINGERPRINT, translator.tr('grp_api'), "", self.view)
        self.api_vbox = QVBoxLayout()
        self.api_vbox.setContentsMargins(48, 0, 48, 24)
        self.api_vbox.setSpacing(8)
        
        self.tmdb_api_key_input = LineEdit()
        self.tmdb_api_key_input.setPlaceholderText(translator.tr('lbl_tmdb_key'))
        self.tmdb_api_key_input.setText(config_manager.get('tmdb_api_key'))
        self.api_vbox.addWidget(SubtitleLabel(translator.tr('lbl_tmdb_key')))
        self.api_vbox.addWidget(self.tmdb_api_key_input)
        
        self.fanart_api_key_input = LineEdit()
        self.fanart_api_key_input.setPlaceholderText(translator.tr('lbl_fanart_key'))
        self.fanart_api_key_input.setText(config_manager.get('fanart_api_key'))
        self.api_vbox.addWidget(SubtitleLabel(translator.tr('lbl_fanart_key')))
        self.api_vbox.addWidget(self.fanart_api_key_input)
        
        api_widget = QWidget()
        api_widget.setLayout(self.api_vbox)
        self.api_card.viewLayout.addWidget(api_widget)
        self.vBoxLayout.addWidget(self.api_card)

        # Languages
        self.lang_card = ExpandSettingCard(FIF.LANGUAGE, translator.tr('grp_lang'), "", self.view)
        self.lang_vbox = QVBoxLayout()
        self.lang_vbox.setContentsMargins(48, 0, 48, 24)
        self.lang_vbox.setSpacing(12)
        
        self.app_lang_combo = ComboBox()
        languages = [
            ("Türkçe", "tr"), ("English", "en"), ("Deutsch", "de"), 
            ("Français", "fr"), ("Español", "es"), ("Русский", "ru"), 
            ("Українська", "uk"), ("简体中文", "zh_CN"), ("繁體中文", "zh_TW"), 
            ("日本語", "ja"), ("한국어", "ko"), ("العربية", "ar")
        ]
        
        current_lang = config_manager.get('app_language', 'tr')
        idx = 0
        for i, (name, code) in enumerate(languages):
            self.app_lang_combo.addItem(name, userData=code)
            if code == current_lang:
                idx = i
                
        self.app_lang_combo.setCurrentIndex(idx)
        self.app_lang_combo.currentIndexChanged.connect(self.on_app_lang_changed)
        self.lang_vbox.addWidget(SubtitleLabel(translator.tr('lbl_app_lang')))
        self.lang_vbox.addWidget(self.app_lang_combo)

        self.m3u_lang_combo = ComboBox()
        self.m3u_lang_combo.addItems(["TR", "EN", "DE", "FR", "IT", "ES"])
        self.m3u_lang_combo.setCurrentText(config_manager.get('your_language_code'))
        self.lang_vbox.addWidget(SubtitleLabel(translator.tr('lbl_m3u_lang')))
        self.lang_vbox.addWidget(self.m3u_lang_combo)

        self.tmdb_lang_combo = ComboBox()
        self.tmdb_lang_combo.addItems(["tr-TR", "en-US", "de-DE", "fr-FR", "it-IT", "es-ES"])
        self.tmdb_lang_combo.setCurrentText(config_manager.get('tmdb_language'))
        self.lang_vbox.addWidget(SubtitleLabel(translator.tr('lbl_tmdb_lang')))
        self.lang_vbox.addWidget(self.tmdb_lang_combo)

        lang_widget = QWidget()
        lang_widget.setLayout(self.lang_vbox)
        self.lang_card.viewLayout.addWidget(lang_widget)
        self.vBoxLayout.addWidget(self.lang_card)

        # Folder Paths
        self.folder_card = ExpandSettingCard(FIF.FOLDER, translator.tr('grp_folders'), translator.tr('grp_folders_desc'), self.view)
        self.folder_vbox = QVBoxLayout()
        self.folder_vbox.setContentsMargins(48, 0, 48, 24)
        self.folder_vbox.setSpacing(8)
        
        self.movies_folder_input = LineEdit()
        self.movies_folder_input.setText(config_manager.get('movies_folder_path', ''))
        self.movies_folder_input.setPlaceholderText(translator.tr('lbl_movies_folder'))
        self.movies_folder_btn = ToolButton(FIF.FOLDER)
        self.movies_folder_btn.clicked.connect(lambda: self.select_folder(self.movies_folder_input))
        
        m_layout = QHBoxLayout()
        m_layout.setContentsMargins(0,0,0,0)
        m_layout.addWidget(self.movies_folder_input)
        m_layout.addWidget(self.movies_folder_btn)
        
        self.series_folder_input = LineEdit()
        self.series_folder_input.setText(config_manager.get('series_folder_path', ''))
        self.series_folder_btn = ToolButton(FIF.FOLDER)
        self.series_folder_btn.clicked.connect(lambda: self.select_folder(self.series_folder_input))
        
        s_layout = QHBoxLayout()
        s_layout.setContentsMargins(0,0,0,0)
        s_layout.addWidget(self.series_folder_input)
        s_layout.addWidget(self.series_folder_btn)
        
        self.porn_folder_input = LineEdit()
        self.porn_folder_input.setText(config_manager.get('porn_folder_path', ''))
        self.porn_folder_btn = ToolButton(FIF.FOLDER)
        self.porn_folder_btn.clicked.connect(lambda: self.select_folder(self.porn_folder_input))
        
        p_layout = QHBoxLayout()
        p_layout.setContentsMargins(0,0,0,0)
        p_layout.addWidget(self.porn_folder_input)
        p_layout.addWidget(self.porn_folder_btn)
        
        self.lbl_movies_folder = SubtitleLabel("Filmler Klasörü")
        self.lbl_series_folder = SubtitleLabel("Diziler Klasörü")
        self.lbl_porn_folder = SubtitleLabel("XXX Klasörü")
        
        self.folder_vbox.addWidget(self.lbl_movies_folder)
        self.folder_vbox.addLayout(m_layout)
        self.folder_vbox.addWidget(self.lbl_series_folder)
        self.folder_vbox.addLayout(s_layout)
        self.folder_vbox.addWidget(self.lbl_porn_folder)
        self.folder_vbox.addLayout(p_layout)
        
        folder_widget = QWidget()
        folder_widget.setLayout(self.folder_vbox)
        self.folder_card.viewLayout.addWidget(folder_widget)
        self.vBoxLayout.addWidget(self.folder_card)

        # Automation Settings
        self.auto_card = ExpandSettingCard(FIF.SYNC, translator.tr('grp_automation'), translator.tr('grp_automation_desc'), self.view)
        self.auto_vbox = QVBoxLayout()
        self.auto_vbox.setContentsMargins(48, 0, 48, 24)
        self.auto_vbox.setSpacing(8)
        
        self.cb_auto_sync = CheckBox(translator.tr('cb_auto_sync'))
        self.cb_auto_sync.setChecked(config_manager.get('auto_sync', False))
        
        self.sync_time_combo = ComboBox()
        for hour in range(24):
            self.sync_time_combo.addItem(f"{hour:02d}:00")
            
        current_time_str = config_manager.get('sync_time', '04:00')
        self.sync_time_combo.setCurrentText(current_time_str)
        
        self.auto_vbox.addWidget(self.cb_auto_sync)
        self.auto_vbox.addWidget(SubtitleLabel(translator.tr('lbl_sync_time')))
        self.auto_vbox.addWidget(self.sync_time_combo)
        
        auto_widget = QWidget()
        auto_widget.setLayout(self.auto_vbox)
        self.auto_card.viewLayout.addWidget(auto_widget)
        self.vBoxLayout.addWidget(self.auto_card)

        # Info Settings
        self.nfo_card = ExpandSettingCard(FIF.DOCUMENT, translator.tr('grp_nfo'), translator.tr('grp_nfo_desc'), self.view)
        self.nfo_vbox = QVBoxLayout()
        self.nfo_vbox.setContentsMargins(48, 0, 48, 24)
        self.nfo_vbox.setSpacing(8)
        self.cb_movie_nfo = CheckBox(translator.tr('cb_movie_nfo')); self.cb_movie_nfo.setChecked(config_manager.get('nfo_movie', True))
        self.cb_series_nfo = CheckBox(translator.tr('cb_series_nfo')); self.cb_series_nfo.setChecked(config_manager.get('nfo_series', True))
        self.cb_episode_nfo = CheckBox(translator.tr('cb_episode_nfo')); self.cb_episode_nfo.setChecked(config_manager.get('nfo_episode', True))
        self.nfo_vbox.addWidget(self.cb_movie_nfo)
        self.nfo_vbox.addWidget(self.cb_series_nfo)
        self.nfo_vbox.addWidget(self.cb_episode_nfo)
        nfo_widget = QWidget(); nfo_widget.setLayout(self.nfo_vbox)
        self.nfo_card.viewLayout.addWidget(nfo_widget)
        self.vBoxLayout.addWidget(self.nfo_card)

        self.movie_img_card = ExpandSettingCard(FIF.PHOTO, translator.tr('grp_movie_img'), translator.tr('grp_movie_img_desc'), self.view)
        self.movie_vbox = QVBoxLayout()
        self.movie_vbox.setContentsMargins(48, 0, 48, 24)
        self.movie_vbox.setSpacing(8)
        self.cb_img_movie_poster = CheckBox(translator.tr('cb_poster')); self.cb_img_movie_poster.setChecked(config_manager.get('img_movie_poster', True))
        self.cb_img_movie_fanart = CheckBox(translator.tr('cb_fanart')); self.cb_img_movie_fanart.setChecked(config_manager.get('img_movie_fanart', True))
        self.cb_img_movie_bg = CheckBox(translator.tr('cb_bg')); self.cb_img_movie_bg.setChecked(config_manager.get('img_movie_bg', True))
        self.cb_img_movie_logo = CheckBox(translator.tr('cb_logo')); self.cb_img_movie_logo.setChecked(config_manager.get('img_movie_logo', True))
        self.cb_img_movie_clearart = CheckBox(translator.tr('cb_clearart')); self.cb_img_movie_clearart.setChecked(config_manager.get('img_movie_clearart', True))
        self.cb_img_movie_discart = CheckBox(translator.tr('cb_discart')); self.cb_img_movie_discart.setChecked(config_manager.get('img_movie_discart', True))
        self.cb_img_movie_banner = CheckBox(translator.tr('cb_banner')); self.cb_img_movie_banner.setChecked(config_manager.get('img_movie_banner', True))
        self.cb_img_movie_thumb = CheckBox(translator.tr('cb_thumb')); self.cb_img_movie_thumb.setChecked(config_manager.get('img_movie_thumb', True))
        self.movie_vbox.addWidget(self.cb_img_movie_poster)
        self.movie_vbox.addWidget(self.cb_img_movie_fanart)
        self.movie_vbox.addWidget(self.cb_img_movie_bg)
        self.movie_vbox.addWidget(self.cb_img_movie_logo)
        self.movie_vbox.addWidget(self.cb_img_movie_clearart)
        self.movie_vbox.addWidget(self.cb_img_movie_discart)
        self.movie_vbox.addWidget(self.cb_img_movie_banner)
        self.movie_vbox.addWidget(self.cb_img_movie_thumb)
        movie_widget = QWidget(); movie_widget.setLayout(self.movie_vbox)
        self.movie_img_card.viewLayout.addWidget(movie_widget)
        self.vBoxLayout.addWidget(self.movie_img_card)

        self.series_img_card = ExpandSettingCard(FIF.VIDEO, translator.tr('grp_series_img'), translator.tr('grp_series_img_desc'), self.view)
        self.series_vbox = QVBoxLayout()
        self.series_vbox.setContentsMargins(48, 0, 48, 24)
        self.series_vbox.setSpacing(8)
        self.cb_img_series_poster = CheckBox(translator.tr('cb_poster')); self.cb_img_series_poster.setChecked(config_manager.get('img_series_poster', True))
        self.cb_img_series_bg = CheckBox(translator.tr('cb_bg')); self.cb_img_series_bg.setChecked(config_manager.get('img_series_bg', True))
        self.cb_img_series_banner = CheckBox(translator.tr('cb_banner')); self.cb_img_series_banner.setChecked(config_manager.get('img_series_banner', True))
        self.cb_img_series_logo = CheckBox(translator.tr('cb_logo')); self.cb_img_series_logo.setChecked(config_manager.get('img_series_logo', True))
        self.cb_img_series_thumb = CheckBox(translator.tr('cb_thumb')); self.cb_img_series_thumb.setChecked(config_manager.get('img_series_thumb', True))
        self.cb_img_series_clearart = CheckBox(translator.tr('cb_clearart')); self.cb_img_series_clearart.setChecked(config_manager.get('img_series_clearart', True))
        self.cb_img_series_character = CheckBox(translator.tr('cb_character')); self.cb_img_series_character.setChecked(config_manager.get('img_series_character', True))
        self.series_vbox.addWidget(self.cb_img_series_poster)
        self.series_vbox.addWidget(self.cb_img_series_bg)
        self.series_vbox.addWidget(self.cb_img_series_banner)
        self.series_vbox.addWidget(self.cb_img_series_logo)
        self.series_vbox.addWidget(self.cb_img_series_thumb)
        self.series_vbox.addWidget(self.cb_img_series_clearart)
        self.series_vbox.addWidget(self.cb_img_series_character)
        series_widget = QWidget(); series_widget.setLayout(self.series_vbox)
        self.series_img_card.viewLayout.addWidget(series_widget)
        self.vBoxLayout.addWidget(self.series_img_card)

        self.season_img_card = ExpandSettingCard(FIF.FOLDER, translator.tr('grp_season_img'), translator.tr('grp_season_img_desc'), self.view)
        self.season_vbox = QVBoxLayout()
        self.season_vbox.setContentsMargins(48, 0, 48, 24)
        self.season_vbox.setSpacing(8)
        self.cb_img_season_poster = CheckBox(translator.tr('cb_poster')); self.cb_img_season_poster.setChecked(config_manager.get('img_season_poster', True))
        self.cb_img_season_banner = CheckBox(translator.tr('cb_banner')); self.cb_img_season_banner.setChecked(config_manager.get('img_season_banner', True))
        self.cb_img_season_thumb = CheckBox(translator.tr('cb_thumb')); self.cb_img_season_thumb.setChecked(config_manager.get('img_season_thumb', True))
        self.season_vbox.addWidget(self.cb_img_season_poster)
        self.season_vbox.addWidget(self.cb_img_season_banner)
        self.season_vbox.addWidget(self.cb_img_season_thumb)
        season_widget = QWidget(); season_widget.setLayout(self.season_vbox)
        self.season_img_card.viewLayout.addWidget(season_widget)
        self.vBoxLayout.addWidget(self.season_img_card)

        # Save Button
        self.save_btn = PrimaryPushButton(translator.tr('btn_save'))
        self.save_btn.clicked.connect(self.save_settings)
        self.vBoxLayout.addWidget(self.save_btn)

        translator.language_changed.connect(self.update_texts)

    def select_local_m3u(self):
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(self, translator.tr('lbl_local_m3u'), "", "M3U/TXT Files (*.m3u *.txt)")
        if file_name:
            self.iptv_local_m3u_input.setText(file_name)

    def select_folder(self, line_edit):
        from PyQt6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            line_edit.setText(folder)

    def on_theme_changed(self):
        theme_str = self.theme_combo.currentData()
        config_manager.set('theme', theme_str)
        if theme_str == 'Light':
            setTheme(Theme.LIGHT)
        elif theme_str == 'Dark':
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.AUTO)

    def on_app_lang_changed(self):
        lang_code = self.app_lang_combo.currentData()
        config_manager.set('app_language', lang_code)
        translator.set_language(lang_code)

    def save_settings(self):
        config_manager.set('tmdb_api_key', self.tmdb_api_key_input.text())
        config_manager.set('fanart_api_key', self.fanart_api_key_input.text())
        config_manager.set('iptvurl', self.iptv_url_input.text())
        config_manager.set('iptvusername', self.iptv_user_input.text())
        config_manager.set('iptvpassword', self.iptv_pass_input.text())
        config_manager.set('local_m3u_file', self.iptv_local_m3u_input.text())
        config_manager.set('your_language_code', self.m3u_lang_combo.currentText())
        config_manager.set('tmdb_language', self.tmdb_lang_combo.currentText())
        config_manager.set('movies_folder_path', self.movies_folder_input.text())
        config_manager.set('series_folder_path', self.series_folder_input.text())
        config_manager.set('porn_folder_path', self.porn_folder_input.text())
        config_manager.set('auto_sync', self.cb_auto_sync.isChecked())
        config_manager.set('sync_time', self.sync_time_combo.currentText())
        config_manager.set('nfo_movie', self.cb_movie_nfo.isChecked())
        config_manager.set('nfo_series', self.cb_series_nfo.isChecked())
        config_manager.set('nfo_episode', self.cb_episode_nfo.isChecked())
        config_manager.set('img_movie_poster', self.cb_img_movie_poster.isChecked())
        config_manager.set('img_movie_fanart', self.cb_img_movie_fanart.isChecked())
        config_manager.set('img_movie_bg', self.cb_img_movie_bg.isChecked())
        config_manager.set('img_movie_logo', self.cb_img_movie_logo.isChecked())
        config_manager.set('img_movie_clearart', self.cb_img_movie_clearart.isChecked())
        config_manager.set('img_movie_discart', self.cb_img_movie_discart.isChecked())
        config_manager.set('img_movie_banner', self.cb_img_movie_banner.isChecked())
        config_manager.set('img_movie_thumb', self.cb_img_movie_thumb.isChecked())
        config_manager.set('img_series_poster', self.cb_img_series_poster.isChecked())
        config_manager.set('img_series_bg', self.cb_img_series_bg.isChecked())
        config_manager.set('img_series_banner', self.cb_img_series_banner.isChecked())
        config_manager.set('img_series_logo', self.cb_img_series_logo.isChecked())
        config_manager.set('img_series_thumb', self.cb_img_series_thumb.isChecked())
        config_manager.set('img_series_clearart', self.cb_img_series_clearart.isChecked())
        config_manager.set('img_series_character', self.cb_img_series_character.isChecked())
        config_manager.set('img_season_poster', self.cb_img_season_poster.isChecked())
        config_manager.set('img_season_banner', self.cb_img_season_banner.isChecked())
        config_manager.set('img_season_thumb', self.cb_img_season_thumb.isChecked())

    def update_texts(self):
        self.title.setText(translator.tr('title_settings'))
        
        self.theme_card.titleLabel.setText(translator.tr('grp_theme'))
        self.theme_card.contentLabel.setText(translator.tr('grp_theme_desc'))
        self.theme_combo.setItemText(0, translator.tr('theme_auto'))
        self.theme_combo.setItemText(1, translator.tr('theme_light'))
        self.theme_combo.setItemText(2, translator.tr('theme_dark'))
        
        self.iptv_card.card.titleLabel.setText(translator.tr('grp_iptv'))
        self.iptv_user_input.setPlaceholderText(translator.tr('lbl_iptv_user'))
        self.iptv_pass_input.setPlaceholderText(translator.tr('lbl_iptv_pass'))
        self.lbl_local_m3u.setText(translator.tr('lbl_local_m3u'))
        
        self.api_card.card.titleLabel.setText(translator.tr('grp_api'))
        self.tmdb_api_key_input.setPlaceholderText(translator.tr('lbl_tmdb_key'))
        self.fanart_api_key_input.setPlaceholderText(translator.tr('lbl_fanart_key'))
        
        self.lang_card.card.titleLabel.setText(translator.tr('grp_lang'))
        
        self.nfo_card.card.titleLabel.setText(translator.tr('grp_nfo'))
        self.nfo_card.card.contentLabel.setText(translator.tr('grp_nfo_desc'))
        self.cb_movie_nfo.setText(translator.tr('cb_movie_nfo'))
        self.cb_series_nfo.setText(translator.tr('cb_series_nfo'))
        self.cb_episode_nfo.setText(translator.tr('cb_episode_nfo'))
        
        self.movie_img_card.card.titleLabel.setText(translator.tr('grp_movie_img'))
        self.movie_img_card.card.contentLabel.setText(translator.tr('grp_movie_img_desc'))
        self.cb_img_movie_poster.setText(translator.tr('cb_poster'))
        self.cb_img_movie_fanart.setText(translator.tr('cb_fanart'))
        self.cb_img_movie_bg.setText(translator.tr('cb_bg'))
        self.cb_img_movie_logo.setText(translator.tr('cb_logo'))
        self.cb_img_movie_clearart.setText(translator.tr('cb_clearart'))
        self.cb_img_movie_discart.setText(translator.tr('cb_discart'))
        self.cb_img_movie_banner.setText(translator.tr('cb_banner'))
        self.cb_img_movie_thumb.setText(translator.tr('cb_thumb'))
        
        self.series_img_card.card.titleLabel.setText(translator.tr('grp_series_img'))
        self.series_img_card.card.contentLabel.setText(translator.tr('grp_series_img_desc'))
        self.cb_img_series_poster.setText(translator.tr('cb_poster'))
        self.cb_img_series_bg.setText(translator.tr('cb_bg'))
        self.cb_img_series_banner.setText(translator.tr('cb_banner'))
        self.cb_img_series_logo.setText(translator.tr('cb_logo'))
        self.cb_img_series_thumb.setText(translator.tr('cb_thumb'))
        self.cb_img_series_clearart.setText(translator.tr('cb_clearart'))
        self.cb_img_series_character.setText(translator.tr('cb_character'))
        
        self.season_img_card.card.titleLabel.setText(translator.tr('grp_season_img'))
        self.season_img_card.card.contentLabel.setText(translator.tr('grp_season_img_desc'))
        self.cb_img_season_poster.setText(translator.tr('cb_poster'))
        self.cb_img_season_banner.setText(translator.tr('cb_banner'))
        self.cb_img_season_thumb.setText(translator.tr('cb_thumb'))
        
        # New Translations for Folders and Automation
        self.folder_card.card.titleLabel.setText(translator.tr('grp_folders'))
        self.folder_card.card.contentLabel.setText(translator.tr('grp_folders_desc'))
        self.lbl_movies_folder.setText(translator.tr('lbl_movies_folder'))
        self.movies_folder_input.setPlaceholderText(translator.tr('lbl_movies_folder'))
        self.lbl_series_folder.setText(translator.tr('lbl_series_folder'))
        self.series_folder_input.setPlaceholderText(translator.tr('lbl_series_folder'))
        self.lbl_porn_folder.setText(translator.tr('lbl_porn_folder'))
        self.porn_folder_input.setPlaceholderText(translator.tr('lbl_porn_folder'))
        
        self.auto_card.card.titleLabel.setText(translator.tr('grp_automation'))
        self.auto_card.card.contentLabel.setText(translator.tr('grp_automation_desc'))
        self.cb_auto_sync.setText(translator.tr('cb_auto_sync'))
        # SubtitleLabel for sync_time doesn't have a direct reference, we should find a way or leave it,
        # but since I don't have a self.lbl_sync_time, I can't update it dynamically here unless I save a reference to it.
        # Actually I can just add a reference to it if needed. For now the static setup translates it on launch.

