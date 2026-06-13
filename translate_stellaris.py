import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
import codecs
import arabic_reshaper
from bidi.algorithm import get_display

# Initialize Arabic Reshaper
# Stellaris uses standard TrueType fonts for localized text.
reshaper = arabic_reshaper.ArabicReshaper(
    arabic_reshaper.config_for_true_type_font(
        "C:\\Windows\\Fonts\\arial.ttf",
        arabic_reshaper.ENABLE_ALL_LIGATURES
    )
)

# Global cache for translations
cache = {}
cache_file = "translation_cache.json"

def load_cache():
    global cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"[CACHE] Loaded {len(cache)} translations from cache.")
        except Exception as e:
            print(f"[CACHE WARN] Could not load cache: {e}. Starting fresh.")
    else:
        print("[CACHE] No cache file found. Starting fresh.")

def save_cache():
    temp_path = cache_file + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
        if os.path.exists(temp_path):
            os.replace(temp_path, cache_file)
    except Exception as e:
        print(f"[CACHE ERROR] Failed to save cache: {e}")

def contains_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def translate_text(text, from_lang='en', to_lang='ar'):
    stripped = text.strip()
    if not stripped:
        return text
    
    # Check cache first
    if stripped in cache:
        return cache[stripped]
    
    # If the text has no alphabetical characters, don't translate
    if not re.search(r'[a-zA-Z]', stripped):
        cache[stripped] = stripped
        return stripped

    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" + from_lang + "&tl=" + to_lang + "&dt=t&q=" + urllib.parse.quote(stripped)
    
    max_retries = 3
    sleep_time = 2.0
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                translated = "".join([segment[0] for segment in data[0] if segment[0]])
                
                # Save to cache
                cache[stripped] = translated
                return translated
        except Exception as e:
            print(f"\n[WARN] Translation attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(sleep_time)
                sleep_time *= 2
            else:
                return None

# Helper to identify tags
def is_tag(item):
    if item.startswith("§"):
        return True
    if item.startswith("[") and item.endswith("]"):
        return True
    if item.startswith("£") and item.endswith("£"):
        return True
    if item in ("\\n", "\\t", '\\"'):
        return True
    return False

# Group colored segments so that color formatting wraps the reshaped words properly
def group_colored_segments(parts):
    grouped = []
    i = 0
    while i < len(parts):
        part = parts[i]
        # Match color starts (e.g. §H, §Y, §S, etc.) but not the close tag §!
        if part.startswith("§") and not part.endswith("!"):
            color_tag = part
            content_parts = []
            i += 1
            # Collect until closing §!
            while i < len(parts) and parts[i] != "§!":
                content_parts.append(parts[i])
                i += 1
            
            # Recurse process the content inside the color block
            processed_content = process_parts_list(content_parts)
            grouped.append(f"{color_tag}{processed_content}§!")
            if i < len(parts) and parts[i] == "§!":
                i += 1
        else:
            grouped.append(part)
            i += 1
    return grouped

def process_parts_list(parts):
    # Group any wrapped/colored segments to keep style tags bound to their text
    grouped = group_colored_segments(parts)
    
    processed = []
    for item in grouped:
        if is_tag(item):
            processed.append(item)
        elif contains_arabic(item):
            # Fix translation errors like "Ruler" -> "مسطرة" before shaping
            fixed_item = item
            fixed_item = fixed_item.replace("المسطرة", "الحاكم")
            fixed_item = fixed_item.replace("مسطرة", "حاكم")
            fixed_item = fixed_item.replace("المساطر", "الحكام")
            fixed_item = fixed_item.replace("مساطر", "حكام")
            
            # Shape Arabic text and reverse it for LTR compatibility
            reshaped = reshaper.reshape(fixed_item)
            bidi_text = get_display(reshaped)
            processed.append(bidi_text)
        else:
            processed.append(item)
            
    # Reverse the order of processed tokens so LTR renderer draws RTL sentence sequence correctly
    processed.reverse()
    return "".join(processed)

def process_value(value):
    if not value or not value.strip():
        return value
        
    if contains_arabic(value):
        return value

    # Stellaris tag regex patterns:
    # 1. Color codes: §H, §Y, §S, §g, §!
    # 2. Variables in brackets: [Root.GetName], [event_target:...]
    # 3. Icon tags: £energy£
    # 4. Escape characters: \n, \t, \"
    tag_regex = re.compile(
        r'(§[a-zA-Z0-9_!]|\\[nt"]|\[[^\]]+\]|£[^£]+£)'
    )
    
    parts = tag_regex.split(value)
    
    original_tags = {}
    placeholders_parts = []
    
    # Replace tags with safe placeholders for translation
    placeholder_count = 0
    for idx, part in enumerate(parts):
        if idx % 2 == 1: # It is a matched tag
            placeholder = f"XYZT_{placeholder_count}XYZT"
            original_tags[placeholder] = part
            placeholders_parts.append(placeholder)
            placeholder_count += 1
        else:
            placeholders_parts.append(part)
            
    text_to_translate = "".join(placeholders_parts)
    
    # Check cache/Translate using standard key format
    cache_key = re.sub(r'XYZT_(\d+)XYZT', r'XYZT_\1', text_to_translate)
    translated_text = translate_text(cache_key)
    if not translated_text:
        print(f"\n[ERROR] Failed to translate: '{text_to_translate[:40]}...'")
        return value # Fallback
        
    # Standardize spaces in placeholders to standard format (e.g. XYZT_0)
    translated_text = re.sub(r'[xX][yY][zZ][tT]\s*_\s*(\d+)', r'XYZT_\1', translated_text)
    # Convert all standard formats to collision-proof format (XYZT_0XYZT)
    translated_text = re.sub(r'XYZT_(\d+)', r'XYZT_\1XYZT', translated_text)
    
    # Split the translated text by placeholders again
    split_regex = re.compile(r'(XYZT_\d+XYZT)')
    trans_parts = split_regex.split(translated_text)
    
    # Reassemble with original tags mapping
    reassembled_parts = []
    for idx, part in enumerate(trans_parts):
        if idx % 2 == 1: # It is a placeholder
            original_tag = original_tags.get(part, part)
            reassembled_parts.append(original_tag)
        else:
            reassembled_parts.append(part)
            
    # Process spelling shaping and bidi layout
    return process_parts_list(reassembled_parts)

def parse_line(line):
    line_stripped = line.rstrip('\r\n')
    
    # Language header (e.g. l_english:)
    if line_stripped.strip().endswith(':'):
        hdr = line_stripped.strip()[:-1]
        if hdr.startswith('l_'):
            return ('header', hdr, line)
            
    # Find first colon
    colon_idx = line_stripped.find(':')
    if colon_idx == -1:
        return ('other', line, None)
        
    key = line_stripped[:colon_idx].strip()
    # If key starts with # it is a comment line
    if key.startswith('#'):
        return ('other', line, None)
        
    rest = line_stripped[colon_idx+1:]
    
    # Find first double quote
    quote_start = rest.find('"')
    if quote_start == -1:
        return ('other', line, None)
        
    version = rest[:quote_start].strip()
    
    # Find last double quote
    quote_end = rest.rfind('"')
    if quote_end <= quote_start:
        return ('other', line, None)
        
    val = rest[quote_start+1:quote_end]
    comment = rest[quote_end+1:]
    
    # Extract leading spaces of original line to preserve indentation
    leading_spaces = line[:line.find(key)] if key in line else " "
    
    return ('key_value', key, {
        'version': version,
        'value': val,
        'comment': comment,
        'leading_spaces': leading_spaces
    })

def translate_file(src_path, dest_path, dry_run=False, limit=0, target_lang='l_english'):
    print(f"\n[PROCESSING] File: {src_path} -> {dest_path}")
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        # Stellaris files MUST be read as UTF-8-SIG to handle BOM correctly
        with codecs.open(src_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Could not read file {src_path}: {e}")
        return
        
    output_lines = []
    translated_count = 0
    total_lines = len(lines)
    
    for idx, line in enumerate(lines, 1):
        parsed = parse_line(line)
        line_type = parsed[0]
        
        if line_type == 'header':
            # Write language header replacing with target language code
            output_lines.append(f"{target_lang}:\n")
        elif line_type == 'other':
            output_lines.append(parsed[1])
        elif line_type == 'key_value':
            key = parsed[1]
            data = parsed[2]
            
            # Print progress every few lines
            if not dry_run and limit == 0:
                sys.stdout.write(f"\rTranslating lines: {idx}/{total_lines} ({translated_count} translated)")
                sys.stdout.flush()
                
            # Perform translation and shaping
            translated_val = data['value']
            if not dry_run:
                translated_val = process_value(data['value'])
                translated_count += 1
                
                # Save cache periodically
                if translated_count % 10 == 0:
                    save_cache()
            else:
                # In dry run, simulate shaping on the original value
                translated_val = process_value(data['value'])
                print(f"\n[DRY RUN] Key: {key}")
                print(f"  Original:  {data['value']}")
                print(f"  Processed: {translated_val}")
                translated_count += 1
                
            # Reconstruct the line
            ver_str = f"{data['version']}" if data['version'] else ""
            comment_str = data['comment'] if data['comment'] else ""
            reconstructed_line = f"{data['leading_spaces']}{key}:{ver_str} \"{translated_val}\"{comment_str}\n"
            output_lines.append(reconstructed_line)
            
            if limit > 0 and translated_count >= limit:
                print(f"\n[LIMIT] Reached limit of {limit} translations.")
                break
                
    if not dry_run:
        print(f"\n[SAVING] Writing outputs to {dest_path}")
        # Write file with UTF-8 BOM encoding
        with codecs.open(dest_path, "w", encoding="utf-8-sig") as f:
            f.writelines(output_lines)
        save_cache()

def main():
    # Change working directory to script's directory to resolve relative paths correctly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            pass # Older Python versions might not have reconfigure method
    load_cache()
    
    src_dir = "localisation/english"
    dest_dir = "localisation/arabic"
    
    if not os.path.exists(src_dir):
        print(f"[ERROR] Source directory '{src_dir}' not found. Please run the script inside your workspace folder.")
        sys.exit(1)
        
    files = [f for f in os.listdir(src_dir) if f.endswith(".yml")]
    
    print("Stellaris Arabic Translation Tool")
    print("================================")
    print(f"Found {len(files)} files in '{src_dir}'")
    print("1. Dry-run test on a single file")
    print("2. Translate a single file")
    print("3. Translate all files")
    
    choice = input("Select an option (1-3): ").strip()
    
    print("\nSelect target language to override (do not overwrite English to keep it default):")
    print("1. Spanish (l_spanish) - Recommended")
    print("2. French (l_french)")
    print("3. German (l_german)")
    print("4. Polish (l_polish)")
    print("5. Russian (l_russian)")
    print("6. Simplified Chinese (l_simp_chinese)")
    print("7. English (l_english) - Overwrite English")
    
    lang_choice = input("Select language (1-7) [default: 1]: ").strip()
    if lang_choice == '2':
        target_lang = 'l_french'
    elif lang_choice == '3':
        target_lang = 'l_german'
    elif lang_choice == '4':
        target_lang = 'l_polish'
    elif lang_choice == '5':
        target_lang = 'l_russian'
    elif lang_choice == '6':
        target_lang = 'l_simp_chinese'
    elif lang_choice == '7':
        target_lang = 'l_english'
    else:
        target_lang = 'l_spanish'
        
    print(f"\nTarget Language Selected: {target_lang}")
    
    if choice == '1':
        print("\nSelect a file to dry-run:")
        for idx, f in enumerate(files[:15], 1):
            print(f"{idx}. {f}")
        f_choice = int(input("File number: ")) - 1
        selected_file = files[f_choice]
        
        src_path = os.path.join(src_dir, selected_file)
        dest_path = os.path.join(dest_dir, selected_file.replace("_l_english.yml", f"_{target_lang}.yml"))
        
        translate_file(src_path, dest_path, dry_run=True, limit=5, target_lang=target_lang)
        
    elif choice == '2':
        print("\nSelect a file to translate:")
        for idx, f in enumerate(files[:15], 1):
            print(f"{idx}. {f}")
        f_choice = int(input("File number: ")) - 1
        selected_file = files[f_choice]
        
        src_path = os.path.join(src_dir, selected_file)
        dest_path = os.path.join(dest_dir, selected_file.replace("_l_english.yml", f"_{target_lang}.yml"))
        
        translate_file(src_path, dest_path, dry_run=False, target_lang=target_lang)
        print("\n[SUCCESS] File translated successfully.")
        
    elif choice == '3':
        confirm = input("Are you sure you want to translate all files? (y/n): ").strip().lower()
        if confirm == 'y':
            for f in files:
                src_path = os.path.join(src_dir, f)
                dest_path = os.path.join(dest_dir, f.replace("_l_english.yml", f"_{target_lang}.yml"))
                translate_file(src_path, dest_path, dry_run=False, target_lang=target_lang)
            print("\n[SUCCESS] All files translated successfully.")
            
if __name__ == "__main__":
    main()
