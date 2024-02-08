from google.cloud import vision
#
# Google vision is a service that allws the reading of text from an image
def extract_image_text(image_path):
    """Detects text in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    descriptions = [text.description for text in response.text_annotations]
    return descriptions