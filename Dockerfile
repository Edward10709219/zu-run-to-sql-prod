FROM python:3.8-slim
WORKDIR /ChooWe

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt  ./
RUN pip install -r requirements.txt

# 複製應用程式代碼
COPY . .

# 啟動 Cloud SQL 代理和應用程式
#CMD uvicorn main:app --host 0.0.0.0 --port 8080
CMD uvicorn main:app --host 127.0.0.1 --port 8080
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
