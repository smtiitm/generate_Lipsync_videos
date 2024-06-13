"""
Lip syncing code - Online version
"""

import os
import sys
import moviepy.editor as mp
from pysrt import SubRipFile, SubRipTime, SubRipItem
import argparse


def srt_time_to_seconds(time_datetime_format):
    time_iso_format = time_datetime_format.isoformat()
    # print(time_iso_format)
    seconds = float(time_iso_format.split(':')[-1])
    rest_list = time_iso_format.split(':')[:-1]
    # print(rest_list)
    if ":".join(rest_list) == "00:00":
        pass
    else:
        for i in range(0,len(rest_list)):
            if i == 0:
                # print(rest_list[i])
                seconds += int(rest_list[i])*3600
            elif i == 1:
                # print(rest_list[i])
                seconds += int(rest_list[i])*60
            else:
                sys.exit("Error in time conversion")
    return seconds

def lip_sync(video_path, srt_path, audio_list, output_video, output_srt):

    # output video filename without extension
    output_filename = os.path.splitext(output_video)[0]

    # read the original video as obj
    video_obj = mp.VideoFileClip(video_path)

    # read target srt file
    srt = SubRipFile.open(srt_path)

    # initialize variables
    video_clips = []

    prev_end_time = SubRipTime(0)

    new_srt_start_time = []
    new_srt_end_time = []
    new_srt_total_duration = 0.0

    # iterate through srt entries
    for i, srt_entry in enumerate(srt):
        
        print(f"srt_num: {i+1}")

        start_time = srt_entry.start.to_time()
        end_time = srt_entry.end.to_time()

        if srt_time_to_seconds(start_time) > srt_time_to_seconds(prev_end_time.to_time()):
            # add inter-srt clip to video_clips
            inter_srt_clip = video_obj.subclip(srt_time_to_seconds(prev_end_time.to_time()), srt_time_to_seconds(start_time))
            inter_srt_clip_without_audio = inter_srt_clip.without_audio()
            # Create a silent audio clip with the same duration as the video
            silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=(srt_time_to_seconds(start_time) - srt_time_to_seconds(prev_end_time.to_time())), nloops=1)
            # Set the silent audio track in the video clip
            inter_srt_clip_with_silence = inter_srt_clip_without_audio.set_audio(silence)
            video_clips.append(inter_srt_clip_with_silence)

            new_srt_total_duration += inter_srt_clip_with_silence.duration

        srt_clip = video_obj.subclip(srt_time_to_seconds(start_time), srt_time_to_seconds(end_time))
        srt_clip_without_audio = srt_clip.without_audio()
        video_clips.append(srt_clip_without_audio)
      
        # read audio file
        audio_clip = mp.AudioFileClip(audio_list[i])
        
        # interpolate video to match audio duration
        if srt_clip.duration != audio_clip.duration:
            
            srt_clip = srt_clip.fx(mp.vfx.speedx, factor=srt_clip.duration/audio_clip.duration)
          
            srt_clip_without_audio = srt_clip.without_audio()

        # replace audio in video clip
        video_clip = srt_clip.set_audio(audio_clip)

        new_srt_start_time.append(new_srt_total_duration)
        new_srt_end_time.append(new_srt_total_duration+video_clip.duration)

        new_srt_total_duration += video_clip.duration

        # add video clip to list
        video_clips[-1] = video_clip

        # update previous end time
        prev_end_time = srt_entry.end


    # check if last srt ends before video ends and add final clip if necessary
    last_srt_end_time = srt[-1].end.to_time()
    video_duration = video_obj.duration
    
    print("Completed for loop")
    try:
        if last_srt_end_time != video_duration:
            final_clip = video_obj.subclip(srt_time_to_seconds(last_srt_end_time), video_duration)
            final_clip_without_audio = final_clip.without_audio()
            # Create a silent audio clip with the same duration as the video
            silence = mp.afx.audio_loop(mp.AudioFileClip("silence.wav"), duration=(video_duration - srt_time_to_seconds(last_srt_end_time)), nloops=1)
            final_clip_with_silence = final_clip_without_audio.set_audio(silence)
            video_clips.append(final_clip_with_silence)
            # video_clips.append(final_clip_without_audio)
    except:
        print("Except")
    
    print("try , except completed here. check here error is there or not")
    # concatenate video clips and write final video
    final_video = mp.concatenate_videoclips(video_clips)
    # final_video.write_videofile("output_video.mp4", threads=30)
    final_video.write_videofile(output_video,  codec="libx264", threads=30, audio_codec='aac', temp_audiofile=output_filename+'.m4a', remove_temp=True, preset="medium", ffmpeg_params=["-profile:v","baseline", "-level","3.0","-pix_fmt", "yuv420p"])

    # create new srt file with updated timings
    new_srt = SubRipFile()
    for i, srt_entry in enumerate(srt):
        new_start_time = SubRipTime(seconds=new_srt_start_time[i])
        new_end_time = SubRipTime(seconds=new_srt_end_time[i])
        new_srt.append(SubRipItem(index=i+1, start=new_start_time, end=new_end_time, text=srt_entry.text))

    # Write the updated srt file to file
    new_srt.save(output_srt, encoding='utf-8')
    
def parse_arguments():
    parser = argparse.ArgumentParser(description="Lip syncing script with command-line arguments.")
    parser.add_argument("--original_video_path", required=True, help="Path to the original video file.")
    parser.add_argument("--Translated_SRT", required=True, help="Path to the translated SRT file.")
    parser.add_argument("--audio_dir", required=True, help="Path to the directory containing TTS audio files.")
    parser.add_argument("--output_video_path", required=True, help="Path for the output video file.")
    parser.add_argument("--new_srt_path", required=True, help="Path for the output SRT file.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    video_path = args.original_video_path
    srt_path = args.Translated_SRT
    audio_dir = args.audio_dir
    output_video = args.output_video_path
    output_srt = args.new_srt_path

    audio_list = os.listdir(audio_dir)
    audio_list.sort()
    audio_list = [os.path.join(audio_dir, file) for file in audio_list]

    lip_sync(video_path, srt_path, audio_list, output_video, output_srt)
