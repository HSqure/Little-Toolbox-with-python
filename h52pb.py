"""
      本脚本文件用于将tensorflow的模型描述文件[.h5]文件(仅权重)转化为用于适用于Edge端设备部署的[.pb]文件
"""

from tensorflow.python.framework import graph_util, graph_io
from tensorflow.python.util import compat

from keras.utils import plot_model
from keras.models import load_model
from keras.layers import Input
from keras import backend as K
import tensorflow as tf
import os.path as osp
import os
#local模型结构调用
from yolo3.model import yolo_body


#---------------------------------------------------
#------------- Customized Information --------------
#---------------------------------------------------

# 模型日志目录
TF_EVENT_PATH = 'pb_file/events/'

# 模型目标类别数量
NUM_CLASSES = 1

# 输入h5模型描述文件路径
INPUT_PATH = ''

# h5模型描述文件名
WEIGHT_FILE = 'trained_weights_only_final.h5'

# 输出路径
OUTPUT_PATH = 'pb_file/'

#---------------------------------------------------
#---------------------------------------------------
#---------------------------------------------------


def h5_to_pb(graph, session, output_node_names, output_dir, model_name):
    """.h5模型文件转换成pb模型文件
    Argument:
        graph: str
            .h5模型文件
        session: pointer
            会话指针
        output_node_names: str
            模型的输出节点名
        output_dir: str
            pb模型文件保存路径
        model_name: str
            pb模型文件名称

    Return: null
            无
    """
    
    # 确认指定的输出路径是否正确，没有就创建一个
    if os.path.exists(output_dir) == False:
        os.mkdir(output_dir)
    
    # 写入pb模型文件配置
    with graph.as_default():
        graphdef_inf = tf.graph_util.remove_training_nodes(graph.as_graph_def()) # 移除训练用的节点
        graphdef_frozen = tf.graph_util.convert_variables_to_constants(session, graphdef_inf, output_node_names) # 模型freeze化，将变量值固定
        graph_io.write_graph(graphdef_frozen, output_dir, name=model_name, as_text=False) # 写入pb模型文件


if __name__ == '__main__':
    """ 主函数 """
    #--------------------- 1.信息加载配置 -----------------------
    tf.keras.backend.set_learning_phase(0)
    weight_file_path = os.path.join(INPUT_PATH, WEIGHT_FILE) #读入模型的权重文件
    h5_model = yolo_body(Input(shape=(None, None, 3)), 3, NUM_CLASSES) # 从local加载模型的结构
    h5_model.load_weights(weight_file_path, by_name=True, skip_mismatch=True) #从路径中加载训练好的模型权重
    output_graph_name = os.path.basename(WEIGHT_FILE[:-3]) + '.pb' # 取输入的.h5模型文件名作为.pb模型文件名  
    output_dir = osp.join(os.getcwd(), OUTPUT_PATH) # pb模型文件输出绝对路径

    #-------------------- 2.模型信息可视化 ----------------------
    #plot_model(h5_model, to_file='logs_test/000/visualized/model.png', show_shapes=True) # 原模型结构的绘制
    #tf.summary.FileWriter(TF_EVENT_PATH, graph=tf.get_default_graph()) #输出events tensorboard日志文件，可视化输入的.h5文件里的模型结构
    h5_model.summary() #打印模型信息


    #--------------- 3.调用函数转换并保存pb文件 -----------------
    session = tf.keras.backend.get_session() #继承session
    h5_to_pb(session.graph, session, [out.op.name for out in h5_model.outputs], output_dir=output_dir, model_name=output_graph_name)


    print('\n----------- Finished! -----------\n')
    print('\n[.pb] file output location: %s\n' %(output_dir+output_graph_name))



