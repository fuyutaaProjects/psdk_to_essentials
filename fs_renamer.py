import os

# renames files to fs_[name in lowercase].png

directory = os.getcwd() + '/fs/'
for f in os.listdir(directory):
    os.rename(os.path.join(directory, f),
                os.path.join(directory, f"{'fs'}_{f.lower()}"))