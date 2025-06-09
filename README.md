# BFL.AI Flux Kontext Pro Image Generation and Editing Tool User Guide

This tool is a simple front-end application built on the Gradio framework. It allows you to generate images from text or edit existing images using the BFL.AI Flux Kontext Pro API.

-----

## 1\. Preparation

Before using this tool, you need to complete the following preparations:

### 1.1 Obtain a BFL API Key

1.  Visit the [bfl.ai](https://bfl.ai) website.
2.  Follow the website's instructions to register an account and obtain your **API Key**. This is your credential for calling the BFL.AI API, so please keep it secure.

### 1.2 Run the Gradio Application

1.  Ensure that Python is installed on your computer, along with the Gradio, Requests, and Pillow libraries. If they are not installed, run the following command to install them:
    ```bash
    pip install gradio requests Pillow
    ```
2.  Save the Gradio application code you obtained as a Python file (e.g., `app.py`).
3.  Navigate to the directory where the `app.py` file is located in your command line.
4.  Run the command to start the application:
    ```bash
    python app.py
    ```
5.  If the application fails to start normally (e.g., encountering a 502 error), this is usually due to a local port conflict or network proxy settings. You can try modifying the `interface.launch()` line in your `app.py` file to use other startup methods:
      * **Use a Shared Link**: This generates a temporary public URL, which may help bypass local network issues.
        ```python
        interface.launch(share=True)
        ```
      * **Specify a Different Port (Server Port)**: If the default port 7860 is occupied, you can try another port, such as 8000.
        ```python
        interface.launch(server_port=8000)
        ```
6.  After a successful run, Gradio will display a local URL in the command line (usually `http://127.0.0.1:7860`). You can open this URL in your browser to access the application interface.

-----

## 2\. Interface Overview

The Gradio application interface is simple and intuitive, mainly consisting of the following sections:

  * **Prompt (for Generation or Editing)**: A text input box used to describe the image content you wish to generate or edit.
  * **Input Image (Optional, for Editing)**: An image upload area, optional. If you want to edit an existing image, upload it here.
  * **BFL API Key**: Your BFL.AI **API Key** input box (password type, input content is not visible and will not be saved).
  * **Parameter Settings Area**: Includes adjustable parameters such as **Aspect Ratio**, **Seed**, **Prompt Upsampling**, **Safety Tolerance**, **Output Format**, **Webhook URL**, and **Webhook Secret**.
  * **Generate button**: Click this button to start the image generation or editing task.
  * **Generated/Edited Image**: Displays the final generated or edited image.
  * **Status/Message**: Displays the current status, progress, or any error messages for the task.

-----

## 3\. Core Features

This tool supports two main functions:

### 3.1 Image Generation (Text-to-Image)

1.  Enter a detailed description of the image you wish to generate in the **Prompt** text box. For example: "A small furry elephant pet looks out from a cat house."
2.  Do not upload any images in the **Input Image** area.
3.  Enter your **API Key** in the **BFL API Key** text box.
4.  Adjust other parameter settings as needed (see Section 4).
5.  Click the **Generate** button.
6.  Wait a moment; the task status will be displayed in the **Status/Message** area, and the final generated image will appear in the **Generated/Edited Image** area.

### 3.2 Image Editing

1.  In the **Input Image** area, click the upload box and select the picture you want to edit.
2.  Enter the description of the edits you want to make to the image in the **Prompt** text box. For example, if you uploaded an image of a cat house, you could enter "Change the cat house to a dog house."
3.  Enter your **API Key** in the **BFL API Key** text box.
4.  Adjust other parameter settings as needed (see Section 4).
5.  Click the **Generate** button.
6.  Wait a moment; the task status will be displayed in the **Status/Message** area, and the final edited image will appear in the **Generated/Edited Image** area.

-----

## 4\. Parameter Details

Below are the parameters you can adjust in the application and their functions:

  * **`Prompt (for Generation or Editing)`** (string, **required**)

      * **Description**: Your text description of the desired image (generated or edited).
      * **Examples**: `"A small furry elephant pet looks out from a cat house"` (generation), `"Change the cat house to a dog house"` (editing).

  * **`Input Image (Optional, for Editing)`** (PIL.Image.Image, **optional**)

      * **Description**: The input image used as a reference for editing.
      * **Usage**: Click the upload area to select your image. If not provided, the tool will perform image generation.

  * **`BFL API Key`** (string, **required**)

      * **Description**: Your personal **API Key** obtained from BFL.AI. Used to authenticate your requests.
      * **Note**: Your **API Key** will not be stored by the application.

  * **`Aspect Ratio`** (string, default `"1:1"`)

      * **Description**: The desired **aspect ratio** for the output image (e.g., `"16:9"`, `"9:16"`). The total pixel count of all output images is approximately 1MP. Ratios from 3:7 to 7:3 are supported.
      * **Accepted values**: `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"3:7"`, `"7:3"`.

  * **`Seed`** (integer, default `null`)

      * **Description**: A reproducible **seed** for image generation or editing. If left blank or set to `null`, a random seed will be used.
      * **Accepted values**: Any integer.

  * **`Prompt Upsampling`** (boolean, default `false`)

      * **Description**: If checked, the prompt will undergo an **upsampling** operation, which may improve generation quality.

  * **`Safety Tolerance`** (integer, default `2`)

      * **Description**: The moderation level for input and output.
      * **Range**: 0 (most strict) to 6 (most lenient).
      * **Note**: If your task fails due to "Content Moderated," you can try increasing this value.

  * **`Output Format`** (string, default `"jpeg"`)

      * **Description**: The desired **format** for the output image.
      * **Accepted values**: `"jpeg"` or `"png"`.

  * **`Webhook URL (Optional)`** (string, default `null`)

      * **Description**: A **URL** for asynchronous task completion notifications. Must be a valid HTTP/HTTPS URL.

  * **`Webhook Secret (Optional)`** (string, default `null`)

      * **Description**: A **secret key** for Webhook signature verification, sent via the `X-Webhook-Secret` header.

-----

## 5\. Results and Status

  * **Generated/Edited Image**: When the task is successfully completed, your generated or edited image will be displayed in this area.
  * **Status/Message**: This area will provide real-time task status feedback:
      * `Processing / Queued / Pending`: The task is being processed or waiting in the queue.
      * `Image operation completed successfully!`: The task completed successfully, and the image has been generated or edited.
      * `Image operation failed: Content Moderated. Reason(s): [Reason]`: This indicates that your prompt or input image triggered BFL.AI's safety filters. You need to modify the prompt/image content, or try increasing the **Safety Tolerance** parameter, and then try again.
      * **Other error messages**: If other network errors or unexpected statuses are returned by the API, this area will display detailed error messages to help you troubleshoot.

We hope this README document helps you better use the BFL.AI Flux Kontext Pro image generation and editing tool\!
