import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import os
from PIL import Image

# Load the pretrained CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def classify_image(image_path):
    # Load the image
    image = Image.open(image_path)

    # Define the text prompts
    prompts = ["An image with a chart or plot", "An image without a chart or plot"]

    # Process the inputs for CLIP
    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)

    # Get the image and text embeddings
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image  # CLIP returns similarity scores between image and text
    probs = logits_per_image.softmax(dim=1)  # Convert to probabilities

    # Display the probabilities
    chart_prob = probs[0][0].item()
    no_chart_prob = probs[0][1].item()
    print(f"Probability of chart/plot: {chart_prob:.2%}")
    # print(f"Probability of no chart/plot: {no_chart_prob:.2%}")

    # Determine the classification
    classification = "Chart/Plot" if chart_prob > 0.3 else "No Chart/Plot"
    return classification

image_uris = [
        os.path.join('D:\MediaWise\output_images/', image_name)
        for image_name in os.listdir('D:\MediaWise\output_images/')
        if image_name.endswith(".png")
    ]

admit=0
for im in image_uris:
    if classify_image(im) == "Chart/Plot":
        admit+=1
    print(classify_image(im), im)
print(admit/len(image_uris))