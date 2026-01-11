from PyQt6.QtCore import QDir, QUrl, pyqtSignal
from PyQt6.QtGui import QImage, QTransform
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from components.AprilTagsComponent import AprilTagsComponent
from components.StyledButton import StyledButton
from components.IconButton import IconButton


class DrawingPage(QWidget):
    finished = pyqtSignal()
    firstStroke = pyqtSignal()
    strokeStarted = pyqtSignal()
    strokeFinished = pyqtSignal()
    undoClicked = pyqtSignal()
    redoClicked = pyqtSignal()

    is_drawing_page = True  # Flaga dla FlowController żeby widział że tutaj może zbierać dane

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
        self.april_tags = AprilTagsComponent(num_tags=6, show_canvas=True)
        self.april_tags.canvas.firstStroke.connect(self.firstStroke.emit)
        self.april_tags.canvas.strokeStarted.connect(self.strokeStarted.emit)
        self.april_tags.canvas.strokeFinished.connect(self.strokeFinished.emit)
        self.april_tags.canvas.undoClicked.connect(self.undoClicked.emit)
        self.april_tags.canvas.redoClicked.connect(self.redoClicked.emit)
        main_layout.addWidget(self.april_tags)

        button_container = QWidget()
        button_container.setStyleSheet("background-color: white;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 0, 20, 0)
        button_layout.setSpacing(20)

        # Lewa strona - undo/redo
        undo_redo_layout = QHBoxLayout()
        self.undo_button = IconButton("assets/icons/arrow-left.png", color="#FFFFFF")
        self.undo_button.setToolTip("Cofnij")
        self.undo_button.clicked.connect(self.april_tags.canvas.undo)
        
        # Dla Redo użyjemy tej samej ikony ale odbitej.
        redo_transform = QTransform().scale(-1, 1)
        self.redo_button = IconButton("assets/icons/arrow-left.png", color="#FFFFFF", transform=redo_transform)
        self.redo_button.setToolTip("Ponów")
        self.redo_button.clicked.connect(self.april_tags.canvas.redo)
        
        undo_redo_layout.addWidget(self.undo_button)
        undo_redo_layout.addWidget(self.redo_button)
        
        button_layout.addLayout(undo_redo_layout)

        done_button = StyledButton("Dalej", color="#000000", font_color="#FFFFFF")
        done_button.setFixedWidth(500)
        done_button.clicked.connect(self.on_done_btn_click)
        button_layout.addStretch()
        button_layout.addWidget(done_button)
        button_layout.addStretch()

        button_container.setFixedHeight(done_button.sizeHint().height())
        print(f'btn: {button_container.sizeHint().height()}')
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

    def export_as_image(self) -> QImage:
        """Zwraca obraz QImage przedstawiający sam obszar rysowania.
        """
        image = self.april_tags.canvas.export_as_image()
        print(image.height())
        print(image.width())
        return image

    def on_done_btn_click(self):
        self.finished.emit()  # Emitujemy sygnał dla kontrolera, że rysowanie zostało zakończone
