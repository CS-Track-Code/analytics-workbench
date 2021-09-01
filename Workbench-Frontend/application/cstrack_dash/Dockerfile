FROM python:3.9

RUN mkdir -p /home/project/dash
WORKDIR /home/project/dash
COPY requirements.txt /home/project/dash
RUN pip install Cython
RUN pip install cmake
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt
EXPOSE 6123

COPY . /home/project/dash
CMD ["bash"]

