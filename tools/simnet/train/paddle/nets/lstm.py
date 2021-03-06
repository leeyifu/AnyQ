#coding=utf-8

# Copyright (c) 2018 Baidu, Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import layers.paddle_layers as layers


class LSTM(object):
    """
    LSTM
    """
    def __init__(self, conf_dict):
        """
        initialize
        """
        self.dict_size = conf_dict["dict_size"]
        self.task_mode = conf_dict["task_mode"]
        self.emb_dim = conf_dict["net"]["emb_dim"]
        self.lstm_dim = conf_dict["net"]["lstm_dim"]
        self.hidden_dim = conf_dict["net"]["hidden_dim"]

    def predict(self, left, right):
        """
        Forward network
        """
        # embedding layer
        emb_layer = layers.EmbeddingLayer(self.dict_size, self.emb_dim, "emb")
        left_emb = emb_layer.ops(left)
        right_emb = emb_layer.ops(right)
        # Presentation context
        lstm_layer = layers.DynamicLSTMLayer(self.lstm_dim, "lstm")
        left_lstm = lstm_layer.ops(left_emb)
        right_lstm = lstm_layer.ops(right_emb)
        last_layer = layers.SequenceLastStepLayer()
        left_last = last_layer.ops(left_lstm)
        right_last = last_layer.ops(right_lstm)
        tanh_layer = layers.FCLayer(self.hidden_dim, "tanh", "tanh")
        left_tanh = tanh_layer.ops(left_last)
        right_tanh = tanh_layer.ops(right_last)
        # matching layer
        if self.task_mode == "pairwise":
            cos_sim_layer = layers.CosSimLayer()
            pred = cos_sim_layer.ops(left_tanh, right_tanh)
        else:
            concat_layer = layers.ConcatLayer(1)
            concat = concat_layer.ops([left_tanh, right_tanh])
            softmax_layer = layers.FCLayer(2, "softmax", "cos_sim")
            pred = softmax_layer.ops(concat)
        return left_tanh, pred
