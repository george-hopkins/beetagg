import itertools
import cv2
import numpy as np


class Detector():
    def detect(self, path):
        image = cv2.imread(path, 0)
        _, thresh = cv2.threshold(image, 127, 255, 0)
        # thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return self.detect_binary(thresh)

    def detect_binary(self, image):
        for corners, pt_size in self._find_corners(image):
            tdst = np.array(corners, dtype='float32')
            tdst = tdst[tdst[:, 0].argsort()]
            tsrc = np.array([[0.0, 0.0], [1.0, 0.0], [0, 1.0], [1.0, 1.0]], dtype='float32')
            transform = cv2.getPerspectiveTransform(tsrc, tdst)

            data = []
            data90 = []
            for j in range(13):
                data.append([])
                data90.append([])
                for i in range(11 + j % 2):
                    x = i/(11 - 1)-((j % 2)/(11 - 1)/2)
                    y = j/(13 - 1)
                    tx, ty = cv2.perspectiveTransform(np.array([[[x, y]]], np.float32), transform)[0][0]
                    data[j].append(self._sample_point(image, tx, ty, pt_size))
                    tx90, ty90 = cv2.perspectiveTransform(np.array([[[y, x]]], np.float32), transform)[0][0]
                    data90[j].append(self._sample_point(image, tx90, ty90, pt_size))

            for candidate in [data, data90]:
                if not (candidate[0][0] and candidate[-1][0] and candidate[0][-1] and candidate[-1][-1]):
                    continue  # invalid corners
                yield list(itertools.chain(*candidate))
                yield list(itertools.chain(*candidate[::-1]))

    def _find_corners(self, image):
        result = []
        _, contours, _ = cv2.findContours(image, 1, 2)
        points = list(map(cv2.minEnclosingCircle, contours))
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            min_dim = min(rect[1][0], rect[1][1])
            if min_dim < 0.5 * min(image.shape[0], image.shape[1]):
                continue  # too small
            if abs(1-rect[1][0]/rect[1][1]) > 0.2:
                continue  # not square

            # find closest 4 points
            box = cv2.boxPoints(rect)
            closest = [None] * len(box)
            for pt, pt_size in points:
                if not (0.03 < pt_size/min_dim < 0.10):
                    continue  # too small/big
                if cv2.pointPolygonTest(box, pt, False) <= 0:
                    continue  # outside
                for i, corner in enumerate(box):
                    dist = cv2.norm(corner-pt)
                    if closest[i] is None or closest[i][0] > dist:
                        closest[i] = (dist, pt, pt_size)
            if None in closest:
                continue  # missing corner point
            pt_size = 0.8 * np.array([c[2] for c in closest]).mean()
            yield [c[1] for c in closest], pt_size

    def _sample_point(self, image, x, y, size):
        roi = image[int(y - size / 2):int(y + size / 2) + 1, int(x - size / 2):int(x + size / 2) + 1]
        return cv2.mean(roi)[0] < 128
