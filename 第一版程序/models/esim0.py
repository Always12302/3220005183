#encoding=utf8
import keras
from keras.models import Model
import tensorflow as tf 
import numpy as np 
import sys
sys.path.append( '../')
from engine.base_model import BaseModel
from engine.layers import SoftAttention


class ESIM(BaseModel):
    """docstring for ESIM"""
    def build(self):
        """
        Build the model.
        """
        a, b = self._make_inputs() # 定义两个输入

        # ---------- Embedding layer ---------- #
        embedding = self.make_embedding_layer() # 定义一个词向量层作为两个输入的共享embedding
        embedded_a = embedding(a)
        embedded_b = embedding(b)

        # ---------- Encoding layer ---------- #
        # encoded_a = keras.layers.Bidirectional(keras.layers.LSTM(
        #     self._params['lstm_units'],
        #     return_sequences=True,
        #     dropout=self._params['dropout_rate']
        # ))(embedded_a)
        # encoded_b = keras.layers.Bidirectional(keras.layers.LSTM(
        #     self._params['lstm_units'],
        #     return_sequences=True,
        #     dropout=self._params['dropout_rate']
        # ))(embedded_b)

        bilstm = keras.layers.Bidirectional(keras.layers.LSTM( # 共享参数的bilstm结构 提取query和doc的语义向量
                    self._params['lstm_units'],
                    return_sequences=True,
                    dropout=self._params['dropout_rate']
                ))

        encoded_a = bilstm(embedded_a) # 把隐藏状态的值保留下来
        encoded_b = bilstm(embedded_b)

        # ---------- Local inference layer ---------- # 本地推理层
        atten_a, atten_b = SoftAttention()([encoded_a, encoded_b]) # 词向量相乘 如果两个词相似乘积较大 softmax求出权重
        # atten_a = 权重 * encoded_b
        # atten_b = 权重 * encoded_a

        sub_a_atten = keras.layers.Lambda(lambda x: x[0]-x[1])([encoded_a, atten_a])
        sub_b_atten = keras.layers.Lambda(lambda x: x[0]-x[1])([encoded_b, atten_b])

        mul_a_atten = keras.layers.Lambda(lambda x: x[0]*x[1])([encoded_a, atten_a])
        mul_b_atten = keras.layers.Lambda(lambda x: x[0]*x[1])([encoded_b, atten_b])

        # ESIM主要是计算新旧序列之间的差和积 并把所有信息合并起来储存在一个序列中？
        m_a = keras.layers.concatenate([encoded_a, atten_a, sub_a_atten, mul_a_atten])
        m_b = keras.layers.concatenate([encoded_b, atten_b, sub_b_atten, mul_b_atten])

        # ---------- Inference composition layer ---------- # 推理成分层
        # ESIM最后还需要综合所有信息 做一个全局的分析 这个过程依然是通过BiLSTM处理这两个序列
        composition_a = keras.layers.Bidirectional(keras.layers.LSTM(
            self._params['lstm_units'],
            return_sequences=True,
            dropout=self._params['dropout_rate']
        ))(m_a)

        # 因为考虑到求和运算对于序列长度是敏感的 因而降低了模型的鲁棒性 所以ESIM选择同时对两个序列进行average pooling和max pooling
        avg_pool_a = keras.layers.GlobalAveragePooling1D()(composition_a)
        max_pool_a = keras.layers.GlobalMaxPooling1D()(composition_a)

        composition_b = keras.layers.Bidirectional(keras.layers.LSTM(
            self._params['lstm_units'],
            return_sequences=True,
            dropout=self._params['dropout_rate']
        ))(m_b)

        avg_pool_b = keras.layers.GlobalAveragePooling1D()(composition_b)
        max_pool_b = keras.layers.GlobalMaxPooling1D()(composition_b)

        pooled = keras.layers.concatenate([avg_pool_a, max_pool_a, avg_pool_b, max_pool_b])
        pooled = keras.layers.Dropout(rate=self._params['dropout_rate'])(pooled)

        # ---------- Classification layer ---------- # 分类层
        mlp = self._make_multi_layer_perceptron_layer()(pooled) # 送入多层感知机
        mlp = keras.layers.Dropout(
            rate=self._params['dropout_rate'])(mlp)

        prediction = self._make_output_layer()(mlp) # 输出层使用softmax进行分类

        model = Model(inputs=[a, b], outputs=prediction)

        return model