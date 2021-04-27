'''

用戶上傳照片時，將照片從Line取回，放入CloudStorage

瀏覽用戶目前擁有多少張照片（未）

'''

from models.user import User
from flask import Request
from linebot import (
    LineBotApi
)

import os
from daos.user_dao import UserDAO
from linebot.models import (
    TextSendMessage
)


# 圖片下載與上傳專用
import urllib.request
from google.cloud import storage

# 圖像辨識
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import time

import os

from utils.reply_send_message import detect_json_array_to_new_message_array

model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')

class ImageService:
    line_bot_api = LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    '''
    用戶上傳照片
    將照片取回
    將照片存入CloudStorage內
    '''
    @classmethod
    def line_user_upload_image(cls,event):

        # 取出照片
        image_blob = cls.line_bot_api.get_message_content(event.message.id)
        temp_file_path=f"""{event.message.id}.png"""

        #
        with open(temp_file_path, 'wb') as fd:
            for chunk in image_blob.iter_content():
                fd.write(chunk)

        # 上傳至bucket
        storage_client = storage.Client()
        bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
        destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)



        # 載入模型Label
        '''
        載入類別列表
        '''
        class_dict = {}
        with open('converted_savedmodel/labels.txt') as f:
            for line in f:
                (key, val) = line.split()
                class_dict[int(key)] = val

        # 載入模型
        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        # model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')
        
        # 圖片預測
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(temp_file_path)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0 - 1 )

        # Load the image into the array
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0]= normalized_image_array[0:224,0:224,0:3]

        # run the inference
        prediction = model.predict(data)
        
        # 取得預測值
        max_probability_item_index = np.argmax(prediction[0])

        
        # 將預測值拿去尋找line_message
        # 並依照該line_message，進行消息回覆
        if prediction.max() > 0.6:
            result_message_array = detect_json_array_to_new_message_array("line_message_json/"+class_dict.get(max_probability_item_index)+".json")
            cls.line_bot_api.reply_message(
                event.reply_token,
                result_message_array
            )
        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"""圖片無法辨認，圖片已上傳，請期待未來的AI服務！""")
            )
            
        # 移除本地檔案
        os.remove(temp_file_path)

        # 回覆消息
        # cls.line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(f"""圖片已上傳，請期待未來的AI服務！""")
        # )