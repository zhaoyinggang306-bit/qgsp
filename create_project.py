#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from datetime import datetime

DEFAULT_NEGATIVE = (
    "low quality, blurry face, deformed hands, extra fingers, duplicate person, "
    "childlike face, plastic skin, wax figure, exaggerated expression, "
    "strong lip movement, flicker, jitter, warped background, text, watermark, logo"
)

def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text.strip())
    return text.strip("-")[:50] or "emotion-video"

def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def load_input(args: argparse.Namespace) -> dict:
    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = {}
    if args.topic:
        data["topic"] = args.topic
    if not data.get("topic"):
        raise SystemExit("必须通过 --topic 或 --input 提供 topic")
    return data

def main() -> None:
    parser = argparse.ArgumentParser(description="创建情感短视频项目骨架")
    parser.add_argument("--topic", help="短视频主题")
    parser.add_argument("--input", help="JSON 输入文件")
    parser.add_argument("--output", default="./output", help="输出目录")
    args = parser.parse_args()

    data = load_input(args)
    topic = data["topic"]
    audience = data.get("audience", "25-45岁中文短视频用户")
    voice = data.get("voice", "温暖、克制、略带故事感的中文男声")
    duration = int(data.get("duration", 50))
    character = data.get(
        "character",
        "38岁成年东方男性，短发，深色简洁外套，真实自然面孔，神情平静略带疲惫"
    )

    project_dir = Path(args.output) / slugify(topic)
    project_dir.mkdir(parents=True, exist_ok=True)

    hook = f"你有没有在某个安静的晚上，突然想起：{topic}"
    script = (
        f"{hook}？\n\n"
        "小时候总以为，长大以后就会拥有答案。\n"
        "后来才明白，生活不是把所有问题解决掉，"
        "而是在忙碌、遗憾和责任之间，依然保留一点属于自己的光。\n"
        "有些快乐很小，小到只是一顿热饭，一通电话，"
        "或者回家路上吹来的一阵晚风。\n"
        "我们不是不快乐，只是太久没有停下来，好好感受它。\n"
        "愿你经历了生活的风雨，仍然记得照顾自己。\n"
        "屏幕前的你，最近一次真正开心，是什么时候？"
    )

    shots = [
        ("夜晚公交车窗边", "望向窗外，呼吸平稳", "缓慢侧向推近"),
        ("老城区清晨街道", "独自缓步行走", "低机位跟拍"),
        ("家中餐桌", "双手捧着热茶", "微距缓慢拉近"),
        ("地铁站人群", "在人群中短暂停下", "稳定器横移"),
        ("河边黄昏", "靠在栏杆看远处", "背后缓慢环绕"),
        ("雨后街角", "抬头看路灯和树叶", "轻微仰拍"),
        ("家门口暖光", "轻轻推门回家", "背面跟拍"),
        ("窗边夜景", "安静坐下，露出很淡的微笑", "缓慢拉远"),
    ]

    segments = [x.strip() for x in re.split(r"(?<=[。？！])", script.replace("\n", "")) if x.strip()]
    per = duration / len(shots)
    storyboard = []
    prompts = []
    srt = []
    cursor = 0.0

    for i, (scene, action, camera) in enumerate(shots, start=1):
        narration = segments[min(i - 1, len(segments) - 1)]
        start, end = cursor, min(duration, cursor + per)
        cursor = end
        zh_prompt = (
            f"{character}，{scene}，{action}，情绪克制、真实、有故事感，"
            f"自然电影光线，中近景，{camera}，浅景深，真实皮肤纹理，"
            "35mm电影镜头，细腻胶片质感，竖屏9:16"
        )
        en_prompt = (
            f"An adult East Asian man in his late thirties, short hair, simple dark jacket, "
            f"natural realistic face, in {scene}, {action}, restrained emotional expression, "
            f"cinematic natural lighting, medium close-up, {camera}, shallow depth of field, "
            "realistic skin texture, 35mm film look, subtle film grain, vertical 9:16"
        )
        storyboard.append({
            "shot": i, "start": start, "end": end, "narration": narration,
            "scene": scene, "action": action, "camera": camera,
        })
        prompts.append({
            "shot": i, "prompt_zh": zh_prompt, "prompt_en": en_prompt,
            "negative_prompt": DEFAULT_NEGATIVE
        })
        srt.append(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{narration}\n")

    project = {
        "title": topic,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "format": "9:16",
        "resolution": "1080x1920",
        "duration_seconds": duration,
        "audience": audience,
        "voice": voice,
        "character": character,
        "recommended_workflow": "video Z image wan2.2",
        "status": "project scaffold; prompts and copy should be reviewed before publishing",
    }

    (project_dir / "project.json").write_text(
        json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (project_dir / "script.txt").write_text(script + "\n", encoding="utf-8")
    (project_dir / "voiceover.txt").write_text(
        f"配音建议：{voice}\n语速：0.92倍左右\n\n{script}\n", encoding="utf-8"
    )
    (project_dir / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    (project_dir / "prompts.json").write_text(
        json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [f"# 分镜表：{topic}", "", f"- 总时长：{duration}秒", "- 画幅：9:16", ""]
    for item, prompt in zip(storyboard, prompts):
        md += [
            f"## 镜头 {item['shot']}",
            f"- 时间：{item['start']:.1f}s–{item['end']:.1f}s",
            f"- 旁白：{item['narration']}",
            f"- 场景：{item['scene']}",
            f"- 动作：{item['action']}",
            f"- 运镜：{item['camera']}",
            f"- 中文提示词：{prompt['prompt_zh']}",
            "",
        ]
    (project_dir / "storyboard.md").write_text("\n".join(md), encoding="utf-8")

    notes = f"""# RunningHub / Wan2.2 使用建议

- 推荐模板：video Z image wan2.2
- 画幅：9:16
- 分辨率：1080×1920
- 总时长：约 {duration} 秒
- 做法：每个镜头单独生成，再在剪辑软件中拼接
- 角色参考：所有镜头使用同一张成年人物参考图
- 动作幅度：低到中
- 配音：先生成完整中文音频，再按音频时间轴调整字幕
- 字幕：使用项目中的 subtitles.srt
- 注意：本项目未自动调用 RunningHub 或配音 API
"""
    (project_dir / "runninghub-notes.md").write_text(notes, encoding="utf-8")

    print(f"项目已创建：{project_dir.resolve()}")

if __name__ == "__main__":
    main()
