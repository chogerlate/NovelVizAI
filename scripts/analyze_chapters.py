#!/usr/bin/env python3
"""
Script to analyze novel chapters using an LLM and store results in MongoDB.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from novel_companion.config import settings
from novel_companion.models.mongodb_connection import (
    connect_to_mongodb,
    disconnect_from_mongodb,
    get_novel_by_title,
)
from novel_companion.models.mongodb_models import Chapter
from novel_companion.models.mongodb_operations import ChapterOperations

# --- Configuration ---
NOVEL_TITLE_TO_PROCESS = "Omniscient Reader's Viewpoint"
CHAPTERS_DIRECTORY = Path("data/novels/orv")
PROMPT_TEMPLATE_PATH = Path("prompt_template.txt")
OPENROUTER_API_KEY = settings.openrouter_api_key
OPENROUTER_API_URL = f"{settings.openrouter_base_url}/chat/completions"
LLM_MODEL = settings.deepseek_model

# --- Helper Functions ---

def load_prompt_template() -> str:
    """Loads the prompt template from the specified file."""
    try:
        with open(PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: Prompt template file not found at {PROMPT_TEMPLATE_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading prompt template: {e}")
        sys.exit(1)

def extract_chapter_number_from_filename(filename: str) -> Optional[int]:
    """Extracts chapter number from filename like ch1.md, chapter_01.txt etc."""
    name_part = Path(filename).stem
    parts = name_part.replace('_', '').replace('-', '').lower()
    if parts.startswith("ch"):
        num_str = parts[2:]
        if num_str.isdigit():
            return int(num_str)
    return None

async def get_llm_analysis(prompt: str) -> Optional[Dict[str, Any]]:
    """Sends a prompt to the OpenRouter API and returns the JSON response."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"} # Request JSON output
    }

    async with httpx.AsyncClient(timeout=120.0) as client: # Increased timeout
        try:
            print(f"   Sending request to LLM for analysis (model: {LLM_MODEL})...")
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_json = response.json()
            
            if response_json.get("choices") and response_json["choices"][0].get("message"):
                content_str = response_json["choices"][0]["message"].get("content")
                if content_str:
                    json_substring = None
                    try:
                        # Priority 1: Look for a markdown ```json ... ``` block
                        if content_str.strip().startswith("```json"):
                            start_marker = content_str.find("```json") + 7 # Length of "```json\n"
                            end_marker = content_str.rfind("```")
                            if start_marker != -1 and end_marker != -1 and start_marker < end_marker:
                                json_substring = content_str[start_marker:end_marker].strip()
                                # Try parsing this first specific block
                                analysis_json = json.loads(json_substring)
                                return analysis_json 
                        
                        # Priority 2: If no clear markdown, try to find the first complete JSON object
                        # This handles cases where the JSON might be embedded or followed by other text.
                        json_start_index = content_str.find('{')
                        if json_start_index != -1:
                            # Try to find the matching closing brace for the first opening brace
                            open_braces = 0
                            json_end_index = -1
                            for i in range(json_start_index, len(content_str)):
                                if content_str[i] == '{':
                                    open_braces += 1
                                elif content_str[i] == '}':
                                    open_braces -= 1
                                    if open_braces == 0:
                                        json_end_index = i
                                        break
                            
                            if json_end_index != -1:
                                json_substring = content_str[json_start_index : json_end_index + 1]
                                analysis_json = json.loads(json_substring)
                                return analysis_json

                        # Fallback: If the above fail, use the previous broader extraction (less reliable for mixed content)
                        # This part is less likely to be reached if the above are effective
                        if json_substring is None: # only if not set by markdown block logic
                            json_start_index = content_str.find('{')
                            json_end_index = content_str.rfind('}')
                            if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
                                json_substring = content_str[json_start_index : json_end_index + 1]
                            else: # Last resort, assume content_str itself might be the JSON (after simple stripping)
                                temp_str = content_str.strip()
                                if temp_str.startswith("```json"):
                                    temp_str = temp_str[7:]
                                if temp_str.startswith("```"):
                                    temp_str = temp_str[3:]
                                if temp_str.endswith("```"):
                                    temp_str = temp_str[:-3]
                                json_substring = temp_str.strip()
                        
                        analysis_json = json.loads(json_substring) # Try parsing the derived substring
                        return analysis_json

                    except json.JSONDecodeError as e:
                        error_context = json_substring if json_substring is not None else content_str
                        print(f"❌ Error decoding JSON from LLM response content: {e}")
                        print(f"LLM Raw Content (or attempted part):\n{error_context[:1000]}...")
                        return None
                else:
                    print("❌ LLM response content is empty.")
                    return None
            else:
                print(f"❌ Unexpected LLM response structure: {response_json}")
                return None
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"❌ Request error occurred: {e}")
            return None
        except Exception as e:
            print(f"❌ An unexpected error occurred during LLM call: {e}")
            return None

