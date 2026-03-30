# Qwen Image 2.0 POC

This is a functional Proof of Concept (POC) backend application that accepts local image references and a text prompt to perform multimodal image generation using the Alibaba DashScope `qwen-image-2.0-pro` model.

The application automatically downloads any generated images back to the `outputs` directory.

## Requirements
- Python 3.10+
- Internet connection (to access DashScope and to fetch public URLs)

## Setup

1. **Clone/Download the repository** to your local machine.
2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   # source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the root directory and ensure your Alibaba DashScope API Key is set correctly:
   ```env
   DASHSCOPE_API_KEY=sk-your-alibaba-api-key
   ```

## Running the API

Start the FastAPI server utilizing `uvicorn`:
```bash
uvicorn main:app --reload
```
The server will now listen at `http://127.0.0.1:8000`.

## Testing the API

You can use `curl` or Postman to test the generation endpoint.
*Note: Make sure the image paths you pass in the `images` array exist on your local filesystem relative to the execution context or as absolute paths.*

**Example Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "images": [
    "C:/temp/input1.jpg",
    "C:/temp/input2.jpg"
  ],
  "prompt": "Create a realistic image using the face from image 1, the clothing from image 2. Maintain natural lighting, sharp details, and professional photography quality.",
  "negative_prompt": "low quality, text, logos",
  "n": 1,
  "size": "1024*1024"
}'
```

**Example Response:**
```json
{
  "status": "success",
  "output_images": [
    "outputs/f4e24ef4-32a2-46cc-9b16-ab10d1a49479.png"
  ]
}
```

## Structure Explanation
* `main.py`: Entrypoint for the webserver using FastAPI.
* `service/image_service.py`: Contains API call to DashScope. Uses `MultiModalConversation` correctly formatted.
* `models/request_models.py`: Input payload Pydantic models with path validation logic.
* `utils/file_utils.py`: Helpers for converting local paths to `file:///` URIs and downlaoding public image urls.
* `outputs/`: Created organically to store any downloaded URLs resulting from the completion.
