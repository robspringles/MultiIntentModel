import sys
import numpy as np
import tensorflow as tf
from Data import Data

rnn_size = 100
batch_size = 10
word_length = 5
max_sentence_length = 3
lr = 0.002

d = Data()
vocab_size = len(d.vocab) + 2
print(vocab_size)

data_x, data_y = d.run()
questions_count = len(d.questions_all)
print(data_x)
print(data_y)
print(data_x.shape)
print(data_y.shape)
# sys.exit()

train_graph = tf.Graph()
with train_graph.as_default():
    input_text = tf.placeholder(tf.int32, shape=(None, None), name="input")
    targets = tf.placeholder(tf.int32, shape=(None, None), name="targets")
    learning_rate = tf.placeholder(tf.float32, name="learning_rate")

    # Character RNN
    # char_final_states = []
    # embedding = tf.Variable(tf.random_uniform((vocab_size, rnn_size), -1, 1))
    # embed = tf.nn.embedding_lookup(embedding, input_text)
    lstm = tf.contrib.rnn.BasicLSTMCell(rnn_size, name="lstm")
    # cell = tf.contrib.rnn.MultiRNNCell([lstm] * 2)
    input_oh = tf.one_hot(input_text, vocab_size)
    outputs, _ = tf.nn.dynamic_rnn(lstm, input_oh, dtype=tf.float32)
    # final_state = tf.identity(final_state, name="final_state_char")
    #
    outputs_b = tf.transpose(outputs, [1, 0, 2])
    last = tf.gather(outputs_b, 999)
    #
    logits = tf.contrib.layers.fully_connected(last, rnn_size, activation_fn=None)
    logits = tf.contrib.layers.fully_connected(logits, questions_count * 1, activation_fn=None)
    logits = tf.identity(logits, name="final_logits")
    # logits_t = tf.reshape(logits, [-1, 2])
    # prediction = tf.nn.softmax(logits_t)
    prediction = tf.nn.sigmoid(logits)
    # targets_t = tf.reshape(targets, [-1, 2])
    # cost = tf.reduce_sum(tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits_t, labels=targets_t))
    # cost = tf.losses.mean_squared_error(targets_t, prediction)
    cost = tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.cast(targets, tf.float32), logits=logits)
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(cost)


with tf.Session(graph=train_graph) as sess:
    sess.run(tf.global_variables_initializer())
    x = data_x
    y = data_y
    for n in range(500):
        for nn in range(0, len(x) - batch_size, batch_size):
            # print(x[nn])
            # print(y[nn])
            feed = {
                input_text: x[nn:nn + batch_size],
                targets: y[nn:nn + batch_size],
                learning_rate: lr
            }
            # print(sess.run(prediction, feed))
            # sys.exit()
            pred, targ, train_loss, _ = sess.run([prediction, targets, cost, train_op], feed)
            print(pred)
            print(targ)
            print(train_loss.mean())

    while 1:
        text_input = input(">")
        x = d.message_to_ints(text_input, 1000)
        feed = {
            input_text: [x],
        }
        pred = sess.run(prediction, feed)
        print(pred)
        for question in range(questions_count):
            if pred[0][question] > 0.5:
                print(d.questions_all[question])
