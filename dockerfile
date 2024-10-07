FROM python:3.9-slim

WORKDIR ./app

COPY . .

RUN chmod a+x worker.sh

RUN pip3 install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6000
EXPOSE 7000

CMD ["./worker.sh", "--host=0.0.0.0"]
