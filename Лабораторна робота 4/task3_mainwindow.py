"""Завдання 3. Текстовий редактор на QMainWindow: меню, toolbar, statusBar."""
import sys
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox, QLabel,
)


class Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Завдання 3 — Простий редактор")
        self.resize(700, 500)
        self.current_path = None

        self.text = QTextEdit()
        self.setCentralWidget(self.text)

        self._create_actions()
        self._create_menu()
        self._create_toolbar()

        self.count_label = QLabel("Символів: 0")
        self.statusBar().addPermanentWidget(self.count_label)
        self.statusBar().showMessage("Готово", 3000)
        self.text.textChanged.connect(self.update_count)

    def _create_actions(self):
        self.new_act = QAction("Новий", self)
        self.new_act.setShortcut(QKeySequence.StandardKey.New) 
        self.new_act.setStatusTip("Створити новий документ")
        self.new_act.triggered.connect(self.new_file)

        self.open_act = QAction("Відкрити...", self)
        self.open_act.setShortcut(QKeySequence.StandardKey.Open)
        self.open_act.setStatusTip("Відкрити текстовий файл")
        self.open_act.triggered.connect(self.open_file)

        self.save_act = QAction("Зберегти як...", self)
        self.save_act.setShortcut(QKeySequence("Ctrl+S"))
        self.save_act.setStatusTip("Зберегти документ у файл")
        self.save_act.triggered.connect(self.save_file)

        self.exit_act = QAction("Вихід", self)
        self.exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_act.triggered.connect(self.close)

        self.about_act = QAction("Про програму", self)
        self.about_act.setStatusTip("Інформація про програму")
        self.about_act.triggered.connect(self.show_about)

        self.help_act = QAction("Довідка", self)
        self.help_act.setShortcut(QKeySequence("F1"))
        self.help_act.triggered.connect(lambda: QMessageBox.information(
            self, "Довідка", "Використовуйте меню «Файл» для роботи з файлами."))

    def _create_menu(self):
        bar = self.menuBar()
        file_menu = bar.addMenu("&Файл")
        file_menu.addActions([self.new_act, self.open_act, self.save_act])
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        help_menu = bar.addMenu("&Довідка")
        help_menu.addActions([self.help_act, self.about_act])

    def _create_toolbar(self):
        tb = self.addToolBar("Основна")
        tb.addActions([self.new_act, self.open_act, self.save_act])
        tb.addSeparator()
        tb.addAction(self.about_act)

    def update_count(self):
        n = len(self.text.toPlainText())
        self.count_label.setText(f"Символів: {n}")

    def new_file(self):
        self.text.clear()
        self.current_path = None
        self.statusBar().showMessage("Створено новий документ", 3000)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Відкрити файл", "", "Текстові файли (*.txt);;Усі файли (*)")
        if not path:
            self.statusBar().showMessage("Відкриття скасовано", 3000)
            return
        try:
            with open(path, encoding="utf-8") as f:
                self.text.setPlainText(f.read())
            self.current_path = path
            self.statusBar().showMessage(f"Відкрито: {path}", 5000)
        except OSError as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти файл", self.current_path or "",
            "Текстові файли (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.toPlainText())
            self.current_path = path
            self.statusBar().showMessage(f"Збережено: {path}", 5000)
        except OSError as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def show_about(self):
        QMessageBox.about(self, "Про програму",
                          "Простий редактор\nЛабораторна робота з PyQt6")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Editor()
    w.show()
    sys.exit(app.exec())
