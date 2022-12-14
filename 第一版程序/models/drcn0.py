#encoding=utf8
import keras
from keras.models import Model
import keras.backend as K
import tensorflow as tf 
import numpy as np 
import sys
sys.path.append( '../')
from engine.base_model import BaseModel
from engine.layers import SoftAttention

class DRCN(BaseModel):
    """docstring for DRCN"""
    def _make_inputs(self):

        input_left_char = keras.layers.Input(
            name='char_left',
            shape=self._params['input_shapes'][0]
        )
        input_right_char = keras.layers.Input(
            name='char_right',
            shape=self._params['input_shapes'][1]
        )
        input_left_word = keras.layers.Input(
            name='word_left',
            shape=self._params['input_shapes'][2]
        )
        input_right_word = keras.layers.Input(
            name='word_right',
            shape=self._params['input_shapes'][3]
        )
        input_same_word = keras.layers.Input(
            name='same_word',
            shape=(1,)
        )

        return [input_left_char, input_right_char,input_left_word,\
                input_right_word,input_same_word]

    def _rnn_densenet_block(self, left, right):

        for i in range(2):
            rep_left, rep_right = left, right

            # rep_left = keras.layers.Bidirectional(keras.layers.LSTM(
            #     self._params['lstm_units'],
            #     return_sequences=True,
            #     dropout=self._params['dropout_rate']
            # ))(left)
            # rep_right = keras.layers.Bidirectional(keras.layers.LSTM(
            #     self._params['lstm_units'],
            #     return_sequences=True,
            #     dropout=self._params['dropout_rate']
            # ))(right)
            bilstm = keras.layers.Bidirectional(keras.layers.LSTM( # 共享参数的bilstm结构 提取query和doc的语义向量
                self._params['lstm_units'],
                return_sequences=True,
                dropout=self._params['dropout_rate']
            ))

            rep_left = bilstm(left) # 把隐藏状态的值保留下来
            rep_right = bilstm(right)
            
            atten_left, atten_right = SoftAttention()([rep_left, rep_right]) # 词向量相乘 如果两个词相似乘积较大 softmax求出权重
            # atten_left = 权重 * rep_right
            # atten_right = 权重 * rep_left

            # 包含残差连接 最大程度的保留了各自的独有信息
            left = keras.layers.concatenate([left,atten_left,rep_left], axis=-1)
            right = keras.layers.concatenate([right,atten_right,rep_right], axis=-1)

            # 这种dense连接会使随着模型的加深 参数越来越多 使用AutoEncoder作为瓶颈组件来压缩向量表示 减少特征数量 同时可以保持原始的信息
            left = keras.layers.normalization.BatchNormalization()(left)
            right = keras.layers.normalization.BatchNormalization()(right)

        left = keras.layers.Dense(units = 64, 
            activation = self._params['mlp_activation_func']
            )(left)
        right = keras.layers.Dense(units = 64, 
            activation = self._params['mlp_activation_func']
            )(right)

        left = keras.layers.normalization.BatchNormalization()(left)
        right = keras.layers.normalization.BatchNormalization()(right)

        return left, right

    def build(self):
        p_c,h_c,p_w,h_w,same_word = self._make_inputs()

        # ---------- Embedding layer ---------- #
        # word embedding通过两种方式构建 一种是可训练的(容易过拟合) 一种是固定的(缺少灵活性)
        char_embedding = self.make_embedding_layer(name='char_embedding')
        embedded_p_c = char_embedding(p_c)
        embedded_h_c = char_embedding(h_c)

        word_embedding = self.make_embedding_layer(name='word_embedding',embed_type='word')
        embedded_p_w = word_embedding(p_w)
        embedded_h_w = word_embedding(h_w)

        # same = keras.layers.Lambda(self._expand)(same_word)
        # 结合两种词向量
        p = keras.layers.concatenate([embedded_p_c, embedded_p_w], axis=-1)
        h = keras.layers.concatenate([embedded_h_c, embedded_h_w], axis=-1)

        # 字符级别的表示Char-Conv 通过在CNN(max pooling)中随机初始化字符向量获得
        # 将字符嵌入通过一维卷积核过滤 然后将字符卷积特征map进行max pooling获得字符向量
        p = keras.layers.SpatialDropout1D(0.2)(p)
        h = keras.layers.SpatialDropout1D(0.2)(h)

        # 连接RNN
        for i in range(self._params['num_blocks']):
            p, h = self._rnn_densenet_block(p, h)

        # interaction and prediction layer
        sub_p_h = keras.layers.Lambda(lambda x: x[0]-x[1])([p, h]) # 交叉方式
        add_p_h = keras.layers.Lambda(lambda x: x[0]+x[1])([p, h])
        norm_p_h = keras.layers.Lambda(self._expend_norm)(sub_p_h)
        # 聚合特征
        prediction = keras.layers.concatenate(
            [p, h, sub_p_h, add_p_h, norm_p_h], 
            axis=-1)
        # _,r,c = prediction.get_shape()
        prediction = keras.layers.Flatten()(prediction)
        prediction = keras.layers.normalization.BatchNormalization()(prediction)
        prediction = self._make_multi_layer_perceptron_layer()(prediction) # 送入两层ReLU激活的全连接层
        prediction = self._make_output_layer()(prediction) # 输出层使用softmax进行分类

        model = Model(inputs=[p_c,h_c,p_w,h_w], outputs=prediction)

        return model

    def _expand(self,x):
        x = K.expand_dims(x, axis=-1)
        x = K.tile(x, [1,self._params['input_shapes'][0][0],1])
        return x

    def _expend_norm(self,x):
        return K.expand_dims(tf.norm(x, axis=-1))