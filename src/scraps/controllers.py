from flask import request, jsonify,abort
import uuid,os,json
import http
import urllib.request
from html.parser import HTMLParser
import re,ssl
import base64
import base64
import pandas as pd
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image
from ..utils.ImageProccessor import CoreImageAnalyzer
from ..utils.milvus import MyMilvuesClient
from ..utils.milvus import MyMilvuesClient
from src.utils.minioProvider import MinIoProvider
milvus=MyMilvuesClient().connect()
minio = MinIoProvider()
import requests as rq
import ssl


minio.Connect()
ssl_context = ssl._create_unverified_context()
ssl._create_default_https_context = ssl._create_unverified_context
class MyHmtlParser(HTMLParser):
        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                return super().handle_starttag(tag, attrs)
        def handle_data(self, data: str) -> None:

                return super().handle_data(data)
        def handle_endtag(self, tag: str) -> None:
                return super().handle_endtag(tag)





def StartScrap(url):
        print(f"in handler {url}")
        with urllib.request.urlopen(b"https://api.digikala.com/v1/categories/headphone/search/?attributes%5B2352%5D%5B0%5D=21576&attributes%5B2352%5D%5B1%5D=31584&attributes%5B2352%5D%5B2%5D=21577&sort=21&types%5B0%5D=127&page=2".decode(),context=ssl_context) as response:
                
                htmlContent = response.read().decode('utf-8')  # Decode bytes to string
                # print(htmlContent)

        data = json.loads(htmlContent)


        print(type(data['data']["products"]))

        for x in data['data']["products"]:
                print(">>>>>"+str(x["id"]))
                scrapDetailPage(str(x["id"]))


        # Saving the HTML content to a file
        with open("output.json", "w", encoding="utf-8") as file:
                file.write(htmlContent)

        return ""



def scrapDetailPage(proId):
        """get images with title sesc and images to index that"""
        with urllib.request.urlopen(("https://api.digikala.com/v2/product/"+proId+"/"),context=ssl_context) as response:
                
                detailPage = response.read().decode('utf-8')  # Decode bytes to string
                with open(f"outputDeatil{proId}.json", "w", encoding="utf-8") as file:
                        file.write(detailPage)

        data = json.loads(detailPage)

        product = data['data']["product"]
        # print(product)
        title = product["title_fa"]
        pageUrl = f"https://www.digikala.com/product/dkp-{proId}/"
        print(pageUrl)
        images = product["images"]
        for x in images["list"]:
                imageUrl=x["url"][0]
                a = urlparse(str(imageUrl))
                imageFileName=os.path.basename(a.path)
                localFileAddress = "scraps/images/"+imageFileName
                
                local_file, headers = urllib.request.urlretrieve(url=imageUrl, filename=localFileAddress)
                print(f"Image downloaded: {local_file}")
                
                if minio.Upload_File_By_Path(localFileAddress):
                        print(f"Image uploaded to MinIO: {localFileAddress}")
                        feature = CoreImageAnalyzer().FeattureExtraction(localFileAddress)
                        ids = milvus.insert_vectors(imageFileName,feature,proId,pageUrl)
                        if ids is None:
                                print("not indexed ")
                        else:
                                print(f"{ids}indexed")


                      



def save_base64_as_jpeg(base64_string, output_filename):
    # Remove the `data:image/webp;base64,` prefix if it's there
    base64_string = base64_string.split(",")[1]
    
    # Decode the Base64 string
    image_data = base64.b64decode(base64_string)

    # Open the image with Pillow (PIL) and convert it to a format we can work with
    image = Image.open(BytesIO(image_data))

    # Convert to RGB mode because JPEG doesn't support transparency
    rgb_image = image.convert('RGB')

    # Save the image as JPEG
    rgb_image.save(output_filename, format="JPEG")
