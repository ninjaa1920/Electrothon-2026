import torch
from torchvision import transforms, models
from PIL import Image
import sys
import torch.nn as nn

MODEL_PATH = 'vgg16_gender.pth'

def predict_gender(image_path):
    # 1. Setup Model Architecture (Must match training)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.vgg16(pretrained=False) # No need to download weights, we load our own
    
    # Re-create the classifier head
    num_features = model.classifier[6].in_features
    model.classifier[6] = nn.Linear(num_features, 2)
    
    # 2. Load Weights
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    except FileNotFoundError:
        print(f"Model file not found: {MODEL_PATH}")
        return

    model = model.to(device)
    model.eval()

    # 3. Prepare Image
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    try:
        img = Image.open(image_path)
        img_t = transform(img).unsqueeze(0).to(device)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # 4. Predict
    class_names = ['female', 'male'] # Alphabetical order from ImageFolder
    
    with torch.no_grad():
        outputs = model(img_t)
        _, preds = torch.max(outputs, 1)
        prob = torch.nn.functional.softmax(outputs, dim=1)[0] * 100

    predicted_class = class_names[preds[0]]
    confidence = prob[preds[0]].item()

    print(f"Prediction: {predicted_class.upper()} ({confidence:.2f}%)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_gender.py <path_to_image>")
    else:
        predict_gender(sys.argv[1])
