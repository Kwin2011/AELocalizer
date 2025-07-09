import os
import sys
from pathlib import Path
import questionary
from WordTableExtractor import WordTableExtractor
from XMLTextReplacer import XMLTextReplacer

class LocalizationController:
    def __init__(self):
        self.xml_path: Path | None = None
        self.output_dir: Path | None = None
        self.translation_memory_dir = Path("translationMemory")
        self.translation_memory_dir.mkdir(parents=True, exist_ok=True)

    def ask_for_xml_path(self):
        while True:
            path = questionary.path("Enter path to XML file:").ask()
            if not path:
                print("❌ XML path is required. Exiting.")
                sys.exit(1)
            path = Path(path)
            if path.exists() and path.is_file():
                self.xml_path = path
                print(f"✅ XML file is correct")
                break
            else:
                print("❌ File does not exist. Try again.")

    def ask_for_output_dir(self):
        while True:
            answer = questionary.text("Enter output directory (leave empty for default):").ask()
            if not answer:
                self.output_dir = Path("ready_XML_for_AE")
                self.output_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Output directory is set to default: {self.output_dir}")
                break

            path = Path(answer)

            if path.exists():
                if path.is_file() and path.suffix.lower() == ".docx":
                    # User accidentally entered a translation file instead of a folder
                    print(f"⚠️  It looks like you entered a DOCX file instead of a folder. I’ll use it as a translation file.")
                    self.translation_candidate = path
                    continue  # Ask again for proper output_dir
                elif path.is_file():
                    print(f"❌ Error: You've entered a file, not a folder: {path}")
                    continue
                else:
                    self.output_dir = path
                    self.output_dir.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Output directory is correct: {self.output_dir}")
                    break
            else:
                # Create the directory
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    self.output_dir = path
                    print(f"✅ Created and set output directory: {self.output_dir}")
                    break
                except Exception as e:
                    print(f"❌ Failed to create directory: {e}")



    def process_translation(self, docx_path: Path):
        if self.xml_path is None or self.output_dir is None:
            raise ValueError("❌ XML path or output directory is not set.")

        print(f"📥 Processing: {docx_path.name}")
        extractor = WordTableExtractor(str(docx_path), str(self.translation_memory_dir))
        extractor.extract_columns()
        extractor.save_as_json()

        json_filename = extractor.basename + ".json"
        translations_json_path = self.translation_memory_dir / json_filename

        lang_code = extractor.basename.split("_")[-1].upper()
        output_filename = f"{self.xml_path.stem}_{lang_code}.xml"
        output_path = self.output_dir / output_filename

        replacer = XMLTextReplacer(
            xml_path=str(self.xml_path),
            translations_path=str(translations_json_path),
            output_dir=str(self.output_dir)
        )
        replacer.replace_text()

        print(f"✅ XML ready: {output_path}")

        log_path = self.output_dir / f"{self.xml_path.stem}_{lang_code}.log"
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()
            if "[MISSING]" in log_content:
                print("\n⚠️ Missing translations detected! Showing log content:\n" + "-" * 40)
                print(log_content)
                print("-" * 40 + "\n")
            else:
                show_log = questionary.confirm("Open log file?").ask()
                if show_log:
                    print("\n📄 LOG CONTENT\n" + "-" * 40)
                    print(log_content)
                    print("-" * 40 + "\n")
        else:
            print("ℹ️ Log file not found.")


    def run(self):
        self.ask_for_xml_path()
        self.translation_candidate = None
        self.ask_for_output_dir()

        docx_paths = []
        if self.translation_candidate:
            docx_paths.append(self.translation_candidate)

        while True:
            if not docx_paths:
                docx_path = questionary.path("Enter DOCX translation file path:").ask()
                if not docx_path:
                    print("❌ No DOCX path provided.")
                    continue
                docx_paths.append(Path(docx_path))

            docx_file = docx_paths.pop(0)

            if not docx_file.exists() or not docx_file.is_file():
                print("❌ DOCX file not found. Try again.")
                continue

            try:
                self.process_translation(docx_file)
            except Exception as e:
                print(f"❌ Error during processing: {e}")

            more = questionary.confirm("Do you want to process another translation?").ask()
            if not more:
                print("👋 Exiting. All done.")
                break



if __name__ == "__main__":
    controller = LocalizationController()
    controller.run()
    
