# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/dataloader.ipynb (unless otherwise specified).

__all__ = ['CameraParameters', 'KittiDataset']

# Cell

import os
import glob
import numpy as np

# Cell

class CameraParameters():
    def __init__(self, fx, fy, cx, cy):
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy

    @property
    def camera_matrix(self):
        matrix = np.array([[self.fx, 0.0, self.cx],
                           [0.0, self.fx, self.cy],
                           [0.0, 0.0, 1.0]])
        return matrix

    def __call__(self):
        return self.camera_matrix

# Cell

class KittiDataset():

    def __init__(self, path):

        self.left_images_path=os.path.join(path, 'image_0')
        self.right_images_path=os.path.join(path, 'image_1')

        self.calibfile=os.path.join(path, 'calib.txt')
        self.sequence_count=os.path.dirname(path).split('/')[-1]
        self.gt_path=os.path.join(path, 'data_odometry_poses', 'dataset', 'poses', self.sequence_count + '.txt')
        self.ground_truth=self.load_ground_truth_pose(self.gt_path)

        self.left_image_paths=self.load_image_paths(self.left_images_path)
        self.right_image_paths=self.load_image_paths(self.right_images_path)

        self.camera_intrinsic, self.PL, self.PR =self.load_camera_parameters(self.calibfile)

        assert len(self.ground_truth)==len(self.left_image_paths)

    def convert_text_to_ground_truth(self, gt_line):

        matrix = np.array(gt_line.split()).reshape((3, 4)).astype(np.float32)
        return matrix

    def load_ground_truth_pose(self, gt_path):

        ground_truth = None
        if not os.path.exists(gt_path):
            print("ground truth path is not found.")
            return None

        ground_truth = []

        with open(gt_path) as gt_file:
            gt_lines = gt_file.readlines()

            for gt_line in gt_lines:
                pose = self.convert_text_to_ground_truth(gt_line)
                ground_truth.append(pose)

        return ground_truth

    def load_image_paths(self, image_dir):

        img_paths = [os.path.join(image_dir,img_id) for img_id in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, img_id))]
        img_paths.sort()
        return img_paths

    def load_camera_parameters(self, calibfile):

        if not os.path.exists(calibfile):
            print("camera parameter file path is not found.")
            return None

        calibParams = open(calibfile, 'r').readlines()
        P1Vals = calibParams[0].split()
        P2Vals = calibParams[1].split()
        projL = np.array([[float(P1Vals[row*4 + column + 1]) for column in range(4)] for row in range(3)])
        projR = np.array([[float(P2Vals[row*4 + column + 1]) for column in range(4)] for row in range(3)])
        param = CameraParameters(float(P1Vals[1]), float(P1Vals[6]),
                                float(P1Vals[3]), float(P1Vals[7]))

        return param, projL, projR

    def __len__(self):
        assert len(self.left_image_paths)==len(self.right_image_paths)

        return len(self.left_image_paths)

    def __getitem__(self, index):

        img_left = cv2.imread(self.left_image_paths[index])
        img_right = cv2.imread(self.right_image_paths[index])

        img_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
        img_right  =  cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

        gr_truth = self.ground_truth[index]

        return img_left, img_right, gr_truth