import json
import csv
from docx import Document
from pathlib import Path

class WordTableExtractor:
    """
    Extracts key-value pairs from Word (.docx) tables and exports them in various formats.

    Designed for translation/localization workflows where source-target pairs are stored
    in columns of Word tables. Supports export to TSV, JSON, and CSV.
    """

    def __init__(self, filepath_in, output_dir):
        """
        Initializes the extractor with the input Word file and output directory.

        Args:
            filepath_in (str): Path to the .docx file.
            output_dir (str): Folder to save the extracted data.

        Raises:
            FileNotFoundError: If the input file does not exist.
        """
        self.filepath = Path(filepath_in)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        self.result = {}
        self.basename = self.filepath.stem  # e.g. "Video_OST_forTRA_ES"

    def extract_columns(self, col1=0, col2=1):
        """
        Extracts text from the specified columns of all tables in the Word document.

        Args:
            col1 (int): Index of the key/source column (default 0).
            col2 (int): Index of the value/target column (default 1).

        Returns:
            dict: A dictionary of key-value pairs sorted by key length (descending).
        """
        doc = Document(str(self.filepath))
        temp_result = {}

        for table in doc.tables:
            if len(table.columns) <= max(col1, col2):
                continue

            for row in table.rows:
                cells = row.cells
                try:
                    key = cells[col1].text.strip()
                    value = cells[col2].text.strip()
                    if key and value and key != value:
                        temp_result[key] = value
                except IndexError:
                    continue

        sorted_result = dict(sorted(temp_result.items(), key=lambda x: len(x[0]), reverse=True))
        self.result = sorted_result
        return self.result

    def save_as_tsv(self):
        """
        Saves the extracted key-value data as a .tsv (Tab-Separated Values) file.
        """
        output_path = self.output_dir / f"{self.basename}.tsv"
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            for k, v in self.result.items():
                f.write(f"{k}\t{v}\n")

    def save_as_json(self):
        """
        Saves the extracted key-value data as a .json file.
        """
        output_path = self.output_dir / f"{self.basename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.result, f, ensure_ascii=False, indent=2)

    def save_as_csv(self):
        """
        Saves the extracted key-value data as a .csv file with headers.
        """
        output_path = self.output_dir / f"{self.basename}.csv"
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Column1', 'Column2'])
            for k, v in self.result.items():
                writer.writerow([k, v])
