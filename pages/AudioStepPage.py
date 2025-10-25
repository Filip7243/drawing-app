from PyQt6.QtCore import Qt, QDir, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from components.StyledButton import StyledButton


class AudioStepPage(QWidget):
    nextRequested = pyqtSignal()
    repeatRequested = pyqtSignal()

    def __init__(self, audio: str, parent=None,
                 next_label: str = "DALEJ", repeat_label: str = "POWTÓRZ"):
        super().__init__(parent)
        self.setWindowTitle("Tutorial Page")
        self.audio = audio

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(50)

        self.again_btn = StyledButton(repeat_label, color="#89c057")
        self.again_btn.setFixedSize(300, 100)
        self.again_btn.setDisabled(True)
        self.again_btn.clicked.connect(self.repeatRequested.emit)
        btn_layout.addWidget(self.again_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.next_btn = StyledButton(next_label, color="#89c057")
        self.next_btn.setFixedSize(300, 100)
        self.next_btn.setDisabled(True)
        self.next_btn.clicked.connect(self.nextRequested.emit)
        btn_layout.addWidget(self.next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

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
        # When embedded in a container (FlowController's stack), avoid showing the window
        if self.parent() is None:
            self.showMaximized()
        self.again_btn.setDisabled(True)
        self.next_btn.setDisabled(True)
        self.player.stop()
        self.player.play()

    def on_playback_state_changed(self, state):
        from PyQt6.QtMultimedia import QMediaPlayer
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.next_btn.setDisabled(False)
            self.again_btn.setDisabled(False)
