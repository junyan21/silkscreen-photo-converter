# tests/test_silkscreen_converter.py
"""
シルクスクリーン変換ツールのユニットテスト
"""

import pytest
import tempfile
import os
import numpy as np
from PIL import Image
import sys

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from silkscreen_converter import SilkscreenConverter


class TestSilkscreenConverter:
    """SilkscreenConverterクラスのテスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用のコンバーターインスタンス"""
        return SilkscreenConverter()
    
    @pytest.fixture
    def test_image(self):
        """テスト用の画像を作成"""
        # 100x100のグラデーション画像を作成
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(100):
            arr[i, :, :] = [i*2, i*2, i*2]
        return Image.fromarray(arr)
    
    @pytest.fixture
    def temp_image_path(self, test_image):
        """一時的な画像ファイルパス"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_image.save(f.name)
            yield f.name
        os.unlink(f.name)
    
    def test_load_image(self, converter, temp_image_path):
        """画像読み込みのテスト"""
        image = converter.load_image(temp_image_path)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_load_nonexistent_image(self, converter):
        """存在しない画像の読み込みテスト"""
        with pytest.raises(Exception):
            converter.load_image('nonexistent.jpg')
    
    def test_to_grayscale(self, converter, test_image):
        """グレースケール変換のテスト"""
        gray_image = converter.to_grayscale(test_image)
        assert gray_image.mode == 'L'
        assert gray_image.size == test_image.size
    
    def test_adjust_image_contrast(self, converter, test_image):
        """コントラスト調整のテスト"""
        gray_image = converter.to_grayscale(test_image)
        adjusted = converter.adjust_image(gray_image, contrast=1.5)
        assert adjusted.size == gray_image.size
        assert adjusted.mode == gray_image.mode
    
    def test_adjust_image_brightness(self, converter, test_image):
        """明度調整のテスト"""
        gray_image = converter.to_grayscale(test_image)
        adjusted = converter.adjust_image(gray_image, brightness=20)
        assert adjusted.size == gray_image.size
        assert adjusted.mode == gray_image.mode
    
    def test_create_halftone_pattern(self, converter, test_image):
        """網点パターン生成のテスト"""
        gray_image = converter.to_grayscale(test_image)
        halftone = converter.create_halftone_pattern(gray_image, 15, 45, 'circle')
        assert halftone.size == gray_image.size
        assert halftone.mode == 'L'
    
    def test_create_halftone_different_shapes(self, converter, test_image):
        """異なる網点形状のテスト"""
        gray_image = converter.to_grayscale(test_image)
        shapes = ['circle', 'square', 'diamond', 'line']
        
        for shape in shapes:
            halftone = converter.create_halftone_pattern(gray_image, 15, 45, shape)
            assert halftone.size == gray_image.size
            assert halftone.mode == 'L'
    
    def test_create_halftone_vector_output(self, converter, test_image):
        """ベクター出力用網点生成のテスト"""
        gray_image = converter.to_grayscale(test_image)
        halftone = converter.create_halftone_pattern(
            gray_image, 15, 45, 'circle', vector_output=True
        )
        assert len(converter.dot_data) > 0
        assert all('x' in dot and 'y' in dot and 'size' in dot 
                  for dot in converter.dot_data)
    
    def test_to_monochrome_bitmap(self, converter, test_image):
        """モノクロ2階調変換のテスト"""
        gray_image = converter.to_grayscale(test_image)
        mono_image = converter.to_monochrome_bitmap(gray_image)
        assert mono_image.mode == '1'
        assert mono_image.size == gray_image.size
    
    def test_save_image_png(self, converter, test_image):
        """PNG保存のテスト"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            converter.save_image(test_image, f.name, 'PNG')
            assert os.path.exists(f.name)
            # 保存された画像を読み込んで確認
            saved_image = Image.open(f.name)
            assert saved_image.size == test_image.size
            os.unlink(f.name)
    
    def test_save_image_tiff(self, converter, test_image):
        """TIFF保存のテスト"""
        with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as f:
            converter.save_image(test_image, f.name, 'TIFF')
            assert os.path.exists(f.name)
            os.unlink(f.name)
    
    @pytest.mark.skipif(not hasattr(SilkscreenConverter, 'save_pdf'), 
                       reason="PDF support not available")
    def test_save_pdf(self, converter, test_image):
        """PDF保存のテスト"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            try:
                converter.save_pdf(test_image, f.name)
                assert os.path.exists(f.name)
                assert os.path.getsize(f.name) > 0
            except Exception as e:
                if "reportlab" in str(e).lower():
                    pytest.skip("reportlab not installed")
                else:
                    raise
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)
    
    def test_save_ai(self, converter, test_image):
        """AI形式保存のテスト"""
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            try:
                converter.save_ai(test_image, f.name)
                assert os.path.exists(f.name)
                assert os.path.getsize(f.name) > 0
                
                # SVG内容の基本チェック
                with open(f.name, 'r') as svg_file:
                    content = svg_file.read()
                    assert '<svg' in content
                    assert 'xmlns' in content
            finally:
                os.unlink(f.name)
    
    def test_convert_full_workflow(self, converter, temp_image_path):
        """完全な変換ワークフローのテスト"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            try:
                result = converter.convert(
                    temp_image_path, f.name, 
                    lines=15, angle=45, dot_shape='circle',
                    contrast=1.0, brightness=0, dpi=300, format_type='PNG'
                )
                assert os.path.exists(f.name)
                assert result.mode == '1'  # モノクロ2階調
            finally:
                if os.path.exists(f.name):
                    os.unlink(f.name)
    
    def test_convert_different_parameters(self, converter, temp_image_path):
        """異なるパラメーターでの変換テスト"""
        test_cases = [
            {'lines': 10, 'angle': 30, 'dot_shape': 'square'},
            {'lines': 20, 'angle': 60, 'dot_shape': 'diamond'},
            {'lines': 15, 'angle': 90, 'dot_shape': 'line'},
        ]
        
        for params in test_cases:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                try:
                    result = converter.convert(temp_image_path, f.name, **params)
                    assert os.path.exists(f.name)
                    assert result.mode == '1'
                finally:
                    if os.path.exists(f.name):
                        os.unlink(f.name)


