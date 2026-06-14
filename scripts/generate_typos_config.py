#!/usr/bin/env python3
import os

DICTIONARY_PATH = "dictionary.txt"
TYPOS_TOML_PATH = "_typos.toml"

def main():
    dict_path = globals().get("DICTIONARY_PATH", DICTIONARY_PATH)
    config_path = globals().get("TYPOS_TOML_PATH", TYPOS_TOML_PATH)
    
    exclusions = [
        "docs/assets/images/**",
        "conductor/**",
        "*.jpg",
        "*.png",
        "*.gif",
        "*.webp",
        "*.ico",
    ]
    
    words = []
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith("#"):
                    words.append(word)
    
    # Sort and deduplicate words
    words = sorted(list(set(words)))
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("[files]\n")
        f.write("extend-exclude = [\n")
        for exc in exclusions:
            f.write(f'  "{exc}",\n')
        f.write("]\n\n")
        
        f.write("[default.extend-words]\n")
        for word in words:
            # Escape double quotes just in case
            escaped_word = word.replace('"', '\\"')
            # Set word = "word" to whitelist it in typos
            f.write(f'"{escaped_word}" = "{escaped_word}"\n')
            
    print(f"Generated {config_path} with {len(words)} whitelisted words.")

if __name__ == "__main__":
    main()
