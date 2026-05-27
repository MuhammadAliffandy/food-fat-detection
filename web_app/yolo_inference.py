import os
import cv2
from ultralytics import YOLO
import fatsecret_api

# Resolve the absolute path to the model relative to this script
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'best.pt')

# Initialize model instance (lazy loading can be used, but global is fine for basic Flask apps)
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load YOLO model from {MODEL_PATH}. Error: {e}")
    model = None

def run_inference(image_path, output_dir):
    """
    Run YOLOv8 inference on a given image.
    
    Args:
        image_path (str): The absolute path to the uploaded image.
        output_dir (str): The directory to save the annotated image.
        
    Returns:
        tuple: (list of detected food class names, path to the annotated image)
    """
    if model is None:
        return [], image_path

    # Run inference with a default confidence threshold (0.25 is standard)
    results = model(image_path, conf=0.25)
    
    detected_classes = []
    
    # Process results (Ultralytics returns a list of Results objects)
    for r in results:
        # Use the raw original image so we can manually draw ONLY the best box, 
        # avoiding the 100-box spam from the broken model.
        annotated_image = r.orig_img.copy()
        
        # 1. Check if it's an Object Detection model (has bounding boxes)
        if r.boxes is not None and len(r.boxes) > 0:
            # Sort boxes by confidence (highest first) and just take the TOP 1
            sorted_boxes = sorted(r.boxes, key=lambda x: x.conf[0].item(), reverse=True)
            top_box = sorted_boxes[0]
            
            class_id = int(top_box.cls[0].item())
            class_name = model.names[class_id]
            conf = top_box.conf[0].item()
            
            detected_classes.append(class_name)
            nutrition_data = fatsecret_api.fetch_nutrition_for_food(class_name)
            
            # Draw the bounding box
            x1, y1, x2, y2 = map(int, top_box.xyxy[0].cpu().numpy())
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
            
            # Draw the Class Label
            label = f"{class_name} ({conf*100:.1f}%)"
            cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            if nutrition_data:
                text = f"{nutrition_data['calories']} kcal | P:{nutrition_data['protein']}g C:{nutrition_data['carbs']}g"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                text_x, text_y = x1, y1 + 25 
                cv2.rectangle(annotated_image, (text_x, text_y - text_height - 5), (text_x + text_width, text_y + baseline - 5), (0, 0, 0), -1)
                cv2.putText(annotated_image, text, (text_x, text_y - 5), font, font_scale, (255, 255, 255), thickness)
                    
        # 2. Check if it's an Image Classification model (has probabilities instead of boxes)
        elif r.probs is not None:
            class_id = r.probs.top1
            class_name = model.names[class_id]
            
            detected_classes.append(class_name)
                
            nutrition_data = fatsecret_api.fetch_nutrition_for_food(class_name)
            
            if nutrition_data:
                text = f"{class_name}: {nutrition_data['calories']} kcal | P:{nutrition_data['protein']}g C:{nutrition_data['carbs']}g"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                thickness = 2
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                
                # Draw at the bottom left to avoid overlapping YOLO's classification text
                h, w, _ = annotated_image.shape
                text_x, text_y = 10, h - 20
                
                cv2.rectangle(annotated_image, (text_x, text_y - text_height - 5), (text_x + text_width, text_y + baseline - 5), (0, 0, 0), -1)
                cv2.putText(annotated_image, text, (text_x, text_y - 5), font, font_scale, (255, 255, 255), thickness)
        
        # Construct output filename
        filename = os.path.basename(image_path)
        output_path = os.path.join(output_dir, f"annotated_{filename}")
        
        # Write to disk
        cv2.imwrite(output_path, annotated_image)
        
        return detected_classes, output_path

    return [], image_path
