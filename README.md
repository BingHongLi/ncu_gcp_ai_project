# GCP帳號申辦與建置GCP Project


# 環境準備

建置 Project

建置 cloud storage

建置 firestore

# 程式碼準備與部署

複製下列網址，並開啟。

https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2FBingHongLi%2Fncu_gcp_ai_project&cloudshell_open_in_editor=README.md&cloudshell_workspace=.

# 指定教材資料夾為工作目錄

# 將訓練好的模型放入 converted_savedmodel資料夾


# 將要回應的json放入line_message_json資料夾


# 構建程式碼

```
gcloud config set project YOUR-PROJECT-ID
gcloud builds submit  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/ncu-bot-dev:0.0.1
```

# 部署

指定環境變數

```
USER_INFO_GS_BUCKET_NAME:  剛剛建立的資料桶子
LINE_CHANNEL_ACCESS_TOKEN: 課程內述說
LINE_CHANNEL_SECRET: 課程內述說
```
# 將生成的網址追加callback 貼回line網站的webhook
