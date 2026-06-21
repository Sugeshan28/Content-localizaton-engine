"""
Safety Filter Module for Content Localization Engine

This module provides profanity filtering functionality for multilingual text.
Can be imported and used as a module in other Python projects.

Filtering Strategy:
- All profane words are REPLACED with appropriate synonyms when available
- Words without synonyms are MASKED with asterisks (***)
- Optional pure masking mode via use_synonyms=False parameter

Usage as a module:
    from safety_filter import SafetyFilter
    
    # Initialize
    filter = SafetyFilter(language='hi')
    
    # Filter text (replaces with synonyms)
    clean_text = filter.filter("text with profanity")
    
    # Filter text (pure masking)
    clean_text = filter.filter("text with profanity", use_synonyms=False)

Usage from command line:
    python safety_filter.py input.txt output.txt

Author: Vamsi Krishnan
Project: SIH 2025 - Content Localization Engine
"""

import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

try:
    from better_profanity import profanity
    BETTER_PROFANITY_AVAILABLE = True
except ImportError:
    BETTER_PROFANITY_AVAILABLE = False
    print("Warning: better-profanity not installed. Install with: pip install better-profanity")


@dataclass
class FilterResult:
    """Result of profanity filtering operation"""
    original_text: str
    cleaned_text: str
    profane_words: List[str]
    replacements: Dict[str, str]
    detected_language: str


