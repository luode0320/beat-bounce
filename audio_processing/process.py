import librosa


# 提取音乐节拍
def audio_processing_load(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。

    # 加载音频文件
    audio_path = name
    y, sr = librosa.load(audio_path)

    # 提取节拍
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

    return tempo, beat_frames
