from minio import Minio,S3Error
from io import BytesIO
import os
from datetime import timedelta
class MinIoProvider():

        client = None

        def Connect(self):
                print("in connect Func :",os.getenv("MinioAddress"))
                print("in connect Func :",os.getenv("MinioAccessKey"))
                print("in connect Func :",os.getenv("MinioSecretKey"))

                self.client = Minio(os.getenv("MinioAddress"),
                access_key=os.getenv("MinioAccessKey"),
                secret_key=os.getenv("MinioSecretKey"),
                secure =False,#bool(os.getenv("MinioUseSecure")),
                # cert_check = False#bool(os.getenv("MinioCertCheck")),
                )
                try:
                        self.client.set_bucket_policy("tenant", '{}')
                except S3Error as e:
                        print(f"Error setting bucket policy: {e}")

        def Upload_File(self,file):
                # The destination bucket and filename on the MinIO server
                bucket_name = "tenant"
                # destination_file = "my-test-file.txt"
                print(self.client)
                # Make the bucket if it doesn't exist.
                found = self.client.bucket_exists(bucket_name)
                if not found:
                        self.client.make_bucket(bucket_name)
                        print("Created bucket", bucket_name)
                else:
                        print("Bucket", bucket_name, "already exists")

                # Read file content into BytesIO object
                file_data = BytesIO(file.read())

                # Get the content type from the file
                content_type = file.content_type

                # Use put_object to upload the file to MinIO without writing it to a physical location
                self.client.put_object(bucket_name, file.filename, file_data, len(file_data.getvalue()), content_type)

        def GetFileUrl(self,fileName):
                url = self.client.get_presigned_url(bucket_name="tenant",object_name=fileName,method="GET",expires=timedelta(hours=2))
                return url

        
