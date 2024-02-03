
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
        
        def calc_2_similarity(self,path1,path2):
                img1 = io.imread("images/img1.jpeg",as_gray=False)
                img2 = io.imread("images/img2.jpeg",as_gray=False)

                # Compute the structural similarity index between img1 and img2
                print(img1.size)
                ssmim_score = metrics.structural_similarity(img1,img2,channel_axis=2)
                
                print("SSIM Score: ", ssmim_score)
        
        
        def show_2_pic_similarity(self,path1,path2):
                # Load the two images you want to compare
                image1 = io.imread('img1.jpeg')  # Replace 'image1.jpg' with the actual file path
                image2 = io.imread('img2.jpeg')  # Replace 'image2.jpg' with the actual file path

                # Convert the images to grayscale if they are not already
                # image2_gray = color.rgb2gray(image2)
                # image1_gray = color.rgb2gray(image1)

                # Calculate the Structural Similarity Index (SSI)
                ssi_index, _ = ssim(image1, image2,channel_axis=2, full=True)

                # Print the similarity index
                print(f"Structural Similarity Index: {ssi_index}")
        
        
        def FeattureExtraction(self,filePath):

                if filePath is None or "":
                        return None
                
                if os.path.isfile(filePath)==False:
                        return None 

                # Load two example images
                image1 = color.rgb2gray(io.imread(filePath))
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

        def similarity(self,features1,features2):
                # Calculate Euclidean distance between the feature vectors
                distance = self.euclidean_distances([features1], [features2])[0][0]

                print(f"Euclidean Distance between the two images: {distance}")


        def euclidean_distances(self,vector1, vector2):
                return np.sqrt(np.sum((vector1 - vector2)**2))


















               
