import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QMainWindow,
                             QHBoxLayout, QVBoxLayout, QFileDialog, QSlider, QStyleFactory)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, QTimer, QTime

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.playlist = []
        self.current_track = 0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_position)

        self.load_style("styles.qss")

        self.init_ui()

    def load_style(self, style_file):
        try:
            with open(style_file, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
        except FileNotFoundError:
            print(f"Warning: stylesheet file '{style_file}' not found.")

    def init_ui(self):
        self.setWindowTitle("Плеер")

        open_button = QPushButton("Выбрать папку")
        open_button.clicked.connect(self.open_folder)

        prev_button = QPushButton("Предыдущий")
        prev_button.clicked.connect(self.prev_track)

        next_button = QPushButton("Следующий")
        next_button.clicked.connect(self.next_track)

        play_button = QPushButton("Играть/Пауза")
        play_button.clicked.connect(self.play_pause)

        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(50)
        volume_slider.valueChanged.connect(self.change_volume)
        volume_label = QLabel("Громкость")

        self.track_label = QLabel("Ничего не выбрано")

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        self.time_label = QLabel("00:00 / 00:00")

        position_layout = QHBoxLayout()
        position_layout.addWidget(self.position_slider)
        position_layout.addWidget(self.time_label)

        position_label = QLabel("Дорожка трека")

        control_layout = QHBoxLayout()
        control_layout.addWidget(open_button)
        control_layout.addWidget(prev_button)
        control_layout.addWidget(play_button)
        control_layout.addWidget(next_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.track_label)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(volume_label)
        main_layout.addWidget(volume_slider)
        main_layout.addWidget(position_label)
        main_layout.addLayout(position_layout)

        self.setLayout(main_layout)

    def open_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку с музыкой")
        if directory:
            self.playlist = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith(".mp3")]
            if self.playlist:
                self.current_track = 0
                self.play_track()

    def play_track(self):
        if self.playlist:
            file_path = self.playlist[self.current_track]
            url = QUrl.fromLocalFile(file_path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
            self.track_label.setText(os.path.basename(file_path))
            self.timer.start()
            self.player.durationChanged.connect(self.update_duration)
            self.player.positionChanged.connect(self.update_slider_position)



    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)
        total_time = QTime(0, 0, 0).addMSecs(duration)
        self.time_label.setText("00:00 / " + total_time.toString("mm:ss"))


    def update_slider_position(self, position):
        self.position_slider.setValue(position)


    def set_position(self, position):
        self.player.setPosition(position)

    def update_position(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            position = self.player.position()
            current_time = QTime(0, 0, 0).addMSecs(position)
            total_time = QTime(0, 0, 0).addMSecs(self.position_slider.maximum())
            self.time_label.setText(current_time.toString("mm:ss") + " / " + total_time.toString("mm:ss"))

    def prev_track(self):
        if self.playlist:
            self.current_track = (self.current_track - 1) % len(self.playlist)
            self.play_track()

    def next_track(self):
        if self.playlist:
            self.current_track = (self.current_track + 1) % len(self.playlist)
            self.play_track()

    def play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.timer.stop()
        else:
            self.player.play()
            self.timer.start()

    def change_volume(self, value):
        self.player.setVolume(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())