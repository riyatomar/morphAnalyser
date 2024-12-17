import re
from modules.subprocess_runner import run_morph_analyser

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

def get_morph_info(word_data, pos_tag, mapper_dict):
    cat_value = mapper_dict.get(pos_tag, None)
    spans = word_data.split('/')

    if not spans:
        return "NO_SPAN_FOUND"

    if not cat_value:
        return spans[1]

    for span in spans:
        if f"<cat:{cat_value}>" in span:
            return span

    return spans[1]
