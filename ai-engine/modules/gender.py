import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import os

class GenderClassifier:
    def __init__(self, weights_path="vgg16_gender.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading VGG16 Gender Model on {self.device}...")
        
        # Load VGG16 architecture (no need for ImageNet weights since we have our own)
        self.model = models.vgg16(pretrained=False)
        
        # Modify the last layer for Binary Classification (Male/Female)
        num_features = self.model.classifier[6].in_features
        self.model.classifier[6] = nn.Linear(num_features, 2)
        
        if os.path.exists(weights_path):
            try:
                self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
                print(f"✅ Model weights loaded from {weights_path}")
            except Exception as e:
                print(f"❌ Error loading weights: {e}")
        else:
            print(f"⚠️ Warning: Weights file '{weights_path}' not found! Model will output random guesses.")
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        self.classes = ['Female', 'Male'] # 0: Female, 1: Male

    def predict(self, face_crop):
        """
        Takes a cv2 image (BGR), converts to PIL, preprocesses, and predicts gender.
        """
        if face_crop is None or face_crop.size == 0:
            return "Unknown", 0.0

        # Convert CV2 (BGR) to PIL (RGB)
        try:
            img = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            
            input_tensor = self.preprocess(pil_img)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(input_batch)
                probabilities = torch.nn.functional.softmax(output, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)
                
            predicted_label = self.classes[predicted_idx.item()]
            return predicted_label, confidence.item()
            
        except Exception as e:
            print(f"Prediction Error: {e}")
            return "Unknown", 0.0
