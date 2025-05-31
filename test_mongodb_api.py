#!/usr/bin/env python3
"""
Comprehensive test script for the MongoDB-based Novel Companion API.
This script tests all endpoints and validates the complete workflow.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.novel_id: Optional[str] = None
        self.chapter_ids: list = []
        
    def log(self, message: str):
        """Print a formatted log message."""
        print(f"🔍 {message}")
        
    def log_success(self, message: str):
        """Print a formatted success message."""
        print(f"✅ {message}")
        
    def log_error(self, message: str):
        """Print a formatted error message."""
        print(f"❌ {message}")
        
    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, files=None) -> Dict[Any, Any]:
        """Make an API request and return the response."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"Request failed for {method} {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.log_error(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    self.log_error(f"Response text: {e.response.text}")
            return {"error": str(e)}
    
    def test_health_check(self):
        """Test if the API server is running."""
        self.log("Testing API health check...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_success("API server is running and serving the frontend")
            else:
                self.log_error(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.log_error(f"Health check failed: {e}")
    
    def test_list_novels(self):
        """Test listing all novels."""
        self.log("Testing novel listing...")
        result = self.make_request("GET", "/api/novels/")
        
        if "error" not in result:
            self.log_success(f"Retrieved {len(result)} novels")
            for novel in result:
                print(f"  📚 {novel.get('title', 'Unknown')} (ID: {novel.get('id', 'Unknown')})")
        else:
            self.log_error("Failed to list novels")
            
        return result
    
    def test_create_novel(self):
        """Test creating a new novel."""
        self.log("Testing novel creation...")
        
        test_content = """Chapter 1: The Hero's Journey
        
        In a land far away, there lived a young hero named Alex who discovered they had magical powers. The journey was just beginning, and many challenges lay ahead. This chapter introduces our protagonist and sets up the world where the adventure will unfold.
        
        Chapter 2: The First Challenge
        
        Alex encountered their first real test when a dragon appeared near the village. Using newly discovered powers, Alex managed to communicate with the dragon and learned that not all dragons are evil. This chapter explores themes of understanding and prejudice.
        
        Chapter 3: The Wise Mentor
        
        An old wizard named Gandalf found Alex and offered to train them. The training was rigorous but essential for the upcoming battles. This chapter focuses on growth, learning, and the importance of mentorship in personal development.
        """
        
        novel_data = {
            "title": "The MongoDB Adventure",
            "author": "API Tester",
            "content": test_content,
            "genre": "Fantasy"
        }
        
        result = self.make_request("POST", "/api/novels/", novel_data)
        
        if "error" not in result and "id" in result:
            self.novel_id = result["id"]
            self.log_success(f"Novel created successfully with ID: {self.novel_id}")
            self.log(f"Title: {result.get('title')}")
            self.log(f"Author: {result.get('author')}")
            self.log(f"Genre: {result.get('genre')}")
        else:
            self.log_error("Failed to create novel")
            
        return result
    
    def test_get_novel(self):
        """Test retrieving a specific novel."""
        if not self.novel_id:
            self.log_error("No novel ID available for testing")
            return
            
        self.log(f"Testing novel retrieval for ID: {self.novel_id}")
        result = self.make_request("GET", f"/api/novels/{self.novel_id}")
        
        if "error" not in result:
            self.log_success("Novel retrieved successfully")
            self.log(f"Title: {result.get('title')}")
            self.log(f"Processing status: {result.get('is_processed')}")
        else:
            self.log_error("Failed to retrieve novel")
            
        return result
    
    def test_get_chapters(self):
        """Test retrieving chapters for a novel."""
        if not self.novel_id:
            self.log_error("No novel ID available for testing")
            return
            
        self.log(f"Testing chapter retrieval for novel: {self.novel_id}")
        
        # Wait a moment for background processing
        time.sleep(2)
        
        result = self.make_request("GET", f"/api/novels/{self.novel_id}/chapters")
        
        if "error" not in result and isinstance(result, list):
            self.chapter_ids = [chapter.get("id") for chapter in result if chapter.get("id")]
            self.log_success(f"Retrieved {len(result)} chapters")
            for i, chapter in enumerate(result):
                print(f"  📄 Chapter {chapter.get('chapter_number', i+1)}: {chapter.get('title', 'Unknown')}")
                print(f"      Word count: {chapter.get('word_count', 0)}")
                print(f"      Processed: {chapter.get('is_processed', False)}")
        else:
            self.log_error("Failed to retrieve chapters")
            
        return result
    
    def test_get_characters(self):
        """Test retrieving characters for a novel."""
        if not self.novel_id:
            self.log_error("No novel ID available for testing")
            return
            
        self.log(f"Testing character retrieval for novel: {self.novel_id}")
        result = self.make_request("GET", f"/api/novels/{self.novel_id}/characters")
        
        if "error" not in result and isinstance(result, list):
            self.log_success(f"Retrieved {len(result)} characters")
            for character in result:
                print(f"  👤 {character.get('name', 'Unknown')}: {character.get('description', 'No description')}")
        else:
            self.log_error("Failed to retrieve characters")
            
        return result
    
    def test_chapter_summarization(self):
        """Test chapter summarization."""
        if not self.chapter_ids:
            self.log_error("No chapter IDs available for testing")
            return
            
        chapter_id = self.chapter_ids[0]
        self.log(f"Testing chapter summarization for chapter: {chapter_id}")
        
        # The summarization endpoint might not require a body, let's try without first
        result = self.make_request("POST", f"/api/chapters/{chapter_id}/summarize")
        
        if "error" not in result:
            self.log_success("Chapter summarization completed")
            self.log(f"Summary: {result.get('summary', 'No summary')[:100]}...")
        else:
            self.log_error("Failed to summarize chapter")
            
        return result
    
    def test_chat(self):
        """Test the chat functionality."""
        if not self.novel_id:
            self.log_error("No novel ID available for testing")
            return
            
        self.log(f"Testing chat functionality for novel: {self.novel_id}")
        
        chat_data = {
            "message": "What are the main themes in this novel and who are the key characters?"
        }
        
        result = self.make_request("POST", f"/api/novels/{self.novel_id}/chat", chat_data)
        
        if "error" not in result and "response" in result:
            self.log_success("Chat response received")
            response_text = result.get("response", "")
            print(f"  🤖 Response (first 200 chars): {response_text[:200]}...")
            
            references = result.get("references", [])
            if references:
                print(f"  📖 References: {len(references)} items")
                
            suggestions = result.get("suggested_questions", [])
            if suggestions:
                print(f"  💭 Suggested questions: {len(suggestions)} items")
        else:
            self.log_error("Failed to get chat response")
            
        return result
    
    def test_file_upload(self):
        """Test file upload functionality."""
        self.log("Testing file upload functionality...")
        
        # Create a test file
        test_content = """Chapter 1: A New Beginning

        This is a test novel uploaded via the API. It contains multiple chapters to test the file upload and processing functionality.

        Chapter 2: The Development

        The second chapter continues the story and provides more content for analysis and processing by the system.

        Chapter 3: The Conclusion

        The final chapter wraps up our test story and ensures we have enough content for proper testing.
        """
        
        files = {
            'file': ('test_upload.txt', test_content, 'text/plain')
        }
        
        data = {
            'title': 'Uploaded Test Novel',
            'author': 'File Upload Tester',
            'genre': 'Test'
        }
        
        result = self.make_request("POST", "/api/upload/", data, files)
        
        if "error" not in result:
            self.log_success("File uploaded successfully")
            uploaded_novel_id = result.get("novel_id")
            if uploaded_novel_id:
                self.log(f"Uploaded novel ID: {uploaded_novel_id}")
        else:
            self.log_error("Failed to upload file")
            
        return result
    
    def run_all_tests(self):
        """Run all API tests in sequence."""
        print("🚀 Starting comprehensive MongoDB API tests...\n")
        
        # Basic connectivity
        self.test_health_check()
        print()
        
        # List existing novels
        self.test_list_novels()
        print()
        
        # Create a new novel
        self.test_create_novel()
        print()
        
        # Test novel retrieval
        self.test_get_novel()
        print()
        
        # Test chapter retrieval
        self.test_get_chapters()
        print()
        
        # Test character retrieval
        self.test_get_characters()
        print()
        
        # Test chapter summarization
        if self.chapter_ids:
            self.test_chapter_summarization()
            print()
        
        # Test chat functionality
        self.test_chat()
        print()
        
        # Test file upload
        self.test_file_upload()
        print()
        
        print("🎉 All tests completed!")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 