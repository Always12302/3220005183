import keras
from keras.models import Model
import tensorflow as tf
import numpy as np
import sys
from line_profiler_pycharm import profile
sys.path.append( '../')

np.random.seed(1)
tf.set_random_seed(1)

@profile
def pad_sequences(sequences, maxlen=None, dtype='int32', value=0.): # padding机制 使得文本不同长度仍可以计算相似度

    # 下方这里 原本是用来训练模型的 所以是sequences原本是各句子组成的列表
    lengths = [len(s) for s in sequences] # 拿出每个句子的长度

    nb_samples = len(sequences) # 获得有几个句子
    if maxlen is None: # 如果没有规定最大长度
        maxlen = np.max(lengths) # 最大长度就是句子列表中最长句子的长度

    x = (np.ones((nb_samples, maxlen)) * value).astype(dtype) # 构建一个全由0组成的的矩阵
    for idx, s in enumerate(sequences): # 每一个句子
        if len(s) == 0: # 如果这一句长度为0
            continue # 跳过
        trunc = s[:maxlen] # 获取句子指定长度的内容 如果超长则截断
        x[idx, :len(trunc)] = trunc # 用句子的内容替换掉矩阵中的部分 如果这个句子没达到最大长度 剩下的内容便全是0的填充

    return x # 返回padding矩阵

class bitter(object):

    @profile
    def __init__(self, params):

        self._params = params # 获取参数

    @profile
    def make_embedding_layer(self, name='embedding', **kwargs): # 构建embedding层

        def init_embedding(weights=None):

            input_dim = self._params['max_features'] # 输入的维度
            output_dim = self._params['embed_size'] # 输出的维度

            return keras.layers.Embedding( # 调用Embedding函数 构建embedding层
                input_dim=input_dim,
                output_dim=output_dim,
                trainable=False,
                name=name,
                weights=weights,
                **kwargs)

        embedding = init_embedding()

        return embedding # 将上方这个函数回传

    @profile
    def _create_base_network(self): # 构建基本网络结构

        def _wrapper(x):

            x = self.embedding(x) # 先加一个embedding层
            x = keras.layers.Conv1D( # 一维卷积 内部包含word hashing
                filters=self._params['filters'],
                kernel_size=self._params['kernel_size'],
                strides=1,
                padding='same',
                activation='relu',
                kernel_initializer='random_uniform',
                bias_initializer='zeros')(x)
            x = keras.layers.Dropout(self._params['dropout_rate'])(x) # 使用dropout丢弃部分信息
            x = keras.layers.GlobalMaxPool1D()(x) # 全局最大池化 将提取的语义特征降维
            x = self._make_multi_layer_perceptron_layer()(x) # 传入全连接层 这里函数名字其实是多层感知机 但这里只有一层 也就是一层全连接层
            return x # 把构建好了的模型回传

        return _wrapper

    @profile
    def _make_inputs(self) -> list:
        input_left = keras.layers.Input( # 第一个输入 这里是原论文
            name='text_left',
            shape=self._params['input_shapes'][0]
        )
        input_right = keras.layers.Input( # 另一个输入 这里是抄袭论文
            name='text_right',
            shape=self._params['input_shapes'][1]
        )
        return [input_left, input_right]

    @profile
    def _make_output_layer(self) -> keras.layers.Layer: # 构建输出层

        # 将全连接层的结果进行softmax运算 结果进行二分类 如果输入的另外一个输入有较多内容 就变成了一个ranking任务 如果只是一个内容 就是分类任务
        return keras.layers.Dense(2, activation='softmax')

    @profile
    def _make_multi_layer_perceptron_layer(self) -> keras.layers.Layer: # 构建全连接层

        def _wrapper(x):
            activation = 'relu' # 激活函数选用relu
            for _ in range(self._params['mlp_num_layers']): # 要几个全连接层
                x = keras.layers.Dense(self._params['mlp_num_units'],
                                       activation=activation)(x)
            return keras.layers.Dense(self._params['mlp_num_fan_out'],
                                      activation=activation)(x)

        return _wrapper

    @profile
    def build(self):

        self.embedding = self.make_embedding_layer() # 指定embedding函数
        base_network = self._create_base_network() # 指定构建网络模型函数
        input_left, input_right = self._make_inputs() # 指定输入传入函数
        x = [base_network(input_left),
             base_network(input_right)]
        x = keras.layers.Dot(axes=[1, 1], normalize=True)(x) # 使用dot点乘 计算余弦相似度
        x_out = self._make_output_layer()(x) # softmax计算二分类
        model = Model(inputs=[input_left, input_right],
                              outputs=x_out) # 指定模型的输入输出
        return model # 将模型回传

