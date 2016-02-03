FROM ubuntu:wily

ENV HOME /app
ENV LANG en_US.UTF-8
RUN echo -e "LANG=en_US.UTF-8\nLC_MESSAGES=POSIX\nLANGUAGE=en\n" > /etc/default/locale
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales

RUN adduser --disabled-password --gecos ",,," --home "/app" app
COPY . /app/ecs

RUN mkdir -p /app/ecs-storage-vault
RUN chown -R app /app
RUN chmod +x /app/ecs/scripts/*.sh
RUN cd /app/ecs/ && ./scripts/install-os-deps.sh

WORKDIR /app/ecs
USER app

RUN echo 'ECS_VERSION= "'`git branch -v | grep "^\*" | sed -re "s/\* ([a-z._-]+) ([0-9a-f]+) (.{,27}).*/\1 \2 \3 /g"`'"' > /app/ecs/ecs/version.py
RUN ./scripts/install-user-deps.sh /app/env requirements/main.txt requirements/developer.txt requirements/testing.txt

VOLUME ["/app/ecs-storage-vault"]
EXPOSE 5000
ENTRYPOINT ["/app/ecs/scripts/docker-entrypoint.sh"]
CMD ["web"]
