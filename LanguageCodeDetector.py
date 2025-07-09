import re

class LanguageCodeDetector:
    """
    A utility class for detecting language codes from filenames or paths.

    This class scans a string (usually a filename) and returns a list of known language codes
    such as 'EN', 'FR', 'PTBR', etc. Supports extended codes like 'ENUS', 'ENUK'.

    If 'EN' is found alongside other languages, it is excluded to avoid false positives.
    """


    def __init__(self):
        # Dictionary of known language codes (key = code, value = human-readable name)
        self.language_codes = {
            "EN": "English", "ENUS": "English (US)", "ENUK": "English (UK)",
            "US": "English (US)", "UK": "English (UK)",
            "DE": "German", "ES": "Spanish", "FR": "French", "IT": "Italian",
            "PT": "Portuguese", "PTBR": "Portuguese (Brazil)", "BR": "Portuguese (Brazil)",
            "NL": "Dutch", "RU": "Russian", "PL": "Polish",
            "SV": "Swedish", "NO": "Norwegian", "DA": "Danish", "FI": "Finnish",
            "CZ": "Czech", "SK": "Slovak", "HU": "Hungarian",
            "AR": "Arabic", "ZH": "Chinese", "CN": "Chinese",
            "CHS": "Chinese (Simplified)", "CHT": "Chinese (Traditional)",
            "JA": "Japanese", "KO": "Korean"
            # You can extend this list with more codes as needed
        }

    def detect_languages(self, filename):
        """
        Detects language codes in the given filename or path.

        Args:
            filename (str): The filename or path to analyze.

        Returns:
            list[str]: A list of detected language codes (e.g., ['FR', 'PTBR']).
        """
        
        name = filename.upper()
        tokens = re.split(r'[^A-Z0-9]+', name)
        found = []

        # Check each token against the known language codes
        for token in tokens:
            if not token:
                continue  # Skip empty tokens
            if token in self.language_codes and token not in found:
                found.append(token)

        # Special rule: if multiple codes are found and one of them is "EN", exclude "EN"
        if 'EN' in found and len(found) > 1:
            found = [code for code in found if code != 'EN']

        return found


if __name__ == "__main__":
    # Ask the user to enter the path to the file
    path = input("Enter file path: ").strip()

    # Create an instance of the language detector
    detector = LanguageCodeDetector()

    # Try to detect languages from the given filename
    langs = detector.detect_languages(path)

    if langs:
        # If codes are found, display both the code and the full language name
        full_names = [detector.language_codes.get(code, code) for code in langs]
        print(f"Detected language codes: {', '.join(langs)}")
    else:
        # If no known language code is found
        print("Unknown language")
