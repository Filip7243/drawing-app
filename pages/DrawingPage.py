from PyQt6.QtCore import QDir, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledButton import StyledButton


class DrawingPage(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None, audio="05_odwzoruj_rysunek.wav", is_tutorial=True):
        super().__init__(parent)
        self.setWindowTitle("Draw Figure Page")
        self.audio = audio
        self.is_tutorial = is_tutorial

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        april_tags = AprilTagsComponent(num_tags=4, show_canvas=True)
        main_layout.addWidget(april_tags)

        button_container = QWidget()
        button_container.setStyleSheet("background-color: white;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        done_button = StyledButton("Dalej", color="#000000", font_color="#FFFFFF")
        done_button.setFixedWidth(500)
        done_button.clicked.connect(self.on_done_btn_click)
        button_layout.addStretch()
        button_layout.addWidget(done_button)
        button_layout.addStretch()

        button_container.setFixedHeight(done_button.sizeHint().height())
        main_layout.addWidget(button_container)
        self.setLayout(main_layout)

        self.player = None
        if self.audio is not None:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(1.0)

            dir_assets = QDir("assets:/audio")
            audio_path = dir_assets.absoluteFilePath(self.audio)
            self.player.setSource(QUrl.fromLocalFile(audio_path))

            self.player.stop()
            self.player.play()

    def on_done_btn_click(self):
        self.finished.emit()
