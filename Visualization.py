import json
from pathlib import Path
import matplotlib.pyplot as plt

class ReportBuilder:
    """
    Builds simple visual reports (charts, stats) based on
    the JSON or log outputs of the localization pipeline.
    """

    def __init__(self, translations_json_path, log_path):
        self.translations_json_path = Path(translations_json_path)
        self.log_path               = Path(log_path)

        if not self.log_path.exists():
            raise FileNotFoundError(f"No log file found at {self.log_path}")

    def load_translations(self):
        if self.translations_json_path is None:
            raise ValueError("No path provided for translations JSON")
        if not self.translations_json_path.exists():
            raise FileNotFoundError(f"No translations JSON: {self.translations_json_path}")

        # Використовуємо метод Path.open(), щоб IDE не скаржилась
        with self.translations_json_path.open('r', encoding='utf-8') as f:
            return json.load(f)


    def parse_log(self):
        """
        Parses the replacer’s .log to count:
          - total replaced
          - missing
          - empty
        """
        stats = {'replaced': 0, 'missing': 0, 'empty': 0}
        lines = self.log_path.read_text(encoding='utf-8').splitlines()
        for line in lines:
            if line.startswith('[OK]'):
                stats['replaced'] += 1
            elif line.startswith('[MISSING]'):
                stats['missing'] += 1
            elif line.startswith('[EMPTY]'):
                stats['empty'] += 1
        return stats

    def plot_stats(self, stats: dict):
        """
        Draws a simple bar chart of replaced/missing/empty counts.
        """
        labels = list(stats.keys())
        values = list(stats.values())
        plt.figure()
        plt.bar(labels, values)
        plt.title("Localization Results")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.show()
