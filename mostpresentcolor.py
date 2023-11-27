from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def most_dominant_color(image_path, num_colors=1):
    # Open the image using Pillow (PIL)
    image = Image.open(image_path)

    # Convert the image to RGB mode to ensure consistency
    image = image.convert("RGB")

    # Convert the image data to a NumPy array
    image_data = np.array(image)

    # Reshape the image data to be a list of RGB values
    pixels = image_data.reshape(-1, 3)

    # Use K-Means clustering to find the dominant color(s)
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)

    # Get the RGB values of the dominant color(s)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # If num_colors is set to 1, return a single RGB tuple
    if num_colors == 1:
        return tuple(dominant_colors[0])

    # If num_colors is greater than 1, return a list of RGB tuples
    return [tuple(color) for color in dominant_colors]

# Example usage:
if __name__ == "__main__":
    image_path = "./fs/fs_chlorofyte.png"
    dominant_color = most_dominant_color(image_path)
    
    # If you want the top N dominant colors, change num_colors parameter
    # dominant_colors = most_dominant_color(image_path, num_colors=3)
    
    print("Dominant color(s) (RGB):", dominant_color)
