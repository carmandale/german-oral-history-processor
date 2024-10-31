# German Oral History Processor

A tool for processing and translating German oral history interviews using OpenAI's GPT models.

## Setup

1. Clone the repository
    ```bash
    git clone https://github.com/yourusername/german-oral-history-processor.git
    cd german-oral-history-processor
    ```

2. Create and activate virtual environment
    ```bash
    python -m venv venv
    # On Unix/macOS:
    source venv/bin/activate
    # On Windows:
    venv\Scripts\activate
    ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Create .env file with your OpenAI API key
    ```bash
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    ```

## Usage

1. Transcribe audio to text:
    ```bash
    python src/transcribe.py path/to/audio.m4a output/transcription.txt
    ```

2. Process and format transcription:
    ```bash
    python src/reformat_text.py output/transcription.txt --output output/formatted.txt
    ```

## License

MIT