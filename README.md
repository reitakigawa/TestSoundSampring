# AutoOtoMaker

WhisperXで文字起こしした長文WAVから、連続音向けの`oto.ini`を半自動生成するデスクトップツールです。

## 機能

- WAVとWhisperX JSONのドラッグ&ドロップ読込
- WhisperX認識文の編集
- 読みだけの編集
- 自動ひらがな化とモーラ分割
- 発声されていない、または時刻情報が不足した音の赤表示
- モーラ時刻を元にした連続音エイリアスの`oto.ini`生成

## 起動

```bash
cd AutoOtoMaker
pip install -r requirements.txt
python main.py
```


## 別パッケージ

- `AutoOtoMaker/`: WhisperX長文WAVから連続音向け`oto.ini`を生成するツール。
- `SingleOtoEditor/`: 分割済みWAVフォルダから単独音向け`oto.ini`を編集するツール。
