import sys
import webvtt
import os
import re

class SrtToWebVttConverter:
    
    def __init__(self, srt_filename, input_path):
        self.srt_filename = srt_filename
        self.input_path = input_path

    def remove_tags(self, text):
        return re.sub(r'</?DNT>|</?DT>', '', text)

    def convert_srt_to_webvtt(self, srt_filepath):
        vtt_folderpath = os.path.join(self.input_path, "VTT")
        if not os.path.exists(vtt_folderpath):
            os.makedirs(vtt_folderpath)

        vtt_filepath = os.path.join(vtt_folderpath, self.srt_filename.replace(".srt", ".vtt"))
        print("text to Vtt",vtt_filepath)
        subtitles = webvtt.from_srt(srt_filepath)

        # Clean tags from each caption
        for caption in subtitles:
            caption.text = self.remove_tags(caption.text)
            # print(caption.text)
        subtitles.save(vtt_filepath)
        return vtt_filepath, vtt_folderpath
