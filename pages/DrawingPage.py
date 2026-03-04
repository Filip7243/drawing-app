from PyQt6.QtCore import QDir, QUrl, pyqtSignal
from PyQt6.QtGui import QImage, QTransform
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.AprilTagsComponent import AprilTagsComponent
from components.IconButton import IconButton
from components.StyledButton import StyledButton


class DrawingPage(QWidget):
    finished = pyqtSignal()
    firstStroke = pyqtSignal()
    strokeStarted = pyqtSignal()
    strokeFinished = pyqtSignal()
    strokeDataCollected = pyqtSignal(dict)
    undoClicked = pyqtSignal()
    redoClicked = pyqtSignal()

    is_drawing_page = True  # Flaga dla FlowController, żeby widział, że tutaj może zbierać dane

    def __init__(self, parent=None, audio="05_odwzoruj_rysunek.wav", is_tutorial=True):
        super().__init__(parent)
        self.setWindowTitle("Draw Figure Page")
        self.audio = audio
        self.is_tutorial = is_tutorial
        self.exporter = self.export_as_image

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Z tego komponentu jest pobierany obraz
        self.april_tags = AprilTagsComponent(num_tags=6, show_canvas=True, show_frame=True)
        self.april_tags.canvas.firstStroke.connect(self.firstStroke.emit)
        self.april_tags.canvas.strokeStarted.connect(self.strokeStarted.emit)
        self.april_tags.canvas.strokeFinished.connect(self.strokeFinished.emit)
        self.april_tags.canvas.strokeDataCollected.connect(self.strokeDataCollected.emit)
        self.april_tags.canvas.undoClicked.connect(self.undoClicked.emit)
        self.april_tags.canvas.redoClicked.connect(self.redoClicked.emit)
        main_layout.addWidget(self.april_tags)

        # Przyciski przeniesione na AprilTagsComponent (na czarną ramkę)
        # Lewa strona - undo/redo
        self.undo_button = IconButton("assets/icons/arrow-left.png", color="#FFFFFF", icon_size=72, padding=14)
        self.undo_button.setToolTip("Cofnij")
        self.undo_button.clicked.connect(self.april_tags.canvas.undo)
        
        # Dla Redo użyjemy tej samej ikony ale odbitej.
        redo_transform = QTransform().scale(-1, 1)
        self.redo_button = IconButton("assets/icons/arrow-left.png", color="#FFFFFF",
                                      transform=redo_transform, icon_size=72, padding=14)
        self.redo_button.setToolTip("Ponów")
        self.redo_button.clicked.connect(self.april_tags.canvas.redo)

        # Przycisk Dalej
        self.done_button = StyledButton("DALEJ", color="#FFFFFF", font_color="#000000", font_size=22)
        self.done_button.clicked.connect(self.on_done_btn_click)
        
        # Dodajemy do ramki w AprilTagsComponent (kolejność ma znaczenie dla pozycjonowania w resizeEvent)
        self.april_tags.add_widget_to_frame(self.undo_button)
        self.april_tags.add_widget_to_frame(self.redo_button)
        self.april_tags.add_widget_to_frame(self.done_button)

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

            self.player.playbackStateChanged.connect(self._on_playback_state_changed)

            self.player.stop()
            self.player.play()

            # Zablokuj przyciski na początku odtwarzania
            self._set_buttons_enabled(False)

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self._set_buttons_enabled(True)
        else:
            self._set_buttons_enabled(False)

    def _set_buttons_enabled(self, enabled: bool):
        self.done_button.setEnabled(enabled)
        self.undo_button.setEnabled(enabled)
        self.redo_button.setEnabled(enabled)

    def export_as_image(self) -> QImage:
        """
            Zwraca obraz QImage przedstawiający sam obszar rysowania.
            Exporter używany w FlowController.py, po każdym zakończeniu rysowania rysunku zapisuje go w session_dir.
        """
        image = self.april_tags.canvas.export_as_image()
        print(image.height())
        print(image.width())
        return image

    def on_done_btn_click(self):
        self.finished.emit()  # Emitujemy sygnał dla kontrolera, że rysowanie zostało zakończone
