import os
import logging
import aiohttp
import asyncio

from PIL import Image
from io import BytesIO
from openai import AsyncOpenAI

logger = logging.getLogger('vision_manager')

class VisionManager:

    async def generate_and_save_image(self, prompt: str, output_path: str) -> str:
        """
        Generate an image using OpenAI DALL-E 3 and save it to the specified path.
        
        Args:
            prompt: Text description of the image to generate
            output_path: Path where the generated image should be saved
            
        Returns:
            The path to the saved image
            
        Raises:
            ValueError: If API key is missing or any step in the process fails
        """
        logger.info(f"Generating image for prompt: '{prompt[:50]}...' (truncated)")
        
        # Validate API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        # Create AsyncOpenAI client
        client = AsyncOpenAI(api_key=api_key)

        try:
            # Generate the image using DALL-E 3
            logger.debug("Sending request to OpenAI API")
            response = await client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3"
            )
            
            image_url = response.data[0].url
            logger.debug(f"Image generated successfully, URL received")
            
        except Exception as e:
            logger.error(f"Failed to generate image: {str(e)}")
            raise ValueError(f"Failed to generate image: {str(e)}")

        # Download the image asynchronously
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Downloading image from URL")
                async with session.get(image_url) as response:
                    if response.status != 200:
                        error_msg = f"Failed to download generated image: HTTP {response.status}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    
                    image_data = await response.read()
                    logger.debug(f"Image downloaded successfully: {len(image_data)} bytes")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error downloading image: {str(e)}")
            raise ValueError(f"Network error downloading image: {str(e)}")

        # Save the image
        try:
            # Ensure the save directory exists
            directory = os.path.dirname(output_path)
            if directory:
                logger.debug(f"Creating directory if needed: {directory}")
                os.makedirs(directory, exist_ok=True)
                
            # Process and save the image
            logger.debug(f"Processing and saving image to: {output_path}")
            image = Image.open(BytesIO(image_data))
            image.save(output_path)
            logger.info(f"Image successfully saved to: {output_path}")
            
        except OSError as e:
            logger.error(f"Failed to create directory or save image: {str(e)}")
            raise ValueError(f"Failed to save image to {output_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error saving image: {str(e)}")
            raise ValueError(f"Error processing image: {str(e)}")

        return output_path