class SafetyFilter:
    """
    Multilingual profanity filter for English, Hindi, Tamil, and Telugu.
    
    This class provides text filtering functionality with automatic language detection
    and context-aware filtering:
    - By default, replaces profane words with appropriate synonyms
    - Falls back to masking (***) if no synonym is available
    - Optional pure masking mode
    
    Attributes:
        language (str): Target language code ('en', 'hi', 'ta', 'te')
        highly_abusive (dict): Highly offensive words per language
        racial_slurs (dict): Derogatory terms per language
        synonyms (dict): Appropriate replacements
    """
    
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te']
    
    def __init__(self, language: str = 'en', auto_detect: bool = False):
        """
        Initialize the SafetyFilter.
        
        Args:
            language: Language code ('en', 'hi', 'ta', 'te'). Default: 'en'
            auto_detect: If True, automatically detect language from input text
        
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{language}' not supported. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )
        
        self.language = language
        self.auto_detect = auto_detect
        
        # Load better-profanity if available
        if BETTER_PROFANITY_AVAILABLE:
            profanity.load_censor_words()
        
        # Initialize wordlists
        self.highly_abusive = self._load_highly_abusive_words()
        self.racial_slurs = self._load_racial_slurs()
        self.synonyms = self._load_synonyms()
        
        # Add all words to better-profanity for detection
        if BETTER_PROFANITY_AVAILABLE and language in self.highly_abusive:
            all_words = self.highly_abusive.get(language, []) + self.racial_slurs.get(language, [])
            profanity.add_censor_words(all_words)
    
    def _load_highly_abusive_words(self) -> Dict[str, List[str]]:
        """
        Load highly abusive/explicit words.
        These are extreme profanity, sexual explicit terms, etc.
        """
        return {
            "en": [
                # Extreme profanity
                "fuck", "fucking", "shit", "bitch", "asshole", "bastard",
                "dickhead", "prick", "cock", "pussy", "crap", "damn", "hell",
                "ass", "dumbass"
            ],
            "hi": [
                # Highly abusive Hindi words
                "चूतिया", "chutiya", "मादरचोद", "madarchod",
                "बहनचोद", "behenchod", "भोसडीके", "bhosadike",
                "लौडा", "lauda", "लंड", "lund", "गांडू", "gandu",
                "झाटू", "jhatu", "भोसडा", "bhosda", "रांड", "randi",
                "चुतियापा", "chutiyapa", "बकचोद", "bakchod"
            ],
            "ta": [
                # Highly abusive Tamil words
                "புண்டா", "punda", "ஓத்தா", "otha",
                "ஓம்பு", "ombu", "தேவடியா", "thevidiya",
                "குத்தி", "koothi", "பூல்", "pul"
            ],
            "te": [
                # Highly abusive Telugu words
                "పూకు", "pooku", "లండ", "land",
                "బోడు", "bodu", "కూతురు", "kothuru",
                "పూరి", "poori", "lanjakoduku"
            ]
        }
    
    def _load_racial_slurs(self) -> Dict[str, List[str]]:
        """
        Load racial slurs and derogatory terms.
        These include identity-based insults, mild profanity, etc.
        """
        return {
            "en": [
                # Racial/derogatory slurs
                "stupid", "idiot", "fool", "dumb", "moron",
                "retard", "retarded", "imbecile", "jerk", "loser",
                "scum", "trash", "garbage", "worthless", "pathetic"
            ],
            "hi": [
                # Derogatory Hindi terms
                "बेवकूफ़", "बेवकूफ", "bewakoof", "bewakuf",
                "मूर्ख", "गधा", "gadha", "उल्लू", "ullu",
                "हरामी", "harami", "हरामज़ादा", "haramzada",
                "कमीना", "kamina", "कमीने", "kamine",
                "कुत्ता", "kutta", "कुत्ते", "kutte",
                "सुअर", "suar", "बकवास", "bakwas",
                "गाली", "gaali", "गंदा", "ganda", "ब्लडी फूल", "bloody fool"
            ],
            "ta": [
                # Derogatory Tamil terms
                "முட்டாள்", "muttaal", "பைத்தியம்", "paithiyam",
                "கழுதை", "kazhudhai", "நாய்", "naai",
                "பன்னி", "panni", "பண்ணி",
                "loosu", "porukki", "kirukku"
            ],
            "te": [
                # Derogatory Telugu terms
                "మూర్ఖుడు", "moorkhhudu", "వెధవ", "vedava",
                "గాడిదేడు", "gadidhedu", "గోవు", "govu",
                "కుక్క", "kukka", "పంది", "pandi",
                "ద్రోహి", "drohi", "gadu"
            ]
        }
    
    def _load_synonyms(self) -> Dict[str, Dict[str, str]]:
        """Load appropriate synonym replacements for all profane words"""
        return {
            "en": {
                # Synonyms for highly abusive words
                "fuck": "extremely bad", "fucking": "very", "shit": "nonsense",
                "bitch": "difficult person", "asshole": "unpleasant person",
                "bastard": "difficult person", "dickhead": "rude person",
                "prick": "annoying person", "damn": "darn", "hell": "heck",
                "crap": "nonsense", "ass": "fool", "dumbass": "misguided person",
                # Synonyms for derogatory terms
                "stupid": "unwise", "idiot": "inexperienced person",
                "fool": "naive person", "dumb": "uninformed",
                "moron": "confused person", "retard": "challenged person",
                "retarded": "developmentally different", "imbecile": "uninformed person",
                "jerk": "rude person", "loser": "unsuccessful person",
                "scum": "unpleasant person", "trash": "undesirable",
                "garbage": "poor quality", "worthless": "unvalued",
                "pathetic": "unfortunate"
            },
            "hi": {
                # Synonyms for highly abusive Hindi words
                "चूतिया": "मूर्ख", "chutiya": "moorkhh",
                "मादरचोद": "अत्यंत बुरा", "madarchod": "atyant bura",
                "बहनचोद": "अत्यंत बुरा", "behenchod": "atyant bura",
                "भोसडीके": "बुरा व्यक्ति", "bhosadike": "bura vyakti",
                "रांड": "बुरी महिला", "randi": "buri mahila",
                "चुतियापा": "बेकार काम", "chutiyapa": "bekaar kaam",
                "बकचोद": "बकवास करने वाला", "bakchod": "bakwas karne wala",
                # Synonyms for derogatory Hindi terms
                "बेवकूफ़": "अनजान", "बेवकूफ": "अनजान",
                "bewakoof": "anjaan", "bewakuf": "anjaan",
                "मूर्ख": "अज्ञानी", "गधा": "नासमझ", "gadha": "nasamajh",
                "उल्लू": "भोला", "ullu": "bhola",
                "हरामी": "बुरा व्यक्ति", "harami": "bura vyakti",
                "हरामज़ादा": "अविश्वासी व्यक्ति", "haramzada": "avishvaasi vyakti",
                "कमीना": "बुरा व्यक्ति", "kamina": "bura vyakti",
                "कमीने": "बुरे लोग", "kamine": "bure log",
                "कुत्ता": "नीच व्यक्ति", "kutta": "neech vyakti",
                "कुत्ते": "नीच लोग", "kutte": "neech log",
                "सुअर": "अस्वच्छ व्यक्ति", "suar": "asvachh vyakti",
                "बकवास": "बेकार बात", "bakwas": "bekaar baat",
                "गाली": "अपमानजनक शब्द", "gaali": "apmaanjanak shabd",
                "गंदा": "अशुभ", "ganda": "ashubh",
                "ब्लडी फूल": "मूर्ख", "bloody fool": "moorkhh"
            },
            "ta": {
                # Synonyms for highly abusive Tamil words
                "புண்டா": "மோசமானவர்", "punda": "mosamaanavar",
                "ஓத்தா": "மிக மோசம்", "otha": "miga mosam",
                "ஓம்பு": "மிக மோசம்", "ombu": "miga mosam",
                "தேவடியா": "கெட்டவர்", "thevidiya": "kettavar",
                "குத்தி": "கெட்டவர்", "koothi": "kettavar",
                "பூல்": "மோசம்", "pul": "mosam",
                # Synonyms for derogatory Tamil terms
                "முட்டாள்": "அறியாதவர்", "muttaal": "ariyathavar",
                "பைத்தியம்": "குழப்பமானவர்", "paithiyam": "kuzhhappamanavar",
                "கழுதை": "மூடனம்றவர்", "kazhudhai": "mudanamravar",
                "நாய்": "தீயவர்", "naai": "theeyavar",
                "பன்னி": "தீயவர்", "panni": "theeyavar",
                "loosu": "theriyadhavar", "porukki": "kettavar",
                "kirukku": "pizhhaiyaanavar"
            },
            "te": {
                # Synonyms for highly abusive Telugu words
                "పూకు": "చెడ్డది", "pooku": "cheddadi",
                "లండ": "చెడ్డది", "land": "cheddadi",
                "బోడు": "చెడ్డ వ్యక్తి", "bodu": "chedda vyakthi",
                "కూతురు": "చెడ్డది", "kothuru": "cheddadi",
                "పూరి": "చెడ్డది", "poori": "cheddadi",
                "lanjakoduku": "chedda vyakthi",
                # Synonyms for derogatory Telugu terms
                "మూర్ఖుడు": "తెలియని వ్యక్తి", "moorkhhudu": "teliyani vyakthi",
                "వెధవ": "అనుభవం లేని వారు", "vedava": "anubhavam leni vaaru",
                "గాడిదేడు": "మూర్ఖుడు", "gadidhedu": "moorkhhudu",
                "గోవు": "మూఢనంమైన వ్యక్తి", "govu": "mudanamaina vyakthi",
                "కుక్క": "తప్పుడు వ్యక్తి", "kukka": "thappudu vyakthi",
                "పంది": "మూఢనంమైన వ్యక్తి", "pandi": "mudanamaina vyakthi",
                "ద్రోహి": "తప్పు మనసు ఉన్న వ్యక్తి", "drohi": "thappu manasu unna vyakthi",
                "gadu": "chedda vyakthi"
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Auto-detect language from Unicode script"""
        devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        tamil = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        telugu = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
        
        if devanagari > 0:
            return 'hi'
        elif tamil > 0:
            return 'ta'
        elif telugu > 0:
            return 'te'
        return 'en'
    
    def filter(self, text: str, use_synonyms: bool = True) -> str:
        """
        Filter profanity from text (simple interface).
        
        Args:
            text: Input text to filter
            use_synonyms: Replace with synonyms if True, mask with * if False
        
        Returns:
            Cleaned text string
        """
        result = self.filter_detailed(text, use_synonyms)
        return result.cleaned_text
    
    def filter_detailed(self, text: str, use_synonyms: bool = True) -> FilterResult:
        """
        Filter profanity from text.
        
        - If use_synonyms=True: replace with synonyms where available,
          otherwise mask with *****.
        - If use_synonyms=False: mask all profane words.
        
        Args:
            text: Input text to filter
            use_synonyms: Replace with synonyms if True, mask if False
        
        Returns:
            FilterResult object with detailed information
        """
        if not text:
            return FilterResult(text, text, [], {}, self.language)
        
        # Auto-detect language if enabled
        lang = self.detect_language(text) if self.auto_detect else self.language
        
        # Union of all profane words for this language
        all_words = set()
        all_words.update(self.highly_abusive.get(lang, []))
        all_words.update(self.racial_slurs.get(lang, []))
        
        found = []
        lower = text.lower()
        for word in all_words:
            if word.lower() in lower:
                found.append(word)
        
        cleaned = text
        replacements = {}
        
        if use_synonyms:
            # Prefer synonyms; fallback to masking if no synonym exists
            for word in found:
                rep = self._get_synonym(word, lang)
                if rep == word:          # no synonym defined
                    rep = '*' * len(word)
                cleaned = self._replace_word(cleaned, word, rep)
                replacements[word] = rep
        else:
            # Pure masking mode
            if BETTER_PROFANITY_AVAILABLE:
                cleaned = profanity.censor(text)
            for word in found:
                masked = '*' * len(word)
                cleaned = self._replace_word(cleaned, word, masked)
                replacements[word] = masked
        
        return FilterResult(text, cleaned, list(set(found)), replacements, lang)
    
    def _get_synonym(self, word: str, lang: str) -> str:
        """Get appropriate synonym if available; otherwise return original."""
        synonyms = self.synonyms.get(lang, {})
        rep = synonyms.get(word.lower()) or synonyms.get(word)
        return rep if rep else word
    
    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        """Replace word in text while preserving boundaries"""
        import re
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        return pattern.sub(replacement, text)


# Convenience function for quick filtering
def filter_text(text: str, language: str = 'en', use_synonyms: bool = True) -> str:
    """
    Quick profanity filter function.
    
    Args:
        text: Text to filter
        language: Language code ('en', 'hi', 'ta', 'te')
        use_synonyms: Replace with synonyms if True, mask if False
    
    Returns:
        Cleaned text
    """
    filter = SafetyFilter(language=language)
    return filter.filter(text, use_synonyms=use_synonyms)


# Command-line interface
def main():
    """CLI entry point"""
    if len(sys.argv) != 3:
        print("Usage: python safety_filter.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file, output_file = sys.argv[1], sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Filter with auto-detection
    filter = SafetyFilter(auto_detect=True)
    result = filter.filter_detailed(text)
    
    # Create output directory
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.cleaned_text)
    
    print(f"Done: {output_file}")


if __name__ == '__main__':
    main()
