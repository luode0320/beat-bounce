import os
from datetime import datetime

import bpy
import librosa

# 假设帧率为24FPS
frame_rate = 24


def audio_processing_load(audio_path):
    # 加载音频文件
    y, sr = librosa.load(audio_path)

    # 提取节拍
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    # 将节拍时间点转换为帧数（假设Blender的帧率为24fps）
    beat_frames_in_blender = [int(beat * frame_rate) for beat in librosa.frames_to_time(beat_frames, sr=sr)]

    return tempo, beat_frames_in_blender


def create_ball():
    """创建一个球体并返回其引用"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 5))  # 初始位置在空中
    ball = bpy.context.object
    return ball


def create_ground():
    """创建一个长方形表面并返回其引用"""
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    ground = bpy.context.object
    return ground


def animation_generation_load(tempo, beat_frames):
    # 如果没有找到名为"Ball"的对象，则创建一个新的
    if 'Ball' not in bpy.data.objects:
        ball = create_ball()
        ball.name = 'Ball'
    else:
        ball = bpy.data.objects['Ball']

    # 创建地面
    if 'Ground' not in bpy.data.objects:
        ground = create_ground()
        ground.name = 'Ground'

    # 设置起始帧
    frame_start = 1
    bounce_height = 5  # 每次弹起的高度
    gravity_acceleration = -9.81 / (frame_rate ** 2)  # 简化的重力加速度

    for i, beat_frame in enumerate(beat_frames):
        # 计算从当前节拍到下一个节拍的时间间隔（帧数）
        next_beat_frame = beat_frames[i + 1] if i + 1 < len(beat_frames) else beat_frames[-1] + 30  # 假设最后一个节拍后有额外的30帧
        interval_frames = next_beat_frame - beat_frame

        # 在每个节拍处设置关键帧：球下落
        bpy.context.scene.frame_set(beat_frame)
        ball.location.z = bounce_height
        ball.keyframe_insert(data_path="location", index=2)

        # 在节拍之间设置关键帧：球上升和下降
        for frame in range(1, interval_frames):
            bpy.context.scene.frame_set(beat_frame + frame)
            t = frame / interval_frames  # 时间归一化
            z_position = bounce_height * (1 - 4 * t * (1 - t))  # 弹簧函数模拟反弹
            ball.location.z = z_position
            ball.keyframe_insert(data_path="location", index=2)

        # 最终落到地面的关键帧
        bpy.context.scene.frame_set(next_beat_frame)
        ball.location.z = 0
        ball.keyframe_insert(data_path="location", index=2)


def render_animation(output_path):
    """
    渲染Blender场景到指定路径
    :param output_path: 输出文件夹或文件路径
    """
    # 设置输出格式为FFMPEG视频
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'

    # 设置输出路径
    bpy.context.scene.render.filepath = output_path

    # 设置编码器和其他视频参数
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'  # 可以是 'NONE', 'LOSSLESS', 'PERC_LOSSLESS', 'HIGH', 'MEDIUM', 'LOW'
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'  # 预设可以是 'BEST', 'GOOD', 'REALTIME'
    bpy.context.scene.render.resolution_x = 1920  # 分辨率宽度
    bpy.context.scene.render.resolution_y = 1080  # 分辨率高度
    bpy.context.scene.render.resolution_percentage = 100  # 分辨率百分比
    bpy.context.scene.render.fps = frame_rate  # 帧率

    # 开始渲染
    bpy.ops.render.render(animation=True)


# 获取当前时间戳并格式化
def get_timestamp():
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")


# Blender主脚本入口
if __name__ == "__main__":
    # 定义根路径
    path_root = '/path/to/your/project/'  # 替换为实际的根路径

    # 获取时间戳
    timestamp = get_timestamp()

    # 设置渲染输出路径（带有时间戳）
    output_directory = f"{path_root}output_{timestamp}"
    final_output_video_path = os.path.join(output_directory, f"final_video_{timestamp}.mp4")  # 最终视频输出路径

    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(final_output_video_path), exist_ok=True)

    # 提取音乐节拍
    audio_path = '/path/to/your/audio/file.flac'  # 替换为实际的音频文件路径
    tempo, beat_frames = audio_processing_load(audio_path)

    # 生成小球及其他元素跟随音乐节奏弹跳的动画
    animation_generation_load(tempo, beat_frames)

    # 渲染动画并导出为视频
    render_animation(final_output_video_path)
