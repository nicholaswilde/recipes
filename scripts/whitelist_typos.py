#!/usr/bin/env python3
import sys
import os
import argparse

# Define constants that can be overridden for testing
DICTIONARY_PATH = "dictionary.txt"
TYPOS_TOML_PATH = "_typos.toml"

def main():
    parser = argparse.ArgumentParser(description="Whitelist words in the spellchecker dictionary and rebuild typos configuration.")
    parser.add_argument("words", nargs="+", help="Word(s) to whitelist")
    
    args = parser.parse_args()
    
    dict_path = globals().get("DICTIONARY_PATH", DICTIONARY_PATH)
    config_path = globals().get("TYPOS_TOML_PATH", TYPOS_TOML_PATH)
    
    # Read existing words
    words = []
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    words.append(word)
                    
    # Add new words
    for w in args.words:
        cleaned_word = w.strip()
        if cleaned_word:
            words.append(cleaned_word)
            
    # Sort and deduplicate
    words = sorted(list(set(words)))
    
    # Write back to dictionary.txt
    with open(dict_path, "w", encoding="utf-8") as f:
        # Keep an empty line at the top if there was one (some dictionaries have it, let's just write words)
        for word in words:
            f.write(f"{word}\n")
            
    print(f"Updated and sorted {dict_path} (total: {len(words)} words).")
    
    # Trigger typos configuration rebuild
    # Import generate_typos_config dynamically and override its paths
    try:
        import generate_typos_config
    except ImportError:
        # Fallback if running via pytest/sys.path setup
        import importlib.util
        spec = importlib.util.spec_from_file_location("generate_typos_config", os.path.join(os.path.dirname(__file__), "generate_typos_config.py"))
        generate_typos_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generate_typos_config)
        
    generate_typos_config.DICTIONARY_PATH = dict_path
    generate_typos_config.TYPOS_TOML_PATH = config_path
    generate_typos_config.main()
    
    print("Spellchecker configuration successfully regenerated.")

if __name__ == "__main__":
    main()
