#encoding=utf8
import keras
from keras.models import Model
import tensorflow as tf 
import numpy as np 
import sys
sys.path.append( '../')
from engine.base_model import BaseModel
from engine.layers import KMaxPooling,MatchingLayer


class ArcII(BaseModel):
    """docstring for ArcII"""
    def build(self):
        """
        Build model structure.
        ArcII has the desirable property of letting two sentences meet before
        their own high-level representations mature.
        """
        input_left, input_right = self._make_inputs() # 定义两个输入

        embedding = self.make_embedding_layer() # 定义一个词向量层作为两个输入的共享embedding
        embed_left = embedding(input_left)
        embed_right = embedding(input_right)

        # Phrase level representations
        # conv_1d_left = keras.layers.Conv1D(
        #     self._params['kernel_1d_count'],
        #     self._params['kernel_1d_size'],
        #     padding=self._params['padding']
        # )(embed_left)
        # conv_1d_right = keras.layers.Conv1D(
        #     self._params['kernel_1d_count'],
        #     self._params['kernel_1d_size'],
        #     padding=self._params['padding']
        # )(embed_right)
        conv_1d = keras.layers.Conv1D( # 使用1维卷积对这两个输入语句提取特征
            self._params['kernel_1d_count'],
            self._params['kernel_1d_size'],
            padding=self._params['padding']
        )
        conv_1d_left = conv_1d(embed_left)
        conv_1d_right = conv_1d(embed_right)

        # Interaction
        embed_cross = MatchingLayer( # 对一维卷积的结果进行交互 得到四位数组
            normalize=True,
            matching_type=self._params['matching_type']
            )([conv_1d_left, conv_1d_right])

        for i in range(self._params['num_blocks']): # 使用num_blocks个2维卷积提取特征
            embed_cross = self._conv_pool_block( # 接2维卷积
                embed_cross,
                self._params['kernel_2d_count'][i], # 卷积核数量
                self._params['kernel_2d_size'][i], # 卷积核尺寸
                self._params['padding'], # 填充的方法
                self._params['conv_activation_func'], # 激活函数
                self._params['pool_2d_size'][i] # 池化尺寸
            )

        embed_flat = keras.layers.Flatten()(embed_cross) # 展平
        x = keras.layers.Dropout(rate=self._params['dropout_rate'])(embed_flat) # 接dropout

        inputs = [input_left, input_right]
        x_out = self._make_output_layer()(x) # 接输出
        model = keras.Model(inputs=inputs, outputs=x_out)

        return model

    @classmethod
    def _conv_pool_block(cls, x,kernel_count, kernel_size,padding,activation,pool_size):
        output = keras.layers.Conv2D(kernel_count, # 2维卷积
                                     kernel_size,
                                     padding=padding,
                                     activation=activation)(x)
        output = keras.layers.MaxPooling2D(pool_size=pool_size)(output) # 最大2维池化
        # output = keras.layers.normalization.BatchNormalization()(output)
        return output