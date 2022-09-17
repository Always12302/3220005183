import keras
from utils.data_utils import shuffle, pad_sequences
from keras.models import Model
import tensorflow as tf
import numpy as np
import sys
sys.path.append( '../')

np.random.seed(1)
tf.set_random_seed(1)

class BaseModel(object):

    def __init__(self, params):

        self._params = params

    def make_embedding_layer(self, name='embedding', **kwargs):

        def init_embedding(weights=None):

            input_dim = self._params['max_features']
            output_dim = self._params['embed_size']

            return keras.layers.Embedding(
                input_dim=input_dim,
                output_dim=output_dim,
                trainable=False,
                name=name,
                weights=weights,
                **kwargs)

        embedding = init_embedding()

        return embedding

    def _make_multi_layer_perceptron_layer(self) -> keras.layers.Layer:

        def _wrapper(x):
            activation = 'relu'
            for _ in range(self._params['mlp_num_layers']):
                x = keras.layers.Dense(self._params['mlp_num_units'],
                                       activation=activation)(x)
            return keras.layers.Dense(self._params['mlp_num_fan_out'],
                                      activation=activation)(x)

        return _wrapper

    def _make_inputs(self) -> list:
        input_left = keras.layers.Input(
            name='text_left',
            shape=self._params['input_shapes'][0]
        )
        input_right = keras.layers.Input(
            name='text_right',
            shape=self._params['input_shapes'][1]
        )
        return [input_left, input_right]

    def _make_output_layer(self) -> keras.layers.Layer:

        return keras.layers.Dense(2, activation='softmax')

    def _create_base_network(self):

        def _wrapper(x):

            pass

        return _wrapper

    def build(self):

        pass

        return model

class CDSSM(BaseModel):

    def _create_base_network(self):

        def _wrapper(x):

            x = self.embedding(x)
            x = keras.layers.Conv1D(
                filters=self._params['filters'],
                kernel_size=self._params['kernel_size'],
                strides=1,
                padding='same',
                activation='relu',
                kernel_initializer='random_uniform',
                bias_initializer='zeros')(x)
            x = keras.layers.Dropout(self._params['dropout_rate'])(x)
            x = keras.layers.GlobalMaxPool1D()(x)
            x = self._make_multi_layer_perceptron_layer()(x)
            return x

        return _wrapper

    def build(self):

        self.embedding = self.make_embedding_layer()
        base_network = self._create_base_network()
        input_left, input_right = self._make_inputs()
        x = [base_network(input_left),
             base_network(input_right)]
        x = keras.layers.Dot(axes=[1, 1], normalize=True)(x)
        x_out = self._make_output_layer()(x)
        model = Model(inputs=[input_left, input_right],
                              outputs=x_out)
        return model

base_params = {
    'max_features':8,
    'embed_size':20,
    'filters':200, # 卷积核数量
    'kernel_size':3, # 卷积核大小
    'dropout_rate':0.2,
    'mlp_num_layers':1,
    'mlp_num_units':16,
    'mlp_num_fan_out':16,
    'input_shapes':[(40000,),(40000,)], # 句子最大长度
}

if __name__ == '__main__':

    paper_text_path = 'paper_text.txt'
    paper_fake_path = 'paper_add.txt'
    ans_number_path = 'similarity_number_1.txt'
    paper_text = open(paper_text_path, "r",encoding='utf-8')
    org = paper_text.read()
    paper_fake = open(paper_fake_path, "r",encoding='utf-8')
    add = paper_fake.read()
    p_seg = list(map(lambda x: list(x.replace(" ","")), org))
    h_seg = list(map(lambda x: list(x.replace(" ","")), add))
    common_texts = []
    common_texts.extend(p_seg)
    common_texts.extend(h_seg)
    char_set = set() # 建一个空集合用来存放单字
    for sample in common_texts: # 每个句子
        for char in sample: # 句子中的每个单字
            char_set.add(char) # 加入单字库
    vocab = sorted(list(char_set),reverse=True)
    p = [org]
    h = [add]
    label = [1]
    p, h, _ = shuffle(p, h, label)
    word2idx = {word: index for index, word in enumerate(vocab,start=1)}
    idx2word = {index: word for index, word in enumerate(vocab,start=1)}
    p_list, h_list = [], []
    for p_sentence, h_sentence in zip(p, h):
        p = [word2idx[word.lower()] for word in p_sentence if len(word.strip()) > 0 and word.lower() in word2idx.keys()]
        h = [word2idx[word.lower()] for word in h_sentence if len(word.strip()) > 0 and word.lower() in word2idx.keys()]
        p_list.append(p)
        h_list.append(h)
    p_c_index = pad_sequences(p_list, maxlen=40000)
    h_c_index = pad_sequences(h_list, maxlen=40000)
    x_test = [p_c_index, h_c_index]

    params = base_params
    backend = CDSSM(params)
    model = backend.build() # 建立模型
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
