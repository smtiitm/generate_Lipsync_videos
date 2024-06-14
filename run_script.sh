#!/bin/bash

# Get the directory of the Bash script
script_dir="$(dirname "$(realpath "$0")")"

# Set the path to your virtual environment
virtual_env_path="../envs/cnn_envs/bin/activate"

# Set your paths and language here (relative to the script's location)

# Target language {'hin':'hindi','mal':'malayalam','kan':'kannada','bn':'bengali','ur':'urdu','tel':'telugu','pun':'punjabi', 'mar':'marathi', 'guj':'gujarati', 'tam':'tamil', 'hin':'hindi','en':'english'}

target_lang="tam"

# Original video path 
original_video_path="$script_dir/OrigVideo/Week4_Lecture3.mp4"

# Translated SRT path
translated_srt_path="$script_dir/Translated_SRT/Week4_Lecture3_Cleaned_Tagged.ta.srt"


output_audio_segments_path="$script_dir/TTS_AUDIO"
final_output_file_path="$script_dir/final_output_vedios"

srt_folderpath="$script_dir/Translated_SRT"

# Activate the virtual environment
source "$virtual_env_path"


# Extract the original video filename without extension
original_video_name=$(basename "$original_video_path" .mp4)
srt_file_name=$(basename "$translated_srt_path" .srt)
# Automatically create new video and SRT file paths based on the original video name
new_video="$script_dir/$original_video_name.mp4"
new_srt="$script_dir/$original_video_name.srt"

# Create a folder for each target language if it doesn't exist
output_folder="$final_output_file_path/$target_lang"
if [ ! -d "$output_folder" ]; then
    mkdir -p "$output_folder"
fi

#echo "location1"
# Call the Python script for SRT to audio conversion
python3 "$script_dir/srt_to_audio_original.py" --target_lang "$target_lang" --output_audiopath "$output_audio_segments_path" --srt_folderpath "$srt_folderpath"

# TTS audio directory
audio_dir="$output_audio_segments_path/${target_lang}_WAV/$srt_file_name"

echo "audio_dir"

#echo "location2"
# Call the Python lip syncing script with the provided arguments
python3 "$script_dir/lip_sync_online_v1_original.py" --original_video_path "$original_video_path" --Translated_SRT "$translated_srt_path" --audio_dir "$audio_dir" --output_video_path "$new_video" --new_srt_path "$new_srt"

#echo "location3"
# Run ffmpeg command to convert SRT to ASS to add Subtitle to New Video 
ffmpeg -i "$new_srt" -vf "ass=fontsize=12" "$script_dir/$original_video_name.ass"

ffmpeg -i "$new_video" -vf "ass=$script_dir/$original_video_name.ass" "$output_folder/$original_video_name"_with_subtitle.mp4

# Remove temporary files
rm "$new_srt" "$new_video" "$script_dir/$original_video_name.ass"
