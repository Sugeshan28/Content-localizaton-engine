"""
Safety layer class for text profanity filtering.
Uses better-profanity and simple synonym logic to mask/replace abusive words.

Usage:
    python safety_layer_text.py <input_file_path> <output_file_path>
    
Example:
    python safety_layer_text.py p_text.txt output/cleaned.txt
"""

import sys
import os
from dataclasses import dataclass
from typing import Dict, List

from better_profanity import profanity


@dataclass
class ProfanityFilterResult:
    original_text: str
    cleaned_text: str
    profane_words: List[str]
    replacements: Dict[str, str]
    detected_language: str


class SafetyLayer:
    def __init__(self, language: str = "en") -> None:
        self.language = language
        profanity.load_censor_words()

        # Expanded dictionaries with comprehensive profanity words
        self.custom_words: Dict[str, List[str]] = {
            "en": [
                # Common profanity
                "stupid", "idiot", "fool", "dumb", "moron", "dumbass", "ass",
                "bastard", "bitch", "damn", "hell", "crap", "shit", "fuck",
                "fucking", "asshole", "dickhead", "prick", "cock", "pussy",
                "retard", "retarded", "imbecile", "jerk", "loser", "scum",
                "trash", "garbage", "worthless", "pathetic"
            ],
            "hi": [
                # Devanagari script
                "बेवकूफ़", "बेवकूफ", "मूर्ख", "गधा", "उल्लू", "ब्लडी फूल",
                "चूतिया", "हरामी", "हरामज़ादा", "कमीना", "कमीने", "कुत्ता", "कुत्ते",
                "मादरचोद", "बहनचोद", "भोसडीके", "लौडा", "लंड",
                "गांडू", "झाटू", "भोसडा", "रांड", "सुअर",
                "चुतियापा", "बकवास", "बकचोद", "गाली", "गंदा",
                # Romanized/Hinglish
                "bewakoof", "bewakuf", "gadha", "ullu", "bloody fool",
                "chutiya", "harami", "haramzada", "kamina", "kamine",
                "kutta", "kutte", "madarchod", "behenchod", "bhosadike",
                "lauda", "lund", "gandu", "jhatu", "bhosda", "randi",
                "suar", "chutiyapa", "bakwas", "bakchod", "gaali", "ganda"
            ],
            "ta": [
                # Tamil script
                "முட்டாள்", "பைத்தியம்", "கழுதை", "நாய்",
                "புண்டா", "ஓத்தா", "ஓம்பு", "தேவடியா",
                "குத்தி", "பன்னி", "பூல்", "பண்ணி",
                # Romanized Tamil
                "muttaal", "paithiyam", "kazhudhai", "naai", "punda",
                "otha", "ombu", "thevidiya", "koothi", "panni", "pul", "panni",
                "loosu", "porukki", "kirukku"
            ],
            "te": [
                # Telugu script
                "మూర్ఖుడు", "వెధవ", "గాడిదేడు", "గోవు",
                "కుక్క", "పంది", "పూకు", "ద్రోహి",
                "లండ", "బోడు", "కూతురు", "పూరి",
                # Romanized Telugu
                "moorkhhudu", "vedava", "gadidhedu", "govu", "kukka",
                "pandi", "pooku", "drohi", "land", "bodu", "kothuru", "poori",
                "gadu", "lanjakoduku"
            ]
        }
        
        self.synonyms: Dict[str, Dict[str, str]] = {
            "en": {
                # Milder/appropriate replacements
                "stupid": "unwise",
                "idiot": "inexperienced person",
                "fool": "naive person",
                "dumb": "uninformed",
                "moron": "confused person",
                "dumbass": "misguided individual",
                "bastard": "difficult person",
                "damn": "darn",
                "hell": "heck",
                "crap": "nonsense",
                "jerk": "rude person",
                "loser": "unsuccessful person",
                "scum": "unpleasant person",
                "trash": "worthless",
                "garbage": "poor quality",
                "pathetic": "unfortunate"
            },
            "hi": {
                # Devanagari replacements
                "बेवकूफ़": "अनजान",
                "बेवकूफ": "अनजान",
                "मूर्ख": "अज्ञानी",
                "गधा": "नासमझ",
                "उल्लू": "भोला",
                "ब्लडी फूल": "मूर्ख",
                "कमीना": "बुरा व्यक्ति",
                "कमीने": "बुरे लोग",
                "कुत्ता": "नीच व्यक्ति",
                "कुत्ते": "नीच लोग",
                "बकवास": "बेकार बात",
                "गाली": "अपमानजनक शब्द",
                "गंदा": "अशुभ",
                # Romanized replacements
                "bewakoof": "anjaan",
                "bewakuf": "anjaan",
                "gadha": "nasamajh",
                "ullu": "bhola",
                "bloody fool": "moorkhh",
                "kamina": "bura vyakti",
                "kamine": "bure log",
                "kutta": "neech vyakti",
                "kutte": "neech log",
                "bakwas": "bekaar baat",
                "gaali": "apmaanjanak shabd",
                "ganda": "ashubh"
            },
            "ta": {
                # Tamil replacements
                "முட்டாள்": "அறியாதவர்",
                "பைத்தியம்": "குழப்பமானவர்",
                "கழுதை": "மூடனம்றவர்",
                "நாய்": "தீயவர்",
                "குத்தி": "தீயவர்",
                "muttaal": "ariyathavar",
                "paithiyam": "kuzhhappamanavar",
                "kazhudhai": "mudanamravar",
                "naai": "theeyavar",
                "loosu": "theriyadhavar",
                "porukki": "kettavar",
                "kirukku": "pizhhaiyaanavar"
            },
            "te": {
                # Telugu replacements
                "మూర్ఖుడు": "తెలియని వ్యక్తి",
                "వెధవ": "అనుభవం లేని వారు",
                "గాడిదేడు": "మూర్ఖుడు",
                "గోవు": "మూఢనంమైన వ్యక్తి",
                "కుక్క": "తప్పుడు వ్యక్తి",
                "పంది": "మూఢనంమైన వ్యక్తి",
                "ద్రోహి": "తప్పు మనసు ఉన్న వ్యక్తి",
                "moorkhhudu": "teliyani vyakthi",
                "vedava": "anubhavam leni vaaru",
                "gadidhedu": "moorkhhudu",
                "govu": "mudanamaina vyakthi",
                "kukka": "thappudu vyakthi",
                "pandi": "mudanamaina vyakthi",
                "drohi": "thappu manasu unna vyakthi",
                "gadu": "chedda vyakthi"
            }
        }

        if language in self.custom_words:
            profanity.add_censor_words(self.custom_words[language])

    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on Unicode script ranges.
        Returns 'en', 'hi', 'ta', or 'te'.
        """
        # Count characters from each script
        devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')  # Hindi
        tamil = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')  # Tamil
        telugu = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')  # Telugu
        
        # Return language with highest character count
        if devanagari > 0:
            return 'hi'
        elif tamil > 0:
            return 'ta'
        elif telugu > 0:
            return 'te'
        else:
            return 'en'  # Default to English

    def profanity_filter_text(self, text: str, use_synonyms: bool = True) -> ProfanityFilterResult:
        if not text:
            return ProfanityFilterResult(text, text, [], {}, self.language)

        found: List[str] = []
        lower = text.lower()
        for w in self.custom_words.get(self.language, []):
            if w.lower() in lower:
                found.append(w)

        cleaned = text
        replacements: Dict[str, str] = {}

        if use_synonyms:
            for w in found:
                rep = self._get_replacement(w)
                cleaned = self._replace_word(cleaned, w, rep)
                replacements[w] = rep
        else:
            cleaned = profanity.censor(text)
            for w in found:
                replacements[w] = "*" * len(w)

        return ProfanityFilterResult(text, cleaned, list(set(found)), replacements, self.language)

    def _get_replacement(self, word: str) -> str:
        m = self.synonyms.get(self.language, {})
        rep = m.get(word.lower()) or m.get(word)  # simple lookup
        return rep if rep else "*" * len(word)

    def _replace_word(self, text: str, word: str, replacement: str) -> str:
        import re

        pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)

        def _m(mo):
            return replacement

        return pattern.sub(_m, text)


def main():
    """
    Command-line interface for safety_layer_text.
    """
    if len(sys.argv) != 3:
        print("Usage: python safety_layer_text.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Read input text
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Auto-detect language
    temp_layer = SafetyLayer()
    detected_lang = temp_layer.detect_language(text)
    
    # Initialize with detected language
    safety = SafetyLayer(language=detected_lang)
    
    # Filter text
    result = safety.profanity_filter_text(text, use_synonyms=True)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Write output - ADD EXPLICIT FLUSH
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.cleaned_text)
            f.flush()  # Force write to disk
        # Verify file was written
        if os.path.exists(output_file):
            print(f"Done: {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()