
from skimage import io,metrics
from skimage import io,color
from skimage.metrics import structural_similarity as ssim
from skimage.filters import gabor
from skimage import color, data, filters, io
import numpy as np
import os.path



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

