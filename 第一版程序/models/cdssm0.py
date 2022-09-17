import keras
from keras.models import Model
import tensorflow as tf
import numpy as np
import sys
import os
sys.path.append( '../')
from engine.base_model import BaseModel

np.random.seed(1)
tf.set_random_seed(1)


class CDSSM(BaseModel):

    def _create_base_network(self): # 定义网络基本结构

        def _wrapper(x):

            x = self.embedding(x) # 定义embedding层
            x = keras.layers.Conv1D(
                filters=self._params['filters'], # 输出的维度
                kernel_size=self._params['kernel_size'], # 一个维度的长度
                strides=self._params['strides'], # 卷积的步长
                padding=self._params['padding'], # 控制填充 为same时输出与输入一样大小
                activation=self._params['conv_activation_func'], # 激活函数
                kernel_initializer=self._params['w_initializer'], # 应用于核矩阵的约束函数
                bias_initializer=self._params['b_initializer'])(x) # 应用于偏置向量的约束函数
            # 通过在每个维度上取最大值来应用最大池化
            # 所有 word_trigram 功能
            x = keras.layers.Dropout(self._params['dropout_rate'])(x) # 保留率0.8
            x = keras.layers.GlobalMaxPool1D()(x) # 时态数据的全局最大池化操作
            # 使用 tanh 层应用非线性变换
            x = self._make_multi_layer_perceptron_layer()(x) # 此处是多层感知机
            return x

        return _wrapper

    def build(self):
        """
        构建模型结构
        cdssm 使用 Siamese 架构
        """
        self.embedding = self.make_embedding_layer() # 加载词向量作为query和title的共享词向量矩阵
        base_network = self._create_base_network() # 定义网络基本结构
        # 左输入和右输入
        input_left, input_right = self._make_inputs()
        # 处理左右输入
        x = [base_network(input_left),
             base_network(input_right)]
        # 具有余弦相似度的点积
        x = keras.layers.Dot(axes=[1, 1], normalize=True)(x) # 用点乘来计算两个输入之间的关系
        x_out = self._make_output_layer()(x)
        model = Model(inputs=[input_left, input_right],
                              outputs=x_out)
        return model