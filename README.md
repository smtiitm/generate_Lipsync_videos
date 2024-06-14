# Lip-Sync Video Generation

This project generates a lip-synced video based on an original video and translated subtitles.

## Prerequisites

- Conda
- Python 3.8

## Setup

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate the conda environment:

    ```bash
    conda create -n lipsync_env python=3.8
    conda activate lipsync_env
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Edit the `run_script.sh` file to assign the paths to your original video and translated subtitles:

    ```bash
    original_video_path="path/to/original_video.mp4"
    translated_srt_path="path/to/translated_subtitles.srt"
    ```

2. Assign the target language code in `run_script.sh`:

    ```bash
    target_language_code="hin"  # Example: 'hin' for Hindi
    ```

3. Run the script:

    ```bash
    ./run_script.sh
    ```

## Supported Languages

- Hindi (hin)
- Malayalam (mal)
- Kannada (kan)
- Bengali (bn)
- Urdu (ur)
- Telugu (tel)
- Punjabi (pun)
- Marathi (mar)
- Gujarati (guj)
- Tamil (tam)
- English (en)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
