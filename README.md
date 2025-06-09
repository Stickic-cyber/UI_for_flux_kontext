# BFL.AI Flux Kontext Pro 图像生成与编辑工具使用指南

本工具是一个基于 Gradio 框架构建的简易前端应用，它允许您通过 BFL.AI 的 Flux Kontext Pro API 进行文本到图像的生成，或对现有图像进行编辑。

## 1\. 准备工作

在使用本工具之前，您需要完成以下准备工作：

### 1.1 获取 BFL API Key

1.  访问 [bfl.ai](https://bfl.ai) 网站。
2.  根据网站指引注册账号并获取您的 API Key。API Key 通常以 `sk-` 开头。这是您调用 BFL.AI API 的凭证，请务必妥善保管。

### 1.2 运行 Gradio 应用

1.  确保您的电脑已安装 Python，并且安装了 Gradio、Requests 和 Pillow 库。如果未安装，请运行以下命令进行安装：
    ```bash
    pip install gradio requests Pillow
    ```
2.  将您获得的 Gradio 应用代码保存为一个 Python 文件（例如 `app.py`）。
3.  在命令行中导航到 `app.py` 文件所在的目录。
4.  运行命令启动应用：
    ```bash
    python app.py
    ```
5.  如果应用无法正常启动（例如遇到 502 错误），这通常是由于本地端口冲突或网络代理设置问题。您可以尝试修改 `app.py` 文件中 `interface.launch()` 这一行，尝试使用其他启动方式：
      * **使用共享链接 (Share Link)**：这会生成一个临时的公共 URL，可能有助于绕过本地网络问题。
        ```python
        interface.launch(share=True)
        ```
      * **指定其他端口 (Server Port)**：如果默认端口 7860 被占用，可以尝试其他端口，例如 8000。
        ```python
        interface.launch(server_port=8000)
        ```
6.  运行成功后，Gradio 会在命令行中显示一个本地 URL（通常是 `http://127.0.0.1:7860`），您可以在浏览器中打开该 URL 来访问应用界面。

## 2\. 界面概览

Gradio 应用界面简洁直观，主要包含以下几个部分：

  * **Prompt (for Generation or Editing)**：文本输入框，用于描述您希望生成或编辑的图像内容。
  * **Input Image (Optional, for Editing)**：图像上传区域，可选。如果您想编辑现有图像，请在此处上传图片。
  * **BFL API Key**：您的 BFL.AI API Key 输入框（密码类型，输入内容不可见，不会被保存）。
  * **参数设置区域**：包括宽高比、种子、提示词升采样、安全容忍度、输出格式、Webhook URL 和 Webhook Secret 等可调参数。
  * **Generate (生成) 按钮**：点击此按钮开始图像生成或编辑任务。
  * **Generated/Edited Image (生成/编辑后的图像)**：显示最终生成或编辑后的图像。
  * **Status/Message (状态/消息)**：显示任务的当前状态、进度或任何错误信息。

## 3\. 核心功能

本工具支持两种主要功能：

### 3.1 图像生成 (Text-to-Image)

1.  在 **Prompt (提示词)** 文本框中输入您希望生成图像的详细描述。例如：“一只小毛象宠物从猫屋里往外看”。
2.  不要在 **Input Image (输入图像)** 区域上传任何图片。
3.  在 **BFL API Key** 文本框中输入您的 API Key。
4.  根据需要调整其他参数设置（见第 4 节）。
5.  点击 **Generate (生成)** 按钮。
6.  等待片刻，任务状态会在 **Status/Message** 区域显示，最终生成的图像将显示在 **Generated/Edited Image** 区域。

### 3.2 图像编辑 (Image Editing)

1.  在 **Input Image (输入图像)** 区域点击上传框，选择您想要编辑的图片。
2.  在 **Prompt (提示词)** 文本框中输入您希望对图片进行的编辑描述。例如，如果上传了一张猫屋的图片，您可以输入“把猫屋改成狗屋”。
3.  在 **BFL API Key** 文本框中输入您的 API Key。
4.  根据需要调整其他参数设置（见第 4 节）。
5.  点击 **Generate (生成)** 按钮。
6.  等待片刻，任务状态会在 **Status/Message** 区域显示，最终编辑后的图像将显示在 **Generated/Edited Image** 区域。

## 4\. 参数详解

以下是您可以在应用中调整的各项参数及其作用：

  * **`Prompt (for Generation or Editing)`** (string, **必填**)

      * **描述**: 您对期望图像（生成或编辑）的文字描述。
      * **示例**: `"A small furry elephant pet looks out from a cat house"` (生成), `"Change the cat house to a dog house"` (编辑)。

  * **`Input Image (Optional, for Editing)`** (PIL.Image.Image, **可选**)

      * **描述**: 用作编辑参考的输入图像。
      * **使用方式**: 点击上传区域选择您的图片。如果未提供，工具将执行图像生成。

  * **`BFL API Key`** (string, **必填**)

      * **描述**: 您从 BFL.AI 获取的个人 API Key。用于验证您的请求。
      * **注意**: 您的 API Key 不会被应用程序存储。

  * **`Aspect Ratio` (宽高比)** (string, 默认 `"1:1"`)

      * **描述**: 输出图像的期望宽高比（例如，`"16:9"`、`"9:16"`）。所有输出图像的总像素量大约为 1MP。支持从 3:7 到 7:3 的比例。
      * **可选值**: `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"3:7"`, `"7:3"`。

  * **`Seed` (种子)** (integer, 默认 `null`)

      * **描述**: 用于图像生成或编辑的可复现性种子。如果留空或设置为 `null`，则会使用随机种子。
      * **接受值**: 任何整数。

  * **`Prompt Upsampling` (提示词升采样)** (boolean, 默认 `false`)

      * **描述**: 如果选中，将对提示词执行升采样操作，可能会提升生成质量。

  * **`Safety Tolerance` (安全容忍度)** (integer, 默认 `2`)

      * **描述**: 输入和输出的审核级别。
      * **范围**: 0（最严格）到 6（最宽松）。
      * **注意**: 如果您的任务因“Content Moderated”而失败，可以尝试调高此值。

  * **`Output Format` (输出格式)** (string, 默认 `"jpeg"`)

      * **描述**: 输出图像的期望格式。
      * **可选值**: `"jpeg"` 或 `"png"`。

  * **`Webhook URL (Optional)`** (**可选**) (string, 默认 `null`)

      * **描述**: 用于异步任务完成通知的 URL。必须是有效的 HTTP/HTTPS URL。

  * **`Webhook Secret (Optional)`** (**可选**) (string, 默认 `null`)

      * **描述**: 用于 Webhook 签名验证的密钥，将通过 `X-Webhook-Secret` 头发送。

## 5\. 结果与状态

  * **Generated/Edited Image**：当任务成功完成时，您生成的或编辑后的图像将显示在此区域。
  * **Status/Message**：此区域会提供实时的任务状态反馈：
      * `Processing / Queued / Pending`: 任务正在处理中或等待队列中。
      * `Image operation completed successfully!`: 任务成功完成，图像已生成或编辑。
      * `Image operation failed: Content Moderated. Reason(s): [原因]`: 这表示您的提示词或输入图像触发了 BFL.AI 的安全过滤器。您需要修改提示词/图像内容，或尝试将 **Safety Tolerance (安全容忍度)** 参数调高，然后再次尝试。
      * **其他错误消息**：如果出现其他网络错误或 API 返回的意外状态，此区域将显示详细的错误信息，帮助您进行故障排除。

希望这份 README 文档能帮助您更好地使用 BFL.AI Flux Kontext Pro 图像生成与编辑工具！
