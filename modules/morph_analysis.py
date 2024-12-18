from constant.map import MAPPER_DICT
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
            # print('output_lines--->', output_lines)
            if output.startswith('^') and '/' in output:
                original = output.split('^')[1].split('/')[0]
                original_words.append(original)
                all_spans = "\n".join(output_lines)
                # print('-------------->', all_spans)
    # return "\n".join(output_lines), original_words
    return all_spans, original_words

def get_morph_info(all_spans, pos_tag, MAPPER_DICT):
    cat_value = MAPPER_DICT.get(pos_tag, None)
    # print('cat_value--->', cat_value, pos_tag)
    # print('============>', all_spans)
    spans = all_spans.split('/')
    # print('============>', spans)

    if len(spans) < 2:
        # print('===============', word_data)
        return all_spans

    if not cat_value:
        return spans[1]

    for span in spans:
        # print('===========>', cat_value)
        if f"<cat:{cat_value}>" in span:
            return span
            
    return spans[1]


