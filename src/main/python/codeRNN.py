# -*- coding: UTF-8 -*-
from gensim.models import word2vec
from preprocessor import preprocessor

import tensorflow as tf
import numpy as np
import logging
import os
import json

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

VECTOR_SIZE = 100
TRAIN_ITERS = 100
BATCH_SIZE = 128
HIDDEN_SIZE = 100
N_INPUTS = 100
LEARNING_RATE = 0.001

LSTM_KEEP_PROB = 0.9

REPO_ID = 13421878
MAX_RECORD = {'step': -1, 'acc': 0.0}
MAX_PRECISION = {'step': -1, 'acc': 0.0}
MAX_RECALL = {'step': -1, 'acc': 0.0}
MAX_F_MEASURE = {'step': -1, 'acc': 0.0}

wordModel = word2vec.Word2Vec.load('test/nocode%d.model' % REPO_ID)
codeModel = word2vec.Word2Vec.load('test/code%d.model' % REPO_ID)

# text data
def text2vec(text, isHtml):
    if isHtml:
        seqs = preprocessor.processHTMLNoCamel(text)
    else:
        seqs = preprocessor.preprocessNoCamel(text)
    res = []
    for seq in seqs:
        for word in seq:
            try:
                res.append(wordModel[word])
            except KeyError:
                res.append(np.zeros(VECTOR_SIZE))
    return res


def code2vec(text):
    res = []
    for seq in text:
        for word in seq:
            try:
                res.append(codeModel[word])
            except KeyError:
                res.append(np.zeros(VECTOR_SIZE))
    if len(res) > 0:
        pass
    else:
        res.append(np.zeros(VECTOR_SIZE))
    return res


#  shape = [None, seq len, Vec size]
def read_data(path):
    X1 = []
    X2 = []
    T = []
    L1 = []
    L2 = []
    LT = []
    Y = []
    C1=[]
    C2=[]
    L3=[]
    L4=[]
    filelist = os.listdir(path)
    for i in range(0, len(filelist)):
        filepath = os.path.join(path, filelist[i])
        logging.info("Loaded the file:"+filepath)
        if os.path.isfile(filepath):
            file = open(filepath, 'rb')
            testlist = json.loads(file.read())
            for map in testlist:
                commit = text2vec(map['commit'], False)
                issue = text2vec(map['issue'], True)
                title = text2vec(map['issuetitle'], False)
                commitcode = code2vec(map['commitcode'])
                issuecode = code2vec(map['issuecode'])
                if len(commit) < 5:
                    continue
                if len(issue)+len(title) < 5:
                    continue
                L1.append(len(commit))
                X1.append(commit)
                L2.append(len(issue))
                X2.append(issue)
                LT.append(len(title))
                T.append(title)
                Y.append(float(map['type']))
                L3.append(len(commitcode))
                C1.append(commitcode)
                L4.append(len(issuecode))
                C2.append(issuecode)
            file.close()
    return X1, X2, T, L1, L2, LT, Y, C1, C2, L3, L4


