import cv2
import os

import datetime
import numpy as np
from matplotlib.image import imsave


def save_img(path, img):
    """
    Saves a given image at given location.
    :param path: Location where image is to be saved.
    :param img: Image
    :return: None
    """
    imsave(path, img)


def generate_points(m, b, x):
    """
    Generates a list of 2 (x, y) tuples to be used by opencv line method.
    :param m: Slope of the line
    :param b: y-intercept of the line
    :param x: initial x co-ordinate to begin with
    :return: A list of two (x,y) tuples which can be used by opencv line method
    to draw a line.
    """
    x1 = x
    y1 = m*x1 + np.mean(b)
    x2 = x + 5000
    y2 = m*x2 + np.mean(b)
    return [(int(x1), int(y1)), (int(x2), int(y2))]


def get_slope(x1, y1, x2, y2):
    """

    :param x1: x1 co-ordinate
    :param y1: y1 co-ordinate
    :param x2: x2 co-ordinate
    :param y2: y2 co-ordinate
    :return: slope of the line joining (x1, y1) and (x2, y2)
    """
    if x1 == x2:
        return np.Infinity
    else:
        return (y2 - y1)/(x2 - x1)


def get_intercept(x1, y1, x2, y2):
    """

    :param x1: x1 co-ordinate
    :param y1: y1 co-ordinate
    :param x2: x2 co-ordinate
    :param y2: y2 co-ordinate
    :return: y-intercept of the line joining (x1, y1) and (x2, y2)
    """
    if x1 == x2:
        return np.Infinity
    if y1 == y2:
        return y1
    return y2 - ((y2 - y1)/(x2 - x1))*x2


def region_of_interest(img, vertices):
    """
    Preserves a given area of image, specified by vertices. Changes color of every other
    pixel to black.

    If you are changing your test set, make sure to change the vertices so that
    it contains the region where lanes are most likely present and noise is minimum.

    :param img: source image
    :param vertices: Co-ordinates of the vertices
    :return: masked image
    """
    mask = np.zeros_like(img)
    if len(img.shape) > 2:
        channel_count = img.shape[2]
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def remove_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


def divide_intercept(slope_array, intercept_array):
    mean_slope = np.mean(slope_array)
    b_low = []
    b_high = []
    for i in range(len(slope_array)):
        if slope_array[i] < mean_slope:
            b_low.append(intercept_array[i])
        else:
            b_high.append(intercept_array[i])
    return b_low, b_high


def divide_slope(slope_array):
    mean_slope = np.mean(slope_array)
    m_low = []
    m_high = []
    for slope in slope_array:
        if slope < mean_slope:
            m_low.append(slope)
        else:
            m_high.append(slope)
    return m_low, m_high


def get_vertices(imshape):
    lower_left = [0, 0]
    lower_right = [imshape[1], 0]
    top_left = [0, imshape[0] * 120 // 128]
    top_right = [imshape[1], imshape[0] * 120 // 128]
    return [np.array([lower_left, top_left, top_right, lower_right], dtype=np.int32)]


def run(save_final_image=False, min_line_length=26, max_line_gap=6):
    start = datetime.datetime.now()
    for source_img in os.listdir(source_dir):
        try:
            img = cv2.imread(source_dir + source_img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 100)
            imshape = edges.shape
            vertices = get_vertices(imshape)
            edges = region_of_interest(edges, vertices)
            lines = cv2.HoughLinesP(edges, 5, np.pi/90, 70, min_line_length, max_line_gap)
            slope_intercept_pairs = []
            for line in lines:
                for x1, y1, x2, y2 in line:
                    slope = get_slope(x1, y1, x2, y2)
                    intercept = get_intercept(x1, y1, x2, y2)
                    if slope != np.Infinity and intercept != np.Infinity:
                        slope_intercept_pairs.append([slope, intercept])
            slope_array = np.asarray(slope_intercept_pairs)[:, 0]
            intercept_array = np.asarray(slope_intercept_pairs)[:, 1]
            m_low, m_high = divide_slope(slope_array)
            b_low, b_high = divide_intercept(slope_array, intercept_array)
            low_points = generate_points(np.mean(m_low), np.mean(b_low), 50)
            high_points = generate_points(np.mean(m_high), np.mean(b_high), 50)
            if save_final_image:
                cv2.line(img, low_points[0], low_points[1], color=(0, 0, 255), thickness=8)
                cv2.line(img, high_points[0], high_points[1], color=(0, 0, 255), thickness=8)
                save_img("hough_output/final_" + source_img, img)
        except Exception as e:
            print(e)
            continue
    end = datetime.datetime.now()
    print(end - start)


if __name__ == "__main__":
    source_dir = "autocom_images/"
    run()
