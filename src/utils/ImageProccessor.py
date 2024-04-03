
from skimage import io,metrics
from skimage import io,color
from skimage.metrics import structural_similarity as ssim
from skimage.filters import gabor
from skimage import color, data, filters, io
import numpy as np
import os.path
# from tensorflow.keras.applications import VGG16
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.vgg16 import preprocess_input




class CoreImageAnalyzer:
        ss:str
        def __init__(self) -> None:
                ss=""
               
        def FeattureExtraction(self,file):

                if file is None or "":
                        return None
                
           

                # Load two example images
                image1 = color.rgb2gray(io.imread(file))
                # image2 = color.rgb2gray(io.imread("image2.jpg"))

                # Define Gabor filter parameters
                frequency = 0.6
                theta = 0.8
                sigma_x = 1
                sigma_y = 1

                # Apply the Gabor filter to both images
                features, _ = gabor(image1, frequency=frequency, theta=theta, sigma_x=sigma_x, sigma_y=sigma_y)

                # Reshape the feature matrices to 1D arrays
                features = features.flatten()
                # features2 = features2.flatten()
                return features



        # Define a function to extract features from an image using VGG16 model
        # def extract_features(image_path):
        #         model = VGG16(weights='imagenet', include_top=False)
        #         img = image.load_img(image_path, target_size=(224, 224))
        #         img_data = image.img_to_array(img)
        #         img_data = np.expand_dims(img_data, axis=0)
        #         img_data = preprocess_input(img_data)
        #         features = model.predict(img_data)
        #         flattened_features = features.flatten()
        #         normalized_features = flattened_features / np.linalg.norm(flattened_features)
        #         return normalized_features