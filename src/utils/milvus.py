from pymilvus import connections, db
from pymilvus import connections, FieldSchema, CollectionSchema, DataType,utility,Collection
import pandas as pa

import numpy as np
# import cv2
import os
# Connect to Milvus server

class MilvuesClient():
        milvus_connection =None #milvus.Milvus(host='127.0.0.1', port='19530')


        # Check if collection exists, create if it doesn't
        def create_collection_if_not_exists(self,collection_name):
                print('create_collection_if_not_exists => connect:',self.milvus_connection)
                if collection_name not in utility.list_collections():
                        
                        vectorid = FieldSchema(name="vectorId",dtype=DataType.VARCHAR,max_length=64,is_primary=True,)
                        product_id =FieldSchema(name="productId", dtype=DataType.VARCHAR,max_length=64) 
                        image_id =FieldSchema(name="imageId", dtype=DataType.VARCHAR,max_length=64)
                        field_schema = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)
                        schema = CollectionSchema(fields=[vectorid,product_id,image_id,field_schema], description="Collection for storing image features")
                        
                        # self.milvus_connection.create_collection(collection_name, schema)
                        collection = Collection(
                        name=collection_name,
                        schema=schema,
                        using='default',
                        shards_num=2
                        )
                        # collection.cre
                        print(f"Collection '{collection_name}' created successfully.")
                else:
                        print(f"Collection '{collection_name}' already exists.")

        def connect(self) -> 'MilvuesClient':
                print('in connect :',os.getenv('milvusHost'))
                # connections.connect(alias="default",uri=os.getenv('milvusHost'),token="root:Milvus",)
                # connections.connect(alias="default",uri='localhost',token="root:Milvus",)
                connections.connect(uri='tcp://127.0.0.1:19530')
                print('in connect affer:',os.getenv('milvusHost'))
                self.milvus_connection = connections
                self.create_collection_if_not_exists(os.getenv('milvusBucketName'))
                # self.milvus_client = milvus.(host=os.getenv('milvusHost'), port=os.getenv('milvusHostPort'))
                
                return self
        
        # Define a function to insert vectors into Milvus
        def insert_vectors(self,imgId,vectors):
                # status, ids = self.milvus_connection.insert(collection_name=os.getenv('milvusBucketName'), records=vectors)
                collection = Collection(os.getenv('milvusBucketName'))      # Get an existing collection.
                data = [{
                "vectorId": 1,
                "productId": 0,
                "imageId": imgId,
                "vector":[vectors]
                }]
                print(data)
                #load data into a DataFrame object:
                df = pa.DataFrame(data)

                mr = collection.insert(df)
                if mr.OK():
                        print("Vectors inserted successfully!")
                        return mr.primary_keys
                else:
                        print("Failed to insert vectors:", mr.err_index)
                        return None

        # Define a function to perform similarity search
        def search_similar_vectors(self, query_vector, top_k=5):
                status, results = self.milvus_connection.search(collection_name=os.getenv('milvusBucketName'), query_records=query_vector, top_k=top_k)
                if status.OK():
                        print("Similar vectors found:", results)
                else:
                        print("Failed to search similar vectors:", status)

# Example usage:
# Inserting vectors
# image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
# collection_name = 'image_collection'
# vectors = [extract_features(image_path) for image_path in image_paths]
# ids = insert_vectors(collection_name, vectors)

# # Perform similarity search
# query_image_path = 'query_image.jpg'
# query_vector = extract_features(query_image_path)
# search_similar_vectors(collection_name, [query_vector])
