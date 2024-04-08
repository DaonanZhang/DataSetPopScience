import os

import pandas as pd
import textstat
import cntext as ct
import re
import csv

def fk_ari_score(text):
    return textstat.textstat.flesch_kincaid_grade(text), textstat.textstat.automated_readability_index(text)

# readability1 ---Average number of words per sentence.
# readability2 ---The proportion of adverbs and conjunctions in each sentence.
# readability3 ---Referring to the Fog Index, readability3 is calculated as the sum of readability1 and readability2, multiplied by 0.5.
def cn_readability(text):
    return ct.readability(text)

def jp_readability(text):
    ratio_dict, _, ls, cp = jp_text_calculation(text)

    # pc = percentage['kanji'] if 'kanji' in percentage else 0
    # ph = percentage['hiragana'] if 'hiragana' in percentage else 0
    # pk = percentage['katakana'] if 'katakana' in percentage else 0
    # pa = percentage['roman'] if 'roman' in percentage else 0

    lc = ratio_dict['kanji'] if 'kanji' in ratio_dict else 0
    lh = ratio_dict['hiragana'] if 'hiragana' in ratio_dict else 0
    lk = ratio_dict['katakana'] if 'katakana' in ratio_dict else 0
    la = ratio_dict['roman'] if 'roman' in ratio_dict else 0

    rs = -0.12*ls-1.37*la+7.4*lh-23.18*lc-5.4*lk-4.67*cp + 115.79
    return rs


def jp_text_calculation(text):

    num_period = len(re.findall(r'。', text))
    num_exclamation = len(re.findall(r'！', text))
    num_question = len(re.findall(r'？', text))
    num_period = num_period + num_exclamation + num_question

    num_comma = len(re.findall(r'、', text))
    num_dunhao = len(re.findall(r'，', text))
    num_comma = num_comma + num_dunhao
    cp = num_comma / num_period if num_period > 0 else 0

    sentences = re.split(r'[。！？]', text)
    sentences = [sentence.strip() for sentence in sentences if sentence]
    num_sentences = len(sentences)
    ls = sum(len(sentence) for sentence in sentences) / num_sentences

    lengths = {}
    amount_run = {}

    for sentence in sentences:
        runs = split_into_runs(sentence)

        for key, value in runs.items():
            if value not in amount_run:
                amount_run[value] = 1
            else:
                amount_run[value] += 1
            runs[key] = (value, len(key))

        for run_type, (run_value, run_length) in runs.items():
            if run_value not in lengths:
                lengths[run_value] = run_length
            else:
                lengths[run_value] += run_length

    # print(amount_run)
    # print(lengths)
    ratio_dict = {}
    for key in lengths:
       if key in amount_run and amount_run[key] > 0:
           ratio_dict[key] = lengths[key] / amount_run[key]

    # print(amount_run)
    total = sum(amount_run.values())
    percentage = {key: value / total for key, value in amount_run.items()}
    # print(percentage)

    # print(ratio_dict)

    return ratio_dict, percentage, ls, cp

def split_into_runs(text):
    runs = {}
    current_run = ""
    prev_char_type = None

    for char in text:
        char_type = get_character_type(char)

        if char_type == prev_char_type:
            current_run += char
        else:
            if current_run:
                runs[current_run] = prev_char_type
            current_run = char
            prev_char_type = char_type

    if current_run:
        runs[current_run] = prev_char_type

    return runs

def get_character_type(char):
    # 使用Unicode范围来确定字符类型
    if re.match(r'[\u3040-\u309F]', char):  # 平假名
        return "hiragana"
    elif re.match(r'[\u30A0-\u30FF]', char):  # 片假名
        return "katakana"
    elif re.match(r'[\u4E00-\u9FFF]', char):  # 汉字
        return "kanji"
    elif re.match(r'[a-zA-Z]', char):  # 罗马字母
        return "roman"
    elif re.match(r'[,、]', char):  # 日语逗号
        return "roman"
    elif re.match(r'[。！？]', char):  # 句号
        return "roman"
    else:
        return "roman"



if __name__ == "__main__":
    folder = "F:\DataSetPopScience\ParallelCorpus\\NatureJP\store"
    file_list = os.listdir(folder)

    for file in file_list:
        # # for lexical corpus
        # file = os.path.join(folder, file)
        # if 'href' not in file:
        #     df = pd.read_csv(file, encoding='latin-1')
        #     df['Explanation_fk_score'] = df['Explanation'].apply(lambda x: fk_ari_score(x)[0])
        #     df['Explanation_ari_score'] = df['Explanation'].apply(lambda x: fk_ari_score(x)[1])
        #     df.to_csv(os.path.join(folder,f'{file}_new.csv'), index=False, encoding='latin-1')
        #     print(f'{file} is done')

        file_path = os.path.join(folder, file)
        df = pd.read_csv(file_path, encoding='UTF-8')
        print(f'read file done')

        print(len(df))

        # # only for english and germany
        # df['abstract_fk_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[0])
        # df['abstract_ari_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[1])
        # df['article_fk_score'] = df['pls'].apply(lambda x: fk_ari_score(x)[0])
        # df['article_ari_score'] = df['pls'].apply(lambda x: fk_ari_score(x)[1])

        # for chinese
        # df['abstract_fk_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[0])
        # df['abstract_ari_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[1])
        # df['article_cn_score'] = df['pls'].apply(lambda x: cn_readability(x))


        # # for japanese
        # df['abstract_fk_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[0])
        # df['abstract_ari_score'] = df['abstract'].apply(lambda x: fk_ari_score(x)[1])
        # df['article_jp_score'] = df['pls'].apply(lambda x: jp_readability(x))

        # only for parallel corpus
        # df.drop(['fk_score', 'ari_score'], axis=1, inplace=True)
        # df.to_csv(os.path.join(folder,f'{file}_new.csv'), index=False, encoding='UTF-8')
        # print(f'{file} is done')