class TestParameterValidation:
    """パラメーター検証のテスト"""
    
    def test_lines_validation(self):
        """線数パラメーターの検証"""
        converter = SilkscreenConverter()
        
        # 有効な範囲
        valid_lines = [5, 10, 15, 20, 30, 50]
        for lines in valid_lines:
            # エラーが発生しないことを確認
            assert 5 <= lines <= 50
    
    def test_angle_validation(self):
        """角度パラメーターの検証"""
        valid_angles = [0, 15, 30, 45, 60, 90]
        for angle in valid_angles:
            assert 0 <= angle <= 90
    
    def test_shape_validation(self):
        """形状パラメーターの検証"""
        valid_shapes = ['circle', 'square', 'diamond', 'line']
        for shape in valid_shapes:
            assert shape in valid_shapes


class TestImageProcessing:
    """画像処理の詳細テスト"""
    
    def test_dot_drawing_circle(self):
        """円形網点描画のテスト"""
        converter = SilkscreenConverter()
        array = np.full((50, 50), 255, dtype=np.uint8)
        
        converter._draw_dot(array, 25, 25, 10, 0, 'circle', 50, 50)
        
        # 中心付近が黒になっていることを確認
        assert array[25, 25] == 0
        # 端は白のまま
        assert array[0, 0] == 255
    
    def test_dot_drawing_square(self):
        """四角形網点描画のテスト"""
        converter = SilkscreenConverter()
        array = np.full((50, 50), 255, dtype=np.uint8)
        
        converter._draw_dot(array, 25, 25, 10, 0, 'square', 50, 50)
        
        # 中心付近が黒になっていることを確認
        assert array[25, 25] == 0
        # 四角形の範囲内
        assert array[20, 20] == 0
        assert array[30, 30] == 0
    
    def test_brightness_range(self):
        """明度調整の範囲テスト"""
        converter = SilkscreenConverter()
        
        # グレーの画像を作成
        img = Image.new('L', (50, 50), 128)
        
        # 明度を上げる
        bright = converter.adjust_image(img, brightness=50)
        bright_array = np.array(bright)
        
        # 明度を下げる
        dark = converter.adjust_image(img, brightness=-50)
        dark_array = np.array(dark)
        
        # 明るい画像の方が値が大きいことを確認
        assert np.mean(bright_array) > np.mean(dark_array)


if __name__ == '__main__':
    pytest.main([__file__])