import os

langs = {
    'en': 'English',
    'tr': 'Türkçe',
    'de': 'Deutsch',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'ru': 'Русский',
    'uk': 'Українська',
    'ar': 'العربية',
    'ja': '日本語',
    'ko': '한국어',
    'zh_CN': '简体中文',
    'zh_TW': '繁體中文'
}

translations = {
    'en': {
        'desc_short': 'A powerful tool to convert your IPTV M3U playlists into STRM files for media centers like Kodi, Jellyfin, and Emby with rich TMDb metadata.',
        'features_title': 'Features',
        'feat_1_title': 'Automatic STRM Generation', 'feat_1_desc': 'Converts M3U links to STRM files organized by Movies, Series, and XXX.',
        'feat_2_title': 'Rich Metadata & Images', 'feat_2_desc': 'Downloads .nfo files, posters, fanarts, clearlogos, discarts, and thumbnails.',
        'feat_3_title': 'Smart Matching', 'feat_3_desc': 'Uses advanced algorithms to match corrupted or complex movie/series names with TMDb.',
        'feat_4_title': 'Multi-language Support', 'feat_4_desc': 'Interface available in 13 languages.',
        'feat_5_title': 'Resumable Processing', 'feat_5_desc': 'Automatically remembers where it left off and avoids duplicating existing files.',
        'feat_6_title': 'Auto-Sync', 'feat_6_desc': 'Background automation to keep your STRM library up to date at a specific time daily.',
        'install_title': 'Installation',
        'install_1': 'Clone the repository:',
        'install_2': 'Install dependencies:', 'install_2_alt': 'or run install.bat on Windows',
        'install_3': 'Run the application:',
        'usage_title': 'Usage',
        'usage_1': 'Go to the **Settings** tab.',
        'usage_2': 'Enter your IPTV details (URL, username, password) or select a local M3U file.',
        'usage_3': 'Enter your TMDB and Fanart.tv API keys.',
        'usage_4': 'Go to the **M3U Processing Engine** tab and click **Start Processing**.',
        'license_title': 'License',
        'license_desc': 'This project is open-source and free to use.'
    },
    'tr': {
        'desc_short': 'IPTV M3U oynatma listelerinizi TMDb meta verileriyle Kodi, Jellyfin ve Emby gibi medya merkezleri için STRM dosyalarına dönüştüren güçlü bir araç.',
        'features_title': 'Özellikler',
        'feat_1_title': 'Otomatik STRM Oluşturma', 'feat_1_desc': 'M3U linklerini Filmler, Diziler ve XXX olarak klasörleyerek STRM dosyalarına dönüştürür.',
        'feat_2_title': 'Gelişmiş Meta Veri ve Görseller', 'feat_2_desc': '.nfo dosyaları, posterler, fanartlar, logolar, disk artları ve küçük resimler indirir.',
        'feat_3_title': 'Akıllı Eşleştirme', 'feat_3_desc': 'Bozuk veya karmaşık film/dizi isimlerini TMDb ile eşleştirmek için gelişmiş algoritmalar kullanır.',
        'feat_4_title': 'Çoklu Dil Desteği', 'feat_4_desc': 'Arayüz 13 farklı dilde kullanılabilir.',
        'feat_5_title': 'Kaldığı Yerden Devam Etme', 'feat_5_desc': 'Nerede kaldığını otomatik hatırlar ve var olan dosyaları tekrar indirmeyi önler.',
        'feat_6_title': 'Otomatik Senkronizasyon', 'feat_6_desc': 'STRM kütüphanenizi her gün belirli bir saatte güncel tutmak için arka planda otomatik çalışır.',
        'install_title': 'Kurulum',
        'install_1': 'Depoyu klonlayın:',
        'install_2': 'Gereksinimleri yükleyin:', 'install_2_alt': 'veya Windows üzerinde install.bat çalıştırın',
        'install_3': 'Uygulamayı başlatın:',
        'usage_title': 'Kullanım',
        'usage_1': '**Ayarlar** sekmesine gidin.',
        'usage_2': 'IPTV bilgilerinizi (URL, kullanıcı adı, şifre) girin veya yerel bir M3U dosyası seçin.',
        'usage_3': 'TMDB ve Fanart.tv API anahtarlarınızı girin.',
        'usage_4': '**M3U İşleme Motoru** sekmesine gidip **İşlemi Başlat** butonuna tıklayın.',
        'license_title': 'Lisans',
        'license_desc': 'Bu proje açık kaynaklıdır ve kullanımı ücretsizdir.'
    },
    'de': {
        'desc_short': 'Ein leistungsstarkes Tool, um IPTV M3U-Playlists mit umfangreichen TMDb-Metadaten in STRM-Dateien für Kodi, Jellyfin und Emby zu konvertieren.',
        'features_title': 'Eigenschaften',
        'feat_1_title': 'Automatische STRM-Erstellung', 'feat_1_desc': 'Konvertiert M3U-Links in STRM-Dateien (organisiert nach Filme, Serien und XXX).',
        'feat_2_title': 'Umfangreiche Metadaten & Bilder', 'feat_2_desc': 'Lädt .nfo-Dateien, Poster, Fanarts, Logos, Discarts und Thumbnails herunter.',
        'feat_3_title': 'Intelligente Zuordnung', 'feat_3_desc': 'Nutzt fortschrittliche Algorithmen, um Namen mit TMDb abzugleichen.',
        'feat_4_title': 'Mehrsprachig', 'feat_4_desc': 'Oberfläche in 13 Sprachen verfügbar.',
        'feat_5_title': 'Fortsetzbare Verarbeitung', 'feat_5_desc': 'Merkt sich den Fortschritt und vermeidet Duplikate.',
        'feat_6_title': 'Auto-Sync', 'feat_6_desc': 'Hintergrund-Automatisierung für tägliche Aktualisierungen.',
        'install_title': 'Installation',
        'install_1': 'Repository klonen:',
        'install_2': 'Abhängigkeiten installieren:', 'install_2_alt': 'oder install.bat unter Windows ausführen',
        'install_3': 'Anwendung starten:',
        'usage_title': 'Verwendung',
        'usage_1': 'Gehen Sie zum Reiter **Einstellungen**.',
        'usage_2': 'Geben Sie Ihre IPTV-Daten ein oder wählen Sie eine lokale M3U-Datei.',
        'usage_3': 'Geben Sie Ihre TMDB- und Fanart.tv-API-Schlüssel ein.',
        'usage_4': 'Gehen Sie zum Reiter **M3U Processing Engine** und klicken Sie auf **Verarbeitung starten**.',
        'license_title': 'Lizenz',
        'license_desc': 'Dieses Projekt ist Open Source und kostenlos.'
    },
    'es': {
        'desc_short': 'Una poderosa herramienta para convertir tus listas M3U de IPTV en archivos STRM para centros multimedia como Kodi, Jellyfin y Emby con metadatos de TMDb.',
        'features_title': 'Características',
        'feat_1_title': 'Generación automática de STRM', 'feat_1_desc': 'Convierte enlaces M3U a STRM organizados por Películas, Series y XXX.',
        'feat_2_title': 'Metadatos e Imágenes', 'feat_2_desc': 'Descarga archivos .nfo, pósteres, fanarts, logos, discarts y miniaturas.',
        'feat_3_title': 'Coincidencia Inteligente', 'feat_3_desc': 'Usa algoritmos avanzados para emparejar nombres complejos con TMDb.',
        'feat_4_title': 'Soporte Multilingüe', 'feat_4_desc': 'Interfaz disponible en 13 idiomas.',
        'feat_5_title': 'Procesamiento Reanudable', 'feat_5_desc': 'Recuerda el progreso y evita duplicar archivos.',
        'feat_6_title': 'Sincronización Automática', 'feat_6_desc': 'Automatización en segundo plano para actualizar diariamente.',
        'install_title': 'Instalación',
        'install_1': 'Clona el repositorio:',
        'install_2': 'Instala las dependencias:', 'install_2_alt': 'o ejecuta install.bat en Windows',
        'install_3': 'Ejecuta la aplicación:',
        'usage_title': 'Uso',
        'usage_1': 'Ve a la pestaña **Configuración**.',
        'usage_2': 'Introduce tus datos de IPTV o selecciona un archivo M3U.',
        'usage_3': 'Introduce tus claves de API de TMDB y Fanart.tv.',
        'usage_4': 'Ve a la pestaña **Motor de Procesamiento M3U** y haz clic en **Iniciar Procesamiento**.',
        'license_title': 'Licencia',
        'license_desc': 'Este proyecto es de código abierto y de uso gratuito.'
    },
    'fr': {
        'desc_short': 'Un outil puissant pour convertir vos listes de lecture IPTV M3U en fichiers STRM pour Kodi, Jellyfin et Emby avec les métadonnées TMDb.',
        'features_title': 'Fonctionnalités',
        'feat_1_title': 'Génération automatique de STRM', 'feat_1_desc': 'Convertit les liens M3U en fichiers STRM (Films, Séries et XXX).',
        'feat_2_title': 'Métadonnées et Images', 'feat_2_desc': 'Télécharge les fichiers .nfo, affiches, fanarts, logos, discarts.',
        'feat_3_title': 'Correspondance Intelligente', 'feat_3_desc': 'Algorithmes avancés pour faire correspondre les noms avec TMDb.',
        'feat_4_title': 'Multilingue', 'feat_4_desc': 'Interface en 13 langues.',
        'feat_5_title': 'Reprise du traitement', 'feat_5_desc': 'Mémorise la progression et évite les doublons.',
        'feat_6_title': 'Synchronisation Auto', 'feat_6_desc': 'Mise à jour automatique quotidienne en arrière-plan.',
        'install_title': 'Installation',
        'install_1': 'Cloner le dépôt:',
        'install_2': 'Installer les dépendances:', 'install_2_alt': 'ou exécutez install.bat sur Windows',
        'install_3': 'Lancer l\'application:',
        'usage_title': 'Utilisation',
        'usage_1': 'Allez dans l\'onglet **Paramètres**.',
        'usage_2': 'Entrez vos informations IPTV ou sélectionnez un fichier M3U.',
        'usage_3': 'Entrez vos clés API TMDB et Fanart.tv.',
        'usage_4': 'Allez dans l\'onglet **Moteur de traitement M3U** et cliquez sur **Démarrer**.',
        'license_title': 'Licence',
        'license_desc': 'Ce projet est open source et gratuit.'
    },
    'it': {
        'desc_short': 'Un potente strumento per convertire le playlist IPTV M3U in file STRM per Kodi, Jellyfin ed Emby con metadati TMDb.',
        'features_title': 'Caratteristiche',
        'feat_1_title': 'Generazione automatica STRM', 'feat_1_desc': 'Converte i link M3U in STRM (Film, Serie, XXX).',
        'feat_2_title': 'Metadati e Immagini', 'feat_2_desc': 'Scarica file .nfo, poster, fanart, loghi e miniature.',
        'feat_3_title': 'Abbinamento Intelligente', 'feat_3_desc': 'Usa algoritmi avanzati per cercare i nomi su TMDb.',
        'feat_4_title': 'Multilingua', 'feat_4_desc': 'Interfaccia disponibile in 13 lingue.',
        'feat_5_title': 'Elaborazione Riprendibile', 'feat_5_desc': 'Ricorda dove si era interrotto ed evita file duplicati.',
        'feat_6_title': 'Auto-Sync', 'feat_6_desc': 'Aggiornamento automatico giornaliero in background.',
        'install_title': 'Installazione',
        'install_1': 'Clona il repository:',
        'install_2': 'Installa le dipendenze:', 'install_2_alt': 'o esegui install.bat su Windows',
        'install_3': 'Avvia l\'applicazione:',
        'usage_title': 'Utilizzo',
        'usage_1': 'Vai alla scheda **Impostazioni**.',
        'usage_2': 'Inserisci i tuoi dati IPTV o seleziona un file M3U locale.',
        'usage_3': 'Inserisci le tue chiavi API TMDB e Fanart.tv.',
        'usage_4': 'Vai alla scheda **Motore di Elaborazione M3U** e clicca su **Inizia Elaborazione**.',
        'license_title': 'Licenza',
        'license_desc': 'Questo progetto è open source e gratuito.'
    },
    'ru': {
        'desc_short': 'Мощный инструмент для преобразования плейлистов IPTV M3U в файлы STRM для Kodi, Jellyfin и Emby с метаданными TMDb.',
        'features_title': 'Особенности',
        'feat_1_title': 'Автоматическое создание STRM', 'feat_1_desc': 'Преобразует ссылки M3U в файлы STRM.',
        'feat_2_title': 'Метаданные и Изображения', 'feat_2_desc': 'Загружает файлы .nfo, постеры, фанарты, логотипы.',
        'feat_3_title': 'Умный поиск', 'feat_3_desc': 'Использует продвинутые алгоритмы для сопоставления с TMDb.',
        'feat_4_title': 'Мультиязычность', 'feat_4_desc': 'Интерфейс на 13 языках.',
        'feat_5_title': 'Возобновление работы', 'feat_5_desc': 'Запоминает прогресс и избегает дублирования.',
        'feat_6_title': 'Авто-Синхронизация', 'feat_6_desc': 'Ежедневное обновление в фоновом режиме.',
        'install_title': 'Установка',
        'install_1': 'Клонировать репозиторий:',
        'install_2': 'Установить зависимости:', 'install_2_alt': 'или запустить install.bat на Windows',
        'install_3': 'Запустить приложение:',
        'usage_title': 'Использование',
        'usage_1': 'Перейдите на вкладку **Настройки**.',
        'usage_2': 'Введите данные IPTV или выберите локальный файл M3U.',
        'usage_3': 'Введите ваши ключи API TMDB и Fanart.tv.',
        'usage_4': 'Перейдите на вкладку **Обработка M3U** и нажмите **Начать**.',
        'license_title': 'Лицензия',
        'license_desc': 'Этот проект имеет открытый исходный код.'
    },
    'uk': {
        'desc_short': 'Потужний інструмент для перетворення списків IPTV M3U у файли STRM для Kodi, Jellyfin та Emby.',
        'features_title': 'Особливості',
        'feat_1_title': 'Автоматичне створення STRM', 'feat_1_desc': 'Перетворює посилання M3U у файли STRM.',
        'feat_2_title': 'Метадані та Зображення', 'feat_2_desc': 'Завантажує файли .nfo, постери, фанарти, логотипи.',
        'feat_3_title': 'Розумний пошук', 'feat_3_desc': 'Використовує алгоритми для пошуку в TMDb.',
        'feat_4_title': 'Багатомовність', 'feat_4_desc': 'Інтерфейс доступний 13 мовами.',
        'feat_5_title': 'Відновлення роботи', 'feat_5_desc': 'Запам\'ятовує прогрес.',
        'feat_6_title': 'Авто-Синхронізація', 'feat_6_desc': 'Щоденне оновлення у фоновому режимі.',
        'install_title': 'Встановлення',
        'install_1': 'Клонувати репозиторій:',
        'install_2': 'Встановити залежності:', 'install_2_alt': 'або запустити install.bat (Windows)',
        'install_3': 'Запустити програму:',
        'usage_title': 'Використання',
        'usage_1': 'Перейдіть на вкладку **Налаштування**.',
        'usage_2': 'Введіть дані IPTV або виберіть локальний файл M3U.',
        'usage_3': 'Введіть ключі API TMDB та Fanart.tv.',
        'usage_4': 'Перейдіть на вкладку **Обробка M3U** і натисніть **Почати**.',
        'license_title': 'Ліцензія',
        'license_desc': 'Проект з відкритим кодом.'
    },
    'ar': {
        'desc_short': 'أداة قوية لتحويل قوائم IPTV M3U إلى ملفات STRM لمراكز الميديا مثل Kodi و Jellyfin.',
        'features_title': 'المميزات',
        'feat_1_title': 'إنشاء STRM تلقائي', 'feat_1_desc': 'يحول الروابط إلى ملفات STRM.',
        'feat_2_title': 'صور وبيانات وصفية', 'feat_2_desc': 'يقوم بتنزيل ملفات .nfo والملصقات.',
        'feat_3_title': 'مطابقة ذكية', 'feat_3_desc': 'يستخدم خوارزميات للبحث في TMDb.',
        'feat_4_title': 'لغات متعددة', 'feat_4_desc': 'الواجهة متوفرة بـ 13 لغة.',
        'feat_5_title': 'استئناف المعالجة', 'feat_5_desc': 'يتذكر التقدم ويتجنب التكرار.',
        'feat_6_title': 'مزامنة تلقائية', 'feat_6_desc': 'تحديث يومي في الخلفية.',
        'install_title': 'التثبيت',
        'install_1': 'استنساخ المستودع:',
        'install_2': 'تثبيت المتطلبات:', 'install_2_alt': 'أو تشغيل install.bat',
        'install_3': 'تشغيل البرنامج:',
        'usage_title': 'الاستخدام',
        'usage_1': 'انتقل إلى علامة التبويب **الإعدادات**.',
        'usage_2': 'أدخل تفاصيل IPTV الخاصة بك.',
        'usage_3': 'أدخل مفاتيح API الخاصة بك.',
        'usage_4': 'ابدأ المعالجة.',
        'license_title': 'الترخيص',
        'license_desc': 'هذا المشروع مفتوح المصدر.'
    },
    'ja': {
        'desc_short': 'IPTV M3UプレイリストをKodi、Jellyfin、Emby用のSTRMファイルに変換する強力なツールです。',
        'features_title': '機能',
        'feat_1_title': '自動STRM生成', 'feat_1_desc': 'M3UリンクをSTRMファイルに変換します。',
        'feat_2_title': '豊富なメタデータ', 'feat_2_desc': '.nfoファイル、ポスター、ロゴなどをダウンロードします。',
        'feat_3_title': 'スマートマッチング', 'feat_3_desc': 'TMDbで高度なアルゴリズムを使用します。',
        'feat_4_title': '多言語対応', 'feat_4_desc': '13言語で利用可能です。',
        'feat_5_title': '再開可能な処理', 'feat_5_desc': '進行状況を記憶し、重複を避けます。',
        'feat_6_title': '自動同期', 'feat_6_desc': 'バックグラウンドで毎日同期します。',
        'install_title': 'インストール',
        'install_1': 'リポジトリのクローン:',
        'install_2': '依存関係のインストール:', 'install_2_alt': 'Windowsの場合はinstall.batを実行',
        'install_3': 'アプリケーションの実行:',
        'usage_title': '使い方',
        'usage_1': '**設定**タブに移動します。',
        'usage_2': 'IPTVの詳細を入力するか、M3Uファイルを選択します。',
        'usage_3': 'TMDBとFanart.tvのAPIキーを入力します。',
        'usage_4': '**処理開始**をクリックします。',
        'license_title': 'ライセンス',
        'license_desc': 'このプロジェクトはオープンソースです。'
    },
    'ko': {
        'desc_short': 'IPTV M3U 재생 목록을 Kodi, Jellyfin 및 Emby용 STRM 파일로 변환하는 강력한 도구입니다.',
        'features_title': '특징',
        'feat_1_title': 'STRM 자동 생성', 'feat_1_desc': 'M3U 링크를 STRM 파일로 변환합니다.',
        'feat_2_title': '풍부한 메타데이터', 'feat_2_desc': '.nfo 파일, 포스터, 로고 등을 다운로드합니다.',
        'feat_3_title': '스마트 매칭', 'feat_3_desc': 'TMDb와 일치시키는 고급 알고리즘을 사용합니다.',
        'feat_4_title': '다국어 지원', 'feat_4_desc': '13개 언어로 제공됩니다.',
        'feat_5_title': '재개 가능한 처리', 'feat_5_desc': '진행 상황을 기억하고 중복을 방지합니다.',
        'feat_6_title': '자동 동기화', 'feat_6_desc': '백그라운드에서 매일 동기화합니다.',
        'install_title': '설치',
        'install_1': '저장소 복제:',
        'install_2': '종속성 설치:', 'install_2_alt': '또는 install.bat 실행',
        'install_3': '응용 프로그램 실행:',
        'usage_title': '사용법',
        'usage_1': '**설정** 탭으로 이동합니다.',
        'usage_2': 'IPTV 세부 정보를 입력하거나 M3U 파일을 선택합니다.',
        'usage_3': 'API 키를 입력합니다.',
        'usage_4': '**처리 시작**을 클릭합니다.',
        'license_title': '라이선스',
        'license_desc': '이 프로젝트는 오픈 소스입니다.'
    },
    'zh_CN': {
        'desc_short': '一个将IPTV M3U播放列表转换为Kodi、Jellyfin和Emby的STRM文件的强大工具。',
        'features_title': '特点',
        'feat_1_title': '自动生成STRM', 'feat_1_desc': '将M3U链接转换为STRM文件。',
        'feat_2_title': '丰富的元数据', 'feat_2_desc': '下载.nfo文件、海报、同人画等。',
        'feat_3_title': '智能匹配', 'feat_3_desc': '使用高级算法在TMDb中匹配。',
        'feat_4_title': '多语言支持', 'feat_4_desc': '提供13种语言。',
        'feat_5_title': '可恢复的处理', 'feat_5_desc': '记住进度，避免重复。',
        'feat_6_title': '自动同步', 'feat_6_desc': '每天后台自动同步。',
        'install_title': '安装',
        'install_1': '克隆仓库:',
        'install_2': '安装依赖:', 'install_2_alt': '或运行 install.bat',
        'install_3': '运行应用:',
        'usage_title': '使用',
        'usage_1': '前往 **设置** 选项卡。',
        'usage_2': '输入您的IPTV详细信息或选择本地M3U文件。',
        'usage_3': '输入您的API密钥。',
        'usage_4': '点击 **开始处理**。',
        'license_title': '许可证',
        'license_desc': '此项目是开源的。'
    },
    'zh_TW': {
        'desc_short': '一個將IPTV M3U播放清單轉換為Kodi、Jellyfin和Emby的STRM文件的強大工具。',
        'features_title': '特點',
        'feat_1_title': '自動生成STRM', 'feat_1_desc': '將M3U連結轉換為STRM文件。',
        'feat_2_title': '豐富的元數據', 'feat_2_desc': '下載.nfo文件、海報、同人畫等。',
        'feat_3_title': '智能匹配', 'feat_3_desc': '使用高級算法在TMDb中匹配。',
        'feat_4_title': '多語言支持', 'feat_4_desc': '提供13種語言。',
        'feat_5_title': '可恢復的處理', 'feat_5_desc': '記住進度，避免重複。',
        'feat_6_title': '自動同步', 'feat_6_desc': '每天後台自動同步。',
        'install_title': '安裝',
        'install_1': '克隆倉庫:',
        'install_2': '安裝依賴:', 'install_2_alt': '或運行 install.bat',
        'install_3': '運行應用:',
        'usage_title': '使用',
        'usage_1': '前往 **設置** 選項卡。',
        'usage_2': '輸入您的IPTV詳細信息或選擇本地M3U文件。',
        'usage_3': '輸入您的API密鑰。',
        'usage_4': '點擊 **開始處理**。',
        'license_title': '許可證',
        'license_desc': '此項目是開源的。'
    }
}

