"""System commands."""

import os

from inspect import getfullargspec
from functools import wraps

from .variables import WSL, CUDA


def windowspath(path):
    path = str(path)

    if path.startswith('/mnt/'):
        new_path = path.replace('/mnt/', '')
        new_path = new_path[0] + ':/' + new_path[1:]

    else:
        cmd = get_windows_path(path)
        new_path = os.popen(cmd)
        new_path = new_path.read().strip('\n')

    return new_path


def handle_args_decorator(arguments, argument_fn, output_fn):
    def decorator(f):
        argspec = getfullargspec(f)
        @wraps(f)
        def wrapper(*args, **kwargs):
            args = list(args)
            for argument_name in arguments:
                argument_index = argspec.args.index(argument_name)
                try:
                    args[argument_index] = argument_fn(args[argument_index])
                except IndexError:
                    kwargs[argument_name] = argument_fn(kwargs[argument_name])
            args = tuple(args)
            output = f(*args, **kwargs)
            output = output_fn(output)
            return output
        return wrapper
    return decorator


def handle_path(path):
    return path if not WSL else windowspath(path)


def handle_command(cmd):
    return cmd if not WSL else cmd.replace(
        'ffmpeg', 'ffmpeg.exe', 1).replace('ffprobe', 'ffprobe.exe', 1)


@handle_args_decorator(['src', 'dest'], handle_path, handle_command)
def convert_to_wav(src, dest):
    cmd = f'ffmpeg -y -hide_banner -loglevel error -i "{src}" -af silenceremove=1:0:-50dB "{dest}"'

    return cmd


@handle_args_decorator(['input_file', 'output_file'], handle_path, handle_command)
def process_segment(
    start, length, input_file, output_file, cuda, segment_codec,
    width=None, height=None, watermark=None, watermark_fontsize=40,
    even_dimensions=False
):
    if cuda is None:
        cuda = CUDA

    # hwaccel = '-hwaccel cuvid -hwaccel_output_format cuda' if cuda else ''
    hwaccel = ''
    input_codec = '-c:v h264_cuvid' if cuda else ''

    if segment_codec is None:
        if cuda:
            segment_codec = '-c:v h264_nvenc -preset:v fast -tune:v hq -rc:v vbr -cq:v 19 -b:v 0 -profile:v high'
        else:
            segment_codec = '-c:v libx264 -crf 27 -preset ultrafast'

    vf = get_vf(
        width, height, watermark, watermark_fontsize, even_dimensions,
        deinterlace=False, colorspace=False, cuda=cuda
    )

    timebase = '-video_track_timescale 60000'

    cmd = f'ffmpeg -y -hide_banner -loglevel error {hwaccel} {input_codec} -vsync 0 -ss {start} -t {length} -i "{input_file}" -ac 2 -c:a ac3 -ar 48000 -mbd rd -trellis 2 -cmp 2 -subcmp 2 -g 100 {segment_codec} {timebase} -f mpeg {vf} "{output_file}"'

    return cmd


@handle_args_decorator(['input_file', 'output'], handle_path, handle_command)
def join(
    input_file, output,
    width=None, height=None,
    convert=False, output_codec=None,
    watermark=None, watermark_fontsize=40
):
    if convert:
        if output_codec is None:
            # if CUDA:
            #     hwaccel = '-hwaccel cuvid -hwaccel_output_format cuda -c:v h264_cuvid'
            #     output_codec = '-c:v h264_nvenc -preset:v fast -tune:v hq -rc:v vbr -cq:v 19 -b:v 0 -profile:v high'
            # else:
            hwaccel = ''
            output_codec = '-c:v libx264 -crf 27 -preset ultrafast'
        else:
            hwaccel = ''
    else:
        hwaccel = ''
        output_codec = '-c:v copy'

    vf = ''

    return f'ffmpeg -y -hide_banner -loglevel error {hwaccel} -auto_convert 1 -f concat -safe 0 -i "{input_file}" {output_codec} -movflags faststart {vf} "{output}"'


@handle_args_decorator(['input_file', 'output_file'], handle_path, handle_command)
def convert_audio(input_file, output_file, acodec):
    cmd = f'ffmpeg -y -hide_banner -loglevel error -i "{input_file}" -acodec {acodec} "{output_file}"'
    return cmd


@handle_args_decorator(['video', 'audio', 'output'], handle_path, handle_command)
def join_audio_video(offset, video, audio, channel, output):
    acodec = '-acodec aac'
    if channel == 'mix':
        mapping = '-filter_complex amix'
    else:
        mapping = f'-map 0:v:0 -map {channel}:a:0'

    return f'ffmpeg -y -hide_banner -loglevel error -itsoffset {offset} -i "{video}" -i "{audio}" -vcodec copy {acodec} -shortest {mapping} "{output}"'


@handle_args_decorator(['path'], handle_path, handle_command)
def get_duration(path):
    print(path)
    return f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{path}"'


@handle_args_decorator(['path'], handle_path, handle_command)
def get_bitrate(path):
    return f'ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 "{path}"'


@handle_args_decorator(['path'], handle_path, handle_command)
def get_streams(path, stream_type):
    return f'ffprobe -i "{path}" -show_streams -select_streams {stream_type} -loglevel error'


def get_wslpath(path):
    return f'wslpath "{path}"'


def get_windows_path(path):
    return f'wslpath -m "{path}"'


def get_vf(
    width, height, watermark, watermark_fontsize, even_dimensions, deinterlace,
    colorspace, cuda
):
    vf = []

    if width is not None and height is not None:
        vf.append(
            f'scale=(iw*sar)*min({width}/(iw*sar)\,{height}/ih):ih*min({width}/(iw*sar)\,{height}/ih), pad={width}:{height}:({width}-iw*min({width}/iw\,{height}/ih))/2:({height}-ih*min({width}/iw\,{height}/ih))/2'
        )

    if even_dimensions:
        vf.append('crop=trunc(iw/2)*2:trunc(ih/2)*2')

    if deinterlace:
        if cuda:
            vf.append('yadif_cuda')
        else:
            vf.append('yadif')

    if colorspace:
        vf.append('format=pix_fmts=yuv420p')

    if watermark is not None:
        watermark = watermark.split('<EOL>')
        start = 10
        for text in watermark:
            vf.append(f"drawtext=text='{text}':x=10:y={start}:bordercolor=black:borderw=3:fontcolor=white:fontsize={watermark_fontsize}:fontfile=Arial")
            start += watermark_fontsize + 5

    if len(vf):
        vf = ','.join(vf)
        vf = f'-vf "[in]{vf}[out]"'
    else:
        vf = ''

    return vf
