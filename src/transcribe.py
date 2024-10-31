import mlx_whisper
import sys
import os

def transcribe_audio(input_path, output_path):
    # Verify input file exists and has valid extension
    supported_formats = {'.m4a', '.mp3', '.wav', '.flac', '.ogg'}
    file_extension = os.path.splitext(input_path)[1].lower()
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return
    
    if file_extension not in supported_formats:
        print(f"Error: Unsupported file format '{file_extension}'. Supported formats: {', '.join(supported_formats)}")
        return

    try:
        # Perform transcription with absolute path
        text = mlx_whisper.transcribe(
            os.path.abspath(input_path),  # Convert to absolute path
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo"
        )["text"]
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Transcription saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    # Check if correct number of arguments provided
    if len(sys.argv) != 3:
        print("Usage: python transcribe.py <input_audio_path> <output_text_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    transcribe_audio(input_path, output_path)