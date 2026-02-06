import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

class GenderClassifier:
    def __init__(self, weights_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading VGG16 Gender Model on {self.device}...")
        
        # Load pre-trained VGG16
        self.model = models.vgg16(pretrained=True)
        
        # Modify the last layer for Binary Classification (Male/Female)
        num_features = self.model.classifier[6].in_features
        self.model.classifier[6] = nn.Linear(num_features, 2)
        
        if weights_path:
            try:
                self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
                print("Custom weights loaded.")
            except FileNotFoundError:
                print("Weights file not found. Using initialized weights (Accuracy will be low until trained).")
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        self.classes = ['Female', 'Male'] # Assuming 0: Female, 1: Male (Check dataset mapping)

    def predict(self, face_crop):
        """
        Takes a cv2 image (BGR), converts to PIL, preprocesses, and predicts gender.
        """
        if face_crop is None or face_crop.size == 0:
            return "Unknown"

        # Convert CV2 (BGR) to PIL (RGB)
        img = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        
        input_tensor = self.preprocess(pil_img)
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_batch)
            _, predicted_idx = torch.max(output, 1)
            
        return self.classes[predicted_idx.item()]

# Needed because we use cv2 inside predict but forgot to import it above
import cv2
