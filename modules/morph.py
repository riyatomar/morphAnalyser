from wxconv import WXC
import sys, os, json, re, subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from constant.map import MAPPER_DICT

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

def get_morph_info(word_data, pos_tag):
    cat_value = MAPPER_DICT.get(pos_tag, None)
    spans = word_data.split('/')
    
    if not spans:
        return "NO_SPAN_FOUND"

    if not cat_value:
        return spans[1]

    for span in spans:
        if f"<cat:{cat_value}>" in span:
            return span
    
    return spans[1]

def merge_morph_with_parser(sentences_data, parser_output):
    for sentence_data in sentences_data:
        sentence_id = sentence_data["sentence_id"]
        original_words = sentence_data["original"]
        morph_outputs = sentence_data["morph_outputs"]

        matching_parser = next((item for item in parser_output if item["sentence_id"] == sentence_id), None)

        if matching_parser:
            for parser_word in matching_parser["parser_output"]:
                word = parser_word["original_word"]
                pos_tag = parser_word["pos_tag"]

                # Find corresponding morph_output
                morph_output = next((mo for mo in morph_outputs if word in mo), None)
                if morph_output:
                    morph_info = get_morph_info(morph_output, pos_tag)

                    # Extract root and tags
                    root_pattern = r"^(\w+)"
                    root_pattern1 = r"^(\*?\w+\$?)"
                    tags_pattern = r"<([^>]+)>"

                    root_match = re.match(root_pattern, morph_info)
                    root_match1 = re.match(root_pattern1, morph_info)
                    root = root_match.group(1) if root_match else root_match1.group(1).strip('*$')

                    tags = re.findall(tags_pattern, morph_info)
                    morph_info_dict = {"root": root}
                    for tag in tags:
                        if ':' in tag:
                            key, value = tag.split(':')
                            morph_info_dict[key] = value
                        else:
                            morph_info_dict[tag] = None

                    # Attach morph_info to parser_word
                    parser_word["morph_info"] = morph_info_dict

    return parser_output

if __name__ == "__main__":
    input_file = "IO/input.txt"
    parser_output_file = "IO/parser_output.txt"

    # Read input files
    sentences_data = read_from_json(input_file)
    parser_output = read_parser_output(parser_output_file)

    # Process sentences
    for sentence_data in sentences_data:
        sentence = sentence_data["sentence"]
        wx_notation = devanagari_to_wx(sentence)
        morph_output, original_words = morph_analyzer(wx_notation, run_morph_analyser)
        sentence_data["original"] = original_words
        sentence_data["morph_outputs"] = morph_output.split("\n")

    # Merge morph_info with parser output
    updated_parser_output = merge_morph_with_parser(sentences_data, parser_output)

    # Save updated parser output
    output_file = "IO/updated_parser_output.json"
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump({"response": updated_parser_output}, file, ensure_ascii=False, indent=4)

    print(f"Updated parser output saved to {output_file}")