# shape=[batch_size, None]
def make_batches(data, batch_size):
    X1, X2, T, L1, L2, LT, Y, C1,C2,L3,L4 = data
    num_batches = len(Y) // batch_size
    data1 = np.array(X1[: batch_size*num_batches])
    data1 = np.reshape(data1, [batch_size, num_batches])
    data_batches1 = np.split(data1, num_batches, axis=1)  #  list
    data_batches1_rs = []
    for d1 in data_batches1:
        sub_batch = []
        maxD = 0
        for d in d1:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d1:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches1_rs.append(np.array(sub_batch))

    data2 = np.array(X2[: batch_size*num_batches])
    data2 = np.reshape(data2, [batch_size, num_batches])
    data_batches2 = np.split(data2, num_batches, axis=1)
    data_batches2_rs = []
    for d2 in data_batches2:
        sub_batch = []
        maxD = 0
        for d in d2:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d2:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches2_rs.append(np.array(sub_batch))

    dataT = np.array(T[: batch_size*num_batches])
    dataT = np.reshape(dataT, [batch_size, num_batches])
    data_batchesT = np.split(dataT, num_batches, axis=1)  #  list
    data_batchesT_rs = []
    for d3t in data_batchesT:
        sub_batch = []
        maxD = 0
        for d in d3t:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d3t:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batchesT_rs.append(np.array(sub_batch))

    len1 = np.array(L1[: batch_size*num_batches])
    len1 = np.reshape(len1, [batch_size, num_batches])
    len_batches1 = np.split(len1, num_batches, axis=1)
    len_batches1 = np.reshape(np.array(len_batches1), [num_batches, BATCH_SIZE])

    len2 = np.array(L2[: batch_size * num_batches])
    len2 = np.reshape(len2, [batch_size, num_batches])
    len_batches2 = np.split(len2, num_batches, axis=1)
    len_batches2 = np.reshape(np.array(len_batches2), [num_batches, BATCH_SIZE])

    lenT = np.array(LT[: batch_size * num_batches])
    lenT = np.reshape(lenT, [batch_size, num_batches])
    len_batchesT = np.split(lenT, num_batches, axis=1)
    len_batchesT = np.reshape(np.array(len_batchesT), [num_batches, BATCH_SIZE])

    label = np.array(Y[: batch_size*num_batches])
    label = np.reshape(label, [batch_size, num_batches])
    label_batches = np.split(label, num_batches, axis=1)

    # code part
    data3 = np.array(C1[: batch_size * num_batches])
    data3 = np.reshape(data3, [batch_size, num_batches])
    data_batches3 = np.split(data3, num_batches, axis=1)  # list
    data_batches3_rs = []
    for d3 in data_batches3:
        sub_batch = []
        maxD = 0
        for d in d3:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d3:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches3_rs.append(np.array(sub_batch))

    data4 = np.array(C2[: batch_size * num_batches])
    data4 = np.reshape(data4, [batch_size, num_batches])
    data_batches4 = np.split(data4, num_batches, axis=1)
    data_batches4_rs = []
    for d4 in data_batches4:
        sub_batch = []
        maxD = 0
        for d in d4:
            for dt in d:
                maxD = max(maxD, len(dt))
        for d in d4:
            for dt in d:
                todo = maxD - len(dt)
                for index in range(todo):
                    dt.append(np.zeros(VECTOR_SIZE))
                sub_batch.append(np.array(dt))
        data_batches4_rs.append(np.array(sub_batch))

    len3 = np.array(L3[: batch_size * num_batches])
    len3 = np.reshape(len3, [batch_size, num_batches])
    len_batches3 = np.split(len3, num_batches, axis=1)
    len_batches3 = np.reshape(np.array(len_batches3), [num_batches, BATCH_SIZE])

    len4 = np.array(L4[: batch_size * num_batches])
    len4 = np.reshape(len4, [batch_size, num_batches])
    len_batches4 = np.split(len4, num_batches, axis=1)
    len_batches4 = np.reshape(np.array(len_batches4), [num_batches, BATCH_SIZE])

    return list(zip(data_batches1_rs, data_batches2_rs, data_batchesT_rs, len_batches1, len_batches2, len_batchesT, label_batches,
                    data_batches3_rs, data_batches4_rs, len_batches3, len_batches4))


