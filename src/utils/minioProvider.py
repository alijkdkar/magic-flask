from minio import Minio,S3Error
from io import BytesIO,FileIO
from urllib.parse import urlparse
import os,re
from datetime import timedelta
class MinIoProvider():

        client = None
        bucketName=""

        def Connect(self):
                print("in connect Func :",os.getenv("MinioAddress"))
                print("in connect Func :",os.getenv("MinioAccessKey"))
                print("in connect Func :",os.getenv("MinioSecretKey"))

                self.client = Minio(os.getenv("MinioAddress"),
                access_key=os.getenv("MinioAccessKey"),
                secret_key=os.getenv("MinioSecretKey"),
                secure =False,
                )


                self.bucketName =  os.getenv("MinioBucketName")
                
                self.BucketExist(self.bucketName)
                print("before policy set")
                try:
                        self.client.set_bucket_policy(self.bucketName, '{}')
                except S3Error as e:
                        print(f"Error setting bucket policy: {e}")


        def Upload_File_By_Path(self,filePath):
                try:
                        
                        self.BucketExist(self.bucketName)
                        a = urlparse(str(filePath))
                        imageFileName=os.path.basename(a.path)
                        self.client.fput_object(self.bucketName,imageFileName,file_path=filePath)
                        return True
                except Exception as ex:
                        return False
                




        def BucketExist(self,bucket_name):

                  # Check for valid bucket name pattern
                if not re.match(r'^[a-z0-9.-]{3,63}$', bucket_name):
                        print(f"Error: Invalid bucket name '{bucket_name}'")
                        return
                print(f"in exist bucket{bucket_name}")

                try:
                        found = self.client.bucket_exists(bucket_name)
                        
                        if not found:
                                self.client.make_bucket(bucket_name)
                                print("Created bucket", bucket_name)
                        else:
                                print("Bucket", bucket_name, "already exists")
                except Exception as ex:
                        print(f"exception on bucket checked {ex}")
                print(f"end of exist bucket{bucket_name}")



        def Upload_File(self,file):
                print(f"upload to {self.bucketName}")
                try:
                        self.BucketExist(self.bucketName)
                        file_data = BytesIO(file.read())
                        content_type = file.content_type
                        res=self.client.put_object(self.bucketName, file.filename, file_data, len(file_data.getvalue()), content_type)
                except Exception as ex:
                        return None        
                return res.object_name

        def GetFileUrl(self,fileName):
                url = self.client.get_presigned_url(bucket_name=self.bucketName,object_name=fileName,method="GET",expires=timedelta(hours=2))
                return url

        
