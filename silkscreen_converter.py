#!/usr/bin/env python3
"""
シルクスクリーン写真変換ツール
コマンドライン版（AI・PDF対応）

使用方法:
python silkscreen_converter.py input.jpg -o output.ai --lines 15 --angle 45

必要なライブラリ:
pip install Pillow numpy click reportlab svglib

AI形式の出力にはIllustratorまたは互換ソフトが必要です。
"""

import math
import os
import tempfile
from io import BytesIO

import click
import numpy as np
from PIL import Image, ImageEnhance

# PDF/AI生成用ライブラリ
try:
    from reportlab.pdfgen import canvas

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# SVG生成用（AI形式のベース）
try:
    import defusedxml
    defusedxml.defuse_stdlib()
    import xml.etree.ElementTree as ET

    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False


class SilkscreenConverter:
    """シルクスクリーン用データ変換クラス"""

    def __init__(self):
        self.supported_formats = [
            ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"
        ]
        self.dot_data = []  # ベクターデータ用の網点情報

    def load_image(self, input_path):
        """画像を読み込み、RGBモードに変換"""
        try:
            image = Image.open(input_path)
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise click.ClickException(f"画像の読み込みに失敗しました: {e}")

    def to_grayscale(self, image):
        """RGBからグレースケールに変換"""
        return image.convert("L")

    def adjust_image(self, image, contrast=1.0, brightness=0):
        """コントラストと明度を調整"""
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)

        if brightness != 0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + brightness / 100.0)

        return image

    def create_halftone_pattern(
        self, image, lines, angle, dot_shape="circle", vector_output=False
    ):
        """網点パターンを生成（ベクター出力対応）"""
        width, height = image.size
        dot_spacing = max(2, int(72 / lines))
        angle_rad = math.radians(angle)

        # ベクター出力用のデータをクリア
        if vector_output:
            self.dot_data = []

        # ラスター出力用
        result = Image.new("L", (width, height), 255)
        result_array = np.array(result)
        img_array = np.array(image)

        for y in range(0, height, dot_spacing):
            for x in range(0, width, dot_spacing):
                y_end = min(y + dot_spacing, height)
                x_end = min(x + dot_spacing, width)

                region = img_array[y:y_end, x:x_end]
                avg_brightness = np.mean(region)
                darkness = 1.0 - (avg_brightness / 255.0)
                dot_size = int(dot_spacing * darkness)

                if dot_size > 0:
                    center_x = x + dot_spacing // 2
                    center_y = y + dot_spacing // 2

                    # ベクター出力用データを保存
                    if vector_output:
                        self.dot_data.append(
                            {
                                "x": center_x,
                                "y": center_y,
                                "size": dot_size,
                                "shape": dot_shape,
                                "angle": angle_rad,
                            }
                        )

                    # ラスター出力用描画
                    self._draw_dot(
                        result_array,
                        center_x,
                        center_y,
                        dot_size,
                        angle_rad,
                        dot_shape,
                        width,
                        height,
                    )

        return Image.fromarray(result_array)

    def _draw_dot(
        self, array, center_x, center_y, size, angle, shape, width, height
    ):
        """指定した形状の網点を描画"""
        radius = size // 2

        y_start = max(0, center_y - radius)
        y_end = min(height, center_y + radius + 1)
        x_start = max(0, center_x - radius)
        x_end = min(width, center_x + radius + 1)

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                dx = x - center_x
                dy = y - center_y

                rotated_x = dx * math.cos(angle) - dy * math.sin(angle)
                rotated_y = dx * math.sin(angle) + dy * math.cos(angle)

                draw_pixel = False

                if shape == "circle":
                    distance = math.sqrt(rotated_x**2 + rotated_y**2)
                    draw_pixel = distance <= radius
                elif shape == "square":
                    draw_pixel = (
                        abs(rotated_x) <= radius and abs(rotated_y) <= radius
                    )
                elif shape == "diamond":
                    draw_pixel = abs(rotated_x) + abs(rotated_y) <= radius
                elif shape == "line":
                    draw_pixel = (
                        abs(rotated_y) <= radius * 0.3
                        and abs(rotated_x) <= radius
                    )

                if draw_pixel:
                    array[y, x] = 0

    def to_monochrome_bitmap(self, image, threshold=128):
        """グレースケール画像をモノクロ2階調に変換"""

        def binarize(pixel):
            return 0 if pixel < threshold else 255

        return image.point(binarize, mode="1")

    def save_image(self, image, output_path, format_type="PNG", dpi=300):
        """画像を指定形式で保存"""
        try:
            if format_type.upper() in ["PNG", "TIFF", "JPG", "JPEG"]:
                image.save(output_path, format=format_type, dpi=(dpi, dpi))
            else:
                image.save(output_path)

            click.echo(f"✅ 変換完了: {output_path}")
            click.echo(f"   形式: {format_type}, 解像度: {dpi} DPI")

        except Exception as e:
            raise click.ClickException(f"画像の保存に失敗しました: {e}")

    def save_pdf(self, image, output_path, dpi=300):
        """PDF形式で保存（ベクターデータ対応）"""
        if not PDF_AVAILABLE:
            raise click.ClickException(
                "PDF出力にはreportlabが必要です: pip install reportlab"
            )

        try:
            width, height = image.size

            # PDF用のサイズ計算（ポイント単位）
            pdf_width = (width * 72) / dpi
            pdf_height = (height * 72) / dpi

            # PDFキャンバス作成
            c = canvas.Canvas(output_path, pagesize=(pdf_width, pdf_height))

            if self.dot_data:
                # ベクターデータがある場合は網点を描画
                c.setFillColor("black")
                c.setStrokeColor("black")

                scale_x = pdf_width / width
                scale_y = pdf_height / height

                for dot in self.dot_data:
                    x = dot["x"] * scale_x
                    y = pdf_height - (dot["y"] * scale_y)  # PDFは下原点
                    size = dot["size"] * min(scale_x, scale_y)

                    if dot["shape"] == "circle":
                        c.circle(x, y, size / 2, fill=1)
                    elif dot["shape"] == "square":
                        c.rect(x - size / 2, y - size / 2, size, size, fill=1)
                    elif dot["shape"] == "diamond":
                        # ダイヤモンド形状
                        points = [
                            (x, y + size / 2),  # 上
                            (x + size / 2, y),  # 右
                            (x, y - size / 2),  # 下
                            (x - size / 2, y),  # 左
                        ]
                        path = c.beginPath()
                        path.moveTo(*points[0])
                        for point in points[1:]:
                            path.lineTo(*point)
                        path.close()
                        c.drawPath(path, fill=1)
                    elif dot["shape"] == "line":
                        # ライン形状
                        c.rect(
                            x - size / 2, y - size * 0.15,
                            size, size * 0.3, fill=1
                        )
            else:
                # ラスター画像をPDFに埋め込み
                with tempfile.NamedTemporaryFile(
                    suffix=".png", delete=False
                ) as temp_file:
                    temp_path = temp_file.name
                    image.save(temp_path, "PNG", dpi=(dpi, dpi))
                    c.drawImage(temp_path, 0, 0, pdf_width, pdf_height)
                os.unlink(temp_path)

            c.save()
            click.echo(f"✅ PDF保存完了: {output_path}")

        except Exception as e:
            raise click.ClickException(f"PDF保存に失敗しました: {e}")

    def save_ai(self, image, output_path, dpi=300):
        """AI形式で保存（SVGベース）"""
        if not SVG_AVAILABLE:
            raise click.ClickException("AI出力にはxml.etree.ElementTreeが必要です")

        try:
            width, height = image.size

            # SVG作成（AI互換形式）
            svg = ET.Element("svg")
            svg.set("version", "1.1")
            svg.set("xmlns", "http://www.w3.org/2000/svg")
            svg.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
            svg.set("width", f"{width}px")
            svg.set("height", f"{height}px")
            svg.set("viewBox", f"0 0 {width} {height}")

            # Adobe Illustrator識別用コメント
            comment = ET.Comment(" Generator: Silkscreen Converter ")
            svg.append(comment)

            # デフス（定義）セクション
            ET.SubElement(svg, "defs")

            if self.dot_data:
                # ベクターデータから網点を生成
                group = ET.SubElement(svg, "g")
                group.set("fill", "#000000")  # K-100%
                group.set("stroke", "none")

                for dot in self.dot_data:
                    x, y, size = dot["x"], dot["y"], dot["size"]
                    shape = dot["shape"]

                    if shape == "circle":
                        circle = ET.SubElement(group, "circle")
                        circle.set("cx", str(x))
                        circle.set("cy", str(y))
                        circle.set("r", str(size / 2))

                    elif shape == "square":
                        rect = ET.SubElement(group, "rect")
                        rect.set("x", str(x - size / 2))
                        rect.set("y", str(y - size / 2))
                        rect.set("width", str(size))
                        rect.set("height", str(size))

                    elif shape == "diamond":
                        polygon = ET.SubElement(group, "polygon")
                        points = [
                            f"{x},{y-size/2}",  # 上
                            f"{x+size/2},{y}",  # 右
                            f"{x},{y+size/2}",  # 下
                            f"{x-size/2},{y}",  # 左
                        ]
                        polygon.set("points", " ".join(points))

                    elif shape == "line":
                        rect = ET.SubElement(group, "rect")
                        rect.set("x", str(x - size / 2))
                        rect.set("y", str(y - size * 0.15))
                        rect.set("width", str(size))
                        rect.set("height", str(size * 0.3))

            else:
                # ラスター画像を埋め込み
                import base64

                temp_buffer = BytesIO()
                image.save(temp_buffer, format="PNG")
                img_data = base64.b64encode(temp_buffer.getvalue()).decode()

                img_element = ET.SubElement(svg, "image")
                img_element.set("x", "0")
                img_element.set("y", "0")
                img_element.set("width", str(width))
                img_element.set("height", str(height))
                base64_data = f"data:image/png;base64,{img_data}"
                img_element.set("xlink:href", base64_data)

            # AI形式のヘッダー情報を追加
            ai_header = ET.Comment(
                """
            Adobe Illustrator Compatible SVG
            This file can be opened in Adobe Illustrator
            """
            )
            svg.insert(0, ai_header)

            # XML書き出し
            tree = ET.ElementTree(svg)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)

            click.echo(f"✅ AI形式保存完了: {output_path}")
            click.echo("   ※ Adobe IllustratorまたはInkscapeで開けます")

        except Exception as e:
            raise click.ClickException(f"AI保存に失敗しました: {e}")

    def convert(
        self,
        input_path,
        output_path,
        lines=15,
        angle=45,
        dot_shape="circle",
        contrast=1.0,
        brightness=0,
        dpi=300,
        format_type="PNG",
        body_color="white",
    ):
        """メイン変換処理"""

        click.echo(f"🔄 変換開始: {input_path}")
        click.echo(f"   設定 - 線数: {lines}, 角度: {angle}°, 形状: {dot_shape}, ボディ色: {body_color}")

        # ベクター出力が必要かどうかを判定
        vector_output = format_type.upper() in ["AI", "PDF"]

        # 1. 画像読み込み
        image = self.load_image(input_path)
        click.echo(f"📷 画像読み込み完了: {image.size[0]}x{image.size[1]}")

        # 2. グレースケール変換
        gray_image = self.to_grayscale(image)
        click.echo("🔄 グレースケール変換完了")

        # 3. 明度・コントラスト調整
        if contrast != 1.0 or brightness != 0:
            gray_image = self.adjust_image(gray_image, contrast, brightness)
            click.echo("🔄 明度・コントラスト調整完了")

        # 3.5. ボディ色に応じた画像処理
        if body_color.lower() == "black":
            # 黒ボディの場合は画像を反転（明るい部分が印刷される）
            gray_image = gray_image.point(lambda x: 255 - x)
            click.echo("🔄 黒ボディ用画像反転完了")

        # 4. 網点処理（ベクター対応）
        halftone_image = self.create_halftone_pattern(
            gray_image, lines, angle, dot_shape, vector_output
        )
        click.echo("🔄 網点処理完了")

        # 5. モノクロ2階調変換
        final_image = self.to_monochrome_bitmap(halftone_image)
        click.echo("🔄 モノクロ2階調変換完了")

        # 6. 形式別保存
        if format_type.upper() == "PDF":
            self.save_pdf(final_image, output_path, dpi)
        elif format_type.upper() == "AI":
            self.save_ai(final_image, output_path, dpi)
        else:
            self.save_image(final_image, output_path, format_type, dpi)

        return final_image


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "-o", "--output", "output_path", help="出力ファイルパス（省略時は自動生成）"
)
@click.option("--lines", default=15, type=int, help="線数 (10-30, デフォルト: 15)")
@click.option("--angle", default=45, type=int, help="網点角度 (0-90, デフォルト: 45)")
@click.option(
    "--shape",
    "dot_shape",
    type=click.Choice(["circle", "square", "diamond", "line"]),
    default="circle",
    help="網点形状 (デフォルト: circle)",
)
@click.option(
    "--contrast",
    default=1.0,
    type=float,
    help="コントラスト調整 (0.5-2.0, デフォルト: 1.0)",
)
@click.option(
    "--brightness", default=0, type=int, help="明度調整 (-50 to 50, デフォルト: 0)"
)
@click.option("--dpi", default=300, type=int, help="出力解像度 (デフォルト: 300)")
@click.option(
    "--format",
    "format_type",
    type=click.Choice(["PNG", "TIFF", "PDF", "AI"]),
    default="PNG",
    help="出力形式 (デフォルト: PNG)",
)
@click.option("--batch", is_flag=True, help="フォルダ内の全画像を一括変換")
@click.option(
    "--body-color",
    "body_color",
    type=click.Choice(["white", "black"]),
    default="white",
    help="Tシャツボディ色 (white: 白ボディ, black: 黒ボディ, デフォルト: white)",
)
def main(
    input_path,
    output_path,
    lines,
    angle,
    dot_shape,
    contrast,
    brightness,
    dpi,
    format_type,
    batch,
    body_color,
):
    """
    シルクスクリーン用写真変換ツール（AI・PDF対応版）

    写真をシルクスクリーン印刷用のモノクロ2階調データに変換します。
    出力はK-100%の純粋な黒のみで構成されます。

    対応形式:
      - PNG/TIFF: 高品質ラスター画像
      - PDF: ベクターデータ（拡大縮小可能）
      - AI: Adobe Illustrator互換SVG形式

    ボディ色対応:
      - white: 白いTシャツ用（暗い部分が印刷される）
      - black: 黒いTシャツ用（明るい部分が印刷される）

    例:
      python silkscreen_converter.py photo.jpg -o output.ai --format AI --body-color white
      python silkscreen_converter.py photo.jpg -o output.pdf --format PDF --body-color black
      python silkscreen_converter.py images/ --batch --format AI --lines 15 --body-color white
    """

    # 必要なライブラリチェック
    if format_type.upper() == "PDF" and not PDF_AVAILABLE:
        raise click.ClickException(
            "PDF出力には追加ライブラリが必要です:\n" "pip install reportlab"
        )

    converter = SilkscreenConverter()

    # バッチ処理
    if batch:
        if not os.path.isdir(input_path):
            raise click.ClickException("バッチ処理にはフォルダパスを指定してください")

        image_files = []
        for file in os.listdir(input_path):
            if any(file.lower().endswith(ext)
                   for ext in converter.supported_formats):
                image_files.append(file)

        if not image_files:
            raise click.ClickException("対応する画像ファイルが見つかりません")

        click.echo(f"📁 バッチ処理開始: {len(image_files)}ファイル")

        for file in image_files:
            input_file = os.path.join(input_path, file)
            name, _ = os.path.splitext(file)

            # 拡張子を形式に合わせて設定
            if format_type.upper() == "AI":
                ext = "svg"  # AI互換SVG
            else:
                ext = format_type.lower()

            output_file = os.path.join(input_path, f"{name}_silkscreen_{body_color}.{ext}")

            try:
                converter.convert(
                    input_file,
                    output_file,
                    lines,
                    angle,
                    dot_shape,
                    contrast,
                    brightness,
                    dpi,
                    format_type,
                    body_color,
                )
            except Exception as e:
                click.echo(f"❌ エラー ({file}): {e}")

        click.echo("✅ バッチ処理完了")
        return

    # 単一ファイル処理
    if not output_path:
        name, _ = os.path.splitext(input_path)
        if format_type.upper() == "AI":
            ext = "svg"
        else:
            ext = format_type.lower()
        output_path = f"{name}_silkscreen_{body_color}.{ext}"

    # バリデーション
    if lines < 5 or lines > 50:
        raise click.ClickException("線数は5-50の範囲で指定してください")

    if angle < 0 or angle > 90:
        raise click.ClickException("角度は0-90の範囲で指定してください")

    if contrast < 0.1 or contrast > 3.0:
        raise click.ClickException("コントラストは0.1-3.0の範囲で指定してください")

    # 変換実行
    try:
        converter.convert(
            input_path,
            output_path,
            lines,
            angle,
            dot_shape,
            contrast,
            brightness,
            dpi,
            format_type,
            body_color,
        )

        # 形式別の追加情報
        if format_type.upper() == "AI":
            click.echo("\n💡 使用方法:")
            click.echo("   - Adobe Illustratorで開く: ファイル → 開く")
            click.echo("   - Inkscapeで編集可能")
            click.echo("   - ベクターデータなので拡大縮小自由")
        elif format_type.upper() == "PDF":
            click.echo("\n💡 使用方法:")
            click.echo("   - 印刷用高品質データ")
            click.echo("   - ベクターベースで拡大縮小可能")
            click.echo("   - 製版サービスに直接入稿可能")

    except Exception as e:
        raise click.ClickException(f"変換に失敗しました: {e}")


if __name__ == "__main__":
    main()
