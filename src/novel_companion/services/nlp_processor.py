"""
NLP processing service for Novel Companion AI
"""

import re
import spacy
from typing import List, Dict, Any, Tuple
import networkx as nx
from collections import defaultdict, Counter

from ..config import settings


class NLPProcessor:
    """Natural Language Processing service for novel analysis"""
    
    def __init__(self):
        """Initialize the NLP processor"""
        try:
            self.nlp = spacy.load(settings.spacy_model)
        except OSError:
            # Fallback to a basic processor if spacy model not available
            print(f"Warning: spaCy model '{settings.spacy_model}' not found. Using basic processing.")
            self.nlp = None
    
    def split_into_chapters(self, content: str, novel_title: str) -> List[Dict[str, Any]]:
        """
        Split novel content into chapters
        
        Args:
            content: Full novel text
            novel_title: Title of the novel
        
        Returns:
            List of chapter dictionaries with title, content, and chapter number
        """
        chapters = []
        
        # Common chapter patterns
        chapter_patterns = [
            r'\bChapter\s+(\d+|[IVXLCDM]+)\b',  # Chapter 1, Chapter I
            r'\bCh\.\s+(\d+)\b',                # Ch. 1
            r'^\s*(\d+)\s*$',                   # Just a number on its own line
            r'\b(\d+)\.\s',                     # 1. at start of line
        ]
        
        # Try each pattern
        for pattern in chapter_patterns:
            splits = re.split(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
            if len(splits) > 3:  # Found meaningful splits
                break
        else:
            # No chapter markers found, split by length
            return self._split_by_length(content, novel_title)
        
        # Process the splits
        current_chapter = 1
        for i in range(1, len(splits), 2):  # Skip the first empty split
            if i + 1 < len(splits):
                chapter_content = splits[i + 1].strip()
                
                if len(chapter_content) > 100:  # Minimum chapter length
                    # Extract title from the beginning of the chapter
                    title = self._extract_chapter_title(chapter_content, current_chapter)
                    
                    chapters.append({
                        "title": title,
                        "content": chapter_content,
                        "chapter_number": current_chapter
                    })
                    current_chapter += 1
        
        return chapters if chapters else self._split_by_length(content, novel_title)
    
    def _split_by_length(self, content: str, novel_title: str) -> List[Dict[str, Any]]:
        """Split content by length if no chapter markers found"""
        words = content.split()
        words_per_chapter = max(2000, len(words) // 10)  # Aim for ~10 chapters
        
        chapters = []
        for i in range(0, len(words), words_per_chapter):
            chapter_words = words[i:i + words_per_chapter]
            chapter_content = ' '.join(chapter_words)
            
            if len(chapter_content) > 100:
                chapters.append({
                    "title": f"Part {len(chapters) + 1}",
                    "content": chapter_content,
                    "chapter_number": len(chapters) + 1
                })
        
        return chapters
    
    def _extract_chapter_title(self, content: str, chapter_number: int) -> str:
        """Extract or generate chapter title"""
        # Look for a title in the first few lines
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and not line.lower().startswith('chapter'):
                # Check if it looks like a title (short, possibly capitalized)
                if len(line.split()) <= 8:
                    return line
        
        # Default chapter title
        return f"Chapter {chapter_number}"
    
    def extract_named_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text using spaCy
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with entity types and their occurrences
        """
        if not self.nlp:
            return self._basic_entity_extraction(text)
        
        doc = self.nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Filter out common false positives
                if len(ent.text) > 2 and not ent.text.lower() in ['he', 'she', 'it', 'they']:
                    entities["PERSON"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:  # Geopolitical entities, locations
                entities["LOCATION"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["ORGANIZATION"].append(ent.text)
        
        # Remove duplicates and sort by frequency
        for entity_type in entities:
            entity_counts = Counter(entities[entity_type])
            entities[entity_type] = [entity for entity, count in entity_counts.most_common()]
        
        return dict(entities)
    
    def _basic_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Basic entity extraction without spaCy"""
        # Simple capitalized word extraction for names
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Filter common words and keep potential names
        common_words = {'The', 'This', 'That', 'There', 'Then', 'When', 'Where', 'What', 'Who', 'How', 'Why'}
        potential_names = [word for word in words if word not in common_words]
        
        # Count occurrences and keep frequent ones
        name_counts = Counter(potential_names)
        frequent_names = [name for name, count in name_counts.most_common(20) if count > 1]
        
        return {"PERSON": frequent_names}
    
    def analyze_character_relationships(self, text: str, characters: List[str]) -> Dict[str, Any]:
        """
        Analyze relationships between characters based on text co-occurrence
        
        Args:
            text: Full text to analyze
            characters: List of character names
        
        Returns:
            Dictionary with relationship analysis and network data
        """
        if not characters:
            return {"relationships": [], "network": {}}
        
        # Create relationship network
        G = nx.Graph()
        
        # Add characters as nodes
        for char in characters:
            G.add_node(char)
        
        # Analyze text in chunks to find co-occurrences
        sentences = self._split_into_sentences(text)
        
        # Track character co-occurrences
        cooccurrences = defaultdict(int)
        
        for sentence in sentences:
            sentence_chars = []
            for char in characters:
                if char.lower() in sentence.lower():
                    sentence_chars.append(char)
            
            # Create edges for characters appearing in the same sentence
            for i, char1 in enumerate(sentence_chars):
                for char2 in sentence_chars[i+1:]:
                    if char1 != char2:
                        pair = tuple(sorted([char1, char2]))
                        cooccurrences[pair] += 1
        
        # Add edges to graph with weights
        relationships = []
        for (char1, char2), weight in cooccurrences.items():
            if weight > 1:  # Only include significant relationships
                G.add_edge(char1, char2, weight=weight)
                relationships.append({
                    "source": char1,
                    "target": char2,
                    "strength": weight,
                    "relationship_type": self._infer_relationship_type(weight)
                })
        
        # Generate network data for visualization
        network_data = {
            "nodes": [{"id": char, "label": char} for char in characters],
            "edges": [
                {
                    "source": rel["source"],
                    "target": rel["target"],
                    "weight": rel["strength"]
                }
                for rel in relationships
            ]
        }
        
        return {
            "relationships": relationships,
            "network": network_data
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if self.nlp:
            doc = self.nlp(text)
            return [sent.text for sent in doc.sents]
        else:
            # Basic sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _infer_relationship_type(self, strength: int) -> str:
        """Infer relationship type based on co-occurrence strength"""
        if strength > 10:
            return "very_close"
        elif strength > 5:
            return "close"
        elif strength > 2:
            return "acquainted"
        else:
            return "mentioned_together"
    
    def extract_themes_keywords(self, text: str) -> List[str]:
        """
        Extract potential themes and keywords from text
        
        Args:
            text: Text to analyze
        
        Returns:
            List of potential theme keywords
        """
        if not self.nlp:
            return self._basic_keyword_extraction(text)
        
        doc = self.nlp(text)
        
        # Extract meaningful tokens (nouns, adjectives, significant verbs)
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 3):
                keywords.append(token.lemma_.lower())
        
        # Count and return most frequent keywords
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(20)]
    
    def _basic_keyword_extraction(self, text: str) -> List[str]:
        """Basic keyword extraction without spaCy"""
        # Simple word frequency analysis
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        word_counts = Counter(filtered_words)
        
        return [word for word, count in word_counts.most_common(20)]


# Global processor instance
nlp_processor = NLPProcessor() 