import subprocess

def run_morph_analyser(word):
    try:
        result = subprocess.run(
            ["sh", "run_morph-analyser.sh"],
            input=word, text=True, capture_output=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error while running morph analyzer for word '{word}': {e}")
        return f"error-for-{word}"
