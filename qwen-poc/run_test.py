from models.request_models import GenerateImageRequest
from service.image_service import generate_images

# Use public image URLs (Alibaba documentation sample images)
# This avoids needing to upload local files and matches the working reference implementation
test_images = [
    "https://thumbs.dreamstime.com/b/slim-teen-girl-blue-dress-white-background-girl-blue-dress-128302673.jpg",
    "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/iclsnx/input2.png",
    "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250925/gborgw/input3.png",
]

# Create the request
request_data = GenerateImageRequest(
    images=test_images,
    prompt="Make the girl from Image 1 wear the black dress from Image 2 and sit in the pose from Image 3.",
    negative_prompt="",
    n=2,
)

# Call the generation function directly
print("Calling generate_images (this may take a minute)...")
try:
    output_paths = generate_images(request_data)
    print("Test successful!")
    print(f"Output image paths: {output_paths}")
except Exception as e:
    import traceback
    print(f"Test failed with exception: {e}")
    traceback.print_exc()