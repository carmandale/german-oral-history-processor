import argparse
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import concurrent.futures
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

class CostTracker:
    def __init__(self):
        self.start_time = time.time()
        self.total_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        
    def add_usage(self, response):
        """Add usage statistics from an OpenAI API response"""
        if hasattr(response, 'usage'):
            self.total_tokens += response.usage.total_tokens
            self.total_prompt_tokens += response.usage.prompt_tokens
            self.total_completion_tokens += response.usage.completion_tokens
    
    def report(self):
        """Generate processing report with costs"""
        duration = time.time() - self.start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # GPT-4o costs (50% cheaper than GPT-4 Turbo)
        prompt_cost = (self.total_prompt_tokens / 1000) * 0.005  # $0.005 per 1K tokens
        completion_cost = (self.total_completion_tokens / 1000) * 0.015  # $0.015 per 1K tokens
        total_cost = prompt_cost + completion_cost
        
        return f"""Processing Summary:
Total time: {int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}
Prompt tokens: {self.total_prompt_tokens:,}
Completion tokens: {self.total_completion_tokens:,}
Total tokens processed: {self.total_tokens:,}
Estimated total cost: ${total_cost:.2f}"""

cost_tracker = CostTracker()

def split_into_contextual_chunks(text, max_chunk_size=400):
    """Split text into chunks while preserving context"""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
        else:
            current_chunk += sentence + '. '
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Filter out any empty chunks or chunks that are too small
    chunks = [chunk for chunk in chunks if len(chunk) > 50]
    
    print(f"Created {len(chunks)} chunks")
    # Debug first chunk
    if chunks:
        print(f"First chunk sample: {chunks[0][:100]}...")
    
    return chunks

def process_chunk(chunk: str, client: OpenAI, chunk_number: int) -> str:
    """Process a single chunk with better error handling"""
    try:
        print(f"Processing chunk {chunk_number}...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are an expert translator and oral history editor.
                Format the dialogue with clear speaker labels and separate German/English lines.
                
                Format each exchange as:
                Speaker: [Interviewer/Interviewee]
                German: [Original German text]
                English: [English translation]
                
                Add a blank line between speakers."""},
                {"role": "user", "content": f"""Translate and format this interview segment.
                
                Important formatting rules:
                1. Label each speaker as Interviewer or Interviewee
                2. Show German original on one line starting with "German: "
                3. Show English translation on next line starting with "English: "
                4. Add blank line between speakers
                
                Text to process:
                {chunk}"""}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Add usage tracking
        cost_tracker.add_usage(response)
        
        result = response.choices[0].message.content.strip()
        
        # Verify the content has proper formatting
        if "German:" not in result or "English:" not in result:
            print(f"Warning: Chunk {chunk_number} missing proper formatting")
            return f"[Error processing chunk {chunk_number}]\n{result}"
        
        return result
        
    except Exception as e:
        print(f"Error processing chunk {chunk_number}: {str(e)}")
        return ""

def process_chunks_parallel(chunks: List[str], max_workers: int = 3) -> List[str]:
    """Process chunks in parallel with better error handling"""
    client = OpenAI()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit chunks with their index numbers
        future_to_chunk = {
            executor.submit(process_chunk, chunk, client, i): (i, chunk) 
            for i, chunk in enumerate(chunks, 1)
        }
        
        # Process completed futures as they complete
        for future in concurrent.futures.as_completed(future_to_chunk):
            chunk_num, chunk = future_to_chunk[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Completed chunk {chunk_num}/{len(chunks)}")
            except Exception as e:
                print(f"Failed to process chunk {chunk_num}: {str(e)}")
                results.append("")
    
    return results

def reformat_text(input_file: str, output_file: str):
    try:
        print(f"Reading file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Total text length: {len(text)} characters")
        chunks = split_into_contextual_chunks(text)
        
        print(f"\nProcessing {len(chunks)} chunks in parallel...")
        results = process_chunks_parallel(chunks)
        
        # Combine results with double line breaks between chunks
        formatted_text = "\n\n---\n\n".join(r for r in results if r)
        
        # Save output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"\nProcessing completed!")
        print(cost_tracker.report())
        print(f"File created:\n- {output_file}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reformat interview transcript and create English version')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output', default='interview_formatted_bilingual.txt', 
                        help='Path to save the formatted bilingual version')
    
    args = parser.parse_args()
    reformat_text(args.input_file, args.output)
