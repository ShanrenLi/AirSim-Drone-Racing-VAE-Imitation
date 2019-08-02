import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import random
import os
import matplotlib.pyplot as plt
import glob
from PIL import Image
import cv2
from sklearn.model_selection import train_test_split


def normalize_v(v):
    # normalization of velocities from whatever to [-1, 1] range
    v_x_range = [-1, 7]
    v_y_range = [-3, 3]
    v_z_range = [-3, 3]
    v_yaw_range = [-1, 1]
    if len(v.shape) == 1:
        # means that it's a 1D vector of velocities
        v[0] = 2.0 * (v[0] - v_x_range[0]) / (v_x_range[1] - v_x_range[0]) - 1.0
        v[1] = 2.0 * (v[1] - v_y_range[0]) / (v_y_range[1] - v_y_range[0]) - 1.0
        v[2] = 2.0 * (v[2] - v_z_range[0]) / (v_z_range[1] - v_z_range[0]) - 1.0
        v[3] = 2.0 * (v[3] - v_yaw_range[0]) / (v_yaw_range[1] - v_yaw_range[0]) - 1.0
    elif len(v.shape) == 2:
        # means that it's a 2D vector of velocities
        v[:, 0] = 2.0 * (v[:, 0] - v_x_range[0]) / (v_x_range[1] - v_x_range[0]) - 1.0
        v[:, 1] = 2.0 * (v[:, 1] - v_y_range[0]) / (v_y_range[1] - v_y_range[0]) - 1.0
        v[:, 2] = 2.0 * (v[:, 2] - v_z_range[0]) / (v_z_range[1] - v_z_range[0]) - 1.0
        v[:, 3] = 2.0 * (v[:, 3] - v_yaw_range[0]) / (v_yaw_range[1] - v_yaw_range[0]) - 1.0
    else:
        raise Exception('Error in data format of V shape: {}'.format(v.shape))
    return v


def de_normalize_v(v):
    # normalization of velocities from [-1, 1] range to whatever
    v_x_range = [-1, 7]
    v_y_range = [-3, 3]
    v_z_range = [-3, 3]
    v_yaw_range = [-1, 1]
    if len(v.shape) == 1:
        # means that it's a 1D vector of velocities
        v[0] = (v[0] + 1.0) / 2.0 * (v_x_range[1] - v_x_range[0]) + v_x_range[0]
        v[1] = (v[1] + 1.0) / 2.0 * (v_y_range[1] - v_y_range[0]) + v_y_range[0]
        v[2] = (v[2] + 1.0) / 2.0 * (v_z_range[1] - v_z_range[0]) + v_z_range[0]
        v[3] = (v[3] + 1.0) / 2.0 * (v_yaw_range[1] - v_yaw_range[0]) + v_yaw_range[0]
    elif len(v.shape) == 2:
        # means that it's a 2D vector of velocities
        v[:, 0] = (v[:, 0] + 1.0) / 2.0 * (v_x_range[1] - v_x_range[0]) + v_x_range[0]
        v[:, 1] = (v[:, 1] + 1.0) / 2.0 * (v_y_range[1] - v_y_range[0]) + v_y_range[0]
        v[:, 2] = (v[:, 2] + 1.0) / 2.0 * (v_z_range[1] - v_z_range[0]) + v_z_range[0]
        v[:, 3] = (v[:, 3] + 1.0) / 2.0 * (v_yaw_range[1] - v_yaw_range[0]) + v_yaw_range[0]
    else:
        raise Exception('Error in data format of V shape: {}'.format(v.shape))
    return v


def normalize_gate(pose):
    # normalization of velocities from whatever to [-1, 1] range
    r_range = [3.0, 10.0]
    cam_fov = 90  # in degrees -- needs to be a bit smaller than 90 in fact because of cone vs. square
    alpha = cam_fov / 180.0 * np.pi / 2.0  # alpha is half of fov angle
    theta_range = [-alpha, alpha]
    psi_range = [np.pi / 2 - alpha, np.pi / 2 + alpha]
    eps = 0.0
    phi_rel_range = [-np.pi + eps, 0 - eps]
    if len(pose.shape) == 1:
        # means that it's a 1D vector of velocities
        pose[0] = 2.0 * (pose[0] - r_range[0]) / (r_range[1] - r_range[0]) - 1.0
        pose[1] = 2.0 * (pose[1] - theta_range[0]) / (theta_range[1] - theta_range[0]) - 1.0
        pose[2] = 2.0 * (pose[2] - psi_range[0]) / (psi_range[1] - psi_range[0]) - 1.0
        pose[3] = 2.0 * (pose[3] - phi_rel_range[0]) / (phi_rel_range[1] - phi_rel_range[0]) - 1.0
    elif len(pose.shape) == 2:
        # means that it's a 2D vector of velocities
        pose[:, 0] = 2.0 * (pose[:, 0] - r_range[0]) / (r_range[1] - r_range[0]) - 1.0
        pose[:, 1] = 2.0 * (pose[:, 1] - theta_range[0]) / (theta_range[1] - theta_range[0]) - 1.0
        pose[:, 2] = 2.0 * (pose[:, 2] - psi_range[0]) / (psi_range[1] - psi_range[0]) - 1.0
        pose[:, 3] = 2.0 * (pose[:, 3] - phi_rel_range[0]) / (phi_rel_range[1] - phi_rel_range[0]) - 1.0
    else:
        raise Exception('Error in data format of V shape: {}'.format(pose.shape))
    return pose


