"""PySide6 GUI for editing single-sound oto.ini files."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from audio import is_unvoiced
from oto_loader import SingleOtoEntry, load_folder, save_oto_ini


class MainWindow(QMainWindow):
    """Folder-based editor for already-split single-sound WAV files."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SingleOtoEditor")
        self.setAcceptDrops(True)
        self.folder: Path | None = None
        self.entries: list[SingleOtoEntry] = []
        self.player = QSoundEffect(self)

        self.status = QLabel("WAVフォルダをドラッグ&ドロップ、またはフォルダ読込してください")
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["WAV", "エイリアス", "Offset", "固定範囲", "右ブランク", "先行発声", "オーバーラップ", "状態"])
        self.table.itemChanged.connect(self._item_changed)

        open_folder = QPushButton("フォルダ読込")
        play = QPushButton("選択WAV再生")
        delete = QPushButton("音声ファイル削除")
        save = QPushButton("oto.ini保存")
        open_folder.clicked.connect(self.pick_folder)
        play.clicked.connect(self.play_selected)
        delete.clicked.connect(self.delete_selected)
        save.clicked.connect(self.save)

        buttons = QHBoxLayout()
        for button in (open_folder, play, delete, save):
            buttons.addWidget(button)

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
            path = Path(url.toLocalFile())
            self.load_folder(path if path.is_dir() else path.parent)
            break

    def pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "WAVとoto.iniのフォルダを選択")
        if folder:
            self.load_folder(Path(folder))

    def load_folder(self, folder: Path) -> None:
        self.folder = folder
        self.entries = load_folder(folder)
        self.refresh_missing_flags()
        self.populate_table()
        self.status.setText(f"フォルダ: {folder} ({len(self.entries)}件)")

    def refresh_missing_flags(self) -> None:
        if self.folder is None:
            return
        for entry in self.entries:
            wav_path = self.folder / entry.wav_name
            entry.missing = not wav_path.exists() or is_unvoiced(wav_path) or not entry.alias.strip()

    def populate_table(self) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.entries))
        for row, entry in enumerate(self.entries):
            values = [
                entry.wav_name,
                entry.alias,
                f"{entry.offset:.3f}",
                f"{entry.consonant:.3f}",
                f"{entry.cutoff:.3f}",
                f"{entry.preutterance:.3f}",
                f"{entry.overlap:.3f}",
                "未発声/不足" if entry.missing else "OK",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col in (0, 7):
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if entry.missing:
                    item.setBackground(QColor("#ffcccc"))
                self.table.setItem(row, col, item)
        self.table.blockSignals(False)

    def _item_changed(self, item: QTableWidgetItem) -> None:
        entry = self.entries[item.row()]
        value = item.text().strip()
        if item.column() == 1:
            entry.alias = value
        elif item.column() in (2, 3, 4, 5, 6):
            try:
                number = float(value)
            except ValueError:
                self.populate_table()
                return
            attr = ["offset", "consonant", "cutoff", "preutterance", "overlap"][item.column() - 2]
            setattr(entry, attr, number)
        self.refresh_missing_flags()
        self.populate_table()

    def selected_entry(self) -> tuple[int, SingleOtoEntry] | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.entries):
            self.status.setText("行を選択してください")
            return None
        return row, self.entries[row]

    def play_selected(self) -> None:
        selected = self.selected_entry()
        if selected is None or self.folder is None:
            return
        _, entry = selected
        wav_path = self.folder / entry.wav_name
        if not wav_path.exists():
            self.status.setText(f"WAVが見つかりません: {entry.wav_name}")
            return
        self.player.setSource(QUrl.fromLocalFile(str(wav_path)))
        self.player.play()
        self.status.setText(f"再生中: {entry.wav_name}")

    def delete_selected(self) -> None:
        selected = self.selected_entry()
        if selected is None or self.folder is None:
            return
        row, entry = selected
        wav_path = self.folder / entry.wav_name
        answer = QMessageBox.question(self, "削除確認", f"{entry.wav_name} を削除しますか？")
        if answer != QMessageBox.Yes:
            return
        if wav_path.exists():
            wav_path.unlink()
        self.entries.pop(row)
        self.populate_table()
        self.status.setText(f"削除しました: {entry.wav_name}")

    def save(self) -> None:
        if self.folder is None:
            self.status.setText("フォルダを先に読み込んでください")
            return
        self.refresh_missing_flags()
        save_oto_ini(self.folder, self.entries)
        self.populate_table()
        self.status.setText("oto.iniを保存しました")


def run() -> None:
    app = QApplication([])
    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    app.exec()
