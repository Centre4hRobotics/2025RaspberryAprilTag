import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    cap.release()
    exit()

ret, frame = cap.read()
if ret:
    cv.imwrite("/home/pi/image.png", frame)
else:
    print("Failed!!")

cap.release()
