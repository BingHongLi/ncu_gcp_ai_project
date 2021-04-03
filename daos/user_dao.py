'''
負責與db溝通
save_user(user:User) :新增資料時，若有重複資料，則採更新
get_user(user_id:str):取用資料，開放以user_id的方式尋找
'''

from models.user import User
from google.cloud import firestore


class UserDAO:
    # 建立客戶端
    db = firestore.Client()
    users_ref = db.collection(u'users')

    # 新增資料時，若有重複資料，則採更新
    @classmethod
    def save_user(cls, user: User) -> None:
        # print(user)

        # 查找用戶資料
        user_ref = cls.users_ref.document(user.line_user_id)
        user_doc = user_ref.get()

        # 檢查用戶資料是否存在
        if user_doc.exists:
            # 更新
            user_ref.set(document_data=user.to_dict(), merge=True)
            # print(u'has already update')
        else:
            # 直接插入
            cls.users_ref.add(document_data=user.to_dict(), document_id=user.line_user_id)
            # print(u'No such document!')
        return user.to_dict()

    # 取用資料，開放以user_id的方式尋找
    @classmethod
    def get_user(cls, user_id: str) -> User:

        # 設定要查找的資料
        user_ref = cls.users_ref.document(user_id)

        # 查找資料
        user_doc = user_ref.get()

        # 若資料存在
        if user_doc.exists:
            user = User.from_dict(user_doc.to_dict())
            # print(f'Document data: {user_doc.to_dict()}')
        else:
            pass
            # print(u'No such document!')

        return user