import cv2 as cv
import numpy as np
from gcode_layer_visualization import get_layer_coordinates
import copy
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True)

class DefectDetection:
    def __init__(self, camera_matrix, dist_coeffs, T_nozzle_cam, 
                 gcode_path, img_folder_path, img_taken_position, layer_height = 0.1):
        # set camera intrinsic and extrinsic parameters
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.img_shape = (1920, 1080)
        self.undistort_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self.camera_matrix, 
        self.dist_coeffs, self.img_shape, 1, self.img_shape)
        self.undistort_dist_coeffs = np.array([0., 0., 0., 0., 0.])
        self.undistort_mapx, self.undistort_mapy = cv.initUndistortRectifyMap(self.camera_matrix, self.dist_coeffs, None, 
                                                                              self.undistort_camera_matrix, self.img_shape, 5)
        self.T_nozzle_cam = T_nozzle_cam
        
        self.gcode_path = gcode_path
        self.layer_height = layer_height
        self.nozzle_pos = [0, 0, 0]

        self.img_folder_path = img_folder_path
        self.img_taken_position = img_taken_position

    def update_nozzle_pos(self, layerID):
        Z = (layerID - 1) * self.layer_height + 0.2
        self.nozzle_pos = [self.img_taken_position[0], self.img_taken_position[1], Z]

    # calculate transformation between camera and printer for contour projection
    def get_T_printer_cam(self, layerID):
        self.update_nozzle_pos(layerID)
        T_printer_nozzle = np.array([
            [1, 0, 0, -self.nozzle_pos[0]],
            [0, 1, 0, -self.nozzle_pos[1]],
            [0, 0, 1, -self.nozzle_pos[2]],
            [0, 0, 0, 1]
        ])
        
        T_printer_cam = np.matmul(self.T_nozzle_cam, T_printer_nozzle)
        tvec = T_printer_cam[:3, 3].reshape((3, 1))
        rvec, _ = cv.Rodrigues(T_printer_cam[:3, :3])

        return T_printer_cam, tvec, rvec
    
    # (NOT USED IN THIS PAPER) convert 2D pixel position to 3D position in the printer frame
    def image_pixel_to_Gcode_position(self, defect_coord):
        img_center_pos = copy.copy(self.nozzle_pos) # in printer frame
        img_center_pos[0] -= self.T_nozzle_cam[0, 3]
        img_center_pos[1] += self.T_nozzle_cam[1, 3]

        (w, h) = self.img_shape
        undistort_camera_matrix, roi = cv.getOptimalNewCameraMatrix(self.camera_matrix, 
                                                                    self.dist_coeffs, 
                                                                    (w,h), 1, (w,h))

        fx = undistort_camera_matrix[0, 0]
        fy = undistort_camera_matrix[1, 1]
        f = (fx + fy) / 2
        cx = undistort_camera_matrix[0, 2]
        cy = undistort_camera_matrix[1, 2]
        depth = self.T_nozzle_cam[2, 3]

        dx = defect_coord[0] - cx
        dy = defect_coord[1] - cy

        dX_printer = depth / f * dx
        dY_printer = -depth / f * dy
        defect_pos = copy.copy(img_center_pos) + np.array([dX_printer, dY_printer, 0])

        return defect_pos

    # (NOT USED IN THIS PAPER)
    def get_Gcode_positions(self, defect_coords):
        all_positions = []
        for coord in defect_coords:
            all_positions.append(self.image_pixel_to_Gcode_position(coord))
        return all_positions
    
    # (NOT USED IN THIS PAPER)
    def defect_mask_to_positions(self, defect_mask, type):
        # type 1: centroid
        # type 2: all points
        analysis = cv.connectedComponentsWithStats(defect_mask, 8, cv.CV_32S)
        (totalLabels, label_ids, values, centroid) = analysis

        if type == 1:
            return self.get_Gcode_positions(centroid[1:])
        elif type == 2:
            defect_positions = []
            for i in range(1, totalLabels):
                pixels = np.argwhere(label_ids == i)
                pixels = pixels[:, ::-1]
                defect_positions.append(self.get_Gcode_positions(pixels))
            return defect_positions

    # get contour of certain layer from G-code
    def get_contours(self, layerID):
        x, y, z = get_layer_coordinates(self.gcode_path, layerID, 2) # 2: perimeter
        num_contour = len(x)
        all_contours = []
        for contour_id in range(num_contour):
            size_contour = len(x[contour_id])
            contour_points = np.zeros((size_contour, 3), np.float32)
            contour_points[:, 0] = np.array(x[contour_id])
            contour_points[:, 1] = np.array(y[contour_id])
            contour_points[:, 2] = z
            all_contours.append(contour_points)

        return all_contours
    
    # project contour from G-code to the image
    def project_contour(self, img, layerID, save_projection_img = True):
        img = cv.resize(img, self.img_shape)
        img = cv.remap(img, self.undistort_mapx, self.undistort_mapy, cv.INTER_LINEAR)
        height, width = img.shape[:2]

        isClosed = True
        contour_color = (255, 0, 0)
        thickness = 2
        img_contour = copy.copy(img)

        mask_color = (255, 255, 255)
        masks = []

        _, tvec, rvec = self.get_T_printer_cam(layerID)
        contours = self.get_contours(layerID)
        for contour_points in contours:
            img_points, _ = cv.projectPoints(contour_points, rvec, tvec, self.undistort_camera_matrix, self.undistort_dist_coeffs)
            img_points.reshape(-1, 1, 2)
            mask = np.zeros((height, width), dtype=np.uint8)
            cv.drawContours(mask, [img_points.astype(np.int32)], 0, mask_color, thickness=cv.FILLED)
            masks.append(mask)

            if save_projection_img:
                img_contour = cv.polylines(img_contour, [img_points.astype(np.int32)],isClosed, contour_color, thickness)

        if save_projection_img:
            cv.imwrite(self.img_folder_path+"layer_{}_w_contour.jpg".format(layerID), img_contour)

        # xor all masks
        final_mask = np.zeros((height, width), dtype=np.uint8)
        for mask in masks:
            final_mask = cv.bitwise_xor(final_mask, mask)

        # crop out valid part
        dst = cv.bitwise_and(img, img, mask=final_mask)

        # make background white
        dst[np.where(np.all(dst[..., :3] == 0, -1))] = 255
        r,g,b = cv.split(dst)

        # merge and use mask as alpha channel
        cropped_img = cv.merge([r, g, b, final_mask], 4)
        return cropped_img
    
    # apply binary threshold and area-based filter to detect defects
    def get_defect_mask(self, cropped_img, binary_threshold = 90):
        # Image pre processing
        grayImage = cv.cvtColor(cropped_img, cv.COLOR_BGR2GRAY)

        gaussianBlur = cv.GaussianBlur(grayImage, (5, 5), 0)
        ret, binary = cv.threshold(gaussianBlur, binary_threshold, 255, cv.THRESH_BINARY_INV)

        min_threshold = 10
        max_threshold = 200
        defect_mask = copy.copy(binary)
        analysis = cv.connectedComponentsWithStats(defect_mask, 8, cv.CV_32S)
        (totalLabels, label_ids, values, centroid) = analysis
        for i in range(1, totalLabels):
            if values[i, 4] < min_threshold or values[i, 4] > max_threshold:
                defect_mask[label_ids == i] = 0

        return defect_mask

    def get_defect_positions(self, img, layerID, type = 1, binary_threshold = 90):
        # type 1: centroid
        # type 2: all points
        cropped_img = self.project_contour(img, layerID)
        defect_mask = self.get_defect_mask(cropped_img, binary_threshold)
        cv.imwrite(self.img_folder_path+"layer_{}_crop.png".format(layerID), cropped_img)
        cv.imwrite(self.img_folder_path+"layer_{}_defect.png".format(layerID), defect_mask)

        return self.defect_mask_to_positions(defect_mask, type)