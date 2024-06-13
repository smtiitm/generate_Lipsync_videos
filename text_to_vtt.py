import sys
from pysrt import SubRipFile, SubRipTime, SubRipItem
import webvtt
import os 

class SrtToWebVttConverter:
    
    def __init__(self, srt_filename, input_path):
        self.srt_filename = srt_filename
        self.input_path = input_path

    def convert_srt_to_webvtt(self, srt_filepath):
        vtt_folderpath = self.input_path + "/VTT"
        if not os.path.exists(vtt_folderpath):
            os.makedirs(vtt_folderpath)
        vtt_filepath = vtt_folderpath  + "/" + self.srt_filename.split(".srt")[0] + ".vtt"
        subtitles = webvtt.from_srt(srt_filepath)
        subtitles.save(vtt_filepath)
        return vtt_filepath, vtt_folderpath
      

