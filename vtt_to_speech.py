import requests
import json
import base64
import os 

class TextToSpeechAPI:
    def __init__(self, tts_url, input_path, srt_filename, target_lang, vtt_filepath):
        self.tts_url = tts_url
        self.input_path = input_path
        self.srt_filename = srt_filename
        self.target_lang = target_lang
        self.vtt_filepath= vtt_filepath
        self.lang_dict = {'hin':'hindi','mal':'malayalam','kan':'kannada','bn':'bengali','ur':'urdu','tel':'telugu','pun':'punjabi', 'mar':'marathi', 'guj':'gujarati', 'tam':'tamil', 'hin':'hindi','en':'english'}

    def text_to_speech(self, alpha=1, gender='male', segmentwise=True):#alpha=0.8333332836627969

        with open(self.vtt_filepath, "r") as f:
            text = f.read()
        payload = json.dumps({
            "input": text,
            "lang": self.lang_dict[self.target_lang],
            "gender": gender,
            "alpha": alpha,
            "segmentwise": segmentwise
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", self.tts_url, headers=headers, data=payload)
        print(response)
        api_output = response.json()
        if api_output["status"]=='success':
            segments = api_output['segments']
            print("length of segments:", len(segments))
            wav_folderpath = self.input_path + "/" + self.target_lang + "_WAV"
            if not os.path.exists(wav_folderpath):
                    os.makedirs(wav_folderpath)
            for wave_idx, segment in enumerate(segments):
                file_prefix = self.srt_filename.split(".srt")[0]
                week_folderpath = wav_folderpath + "/" + file_prefix
                if not os.path.exists(week_folderpath):
                    os.makedirs(week_folderpath)
                wav_file = open("{}/{}_{:04}.wav".format(week_folderpath,file_prefix,wave_idx+1),'wb')
                decode_string = base64.b64decode(segment)
                wav_file.write(decode_string)
                wav_file.close()

            print(f'Log: TTS saved to folder: "{wav_folderpath}"')
        else:
             print(api_output['reason'])
