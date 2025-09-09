# Python Video Plugin

## 项目简介
该插件旨在根据用户输入的文案、视频类型、视频数量和开头视频地址，自动生成视频剪辑草稿。插件会对文案进行分镜处理，插入字幕和口播，并从本地视频素材库中检索合适的视频进行剪辑，确保最终输出的视频完全符合给定文案。

## 功能
- 文案分镜处理
- 字幕插入
- 口播生成
- 本地视频素材检索
- 视频剪辑与导出

## 使用方法
1. 克隆或下载该项目到本地。
2. 安装所需的依赖库：
   ```
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```
3. 在命令行中运行插件：
   ```
   python src/main.py --text "你的文案" --videoType "视频类型" --n 生成视频数量 --firstVideoUrl "开头视频地址"
   ```

## 项目结构
```
python-video-plugin
├── src
│   ├── main.py                   # 插件入口点
│   ├── utils
│   │   └── video_processing.py    # 视频处理实用函数
│   ├── services
│   │   ├── script_parser.py       # 文案分镜处理
│   │   ├── subtitle_inserter.py   # 字幕插入
│   │   ├── voiceover_generator.py  # 口播生成
│   │   └── video_searcher.py      # 视频素材检索
│   └── types
│       └── index.py               # 类型和常量定义
├── requirements.txt               # 项目依赖
└── README.md                      # 项目文档
```

## 贡献
欢迎任何形式的贡献！请提交问题或拉取请求。

## 许可证
该项目遵循MIT许可证。