def de_normalize_gate(pose):
    # normalization of velocities from [-1, 1] range to whatever
    r_range = [3.0, 10.0]
    cam_fov = 90  # in degrees -- needs to be a bit smaller than 90 in fact because of cone vs. square
    alpha = cam_fov / 180.0 * np.pi / 2.0  # alpha is half of fov angle
    theta_range = [-alpha, alpha]
    psi_range = [np.pi / 2 - alpha, np.pi / 2 + alpha]
    eps = 0.0
    phi_rel_range = [-np.pi + eps, 0 - eps]
    if len(pose.shape) == 1:
        # means that it's a 1D vector of velocities
        pose[0] = (pose[0] + 1.0) / 2.0 * (r_range[1] - r_range[0]) + r_range[0]
        pose[1] = (pose[1] + 1.0) / 2.0 * (theta_range[1] - theta_range[0]) + theta_range[0]
        pose[2] = (pose[2] + 1.0) / 2.0 * (psi_range[1] - psi_range[0]) + psi_range[0]
        pose[3] = (pose[3] + 1.0) / 2.0 * (phi_rel_range[1] - phi_rel_range[0]) + phi_rel_range[0]
    elif len(pose.shape) == 2:
        # means that it's a 2D vector of velocities
        pose[:, 0] = (pose[:, 0] + 1.0) / 2.0 * (r_range[1] - r_range[0]) + r_range[0]
        pose[:, 1] = (pose[:, 1] + 1.0) / 2.0 * (theta_range[1] - theta_range[0]) + theta_range[0]
        pose[:, 2] = (pose[:, 2] + 1.0) / 2.0 * (psi_range[1] - psi_range[0]) + psi_range[0]
        pose[:, 3] = (pose[:, 3] + 1.0) / 2.0 * (phi_rel_range[1] - phi_rel_range[0]) + phi_rel_range[0]
    else:
        raise Exception('Error in data format of V shape: {}'.format(pose.shape))
    return pose


def create_dataset_csv(data_dir, batch_size, res, num_channels):
    # prepare image dataset from a folder
    files_list = glob.glob(os.path.join(data_dir, 'images/*.png'))
    files_list.sort() # make sure we're reading the images in order later
    images_list = []
    for file in files_list:
        if num_channels == 1:
            im = Image.open(file).resize((res, res), Image.BILINEAR).convert('L')
            im = np.expand_dims(np.array(im), axis=-1) / 255.0 * 2 - 1.0  # add one more axis and convert to the -1 -> 1 scale
        elif num_channels == 3:
            im = Image.open(file).resize((res, res), Image.BILINEAR)
            im = np.array(im)/255.0*2 - 1.0  # convert to the -1 -> 1 scale
        images_list.append(im)
    images_np = np.array(images_list).astype(np.float32)

    # prepare gate R THETA PSI PHI as np array reading from a file
    raw_table = np.loadtxt(data_dir + '/gate_training_data.csv', delimiter=' ')
    # sanity check
    if raw_table.shape[0] != images_np.shape[0]:
        raise Exception('Number of images ({}) different than number of entries in table ({}): '.format(images_np.shape[0], raw_table.shape[0]))
    raw_table.astype(np.float32)

    # print some useful statistics
    print("Average gate values: {}".format(np.mean(raw_table, axis=1)))
    print("Median  gate values: {}".format(np.median(raw_table, axis=1)))
    print("STD of  gate values: {}".format(np.std(raw_table, axis=1)))
    print("Max of  gate values: {}".format(np.max(raw_table, axis=1)))
    print("Min of  gate values: {}".format(np.min(raw_table, axis=1)))

    # normalize distances to gate to [-1, 1] range
    raw_table = normalize_gate(raw_table)

    img_train, img_test, dist_train, dist_test = train_test_split(images_np, raw_table, test_size=0.1, random_state=42)

    # convert to tf format dataset and prepare batches
    ds_train = tf.data.Dataset.from_tensor_slices((img_train, dist_train)).batch(batch_size)
    ds_test = tf.data.Dataset.from_tensor_slices((img_test, dist_test)).batch(batch_size)

    return ds_train, ds_test