class MyModel(object):
    def __init__(self, is_training, batch_size):
        self.batch_size = batch_size

        self.input1 = tf.placeholder(tf.float32, [BATCH_SIZE, None, VECTOR_SIZE])
        self.input2 = tf.placeholder(tf.float32, [BATCH_SIZE, None, VECTOR_SIZE])
        self.inputT = tf.placeholder(tf.float32, [BATCH_SIZE, None, VECTOR_SIZE])
        self.len1 = tf.placeholder(tf.int32, [BATCH_SIZE, ])
        self.len2 = tf.placeholder(tf.int32, [BATCH_SIZE, ])
        self.lent = tf.placeholder(tf.int32, [BATCH_SIZE, ])
        self.target = tf.placeholder(tf.float32, [BATCH_SIZE, 1])

        self.input3 = tf.placeholder(tf.float32, [BATCH_SIZE, None, VECTOR_SIZE])
        self.input4 = tf.placeholder(tf.float32, [BATCH_SIZE, None, VECTOR_SIZE])
        self.len3 = tf.placeholder(tf.int32, [BATCH_SIZE, ])
        self.len4 = tf.placeholder(tf.int32, [BATCH_SIZE, ])

        with tf.variable_scope("commit"):
            outputs1, states1 = self.RNN(self.input1, self.len1, is_training)
        with tf.variable_scope("issue"):
            outputs2, states2 = self.RNN(self.input2, self.len2, is_training)
        with tf.variable_scope("title"):
            outputs3, states3 = self.RNN(self.inputT, self.lent, is_training)

        with tf.variable_scope("commitcode"):
            outputs4, states4 = self.RNN(self.input3, self.len3, is_training)
        with tf.variable_scope("issuecode"):
            outputs5, states5 = self.RNN(self.input4, self.len4, is_training)

        newoutput1 = states1[-1].h
        newoutput2 = states2[-1].h
        newoutput3 = states3[-1].h
        newoutput4 = states4[-1].h
        newoutput5 = states5[-1].h

        # Define loss and optimizer
        self.cos_score = self.getScore(newoutput1, newoutput2, newoutput3, newoutput4, newoutput5)
        self.loss_op = self.getLoss(self.cos_score, self.target)

        if not is_training:
            return

        optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)
        self.train_op = optimizer.minimize(self.loss_op)

    def getScore(self, state1, state2, state3, state4, state5):
        pooled_len_1 = tf.sqrt(tf.reduce_sum(state1 * state1, 1))
        pooled_len_2 = tf.sqrt(tf.reduce_sum(state2 * state2, 1))
        pooled_mul_12 = tf.reduce_sum(state1 * state2, 1)
        score1 = tf.div(pooled_mul_12, pooled_len_1 * pooled_len_2 + 1e-8, name="scores1")  # +1e-8 avoid 'len_1/len_2 == 0'
        score1 = tf.reshape(score1, [BATCH_SIZE, 1])

        pooled_len_3 = tf.sqrt(tf.reduce_sum(state3 * state3, 1))
        pooled_mul_13 = tf.reduce_sum(state1 * state3, 1)
        score2 = tf.div(pooled_mul_13, pooled_len_1 * pooled_len_3 + 1e-8, name="scores2")  # +1e-8 avoid 'len_1/len_2 == 0'
        score2 = tf.reshape(score2, [BATCH_SIZE, 1])

        score = tf.concat([score1, score2], 1)
        score = tf.reduce_max(score, 1)

        pooled_len_4 = tf.sqrt(tf.reduce_sum(state4 * state4, 1))
        pooled_len_5 = tf.sqrt(tf.reduce_sum(state5 * state5, 1))
        pooled_mul_14 = tf.reduce_sum(state4 * state5, 1)
        score3 = tf.div(pooled_mul_14, pooled_len_4 * pooled_len_5 + 1e-8, name="scores3")  # +1e-8 avoid 'len_1/len_2 == 0'
        score3 = tf.reshape(score3, [BATCH_SIZE, 1])

        score = tf.reshape(score, [BATCH_SIZE, 1])
        score = tf.concat([score, score3], 1)
        score = tf.reduce_max(score, 1)
        return tf.reshape(score, [BATCH_SIZE, 1])

    #  |t - cossimilar(state1, state2)|
    def getLoss(self, score, t):
        rs = t - score
        rs = tf.abs(rs)
        return tf.reduce_sum(rs)

    def RNN(self, input_data, seq_len, is_training):
        dropout_keep_prob = LSTM_KEEP_PROB if is_training else 1.0
        lstm_cells = [
            tf.nn.rnn_cell.DropoutWrapper(tf.nn.rnn_cell.BasicLSTMCell(HIDDEN_SIZE), output_keep_prob=dropout_keep_prob)
            for _ in range(1)
        ]
        rnn_cell = tf.nn.rnn_cell.MultiRNNCell(lstm_cells)
        outputs, state = tf.nn.dynamic_rnn(rnn_cell, input_data, sequence_length=seq_len, dtype=tf.float32)
        return outputs, state


def run_epoch(session, model, batches, step):
    # session.run(model.init_state)
    for x1, x2, t, l1, l2, lt, y, c1,c2,l3,l4 in batches:
        loss, _ = session.run([model.loss_op, model.train_op],
                           feed_dict={model.input1: x1, model.input2: x2, model.inputT: t, model.len1: l1, model.len2: l2, model.lent: lt, model.target: y,
                                      model.input3:c1, model.input4:c2, model.len3:l3, model.len4:l4})
        logging.info("At the step %d, the loss is %f" % (step, loss))


