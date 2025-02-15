import bpy


# 根据音乐节拍, 生成小球或其他元素跟随音乐节奏弹跳的动画
def animation_generation_load(tempo, beat_frames):
    # 假设你已经有一个名为"Ball"的对象
    ball = bpy.data.objects['Ball']
    frame_start = 1
    for i, beat in enumerate(beat_frames):
        # 在每个节拍处设置关键帧
        ball.location.z = (i % 2) * 2  # 简单的上下移动
        ball.keyframe_insert(data_path="location", frame=beat + frame_start)
