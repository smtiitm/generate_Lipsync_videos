import os
from gtts import gTTS

class TextToSpeechAPI:
    def __init__(self, tts_url, input_path, srt_filename, target_lang, vtt_filepath):
        self.input_path = input_path
        self.srt_filename = srt_filename
        self.target_lang = target_lang
        self.vtt_filepath = vtt_filepath

        # Language codes for gTTS (you can expand this dictionary)
        self.lang_dict = {
            'ta': 'ta',  # Tamil
            'hin': 'hi',  # Hindi
            'en': 'en',   # English
            'mal': 'ml',  # Malayalam
            'kan': 'kn',  # Kannada
            'tel': 'te',  # Telugu
            'mar': 'mr',  # Marathi
            'guj': 'gu',  # Gujarati
            'bn':  'bn',  # Bengali
            'pun': 'pa',  # Punjabi
            'ur':  'ur',  # Urdu
        }

    def text_to_speech(self):
        # 1. Read VTT file
        try:
            print("VTTPATH",self.vtt_filepath)
            with open(f"{self.vtt_filepath}", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[Error] VTT file not found: {self.vtt_filepath}")
            return

        # 2. Get language code
        lang_code = self.lang_dict.get(self.target_lang)
        if not lang_code:
            print(f"[Error] Unsupported target language: {self.target_lang}")
            return

        # 3. Extract only spoken lines (remove timestamps, metadata)
        spoken_lines = []
        for line in lines:
            line = line.strip()
            if not line or "-->" in line or line.lower().startswith("webvtt"):
                continue
            spoken_lines.append(line)

        if not spoken_lines:
            print("[Error] No text found in VTT file.")
            return

        clean_text = " ".join(spoken_lines)
        print(f"[Info] Preview of TTS input: {clean_text[:100]}...")

        # 4. Use gTTS to synthesize audio
        try:
            tts = gTTS(clean_text, lang=lang_code)
        except Exception as e:
            print(f"[Error] gTTS failed: {e}")
            return

        # 5. Prepare output paths
        wav_folderpath = os.path.join(self.input_path, f"{self.target_lang}_WAV")
        os.makedirs(wav_folderpath, exist_ok=True)

        file_prefix = self.srt_filename.split(".srt")[0]
        week_folderpath = os.path.join(wav_folderpath, file_prefix)
        os.makedirs(week_folderpath, exist_ok=True)

        # audio_path = os.path.join(week_folderpath, f"{file_prefix}_full.mp3")
        audio_path = os.path.join(week_folderpath, f"{file_prefix}.mp3")

        # 6. Save audio file
        try:
            tts.save(audio_path)
            print(f"[Success] gTTS audio saved to: {audio_path}")
        except Exception as e:
            print(f"[Error] Failed to save audio: {e}")