import sys
sys.path.append('C:/Users/nguye/OneDrive/Desktop/ai4theblind/SSD-pytorch/src')
import numpy as np
import argparse
import torch
from transform import SSDTransformer
import cv2
from PIL import Image

from Default_boxes import generate_dboxes
import encoder as Encoder
from models import SSD, ResNet,coco_classes
from imutils.video import FPS, WebcamVideoStream





colors = [None, (39, 129, 113), (164, 80, 133), (83, 122, 114), (99, 81, 172), (95, 56, 104), (37, 84, 86),
          (14, 89, 122),
          (80, 7, 65), (10, 102, 25), (90, 185, 109), (106, 110, 132), (169, 158, 85), (188, 185, 26), (103, 1, 17),
          (82, 144, 81), (92, 7, 184), (49, 81, 155), (179, 177, 69), (93, 187, 158), (13, 39, 73), (12, 50, 60),
          (16, 179, 33), (112, 69, 165), (15, 139, 63), (33, 191, 159), (182, 173, 32), (34, 113, 133), (90, 135, 34),
          (53, 34, 86), (141, 35, 190), (6, 171, 8), (118, 76, 112), (89, 60, 55), (15, 54, 88), (112, 75, 181),
          (42, 147, 38), (138, 52, 63), (128, 65, 149), (106, 103, 24), (168, 33, 45), (28, 136, 135), (86, 91, 108),
          (52, 11, 76), (142, 6, 189), (57, 81, 168), (55, 19, 148), (182, 101, 89), (44, 65, 179), (1, 33, 26),
          (122, 164, 26), (70, 63, 134), (137, 106, 82), (120, 118, 52), (129, 74, 42), (182, 147, 112), (22, 157, 50),
          (56, 50, 20), (2, 22, 177), (156, 100, 106), (21, 35, 42), (13, 8, 121), (142, 92, 28), (45, 118, 33),
          (105, 118, 30), (7, 185, 124), (46, 34, 146), (105, 184, 169), (22, 18, 5), (147, 71, 73), (181, 64, 91),
          (31, 39, 184), (164, 179, 33), (96, 50, 18), (95, 15, 106), (113, 68, 54), (136, 116, 112), (119, 139, 130),
          (31, 139, 34), (66, 6, 127), (62, 39, 2), (49, 99, 180), (49, 119, 155), (153, 50, 183), (125, 38, 3),
          (129, 87, 143), (49, 87, 40), (128, 62, 120), (73, 85, 148), (28, 144, 118), (29, 9, 24), (175, 45, 108),
          (81, 175, 64), (178, 19, 157), (74, 188, 190), (18, 114, 2), (62, 128, 96), (21, 3, 150), (0, 6, 95),
          (2, 20, 184), (122, 37, 185)]

input = 'C:/Users/nguye/OneDrive/Desktop/ai4theblind/VGG_SSD/data/test_img/aa.jpg'
pretrained_model = 'C:/Users/nguye/OneDrive/Desktop/ai4theblind/SSD_ver2/weights/SSD.pth'
nms_threshold = 0.35
cls_threshold  = 0.3

model = SSD(backbone=ResNet())
checkpoint = torch.load(pretrained_model)
model.load_state_dict(checkpoint["model_state_dict"])
if torch.cuda.is_available():
        model.cuda()
model.eval()
dboxes = generate_dboxes()
transformer = SSDTransformer(dboxes, (300, 300), val=True)
cap = cv2.VideoCapture(0)
fps = FPS().start()

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
encoder = Encoder(dboxes)
while True:
    ref,frame = cap.read()
    
    fps.update()
    
    output_frame = np.copy(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = Image.fromarray(frame)
    frame, _, _, _ = transformer(frame, None, torch.zeros(1, 4), torch.zeros(1))

    if torch.cuda.is_available():
        frame = frame.cuda()
    with torch.no_grad():
        ploc, plabel = model(frame.unsqueeze(dim=0))
        result = encoder.decode_batch(ploc, plabel, nms_threshold, 20)[0]
        loc, label, prob = [r.cpu().numpy() for r in result]
        best = np.argwhere(prob > cls_threshold).squeeze(axis=1)
        loc = loc[best]
        label = label[best]
        prob = prob[best]
        if len(loc) > 0:
            loc[:, 0::2] *= width
            loc[:, 1::2] *= height
            loc = loc.astype(np.int32)
            for box, lb, pr in zip(loc, label, prob):
                category = coco_classes[lb]
                color = colors[lb]
                xmin, ymin, xmax, ymax = box
                cv2.rectangle(output_frame, (xmin, ymin), (xmax, ymax), color, 2)
                text_size = cv2.getTextSize(category + " : %.2f" % pr, cv2.FONT_HERSHEY_PLAIN, 1, 1)[0]
                cv2.rectangle(output_frame, (xmin, ymin), (xmin + text_size[0] + 3, ymin + text_size[1] + 4), color,
                                  -1)
                cv2.putText(
                        output_frame, category + " : %.2f" % pr,
                        (xmin, ymin + text_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1,
                        (255, 255, 255), 1)
    cv2.imshow('image',output_frame)
    if cv2.waitKey(1) == ord('q'):
        break

fps.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
