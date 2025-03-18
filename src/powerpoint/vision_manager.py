import os
import requests

from PIL import Image
from io import BytesIO
from openai import OpenAI

class VisionManager:
    
    def generate_and_save_image(self, prompt: str, output_path: str) -> str:
        """Generate an image using OpenAI DALL-E 3 and save it to the specified path."""

        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        client = OpenAI(api_key=api_key)

        try:
            # Generate the image using DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
        except Exception as e:
            raise ValueError(f"Failed to generate image: {str(e)}")

        image_url = response.data[0].url

        # Download the image
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                raise ValueError(f"Failed to download generated image: HTTP {response.status_code}")
        except requests.RequestException as e:
            raise ValueError(f"Network error downloading image: {str(e)}")

        # Save the image
        try:
            image = Image.open(BytesIO(response.content))
            # Ensure the save directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Save the image
            image.save(output_path)
        except (IOError, OSError) as e:
            raise ValueError(f"Failed to save image to {output_path}: {str(e)}")

        return output_path