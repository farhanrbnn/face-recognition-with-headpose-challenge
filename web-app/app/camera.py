import cv2
import face_recognition as fr
import pickle 
import numpy as np 
import time
import imutils

class VideoCamera(object):

	def __init__(self, video):
		self.video = video

	def __del__(self):
		self.video.release()

	def get_frame(self):
		frame = self.video.read()
		frame = imutils.resize(frame, width=300)

		data = pickle.loads(open('encodings.pickle', 'rb').read())
		encodings = data['encodings']
		name = data['names']

		recognize = []
		count_bbox = []

		# print(topp, rightt, bottomm, leftt)

		process_video = True

		if process_video:
			start = time.time()
			# get face location and face encodings
			face_locations = fr.face_locations(frame, number_of_times_to_upsample = 0, model = 'hog')
			face_encodings = fr.face_encodings(frame, known_face_locations = face_locations)

			for face_location in face_locations:
				# make a bounding box
				top, right, bottom, left = face_location

				count_bbox.append(face_location)

				# if len(count_bbox) == 2:
				# 	top_one, right_one, bottom_one, left_one = count_bbox[0]
				# 	top_two, right_two, bottom_two, left_two = count_bbox[1]

				# 	length_bbox_one = left_one - right_one
				# 	width_bbox_one = top_one - bottom_one

				# 	length_bbox_two = left_two - right_two
				# 	width_bbox_two = top_two - bottom_two

				# 	print('AREA BOUNDING BOX 1: {}'.format(length_bbox_one*width_bbox_one))
				# 	print('AREA BOUNDING BOX 2: {}'.format(length_bbox_two*width_bbox_two))

				cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

			for face_encoding in face_encodings:
				face_distances = fr.face_distance(encodings, face_encodings[0])

				best_match_index = np.argmin(face_distances)

				if face_distances[best_match_index] and face_distances[best_match_index] < 0.4:
					end = time.time()
					# print('time elapsed: {}'.format(end - start))
					name = name[best_match_index]

					recognize.append(name)

					cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

		ret, jpeg = cv2.imencode('.jpg', frame)
		
		return [jpeg.tobytes(), recognize]