import os
import sys
import shutil
import codecs

def get_documents_path():
    # Attempt standard environment path on Windows
    home = os.path.expanduser("~")
    docs = os.path.join(home, "Documents")
    
    # Check if Paradox Interactive directory exists under Documents
    pdx_path = os.path.join(docs, "Paradox Interactive", "Stellaris")
    if os.path.exists(pdx_path):
        return pdx_path
        
    # Check OneDrive path which is common on modern Windows systems
    onedrive_docs = os.path.join(home, "OneDrive", "Documents")
    pdx_onedrive = os.path.join(onedrive_docs, "Paradox Interactive", "Stellaris")
    if os.path.exists(pdx_onedrive):
        return pdx_onedrive
        
    # Fallback to standard Documents path
    return pdx_path

def main():
    # Change working directory to script's directory to resolve relative paths correctly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Stellaris Arabic Mod Bundler")
    print("===========================")
    
    pdx_stell_path = get_documents_path()
    mod_dir = os.path.join(pdx_stell_path, "mod")
    mod_target_dir = os.path.join(mod_dir, "stellaris_arabic_translation")
    
    print(f"Target Stellaris Path: {pdx_stell_path}")
    print(f"Mod Target Path: {mod_target_dir}")
    
    # Auto-detect target language from files in localisation/arabic
    src_loc_dir = "localisation/arabic"
    if not os.path.exists(src_loc_dir):
        print(f"[ERROR] Source translation directory '{src_loc_dir}' not found. Please translate files first.")
        sys.exit(1)
        
    available_langs = set()
    supported_suffixes = ['english', 'spanish', 'french', 'german', 'polish', 'russian', 'simp_chinese', 'braz_por', 'japanese', 'korean']
    for f in os.listdir(src_loc_dir):
        if f.endswith(".yml"):
            for lang in supported_suffixes:
                if f.endswith(f"_l_{lang}.yml"):
                    available_langs.add(f"l_{lang}")
                    
    available_langs = sorted(list(available_langs))
    if not available_langs:
        print("[ERROR] No translation files found in localisation/arabic.")
        sys.exit(1)
        
    print("\nAvailable translated languages in localisation/arabic:")
    # Sort so l_english is always first or easy to select
    if 'l_english' in available_langs:
        available_langs.remove('l_english')
        available_langs.insert(0, 'l_english')
        
    for idx, lang in enumerate(available_langs, 1):
        suffix = " (Recommended - Arabic will show up immediately)" if lang == 'l_english' else ""
        print(f"{idx}. {lang}{suffix}")
        
    choice_idx = 0
    if len(available_langs) > 1:
        try:
            choice_str = input(f"Select language to bundle (1-{len(available_langs)}) [default: 1]: ").strip()
            if choice_str:
                choice_idx = int(choice_str) - 1
                if choice_idx < 0 or choice_idx >= len(available_langs):
                    choice_idx = 0
        except ValueError:
            choice_idx = 0
            
    detected_lang = available_langs[choice_idx]
    
    lang_to_folder = {
        'l_english': 'english',
        'l_spanish': 'spanish',
        'l_french': 'french',
        'l_german': 'german',
        'l_polish': 'polish',
        'l_russian': 'russian',
        'l_simp_chinese': 'simp_chinese',
        'l_braz_por': 'braz_por',
        'l_japanese': 'japanese',
        'l_korean': 'korean'
    }
    target_folder = lang_to_folder.get(detected_lang, 'english')
    print(f"Bundling Language: {detected_lang} (Folder: localisation/{target_folder})")
    
    # 1. Create directory structure
    print("\n[1/7] Creating mod folder structure...")
    os.makedirs(os.path.join(mod_target_dir, "localisation", target_folder), exist_ok=True)
    os.makedirs(os.path.join(mod_target_dir, "interface"), exist_ok=True)
    os.makedirs(os.path.join(mod_target_dir, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(mod_target_dir, "gfx", "fonts"), exist_ok=True)
    
    # 2. Write descriptor files
    print("[2/7] Writing descriptor files...")
    descriptor_content = """name="Stellaris Arabic Translation"
path="mod/stellaris_arabic_translation"
tags={
	"Translation"
	"Localisation"
}
supported_version="v3.12.*"
"""
    
    # Outer mod file
    outer_mod = os.path.join(mod_dir, "stellaris_arabic_translation.mod")
    with open(outer_mod, "w", encoding="utf-8") as f:
        f.write(descriptor_content)
        
    # Inner mod file
    inner_mod = os.path.join(mod_target_dir, "descriptor.mod")
    with open(inner_mod, "w", encoding="utf-8") as f:
        f.write(descriptor_content)
        
    # 3. Copy translated YAML files
    print("[3/7] Copying translation files...")
    dest_loc_dir = os.path.join(mod_target_dir, "localisation", target_folder)
    
    # Clean up old target folders in mod to avoid mixing translations
    for folder in lang_to_folder.values():
        old_folder_path = os.path.join(mod_target_dir, "localisation", folder)
        if folder != target_folder and os.path.exists(old_folder_path):
            try:
                shutil.rmtree(old_folder_path)
            except Exception:
                pass
        
    copied_count = 0
    for f in os.listdir(src_loc_dir):
        if f.endswith(f"_{detected_lang}.yml"):
            shutil.copy(
                os.path.join(src_loc_dir, f),
                os.path.join(dest_loc_dir, f)
            )
            copied_count += 1
    print(f"Copied {copied_count} translation files.")
    
    # 4. Copy font asset file
    print("[4/7] Creating font asset file...")
    asset_content = """font = {
	name = "Arabic_normal"
	
	fontstyle = {
		style = regular
		file = "gfx/fonts/arabic_font.ttf"
	}
}
"""
    with open(os.path.join(mod_target_dir, "fonts", "arabic_font.asset"), "w", encoding="utf-8") as f:
        f.write(asset_content)
        
    # 5. Copy Windows TrueType font to mod
    print("[5/7] Copying a bold Arabic system font from Windows...")
    sys_font_candidates = [
        "C:\\Windows\\Fonts\\tahomabd.ttf", # Tahoma Bold (great for small size UI legibility)
        "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold
        "C:\\Windows\\Fonts\\segoeuib.ttf",  # Segoe UI Bold
        "C:\\Windows\\Fonts\\tahoma.ttf",    # Tahoma Regular
        "C:\\Windows\\Fonts\\arial.ttf"      # Arial Regular
    ]
    
    copied_font = False
    dest_font = os.path.join(mod_target_dir, "gfx", "fonts", "arabic_font.ttf")
    for sys_font in sys_font_candidates:
        if os.path.exists(sys_font):
            shutil.copy(sys_font, dest_font)
            print(f"Copied font successfully: {os.path.basename(sys_font)}")
            copied_font = True
            break
            
    if not copied_font:
        print("[WARN] No system fonts found. Please place a font in gfx/fonts/arabic_font.ttf manually.")
        
    # 6. Process fonts.gfx overrides
    print("[6/7] Generating fonts.gfx overrides...")
    src_gfx = "interface/fonts.gfx"
    dest_gfx = os.path.join(mod_target_dir, "interface", "fonts.gfx")
    
    if os.path.exists(src_gfx):
        with open(src_gfx, "r", encoding="utf-8") as f:
            gfx_content = f.read()
            
        # Define overrides we want to insert
        overrides = f"""
	# Custom Arabic overrides for game UI
	bitmapfont_override = {{
		name = "standard_font"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "large_title_font"
		ttf_font = "Arabic_normal"
		ttf_size = "28"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "large_title_font_28"
		ttf_font = "Arabic_normal"
		ttf_size = "26"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "cg_16b"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "hoi_16mbs"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "jura"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "malgun_goth_24"
		ttf_font = "Arabic_normal"
		ttf_size = "24"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "map_name_border"
		ttf_font = "Arabic_normal"
		ttf_size = "40"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "map_name_nebula"
		ttf_font = "Arabic_normal"
		ttf_size = "30"
		languages = {{ "{detected_lang}" }}
	}}
	bitmapfont_override = {{
		name = "map_name_sector"
		ttf_font = "Arabic_normal"
		ttf_size = "30"
		languages = {{ "{detected_lang}" }}
	}}
"""
        # Find the last closing brace and insert overrides
        last_brace = gfx_content.rfind("}")
        if last_brace != -1:
            modified_gfx = gfx_content[:last_brace] + overrides + "\n}"
            with open(dest_gfx, "w", encoding="utf-8") as f:
                f.write(modified_gfx)
            print("Wrote fonts.gfx with Arabic overrides.")
        else:
            shutil.copy(src_gfx, dest_gfx)
            print("[WARN] Could not find closing brace in fonts.gfx. Copied unmodified file.")
    else:
        print("[WARN] interface/fonts.gfx not found in project directory.")
        
    # 7. Process load_screen_font.gfx overrides
    print("[7/7] Generating load_screen_font.gfx overrides...")
    src_load_gfx = "interface/load_screen_font.gfx"
    dest_load_gfx = os.path.join(mod_target_dir, "interface", "load_screen_font.gfx")
    
    if os.path.exists(src_load_gfx):
        with open(src_load_gfx, "r", encoding="utf-8") as f:
            load_gfx_content = f.read()
            
        load_overrides = f"""
	bitmapfont_override = {{
		name = "load_screen"
		ttf_font = "Arabic_normal"
		ttf_size = "24"
		languages = {{ "{detected_lang}" }}
	}}
"""
        last_brace = load_gfx_content.rfind("}")
        if last_brace != -1:
            modified_load_gfx = load_gfx_content[:last_brace] + load_overrides + "\n}"
            with open(dest_load_gfx, "w", encoding="utf-8") as f:
                f.write(modified_load_gfx)
            print("Wrote load_screen_font.gfx with Arabic overrides.")
        else:
            shutil.copy(src_load_gfx, dest_load_gfx)
            print("[WARN] Could not find closing brace in load_screen_font.gfx. Copied unmodified file.")
    else:
        print("[WARN] interface/load_screen_font.gfx not found in project directory.")
        
    print("\n==================================================")
    print("[SUCCESS] Mod generated successfully!")
    print(f"You can now open the Stellaris Launcher and enable:")
    print("  'Stellaris Arabic Translation'")
    print("==================================================")

if __name__ == "__main__":
    main()
