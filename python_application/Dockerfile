FROM debian:10.3-slim

RUN apt update \
	&& apt install -y python3 python3-pip build-essential gcc python3-dev python3-numpy python3-pandas \
		libxslt-dev libffi-dev libssl-dev cron tzdata \
	&& rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt \
	&& pip3 install pyzmq \
	&& pip3 install ipywidgets==7.6.5

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& echo $TZ > /etc/timezone \
	&& dpkg-reconfigure -f noninteractive tzdata

COPY ./run.sh run.sh
CMD ["./run.sh"]
