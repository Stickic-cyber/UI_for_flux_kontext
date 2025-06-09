import gradio as gr
import os
import requests
import base64
from PIL import Image
from io import BytesIO
import time

# This function handles the entire image generation or editing process,
# from sending the initial request to polling for the result.
def generate_image(
    prompt: str,
    input_image: Image.Image, # Added input_image parameter
    api_key: str,
    aspect_ratio: str = "1:1",
    seed: int = None,
    prompt_upsampling: bool = False,
    safety_tolerance: int = 2,
    output_format: str = "jpeg",
    webhook_url: str = None,
    webhook_secret: str = None
):
    """
    Generates or edits an image using the BFL.AI Flux Kontext Pro API based on a given prompt,
    an optional input image, and additional parameters.

    Args:
        prompt (str): The text description for the image to be generated or the edit to be applied.
        input_image (PIL.Image.Image or None): The image to be edited. If None, it's a text-to-image generation.
        api_key (str): Your BFL.AI API key.
        aspect_ratio (str): Desired aspect ratio (e.g., “16:9”). Default "1:1".
        seed (int): Seed for reproducibility. If None, a random seed is used.
        prompt_upsampling (bool): If true, performs upsampling on the prompt. Default False.
        safety_tolerance (int): Moderation level for inputs and outputs. Value ranges from 0 to 6. Default 2.
        output_format (str): Desired format of the output image. Can be “jpeg” or “png”. Default "jpeg".
        webhook_url (str): URL for asynchronous completion notification.
        webhook_secret (str): Secret for webhook signature verification.

    Returns:
        tuple: A tuple containing:
            - PIL.Image.Image or None: The generated/edited image if successful, None otherwise.
            - str: A status message indicating success, processing status, or an error.
    """
    # Validate the API key
    if not api_key:
        return None, "Please provide your BFL API Key to proceed."

    # Set the API key as an environment variable for the requests
    os.environ["BFL_API_KEY"] = api_key

    # Construct the JSON payload for the API request
    payload = {
        'prompt': prompt,
    }

    # Handle input_image if provided (for image editing)
    if input_image:
        buffered = BytesIO()
        # Determine the format to save the input image based on the desired output format
        # If output_format is not 'jpeg' or 'png', default to 'JPEG' for saving input image
        img_save_format = output_format.upper() if output_format in ["jpeg", "png"] else "JPEG"
        try:
            # Ensure the image is in RGB mode before saving as JPEG (no alpha channel)
            # If input_image has an alpha channel (RGBA) and we're saving as JPEG, convert it to RGB
            if img_save_format == "JPEG" and input_image.mode == "RGBA":
                input_image = input_image.convert("RGB")
            input_image.save(buffered, format=img_save_format)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            payload['input_image'] = img_str
        except Exception as e:
            return None, f"Error encoding input image: {e}"
    else:
        # If no input image is provided, ensure a prompt is given for text-to-image generation
        if not prompt:
            return None, "Please provide a prompt for image generation (or an input image for editing)."


    # Add optional parameters if they are provided and valid
    if aspect_ratio:
        payload['aspect_ratio'] = aspect_ratio
    if seed is not None: # Use is not None to allow 0 as a valid seed
        payload['seed'] = seed
    if prompt_upsampling: # Only add if true, as default is false
        payload['prompt_upsampling'] = prompt_upsampling
    # Safety tolerance is always included due to default, but check range
    if 0 <= safety_tolerance <= 6:
        payload['safety_tolerance'] = safety_tolerance
    else:
        return None, "Safety tolerance must be between 0 and 6."
    if output_format in ["jpeg", "png"]:
        payload['output_format'] = output_format
    if webhook_url:
        payload['webhook_url'] = webhook_url
    if webhook_secret:
        payload['webhook_secret'] = webhook_secret

    # --- Part 1: Send the initial image generation/editing request ---
    try:
        # Make a POST request to the image generation endpoint
        response = requests.post(
            'https://api.bfl.ai/v1/flux-kontext-pro',
            headers={
                'accept': 'application/json',
                'x-key': os.environ.get("BFL_API_KEY"), # Use the API key from environment
                'Content-Type': 'application/json',
            },
            json=payload, # Use the dynamically constructed payload
        ).json()

        # Extract the request ID from the response
        request_id = response.get("id")
        if not request_id:
            # If no request ID is returned, something went wrong
            return None, f"Failed to initiate image operation. API response: {response.get('detail', 'No ID returned')}"
    except requests.exceptions.RequestException as e:
        # Handle network-related errors during the initial request
        return None, f"Network error during initial request: {e}"
    except Exception as e:
        # Handle any other unexpected errors
        return None, f"An unexpected error occurred during initial request: {e}"

    # --- Part 2: Poll for the image generation/editing result ---
    while True:
        # Wait for a short period before polling again to avoid overwhelming the API
        time.sleep(1.5)
        try:
            # Make a GET request to retrieve the result using the request ID
            result = requests.get(
                'https://api.bfl.ai/v1/get_result',
                headers={
                    'accept': 'application/json',
                    'x-key': os.environ.get("BFL_API_KEY"), # Use the API key from environment
                },
                params={'id': request_id}, # Use the obtained request ID
            ).json()

            status = result.get("status")
            # Print status to the console for debugging purposes
            print(f"Polling Status: {status}")

            if status == "Ready":
                # If the status is 'Ready', the image is available as a URL
                image_url = result.get('result', {}).get('sample')
                if image_url:
                    try:
                        # Fetch the image from the URL
                        print(f"Fetching image from URL: {image_url}") # Debug print
                        image_response = requests.get(image_url)
                        image_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                        # Read the raw image bytes from the response content
                        image_data = image_response.content
                        print(f"Received image data length from URL: {len(image_data)}") # Debug print

                        if len(image_data) == 0:
                            return None, "Fetched image data is empty from URL. Please check the URL or API response."

                        # Open the image using Pillow from the byte stream
                        image = Image.open(BytesIO(image_data))
                        return image, "Image operation completed successfully!"
                    except requests.exceptions.RequestException as e:
                        return None, f"Error fetching image from URL: {e}. Please check the URL or network connectivity."
                    except Exception as e:
                        return None, f"Error opening image data from URL: {e}. The fetched data might not be a valid image."
                else:
                    return None, "Image result URL missing from API response (sample is empty or None)."
            elif status == "Content Moderated":
                # Explicitly handle content moderation error
                details = result.get('details', {})
                moderation_reasons = details.get('Moderation Reasons', ['Unknown reason'])
                return None, f"Image operation failed: Content Moderated. Reason(s): {', '.join(moderation_reasons)}. Please try a different prompt or adjust Safety Tolerance."
            elif status not in ["Processing", "Queued", "Pending"]:
                # If the status is not 'Processing', 'Queued', 'Pending', 'Ready', or 'Content Moderated', it's an error
                return None, f"An error or unexpected status occurred: {result.get('detail', 'Unknown error')}. Full response: {result}"
            # If status is "Processing", "Queued", or "Pending", the loop continues to poll
        except requests.exceptions.RequestException as e:
            # Handle network-related errors during polling
            return None, f"Network error during polling for result: {e}"
        except Exception as e:
            # Handle any other unexpected errors during polling
            return None, f"An unexpected error occurred during polling: {e}"

