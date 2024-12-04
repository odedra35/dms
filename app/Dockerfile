FROM python
RUN mkdir /docker_dms
RUN chmod 777 /docker_dms
COPY . /docker_dms
WORKDIR /docker_dms
RUN pip install -r requirements.txt --break-system-packeges --ignore-installed
CMD ["python", "routes.py"]