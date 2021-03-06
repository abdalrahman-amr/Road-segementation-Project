import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from skimage import exposure
input_name = 'harder_challenge_video.mp4' # 'challenge_video.mp4'
final=[]
left_line = Line()
right_line = Line()

th_sobelx, th_sobely, th_mag, th_dir = (35, 100), (30, 255), (30, 255), (0.7, 1.3)
th_h, th_l, th_s = (10, 100), (0, 60), (85, 255)

# camera matrix & distortion coefficient
mtx, dist = calib()

if __name__ == '__main__':
    cap = cv2.VideoCapture(input_name)
    while (True):
        success, frame = cap.read()
        if(success):

             # Correcting for Distortion
            undist_img = undistort(frame, mtx, dist)
                # resize video
            undist_img = cv2.resize(undist_img, None, fx=1 / 2, fy=1 / 2, interpolation=cv2.INTER_AREA)
            rows, cols = undist_img.shape[:2]

            combined_gradient = gradient_combine(undist_img, th_sobelx, th_sobely, th_mag, th_dir)
                #cv2.imshow('gradient combined image', combined_gradient)

            combined_hls = hls_combine(undist_img, th_h, th_l, th_s)
                #cv2.imshow('HLS combined image', combined_hls)

            combined_result = comb_result(combined_gradient, combined_hls)

            c_rows, c_cols = combined_result.shape[:2]
            s_LTop2, s_RTop2 = [c_cols / 2 - 24, 5], [c_cols / 2 + 24, 5]
            s_LBot2, s_RBot2 = [110, c_rows], [c_cols - 110, c_rows]

            src = np.float32([s_LBot2, s_LTop2, s_RTop2, s_RBot2])
            dst = np.float32([(170, 720), (170, 0), (550, 0), (550, 720)])

            warp_img, M, Minv = warp_image(combined_result, src, dst, (720, 720))
            #cv2.imshow('warp', warp_img)



            searching_img = find_LR_lines(warp_img, left_line, right_line)
            #cv2.imshow('LR searching', searching_img)

            w_comb_result, w_color_result = draw_lane(searching_img, left_line, right_line)
            #cv2.imshow('w_comb_result', w_comb_result)

                # Drawing the lines back down onto the road
            color_result = cv2.warpPerspective(w_color_result, Minv, (c_cols, c_rows))
            lane_color = np.zeros_like(undist_img)
            lane_color[220:rows - 12, 0:cols] = color_result

                # Combine the result with the original image
            result = cv2.addWeighted(undist_img, 1, lane_color, 0.3, 0)
                #cv2.imshow('result', result.astype(np.uint8))

            info =  np.zeros_like(result)
            info[5:110, 5:190] = (255, 255, 255)

            info = cv2.addWeighted(result, 1, info, 0.2, 0)


            info = print_road_status(info, left_line, right_line)
            #cv2.imshow('road info', info)

            #out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.waitKey(0)

            final.append(info)   
        else:
            break
    cap.release()
    cv2.destroyAllWindows()






import os
if not os.path.exists("data5"):
    os.makedirs('data5')
for i in range(len(final)):
    name = './data5/frame'+ ""+str(i)+ '.jpg'
    cv2.imwrite(name,final[i])
    
    
    
import cv2
import numpy as np
import glob

img_array = []
i = 0
#for filename in glob.glob("data5/frame"+ ""+str(i)+".jpg"):
for i in range(len(final)):
    img = cv2.imread("data5/frame"+ ""+str(i)+".jpg")
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)


out = cv2.VideoWriter('project2.avi',cv2.VideoWriter_fourcc(*'DIVX'), 25 , size)
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()    
