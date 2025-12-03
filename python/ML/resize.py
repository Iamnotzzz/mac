import os
from PIL import Image
from tqdm import tqdm
import shutil

# 把 ~ 替换成你的真实用户名路径
INPUT_DIR = "/Users/zhaozhenzhan/code/python/ML/final_icon_dataset"

OUTPUT_DIR = "/Users/zhaozhenzhan/code/python/ML/icons_128"

TARGET_SIZE = (128, 128)

def resize_and_copy():
    # 1. 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ 已创建输出目录: {OUTPUT_DIR}")
    
    # 获取所有文件
    files = os.listdir(INPUT_DIR)
    
    # 过滤出图片和文本
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    text_files = [f for f in files if f.lower().endswith('.txt')]
    
    print(f"📊 统计: 找到 {len(image_files)} 张图片, {len(text_files)} 个文本文件")
    print(f"🚀 开始处理，目标尺寸: {TARGET_SIZE}...")

    # 2. 处理图片
    for img_name in tqdm(image_files, desc="Resizing Images"):
        try:
            src_path = os.path.join(INPUT_DIR, img_name)
            dst_path = os.path.join(OUTPUT_DIR, img_name)
            
            with Image.open(src_path) as img:
                # 强制转换为 RGB (去除可能存在的 Alpha 通道，防止模型报错)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 高质量缩放
                img_resized = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # 保存
                img_resized.save(dst_path)
                
        except Exception as e:
            print(f"❌ 处理图片 {img_name} 失败: {e}")

    # 3. 复制对应的文本文件
    # 这一步很重要，因为你的 DataLoader 期望图片和文本在一起
    print("📦 正在复制对应的 Caption 文本文件...")
    for txt_name in text_files:
        src_txt = os.path.join(INPUT_DIR, txt_name)
        dst_txt = os.path.join(OUTPUT_DIR, txt_name)
        shutil.copy2(src_txt, dst_txt)

    print("\n✅ 🎉 全部完成！")
    print(f"📂 新数据集位于: {OUTPUT_DIR}")

if __name__ == "__main__":
    resize_and_copy()