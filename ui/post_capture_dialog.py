# ui/post_capture_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QRadioButton, QLabel, QSlider, QFileDialog)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon

from core.video_processor import VideoProcessor
from utils.message_box import CustomMessageBox
import os

class PostCaptureDialog(QDialog):
    """
    A dialog displayed after a screen capture is complete.
    It allows the user to preview the recorded video, select a quality level,
    and save the re-encoded video, or discard the capture.
    """
    def __init__(self, temp_video_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RSCapture - ការរក្សាទុកវីដេអូ")
        self.setGeometry(200, 200, 800, 600) # x, y, width, height

        self.temp_video_path = temp_video_path
        self.video_processor = VideoProcessor()
        self.selected_quality = "Medium" # Default quality

        self._setup_ui()
        self._load_video()

    def _setup_ui(self):
        """
        Sets up the user interface for the post-capture dialog.
        """
        main_layout = QVBoxLayout()

        # Video Player Section
        video_player_group = QGroupBox("មើលវីដេអូដែលបានថតរួច")
        video_layout = QVBoxLayout()

        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self) # Create QAudioOutput instance
        self.media_player.setAudioOutput(self.audio_output) # Set the audio output
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start")) # Play icon
        self.play_button.clicked.connect(self._toggle_play_pause)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self._set_position)

        self.media_player.positionChanged.connect(self._update_position_slider)
        self.media_player.durationChanged.connect(self._update_duration)
        self.media_player.playbackStateChanged.connect(self._update_play_button_icon)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)

        video_layout.addWidget(self.video_widget)
        video_layout.addLayout(controls_layout)
        video_player_group.setLayout(video_layout)

        main_layout.addWidget(video_player_group)

        # Quality Selection Section
        quality_group = QGroupBox("ជ្រើសរើសគុណភាពវីដេអូដែលចង់រក្សាទុក")
        quality_layout = QHBoxLayout()

        self.radio_low = QRadioButton("ទាប (Low)")
        self.radio_medium = QRadioButton("មធ្យម (Medium)")
        self.radio_high = QRadioButton("ខ្ពស់ (High)")

        # Set default selection and connect signals
        self.radio_medium.setChecked(True)
        self.radio_low.toggled.connect(lambda: self._set_quality("Low"))
        self.radio_medium.toggled.connect(lambda: self._set_quality("Medium"))
        self.radio_high.toggled.connect(lambda: self._set_quality("High"))

        quality_layout.addWidget(self.radio_low)
        quality_layout.addWidget(self.radio_medium)
        quality_layout.addWidget(self.radio_high)
        quality_group.setLayout(quality_layout)
        main_layout.addWidget(quality_group)

        # Action Buttons Section
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("រក្សាទុក")
        self.discard_button = QPushButton("បោះបង់")

        self.save_button.clicked.connect(self._save_video)
        self.discard_button.clicked.connect(self._discard_video)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.discard_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _load_video(self):
        """
        Loads the temporary video file into the media player.
        """
        if os.path.exists(self.temp_video_path):
            self.media_player.setSource(QUrl.fromLocalFile(self.temp_video_path))
            self.media_player.play()
        else:
            CustomMessageBox.error(self, "Error", "ឯកសារវីដេអូបណ្ដោះអាសន្នមិនមានទេ")
            self.reject() # Close dialog if file is missing

    def _toggle_play_pause(self):
        """
        Toggles between play and pause states for the video player.
        """
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def _update_play_button_icon(self, state: QMediaPlayer.PlaybackState):
        """
        Updates the play/pause button icon based on the media player's state.
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(QIcon.fromTheme("media-playback-pause"))
        else:
            self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _update_position_slider(self, position: int):
        """
        Updates the position slider as the video plays.
        """
        self.position_slider.setValue(position)

    def _update_duration(self, duration: int):
        """
        Updates the maximum value of the position slider when video duration changes.
        """
        self.position_slider.setRange(0, duration)

    def _set_position(self, position: int):
        """
        Sets the media player's position based on the slider's value.
        """
        self.media_player.setPosition(position)

    def _set_quality(self, quality: str):
        """
        Sets the selected quality level.
        """
        self.selected_quality = quality
        print(f"គុណភាពដែលបានជ្រើសរើស: {self.selected_quality}") # Log selected quality

    def _save_video(self):
        """
        Prompts the user to select a save location and re-encodes the video.
        """
        # Stop media player before processing
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "រក្សាទុកវីដេអូ",
            os.path.expanduser("~/Videos/RSCapture_video.mp4"), # Default path and name
            "MP4 ឯកសារ (*.mp4);;MOV ឯកសារ (*.mov);;All Files (*)"
        )

        if file_name:
            CustomMessageBox.info(self, "កំពុងដំណើរការរក្សាទុក", "វីដេអូកំពុងត្រូវបានរក្សាទុក... សូមរង់ចាំ")
            success = self.video_processor.re_encode_video(
                self.temp_video_path,
                file_name,
                self.selected_quality
            )
            if success:
                CustomMessageBox.info(self, "បានរក្សាទុក!", f"វីដេអូត្រូវបានរក្សាទុកដោយជោគជ័យទៅ: {file_name}")
                self.accept() # Close dialog with accepted status
            else:
                CustomMessageBox.error(self, "បរាជ័យ!", "ការរក្សាទុកវីដេអូបានបរាជ័យ")
        else:
            CustomMessageBox.warning(self, "បោះបង់!", "ការរក្សាទុកត្រូវបានបោះបង់")

    def _discard_video(self):
        """
        Discards the temporary video and closes the dialog.
        """
        # Stop media player before discarding
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.stop()

        if CustomMessageBox.question(self, "បញ្ជាក់!", "តើអ្នកពិតជាចង់បោះបង់វីដេអូនេះមែនទេ?"):
            CustomMessageBox.info(self, "បានបោះបង់!", "វីដេអូត្រូវបានបោះបង់")
            self.reject() # Close dialog with rejected status

    def reject(self):
        """
        Overrides the reject method to ensure temporary file is cleaned up.
        """
        self.video_processor.delete_temp_file(self.temp_video_path)
        super().reject()

    def accept(self):
        """
        Overrides the accept method to ensure temporary file is cleaned up.
        """
        self.video_processor.delete_temp_file(self.temp_video_path)
        super().accept()
