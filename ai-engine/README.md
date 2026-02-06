# Women Safety Analytics - AI Engine

## 🏗️ Folder Structure
```
ai-engine/
├── dataset/               # <--- YOU NEED TO CREATE THIS
│   ├── train/
│   │   ├── male/          # Put 100+ images of men here
│   │   └── female/        # Put 100+ images of women here
│   └── val/
│       ├── male/          # Put 20 images of men here
│       └── female/        # Put 20 images of women here
├── modules/
│   ├── gender.py          # Uses the trained model
│   ├── risk.py
│   └── sos.py
├── main.py
├── requirements.txt
└── train_gender.py        # <--- RUN THIS TO TRAIN
```

## 🚀 How to Train VGG16 (Steps)

1.  **Prepare Data**:
    *   Create the `dataset/` folder structure shown above.
    *   Download a Gender dataset (e.g., from Kaggle "Gender Classification Dataset").
    *   Copy images into the folders.

2.  **Run Training**:
    ```bash
    python train_gender.py
    ```
    *   This will run for 10 epochs (rounds).
    *   It will produce a file: `vgg16_gender.pth`.

3.  **Use It**:
    *   Once `vgg16_gender.pth` exists, `main.py` will automatically use it for accurate detection.

## 🛠️ Modules

### 1. Person Detection (YOLOv8)
... (Rest of the readme)
