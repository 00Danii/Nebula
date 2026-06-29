from __future__ import annotations
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass, field


@dataclass
class Keyframe:
    time: float
    params: dict[str, object] = field(default_factory=dict)
    colors: dict[str, tuple[int, int, int]] = field(default_factory=dict)


@dataclass
class AnimationClip:
    style_id: str
    duration: float = 5.0
    fps: int = 24
    keyframes: list[Keyframe] = field(default_factory=list)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(round(lerp(c1[0], c2[0], t))),
        int(round(lerp(c1[1], c2[1], t))),
        int(round(lerp(c1[2], c2[2], t))),
    )


def _find_segment(keyframes: list[Keyframe], time: float) -> tuple[Keyframe | None, Keyframe | None, float]:
    if not keyframes:
        return None, None, 0.0
    if len(keyframes) == 1 or time <= keyframes[0].time:
        return keyframes[0], keyframes[0], 1.0
    if time >= keyframes[-1].time:
        return keyframes[-1], keyframes[-1], 1.0
    for i in range(len(keyframes) - 1):
        a, b = keyframes[i], keyframes[i + 1]
        if a.time <= time <= b.time:
            span = b.time - a.time
            t = (time - a.time) / span if span > 0 else 1.0
            return a, b, t
    return keyframes[-1], keyframes[-1], 1.0


def interpolate_params_at(keyframes: list[Keyframe], time: float) -> dict[str, object]:
    a, b, t = _find_segment(keyframes, time)
    if a is None:
        return {}
    result = {}
    all_keys = set(a.params.keys())
    if b is not None and b is not a:
        all_keys |= set(b.params.keys())
    for key in all_keys:
        va = a.params.get(key)
        vb = b.params.get(key) if b is not None and b is not a else va
        if va is None:
            result[key] = vb
        elif vb is None:
            result[key] = va
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            result[key] = int(round(lerp(float(va), float(vb), t))) if isinstance(va, int) else lerp(va, vb, t)
        elif isinstance(va, tuple) and isinstance(vb, tuple) and len(va) == 3 and len(vb) == 3:
            result[key] = lerp_color(va, vb, t)
        else:
            result[key] = va
    return result


def interpolate_colors_at(keyframes: list[Keyframe], time: float) -> dict[str, tuple[int, int, int]]:
    a, b, t = _find_segment(keyframes, time)
    if a is None:
        return {}
    result = {}
    all_keys = set(a.colors.keys())
    if b is not None and b is not a:
        all_keys |= set(b.colors.keys())
    for key in all_keys:
        ca = a.colors.get(key)
        cb = b.colors.get(key) if b is not None and b is not a else ca
        if ca is None:
            result[key] = cb
        elif cb is None:
            result[key] = ca
        else:
            result[key] = lerp_color(ca, cb, t)
    return result


def frame_generator(clip: AnimationClip):
    total_frames = int(clip.duration * clip.fps)
    for i in range(total_frames):
        time = i / clip.fps
        params = interpolate_params_at(clip.keyframes, time)
        colors = interpolate_colors_at(clip.keyframes, time)
        yield time, params, colors


def render_animation(engine, clip: AnimationClip, image_path: str, progress_callback=None):
    frames: list[Image.Image] = []
    style = engine.style_manager.get(clip.style_id)
    if not style:
        raise ValueError(f"Style '{clip.style_id}' not found")

    old_params = style.get_style_params()
    old_colors = style.get_editable_colors()

    try:
        total_frames = int(clip.duration * clip.fps)
        for i, (time, params, colors) in enumerate(frame_generator(clip)):
            for pname, pval in params.items():
                style.update_style_param(pname, pval)
            for ckey, cval in colors.items():
                style.update_color(ckey, cval)
            frame = engine.render(image_path)
            frames.append(frame)
            if progress_callback:
                progress_callback(i + 1, total_frames, time, clip.duration)
    finally:
        for pname, pdef in old_params.items():
            style.update_style_param(pname, pdef.get("value"))
        for ckey, cval in old_colors.items():
            style.update_color(ckey, cval)

    return frames


def export_video(frames: list[Image.Image], output_path: str, fps: int):
    if not frames:
        return
    w, h = frames[0].size
    codecs = ["avc1", "H264", "mp4v"]
    out = None
    for codec in codecs:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        if out.isOpened():
            break
        out.release()
        out = None
    if out is None:
        raise RuntimeError("No se pudo crear el video con ningun codec disponible")
    try:
        for frame in frames:
            frame_bgr = cv2.cvtColor(np.array(frame.convert("RGB")), cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
    finally:
        out.release()


def export_gif(frames: list[Image.Image], output_path: str, fps: int):
    if not frames:
        return
    duration_ms = int(1000 / fps)
    frames_rgb = [f.convert("P", palette=Image.Palette.ADAPTIVE) for f in frames]
    frames_rgb[0].save(
        output_path,
        save_all=True,
        append_images=frames_rgb[1:],
        duration=duration_ms,
        loop=0,
    )
