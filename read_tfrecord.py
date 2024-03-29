# coding:utf-8
import tensorflow as tf
import numpy as np
import cv2
import os


# just for RNet and ONet, since I change the method of making tfrecord
# as for PNet
def read_single_tfrecord(tfrecord_file, batch_size, net):
    # generate a input queue
    # each epoch shuffle
    filename_queue = tf.train.string_input_producer([tfrecord_file], shuffle=True)
    # read tfrecord
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    image_features = tf.parse_single_example(
        serialized_example,
        features={
            'image/encoded': tf.FixedLenFeature([], tf.string),  # one image  one record
            'image/label': tf.FixedLenFeature([], tf.int64)
        }
    )
    image_size = 24
    image = tf.decode_raw(image_features['image/encoded'], tf.uint8)
    image = tf.reshape(image, [image_size, image_size, 3])
    image = (tf.cast(image, tf.float32) - 127.5) / 128
    # image = tf.image.per_image_standardization(image)
    label = tf.cast(image_features['image/label'], tf.float32)
    image, label = tf.train.batch(
        [image, label],
        batch_size=batch_size,
        num_threads=2,
        capacity=1 * batch_size
    )
    label = tf.reshape(label, [batch_size])
    return image, label


def read():
    BATCH_SIZE = 64
    net = 'PNet'
    dataset_dir = "imglists/PNet"
    landmark_dir = os.path.join(dataset_dir, 'train_PNet_ALL_few.tfrecord_shuffle')
    images, labels, rois, landmarks = read_single_tfrecord(landmark_dir, BATCH_SIZE, net)
    '''
    pos_dir = os.path.join(dataset_dir,'pos.tfrecord_shuffle')
    part_dir = os.path.join(dataset_dir,'part.tfrecord_shuffle')
    neg_dir = os.path.join(dataset_dir,'neg.tfrecord_shuffle')
    dataset_dirs = [pos_dir,part_dir,neg_dir]
    pos_radio = 1.0/5;part_radio = 1.0/5;neg_radio=3.0/5
    batch_sizes = [int(np.ceil(BATCH_SIZE*pos_radio)),int(np.ceil(BATCH_SIZE*part_radio)),int(np.ceil(BATCH_SIZE*neg_radio))]
    images, labels, rois = read_multi_tfrecords(dataset_dirs,batch_sizes, net)
    '''
    with tf.Session() as sess:
        i = 0
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        try:
            while not coord.should_stop() and i < 1:
                # 在这里之使用一个batch
                im_batch, label_batch, roi_batch, landmark_batch = sess.run([images, labels, rois, landmarks])
                i += 1
        except tf.errors.OutOfRangeError:
            print("完成！！！")
        finally:
            coord.request_stop()
        coord.join(threads)
    # print im_batch.shape
    # print label_batch.shape
    # print roi_batch.shape
    # print landmark_batch.shape
    num_landmark = len(np.where(label_batch == -2)[0])
    print(num_landmark)
    num_batch, h, w, c = im_batch.shape
    for i in range(num_batch):
        # cv2.resize(src, dsize)
        cc = cv2.resize(im_batch[i], (120, 120))
        # print label_batch
        # print roi_batch
        # print landmark_batch
        print(label_batch)
        for j in range(5):
            cv2.circle(cc, (int(landmark_batch[i][2 * j] * 120), int(landmark_batch[i][2 * j + 1] * 120)), 3,
                       (0, 0, 255))
        cv2.imshow("lala", cc)
        cv2.waitKey()


if __name__ == '__main__':
    read()
