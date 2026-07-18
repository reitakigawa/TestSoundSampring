"""PySide6 GUI for AutoOtoMaker."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from kana import to_hiragana
from oto import generate_oto_entries, write_oto_ini
from settings import SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_JSON_EXTENSIONS
from whisper_loader import WordSegment, load_whisperx_json


class MainWindow(QMainWindow):
    """Main drag-and-drop window for editing recognition and readings."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AutoOtoMaker")
        self.setAcceptDrops(True)
        self.wav_path: Path | None = None
        self.segments: list[WordSegment] = []

        self.status = QLabel("WAVとWhisperX JSONをドラッグ&ドロップしてください")
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["認識文", "読み", "開始", "終了", "状態"])
        self.table.itemChanged.connect(self._item_changed)

        load_wav = QPushButton("WAV読込")
        load_json = QPushButton("WhisperX JSON読込")
        export = QPushButton("oto.ini生成")
        load_wav.clicked.connect(self.pick_wav)
        load_json.clicked.connect(self.pick_json)
        export.clicked.connect(self.export_oto)

        buttons = QHBoxLayout()
        buttons.addWidget(load_wav)
        buttons.addWidget(load_json)
        buttons.addWidget(export)

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addLayout(buttons)
        layout.addWidget(self.table)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def dragEnterEvent(self, event):  # noqa: N802 - Qt API
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):  # noqa: N802 - Qt API
        for url in event.mimeData().urls():
            self.load_path(Path(url.toLocalFile()))

    def load_path(self, path: Path) -> None:
        suffix = path.suffix.lower()
        if suffix in SUPPORTED_AUDIO_EXTENSIONS:
            self.wav_path = path
            self.status.setText(f"WAV: {path.name}")
        elif suffix in SUPPORTED_JSON_EXTENSIONS:
            self.segments = load_whisperx_json(path)
            self.populate_table()
            self.status.setText(f"JSON: {path.name} ({len(self.segments)}語)")

    def pick_wav(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "WAVを選択", "", "WAV (*.wav)")
        if path:
            self.load_path(Path(path))

    def pick_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "WhisperX JSONを選択", "", "JSON (*.json)")
        if path:
            self.load_path(Path(path))

    def populate_table(self) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.segments))
        for row, segment in enumerate(self.segments):
            values = [segment.text, segment.reading, f"{segment.start:.3f}", f"{segment.end:.3f}", "未発声" if segment.missing else "OK"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col >= 2:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if segment.missing:
                    item.setBackground(QColor("#ffcccc"))
                self.table.setItem(row, col, item)
        self.table.blockSignals(False)

    def _item_changed(self, item: QTableWidgetItem) -> None:
        segment = self.segments[item.row()]
        if item.column() == 0:
            segment.text = item.text()
            segment.reading = to_hiragana(segment.text)
        elif item.column() == 1:
            segment.reading = item.text()
        segment.refresh_reading()
        self.populate_table()

    def export_oto(self) -> None:
        if not self.wav_path or not self.segments:
            self.status.setText("WAVとJSONを先に読み込んでください")
            return
        path, _ = QFileDialog.getSaveFileName(self, "oto.iniを保存", str(self.wav_path.with_name("oto.ini")), "INI (*.ini)")
        if path:
            entries = generate_oto_entries(self.wav_path.name, self.segments)
            write_oto_ini(path, entries)
            self.status.setText(f"oto.iniを生成しました: {len(entries)}件")


def run() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(900, 600)
    window.show()
    app.exec()
