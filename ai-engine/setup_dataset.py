import os
import shutil
import random

# --- CONFIGURATION ---
# REPLACE THIS with the path where you unzipped the Kaggle dataset
# Example: "C:/Users/BIT/Downloads/gender-classification-dataset"
SOURCE_DATASET_PATH = r"C:/Users/BIT/Downloads/archive (1)" 

DEST_DIR = "dataset"
NUM_IMAGES_TO_COPY = 500  # Number of images to copy per category (Male/Female)
# ---------------------

def copy_images(src_folder, dest_folder, count):
    if not os.path.exists(src_folder):
        print(f"Error: Source folder not found: {src_folder}")
        return

    os.makedirs(dest_folder, exist_ok=True)
    
    files = [f for f in os.listdir(src_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if len(files) == 0:
        print(f"No images found in {src_folder}")
        return

    # Shuffle to get a random sample
    random.shuffle(files)
    selected_files = files[:count]

    print(f"Copying {len(selected_files)} images from {src_folder} to {dest_folder}...")
    
    for f in selected_files:
        shutil.copy2(os.path.join(src_folder, f), os.path.join(dest_folder, f))

def main():
    print(f"--- Setting up subset of dataset ({NUM_IMAGES_TO_COPY} images per class) ---")
    
    # Define paths based on standard Kaggle structure
    # Expected: Source/Training/male, Source/Training/female
    
    src_train_male = os.path.join(SOURCE_DATASET_PATH, "Training", "male")
    src_train_female = os.path.join(SOURCE_DATASET_PATH, "Training", "female")
    
    # We will use a smaller split for validation from the original Validation folder
    src_val_male = os.path.join(SOURCE_DATASET_PATH, "Validation", "male")
    src_val_female = os.path.join(SOURCE_DATASET_PATH, "Validation", "female")

    # Destinations
    dest_train_male = os.path.join(DEST_DIR, "train", "male")
    dest_train_female = os.path.join(DEST_DIR, "train", "female")
    dest_val_male = os.path.join(DEST_DIR, "val", "male")
    dest_val_female = os.path.join(DEST_DIR, "val", "female")

    # Copy Training Data
    copy_images(src_train_male, dest_train_male, NUM_IMAGES_TO_COPY)
    copy_images(src_train_female, dest_train_female, NUM_IMAGES_TO_COPY)

    # Copy Validation Data (use 20% of training size)
    val_count = int(NUM_IMAGES_TO_COPY * 0.2)
    copy_images(src_val_male, dest_val_male, val_count)
    copy_images(src_val_female, dest_val_female, val_count)

    print("\nDone! Dataset is ready.")
    print(f"You can now run 'python train_gender.py'.")

if __name__ == "__main__":
    main()
