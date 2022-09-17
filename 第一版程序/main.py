#encoding=utf8

import tensorflow as tf 
import keras 
import numpy as np
import sys
import csv
sys.path.append('../')
from models.cdssm import CDSSM
from models.mvlstm import MVLSTM
from models.arcii import ArcII
from models.esim import ESIM
from models.match_pyramid import MatchPyramid
from models.drcn import DRCN
from utils.load_data import load_char_data,load_word_embed,load_char_embed,load_all_data
from line_profiler_pycharm import profile


np.random.seed(1)
tf.set_random_seed(1)

base_params = {
    'num_classes':2, # 二分类
    'max_features':1700,
    'embed_size':200,
    'filters':300, # 卷积核数量
    'kernel_size':3, # 卷积核大小
    'strides':1,
    'padding':'same',
    'conv_activation_func':'relu', # 激活函数
    'embedding_matrix':[],
    'w_initializer':'random_uniform',
    'b_initializer':'zeros',
    'dropout_rate':0.2,
    'mlp_activation_func':'relu',
    'mlp_num_layers':1,
    'mlp_num_units':128,
    'mlp_num_fan_out':128,
    'input_shapes':[(35000,),(35000,)], # 句子最大长度
    'task':'Classification',
}

@profile
def work():

    paper_text_path = 'paper_text.txt'
    paper_fake_path = 'paper_add.txt'
    ans_number_path = 'similarity_number_1.txt'
    paper_text = open(paper_text_path, "r", encoding='utf-8')
    org = paper_text.read()
    paper_fake = open(paper_fake_path, "r", encoding='utf-8')
    add = paper_fake.read()
    with open('input/work.csv', "w", encoding='gbk') as work_path:
        title = ['sentence1', 'sentence2', 'label']
        writer = csv.DictWriter(work_path, fieldnames=title)
        writer.writeheader()
        writer.writerow({'sentence1': org, 'sentence2': add, 'label': 1})

    model_name = "esim"

    if model_name == "cdssm":
        params = base_params
        backend = CDSSM(params)
    elif model_name == "mvlstm":
        mvlstm_params = base_params
        mvlstm_params['lstm_units'] = 64
        mvlstm_params['top_k'] = 50
        mvlstm_params['mlp_num_units'] = 128
        mvlstm_params['mlp_num_fan_out'] = 128
        mvlstm_params['dropout_rate'] = 0.3
        mvlstm_params['embed_size'] = 100
        char_embedding_matrix = load_char_embed(mvlstm_params['max_features'], mvlstm_params['embed_size'])
        mvlstm_params['embedding_matrix'] = char_embedding_matrix
        params = mvlstm_params
        backend = MVLSTM(params)
    elif model_name == "arcii":
        arcii_params = base_params
        arcii_params['matching_type'] = 'dot'
        arcii_params['num_blocks'] = 3
        arcii_params['kernel_1d_count'] = 32
        arcii_params['kernel_1d_size'] = 3
        arcii_params['kernel_2d_count'] = [16, 32, 32]
        arcii_params['kernel_2d_size'] = [[3, 3], [3, 3], [3, 3]]
        arcii_params['pool_2d_size'] = [[2, 2], [2, 2], [2, 2]]
        arcii_params['dropout_rate'] = 0.5
        params = arcii_params
        backend = ArcII(params)
    elif model_name == "esim":
        esim_params = base_params
        esim_params['mlp_num_layers'] = 1
        esim_params['mlp_num_units'] = 256
        esim_params['mlp_num_fan_out'] = 128
        esim_params['lstm_units'] = 64
        esim_params['dropout_rate'] = 0.3
        esim_params['embed_size'] = 100
        char_embedding_matrix = load_char_embed(esim_params['max_features'], esim_params['embed_size'])
        esim_params['embedding_matrix'] = char_embedding_matrix
        params = esim_params
        backend = ESIM(params)
    elif model_name == "match_pyramid":
        mp_params = base_params
        mp_params['matching_type'] = 'dot'
        mp_params['num_blocks'] = 2
        mp_params['kernel_count'] = [16, 32]
        mp_params['kernel_size'] = [[3, 3], [3, 3]]
        mp_params['pool_size'] = [3, 3]
        mp_params['mlp_num_layers'] = 1
        mp_params['mlp_num_units'] = 128
        mp_params['mlp_num_fan_out'] = 128
        mp_params['embed_size'] = 100
        char_embedding_matrix = load_char_embed(mp_params['max_features'], mp_params['embed_size'])
        mp_params['embedding_matrix'] = char_embedding_matrix
        params = mp_params
        backend = MatchPyramid(params)
    elif model_name == "drcn":
        drcn_params = base_params
        drcn_params['input_shapes'] = [(48,), (48,), (48,), (48,)]
        drcn_params['lstm_units'] = 64
        drcn_params['num_blocks'] = 1
        drcn_params['mlp_num_layers'] = 1
        drcn_params['mlp_num_units'] = 256
        drcn_params['mlp_num_fan_out'] = 128
        drcn_params['max_features'] = 1700
        drcn_params['word_max_features'] = 7300
        drcn_params['word_embed_size'] = 100
        drcn_params['embed_size'] = 100

        word_embedding_matrix = load_word_embed(drcn_params['word_max_features'], drcn_params['word_embed_size'])
        char_embedding_matrix = load_char_embed(drcn_params['max_features'], drcn_params['embed_size'])

        drcn_params['embedding_matrix'] = char_embedding_matrix
        drcn_params['word_embedding_matrix'] = word_embedding_matrix

        params = drcn_params
        backend = DRCN(params)

    if model_name == "drcn":  # 如果是drcn 就额外需要词语生成的词向量模型
        p_c_index_test, h_c_index_test, p_w_index_test, h_w_index_test, same_word_test, y_test = load_all_data(
            './input/work.csv', maxlen=params['input_shapes'][0][0])
        x_test = [p_c_index_test, h_c_index_test, p_w_index_test, h_w_index_test]
        y_test = keras.utils.to_categorical(y_test, num_classes=params['num_classes'])
    else:  # 如果不是drcn 就是用单字生成的词向量模型
        p_test, h_test, y_test = load_char_data('input/work.csv', data_size=None,
                                                maxlen=params['input_shapes'][0][0])  # 测试集
        x_test = [p_test, h_test]
        y_test = keras.utils.to_categorical(y_test, num_classes=params['num_classes'])

    model = backend.build()  # 建立模型

    bast_model_filepath = './output/best_%s_model.h5' % model_name

    model.load_weights(bast_model_filepath)  # 加载权重
    model.compile(  # 编译
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    similarity_number = model.predict(  # 预测相似度
        x=x_test,
    )

    with open(ans_number_path, "w") as ans_number:
        for ans in similarity_number:
            ans_number.write(str(ans[1]))


if __name__ == '__main__':

    work()