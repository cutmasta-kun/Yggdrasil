from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

def load_model():
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-stage1')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-stage1')
    return processor, model

def process_data(image_path, processor, model):
    image = Image.open(image_path).convert('RGB')
    pixel_values = processor(images=image, return_tensors='pt').pixel_values
    generated_ids = model.generate(pixel_values)
    response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

image_path = 'image.png'

# Load the model and processor
processor, model = load_model()

# Process the data
response = process_data(image_path, processor, model)

print(response)