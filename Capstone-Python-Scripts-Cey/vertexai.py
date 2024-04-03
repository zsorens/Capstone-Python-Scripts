import dotenv
import os
import vertexai
from vertexai.vision_models import ImageTextModel, Image
# I'd comment this but I didn't make this - ALvin
# See J Sanders
PROJECT_ID = ''
LOCATION = ''

dotenv.load_dotenv()
vertexai.init(project=PROJECT_ID, location=LOCATION)


def get_captions(img_path, num_results=2, language='en'):
    model = ImageTextModel.from_pretrained('imagetext@001')
    src_img = Image.load_from_file(location=img_path)
    captions = model.get_captions(
        # Required
        image=src_img,
        # Optional
        number_of_results=num_results,
        language=language
    )
    return captions


def ask_question(img_path, question, num_results=1):
    model = ImageTextModel.from_pretrained('imagetext@001')
    src_img = Image.load_from_file(location=img_path)
    answers = model.ask_question(
        # Required
        image=src_img,
        question=question,
        # Optional
        number_of_results=num_results
    )
    return answers


def test():
    test_img_dir = 'test/images'
    for filename in os.listdir(test_img_dir):
        test_img_path = os.path.join(test_img_dir, filename)
        # Image 3 - wave cig ad outside of corner store
        #captions = get_captions(test_img_path)
        #print(f'{test_img_path}: Captions generated: "{captions}"')
        answers = ask_question(test_img_path, question='Are there nicotine containing products shown?')
        print(f'{test_img_path}: Answers generated: "{answers}"')
    


    
if __name__ == '__main__':
    test()