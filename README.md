# Stellaris Arabic Translation Mod (تعريب لعبة ستيلاريس)

## 📌 Introduction (مقدمة)
This project is an automated Arabic translation for the space grand strategy game **Stellaris** (v3.12+).
It translates the entire game files (129 files, over 92,000 strings) using the Google Translate API combined with custom shaping and Bidirectional layout processing (BiDi) to make the Arabic text display correctly in-game from right to left (RTL) under the game's LTR engine.

هذا المشروع هو تعريب تلقائي متكامل للعبة الاستراتيجية الفضائية الشهيرة **Stellaris** (الإصدار v3.12 وما فوق).
يقوم المشروع بترجمة كافة ملفات اللعبة (129 ملفاً، أكثر من 92,000 جملة نصية) باستخدام Google Translate API مع معالجة وإعادة تشكيل الأحرف والاتجاهات (BiDi) لكي تظهر اللغة العربية داخل اللعبة بشكل صحيح ومقروء من اليمين إلى اليسار.

---

## 🎮 For Players (للاعبين)
If you just want to play the game in Arabic:
إذا كنت ترغب فقط في لعب اللعبة باللغة العربية:

### Method 1: Automatic Injection (الطريقة الأولى: التثبيت التلقائي - موصى بها)
1. Download the project repository as a ZIP file and extract it.
2. Run **[4_auto_inject.bat](file:///C:/dev/Stellaris%20arabic_translation.po/4_auto_inject.bat)** (Run as Administrator if the game is in Program Files).
3. If the installer finds your game automatically, press **Enter** to confirm.
4. If not, drag and drop the game icon (Desktop shortcut) or `stellaris.exe` from your game folder directly into the window and press **Enter**.
5. Launch the game directly. It will load in Arabic immediately!

1. قم بتحميل المستودع كملف ZIP وفك الضغط عنه.
2. قم بتشغيل الملف **[4_auto_inject.bat](file:///C:/dev/Stellaris%20arabic_translation.po/4_auto_inject.bat)** (شغله كمسؤول Administrator إذا كانت اللعبة في القرص C).
3. إذا عثر السكربت على اللعبة تلقائياً، اضغط **Enter** للتأكيد.
4. إذا لم يجدها، اسحب أيقونة تشغيل اللعبة من سطح المكتب أو ملف `stellaris.exe` وأفلتها داخل شاشة السكربت ثم اضغط **Enter**.
5. شغل اللعبة مباشرة، وستفتح باللغة العربية فوراً!

### Method 2: Manual Copy-Paste (الطريقة الثانية: النسخ واللصق اليدوي)
1. Open the [direct_injection](file:///C:/dev/Stellaris%20arabic_translation.po/direct_injection) folder.
2. Copy the four folders inside it: `localisation`, `interface`, `fonts`, and `gfx`.
3. Paste them into your main Stellaris installation directory (where `stellaris.exe` is located).
4. Replace all files when prompted.

1. افتح مجلد [direct_injection](file:///C:/dev/Stellaris%20arabic_translation.po/direct_injection).
2. انسخ المجلدات الأربعة التي بداخله: `localisation` و `interface` و `fonts` و `gfx`.
3. الصقها داخل مجلد اللعبة الرئيسي (المجلد الذي يحتوي على ملف `stellaris.exe`).
4. اختر استبدال كافة الملفات عند السؤال.

---

## 🛠️ For Developers (للمطورين)
If you want to modify the translation or run the scripts:
إذا كنت ترغب في تعديل الترجمة أو تشغيل السكربتات البرمجية:

### Prerequisites (المتطلبات):
- Python 3.8+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Project Structure (هيكل المشروع):
- `translate_stellaris.py`: The main translation engine. It parses English files from `localisation/english/`, translates them, handles game style codes (like `§H`, `[Root.GetName]`, etc.), reshapes Arabic, and saves them to `localisation/arabic/`.
- `translation_cache.json`: The translation memory cache containing 92,000+ translated strings. This makes subsequent runs instant!
- `2_create_mod.py`: Packages the files into a standard Paradox Mod (saved in `Documents/Paradox Interactive/Stellaris/mod`).
- `3_create_direct_injection.py`: Creates the pre-packaged `direct_injection` directory.
- `4_auto_inject.py`: The automatic installer program.

### Running scripts (طريقة التشغيل):
1. **To update/translate files**: Run `1_translate.bat` or `python translate_stellaris.py`.
2. **To create a mod package**: Run `2_create_mod.bat` or `python 2_create_mod.py`.
3. **To generate injection files**: Run `3_create_direct_injection.bat` or `python 3_create_direct_injection.py`.
4. **To install automatically**: Run `4_auto_inject.bat` or `python 4_auto_inject.py`.
