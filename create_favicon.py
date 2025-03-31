from PIL import Image
import os

# Create a favicon from the Minto logo
input_path = 'static/images/minto-disability-logo.png'
output_path = 'static/images/favicon.ico'

# Open the logo image
img = Image.open(input_path)

# Resize to appropriate favicon size
favicon = img.resize((32, 32))

# Save as ICO
favicon.save(output_path)

print(f"Favicon created at {output_path}")