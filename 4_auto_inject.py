import os
import sys
import shutil
import subprocess

def resolve_shortcut(lnk_path):
    try:
        # Resolve shortcut via PowerShell COM object
        cmd = f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk_path}').TargetPath"
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
        target = result.stdout.strip()
        if target and os.path.exists(target):
            return target
    except Exception:
        pass
    return lnk_path

def find_desktop_shortcuts():
    desktop_paths = []
    # 1. User desktop
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        desktop_paths.append(os.path.join(user_profile, "Desktop"))
        desktop_paths.append(os.path.join(user_profile, "OneDrive", "Desktop"))
    # 2. Public desktop
    public_drive = os.environ.get("PUBLIC")
    if public_drive:
        desktop_paths.append(os.path.join(public_drive, "Desktop"))
    # 3. Start Menu
    program_data = os.environ.get("PROGRAMDATA")
    if program_data:
        desktop_paths.append(os.path.join(program_data, "Microsoft", "Windows", "Start Menu", "Programs"))
    if user_profile:
        desktop_paths.append(os.path.join(user_profile, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"))
        
    resolved_paths = []
    for d in desktop_paths:
        if os.path.exists(d):
            try:
                for root, dirs, files in os.walk(d):
                    for file in files:
                        if file.lower().endswith(".lnk") and "stellaris" in file.lower():
                            full_lnk = os.path.join(root, file)
                            target = resolve_shortcut(full_lnk)
                            if target and os.path.exists(target):
                                dir_path = os.path.dirname(target) if os.path.isfile(target) else target
                                if os.path.exists(os.path.join(dir_path, "stellaris.exe")) or os.path.exists(os.path.join(dir_path, "stellaris")):
                                    resolved_paths.append(dir_path)
            except Exception:
                pass
    return list(set(resolved_paths))

def find_stellaris_install():
    # 1. First, search for shortcuts on Desktop/Start Menu
    try:
        shortcut_paths = find_desktop_shortcuts()
        if shortcut_paths:
            return shortcut_paths[0]
    except Exception:
        pass

    # 2. Check common paths
    common_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris",
        r"C:\Program Files\Steam\steamapps\common\Stellaris",
        r"D:\SteamLibrary\steamapps\common\Stellaris",
        r"E:\SteamLibrary\steamapps\common\Stellaris",
        r"D:\Games\Stellaris",
        r"E:\Games\Stellaris",
        r"C:\GOG Games\Stellaris",
        r"D:\GOG Games\Stellaris",
    ]
    # Check drives from C to Z for GOG Games and SteamLibrary
    for drive in ["C", "D", "E", "F", "G"]:
        common_paths.append(f"{drive}:\\Games\\Stellaris")
        common_paths.append(f"{drive}:\\GOG Games\\Stellaris")
        common_paths.append(f"{drive}:\\SteamLibrary\\steamapps\\common\\Stellaris")
        
    for path in common_paths:
        if os.path.exists(path) and (os.path.exists(os.path.join(path, "stellaris.exe")) or os.path.exists(os.path.join(path, "stellaris"))):
            return path
    return None

def inject_arabic(game_path):
    print(f"\nInjecting Arabic Translation into: {game_path}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    direct_injection_dir = os.path.join(script_dir, "direct_injection")
    
    # Check if direct_injection folder exists, if not generate it
    if not os.path.exists(direct_injection_dir):
        print("Generating direct injection source files first...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("create_direct_injection", os.path.join(script_dir, "3_create_direct_injection.py"))
        create_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(create_mod)
        create_mod.main()
        
    # Copy folders recursively
    folders = ["localisation", "interface", "fonts", "gfx"]
    for folder in folders:
        src = os.path.join(direct_injection_dir, folder)
        dst = os.path.join(game_path, folder)
        
        if not os.path.exists(src):
            continue
            
        print(f"Injecting into '{folder}'...")
        # Copy file by file to handle existing folders gracefully without deleting original files
        for root, dirs, files in os.walk(src):
            rel_path = os.path.relpath(root, src)
            target_dir = dst if rel_path == "." else os.path.join(dst, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            
            for file in files:
                shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))
                
    print("\n==================================================")
    print("[SUCCESS] Arabic translation injected successfully!")
    print("You can now launch the game directly. It will be in Arabic!")
    print("==================================================")

def main():
    print("Stellaris Automatic Arabic Translation Injector")
    print("==============================================")
    
    # Change working directory to script's directory to resolve relative paths correctly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    detected_path = find_stellaris_install()
    game_path = None
    
    if detected_path:
        print(f"Detected Stellaris Installation: {detected_path}")
        choice = input("Do you want to inject Arabic translation to this path? (y/n) [default: y]: ").strip().lower()
        if choice == 'n':
            game_path = None
        else:
            game_path = detected_path
            
    if not game_path:
        print("\nCould not automatically find game path, or you chose to specify one manually.")
        print("💡 TIP: You can drag and drop your Stellaris game shortcut (.lnk) or the 'stellaris.exe' file into this window and hit Enter!")
        while True:
            path_input = input("Please drag-and-drop or enter the path: ").strip()
            # Remove quotes that Windows adds when drag-dropping
            path_input = path_input.strip('"\'')
            
            if not path_input:
                continue
                
            resolved_path = path_input
            if path_input.lower().endswith(".lnk"):
                print(f"Resolving shortcut: {path_input} ...")
                resolved_path = resolve_shortcut(path_input)
                print(f"Resolved to: {resolved_path}")
                
            if os.path.exists(resolved_path):
                # If they dropped a file (like stellaris.exe), get its folder
                if os.path.isfile(resolved_path):
                    game_path = os.path.dirname(resolved_path)
                else:
                    game_path = resolved_path
                break
            else:
                print(f"[ERROR] Path '{resolved_path}' does not exist. Please check and try again.")
                
    try:
        inject_arabic(game_path)
    except Exception as e:
        print(f"\n[ERROR] Failed to inject files: {e}")
        print("Please make sure you have permission to write to the game folder (try running as Administrator).")

if __name__ == "__main__":
    main()
