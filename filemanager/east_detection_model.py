import argparse
from PIL import Image

import torch
import numpy as np
import cv2 as cv
import math
import os
import time


def fourPointsTransform(frame, vertices):

    x_range = abs(vertices[2][0] - vertices[0][0])
    y_range = abs(vertices[3][1] - vertices[1][1])
    print("x_range, y_range")
    print(x_range)
    print(y_range)
    vertices = np.asarray(vertices)
    x_range = int(x_range)
    y_range = int(y_range)
    outputSize = (x_range, y_range)
    targetVertices = np.array([
        [0, outputSize[1] - 1],
        [0, 0],
        [outputSize[0] - 1, 0],
        [outputSize[0] - 1, outputSize[1] - 1]], dtype="float32")

    rotationMatrix = cv.getPerspectiveTransform(vertices, targetVertices)
    result = cv.warpPerspective(frame, rotationMatrix, outputSize)
    return result

def decodeBoundingBoxes(scores, geometry, scoreThresh):
    detections = []
    confidences = []

    assert len(scores.shape) == 4, "Incorrect dimensions of scores"
    assert len(geometry.shape) == 4, "Incorrect dimensions of geometry"
    assert scores.shape[0] == 1, "Invalid dimensions of scores"
    assert geometry.shape[0] == 1, "Invalid dimensions of geometry"
    assert scores.shape[1] == 1, "Invalid dimensions of scores"
    assert geometry.shape[1] == 5, "Invalid dimensions of geometry"
    assert scores.shape[2] == geometry.shape[2], "Invalid dimensions of scores and geometry"
    assert scores.shape[3] == geometry.shape[3], "Invalid dimensions of scores and geometry"
    height = scores.shape[2]
    width = scores.shape[3]
    for y in range(0, height):

        # Extract data from scores
        scoresData = scores[0][0][y]
        x0_data = geometry[0][0][y]
        x1_data = geometry[0][1][y]
        x2_data = geometry[0][2][y]
        x3_data = geometry[0][3][y]
        anglesData = geometry[0][4][y]
        for x in range(0, width):
            score = scoresData[x]

            # If score is lower than threshold score, move to next x
            if (score < scoreThresh):
                continue

            # Calculate offset
            offsetX = x * 4.0
            offsetY = y * 4.0
            angle = anglesData[x]

            # Calculate cos and sin of angle
            cosA = math.cos(angle)
            sinA = math.sin(angle)
            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            # Calculate offset
            offset = ([offsetX + cosA * x1_data[x] + sinA * x2_data[x], offsetY - sinA * x1_data[x] + cosA * x2_data[x]])

            # Find points for rectangle
            p1 = (-sinA * h + offset[0], -cosA * h + offset[1])
            p3 = (-cosA * w + offset[0], sinA * w + offset[1])
            center = (0.5 * (p1[0] + p3[0]), 0.5 * (p1[1] + p3[1]))
            detections.append((center, (w, h), -1 * angle * 180.0 / math.pi))
            confidences.append(float(score))

    # Return detections and confidences
    return [detections, confidences]

def seq2seq_decode(encoder_out, decoder, decoder_input, decoder_hidden, max_length):
    decoded_words = []
    prob = 1.0
    for di in range(max_length):
        decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_out)
        probs = torch.exp(decoder_output)
        _, topi = decoder_output.data.topk(1)
        ni = topi.squeeze(1)
        decoder_input = ni
        prob *= probs[:, ni]
        if ni == utils.EOS_TOKEN:
            break
        else:
            decoded_words.append(converter.decode(ni))

    words = ''.join(decoded_words)
    prob = prob.item()

    return words, prob


def east_detection(imagepath):

    opt_dict = {}
    opt_dict['input'] = imagepath
    opt_dict['model'] = './east_path/frozen_east_text_detection.pb'
    # opt_dict['ocr'] = "./textmodelpath/crnn_cs_CN.onnx"
    opt_dict['width'] = int(640)
    opt_dict['height'] = int(640)
    opt_dict['thr'] = float(0.5)
    opt_dict['nms'] = float(0.4)

    confThreshold = opt_dict['thr']
    nmsThreshold = opt_dict['nms']
    inputWidth = opt_dict['width']
    inputHeight = opt_dict['height']
    modelDetector = opt_dict['model']

    # Load network
    detector = cv.dnn.readNet(modelDetector)

    # Create a new named window
    outNames = []
    outNames.append("feature_fusion/Conv_7/Sigmoid")
    outNames.append("feature_fusion/concat_3")

    # Open a video file or an image file or a camera stream
    #cap = cv.imread(opt_dict['input'])
    #frame = cap

    frame = Image.open(opt_dict['input']).convert('RGB')
    print(frame.width)
    print(frame.height)
    frame_width = (frame.width // 32) * 32
    frame_height = (frame.height // 32) * 32
    print(frame_width)
    print(frame_height)
    frame = np.asarray(frame)


    opt_dict['width'] = frame_width
    opt_dict['height'] = frame_height

    # cv.imshow(kWinName,cap)

    if os.path.exists(opt_dict['input']):
        # Get frame height and width
        height_ = frame.shape[0]
        width_ = frame.shape[1]
        rW = width_ / float(inputWidth)
        rH = height_ / float(inputHeight)

        # Create a 4D blob from frame.
        blob = cv.dnn.blobFromImage(frame, 1.0, (inputWidth, inputHeight), (123.68, 116.78, 103.94), True, False)

        # Run the detection model
        detector.setInput(blob)


        outs = detector.forward(outNames)


        # Get scores and geometry
        scores = outs[0]
        geometry = outs[1]
        [boxes, confidences] = decodeBoundingBoxes(scores, geometry, confThreshold)

        # Apply NMS
        indices = cv.dnn.NMSBoxesRotated(boxes, confidences, confThreshold, nmsThreshold)
        vertices_list  = []
        for i in indices:
            # get 4 corners of the rotated rect
            vertices = cv.boxPoints(boxes[i[0]])
            # scale the bounding box coordinates based on the respective ratios
            for j in range(4):
                vertices[j][0] *= rW
                vertices[j][1] *= rH
            # print("vertices")
            # print(type(vertices))
            vertices_list.append(vertices)

        # print(vertices_list)
    return vertices_list



