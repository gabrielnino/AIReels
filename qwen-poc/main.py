from fastapi import FastAPI, HTTPException
from models.request_models import GenerateImageRequest
from service.image_service import generate_images

app = FastAPI(title="Qwen Image 2.0 POC", description="API to generate images from text and reference images using Alibaba DashScope")

@app.post("/generate")
def generate(request: GenerateImageRequest):
    try:
        output_images = generate_images(request)
        return {
            "status": "success",
            "output_images": output_images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
