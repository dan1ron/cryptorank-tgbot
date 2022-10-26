FROM python
WORKDIR /usr/src/cryptorank/
COPY . ./
RUN pip3 install -r requirements.txt
CMD [ "python3", "main.py" ]