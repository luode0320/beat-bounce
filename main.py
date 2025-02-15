import os
import subprocess
from datetime import datetime

import bpy
import librosa

path_root = "E:/beat-bounce/"
frame_rate = 24  # 帧率为24fps


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
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
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
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # 或者 'FFMPEG' 如果直接输出视频
    bpy.context.scene.render.filepath = output_path  # 对于图像序列
    bpy.ops.render.render(animation=True)


def merge_audio_video_with_ffmpeg(audio_path, image_sequence_path, output_path):
    """
    使用FFmpeg合并音频和图像序列成视频
    :param audio_path: 音频文件路径
    :param image_sequence_path: 图像序列路径（包含通配符）
    :param output_path: 输出视频文件路径
    """
    command = [
        os.path.join(path_root, "ffmpeg-7.1-essentials_build", "bin", "ffmpeg.exe"),
        '-y',  # 覆盖输出文件
        '-framerate', str(frame_rate),  # 帧率
        '-i', image_sequence_path,  # 输入图像序列
        '-i', audio_path,  # 输入音频
        '-c:v', 'libx264',  # 视频编码器
        '-pix_fmt', 'yuv420p',  # 像素格式
        '-c:a', 'aac',  # 音频编码器
        '-strict', 'experimental',  # 允许实验性功能
        '-b:a', '192k',  # 音频比特率
        output_path  # 输出文件路径
    ]
    subprocess.run(command)


# 获取当前时间戳并格式化
def get_timestamp():
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H%M")


# Blender主脚本入口
if __name__ == "__main__":
    # 提取音乐节拍
    audio_path = os.path.join(path_root, "file", "win臣 - 银行不妙曲 (超燃).flac")
    tempo, beat_frames = audio_processing_load(audio_path)

    # 生成小球或其他元素跟随音乐节奏弹跳的动画
    animation_generation_load(tempo, beat_frames)

    # 设置渲染输出路径, 获取时间戳
    timestamp = get_timestamp()
    output_image_sequence_path = os.path.join(path_root, "path", "frame", f"{timestamp}_")  # 图像序列输出路径
    final_output_video_path = os.path.join(path_root, "path", f"final_video_{timestamp}.mp4")  # 最终视频输出路径

    # 渲染动画
    render_animation(output_image_sequence_path)

    # 合并音频和视频
    merge_audio_video_with_ffmpeg(
        audio_path=audio_path,
        image_sequence_path=output_image_sequence_path + '%04d.png',  # 假设是四位数字编号的序列
        output_path=final_output_video_path
    )
