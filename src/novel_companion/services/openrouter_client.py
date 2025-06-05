"""
OpenRouter client service for DeepSeek R1 integration
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

from ..config import settings


class OpenRouterClient:
    """OpenRouter API client for DeepSeek R1"""
    
    def __init__(self):
        """Initialize the OpenRouter client"""
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.deepseek_model
        
        # Initialize OpenAI client with OpenRouter settings
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    async def generate_chapter_summary(
        self, 
        chapter_content: str, 
        chapter_title: str,
        summary_length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate an intelligent chapter summary using DeepSeek R1
        """
        
        length_instructions = {
            "short": "Provide a concise 2-3 sentence summary",
            "medium": "Provide a detailed paragraph summary (4-6 sentences)",
            "long": "Provide a comprehensive summary with multiple paragraphs"
        }
        
        prompt = f"""
        You are an expert literary analyst. Please analyze the following chapter and provide:

        1. A {summary_length} summary following this instruction: {length_instructions.get(summary_length, length_instructions["medium"])}
        2. A list of key events (3-5 main plot points)
        3. A list of characters mentioned in this chapter

        Chapter Title: {chapter_title}
        
        Chapter Content:
        {chapter_content}

        Please format your response as a JSON object with the following structure:
        {{
            "summary": "Your summary here",
            "key_events": ["Event 1", "Event 2", "Event 3"],
            "characters_mentioned": ["Character 1", "Character 2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "summary": content,
                    "key_events": [],
                    "characters_mentioned": []
                }
                
        except Exception as e:
            raise Exception(f"Error generating chapter summary: {str(e)}")
    
    async def extract_characters(self, novel_content: str, novel_title: str) -> List[Dict[str, Any]]:
        """Extract characters from the novel using AI analysis"""
        
        prompt = f"""
        You are an expert literary analyst specializing in character analysis. 
        Please analyze the following novel and extract all significant characters.

        For each character, provide:
        1. Name
        2. Character type (protagonist, antagonist, supporting, minor)
        3. Brief description (2-3 sentences)
        4. Key traits (list of 3-5 traits)
        5. Relationships with other characters

        Novel Title: {novel_title}
        
        Novel Content:
        {novel_content[:8000]}
        
        Please format your response as a JSON array of character objects:
        [
            {{
                "name": "Character Name",
                "character_type": "protagonist",
                "description": "Character description",
                "key_traits": ["trait1", "trait2", "trait3"],
                "relationships": ["relationship1", "relationship2"]
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                characters = json.loads(content)
                return characters if isinstance(characters, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            raise Exception(f"Error extracting characters: {str(e)}")
    
    async def chat_about_story(
        self, 
        question: str, 
        novel_context: str, 
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Interactive chat about the story using DeepSeek R1"""
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": f"""
                You are an intelligent reading companion AI. You help readers understand and discuss novels.
                You have access to the following novel content for reference:
                
                {novel_context[:6000]}
                
                Guidelines:
                - Provide helpful, insightful responses about the story
                - Reference specific parts of the text when relevant
                - Suggest related questions that might interest the reader
                - Be conversational and engaging
                - If you're not sure about something, say so
                """
            }
        ]
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                messages.append(msg)
        
        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            return {
                "response": content,
                "references": [],
                "suggested_questions": []
            }
            
        except Exception as e:
            raise Exception(f"Error in story chat: {str(e)}")


# Global client instance
openrouter_client = OpenRouterClient() 