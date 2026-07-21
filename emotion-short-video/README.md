# Emotion Short Video Skill

一个可通过 `npx skills add` 安装的 Agent Skill，用来策划中文情感类竖屏短视频。

## 能做什么

输入一个主题，生成：

- 40–60 秒中文口播文案
- 7–9 个电影感分镜
- Wan2.2 中英文视频提示词
- 中文配音稿
- SRT 字幕
- RunningHub 参数建议
- 完整项目目录

## 安装

将本目录上传到你的 GitHub 仓库后执行：

```bash
npx skills add 你的GitHub用户名/你的仓库名 --skill emotion-short-video
```

若仓库根目录就是本 Skill，也可以尝试：

```bash
npx skills add 你的GitHub用户名/你的仓库名
```

## 推荐用法

对智能体说：

> 使用 emotion-short-video，做一条主题为“80后，你快乐吗”的情感短视频。成年男性主角，城市夜景，温暖克制，男声，50秒。

## 本地生成项目骨架

```bash
python scripts/create_project.py --topic "80后，你快乐吗" --output ./output
```

该脚本负责建立规范文件，不会自动调用付费视频或配音 API。
