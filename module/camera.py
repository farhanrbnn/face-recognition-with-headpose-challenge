import cv2
import face_recognition as fr
import pickle 
import numpy as np 


class VideoCamera(object):

	def __init__(self, cap):
		self.cap = cap
		
	def __del__(self):
		self.cap.release()

	def get_frame(self):
		frame = self.cap.read()
		data = pickle.loads(open('encodings.pickle', 'rb').read())
		encodings = data['encodings']
		name = data['names']

		recognize = []

		process_video = True

		if process_video:

			# get face location and face encodings
			face_locations = fr.face_locations(frame, number_of_times_to_upsample = 0, model = 'hog')
			face_encodings = fr.face_encodings(frame, known_face_locations = face_locations)

			for face_location in face_locations:
				# make a bounding box
				top, right, bottom, left = face_location
				cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

			for face_encoding in face_encodings:
				face_distances = fr.face_distance(encodings, face_encodings[0])

				best_match_index = np.argmin(face_distances)

				if face_distances[best_match_index] and face_distances[best_match_index] < 0.4:
					name = name[best_match_index]
					# print(name)
					recognize.append(name)

		ret, jpeg = cv2.imencode('.jpg', frame)
		
		return [jpeg.tobytes(), recognize]
