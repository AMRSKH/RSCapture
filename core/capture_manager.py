# core/capture_manager.py
import subprocess
import os
import shutil
from typing import Optional

class CaptureManager:
    """
    Manages the screen capture process using FFmpeg.
    It initiates FFmpeg as a subprocess and provides methods to stop it.
    """
    def __init__(self):
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        self.temp_output_file: Optional[str] = None

    def _check_ffmpeg(self) -> bool:
        """
        Checks if FFmpeg is installed and accessible in the system's PATH.
        Returns:
            bool: True if FFmpeg is found, False otherwise.
        """
        return shutil.which("ffmpeg") is not None

    def start_capture(self, x: int, y: int, width: int, height: int, output_file: str) -> bool:
        """
        Starts the screen capture using FFmpeg.
        Args:
            x (int): X-coordinate of the top-left corner of the capture area.
            y (int): Y-coordinate of the top-left corner of the capture area.
            width (int): Width of the capture area.
            height (int): Height of the capture area.
            output_file (str): Path to save the temporary raw video file.
        Returns:
            bool: True if capture started successfully, False otherwise.
        """
        if not self._check_ffmpeg():
            # Error message will be handled by the caller (MainWindow)
            return False

        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            # Capture is already running
            return False

        self.temp_output_file = output_file
        display = os.getenv("DISPLAY", ":0.0") # Get current display, default to :0.0 for X11

        # FFmpeg command for X11 screen grabbing on Linux
        # -f x11grab: input format for X11 grabbing
        # -s <width>x<height>: specify capture resolution
        # -i :0.0+<x_offset>,<y_offset>: input display and offset for the capture area
        # -c:v libx264: video codec (H.264)
        # -preset ultrafast: fastest encoding preset, lowest CPU usage, larger file size
        # -qp 0: Constant Quantization Parameter for near-lossless quality (larger file)
        # This is for a raw, high-quality temporary file.
        ffmpeg_command = [
            "ffmpeg",
            "-f", "x11grab",
            "-s", f"{width}x{height}",
            "-i", f"{display}+{x},{y}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-qp", "0", # Near-lossless quality for the temporary file
            self.temp_output_file
        ]

        try:
            # Start FFmpeg as a non-blocking subprocess
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"FFmpeg capture started. Output: {self.temp_output_file}")
            return True
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please ensure it's installed and in your PATH.")
            return False
        except Exception as e:
            print(f"Error starting FFmpeg capture: {e}")
            return False

    def stop_capture(self) -> Optional[str]:
        """
        Stops the running FFmpeg screen capture process.
        Returns:
            Optional[str]: Path to the temporary output file if capture was stopped, None otherwise.
        """
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            print("Stopping FFmpeg process...")
            self.ffmpeg_process.terminate() # Send SIGTERM
            self.ffmpeg_process.wait(timeout=5) # Wait for process to terminate
            if self.ffmpeg_process.poll() is None:
                self.ffmpeg_process.kill() # If still running, send SIGKILL
                self.ffmpeg_process.wait()
            print("FFmpeg process stopped.")
            return self.temp_output_file
        else:
            print("No active FFmpeg capture to stop.")
            return None

    def is_capturing(self) -> bool:
        """
        Checks if the capture process is currently active.
        Returns:
            bool: True if capturing, False otherwise.
        """
        return self.ffmpeg_process is not None and self.ffmpeg_process.poll() is None
