# core/video_processor.py
import subprocess
import os
import shutil

class VideoProcessor:
    """
    Handles post-processing of captured video files,
    specifically re-encoding to different quality levels using FFmpeg.
    """
    def __init__(self):
        self.quality_settings = {
            "Low": {"crf": 28},    # Higher CRF means lower quality, smaller file
            "Medium": {"crf": 23}, # Good balance of quality and size
            "High": {"crf": 18}    # Lower CRF means higher quality, larger file
        }

    def _check_ffmpeg(self) -> bool:
        """
        Checks if FFmpeg is installed and accessible in the system's PATH.
        Returns:
            bool: True if FFmpeg is found, False otherwise.
        """
        return shutil.which("ffmpeg") is not None

    def re_encode_video(self, input_file: str, output_file: str, quality_level: str) -> bool:
        """
        Re-encodes an input video file to a specified quality level.
        Args:
            input_file (str): Path to the input video file (e.g., temporary raw capture).
            output_file (str): Path to save the final re-encoded video file.
            quality_level (str): Desired quality level ("Low", "Medium", "High").
        Returns:
            bool: True if re-encoding was successful, False otherwise.
        """
        if not self._check_ffmpeg():
            # Error message will be handled by the caller (MainWindow)
            return False

        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            return False

        if quality_level not in self.quality_settings:
            print(f"Error: Invalid quality level '{quality_level}'. Choose from {list(self.quality_settings.keys())}")
            return False

        crf_value = self.quality_settings[quality_level]["crf"]

        # FFmpeg command to re-encode using H.264 (libx264) with Constant Rate Factor (CRF)
        ffmpeg_command = [
            "ffmpeg",
            "-i", input_file,         # Input file
            "-c:v", "libx264",        # Video codec (H.264)
            "-crf", str(crf_value),   # Constant Rate Factor for quality control
            "-preset", "medium",      # Encoding preset (medium balance of speed/quality)
            "-c:a", "copy",           # Copy audio stream without re-encoding (if present)
            "-y",                     # Overwrite output file if it exists
            output_file               # Output file
        ]

        try:
            print(f"Starting video re-encoding to {quality_level} quality (CRF={crf_value})...")
            # Run FFmpeg command blocking until completion
            result = subprocess.run(
                ffmpeg_command,
                check=True, # Raise CalledProcessError if the command returns a non-zero exit code
                capture_output=True,
                text=True
            )
            print(f"Video re-encoding successful. Output: {output_file}")
            # print("FFmpeg stdout:", result.stdout)
            # print("FFmpeg stderr:", result.stderr)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during video re-encoding: {e}")
            print("FFmpeg stdout:", e.stdout)
            print("FFmpeg stderr:", e.stderr)
            return False
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please ensure it's installed and in your PATH.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during re-encoding: {e}")
            return False

    def delete_temp_file(self, file_path: str):
        """
        Deletes a temporary file.
        Args:
            file_path (str): Path to the file to be deleted.
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Temporary file deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting temporary file {file_path}: {e}")
