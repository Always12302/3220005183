from gensim.models import Word2Vec
import pandas as pd
import jieba

df = pd.read_csv('input/train.csv') # 读取训练数据
p = df['sentence1'].values # 拿到原句子
h = df['sentence2'].values # 拿到目标句子
p_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), p)) # 将句子去空格再使用分词器 生成词语列表
h_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), h))
common_texts = [] # 建一个空列表用来存放词语列表
common_texts.extend(p_seg) # 加入词语列表库
common_texts.extend(h_seg)

df = pd.read_csv('input/dev.csv') # 读取验证数据
p = df['sentence1'].values
h = df['sentence2'].values
p_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), p))
h_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), h))
common_texts.extend(p_seg)
common_texts.extend(h_seg)

df = pd.read_csv('input/test.csv') # 读取训练数据
p = df['sentence1'].values
h = df['sentence2'].values
p_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), p))
h_seg = list(map(lambda x: list(jieba.cut(x.replace(" ",""))), h))
common_texts.extend(p_seg)
common_texts.extend(h_seg)
model = Word2Vec(common_texts, size=100, window=5, min_count=3, workers=12) # 用词语生成的词向量模型

model.save("input/word2vec/word2vec.model") # 保存用词语生成的词向量模型
model.wv.save_word2vec_format('input/word2vec/word2vec.bin',binary=False) 
word_set = set() # 建一个空集合用来存放词语
for sample in common_texts: # 每个词语列表
    for word in sample: # 词语列表中的每个词语
        word_set.add(word) # 加入词语库
with open('input/word2vec/word_vocab.txt','w',encoding='utf8') as f:
    f.write("\n".join(sorted(list(word_set),reverse=True))) # 保存词语库

p_seg = list(map(lambda x: list(x.replace(" ","")), p)) # 将句子去空格 生成句子
h_seg = list(map(lambda x: list(x.replace(" ","")), h))
common_texts = [] # 建一个空列表用来存放句子
common_texts.extend(p_seg) # 加入句子库
common_texts.extend(h_seg)

df = pd.read_csv('input/dev.csv')
p = df['sentence1'].values
h = df['sentence2'].values
p_seg = list(map(lambda x: list(x.replace(" ","")), p))
h_seg = list(map(lambda x: list(x.replace(" ","")), h))
common_texts.extend(p_seg)
common_texts.extend(h_seg)

df = pd.read_csv('input/train.csv')
p = df['sentence1'].values
h = df['sentence2'].values
p_seg = list(map(lambda x: list(x.replace(" ","")), p))
h_seg = list(map(lambda x: list(x.replace(" ","")), h))
common_texts.extend(p_seg)
common_texts.extend(h_seg)
model = Word2Vec(common_texts, size=100, window=5, min_count=3, workers=12) # 用单字生成的词向量模型

model.save("input/word2vec/char2vec.model") # 保存用单字生成的词向量模型
model.wv.save_word2vec_format('input/word2vec/char2vec.bin',binary=False) 
char_set = set() # 建一个空集合用来存放单字
for sample in common_texts: # 每个句子
    for char in sample: # 句子中的每个单字
        char_set.add(char) # 加入单字库
with open('input/word2vec/char_vocab.txt','w',encoding='utf8') as f:
    f.write("\n".join(sorted(list(char_set),reverse=True))) # 保存单字库