"""
Lip syncing code - Online version
"""

import os
import sys
import moviepy.editor as mp
from pysrt import SubRipFile, SubRipTime, SubRipItem
from pydub import AudioSegment
from tqdm import tqdm
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def srt_time_to_seconds(time_obj):
    # Handles both pysrt.SubRipTime and datetime.time
    if hasattr(time_obj, 'hours'):
        return (
            time_obj.hours * 3600 +
            time_obj.minutes * 60 +
            time_obj.seconds +
            time_obj.milliseconds / 1000.0
        )
    else:
        return (
            time_obj.hour * 3600 +
            time_obj.minute * 60 +
            time_obj.second +
            time_obj.microsecond / 1_000_000.0
        )


def segment_audio(full_audio_path, srt_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    full_audio = AudioSegment.from_file(full_audio_path)
    srt = SubRipFile.open(srt_file)
    audio_paths = []

    logging.info("Segmenting audio based on SRT...")
    for i, entry in enumerate(tqdm(srt, desc="Segmenting")):
        start_ms = int(srt_time_to_seconds(entry.start) * 1000)
        end_ms = int(srt_time_to_seconds(entry.end) * 1000)
        segment = full_audio[start_ms:end_ms]
        segment_path = os.path.join(output_dir, f"segment_{i+1:03d}.mp3")
        segment.export(segment_path, format="mp3")
        audio_paths.append(segment_path)

    return audio_paths

def lip_sync(video_path, srt_path, audio_list, output_video, output_srt):
    output_filename = os.path.splitext(output_video)[0]
    video_obj = mp.VideoFileClip(video_path)
    srt = SubRipFile.open(srt_path)

    video_clips = []
    prev_end_time = SubRipTime(0)
    new_srt_start_time = []
    new_srt_end_time = []
    new_srt_total_duration = 0.0

    for i, entry in enumerate(tqdm(srt, desc="Generating video segments")):
        logging.info(f"Processing subtitle #{i+1}")

        start = entry.start.to_time()
        end = entry.end.to_time()

        if srt_time_to_seconds(start) > srt_time_to_seconds(prev_end_time.to_time()):
            inter_clip = video_obj.subclip(srt_time_to_seconds(prev_end_time.to_time()), srt_time_to_seconds(start)).without_audio()
            silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=inter_clip.duration)
            video_clips.append(inter_clip.set_audio(silence))
            new_srt_total_duration += inter_clip.duration

        srt_clip = video_obj.subclip(srt_time_to_seconds(start), srt_time_to_seconds(end)).without_audio()
        audio_clip = mp.AudioFileClip(audio_list[i])

        if srt_clip.duration != audio_clip.duration:
            srt_clip = srt_clip.fx(mp.vfx.speedx, factor=srt_clip.duration/audio_clip.duration)

        final_clip = srt_clip.set_audio(audio_clip)
        video_clips.append(final_clip)
        new_srt_start_time.append(new_srt_total_duration)
        new_srt_end_time.append(new_srt_total_duration + final_clip.duration)
        new_srt_total_duration += final_clip.duration

        prev_end_time = entry.end

    if srt_time_to_seconds(srt[-1].end.to_time()) < video_obj.duration:
        final_clip = video_obj.subclip(srt_time_to_seconds(srt[-1].end.to_time()), video_obj.duration).without_audio()
        silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=final_clip.duration)
        video_clips.append(final_clip.set_audio(silence))

    logging.info("Concatenating video segments...")
    final_video = mp.concatenate_videoclips(video_clips)
    final_video.write_videofile(
        output_video,
        codec="libx264",
        threads=30,
        audio_codec='aac',
        temp_audiofile=output_filename+'.m4a',
        remove_temp=True,
        preset="medium",
        ffmpeg_params=["-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p"]
    )

    logging.info("Writing updated SRT timings...")
    new_srt = SubRipFile()
    for i, entry in enumerate(srt):
        new_srt.append(SubRipItem(
            index=i+1,
            start=SubRipTime(seconds=new_srt_start_time[i]),
            end=SubRipTime(seconds=new_srt_end_time[i]),
            text=entry.text
        ))
    new_srt.save(output_srt, encoding='utf-8')
    logging.info("Lip sync video generation complete.")

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original_video_path", required=True)
    parser.add_argument("--Translated_SRT", required=True)
    parser.add_argument("--tts_audio_path", required=True)
    parser.add_argument("--output_video_path", required=True)
    parser.add_argument("--new_srt_path", required=True)
    parser.add_argument("--segmented_audio_dir", default="segmented_audio")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    segmented_audio = segment_audio(args.tts_audio_path, args.Translated_SRT, args.segmented_audio_dir)
    lip_sync(args.original_video_path, args.Translated_SRT, segmented_audio, args.output_video_path, args.new_srt_path)
