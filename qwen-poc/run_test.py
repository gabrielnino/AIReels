from utils.run_context import init_run
init_run()  # must be called before any service that uses get_run_dir()

from models.request_models import GenerateImageRequest
from service.image_service import generate_image_urls, download_image
from service.video_service import generate_video

# 1. Image URLs to composite
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
    n=1,  # Only need 1 image for the video test
)

print("1. Generando la imagen (puede tardar un minuto)...")
try:
    # Genera la imagen y devuelve la URL del CDN
    image_urls = generate_image_urls(request_data)
    generated_img_url = image_urls[0]
    print(f"    -> Imagen generada en CDN: {generated_img_url}")
    
    # Descargamos también la imagen resultante
    local_img = download_image(generated_img_url)
    print(f"    -> Imagen descargada localmente en: {local_img}")

    print("\n2. Generando el vídeo a partir de la imagen generada...")
    # Usamos el mismo prompt que sugeriste para la prueba
    video_prompt = """
    A scene of urban fantasy art. A dynamic graffiti art character. The girl from image1, painted with spray paint, comes to life from a concrete wall. She performs a high-energy Spanish rap song at a very fast pace, matching a classic, expressive rapper pose with synchronized lip movement and body gestures.

    The rap lyrics are provided below and must be followed precisely in timing and delivery (approx. 15 seconds):

    [RAP LYRICS]
    Nací en el muro, pintura y presión,
    spray en la mano, latiendo el corazón,
    salgo del concreto, rompo la dimensión,
    ritmo acelerado, pura vibración.

    Luces de la calle, sombra en expansión,
    bajo el puente vibra toda la nación,
    voz como metralla, fuego en la misión,
    cada barra golpea sin compasión.

    Sube la energía, no hay limitación,
    arte callejero en revolución,
    pinto mi destino, firme la visión,
    rap en alta velocidad, pura conexión.

    The scene is set under an urban railway bridge at night. The lighting comes from a single streetlight, creating a cinematic atmosphere with strong contrasts, shadows, and vibrant spray-paint textures. The performance is intense, rhythmic, and visually dynamic.

    The audio of the video must consist entirely of the rap performance based on the provided lyrics, with clear pronunciation, natural flow, and no additional dialogue or background noise.
    """
    
    output_video_path = generate_video(
        img_url=generated_img_url,
        prompt=video_prompt,
        resolution="720P",
        duration=15,
        audio=True
    )
    
    print("\n¡Prueba terminada con éxito! 🎉")
    print(f"Vídeo descargado en: {output_video_path}")
except Exception as e:
    import traceback
    print(f"\nPrueba fallida con la excepción: {e}")
    traceback.print_exc()