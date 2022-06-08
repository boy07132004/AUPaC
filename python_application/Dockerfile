FROM debian:bullseye

RUN apt update \
	&& apt install -y python3 python3-pip build-essential gcc python3-dev cron\
		libxslt-dev libffi-dev libssl-dev cron tzdata \
	&& rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt requirements.txt

RUN python3 -m pip install --no-cache-dir -r requirements.txt

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& echo $TZ > /etc/timezone \
	&& dpkg-reconfigure -f noninteractive tzdata

COPY ./run.sh run.sh
CMD ["./run.sh"]
