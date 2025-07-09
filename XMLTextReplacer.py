import xml.etree.ElementTree as ET
from pathlib import Path
from LanguageCodeDetector import LanguageCodeDetector
import json
from datetime import datetime

class XMLTextReplacer:
    """
    Replaces text in an XML file based on a JSON translation dictionary,
    and writes the result into a specified output directory with a filename:
    <original_basename>_<lang_code>.xml
    """

    def __init__(self, xml_path: str, translations_path: str, output_dir: str):
        """
        Args:
            xml_path (str): Path to the source XML file.
            translations_path (str): Path to the JSON file with translations.
            output_dir (str): Directory where the output XML and log will be saved.
        """
        self.xml_path = Path(xml_path)
        self.translations_path = Path(translations_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.detector = LanguageCodeDetector()

        if not self.xml_path.exists():
            raise FileNotFoundError(f"XML file not found: {self.xml_path}")
        if not self.translations_path.exists():
            raise FileNotFoundError(f"Translation JSON not found: {self.translations_path}")

    def replace_text(self):
        start_time = datetime.now()
        
        # detect lang code (list) and pick first or fallback to 'unknown'
        codes = self.detector.detect_languages(self.translations_path.name)
        lang_code = codes[0] if codes else "unknown"
        print(f"🌐 Detected language code: {lang_code}")

        # load XML
        tree = ET.parse(str(self.xml_path))
        root = tree.getroot()

        # load translations
        with open(self.translations_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # sort by target length desc (optional but helps avoid partial matches)
        sorted_tr = {
            k: translations[k]
            for k in sorted(translations, key=lambda x: len(translations[x]), reverse=True)
        }

        replaced, missing, empty = [], [], []
        count = 0

        for comp in root.findall('composition'):
            for layer in comp.findall('layer'):
                txt = (layer.text or "").strip()
                if not txt:
                    empty.append("[EMPTY]")
                    continue
                if txt in sorted_tr:
                    new = sorted_tr[txt]
                    layer.text = new
                    replaced.append(f"[OK] {txt} → {new}")
                    count += 1
                else:
                    missing.append(f"[MISSING] {txt}")

        # prepare output paths
        base = self.xml_path.stem
        out_xml  = self.output_dir / f"{base}_{lang_code}.xml"
        out_log  = self.output_dir / f"{base}_{lang_code}.log"

        # write XML
        tree.write(str(out_xml), encoding='UTF-8', xml_declaration=True)
        print(f"🔁 Total replaced: {count}")

        # write log with header and numbered entries
        with open(out_log, 'w', encoding='utf-8') as log:
            log.write(f"=== LOG FOR: {base}_{lang_code}.xml ===\n")
            log.write(f"Source XML: {self.xml_path.name}\n")
            log.write(f"Translations JSON: {self.translations_path.name}\n")
            log.write(f"Total Replaced: {len(replaced)}\n")
            log.write(f"Missing Keys: {len(missing)}\n")
            log.write(f"Empty Layers: {len(empty)}\n")
            log.write("=" * 40 + "\n\n")

            log.write("=== REPLACED ===\n")
            log.write("\n".join([f"{i+1}. {line}" for i, line in enumerate(replaced)]) + "\n\n")

            log.write("=== MISSING ===\n")
            log.write("\n".join([f"{i+1}. {line}" for i, line in enumerate(missing)]) + "\n\n")

            log.write("=== EMPTY ===\n")
            log.write("\n".join([f"{i+1}. {line}" for i, line in enumerate(empty)]) + "\n")

            duration = datetime.now() - start_time
            log.write(f"\n⏱ Duration: {duration.total_seconds():.2f} seconds\n")

        print(f"📝 Log saved: {out_log}")
        
        # print(f"📝 Replaced: {len(replaced)} | Missing: {len(missing)} | Empty: {len(empty)}")


# Примітка: для локального тесту можна раскоментувати:
# if __name__ == "__main__":
#     xml_path          = r"m:\Projects\Video\AS-ESE2505001-263\AS-ESE2505001-263\Done\AS-ESE2505001-263.xml"
#     translations_path = r"xml_AE\translationMemory\Video_OST_forTRA_ZH.json"
#     output_dir        = r"xml_AE\ready_XML_for_AE"

#     replacer = XMLTextReplacer(xml_path, translations_path, output_dir)
#     replacer.replace_text()
