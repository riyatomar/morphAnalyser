import re
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from modules.morph_analysis import get_morph_info

def merge_morph_with_parser(sentences_data, parser_output, mapper_dict):
    for sentence_data in sentences_data:
        sentence_id = sentence_data["sentence_id"]
        original_words = sentence_data["original"]
        morph_outputs = sentence_data["morph_outputs"]
        # print(morph_outputs)
        # Preprocess morph_outputs into a dictionary
        morph_dict = {}
        for morph in morph_outputs:
            entries = morph.split('/')
            for entry in entries:
                if entry.startswith('^'):
                    entry = entry[1:]  # Remove leading '^'
                root = entry.split('<')[0]  # Extract root
                if root not in morph_dict:
                    morph_dict[root] = morph

        matching_parser = next((item for item in parser_output if item["sentence_id"] == sentence_id), None)

        if matching_parser:
            for parser_word in matching_parser["parser_output"]:
                word = parser_word["wx_word"]
                if "pos_tag" in parser_word:
                    pos_tag = parser_word["pos_tag"]
                else:
                    continue
                
                # Use preprocessed dictionary for matching
                morph_output = morph_dict.get(word, None)
                if morph_output is None:
                    print(f"No morph output found for word: {word}")
                    continue
                
                try:
                    morph_info = get_morph_info(morph_output, pos_tag, mapper_dict)
                except IndexError as e:
                    print(f"Error processing morph_output: {morph_output}, error: {e}")
                    continue

                # Extract root and tags
                root_pattern = r"^(\w+)"
                root_pattern1 = r"^(\*?\w+\$?)"
                tags_pattern = r"<([^>]+)>"

                root_match = re.match(root_pattern, morph_info)
                root_match1 = re.match(root_pattern1, morph_info)

                if root_match:
                    root = root_match.group(1)
                elif root_match1:
                    root = root_match1.group(1).strip('*$')
                else:
                    print(f"No root found in morph_info: {morph_info}")
                    continue

                tags = re.findall(tags_pattern, morph_info)
                morph_info_dict = {"root": root}
                for tag in tags:
                    if ':' in tag:
                        key, value = tag.split(':')
                        morph_info_dict[key] = value
                    else:
                        morph_info_dict[tag] = None

                parser_word["morph_info"] = morph_info_dict

    return parser_output