os.makedirs('readme', exist_ok=True)

def generate_header(current_lang_code, is_root=False):
    links = []
    # Ensure English is the root one
    for code, name in langs.items():
        if code == 'en':
            target = "README.md" if is_root else "../README.md"
        else:
            target = f"readme/README.{code}.md" if is_root else f"README.{code}.md"
        
        if code == current_lang_code:
            links.append(f"**[{name}]({target})**")
        else:
            links.append(f"[{name}]({target})")
    
    return " | ".join(links) + "\n\n"

template = """{header}<h1 align="center">M3U to STRM Converter</h1>

<p align="center">
  <strong>{desc_short}</strong>
</p>

## {features_title}
- **{feat_1_title}:** {feat_1_desc}
- **{feat_2_title}:** {feat_2_desc}
- **{feat_3_title}:** {feat_3_desc}
- **{feat_4_title}:** {feat_4_desc}
- **{feat_5_title}:** {feat_5_desc}
- **{feat_6_title}:** {feat_6_desc}

## {install_title}
1. {install_1} `git clone https://github.com/aytacesmebasi/m3utostrm.git`
2. {install_2} `pip install -r requirements.txt` ({install_2_alt})
3. {install_3} `python main.py`

## {usage_title}
1. {usage_1}
2. {usage_2}
3. {usage_3}
4. {usage_4}

## {license_title}
{license_desc}
"""

for code, data in translations.items():
    is_root = (code == 'en')
    header = generate_header(code, is_root=is_root)
    content = template.format(header=header, **data)
    
    filepath = 'README.md' if is_root else f'readme/README.{code}.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Generated {filepath}")