def test_epoch(session, model, batches, step):
    temp = []
    total_correct = 0
    total_tests = len(batches) * BATCH_SIZE
    index = 0
    total_TP = 0
    total_TN = 0
    total_FP = 0
    total_FN = 0
    for x11, x21, t1, l11, l21, lt1, y1, c11,c21,l31,l41 in batches:
        score, loss = session.run([model.cos_score, model.loss_op],
                                feed_dict={model.input1: x11, model.input2: x21, model.inputT: t1, model.len1: l11, model.len2: l21, model.lent: lt1,
                                           model.target: y1, model.input3:c11, model.input4:c21, model.len3:l31, model.len4:l41})
        temp.append(loss)
        total_correct = total_correct + get_correct(score, y1, index, len(batches))
        index = index + 1
        measure = get_measure(score, y1)
        total_TP = total_TP + measure[0]
        total_TN = total_TN + measure[1]
        total_FP = total_FP + measure[2]
        total_FN = total_FN + measure[3]

    precision = float(total_TP) / (total_TP + total_FP+1e-8)
    recall = float(total_TP) / (total_TP + total_FN+1e-8)
    f_measure = (2 * precision * recall) / (precision + recall+1e-8)

    logging.info("At the test %d, the avg loss is %f, the accuracy is %f" % (step, np.mean(np.array(temp)), float(total_correct) / total_tests))
    logging.info("At the test %d, TP:%d TN:%d FP:%d FN:%d" % (step, total_TP, total_TN, total_FP, total_FN))
    logging.info("At the test %d, precision:%f recall:%f f_measure:%f" % (step, precision, recall, f_measure))
    if (float(total_correct) / total_tests) > MAX_RECORD['acc']:
        MAX_RECORD['step'] = step
        MAX_RECORD['acc'] = float(total_correct) / total_tests
    if precision > MAX_PRECISION['acc']:
        MAX_PRECISION['step'] = step
        MAX_PRECISION['acc'] = precision
    if recall > MAX_RECALL['acc']:
        MAX_RECALL['step'] = step
        MAX_RECALL['acc'] = recall
    if f_measure > MAX_F_MEASURE['acc']:
        MAX_F_MEASURE['step'] = step
        MAX_F_MEASURE['acc'] = f_measure
    logging.info("MAX is at step %d: %f" % (MAX_RECORD['step'], MAX_RECORD['acc']))
    logging.info("MAX precision is at step %d: %f" % (MAX_PRECISION['step'], MAX_PRECISION['acc']))
    logging.info("MAX recall is at step %d: %f" % (MAX_RECALL['step'], MAX_RECALL['acc']))
    logging.info("MAX f_measure is at step %d: %f" % (MAX_F_MEASURE['step'], MAX_F_MEASURE['acc']))


def get_correct(score, target, index, NUM):
    result = 0
    for i in range(len(target)):
        if target[i][0] == 1 and score[i][0] > 0.5:
            result = result + 1
        elif target[i][0] == 0 and score[i][0] < 0.5:
            result = result + 1
    return result


def get_measure(score, target):
    TP = 0
    TN = 0
    FP = 0
    FN = 0
    for i in range(len(target)):
        if target[i][0] == 1:
            if score[i][0] > 0.5:
                TP = TP+1
            else:
                FN = FN+1
        elif target[i][0] == 0:
            if score[i][0] < 0.5:
                TN = TN+1
            else:
                FP = FP+1
    return TP, TN, FP, FN


def main():
    train_batches = make_batches(read_data(path='./codetrain%d' % REPO_ID), BATCH_SIZE)
    test_batches = make_batches(read_data(path="./codetestset%d" % REPO_ID), BATCH_SIZE)

    with tf.variable_scope("rnn_model", reuse=None):
        train_model = MyModel(True, BATCH_SIZE)
    with tf.variable_scope("rnn_model", reuse=True):
        test_model = MyModel(False, BATCH_SIZE)

    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        saver = tf.train.Saver()
        sess.run(init)
        logging.info("Test Set: %d" % (len(test_batches) * BATCH_SIZE))

        for step in range(TRAIN_ITERS):
            logging.info("Step: " + str(step))
            run_epoch(session=sess, model=train_model, batches=train_batches, step=step)
            test_epoch(session=sess, model=test_model, batches=test_batches, step=step)
        saver.save(sess, 'rnnmodel/adam/rnn', global_step=TRAIN_ITERS)
        logging.info("Optimization Finished!")


if __name__ == "__main__":
    main()
