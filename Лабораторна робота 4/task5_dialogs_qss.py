"""Завдання 5. Діалогові вікна та QSS-стилізація (менеджер нотаток)."""
import sys
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox, QInputDialog,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox, QDialogButtonBox,
    QCheckBox,
)

STYLESHEET = """
QWidget {
    background-color: #f4f6fb;
    font-family: "Segoe UI", Arial;
    font-size: 14px;
}
QLabel { color: #2c3e50; }
QLabel#titleLabel {                 /* стилізація за objectName */
    font-size: 22px;
    font-weight: bold;
    color: #1a5276;
}
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}
QPushButton:hover    { background-color: #2e86c1; }
QPushButton:pressed  { background-color: #1b4f72; }
QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }
QPushButton#dangerButton { background-color: #e74c3c; }
QPushButton#dangerButton:hover { background-color: #c0392b; }
QLineEdit, QTextEdit, QComboBox {
    background-color: white;
    border: 2px solid #aab7c4;
    border-radius: 5px;
    padding: 4px;
}
QLineEdit:focus, QTextEdit:focus { border: 2px solid #3498db; }
QListWidget {
    background-color: white;
    border: 1px solid #aab7c4;
    border-radius: 5px;
}
QListWidget::item:selected { background-color: #d6eaf8; color: black; }
"""

PRIORITY_COLORS = {"Низький": "#d5f5e3", "Середній": "#fcf3cf", "Високий": "#f5b7b1"}


class NoteDialog(QDialog):
    """Власний модальний діалог: повертає дані нотатки."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Нова нотатка")
        self.setModal(True)
        self.setMinimumWidth(360)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Заголовок")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Текст нотатки")
        self.priority_box = QComboBox()
        self.priority_box.addItems(list(PRIORITY_COLORS))

        form = QFormLayout()
        form.addRow("Заголовок:", self.title_edit)
        form.addRow("Текст:", self.text_edit)
        form.addRow("Пріоритет:", self.priority_box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Помилка", "Заголовок не може бути порожнім.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "text": self.text_edit.toPlainText().strip(),
            "priority": self.priority_box.currentText(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 5 — Нотатки")
        self.resize(520, 480)
        self.username = "Гість"

        central = QWidget()
        self.setCentralWidget(central)

        self.title_label = QLabel(f"Нотатки користувача: {self.username}")
        self.title_label.setObjectName("titleLabel")
        self.list = QListWidget()

        self.add_btn = QPushButton("Додати нотатку")       
        self.rename_btn = QPushButton("Змінити ім'я")     
        self.delete_btn = QPushButton("Видалити")          
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setEnabled(False)                  
        self.style_check = QCheckBox("Застосувати QSS-стилі")
        self.style_check.setChecked(True)

        btns = QHBoxLayout()
        for b in (self.add_btn, self.rename_btn, self.delete_btn):
            btns.addWidget(b)
        layout = QVBoxLayout(central)
        layout.addWidget(self.title_label)
        layout.addWidget(self.list)
        layout.addLayout(btns)
        layout.addWidget(self.style_check)

        self.add_btn.clicked.connect(self.add_note)
        self.rename_btn.clicked.connect(self.rename_user)
        self.delete_btn.clicked.connect(self.delete_note)
        self.list.itemSelectionChanged.connect(
            lambda: self.delete_btn.setEnabled(bool(self.list.selectedItems())))
        self.style_check.toggled.connect(self.toggle_style)

    def add_note(self):
        dlg = NoteDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            item = QListWidgetItem(f"{data['title']} [{data['priority']}]\n{data['text']}")
            item.setBackground(QColor(PRIORITY_COLORS[data["priority"]]))
            self.list.addItem(item)
            self.statusBar().showMessage(f"Додано: {data['title']}", 3000)

    def rename_user(self):
        name, ok = QInputDialog.getText(self, "Ім'я користувача",
                                        "Введіть ваше ім'я:", text=self.username)
        if ok and name.strip():
            self.username = name.strip()
            self.title_label.setText(f"Нотатки користувача: {self.username}")

    def delete_note(self):
        item = self.list.currentItem()
        if item is None:
            return
        answer = QMessageBox.question(
            self, "Підтвердження", "Видалити вибрану нотатку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.list.takeItem(self.list.row(item))

    def toggle_style(self, on: bool):
        QApplication.instance().setStyleSheet(STYLESHEET if on else "")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
