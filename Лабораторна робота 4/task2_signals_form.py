"""Завдання 2. Інтерактивна форма: сигнали/слоти, скидання, валідація."""
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QComboBox, QCheckBox, QSlider, QPushButton,
    QMessageBox,
)


def validate(name: str, age: int, country: str):
    """Єдина функція валідації. Повертає список помилок (порожній = все ОК)."""
    errors = []
    if not name.strip():
        errors.append("Ім'я не може бути порожнім.")
    elif len(name.strip()) < 2:
        errors.append("Ім'я має містити щонайменше 2 символи.")
    if not (18 <= age <= 99):
        errors.append("Вік має бути в діапазоні 18–99.")
    if not country:
        errors.append("Оберіть країну.")
    return errors


def char_counter_text(text: str) -> str:
    """Звичайна функція (не метод класу) — використовується як слот."""
    return f"Символів: {len(text)}"


class RegistrationForm(QWidget):
    COUNTRIES = ["", "Україна", "Польща", "Німеччина", "Чехія"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 2 — Форма реєстрації")
        self.setMinimumWidth(400)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ваше ім'я")
        self.counter_label = QLabel(char_counter_text(""))

        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 120)
        self.age_spin.setValue(18)

        self.country_box = QComboBox()
        self.country_box.addItems(self.COUNTRIES)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_label = QLabel("Гучність сповіщень: 50")

        self.agree_check = QCheckBox("Погоджуюсь з умовами")
        self.submit_btn = QPushButton("Підтвердити")
        self.submit_btn.setEnabled(False)
        self.reset_btn = QPushButton("Скинути")
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Ім'я:", self.name_edit)
        form.addRow("", self.counter_label)
        form.addRow("Вік:", self.age_spin)
        form.addRow("Країна:", self.country_box)

        buttons = QHBoxLayout()
        buttons.addWidget(self.submit_btn)
        buttons.addWidget(self.reset_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.agree_check)
        layout.addLayout(buttons)
        layout.addWidget(self.result_label)

        self._connect_signals()

    def _connect_signals(self):
        self.name_edit.textChanged.connect(
            lambda t: self.counter_label.setText(char_counter_text(t)))
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"Гучність сповіщень: {v}"))
        self.agree_check.toggled.connect(self.submit_btn.setEnabled)
        self.submit_btn.clicked.connect(self.on_submit)
        self.reset_btn.clicked.connect(self.reset_form)

    def on_submit(self):
        errors = validate(self.name_edit.text(), self.age_spin.value(),
                          self.country_box.currentText())
        if errors:
            self.result_label.setStyleSheet("color: red;")
            self.result_label.setText("Помилки:\n" + "\n".join(errors))
            QMessageBox.warning(self, "Некоректні дані", "\n".join(errors))
        else:
            self.result_label.setStyleSheet("color: green;")
            self.result_label.setText(
                f"Успіх! {self.name_edit.text().strip()}, "
                f"{self.age_spin.value()} р., {self.country_box.currentText()}.")

    def reset_form(self):
        self.name_edit.clear()
        self.age_spin.setValue(18)
        self.country_box.setCurrentIndex(0)
        self.volume_slider.setValue(50)
        self.agree_check.setChecked(False)  
        self.result_label.clear()
        self.result_label.setStyleSheet("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = RegistrationForm()
    w.show()
    sys.exit(app.exec())