# --- Gradio Interface Definition ---
# Create the Gradio interface
interface = gr.Interface(
    fn=generate_image, # The Python function to call when the interface is submitted
    inputs=[
        # Textbox for the prompt
        gr.Textbox(
            label="Prompt (for Generation or Editing)",
            placeholder="A small furry elephant pet looks out from a cat house OR Change the cat house to a dog house",
            info="Describe the image you want to generate, or the edit you want to apply to the input image."
        ),
        # Image input for editing (optional)
        gr.Image(
            label="Input Image (Optional, for Editing)",
            type="pil", # Return PIL Image object
            interactive=True, # Allow drawing/editing and uploads
            width=256, # Set a default width for the input image display
            height=256, # Set a default height for the input image display
        ),
        # Textbox for the BFL API Key, with type="password" for security
        gr.Textbox(
            label="BFL API Key",
            type="password",
            placeholder="Enter your BFL API Key here (e.g., 'sk-xxxx...')",
            info="Your API key from bfl.ai. This is not stored."
        ),
        # Dropdown for aspect_ratio
        gr.Dropdown(
            label="Aspect Ratio",
            choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:7", "7:3"],
            value="1:1",
            info="Desired aspect ratio for the output image. All outputs are ~1MP total."
        ),
        # Number input for seed
        gr.Number(
            label="Seed",
            value=None,
            step=1,
            info="Seed for reproducibility. Leave blank for a random seed."
        ),
        # Checkbox for prompt_upsampling
        gr.Checkbox(
            label="Prompt Upsampling",
            value=False,
            info="If checked, performs upsampling on the prompt."
        ),
        # Slider for safety_tolerance
        gr.Slider(
            label="Safety Tolerance",
            minimum=0,
            maximum=6,
            step=1,
            value=2,
            info="Moderation level for inputs and outputs (0: most strict, 6: most permissive)."
        ),
        # Dropdown for output_format
        gr.Dropdown(
            label="Output Format",
            choices=["jpeg", "png"],
            value="jpeg",
            info="Desired format of the output image."
        ),
        # Textbox for webhook_url
        gr.Textbox(
            label="Webhook URL (Optional)",
            placeholder="Enter URL for asynchronous completion notification",
            info="Must be a valid HTTP/HTTPS URL."
        ),
        # Textbox for webhook_secret
        gr.Textbox(
            label="Webhook Secret (Optional)",
            type="password",
            placeholder="Enter secret for webhook signature verification",
            info="Secret for webhook signature verification, sent in the X-Webhook-Secret header."
        )
    ],
    outputs=[
        # Image component to display the generated/edited image
        gr.Image(label="Generated/Edited Image", type="pil"),
        # Textbox to display status messages (e.g., "Processing", "Ready", "Error")
        gr.Textbox(label="Status/Message")
    ],
    # Set the title of the Gradio app
    title="BFL.AI Flux Kontext Pro Image Generator & Editor",
    # Provide a description for the app
    description=(
        "Enter a text prompt to generate a new image, or upload an image and provide a prompt to edit it, "
        "using BFL.AI's Flux Kontext Pro model. You will need a BFL API Key from bfl.ai to use this application."
    ),
    # Disable the flagging feature common in Gradio demos
    flagging_mode="never",
    # Add an article section for more detailed instructions or context
    article=(
        "## How to use this app:\n"
        "1. **Get your BFL API Key:** Visit [bfl.ai](https://bfl.ai/) to obtain your API key. "
        "It usually starts with `sk-`.\n"
        "2. **Enter a Prompt:** Type a descriptive sentence for the image you wish to create (e.g., 'A futuristic city at sunset with flying cars'), "
        "OR describe the edit you want to apply to an uploaded image (e.g., 'Make the dog a cat').\n"
        "3. **Upload an Input Image (Optional):** To edit an image, click the upload box and select your image. "
        "If no image is uploaded, the app will generate a new image based on your prompt.\n"
        "4. **Enter your API Key:** Paste your BFL API Key into the designated field.\n"
        "5. **Adjust Parameters:** Modify the aspect ratio, seed, upsampling, safety tolerance, "
        "output format, and optionally webhook details.\n"
        "6. **Click Generate:** The app will send your request to BFL.AI and then poll for the result. "
        "This might take a few seconds or a minute depending on the load.\n"
        "7. **View Result:** Once the image is ready, it will appear in the 'Generated/Edited Image' box.\n\n"
        "This application demonstrates calling a REST API that returns a base64-encoded image for both generation and editing."
    )
)

# To run this Gradio application, uncomment the line below and execute the script:
# If you encounter issues with the app not starting (e.g., 502 error),
# try one of these alternatives:
# 1. Use a shared link (good for bypassing local network/firewall issues):
# interface.launch(share=True)
# 2. Try a different port if port 7860 is already in use:
# interface.launch(server_port=8000) # You can try other ports like 8001, 8888, etc.
interface.launch()