def populate_main_fields_from_analysis(chapter: Chapter, analysis: Dict[str, Any]):
    """Populates main chapter fields from the detailed analysis_data."""
    try:
        chapter_analysis_data = analysis.get("chapter_analysis", {})
        
        # Summary
        summary_data = chapter_analysis_data.get("summary", {})
        chapter.summary = summary_data.get("concise") or summary_data.get("detailed")
        chapter.key_events = summary_data.get("key_events", [])

        # Characters Mentioned (from character_mapping)
        character_mapping_data = analysis.get("character_mapping", {})
        characters_list = character_mapping_data.get("characters", [])
        chapter.characters_mentioned = [char.get("name") for char in characters_list if char.get("name")]

        # Themes
        themes_data = chapter_analysis_data.get("themes", [])
        chapter.themes = [theme.get("theme") for theme in themes_data if theme.get("theme")]
        
        # Sentiment Score (simplified - can be made more sophisticated)
        sentiment_analysis = chapter_analysis_data.get("sentiment_analysis", {})
        if sentiment_analysis.get("emotional_arc"):
            # Example: average intensity of dominant emotions, or a specific metric
            # For now, let's see if we can get an overall score or a primary emotion's intensity
            # This part might need adjustment based on typical LLM output for sentiment
            overall_tone = sentiment_analysis.get("overall_tone", "")
            # A more robust approach would be to have the LLM provide a direct numerical score
            # For now, we'll leave it None if not directly available or easily calculable
            chapter.sentiment_score = None # Placeholder

    except Exception as e:
        print(f"⚠️ Warning: Could not populate all main fields from analysis for chapter {chapter.title}: {e}")


