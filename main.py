import os
from modules.file_io import read_from_json, read_parser_output, save_to_json
from modules.wx_converter import devanagari_to_wx
from modules.morph_analysis import morph_analyzer, get_morph_info
from modules.parser_utils import merge_morph_with_parser
from constant.map import MAPPER_DICT
from modules.subprocess_runner import run_morph_analyser

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
        # morph_info = get_morph_info(morph_output, pos_tag, MAPPER_DICT)
        # print('--------------->',sentence_data["original"])
        # print('================>', sentence_data["morph_outputs"])

    # Merge morph_info with parser output
    updated_parser_output = merge_morph_with_parser(sentences_data, parser_output, MAPPER_DICT)

    # Save updated parser output
    output_file = "IO/updated_parser_output.json"
    save_to_json(output_file, {"response": updated_parser_output})

    print(f"Updated parser output saved to {output_file}")
