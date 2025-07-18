"""
PyQt5 GUI for configuration and global mouse tracking for Click & Yes Cursor.
"""
import sys
import json
import os
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Click & Yes Cursor Config')
        self.x_label = QLabel('X:')
        self.x_entry = QLineEdit()
        self.y_label = QLabel('Y:')
        self.y_entry = QLineEdit()
        self.msg_label = QLabel('Message:')
        self.msg_entry = QLineEdit()
        self.mouse_label = QLabel('Global Mouse Position: (0, 0)')
        self.set_mouse_btn = QPushButton('Set X/Y to Mouse Position')
        self.set_mouse_btn.clicked.connect(self.set_xy_to_mouse)
        self.save_btn = QPushButton('Save')
        self.save_btn.clicked.connect(self.save_config)

        layout = QVBoxLayout()
        layout.addWidget(self.x_label)
        layout.addWidget(self.x_entry)
        layout.addWidget(self.y_label)
        layout.addWidget(self.y_entry)
        layout.addWidget(self.msg_label)
        layout.addWidget(self.msg_entry)
        layout.addWidget(self.mouse_label)
        layout.addWidget(self.set_mouse_btn)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)

    def update_mouse_position(self):
        pos = pyautogui.position()
        self.mouse_label.setText(f'Global Mouse Position: ({pos.x}, {pos.y})')

    def set_xy_to_mouse(self):
        pos = pyautogui.position()
        self.x_entry.setText(str(pos.x))
        self.y_entry.setText(str(pos.y))

    def save_config(self):
        config = {
            "coordinates": {"x": int(self.x_entry.text()), "y": int(self.y_entry.text())},
            "message": self.msg_entry.text()
        }
        with open(os.path.join(os.path.dirname(__file__), '../src/config.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
