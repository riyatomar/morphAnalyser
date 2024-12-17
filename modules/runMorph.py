import json, re
from wxconv import WXC
import subprocess

MAPPER_DICT = {
    "NN": "n", "NST": "nst", "NNP": "n", "NEG": "avy", "PRP": "p",
    "PSP": "prsg", "DEM": "p", "VM": "v", "VAUX": "v", "JJ": "adj",
    "RB": "adv", "RP": "avy", "CC": "avy", "CL": "avy", "WQ": "p",
    "QF": "avy", "QC": "num", "QO": "num", "INTF": "avy", "INJ": "avy",
    "UT": "avy", "UNK": "unk", "SYM": "s", "XC": "c", "NNPC": "n", "QC": "adj"
}


def read_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data["sentences"]


def devanagari_to_wx(devanagari_text):
    wxc = WXC(order='utf2wx')
    return wxc.convert(devanagari_text)


def morph_analyzer(sentence, run_morph_analyser):
    words = sentence.split()
    output_lines = []
    original_words = []

    for word in words:
        if word.startswith("<") and word.endswith(">"):
            processed_word = '^' + word.strip('<>')
            output_lines.append(processed_word)
        else:
            output = run_morph_analyser(word)
            output_lines.append(output)
            if output.startswith('^') and '/' in output:
                original = output.split('^')[1].split('/')[0]
                original_words.append(original)

    return "\n".join(output_lines), original_words


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


def read_parser_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)["response"]


def map_pos_tags(sentences_data, parser_output):
    for sentence_data in sentences_data:
        sentence_id = sentence_data["sentence_id"]
        original_words = sentence_data["original"]

        matching_parser = next((item for item in parser_output if item["sentence_id"] == sentence_id), None)

        if matching_parser:
            pos_tags = []
            for word in original_words:
                matching_word = next(
                    (entry for entry in matching_parser["parser_output"] if entry["original_word"] == word),
                    None
                )
                if matching_word:
                    pos_tags.append(matching_word["pos_tag"])
                else:
                    pos_tags.append("UNKNOWN")
            sentence_data["pos_tags"] = pos_tags
        else:
            sentence_data["pos_tags"] = ["NO_MATCH"] * len(original_words)

    return sentences_data

def get_morph_info(word_data, pos_tag):
    """
    Extract the morphological span for a word that matches the POS tag's corresponding category.
    If no mapping exists, return the first span.
    """
    cat_value = MAPPER_DICT.get(pos_tag, None)
    spans = word_data.split('/')
    
    if not spans:
        return "NO_SPAN_FOUND"  # Handle case where word_data has no spans

    if not cat_value:
        return spans[1]  # If no mapping exists, return the first span

    for span in spans:
        if f"<cat:{cat_value}>" in span:
            return span  # Return the matching span
    
    return spans[1]  # Fallback to the first span if no matching span is found



# Update the main loop to populate morph_info
if __name__ == "__main__":
    input_file = "IO/input.txt"
    parser_output_file = "IO/parser_output.txt"

    sentences_data = read_from_json(input_file)
    parser_output = read_parser_output(parser_output_file)
    

    for sentence_data in sentences_data:
        sentence = sentence_data["sentence"]

        wx_notation = devanagari_to_wx(sentence)
       
        # Run morph analyzer
        morph_output, original_words = morph_analyzer(wx_notation, run_morph_analyser)
        sentence_data["original"] = original_words
        sentence_data["morph_outputs"] = morph_output.split("\n")

    # Map POS tags to words and add morph_info
    sentences_data = map_pos_tags(sentences_data, parser_output)

    for sentence_data in sentences_data:
        morph_outputs = sentence_data.get("morph_outputs", [])
        pos_tags = sentence_data.get("pos_tags", [])

       # Initialize morph_info_list to store detailed information
        morph_info_list = []

        for morph_output, pos_tag in zip(morph_outputs, pos_tags):
            morph_info = get_morph_info(morph_output, pos_tag)
            print(f"Word: {morph_output}, POS Tag: {pos_tag}, Morph Info: {morph_info}")
            
            # Patterns to extract root and tags
            root_pattern = r"^(\w+)"  # Captures the root word before any tags
            root_pattern1 = r"^(\*?\w+\$?)"
            tags_pattern = r"<([^>]+)>"  # Captures all tags enclosed in <>
            
            # Extract the root word
            root_match = re.match(root_pattern, morph_info)
            root_match1 = re.match(root_pattern1, morph_info)
            root = root_match.group(1) if root_match else root_match1.group(1).strip('*$')
            
            # Extract tags and split them into key-value pairs
            tags = re.findall(tags_pattern, morph_info)
            word_info = {"root": root}  # Start with root key
            for tag in tags:
                if ':' in tag:  # Ensures tag has a key-value format
                    key, value = tag.split(':')
                    word_info[key] = value
                else:  # Handle tags without values (e.g., <cat:p>)
                    word_info[tag] = None
                    
            morph_info_list.append(word_info)

        # Save the combined morph_info list back into sentence_data
        sentence_data["morph_info"] = morph_info_list

    # Save the updated data
    output_file = "IO/output_with_pos_and_morph.json"
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"sentences": sentences_data}, file, ensure_ascii=False, indent=4)

    print(f"Updated data with POS tags and morph info saved to {output_file}")
