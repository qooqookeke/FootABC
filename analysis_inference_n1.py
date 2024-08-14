import os
import cv2
import torch
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog
from detectron2 import model_zoo
from detectron2.config import get_cfg

def setup_cfg(config_file, weights_path, num_classes, keypoint_num=None):
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(config_file))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.WEIGHTS = weights_path
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
    if keypoint_num:
        cfg.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = keypoint_num
    cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    return cfg

seg_weights_path = "models/seg_model_final.pth"
kp_weights_path = "models/key_model_final.pth"

seg_cfg = setup_cfg("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml", seg_weights_path, num_classes=3)
kp_cfg = setup_cfg("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml", kp_weights_path, num_classes=1, keypoint_num=14)

seg_metadata = MetadataCatalog.get("my_dataset_train")
seg_metadata.thing_classes = ["forefoot", "midfoot", "hindfoot"]

keypoint_names = ["MM", "MMT", "AW", "1MTB", "1MTH", "1DPS", "1DPT", "1DPI", "SB", "FB", "CT", "AI", "CPFI", "CAT"]
kp_metadata = MetadataCatalog.get("keypoints_train")
kp_metadata.keypoint_names = keypoint_names
kp_metadata.keypoint_flip_map = []


custom_colors = {
    "forefoot": (1.0, 0.75, 0.8), 
    "midfoot": (0.75, 1.0, 0.75),  
    "hindfoot": (0.75, 0.9, 1.0)  
}

seg_predictor = DefaultPredictor(seg_cfg)
kp_predictor = DefaultPredictor(kp_cfg)


def draw_combined_predictions(image, seg_outputs, kp_outputs):
    v = Visualizer(image[:, :, ::-1], seg_metadata, instance_mode=ColorMode.IMAGE)
    seg_instances = seg_outputs["instances"].to("cpu")
    kp_instances = kp_outputs["instances"].to("cpu")

    assigned_colors = [custom_colors[seg_metadata.thing_classes[i]] for i in seg_instances.pred_classes]
    out = v.overlay_instances(masks=seg_instances.pred_masks, assigned_colors=assigned_colors, labels=[seg_metadata.thing_classes[i] for i in seg_instances.pred_classes])
    vis_output_img = out.get_image()[:, :, ::-1].copy()

    keypoints = kp_instances.pred_keypoints

    for kp in keypoints:
        valid_keypoints = [(int(x), int(y)) for (x, y, prob) in kp if prob > 0.5]

        for i in range(len(valid_keypoints)):
            for j in range(i + 1, len(valid_keypoints)):
                cv2.line(vis_output_img, valid_keypoints[i], valid_keypoints[j], (255, 0, 0), 2)

        for i, (x, y, prob) in enumerate(kp):
            if prob > 0.5:
                cv2.circle(vis_output_img, (int(x), int(y)), 8, (0, 255, 0), -1)
                cv2.putText(vis_output_img, keypoint_names[i], (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2)

    return vis_output_img




def predict_and_save(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image_name in os.listdir(input_folder):
        image_path = os.path.join(input_folder, image_name)
        img = cv2.imread(image_path)

        if img is None:
            print(f"Skip {image_path}")
            continue

        seg_outputs = seg_predictor(img)
        kp_outputs = kp_predictor(img)

        combined_img = draw_combined_predictions(img, seg_outputs, kp_outputs)

        result_image_path = os.path.join(output_folder, image_name)
        cv2.imwrite(result_image_path, combined_img)

        print(f"Predicted image saved to {result_image_path}")

input_folder = "test_images/dr_test/"
output_folder = "test_images/dr_result/"

predict_and_save(input_folder, output_folder)