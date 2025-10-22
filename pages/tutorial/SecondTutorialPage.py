from PyQt6.QtCore import Qt, QDir, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.StyledButton import StyledButton


# TODO: Każda straon ma byc osobno, zrobic copy paste kazdej ze stron i tak je uruchamiac a nie bawic sie w takie powiazania dziwne, to bez sensu
class SecondTutorialPage(QWidget):
    def __init__(self, parent=None, audio="02_zapamietaj_rysunek_przedmowa.wav"):
        super().__init__(parent)
        self.setWindowTitle("Tutorial Page")

        self.audio = audio

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(50)

        self.again_btn = StyledButton("POWTÓRZ", color="#89c057")
        self.again_btn.setFixedSize(300, 100)
        self.again_btn.setDisabled(True)
        self.again_btn.clicked.connect(self.on_again_btn_click)
        btn_layout.addWidget(self.again_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tutorial_btn = StyledButton("DALEJ", color="#89c057")
        self.tutorial_btn.setFixedSize(300, 100)
        self.tutorial_btn.setDisabled(True)
        self.tutorial_btn.clicked.connect(self.on_tutorial_btn_click)
        btn_layout.addWidget(self.tutorial_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        dir_assets = QDir("assets:/audio")
        audio_path = dir_assets.absoluteFilePath(audio)
        self.player.setSource(QUrl.fromLocalFile(audio_path))

        self.player.playbackStateChanged.connect(self.on_playback_state_changed)

    def start(self):
        """Rozpocznij odtwarzanie audio i zablokuj przyciski."""
        self.showMaximized()
        self.again_btn.setDisabled(True)
        self.tutorial_btn.setDisabled(True)
        self.player.stop()
        self.player.play()

    def on_playback_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.tutorial_btn.setDisabled(False)
            self.again_btn.setDisabled(False)

    def on_tutorial_btn_click(self):
        from pages.RememberFigurePage import RememberFigurePage
        self.next_page = RememberFigurePage()
        self.next_page.start()
        self.hide()

    def on_again_btn_click(self):
        self.start()
