# SingleOtoEditor

一音ずつに分割済みのWAVフォルダと`oto.ini`を読み込み、単独音用の`oto.ini`を編集するデスクトップツールです。

## 機能

- フォルダのドラッグ&ドロップ読込
- フォルダ内WAVと既存`oto.ini`のマージ読込
- 無音に近いWAV、存在しないWAV、空エイリアスの赤表示
- `oto.ini`値とエイリアスのその場編集
- 選択WAVのその場再生
- 左端の行番号ダブルクリックによるWAV再生
- 選択WAVファイルの削除
- `oto.ini`保存

## 起動

```bash
cd SingleOtoEditor
pip install -r requirements.txt
python main.py
```
