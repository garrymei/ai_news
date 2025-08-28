#!/bin/bash
# AI图片生成环境设置脚本

echo "🚀 设置AI图片生成环境..."

# 激活虚拟环境
source .venv/bin/activate

echo "📦 安装图片生成相关依赖..."

# 基础图片处理
pip install Pillow requests

# 可选：安装Stable Diffusion本地生成 (需要较大存储空间和计算资源)
read -p "是否安装本地Stable Diffusion? (需要3-5GB存储空间) [y/N]: " install_diffusion

if [[ $install_diffusion =~ ^[Yy]$ ]]; then
    echo "安装PyTorch和Diffusers..."
    pip install torch torchvision torchaudio
    pip install diffusers transformers accelerate
    echo "✅ 本地Stable Diffusion已安装"
else
    echo "⏭️ 跳过本地Stable Diffusion安装"
fi

# 创建配置文件
echo "📝 创建配置文件..."

cat > image_generation_config.py << 'EOF'
# 图片生成配置
import os

# API配置 (可选)
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")  # 从 https://platform.stability.ai/ 获取
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")       # 用于DALL-E

# 图片生成优先级 (按顺序尝试)
GENERATION_METHODS = [
    "stability_api",      # Stability AI API (最佳质量，需要API key)
    "local_diffusion",    # 本地Stable Diffusion (需要GPU)
    "enhanced_local",     # 增强本地生成 (始终可用)
]

# 图片设置
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920
IMAGE_QUALITY = 95

# 样式设置
DEFAULT_STYLE = "professional, modern, high-tech, clean design, technology background"
EOF

echo "✅ 配置文件已创建: image_generation_config.py"

# 测试环境
echo "🧪 测试图片生成环境..."
python3 -c "
from PIL import Image, ImageDraw, ImageFont
import requests
print('✅ PIL (Pillow) 可用')
print('✅ requests 可用')

try:
    import torch
    print('✅ PyTorch 可用')
except ImportError:
    print('⚠️ PyTorch 未安装 (本地Diffusion不可用)')

try:
    from diffusers import StableDiffusionPipeline
    print('✅ Diffusers 可用')
except ImportError:
    print('⚠️ Diffusers 未安装 (本地Diffusion不可用)')
"

echo ""
echo "🎉 设置完成！"
echo ""
echo "📋 使用说明:"
echo "1. 基础图片生成: python3 generate_images_advanced.py"
echo "2. 如需API生成，设置环境变量:"
echo "   export STABILITY_API_KEY='your_api_key'"
echo "3. 配置文件: image_generation_config.py"
echo ""
echo "🔗 获取API Key:"
echo "- Stability AI: https://platform.stability.ai/"
echo "- OpenAI DALL-E: https://platform.openai.com/"
