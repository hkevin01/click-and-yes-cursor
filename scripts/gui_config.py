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
    QCheckBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
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
        self.setGeometry(100, 100, 600, 500)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create tabs
        self.basic_tab = self.create_basic_tab()
        self.messages_tab = self.create_messages_tab()
        self.notifications_tab = self.create_notifications_tab()

        # Add tabs
        self.tab_widget.addTab(self.basic_tab, "Basic Settings")
        self.tab_widget.addTab(self.messages_tab, "Messages")
        self.tab_widget.addTab(self.notifications_tab, "Notifications")

        # Save button
        self.save_btn = QPushButton('Save Configuration')
        self.save_btn.clicked.connect(self.save_config)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.mouse_worker = MouseWorker()
        self.mouse_worker.positionChanged.connect(self.update_mouse_position)
        self.mouse_worker.start()
        self._last_pos = (0, 0)

        self.load_config()

    def create_basic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Coordinates
        coord_group = QGroupBox("Coordinates")
        coord_layout = QVBoxLayout()

        self.x_label = QLabel('X:')
        self.x_entry = QLineEdit()
        self.y_label = QLabel('Y:')
        self.y_entry = QLineEdit()
        self.mouse_label = QLabel('Global Mouse Position: (0, 0)')
        self.set_mouse_btn = QPushButton('Set X/Y to Mouse Position')
        self.set_mouse_btn.clicked.connect(self.set_xy_to_mouse)

        coord_layout.addWidget(self.x_label)
        coord_layout.addWidget(self.x_entry)
        coord_layout.addWidget(self.y_label)
        coord_layout.addWidget(self.y_entry)
        coord_layout.addWidget(self.mouse_label)
        coord_layout.addWidget(self.set_mouse_btn)
        coord_group.setLayout(coord_layout)

        # Waiting time
        self.waiting_label = QLabel('Waiting Time (seconds):')
        self.waiting_entry = QLineEdit()

        layout.addWidget(coord_group)
        layout.addWidget(self.waiting_label)
        layout.addWidget(self.waiting_entry)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_messages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Messages (one per line, format: text|weight)"))
        layout.addWidget(QLabel("Example: yes, continue|5"))

        self.messages_text = QTextEdit()
        layout.addWidget(self.messages_text)

        tab.setLayout(layout)
        return tab

    def create_notifications_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()

        self.notifications_enabled = QCheckBox("Enable Notifications")
        self.error_threshold_label = QLabel("Error Threshold:")
        self.error_threshold = QSpinBox()
        self.error_threshold.setRange(1, 10)
        self.error_threshold.setValue(3)

        self.cooldown_label = QLabel("Notification Cooldown (seconds):")
        self.cooldown = QSpinBox()
        self.cooldown.setRange(60, 3600)
        self.cooldown.setValue(300)

        general_layout.addWidget(self.notifications_enabled)
        general_layout.addWidget(self.error_threshold_label)
        general_layout.addWidget(self.error_threshold)
        general_layout.addWidget(self.cooldown_label)
        general_layout.addWidget(self.cooldown)
        general_group.setLayout(general_layout)

        # Email settings
        email_group = QGroupBox("Email Notifications")
        email_layout = QVBoxLayout()

        self.email_enabled = QCheckBox("Enable Email Notifications")
        self.smtp_server_label = QLabel("SMTP Server:")
        self.smtp_server = QLineEdit("smtp.gmail.com")
        self.smtp_port_label = QLabel("SMTP Port:")
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        self.username_label = QLabel("Username:")
        self.username = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.from_email_label = QLabel("From Email:")
        self.from_email = QLineEdit()
        self.to_email_label = QLabel("To Email:")
        self.to_email = QLineEdit()
        self.use_tls = QCheckBox("Use TLS")
        self.use_tls.setChecked(True)

        email_layout.addWidget(self.email_enabled)
        email_layout.addWidget(self.smtp_server_label)
        email_layout.addWidget(self.smtp_server)
        email_layout.addWidget(self.smtp_port_label)
        email_layout.addWidget(self.smtp_port)
        email_layout.addWidget(self.username_label)
        email_layout.addWidget(self.username)
        email_layout.addWidget(self.password_label)
        email_layout.addWidget(self.password)
        email_layout.addWidget(self.from_email_label)
        email_layout.addWidget(self.from_email)
        email_layout.addWidget(self.to_email_label)
        email_layout.addWidget(self.to_email)
        email_layout.addWidget(self.use_tls)
        email_group.setLayout(email_layout)

        # Webhook settings
        webhook_group = QGroupBox("Webhook Notifications")
        webhook_layout = QVBoxLayout()

        self.webhook_enabled = QCheckBox("Enable Webhook Notifications")
        self.webhook_url_label = QLabel("Webhook URL:")
        self.webhook_url = QLineEdit()

        webhook_layout.addWidget(self.webhook_enabled)
        webhook_layout.addWidget(self.webhook_url_label)
        webhook_layout.addWidget(self.webhook_url)
        webhook_group.setLayout(webhook_layout)

        layout.addWidget(general_group)
        layout.addWidget(email_group)
        layout.addWidget(webhook_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

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

                    # Basic settings
                    coords = config.get('coordinates', {})
                    self.x_entry.setText(str(coords.get('x', '')))
                    self.y_entry.setText(str(coords.get('y', '')))
                    self.waiting_entry.setText(
                        str(config.get('waiting_time', ''))
                    )

                    # Messages
                    messages = config.get('message', [])
                    if isinstance(messages, list):
                        message_lines = []
                        for msg in messages:
                            if isinstance(msg, dict):
                                text = msg.get('text', '')
                                weight = msg.get('weight', 1)
                                message_lines.append(f"{text}|{weight}")
                            else:
                                message_lines.append(str(msg))
                        self.messages_text.setPlainText(
                            '\n'.join(message_lines)
                        )
                    else:
                        self.messages_text.setPlainText(str(messages))

                    # Notifications
                    notifications = config.get('notifications', {})
                    self.notifications_enabled.setChecked(
                        notifications.get('enabled', False)
                    )
                    self.error_threshold.setValue(
                        notifications.get('error_threshold', 3)
                    )
                    self.cooldown.setValue(
                        notifications.get('notification_cooldown', 300)
                    )

                    email = notifications.get('email', {})
                    self.email_enabled.setChecked(email.get('enabled', False))
                    self.smtp_server.setText(
                        email.get('smtp_server', 'smtp.gmail.com')
                    )
                    self.smtp_port.setValue(email.get('smtp_port', 587))
                    self.username.setText(email.get('username', ''))
                    self.password.setText(email.get('password', ''))
                    self.from_email.setText(email.get('from_email', ''))
                    self.to_email.setText(email.get('to_email', ''))
                    self.use_tls.setChecked(email.get('use_tls', True))

                    webhook = notifications.get('webhook', {})
                    self.webhook_enabled.setChecked(
                        webhook.get('enabled', False)
                    )
                    self.webhook_url.setText(webhook.get('url', ''))

                except Exception as e:
                    print(f"Error loading config: {e}")

    def save_config(self):
        # Parse messages
        message_lines = self.messages_text.toPlainText().strip().split('\n')
        messages = []
        for line in message_lines:
            line = line.strip()
            if line:
                if '|' in line:
                    text, weight_str = line.split('|', 1)
                    try:
                        weight = int(weight_str)
                    except ValueError:
                        weight = 1
                    messages.append({
                        "text": text.strip(),
                        "weight": weight
                    })
                else:
                    messages.append({"text": line, "weight": 1})

        config = {
            "coordinates": {
                "x": int(self.x_entry.text() or 0),
                "y": int(self.y_entry.text() or 0)
            },
            "waiting_time": float(self.waiting_entry.text() or 0.5),
            "notifications": {
                "enabled": self.notifications_enabled.isChecked(),
                "error_threshold": self.error_threshold.value(),
                "notification_cooldown": self.cooldown.value(),
                "email": {
                    "enabled": self.email_enabled.isChecked(),
                    "smtp_server": self.smtp_server.text(),
                    "smtp_port": self.smtp_port.value(),
                    "username": self.username.text(),
                    "password": self.password.text(),
                    "from_email": self.from_email.text(),
                    "to_email": self.to_email.text(),
                    "use_tls": self.use_tls.isChecked()
                },
                "webhook": {
                    "enabled": self.webhook_enabled.isChecked(),
                    "url": self.webhook_url.text(),
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            },
            "message": messages
        }

        config_path = os.path.join(
            os.path.dirname(__file__), '../src/config.json'
        )
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print("Configuration saved successfully!")
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
