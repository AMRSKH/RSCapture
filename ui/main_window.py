# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QWidget,
                             QHBoxLayout, QLabel, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QDir
from PyQt6.QtGui import QIcon

import os
import tempfile

from ui.selection_overlay import SelectionOverlay
from ui.post_capture_dialog import PostCaptureDialog
from core.capture_manager import CaptureManager
from utils.message_box import CustomMessageBox

class MainWindow(QMainWindow):
    """
    The main window for the RSCapture application.
    It provides controls for screen selection, recording, stopping, and settings.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSCapture - កម្មវិធីថតអេក្រង់ (Screen Recorder)")
        self.setGeometry(100, 100, 400, 250) # x, y, width, height
        self.setWindowIcon(QIcon.fromTheme("video-display")) # Simple icon

        self.capture_manager = CaptureManager()
        self.selection_overlay = SelectionOverlay()
        self.selection_overlay.selection_made.connect(self._handle_selection_made)

        self.is_recording = False
        self.selected_rect = None # Stores (x, y, width, height) of the selected area
        self.temp_video_dir = tempfile.mkdtemp(prefix="RSCapture_temp_") # Create a temp directory
        self.current_temp_file = None

        self._setup_ui()
        self._setup_timer() # Timer for recording duration

    def _setup_ui(self):
        """
        Sets up the user interface components and their layout.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Header Section ---
        header_layout = QHBoxLayout()
        self.app_title_label = QLabel("<h1>RSCapture</h1>")
        self.app_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.app_title_label)
        main_layout.addLayout(header_layout)

        # --- Status & Timer Section ---
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setFrameShadow(QFrame.Shadow.Raised)
        status_layout = QVBoxLayout()
        status_frame.setLayout(status_layout)

        self.status_label = QLabel("ស្ថានភាព: រួចរាល់ (Status: Ready)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)

        self.timer_label = QLabel("០0:00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        status_layout.addWidget(self.timer_label)

        main_layout.addWidget(status_frame)
        main_layout.addSpacing(15)

        # --- Control Buttons Section ---
        button_layout = QHBoxLayout()

        self.btn_select_area = QPushButton("ជ្រើសរើសតំបន់ (Select Area)")
        self.btn_select_area.setIcon(QIcon.fromTheme("selection-rectangle"))
        self.btn_select_area.clicked.connect(self._start_selection)
        button_layout.addWidget(self.btn_select_area)

        self.btn_record = QPushButton("ថត (Record)")
        self.btn_record.setIcon(QIcon.fromTheme("media-record"))
        self.btn_record.clicked.connect(self._start_record)
        self.btn_record.setEnabled(False) # Disable initially, enable after area selection
        button_layout.addWidget(self.btn_record)

        self.btn_stop = QPushButton("បញ្ឈប់ (Stop)")
        self.btn_stop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.btn_stop.clicked.connect(self._stop_record)
        self.btn_stop.setEnabled(False) # Disable initially
        button_layout.addWidget(self.btn_stop)

        main_layout.addLayout(button_layout)
        main_layout.addStretch() # Push everything to the top

        self._update_ui_state() # Initial UI state update

    def _setup_timer(self):
        """
        Sets up a QTimer to update the recording duration.
        """
        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self._update_timer_display)
        self.elapsed_time_ms = 0

    def _update_ui_state(self):
        """
        Updates the enabled/disabled state of buttons based on current application state.
        """
        if self.is_recording:
            self.btn_select_area.setEnabled(False)
            self.btn_record.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.status_label.setText("ស្ថានភាព: កំពុងថត... (Status: Recording...)")
        else:
            self.btn_select_area.setEnabled(True)
            # Enable record only if an area has been selected
            self.btn_record.setEnabled(self.selected_rect is not None)
            self.btn_stop.setEnabled(False)
            self.status_label.setText("ស្ថានភាព: រួចរាល់ (Status: Ready)")

    def _start_selection(self):
        """
        Activates the selection overlay for the user to choose a screen area.
        """
        if self.is_recording:
            CustomMessageBox.warning(self, "Warning", "មិនអាចជ្រើសរើសតំបន់បានទេ ពេលកំពុងថត។ (Cannot select area while recording.)")
            return

        self.hide() # Hide main window while selection overlay is active
        self.selection_overlay.showFullScreen()
        self.selection_overlay.raise_() # Bring to front
        self.selection_overlay.activateWindow()

    def _handle_selection_made(self, x: int, y: int, width: int, height: int):
        """
        Callback for when the user has made a selection with the overlay.
        Args:
            x, y, width, height (int): Coordinates and dimensions of the selected rectangle.
        """
        self.selected_rect = (x, y, width, height)
        print(f"តំបន់ដែលបានជ្រើសរើស: ({x}, {y}) {width}x{height}")
        self.show() # Show main window again
        CustomMessageBox.info(self, "បានជ្រើសរើស (Selected)", f"តំបន់ថតត្រូវបានជ្រើសរើស: {width}x{height}")
        self._update_ui_state()

    def _start_record(self):
        """
        Initiates the screen recording process using FFmpeg.
        """
        if self.is_recording:
            CustomMessageBox.warning(self, "Warning", "ការថតកំពុងដំណើរការរួចហើយ។ (Recording is already active.)")
            return
        if not self.selected_rect:
            CustomMessageBox.warning(self, "Warning", "សូមជ្រើសរើសតំបន់ថតជាមុនសិន។ (Please select a capture area first.)")
            return

        x, y, width, height = self.selected_rect
        # Generate a unique temporary file name in the temp directory
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
        self.current_temp_file = os.path.join(self.temp_video_dir, f"rscapture_temp_{timestamp}.mkv")

        # Check if FFmpeg is available before trying to start capture
        if not self.capture_manager._check_ffmpeg():
            CustomMessageBox.error(self, "FFmpeg មិនមាន (FFmpeg Not Found)",
                                   "FFmpeg មិនត្រូវបានដំឡើងទេ។ សូមដំឡើងវាដើម្បីប្រើ RSCapture។ (FFmpeg is not installed. Please install it to use RSCapture.)"
                                   "\nឧទាហរណ៍: sudo apt install ffmpeg")
            return

        success = self.capture_manager.start_capture(x, y, width, height, self.current_temp_file)
        if success:
            self.is_recording = True
            self.elapsed_time_ms = 0
            self.record_timer.start(1000) # Update every second
            CustomMessageBox.info(self, "កំពុងថត (Recording)", "ការថតបានចាប់ផ្តើម។ (Recording has started.)")
        else:
            CustomMessageBox.error(self, "បរាជ័យ (Failed)", "ការចាប់ផ្តើមថតបានបរាជ័យ។ (Failed to start recording.)")

        self._update_ui_state()

    def _stop_record(self):
        """
        Stops the screen recording process and opens the post-capture dialog.
        """
        if not self.is_recording:
            CustomMessageBox.warning(self, "Warning", "មិនមានការថតសកម្មដើម្បីបញ្ឈប់ទេ។ (No active recording to stop.)")
            return

        self.record_timer.stop()
        self.is_recording = False
        self._update_ui_state()
        self.timer_label.setText("00:00:00") # Reset timer display

        temp_file = self.capture_manager.stop_capture()

        if temp_file and os.path.exists(temp_file):
            print(f"Temporary video saved to: {temp_file}")
            # Open PostCaptureDialog
            dialog = PostCaptureDialog(temp_file, self)
            dialog.exec() # Open dialog modally
        else:
            CustomMessageBox.error(self, "បរាជ័យ (Failed)", "ការបញ្ឈប់ការថតបានបរាជ័យ ឬរកមិនឃើញឯកសារបណ្តោះអាសន្ន។ (Failed to stop recording or temporary file not found.)")
            # Attempt to clean up even if temp_file is None or path doesn't exist.
            # The PostCaptureDialog's reject/accept handles file deletion.
            # If the file wasn't created, there's nothing to delete.

        self.current_temp_file = None # Reset temp file path

    def _update_timer_display(self):
        """
        Updates the recording timer display every second.
        """
        self.elapsed_time_ms += 1000
        seconds = (self.elapsed_time_ms // 1000) % 60
        minutes = (self.elapsed_time_ms // (1000 * 60)) % 60
        hours = (self.elapsed_time_ms // (1000 * 60 * 60))
        self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def closeEvent(self, event):
        """
        Overrides the close event to ensure FFmpeg process is terminated
        and temporary directory is cleaned up on application exit.
        """
        if self.capture_manager.is_capturing():
            if CustomMessageBox.question(self, "បញ្ជាក់ (Confirm)", "ការថតកំពុងដំណើរការ។ តើអ្នកពិតជាចង់បិទកម្មវិធីមែនទេ? (Recording is active. Are you sure you want to exit?)"):
                self.capture_manager.stop_capture() # Stop FFmpeg
                self._cleanup_temp_dir()
                event.accept()
            else:
                event.ignore()
        else:
            self._cleanup_temp_dir()
            event.accept()

    def _cleanup_temp_dir(self):
        """
        Removes the temporary directory created for storing video captures.
        """
        if os.path.exists(self.temp_video_dir):
            try:
                # Remove the directory and all its contents
                shutil.rmtree(self.temp_video_dir)
                print(f"Temporary directory cleaned up: {self.temp_video_dir}")
            except Exception as e:
                print(f"Error cleaning up temporary directory {self.temp_video_dir}: {e}")

