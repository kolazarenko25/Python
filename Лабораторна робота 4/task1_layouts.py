"""Завдання 1. Вікно з базовими віджетами та менеджерами компонування."""
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox, QRadioButton,
    QSlider, QSpinBox, QProgressBar, QPushButton,
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 1 — Анкета студента")
        self.setMinimumSize(520, 560)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введіть прізвище та ім'я")
        self.name_edit.setToolTip("Повне ім'я студента")

        self.course_box = QComboBox()
        self.course_box.addItems(["1 курс", "2 курс", "3 курс", "4 курс"])
        self.course_box.setCurrentIndex(1)
        self.course_box.setToolTip("Оберіть курс навчання")

        self.age_spin = QSpinBox()
        self.age_spin.setRange(16, 60)
        self.age_spin.setValue(19)
        self.age_spin.setToolTip("Вік: від 16 до 60")

        form = QFormLayout()
        form.addRow("Ім'я:", self.name_edit)
        form.addRow("Курс:", self.course_box)
        form.addRow("Вік:", self.age_spin)

        self.radio_budget = QRadioButton("Бюджет")
        self.radio_contract = QRadioButton("Контракт")
        self.radio_budget.setChecked(True)
        self.radio_contract.setToolTip("Форма фінансування")
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_budget)
        radio_layout.addWidget(self.radio_contract)
        radio_group = QGroupBox("Форма навчання")
        radio_group.setLayout(radio_layout)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(30)
        self.slider.setToolTip("Рівень підготовки, %")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(30)
        self.slider.valueChanged.connect(self.progress.setValue)
        skill_layout = QVBoxLayout()
        skill_layout.addWidget(QLabel("Рівень підготовки:"))
        skill_layout.addWidget(self.slider)
        skill_layout.addWidget(self.progress)

        self.newsletter = QCheckBox("Отримувати розсилку")
        self.newsletter.setChecked(True)
        self.newsletter.setToolTip("Новини кафедри на e-mail")

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Додаткова інформація...")
        self.notes.setToolTip("Довільні нотатки")

        self.ok_btn = QPushButton("Зберегти")
        self.ok_btn.setToolTip("Зберегти анкету")
        self.cancel_btn = QPushButton("Скасувати")
        self.cancel_btn.setEnabled(False)  
        self.cancel_btn.setToolTip("Поки недоступно")
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        main = QVBoxLayout(self)
        main.addWidget(QLabel("<h3>Анкета студента</h3>"))
        main.addLayout(form)
        main.addWidget(radio_group)
        main.addLayout(skill_layout)
        main.addWidget(self.newsletter)
        main.addWidget(self.notes, stretch=1)  
        main.addLayout(btn_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
