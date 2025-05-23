# 📸 Silkscreen Photo Converter

[![Tests](https://github.com/yourusername/silkscreen-photo-converter/workflows/Tests/badge.svg)](https://github.com/yourusername/silkscreen-photo-converter/actions)
[![codecov](https://codecov.io/gh/yourusername/silkscreen-photo-converter/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/silkscreen-photo-converter)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**シルクスクリーン写真変換ツール**

写真を自動的にシルクスクリーン印刷用のモノクロ2階調データに変換するコマンドラインツールです。Photoshopでの手動作業を完全自動化し、**K-100%の純粋な黒**のみで構成された高品質な印刷データを生成します。

## ✨ 特徴

- 🎯 **品質**: K-100%の純粋な黒のみで出力（グレー不使用）
- 🔄 **自動化**: Photoshopでの手動作業を自動化
- 📐 **ベクター対応**: AI・PDF形式でベクターデータ出力
- ⚙️ **カスタマイズ可能**: 線数・角度・網点形状を詳細設定
- 🚀 **一括処理**: フォルダ内の画像を一括変換
- 🎨 **多形式対応**: PNG・TIFF・PDF・AI形式での出力
  
## 🚀 クイックスタート

### 方法1: GitHubからダウンロード

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/silkscreen-photo-converter.git
cd silkscreen-photo-converter

# 依存関係をインストール
pip install -r requirements.txt

# 基本変換を実行
python silkscreen_converter.py sample.jpg -o output.png
```

### 方法2: ファイル個別ダウンロード

```bash
# メインスクリプトをダウンロード
wget https://raw.githubusercontent.com/yourusername/silkscreen-photo-converter/main/silkscreen_converter.py

# 依存関係をインストール
pip install Pillow numpy click reportlab

# 実行
python silkscreen_converter.py photo.jpg -o result.ai --format AI
```

## 🛠️ インストール

### 前提条件
- Python 3.7+
- pip

### 依存ライブラリ

**本番用**:
```bash
pip install Pillow numpy click reportlab
```

**開発用**（テスト・リンティング含む）:
```bash
pip install -r requirements-dev.txt
```

### 対応プラットフォーム
- ✅ **Windows** (Windows 10/11)
- ✅ **macOS** (macOS 10.15+)
- ✅ **Linux** (Ubuntu 18.04+)

## 📖 使い方

### 基本的な使用方法

```bash
# 基本変換（推奨設定）
python silkscreen_converter.py photo.jpg -o output.png

# AI形式で出力（Illustratorで編集可能）
python silkscreen_converter.py photo.jpg -o design.ai --format AI

# PDF形式で出力（製版用）
python silkscreen_converter.py photo.jpg -o print.pdf --format PDF
```

### 詳細設定での変換

```bash
# Tシャツくん用設定（10-15線推奨）
python silkscreen_converter.py photo.jpg --lines 15 --angle 45 --shape circle

# 高精細製版用設定
python silkscreen_converter.py photo.jpg --lines 20 --dpi 600 --format TIFF

# コントラスト・明度調整
python silkscreen_converter.py photo.jpg --contrast 1.5 --brightness 10
```

### 一括変換（バッチ処理）

```bash
# フォルダ内の全画像を一括変換
python silkscreen_converter.py images/ --batch --lines 15

# AI形式で一括変換
python silkscreen_converter.py photos/ --batch --format AI --lines 15
```

## ⚙️ オプション一覧

| オプション | 説明 | デフォルト値 | 範囲 |
|-----------|------|-------------|------|
| `-o, --output` | 出力ファイルパス | 自動生成 | - |
| `--lines` | 線数（網点の密度） | 15 | 5-50 |
| `--angle` | 網点角度 | 45 | 0-90 |
| `--shape` | 網点形状 | circle | circle/square/diamond/line |
| `--contrast` | コントラスト調整 | 1.0 | 0.1-3.0 |
| `--brightness` | 明度調整 | 0 | -50 to 50 |
| `--dpi` | 出力解像度 | 300 | 72-1200 |
| `--format` | 出力形式 | PNG | PNG/TIFF/PDF/AI |
| `--batch` | 一括変換モード | - | フラグ |

## 📄 出力形式の比較

| 形式 | 特徴 | 用途 | ベクター | 編集可能 |
|------|------|------|---------|---------|
| **PNG** | 高画質ラスター | プレビュー・Web用 | ❌ | ❌ |
| **TIFF** | 印刷用ラスター | 高品質印刷 | ❌ | ❌ |
| **PDF** | ベクター・印刷最適 | 製版サービス入稿 | ✅ | ⚠️ |
| **AI** | ベクター・編集可能 | Illustratorで編集 | ✅ | ✅ |

## 🎯 線数設定ガイド

シルクスクリーン製版の難易度に応じて線数を選択してください：

- **10線**: 荒い網点、製版簡単、レトロな仕上がり
- **15線**: **推奨設定**、バランスの良い品質
- **20線**: 細かい網点、高品質だが製版やや困難
- **30線**: 非常に細かい、デジタル製版推奨

> **💡 Tシャツくんでの製版なら10-15線がおすすめです**

## 📁 プロジェクト構成

```
silkscreen-photo-converter/
├── .github/
│   └── workflows/
│       └── test.yml                    # GitHub Actions自動テスト
├── tests/
│   ├── __init__.py
│   └── test_silkscreen_converter.py    # ユニットテスト
├── silkscreen_converter.py             # メインスクリプト
├── requirements.txt                    # 本番用依存関係
├── requirements-dev.txt                # 開発用依存関係
├── pytest.ini                         # pytest設定
├── README.md                          # このファイル
└── LICENSE                            # MITライセンス
```

## 📝 使用例

### 基本的なワークフロー

```bash
# 1. 写真を準備
ls photos/
# sample1.jpg  sample2.png  sample3.webp

# 2. テスト変換（1枚）
python silkscreen_converter.py photos/sample1.jpg --lines 15

# 3. 設定を調整
python silkscreen_converter.py photos/sample1.jpg --lines 15 --contrast 1.2

# 4. 一括変換
python silkscreen_converter.py photos/ --batch --lines 15 --format AI
```

### 製版サービス入稿用

```bash
# 高解像度PDF（製版サービス用）
python silkscreen_converter.py design.jpg \
  --format PDF \
  --dpi 600 \
  --lines 20 \
  --contrast 1.1 \
  -o final_design.pdf
```

### Illustratorでの編集用

```bash
# AI形式で出力（後で編集可能）
python silkscreen_converter.py photo.jpg \
  --format AI \
  --lines 15 \
  --shape circle \
  -o editable_design.ai

# → Adobe Illustratorで開いて網点を個別編集可能
```

## 🧪 テスト実行

### 自動テスト（GitHub Actions）

プッシュ・プルリクエスト時に自動実行：
- ✅ **マルチプラットフォーム**: Ubuntu, Windows, macOS
- ✅ **マルチPythonバージョン**: 3.7-3.11
- ✅ **コードカバレッジ**: 80%以上
- ✅ **コード品質**: Black, flake8, mypy
- ✅ **セキュリティ**: bandit, safety

### ローカルテスト

```bash
# 開発用依存関係をインストール
pip install -r requirements-dev.txt

# 全テストを実行
pytest

# カバレッジ付きでテスト実行
pytest --cov=silkscreen_converter

# コードフォーマットチェック
black --check silkscreen_converter.py

# リンティング
flake8 silkscreen_converter.py

# セキュリティチェック
bandit silkscreen_converter.py
```

## 🔬 技術仕様

### 変換処理フロー

1. **画像読み込み**: RGB形式に正規化
2. **グレースケール変換**: 標準的な輝度計算（0.299×R + 0.587×G + 0.114×B）
3. **明度・コントラスト調整**: ユーザー設定に基づく最適化
4. **網点処理**: 指定した線数・角度・形状で網点生成
5. **モノクロ2階調変換**: K-100%の純粋な黒のみに変換
6. **出力**: 指定形式での保存（ベクター対応）

### カラー仕様

- **入力**: RGB形式
- **処理**: グレースケール
- **出力**: **K-100%の純粋な黒のみ**（CMYK準拠）
- **グレー使用**: なし（製版品質保証）

### 品質保証

- **自動テスト**: 15の環境組み合わせでテスト
- **コードカバレッジ**: 80%以上
- **セキュリティチェック**: 既知脆弱性の定期チェック
- **コード品質**: PEP8準拠、型ヒント対応

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### インストールエラー
```bash
# Pillowのインストールでエラーが出る場合
pip install --upgrade pip
pip install Pillow

# M1 Macでの問題
arch -arm64 pip install Pillow numpy
```

#### PDF出力エラー
```bash
# reportlabが見つからない場合
pip install reportlab

# 権限エラーの場合
pip install --user reportlab
```

#### 変換結果が想定と違う場合
```bash
# コントラストを調整
python silkscreen_converter.py photo.jpg --contrast 1.5

# 線数を変更
python silkscreen_converter.py photo.jpg --lines 10

# 明度を調整
python silkscreen_converter.py photo.jpg --brightness 10
```

#### テスト失敗時
```bash
# 特定のテストのみ実行
pytest tests/test_silkscreen_converter.py::TestSilkscreenConverter::test_load_image -v

# 詳細なエラー情報
pytest --tb=long

# テストを一つずつ実行
pytest -x
```

## 📚 関連リソース

- [シルクスクリーンで写真を刷ろう！](https://www.hando-horizon.com/labo/12115/) - 参考にした技術情報
- [Adobe Illustrator](https://www.adobe.com/products/illustrator.html) - AI形式ファイルの編集
- [Inkscape](https://inkscape.org/) - 無料のベクター編集ソフト
- [pytest](https://pytest.org/) - テストフレームワーク
- [GitHub Actions](https://github.com/features/actions) - CI/CD
