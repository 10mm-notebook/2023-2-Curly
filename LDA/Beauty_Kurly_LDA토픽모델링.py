# 필요한 라이브러리 가져오기
from konlpy.tag import Mecab
from tqdm import tqdm
import re
import csv
import pandas as pd
from pandas import DataFrame
import numpy as np
import os
from gensim import corpora
import gensim
import logging
from pprint import pprint
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis
from gensim.models.ldamodel import LdaModel

# 1. 데이터 전처리

# Gensim을 위한 로깅 설정
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# 데이터 파일 경로 설정
title = os.path.basename('C:/Users/zoo55/OneDrive/바탕 화면/DATA/CUK-data-Revised/Data-Revised/Beauty_kurly.csv')

# 텍스트 정제
def clean_text(text): 
    text = text.replace(".", "").strip()
    text = text.replace("·", " ").strip()
    pattern = '[^ ㄱ-ㅣ가-힣|0-9]+'
    text = re.sub(pattern=pattern, repl='', string=text)
    return text

# URL 복사 이웃추가' ~ '기타 보내기 펼치기' 사이의 텍스트 수집
def preprocess(content): 
    result = re.findall(r'URL 복사 이웃추가(.*?)기타 보내기 펼치기', content, re.DOTALL)
    return [x.strip() for x in result]

# Mecab 토크나이저를 사용하여 일반/고유명사, 형용사, 어근 추출
def get_nouns(tokenizer, sentence): 
    tagged = tokenizer.pos(sentence)
    nouns = [s for s, t in tagged if t in ['NNG', 'NNP', 'VA', 'XR'] and len(s) > 1]
    return nouns if len(nouns) > 0 else None

# 토큰화
def tokenize(df): 
    tokenizer = Mecab(dicpath='C:/mecab/mecab-ko-dic')
    processed_data = []
    for sent in tqdm(df['content']):
        # 전처리 적용
        posts = preprocess(sent)
        for post in posts:
            processed_post = get_nouns(tokenizer, post)
            # 명사 리스트가 None이 아닌 경우에만 추가
            if processed_post is not None:
                processed_data.append(processed_post)
    return processed_data

# 전처리된 데이터를 CSV 파일로 저장
def save_processed_data(processed_data): 
    with open("tokenized_data_"+title, 'w', newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        for data in processed_data:
            writer.writerow(data)

# 메인 코드
if __name__ == '__main__':
    # CSV 파일에서 데이터 읽기
    df = pd.read_csv('C:/Users/zoo55/OneDrive/바탕 화면/DATA/CUK-data-Revised/Data-Revised/Beauty_kurly.csv')
    df.columns = ['title','nickname','datetime','content']
    df = df.dropna(how='any')
    
    # 데이터 토큰화 및 전처리
    processed_data = tokenize(df)
    
    # 전처리된 데이터 저장
    save_processed_data(processed_data)

# 전처리된 데이터 불러오기
processed_data = [sent.strip().split(",") for sent in tqdm(open("tokenized_data_"+title,'r',encoding='utf-8').readlines())]
processed_data = DataFrame(processed_data)
processed_data[0] = processed_data[0].replace("", np.nan)
processed_data = processed_data[processed_data[0].notnull()]
processed_data = processed_data.values.tolist()
processed_data2=[]

for i in processed_data:
    i = list(filter(None, i))
    processed_data2.append(i)
processed_data = processed_data2

print(processed_data)

# 2. LDA 토픽 모델링 - (1) Bag of Words

# 빈 리스트 제거
processed_data = [data for data in processed_data if data]

# 고유한 단어들의 사전 생성
dictionary = corpora.Dictionary(processed_data)
dictionary.filter_extremes(no_below=2, no_above=0.4)
corpus = [dictionary.doc2bow(text) for text in processed_data if text]

num_topics = 10
chunksize = 2000
passes = 20
iterations = 400
eval_every = None

temp = dictionary[0]
id2word = dictionary.id2token

# 2. LDA 토픽 모델링 - (2) 모델 학습

model = LdaModel(
    corpus=corpus,
    id2word=id2word,
    chunksize=chunksize,
    alpha='auto',
    eta='auto',
    iterations=iterations,
    num_topics=num_topics,
    passes=passes,
    eval_every=eval_every)

# 상위 토픽들 가져오기
top_topics = model.top_topics(corpus)

# 평균 토픽 일관성 계산
avg_topic_coherence = sum([t[1] for t in top_topics]) / num_topics
print('평균 토픽 일관성: %.4f.' % avg_topic_coherence)

# 상위 토픽 출력
pprint(top_topics)

# 3. 시각화

# pyLDAvis를 사용하여 시각화 생성
lda_visualization = gensimvis.prepare(model, corpus, dictionary, sort_topics=False)

# 시각화를 HTML 파일로 저장
html_path = f'C:/Users/zoo55/Documents/Beauty_{num_topics}.html'
pyLDAvis.save_html(lda_visualization, html_path)