@profile
def work():

    params = {
        'max_features': 40,
        'embed_size': 20,
        'filters': 100, # 卷积核数量
        'kernel_size': 3, # 卷积核大小
        'dropout_rate': 0.2,
        'mlp_num_layers': 1,
        'mlp_num_units': 8,
        'mlp_num_fan_out': 6,
        'input_shapes': [(35000,), (35000,)], # 句子最大长度
    }
    paper_text_path = sys.argv[1] # 获取指令中传入的参数
    paper_fake_path = sys.argv[2]
    ans_number_path = sys.argv[3]
#    paper_text_path = 'paper_text.txt'
#    paper_fake_path = 'paper_add.txt'
#    ans_number_path = 'similarity_number_1.txt'
    paper_text = open(paper_text_path, "r", encoding='utf-8') # 打开指定的文件
    org = paper_text.read() # 获取文件内容
    paper_fake = open(paper_fake_path, "r", encoding='utf-8')
    fake = paper_fake.read()
    p_seg = list(map(lambda x: list(x.replace(" ", "")), org))
    h_seg = list(map(lambda x: list(x.replace(" ", "")), fake))
    common_texts = []
    common_texts.extend(p_seg)
    common_texts.extend(h_seg)
    char_set = set()  # 建一个空集合用来存放单字
    for sample in common_texts:  # 每个句子
        for char in sample:  # 句子中的每个单字
            char_set.add(char)  # 加入单字库
    vocab = sorted(list(char_set), reverse=True) # 排序一下单字库
    p = [org]
    h = [fake]
    word2idx = {word: index
                for index, word in enumerate(vocab, start=1)} # 生成字到index的字典 将句子序列的字转为机器能识别的数字
    p_list, h_list = [], []
    for p_sentence, h_sentence in zip(p, h): # 每一对句子依次转化
        p = [word2idx[word.lower()]
             for word in p_sentence if len(word.strip()) > 0
             and word.lower() in word2idx.keys()]
        h = [word2idx[word.lower()]
             for word in h_sentence if len(word.strip()) > 0
             and word.lower() in word2idx.keys()]
        p_list.append(p)
        h_list.append(h)
    p_c_index = pad_sequences(p_list, maxlen=params['input_shapes'][0][0]) # 转化后用padding让两个句子填充或截断到一样长度
    h_c_index = pad_sequences(h_list, maxlen=params['input_shapes'][1][0])
    x_test = [p_c_index, h_c_index]

    backend = bitter(params) # 将参数传给模型函数
    model = backend.build() # 建立模型
    model.compile(  # 编译
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    similarity_number = model.predict(  # 预测相似度
        x=x_test,
    )

    with open(ans_number_path, "w") as ans_number: # 打开要保存重复率的文件
        for ans in similarity_number:
            if len(fake) == 0: # 如果抄袭论文其实是空文件
                ans_number.write(str(0)) # 重复率为0
            else:
#                ans_number.write(str(round(ans[1],2))) # 如果不是空的 正常写入重复率 此处是限制小数点精度
                ans_number.write(str(ans[1])) # 如果不是空的 正常写入重复率 此处不限制小数点精度
                print('论文原文的文件的路径是：',paper_text_path)
                print('抄袭论文的文件的路径是：',paper_fake_path)
                print('输出的答案文件的路径是：',ans_number_path)
                print('抄袭程度是：',round(ans[1],2))


if __name__ == '__main__':

    work() # 调用工作函数