def create_test_dataset_csv(data_dir, res, num_channels):
    # prepare image dataset from a folder
    files_list = glob.glob(os.path.join(data_dir, 'images/*.png'))
    files_list.sort()  # make sure we're reading the images in order later
    images_list = []
    for file in files_list:
        if num_channels == 1:
            im = Image.open(file).resize((res, res), Image.BILINEAR).convert('L')
            im = np.expand_dims(np.array(im), axis=-1) / 255.0 * 2 - 1.0  # add one more axis and convert to the -1 -> 1 scale
        elif num_channels == 3:
            im = Image.open(file).resize((res, res), Image.BILINEAR)
            im = np.array(im)/255.0*2 - 1.0  # convert to the -1 -> 1 scale
        images_list.append(im)
    images_np = np.array(images_list).astype(np.float32)

    # prepare gate R THETA PSI PHI as np array reading from a file
    raw_table = np.loadtxt(data_dir + '/gate_training_data.csv', delimiter=' ')
    # sanity check
    if raw_table.shape[0] != images_np.shape[0]:
        raise Exception('Number of images ({}) different than number of entries in table ({}): '.format(images_np.shape[0], raw_table.shape[0]))
    raw_table.astype(np.float32)

    # print some useful statistics
    print("Average gate values: {}".format(np.mean(raw_table, axis=0)))
    print("Median  gate values: {}".format(np.median(raw_table, axis=0)))
    print("STD of  gate values: {}".format(np.std(raw_table, axis=0)))
    print("Max of  gate values: {}".format(np.max(raw_table, axis=0)))
    print("Min of  gate values: {}".format(np.min(raw_table, axis=0)))

    # normalize distances to gate to [-1, 1] range
    raw_table = normalize_gate(raw_table)
    # print some useful statistics
    print('After normalizing:')
    print("Average gate values: {}".format(np.mean(raw_table, axis=0)))
    print("Median  gate values: {}".format(np.median(raw_table, axis=0)))
    print("STD of  gate values: {}".format(np.std(raw_table, axis=0)))
    print("Max of  gate values: {}".format(np.max(raw_table, axis=0)))
    print("Min of  gate values: {}".format(np.min(raw_table, axis=0)))

    return images_np, raw_table


def create_dataset_txt(data_dir, batch_size, res, num_channels):
    vel_table = np.loadtxt(data_dir + '/proc_vel.txt', delimiter=',').astype(np.float32)
    with open(data_dir + '/proc_images.txt') as f:
        img_table = f.read().splitlines()

    # sanity check
    if vel_table.shape[0] != len(img_table):
        raise Exception('Number of images ({}) different than number of entries in table ({}): '.format(len(img_table), vel_table.shape[0]))

    images_list = []
    for img_name in img_table:
        im = Image.open(img_name).resize((res, res), Image.BILINEAR)
        im = np.array(im)/255.0*2 - 1.0  # convert to the -1 -> 1 scale
        # TODO: figure out why there's a 4th channel in dataset
        im = im[:,:,:3]
        images_list.append(im)
    images_np = np.array(images_list).astype(np.float32)

    # print some useful statistics and normalize distances
    print("Num samples: {}".format(vel_table.shape[0]))
    print("Average vx: {}".format(np.mean(vel_table[:, 0])))
    print("Average vy: {}".format(np.mean(vel_table[:, 1])))
    print("Average vz: {}".format(np.mean(vel_table[:, 2])))
    print("Average vyaw: {}".format(np.mean(vel_table[:, 3])))

    # normalize the values of velocities to the [-1, 1] range
    vel_table = normalize_v(vel_table)

    img_train, img_test, dist_train, dist_test = train_test_split(images_np, vel_table, test_size=0.1, random_state=42)

    # convert to tf format dataset and prepare batches
    ds_train = tf.data.Dataset.from_tensor_slices((img_train, dist_train)).batch(batch_size)
    ds_test = tf.data.Dataset.from_tensor_slices((img_test, dist_test)).batch(batch_size)

    return ds_train, ds_test
