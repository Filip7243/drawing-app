from PyQt6.QtCore import Qt, QTimer, QDir, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from components.AprilTagsComponent import AprilTagsComponent
from components.TimeBar import TimeBar


class RememberFigurePage(QWidget):
    finished = pyqtSignal()

    def __init__(self,
                 bg_path="assets:img/figures/tutorial_figure_white.png",
                 audio="03_zapamietaj_rysunek.wav",
                 parent=None,
                 is_tutorial=False):
        super().__init__(parent)
        self.setWindowTitle("Remember Figure Page")

        self.background = QPixmap(bg_path)
        print(f'height pixmap: {self.background.height()}')
        print(f'width pixmap: {self.background.width()}')
        self.scaled_background = self.background
        self.audio = audio

        self.is_tutorial = is_tutorial

        self.display_info = None

        self.timer = QTimer(self)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        # wczytanie źródła audio (ale nie odtwarzamy jeszcze)
        dir_assets = QDir("assets:/audio")
        audio_path = dir_assets.absoluteFilePath(audio)
        self.player.setSource(QUrl.fromLocalFile(audio_path))

        # UI
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.time_bar = TimeBar(max_time=3, height=1, color="#FFFFFF")
        print(f"SELF.TIME_BAR.MAX_TIME: {self.time_bar.max_time}")
        main_layout.addWidget(self.time_bar)

        april_tags = AprilTagsComponent(num_tags=6)
        main_layout.addWidget(april_tags)

        self.setLayout(main_layout)

    def start(self):
        print("A CZY JA TUTAJ WCHODZ?")
        """Pokazuje stronę, odtwarza audio i startuje pasek czasu."""
        # When embedded in the controller's stack, avoid showing the window
        if self.parent() is None:
            self.showMaximized()

        # restart audio
        self.player.stop()
        self.player.play()

        print("STARTUJE")
        # start timera dopiero po pokazaniu okna
        QTimer.singleShot(0, self.start_time_bar)

    def start_time_bar(self):
        print("JESTEM W STARCIE!")
        """Uruchamia licznik TimeBar."""
        self.time_bar.setTime(self.time_bar.max_time)
        self.timer.timeout.connect(self.update_time_bar)
        self.timer.start(1000)

    def update_time_bar(self):
        print(f"SELF.TIME_BAR.CURRNET_TIME: {self.time_bar.current_time}")
        if self.time_bar.current_time > 0:
            self.time_bar.setTime(self.time_bar.current_time - 1)
        else:
            self.timer.stop()
            self.player.stop()
            self.finished.emit()

    def resizeEvent(self, event):
        """Skaluje tło przy zmianie rozmiaru."""
        if not self.background.isNull():
            self.scaled_background = self.background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        # NOWE: Aktualizuj display_info przy każdej zmianie rozmiaru
        self.update_display_info()

        super().resizeEvent(event)

    def update_display_info(self):
        """NOWE: Aktualizuje informacje o wyświetlaniu obrazu"""
        if not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2

            self.display_info = {
                'window_width': self.width(),
                'window_height': self.height(),
                'image_width': self.scaled_background.width(),
                'image_height': self.scaled_background.height(),
                'offset_x': x,
                'offset_y': y,
                'original_width': self.background.width(),
                'original_height': self.background.height(),
                'timebar_height': self.time_bar.height()
            }

    def get_display_info(self):
        """NOWE: Zwraca informacje o tym jak obraz był wyświetlany"""
        return self.display_info

    def paintEvent(self, event):
        """Rysuje przeskalowane tło."""
        painter = QPainter(self)
        if not self.scaled_background.isNull():
            x = (self.width() - self.scaled_background.width()) // 2
            y = (self.height() - self.scaled_background.height()) // 2
            painter.drawPixmap(x, y, self.scaled_background)
        super().paintEvent(event)
