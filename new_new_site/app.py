import re
import json
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

from flask import Flask
from flask import render_template, request


app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    print('ok1')
    return render_template('index.html')

#@app.route('/show_results')
#def results():
 #   search_result = 's'
  #  return render_template("results.html", results=search_result)

@app.route('/results', methods=['get'])
def results():
    print('ok2')
    input_string = request.args.get("input_str")
    print(input_string)
    search_result = main_search(input_string, 'panorama_corpus.json')
    #return render_template("results.html", results=search_result)
    return render_template("results.html", results=search_result)


def main_search(input_string, corpus_json):
    with open(corpus_json, encoding='utf-8') as f:
        data = json.load(f)
    answer = []

    # если вся строка в кавычках, поиск
    if (input_string.startswith("'") and input_string.endswith("'")) or (
            input_string.startswith('"') and input_string.endswith('"')):
        input_string = input_string.replace("'", "")
        input_string = input_string.replace('"', "")
        for text in data:
            for sent in text['sentences']:
                if input_string in sent['sentence']:
                    answer_1 = []
                    answer_1.append(text["link"])
                    answer_1.append(text["date"])
                    answer_1.append(text["title"])
                    answer_1.append(sent["sentence"])
                    answer.append(answer_1)
        return answer

    search_tokens = []
    search_lemmas = []
    search_tags = []
    search_types = []

    reg_pos_and_word = re.compile("[А-Яа-яёЁ].*\+[A-Z].*$")
    reg_pos = re.compile("^[A-Z].*")
    reg_word = re.compile("[а-яёЁА-Я]")

    for x in input_string.lower():
        if x in '!#$%&\()*,./:;<=>?@[\\]^_`{|}~«»1234567890':
            input_string = input_string.replace(x, "")

    tokens = input_string.split()
    print(tokens)
    for token in tokens:

        # если в кавычках
        if (token.startswith("'") and input_string.endswith("'")) or (
                token.startswith('"') and input_string.endswith('"')):
            token = token.replace("'", "")
            token = token.replace('"', "")
            token = token.lower()
            search_tokens.append(token)
            search_tags.append(0)
            search_lemmas.append(0)
            search_types.append('qoutes')

        # если со знаком +: слово+тэг
        elif re.search(reg_pos_and_word, token) != None:
            pos_and_word = token.split('+')
            if len(pos_and_word) == 2:
                word = pos_and_word[0]
                tag = pos_and_word[1]
                search_tokens.append(word)
                search_tags.append(tag)
                parsed = morph.parse(word)[0]
                search_lemmas.append(parsed.normal_form)
                search_types.append('word_and_tag')
                # улучшить

        # если слово
        elif re.search(reg_word, token) != None:
            search_tokens.append(token)
            parsed = morph.parse(token)[0]
            search_tags.append(parsed.tag.POS)
            search_lemmas.append(parsed.normal_form)
            search_types.append('word')
            # улучшить

        # если тэг
        elif re.search(reg_pos, token) != None:
            search_tokens.append(0)
            search_tags.append(token)
            search_lemmas.append(0)
            search_types.append('tag')

        else:
            pass

    print('search_tokens', search_tokens, 'search_tags', search_tags, 'search_lemmas', search_lemmas, search_types)

    # поиск
    if len(search_tokens) > 0:
        for text in data:
            for sent in text["sentences"]:
                for j in range(len(sent["words"]) - len(search_tokens) + 1):
                    seq = []
                    for m in range(len(search_tokens)):
                        if search_types[m] == 'qoutes':
                            if search_tokens[m] in sent["words"][j + m]["word"]:
                                seq.append(sent["words"][j + m]["word"])
                        elif search_types[m] == 'word_and_tag':
                            if search_lemmas[m] in sent["words"][j + m]["lemma"] and search_tags[m] in \
                                    sent["words"][j + m]["POS"]:
                                seq.append(sent["words"][j + m]["word"])
                        elif search_types[m] == 'word':
                            if search_lemmas[m] in sent["words"][j + m]["lemma"] or search_tokens[m] in \
                                    sent["words"][j + m]["word"]:
                                seq.append(sent["words"][j + m]["word"])
                        elif search_types[m] == 'tag':
                            if search_tags[m] in sent["words"][j + m]["POS"]:
                                seq.append(sent["words"][j + m]["word"])
                        else:
                            break

                    if len(seq) == len(search_tokens):
                        answer_1 = []
                        answer_1.append(text["link"])
                        answer_1.append(text["date"])
                        answer_1.append(text["title"])
                        answer_1.append(sent["sentence"])
                        answer.append(answer_1)

    if answer == []:
        answer = 'Простите, в нашем корпусе ничего не нашлось по вашему запросу! Проверьте запрос на корректность.'
    return answer


if __name__ == '__main__':
    app.run()
    
