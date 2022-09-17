#encoding=utf8
import keras
from keras.models import Model
import tensorflow as tf 
import numpy as np 
import sys
sys.path.append( '../')
from engine.base_model import BaseModel
from engine.layers import KMaxPooling

np.random.seed(1)
tf.set_random_seed(1)


class MVLSTM(BaseModel):

    def build(self):
        """Build model structure."""
        query, doc = self._make_inputs() # 定义两个输入

        # Embedding layer
        embedding = self.make_embedding_layer(mask_zero=True) # 定义一个共享的embedding层
        embed_query = embedding(query)
        embed_doc = embedding(doc)

        # Bi-directional LSTM layer
        # rep_query = keras.layers.Bidirectional(keras.layers.LSTM(
        #     self._params['lstm_units'],
        #     return_sequences=True,
        #     dropout=self._params['dropout_rate']
        # ))(embed_query)
        # rep_doc = keras.layers.Bidirectional(keras.layers.LSTM(
        #     self._params['lstm_units'],
        #     return_sequences=True,
        #     dropout=self._params['dropout_rate']
        # ))(embed_doc)

        bilstm = keras.layers.Bidirectional(keras.layers.LSTM( # 共享参数的bilstm结构 提取query和doc的语义向量
            self._params['lstm_units'],
            return_sequences=True,
            dropout=self._params['dropout_rate']
        ))
        rep_query = bilstm(embed_query)
        rep_doc = bilstm(embed_doc)


        # Top-k matching layer
        rep_query = keras.layers.Lambda( # 先进行l2正则规范化
            lambda x: tf.math.l2_normalize(x, axis=2)
            )(rep_query)
        rep_doc = keras.layers.Lambda(
            lambda x: tf.math.l2_normalize(x, axis=2)
            )(rep_doc)
        matching_matrix = keras.layers.Dot( # 进行点乘 得到余弦相似性得分
            axes=[2, 2], normalize=False)([rep_query, rep_doc])
        matching_signals = keras.layers.Reshape((-1,))(matching_matrix)
        # matching_topk = keras.layers.Lambda(
        #     tf.nn.top_k, arguments={'k':self._params['top_k'],'sorted':True}
        # )(matching_signals)
        matching_topk = KMaxPooling(k=self._params['top_k'])(matching_signals) # 提取k个最大池化值

        # Multilayer perceptron layer.
        mlp = self._make_multi_layer_perceptron_layer()(matching_topk) # 多层感知机网络
        mlp = keras.layers.Dropout(
            rate=self._params['dropout_rate'])(mlp)

        x_out = self._make_output_layer()(mlp) # 根据任务输出

        model = Model(inputs=[query, doc], outputs=x_out)
        return model