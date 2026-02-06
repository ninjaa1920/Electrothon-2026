import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms, datasets
import time
import os

# --- Configuration ---
DATA_DIR = 'dataset' # Folder containing 'train' and 'val' subfolders
MODEL_SAVE_PATH = 'vgg16_gender.pth'
NUM_EPOCHS = 10
BATCH_SIZE = 32

def train_model():
    # 1. Check for GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # 2. Data Transformations (Augmentation)
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.RandomHorizontalFlip(), # Augmentation
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    # 3. Load Data
    try:
        image_datasets = {x: datasets.ImageFolder(os.path.join(DATA_DIR, x), data_transforms[x]) for x in ['train', 'val']}
        dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=BATCH_SIZE, shuffle=True, num_workers=4) for x in ['train', 'val']}
        dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
        class_names = image_datasets['train'].classes
        print(f"Classes found: {class_names}") # Should be ['female', 'male']
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Please ensure your folder structure is: dataset/train/male, dataset/train/female, etc.")
        return

    # 4. Load Pre-trained VGG16
    print("Loading VGG16...")
    model = models.vgg16(pretrained=True)

    # 5. Freeze Layers (Fine-tuning Strategy)
    # We freeze earlier layers so we don't destroy the basic shape recognition
    for param in model.features.parameters():
        param.requires_grad = False

    # 6. Modify Classifier
    num_features = model.classifier[6].in_features
    model.classifier[6] = nn.Linear(num_features, 2) # Change 1000 classes to 2 (Male/Female)
    model = model.to(device)

    # 7. Optimizer & Loss
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.classifier.parameters(), lr=0.001, momentum=0.9)

    # 8. Training Loop
    print("Starting Training...")
    since = time.time()

    for epoch in range(NUM_EPOCHS):
        print(f'Epoch {epoch}/{NUM_EPOCHS - 1}')
        print('-' * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')

    # 9. Save Model
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_model()
