import os
import sys
import shutil

def main():
    print("Stellaris Direct Arabic Injector Creator")
    print("========================================")
    
    # Change working directory to script's directory to resolve relative paths correctly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    target_dir = os.path.join(script_dir, "direct_injection")
    
    print(f"Creating direct injection files inside: {target_dir}")
    
    # 1. Create directory structure
    print("\n[1/6] Creating folder structure...")
    os.makedirs(os.path.join(target_dir, "localisation", "english"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "interface"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "gfx", "fonts"), exist_ok=True)
    
    # 2. Copy translated English YAML files
    print("[2/6] Copying translation files...")
    src_loc_dir = "localisation/arabic"
    dest_loc_dir = os.path.join(target_dir, "localisation", "english")
    
    if not os.path.exists(src_loc_dir):
        print(f"[ERROR] Source translation directory '{src_loc_dir}' not found. Please translate files first.")
        sys.exit(1)
        
    copied_count = 0
    for f in os.listdir(src_loc_dir):
        # We target l_english because game defaults to English
        if f.endswith("_l_english.yml"):
            shutil.copy(
                os.path.join(src_loc_dir, f),
                os.path.join(dest_loc_dir, f)
            )
            copied_count += 1
            
    if copied_count == 0:
        print("[ERROR] No English translation files (*_l_english.yml) found in localisation/arabic.")
        sys.exit(1)
    print(f"Copied {copied_count} translation files to localisation/english.")
    
    # 3. Copy font asset file
    print("[3/6] Creating font asset file...")
    asset_content = """font = {
	name = "Arabic_normal"
	
	fontstyle = {
		style = regular
		file = "gfx/fonts/arabic_font.ttf"
	}
}
"""
    with open(os.path.join(target_dir, "fonts", "arabic_font.asset"), "w", encoding="utf-8") as f:
        f.write(asset_content)
        
    # 4. Copy Windows TrueType font to mod
    print("[4/6] Copying a bold Arabic system font from Windows...")
    sys_font_candidates = [
        "C:\\Windows\\Fonts\\tahomabd.ttf", # Tahoma Bold (great for small size UI legibility)
        "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold
        "C:\\Windows\\Fonts\\segoeuib.ttf",  # Segoe UI Bold
        "C:\\Windows\\Fonts\\tahoma.ttf",    # Tahoma Regular
        "C:\\Windows\\Fonts\\arial.ttf"      # Arial Regular
    ]
    
    copied_font = False
    dest_font = os.path.join(target_dir, "gfx", "fonts", "arabic_font.ttf")
    for sys_font in sys_font_candidates:
        if os.path.exists(sys_font):
            shutil.copy(sys_font, dest_font)
            print(f"Copied font successfully: {os.path.basename(sys_font)}")
            copied_font = True
            break
            
    if not copied_font:
        print("[WARN] No system fonts found. Please place a font in gfx/fonts/arabic_font.ttf manually.")
        
    # 5. Process fonts.gfx overrides
    print("[5/6] Generating fonts.gfx overrides...")
    src_gfx = "interface/fonts.gfx"
    dest_gfx = os.path.join(target_dir, "interface", "fonts.gfx")
    
    if os.path.exists(src_gfx):
        with open(src_gfx, "r", encoding="utf-8") as f:
            gfx_content = f.read()
            
        overrides = """
	# Custom Arabic overrides for game UI
	bitmapfont_override = {
		name = "standard_font"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "large_title_font"
		ttf_font = "Arabic_normal"
		ttf_size = "28"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "large_title_font_28"
		ttf_font = "Arabic_normal"
		ttf_size = "26"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "cg_16b"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "hoi_16mbs"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "jura"
		ttf_font = "Arabic_normal"
		ttf_size = "16"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "malgun_goth_24"
		ttf_font = "Arabic_normal"
		ttf_size = "24"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "map_name_border"
		ttf_font = "Arabic_normal"
		ttf_size = "40"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "map_name_nebula"
		ttf_font = "Arabic_normal"
		ttf_size = "30"
		languages = { "l_english" }
	}
	bitmapfont_override = {
		name = "map_name_sector"
		ttf_font = "Arabic_normal"
		ttf_size = "30"
		languages = { "l_english" }
	}
"""
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
        
    # 6. Process load_screen_font.gfx overrides
    print("[6/6] Generating load_screen_font.gfx overrides...")
    src_load_gfx = "interface/load_screen_font.gfx"
    dest_load_gfx = os.path.join(target_dir, "interface", "load_screen_font.gfx")
    
    if os.path.exists(src_load_gfx):
        with open(src_load_gfx, "r", encoding="utf-8") as f:
            load_gfx_content = f.read()
            
        load_overrides = """
	bitmapfont_override = {
		name = "load_screen"
		ttf_font = "Arabic_normal"
		ttf_size = "24"
		languages = { "l_english" }
	}
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
    print("[SUCCESS] Direct Injection Files Generated!")
    print(f"Directory: {target_dir}")
    print("==================================================")
    print("HOW TO APPLY TO YOUR GAME:")
    print("1. Open the 'direct_injection' folder.")
    print("2. Copy all the folders inside it: 'localisation', 'interface', 'fonts', 'gfx'.")
    print("3. Paste them into your main Stellaris game installation directory.")
    print("4. Select 'Replace all files in destination' if prompted.")
    print("5. Launch the game directly. It will be in Arabic!")
    print("==================================================")

if __name__ == "__main__":
    main()
