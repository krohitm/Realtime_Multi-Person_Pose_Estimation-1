import pandas as pd
import cv2 as cv
from ast import literal_eval as make_tuple
import os, argparse, sys

parser = argparse.ArgumentParser(description='Folder locations')
#parser.add_argument('--images_location', dest='images_location', 
#                    help='home directory of images', type=str)
parser.add_argument('--store_location', dest='store_location', 
                    help='home directory to store images', type=str)

args = parser.parse_args()
storage_loc = args.store_location

def write_to_csv(folder):
    postures = pd.DataFrame(pose, columns=['pose'])
    pose_info = pd.concat([postures,data], axis=1)

    #print os.path.join(storage_loc, 'poselet_and_posture.csv')
    pose_info.to_csv(os.path.join(storage_loc, folder, 'poselet_and_posture.csv'), index=False)
    sys.exit()

_,folders,_ = os.walk(storage_loc).next()
folders.sort()

#resizing to 368*654 as mentioned in the paper
resize_x = 0.340625
resize_y = 0.340740
    
for folder in folders:
    #if folder != '2017-06-20-0948-40':
    if folder != '2017-07-10-2013-02':
        continue
    if os.path.exists(os.path.join(storage_loc, folder, 'poselet_and_posture.csv')):
        data = pd.read_csv(os.path.join(storage_loc, folder, 'poselet_and_posture.csv'),
                                    delimiter=',', dtype={'image_name':str})
    #data_temp = pd.read_csv(os.path.join(storage_loc, 'poselet_and_posture.csv'),
    #                   delimiter=',', dtype={'image_name':str})[['pose','image_name']]
        pose = list(data['pose'].dropna())
        start = len(pose)
        prev_img_name = data.iloc[start-1]['image_name']
        data.drop(['pose'], inplace=True, axis=1)
    else:
        data = pd.read_csv(os.path.join(storage_loc, folder, 'points.csv'),
                                    delimiter=',', dtype={'image_name':str})
        pose = []
        start = 0

    num_detections = len(data['image_name'])
    all_body_points = data.iloc[:][['Neck','RShoulder','RElbow','LElbow','RHip','RKnee','LHip','LKnee','Nose','REye','LEye']]

    change_pose_flag = 0
    
    i = start
    while i < num_detections:
    #for i in range(start, num_detections):
        img_name = data.iloc[i]['image_name']
        if pd.isnull(img_name):
            img_name = prev_img_name
            data.set_value(i, 'image_name', img_name)
        else:
            prev_img_name = img_name
    
        canvas = cv.imread(img_name) # B,G,R order
        canvas = cv.resize(canvas, None, fx = resize_x, fy = resize_x, 
                           interpolation = cv.INTER_CUBIC)
    
        body_points = all_body_points.loc[i]
        cv.namedWindow(img_name, cv.WINDOW_NORMAL)
        for point in body_points:
            if not pd.isnull(point):
                point = make_tuple(point)
                cv.circle(canvas, (int(float(point[0])), int(float(point[1]))), 4, 
                          color=[0, 0, 255], thickness=-1)
        cv.imshow(img_name,canvas)
    
        key_flag=0
        print "press 1 for sitting on bed, 2 for standing, 3 for lying, 4 for sitting on chair, 5 for supine, 6 for bending"
        print "press n to skip, w for incorrect points, u for unclear, f for correcting previous pose"
        while key_flag==0:
            key_pose = cv.waitKey(30)
            if key_pose == ord('1'):
                cur_pose = 'sitting on bed'
                key_flag=1
            elif key_pose == ord('2'):
                cur_pose= 'standing'
                key_flag=1
            elif key_pose == ord('3'):
                cur_pose= 'lying'
                key_flag=1
            elif key_pose == ord('4'):
                cur_pose= 'sitting on chair'
                key_flag=1
            elif key_pose == ord('5'):
                cur_pose= 'supine'
                key_flag=1
            elif key_pose == ord('6'):
                cur_pose= 'bending'
                key_flag=1
            elif key_pose == ord('n'):
                cur_pose='none'
                key_flag=1
            elif key_pose == ord('w'):
                cur_pose= 'incorrect'
                key_flag=1
            elif key_pose == ord('u'):
                cur_pose= 'unclear'
                key_flag=1
            elif key_pose == ord('s'):
                write_to_csv(folder)
            elif key_pose == ord('f'):
                change_pose_flag = 1
                i -= 1
                key_flag = 1
                
        cv.destroyAllWindows()
        if change_pose_flag == 0:
            pose.append(cur_pose)
        else:
            pose.pop()
            change_pose_flag = 0
            i -= 1
        
        i += 1
    
    write_to_csv(folder)