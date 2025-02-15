import ffmpeg

# 输入音频和图像序列
audio_input = ffmpeg.input('path_to_your_audio_file.mp3')
video_input = ffmpeg.input('path_to_your_image_sequence_%04d.png', framerate=25)

# 输出为最终视频
ffmpeg.output(audio_input, video_input, 'output_video.mp4').run()