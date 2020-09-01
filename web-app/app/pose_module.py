import cv2
import dlib 
import numpy as np 
from imutils import face_utils
import imutils
import time
import random


class FacePosition:


    def __init__ (self, cap):
        K= [6.5308391993466671e+002, 0.0, 3.1950000000000000e+002,
                  0.0, 6.5308391993466671e+002, 2.3950000000000000e+002,
                  0.0, 0.0, 1.0]
        D =  [7.0834633684407095e-002, 6.9140193737175351e-002, 0.0, 0.0, -1.3073460323689292e+000]

        self.cap = cap
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('predictor.dat')
        self.cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
        self.dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)
        self.object_pts = np.float32([[6.825897, 6.760612, 4.402142],
                                      [1.330353, 7.122144, 6.903745],
                                      [-1.330353, 7.122144, 6.903745],
                                      [-6.825897, 6.760612, 4.402142],
                                      [5.311432, 5.485328, 3.987654],
                                      [1.789930, 5.393625, 4.413414],
                                      [-1.789930, 5.393625, 4.413414],
                                      [-5.311432, 5.485328, 3.987654],
                                      [2.005628, 1.409845, 6.165652],
                                      [-2.005628, 1.409845, 6.165652],
                                      [2.774015, -2.080775, 5.048531],
                                      [-2.774015, -2.080775, 5.048531],
                                      [0.000000, -3.116408, 6.097667],
                                      [0.000000, -7.415691, 4.070434]])
        self.reprojectdst = np.float32([[10.0, 10.0, 10.0],
                                     [10.0, 10.0, -10.0],
                                     [10.0, -10.0, -10.0],
                                     [10.0, -10.0, 10.0],
                                     [-10.0, 10.0, 10.0],
                                     [-10.0, 10.0, -10.0],
                                     [-10.0, -10.0, -10.0],
                                     [-10.0, -10.0, 10.0]])
        self.line_pairs = [[0, 1], [1, 2], [2, 3], [3, 0],
                           [4, 5], [5, 6], [6, 7], [7, 4],
                           [0, 4], [1, 5], [2, 6], [3, 7]]

    def run(self):
        frame = self.cap.read()
        frame = imutils.resize(frame, width=300)

        position = []

        if True:
            face_rects = self.detector(frame, 0)
            if len(face_rects) > 0:
                shape = self.predictor(frame, face_rects[0])
                shape = face_utils.shape_to_np(shape)

                image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                               shape[39], shape[42], shape[45], shape[31], shape[35],
                               shape[48], shape[54], shape[57], shape[8]])

                _, rotation_vec, translation_vec = cv2.solvePnP(self.object_pts, image_pts, 
                                                        self.cam_matrix, self.dist_coeffs)

                reprojectdst, _ = cv2.projectPoints(self.reprojectdst, rotation_vec, 
                                                    translation_vec, self.cam_matrix, self.dist_coeffs)
                reprojectdst = tuple(map(tuple, reprojectdst.reshape(8, 2)))

                rotation_mat, _ = cv2.Rodrigues(rotation_vec)

                pose_mat = cv2.hconcat((rotation_mat, translation_vec))
                _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

                for (x, y) in shape:
                    cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

                for start, end in self.line_pairs:
                    cv2.line(frame, reprojectdst[start], reprojectdst[end], (0, 0, 255))

                cv2.putText(frame, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 0, 0), thickness=2)
                cv2.putText(frame, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 0, 0), thickness=2)
                cv2.putText(frame, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            0.75, (0, 0, 0), thickness=2)

                euler_one = euler_angle[0, 0]
                euler_two = euler_angle[1, 0]
                euler_three = euler_angle[1, 0]

                # print('euler Y : {}'.format(euler_two))

                if (euler_two < -40):
                    position = 'left'
                    print(position)

                if (euler_two > 15):
                    position = 'right'
                    print(position)

        return position
            