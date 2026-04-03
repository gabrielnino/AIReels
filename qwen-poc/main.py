from fastapi import FastAPI, HTTPException, Request
from models.request_models import GenerateImageRequest
from service.image_service import generate_images
from utils.logger import get_logger

log = get_logger(__name__)

app = FastAPI(
    title="Qwen Image 2.0 POC",
    description="API to generate images from text and reference images using Alibaba DashScope",
)


@app.post("/generate")
def generate(request: GenerateImageRequest, http_request: Request):
    log.step("POST /generate", "IN",
             prompt_preview=request.prompt[:80],
             n=request.n,
             size=request.size,
             client=http_request.client.host if http_request.client else "unknown")
    try:
        output_images = generate_images(request)
        log.step("POST /generate", "OUT", images_count=len(output_images), paths=output_images)
        return {
            "status": "success",
            "output_images": output_images,
        }
    except Exception as e:
        log.step("POST /generate", "ERR", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
