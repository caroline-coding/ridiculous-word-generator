#!/usr/bin/env python3
"""
Generate obscure words/phrases for 20 Questions using the Anthropic API.
"""

import anthropic
import json
import os
import sys
import time

client = anthropic.Anthropic()

OUTPUT_FILE = "words.json"

CATEGORIES = [
    {
        "name": "famous people",
        "examples": "Harvey Milk, Tony Curtis, Cormac McCarthy",
        "guidance": "Historical figures, politicians, actors, authors - recognizable but not A-list celebrities",
        "count": 150
    },
    {
        "name": "fictional characters or mythological figures",
        "examples": "John Galt, Cerberus",
        "guidance": "Characters from books, mythology, movies - known to well-read people",
        "count": 100
    },
    {
        "name": "brands and companies",
        "examples": "Boost Mobile, Ralph Lauren",
        "guidance": "Real brands people have heard of, but not the biggest like Apple or Nike",
        "count": 100
    },
    {
        "name": "video games",
        "examples": "Tears of the Kingdom",
        "guidance": "Popular games that gamers would know, various eras",
        "count": 80
    },
    {
        "name": "TV shows",
        "examples": "Neon Genesis Evangelion, Meet the Press, I Love Lucy",
        "guidance": "Shows from various decades that people have heard of",
        "count": 100
    },
    {
        "name": "locations",
        "examples": "Upper Peninsula, Kyrgyzstan",
        "guidance": "Real places - countries, regions, cities that are real but not super common",
        "count": 120
    },
    {
        "name": "musicians and bands",
        "examples": "Megadeth, Jason Mraz",
        "guidance": "Real musicians people have heard of, not the absolute biggest stars",
        "count": 100
    },
    {
        "name": "abstract or obscure nouns",
        "examples": "plethora, melody, morass, silhouette",
        "guidance": "Real English words that educated people would know",
        "count": 150
    },
    {
        "name": "abstract or obscure verbs",
        "examples": "obfuscate, inform, orient, convert, circulate",
        "guidance": "Real verbs, some common, some less common but still known",
        "count": 100
    },
    {
        "name": "abstract or obscure adjectives",
        "examples": "spurious",
        "guidance": "Real adjectives that would be in a good vocabulary",
        "count": 80
    },
    {
        "name": "archaic or old-fashioned expressions",
        "examples": "jeepers",
        "guidance": "Old-timey words and expressions people would recognize",
        "count": 80
    },
    {
        "name": "slang phrases and idioms",
        "examples": "big house, gut check, rickroll, eeny meeny miny moe",
        "guidance": "Common slang and expressions people use or have heard",
        "count": 100
    },
    {
        "name": "obscure things and objects",
        "examples": "polliwog, bivouac, cummerbund, pole vault, roustabout",
        "guidance": "Real things that are tricky to guess but people know what they are",
        "count": 200
    },
    {
        "name": "foreign words used in English",
        "examples": "gris-gris, bento, ruble, matzoh",
        "guidance": "Foreign words that English speakers encounter",
        "count": 100
    },
    {
        "name": "philosophical concepts",
        "examples": "theodicy, Fermi paradox, trolley problem, transcendentalism",
        "guidance": "Concepts educated people would have heard of",
        "count": 80
    },
    {
        "name": "scientific terms",
        "examples": "vernal equinox, chloroform",
        "guidance": "Scientific terms that regular people know, not super technical jargon",
        "count": 100
    },
    {
        "name": "food and culinary terms",
        "examples": "prosciutto, ratatouille, julienne",
        "guidance": "Foods and cooking terms people encounter",
        "count": 80
    },
    {
        "name": "sports terms",
        "examples": "triple axel, penalty kick, birdie",
        "guidance": "Sports terms and moves people have heard of",
        "count": 80
    },
    {
        "name": "occupations",
        "examples": "longshoreman, actuary, sommelier",
        "guidance": "Real jobs that people know exist",
        "count": 80
    },
    {
        "name": "music and art terms",
        "examples": "crescendo, impressionism, staccato",
        "guidance": "Terms from music and art that cultured people know",
        "count": 60
    },
]

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

def generate_words_batch(category, count, existing_words):
    sample_existing = list(existing_words)[:100] if existing_words else []
    
    prompt = f"""Generate exactly {count} words or short phrases for the category: {category['name']}

EXAMPLES of the right level: {category['examples']}
Guidance: {category['guidance']}

These are for a 20 Questions game. They should be:
- REAL things (not made up)
- Recognizable to educated adults (not super obscure)
- But still tricky to guess with yes/no questions
- Similar difficulty level to the examples above

Keep phrases to 3 words or less.

AVOID these already-used words: {', '.join(sample_existing) if sample_existing else 'none yet'}

Return ONLY a JSON array of strings:
["word1", "word2", "word3", ...]"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        words = json.loads(text)
        return words
    except Exception as e:
        flush_print(f"  Error: {e}")
        return []

def load_existing_words():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    return []

def save_words(words):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(words, f, indent=2)

def main():
    flush_print("Ridiculous Word Generator")
    flush_print("=" * 50)
    
    # Start fresh
    all_words = []
    existing_set = set()
    
    flush_print(f"Starting fresh")
    
    total_target = sum(cat['count'] for cat in CATEGORIES)
    flush_print(f"Target: {total_target} words across {len(CATEGORIES)} categories\n")
    
    for category in CATEGORIES:
        flush_print(f"[{category['name'][:50]}]: {category['count']} words...")
        
        words = generate_words_batch(category, category['count'], existing_set)
        
        new_words = []
        for word in words:
            if word.lower() not in existing_set:
                new_words.append(word)
                existing_set.add(word.lower())
        
        all_words.extend(new_words)
        save_words(all_words)
        
        flush_print(f"  +{len(new_words)} words (total: {len(all_words)})")
        time.sleep(0.3)
    
    flush_print("\n" + "=" * 50)
    flush_print(f"Complete! Total: {len(all_words)} words")
    flush_print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