async def analyze_and_store_chapter(
    novel_id_str: str,
    chapter_number: int,
    chapter_title_prefix: str,
    chapter_content: str,
    prompt_template: str,
    novel_title: str
):
    """Analyzes a single chapter and stores it in MongoDB."""
    print(f"📄 Processing Chapter {chapter_number}: {chapter_title_prefix}...")

    word_count = len(chapter_content.split())
    estimated_reading_time = max(1, word_count // 200) # Assuming 200 WPM

    # Prepare the prompt
    # Placeholders: {{novel_id}}, {{chapter_id}} (will be generated by DB),
    # {{novel_title}}, {{chapter_number}}, {{chapter_title}},
    # {{word_count}}, {{reading_time}}
    # The main content of the chapter needs to be inserted into the prompt.
    # The template expects a JSON output, so we ask the LLM to fill that structure.

    filled_prompt = prompt_template.replace("{{novel_id}}", novel_id_str)
    # chapter_id is generated by MongoDB, so we might not have it for the prompt.
    # We can tell the LLM to leave it as a placeholder or omit it from the prompt if it's only for DB record.
    # Let's assume for now the LLM can handle {{chapter_id}} as a placeholder or we remove it from the prompt if not needed.
    filled_prompt = filled_prompt.replace("{{chapter_id}}", "GENERATED_BY_DB") # Or an empty string
    filled_prompt = filled_prompt.replace("{{novel_title}}", novel_title)
    filled_prompt = filled_prompt.replace("{{chapter_number}}", str(chapter_number))
    filled_prompt = filled_prompt.replace("{{chapter_title}}", f"{chapter_title_prefix} - Chapter {chapter_number}")
    filled_prompt = filled_prompt.replace("{{word_count}}", str(word_count))
    filled_prompt = filled_prompt.replace("{{reading_time}}", str(estimated_reading_time))
    
    # The crucial part: inserting the chapter content.
    # The prompt template should have a clear section where the chapter text goes.
    # Assuming the template's "Input Format" section implies this.
    # We'll prepend the chapter content before the JSON structure request.
    final_prompt = f"Novel Chapter Text:\n\n{chapter_content}\n\n---END OF CHAPTER TEXT---\n\nAnalyze the above chapter and provide the output in the following JSON format. Ensure the entire output is a single valid JSON object as specified in the schema provided in the initial prompt template instructions:\n\n{filled_prompt}"


    print(f"   Prompt prepared. Word count: {word_count}.")

    analysis_json = await get_llm_analysis(final_prompt)

    if not analysis_json:
        print(f"❌ Failed to get LLM analysis for Chapter {chapter_number}. Skipping.")
        return

    print(f"   ✅ LLM analysis received for Chapter {chapter_number}.")
    
    # Create Chapter document
    chapter_data = {
        "novel_id": novel_id_str,
        "title": f"{chapter_title_prefix} - Chapter {chapter_number}", # Consistent title
        "chapter_number": chapter_number,
        "content": chapter_content,
        "word_count": word_count,
        "reading_time_minutes": estimated_reading_time,
        "analysis_data": analysis_json, # Store the full analysis
        "is_processed": True,
        "processing_timestamp": datetime.utcnow()
    }
    
    new_chapter = Chapter(**chapter_data)
    populate_main_fields_from_analysis(new_chapter, analysis_json)
    
    try:
        await ChapterOperations.create_chapter(new_chapter.model_dump(by_alias=True))
        print(f"   💾 Successfully stored Chapter {chapter_number} ({new_chapter.title}) with analysis in MongoDB.")
    except Exception as e:
        print(f"❌ Error storing Chapter {chapter_number} in MongoDB: {e}")


async def main():
    """Main function to orchestrate chapter analysis and storage."""
    print(f"🚀 Starting Chapter Analysis for Novel: {NOVEL_TITLE_TO_PROCESS}")
    
    if not OPENROUTER_API_KEY:
        print("❌ Error: OPENROUTER_API_KEY is not set in environment or config.")
        sys.exit(1)

    prompt_template_content = load_prompt_template()

    await connect_to_mongodb()

    try:
        novel = await get_novel_by_title(NOVEL_TITLE_TO_PROCESS)
        if not novel:
            print(f"❌ Error: Novel '{NOVEL_TITLE_TO_PROCESS}' not found in the database.")
            return
        
        novel_id_str = str(novel.id)
        print(f"📘 Found Novel ID: {novel_id_str} for '{novel.title}'")

        if not CHAPTERS_DIRECTORY.exists() or not CHAPTERS_DIRECTORY.is_dir():
            print(f"❌ Error: Chapters directory not found or is not a directory: {CHAPTERS_DIRECTORY}")
            return

        chapter_files = sorted(
            [f for f in CHAPTERS_DIRECTORY.iterdir() if f.is_file() and f.suffix.lower() in ['.md', '.txt']],
            key=lambda x: extract_chapter_number_from_filename(x.name) or float('inf') # Sort by chapter number
        )
        
        if not chapter_files:
            print(f"🤷 No chapter files found in {CHAPTERS_DIRECTORY}")
            return

        print(f"📚 Found {len(chapter_files)} chapter files to process.")

        for chapter_file in chapter_files:
            chapter_num_from_filename = extract_chapter_number_from_filename(chapter_file.name)
            if chapter_num_from_filename is None:
                print(f"⚠️ Skipping file {chapter_file.name}, could not determine chapter number.")
                continue
            
            # Check if chapter already processed and analyzed
            existing_chapter = await ChapterOperations.get_chapter_by_number(novel_id_str, chapter_num_from_filename)
            if existing_chapter and existing_chapter.is_processed and existing_chapter.analysis_data:
                print(f"ℹ️ Chapter {chapter_num_from_filename} ({existing_chapter.title}) already analyzed. Skipping.")
                continue

            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chapter_title_prefix = novel.title # Use novel title as prefix for chapter title
                
                await analyze_and_store_chapter(
                    novel_id_str=novel_id_str,
                    chapter_number=chapter_num_from_filename,
                    chapter_title_prefix=chapter_title_prefix,
                    chapter_content=content,
                    prompt_template=prompt_template_content,
                    novel_title=novel.title
                )
                print("-" * 30) # Separator for chapters
            except Exception as e:
                print(f"❌ Error processing chapter file {chapter_file.name}: {e}")
            
            # Optional: Add a delay between API calls if needed
            # await asyncio.sleep(1) 

    except Exception as e:
        print(f"❌ An critical error occurred: {e}")
    finally:
        await disconnect_from_mongodb()
        print("✅ Chapter analysis process finished.")

if __name__ == "__main__":
    # For Pydantic/Beanie compatibility with Uvicorn/FastAPI if models are used directly
    if sys.platform == "win32" and sys.version_info >= (3, 8):
         asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main()) 