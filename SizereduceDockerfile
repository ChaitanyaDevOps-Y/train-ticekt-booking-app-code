FROM python:3.12-alpine as parent
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

FROM parent as child
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python","app.py"]
