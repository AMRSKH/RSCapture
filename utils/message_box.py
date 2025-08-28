# utils/message_box.py
from PyQt6.QtWidgets import QMessageBox

class CustomMessageBox:
    """
    Custom utility for displaying message boxes to the user.
    This avoids direct use of QMessageBox everywhere and allows for
    potential future customization of the dialog style.
    """

    @staticmethod
    def info(parent, title: str, message: str):
        """
        Displays an informational message box.
        Args:
            parent: The parent widget for the message box.
            title (str): The title of the message box.
            message (str): The message to display.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def warning(parent, title: str, message: str):
        """
        Displays a warning message box.
        Args:
            parent: The parent widget for the message box.
            title (str): The title of the message box.
            message (str): The message to display.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def error(parent, title: str, message: str):
        """
        Displays an error message box.
        Args:
            parent: The parent widget for the message box.
            title (str): The title of the message box.
            message (str): The message to display.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def question(parent, title: str, message: str) -> bool:
        """
        Displays a question message box with Yes/No buttons.
        Returns:
            bool: True if 'Yes' is clicked, False otherwise.
        """
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return msg_box.exec() == QMessageBox.StandardButton.Yes
