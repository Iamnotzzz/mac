import os
import io
from pathlib import Path
from PIL import Image
import cairosvg
import re

# ================= 配置区域 =================

# 1. 定义源文件夹及其对应的风格标签
# 键(Key)是文件夹名称，值(Value)是该库的特定风格描述
SOURCE_MAP = {
    "lucide_icons": "lucide style",
    "tailwidens_icons": "heroicons style" # 这里使用了你仓库中的实际文件夹名
}

# 2. 输出路径：处理好的图片和标签将保存在这里
OUTPUT_DIR = "./final_icon_dataset"

# 3. 图像设置
IMG_SIZE = 1024   # SDXL 推荐 1024
ICON_SCALE = 0.8  # 图标在画面中的比例 (0.8 表示留出 20% 的边距)
BG_COLOR = (255, 255, 255, 255) # 纯白背景

# 4. 通用提示词 (Trigger Words)
# 这些词会加在每个图标的描述后面，保证风格统一
COMMON_TAGS = "web icon, line art, minimalist, vector, monochrome, white background, high quality"

# ===========================================

def clean_filename(filename):
    """将文件名转换为可读的英文描述"""
    # 去掉 .svg 后缀
    name = filename.stem
    # 将横杠、下划线替换为空格
    name = name.replace("-", " ").replace("_", " ")
    # 去掉数字后缀 (如 icon-2)
    name = re.sub(r'\s\d+$', '', name)
    return name

def process_svg(svg_path, output_dir, style_tag, global_counter):
    try:
        # 1. 读取 SVG 内容
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # 2. SVG -> PNG 转换 (先转为较大的尺寸以抗锯齿)
        png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), 
                                    output_height=IMG_SIZE, 
                                    output_width=IMG_SIZE)
        
        # 3. 图像处理 (居中 + 白底)
        icon_img = Image.open(io.BytesIO(png_data)).convert("RGBA")
        
        # 创建白底画布
        final_img = Image.new("RGBA", (IMG_SIZE, IMG_SIZE), BG_COLOR)
        
        # 缩放图标以留白
        target_size = int(IMG_SIZE * ICON_SCALE)
        icon_img = icon_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # 计算居中坐标
        offset = (IMG_SIZE - target_size) // 2
        
        # 粘贴 (使用 Alpha 通道作为遮罩，确保透明背景变白)
        final_img.paste(icon_img, (offset, offset), icon_img)
        final_img = final_img.convert("RGB") # 转为 RGB 去掉 Alpha 通道

        # 4. 生成保存文件名 (统一编号，避免重名)
        file_id = f"icon_{global_counter:05d}"
        img_save_path = output_dir / f"{file_id}.png"
        txt_save_path = output_dir / f"{file_id}.txt"

        # 5. 生成 Caption 内容
        # 格式: icon of [物体名], [库风格], [通用词]
        object_name = clean_filename(svg_path)
        caption = f"icon of {object_name}, {style_tag}, {COMMON_TAGS}"

        # 6. 保存文件
        final_img.save(img_save_path, quality=100)
        with open(txt_save_path, "w", encoding="utf-8") as f:
            f.write(caption)

        return True

    except Exception as e:
        print(f"❌ 处理失败: {svg_path.name} - {e}")
        return False

def main():
    base_path = Path(".") # 当前脚本所在目录
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🚀 开始处理数据...")
    print(f"📂 输出目录: {output_path.resolve()}\n")

    global_counter = 1
    success_count = 0

    for folder_name, style_tag in SOURCE_MAP.items():
        folder_path = base_path / folder_name
        
        if not folder_path.exists():
            print(f"⚠️ 警告: 找不到文件夹 {folder_name}，跳过。")
            continue

        # 查找该文件夹下所有的 .svg 文件
        svg_files = list(folder_path.glob("*.svg"))
        print(f"🔍 在 {folder_name} 中发现 {len(svg_files)} 个图标")

        for svg_file in svg_files:
            if process_svg(svg_file, output_path, style_tag, global_counter):
                success_count += 1
                global_counter += 1
                
                # 每处理 50 张显示一次进度
                if success_count % 50 == 0:
                    print(f"   已处理 {success_count} 张图片...")

    print("\n" + "="*30)
    print(f"✅ 处理完成！")
    print(f"📊 总共生成: {success_count} 组训练数据 (图片+标签)")
    print(f"💾 保存位置: {output_path.resolve()}")
    print("="*30)

if __name__ == "__main__":
    main()