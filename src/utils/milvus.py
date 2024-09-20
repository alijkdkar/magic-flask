from pymilvus import connections, db
from pymilvus import connections, FieldSchema, CollectionSchema, DataType,utility,Collection
from pymilvus import MilvusClient
import pandas as pa

import numpy as np
# import cv2
import os
# Connect to Milvus server

class MyMilvuesClient():
        milvus_connection = None #milvus.Milvus(host='127.0.0.1', port='19530')
        MilvusClient = None

        # Check if collection exists, create if it doesn't
        def create_collection_if_not_exists(self,collection_name):
                print('create_collection_if_not_exists => connect:',self.milvus_connection)
                if collection_name in utility.list_collections():
                        print(f"Collection '{collection_name}' already exists.")
                        # self.drop_collection(collection_name)
                else:
                        vectorid = FieldSchema(name="vectorId",dtype=DataType.VARCHAR,max_length=64,is_primary=True,)
                        product_id =FieldSchema(name="productId", dtype=DataType.VARCHAR,max_length=64) 
                        product_url = FieldSchema(name="productUrl",dtype=DataType.VARCHAR,max_length=2000)
                        image_id =FieldSchema(name="imageId", dtype=DataType.VARCHAR,max_length=64)
                        field_schema = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128) # image feature vector
                        schema = CollectionSchema(fields=[vectorid,product_id,image_id,field_schema,product_url], description="Collection for storing image features")
                                
                                # self.milvus_connection.create_collection(collection_name, schema)
                        collection = Collection(
                                name=collection_name,
                                schema=schema,
                                using='default',
                                shards_num=2
                                )
                                # collection.cre


                        if not collection.has_index():  # Check if an index exists
                                print(f"Creating index on collection '{collection_name}'...")
                                index_params = {
                                        "index_type": "IVF_FLAT",  # Example index type; you can choose based on your needs
                                        "metric_type": "L2",       # Distance metric for vectors (L2 for Euclidean distance)
                                        "params": {"nlist": 128}
                                }
                                collection.create_index(field_name="vector", index_params=index_params)
                                print(f"Index created for collection '{collection_name}'.")
                        else:
                                print(f"Index already exists for collection '{collection_name}'.")
                                print(f"Collection '{collection_name}' created successfully.")
                

        def drop_collection(self, collection_name):
                print(f"Dropping collection '{collection_name}'")
                collection = Collection(collection_name)
                collection.drop()
                print(f"Collection '{collection_name}' dropped successfully.")


        def connect(self) -> 'MyMilvuesClient':
                print('in connect :',os.getenv('milvusHost'))
                # connections.connect(alias="default",uri=os.getenv('milvusHost'),token="root:Milvus",)
                # connections.connect(alias="default",uri='localhost',token="root:Milvus",)
                connections.connect(uri='tcp://127.0.0.1:19530')
                print('in connect affer:',os.getenv('milvusHost'))
                self.milvus_connection = connections
                self.create_collection_if_not_exists(os.getenv('milvusBucketName'))

                # self.GetAllIndexed()
                self.MilvusClient = MilvusClient(uri="http://localhost:19530") ##host=os.getenv('milvusHost'), port=os.getenv('milvusHostPort'))
                
                return self
        
        # Define a function to insert vectors into Milvus
        def insert_vectors(self,imgId,vectors):
               
                collection = Collection(os.getenv('milvusBucketName'))

                print('feature size :',vectors.shape)
                data = [{
                "vectorId": imgId,
                "productId": '0',
                "imageId": imgId,
                "vector":vectors[:128], #todo : must to make 128 dim for feature in feature extraction 
                "productUrl" : "http://google.com"
                }]
                print(data)
                #load data into a DataFrame object:
                df = pa.DataFrame(data)

                mr = collection.insert(df)
                print(mr)
                if mr.succ_count>0:
                        print("Vectors inserted successfully!"+(str(mr.primary_keys)))
                        return mr.primary_keys
                else:
                        print("Failed to insert vectors:", mr.err_index)
                        return None

        # Define a function to perform similarity search
        def search_similar_vectors(self, query_vector, top_k=5):
                # status, results = self.MilvusClient.search(collection_name=os.getenv('milvusBucketName'), data=[query_vector], top_k=top_k,search_params={"params":{}})
                # if status.OK():
                #         print("Similar vectors found:", results)
                # else:
                #         print("Failed to search similar vectors:", status)
                # search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                try:
                        results = self.MilvusClient.search(
                        collection_name=os.getenv('milvusBucketName'),
                        data=[query_vector[:128]],
                        # anns_field='vector',  # Replace with the name of your vector field
                        # filter=None,
                        # param=search_params,
                        limit=top_k
                        ,output_fields=["vectorId","vector"]
                        )
                        print("Similar vectors found:", results)
                except Exception as e:
                        print("Failed to search similar vectors:", e)



        def GetAllIndexed(self):
                collection_name = os.getenv('milvusBucketName')
                
                print("get all index")
                # Check if the collection exists before proceeding
                if collection_name not in utility.list_collections():
                        print(f"Collection '{collection_name}' does not exist.")
                        return None
                
                # Load the collection
                collection = Collection(collection_name)
                
                if collection.has_index:
                        print(f"Collection '{collection_name}' has an index.")
                
                # Check if the collection is empty
                if collection.is_empty:
                        print(f"Collection '{collection_name}' is empty.")
                        # return None
                
                
                if self.MilvusClient is None:
                        print("client is none")

                # Load data into memory for querying
                collection.load()

                # Perform a simple query to retrieve all data
                expr = "vectorId != ''"  # Example expression to match all records

                # result = self.milvus_client.get(collection_name=collection_name,expr=expr, output_fields=["vectorId", "productId", "imageId", "vector"])
                result= self.MilvusClient.get(collection_name=collection_name,ids=['73bcc25b-021f-4be8-a8ac-41faa12097a6.jpeg'])
                print("Ssss")
                print(result)
                print("zzzzz")
                if result is not None:
                        print(f"Retrieved {len(result)} records from the collection.")
                        return result
                else:
                        print(f"No records found in collection '{collection_name}'.")
                        return None

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
