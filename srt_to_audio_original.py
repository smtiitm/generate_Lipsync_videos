'''
Machine Translation to Lipsync
Created by: Abdullah Mazhar
Date: 20/02/2023
'''

import os
import requests
import json
import argparse
from text_to_vtt import SrtToWebVttConverter
from vtt_to_speech import TextToSpeechAPI
import shutil

class Translator:
    def __init__(self, target_lang, output_audiopath, srt_folderpath):
        self.tts_url = "http://10.24.6.168:3091/vtt-to-speech"
        self.output_audiopath = output_audiopath
        self.srt_folderpath = srt_folderpath
        self.target_lang = target_lang

    ##This is the main function that is calling other functionslike (MT, TXT to SRT, SRT to VTT and VTT to Audio)
    def main(self):
        for srt_file in os.listdir(self.srt_folderpath):
            if srt_file != ".DS_Store":
                srt_filename = srt_file.split(".srt")[0]
                srt_filepath = os.path.join(self.srt_folderpath,srt_file)
                print(srt_filepath)
                tsv = SrtToWebVttConverter(srt_filename, self.output_audiopath)
                # print('1:',tsv)
                print("srt_filrpath:",srt_filepath)
                vtt_filepath, vtt_folderpath= tsv.convert_srt_to_webvtt(srt_filepath)
                print("vtt_filepath, vtt_folderpath",vtt_filepath, vtt_folderpath)
                try:
                    tts = TextToSpeechAPI(self.tts_url, self.output_audiopath, srt_filename, self.target_lang, vtt_filepath)
                    tts.text_to_speech()
                except:
                    print("tts audio was not generated:", srt_filename)
                # shutil.rmtree(vtt_folderpath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Translate text files using OneMT API')
    parser.add_argument('--target_lang', type=str, required=True, help='Target language of the input files')
    parser.add_argument('--output_audiopath', type=str, required=True, help='Path to the directory containing input text files')
    parser.add_argument('--srt_folderpath', type=str, required=True, help='Path to the directory to take srt files')
    args = parser.parse_args()
    print("srt_2_audio:",args.output_audiopath,args.srt_folderpath)
    translator = Translator(args.target_lang, args.output_audiopath, args.srt_folderpath)
    translator.main()
