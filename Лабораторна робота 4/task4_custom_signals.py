"""Завдання 4. Кастомні сигнали та слабке зв'язування компонентів."""
import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QSpinBox, QListWidget, QCheckBox, QMessageBox,
    QGroupBox,
)

LEVELS = {0: "низький", 1: "середній", 2: "високий"}


class InputPanel(QWidget):
    itemSubmitted = pyqtSignal(str)
    levelChanged = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Новий елемент...")
        self.add_btn = QPushButton("Додати")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 2)
        self.spin = QSpinBox()
        self.spin.setRange(0, 2)

        row = QHBoxLayout()
        row.addWidget(self.edit)
        row.addWidget(self.add_btn)
        lvl = QHBoxLayout()
        lvl.addWidget(QLabel("Рівень:"))
        lvl.addWidget(self.slider)
        lvl.addWidget(self.spin)
        box = QVBoxLayout(self)
        box.addLayout(row)
        box.addLayout(lvl)

        self.add_btn.clicked.connect(self._submit)
        self.edit.returnPressed.connect(self._submit)
        self.slider.valueChanged.connect(self._on_slider)
        self.spin.valueChanged.connect(self._on_spin)

    def _submit(self):
        text = self.edit.text().strip()
        if text:
            self.itemSubmitted.emit(text)
            self.edit.clear()

    def _on_slider(self, v):
        self.spin.blockSignals(True)
        self.spin.setValue(v)
        self.spin.blockSignals(False)
        self.levelChanged.emit(v, LEVELS[v])

    def _on_spin(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(v)
        self.slider.blockSignals(False)
        self.levelChanged.emit(v, LEVELS[v])


class DisplayPanel(QWidget):
    itemsExported = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.level_label = QLabel("Поточний рівень: низький")
        self.list = QListWidget()
        self.export_btn = QPushButton("Експорт")
        self.clear_btn = QPushButton("Очистити")
        self._level = LEVELS[0]

        btns = QHBoxLayout()
        btns.addWidget(self.export_btn)
        btns.addWidget(self.clear_btn)
        box = QVBoxLayout(self)
        box.addWidget(self.level_label)
        box.addWidget(self.list)
        box.addLayout(btns)

        self.export_btn.clicked.connect(self._export)
        self.clear_btn.clicked.connect(self.list.clear)

    def add_item(self, text: str):
        self.list.addItem(f"[{self._level}] {text}")

    def set_level(self, value: int, name: str):
        self._level = name
        self.level_label.setText(f"Поточний рівень: {name} ({value})")

    def _export(self):
        items = [self.list.item(i).text() for i in range(self.list.count())]
        self.itemsExported.emit(items)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 4 — Кастомні сигнали")
        self.resize(420, 420)

        self.input_panel = InputPanel()
        self.display_panel = DisplayPanel()
        self.link_check = QCheckBox("Передавати рівень у панель відображення")
        self.link_check.setChecked(True)
        self.status = QLabel("")

        g1, g2 = QGroupBox("Введення"), QGroupBox("Відображення")
        QVBoxLayout(g1).addWidget(self.input_panel)
        QVBoxLayout(g2).addWidget(self.display_panel)
        layout = QVBoxLayout(self)
        layout.addWidget(g1)
        layout.addWidget(g2)
        layout.addWidget(self.link_check)
        layout.addWidget(self.status)

        self.input_panel.itemSubmitted.connect(self.display_panel.add_item)
        self.input_panel.levelChanged.connect(self.display_panel.set_level)
        self.display_panel.itemsExported.connect(self.on_exported)
        self.link_check.toggled.connect(self.toggle_link)

    def toggle_link(self, on: bool):
        """Демонстрація disconnect: відключаємо/підключаємо передачу рівня."""
        if on:
            self.input_panel.levelChanged.connect(self.display_panel.set_level)
            self.status.setText("Сигнал levelChanged підключено.")
        else:
            self.input_panel.levelChanged.disconnect(self.display_panel.set_level)
            self.status.setText("Сигнал levelChanged відключено — мітка рівня не оновлюється.")

    def on_exported(self, items: list):
        self.status.setText(f"Експортовано елементів: {len(items)}")
        QMessageBox.information(self, "Експорт",
                                "\n".join(items) if items else "Список порожній.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
