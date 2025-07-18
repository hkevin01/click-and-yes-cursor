"""
PyQt5 GUI for configuration and global mouse tracking for Click & Yes Cursor.
Uses QThread for mouse polling to avoid QSocketNotifier error.
"""
import json
import os
import sys

import pyautogui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MouseWorker(QThread):
    positionChanged = pyqtSignal(int, int)

    def run(self):
        while True:
            pos = pyautogui.position()
            self.positionChanged.emit(pos.x, pos.y)
            self.msleep(100)


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
        self.waiting_label = QLabel('Waiting Time (seconds):')
        self.waiting_entry = QLineEdit()
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
        layout.addWidget(self.waiting_label)
        layout.addWidget(self.waiting_entry)
        layout.addWidget(self.mouse_label)
        layout.addWidget(self.set_mouse_btn)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.mouse_worker = MouseWorker()
        self.mouse_worker.positionChanged.connect(self.update_mouse_position)
        self.mouse_worker.start()
        self._last_pos = (0, 0)

        self.load_config()

    def update_mouse_position(self, x, y):
        self.mouse_label.setText(f'Global Mouse Position: ({x}, {y})')
        self._last_pos = (x, y)

    def set_xy_to_mouse(self):
        x, y = self._last_pos
        self.x_entry.setText(str(x))
        self.y_entry.setText(str(y))

    def load_config(self):
        config_path = os.path.join(
            os.path.dirname(__file__), '../src/config.json'
        )
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                    coords = config.get('coordinates', {})
                    self.x_entry.setText(str(coords.get('x', '')))
                    self.y_entry.setText(str(coords.get('y', '')))
                    self.msg_entry.setText(config.get('message', ''))
                    self.waiting_entry.setText(
                        str(config.get('waiting_time', ''))
                    )
                except Exception:
                    pass

    def save_config(self):
        config = {
            "coordinates": {
                "x": int(self.x_entry.text()),
                "y": int(self.y_entry.text())
            },
            "waiting_time": float(self.waiting_entry.text()),
            "message": self.msg_entry.text()
        }
        with open(
            os.path.join(os.path.dirname(__file__), '../src/config.json'),
            'w', encoding='utf-8'
        ) as f:
            json.dump(config, f, indent=4)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
