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

RUN ./scripts/install-user-deps.sh /app/env

# compile static
RUN . /app/env/bin/activate && \
      ./manage.py collectstatic --noinput && \
      ./manage.py compress -f

# prefer GIT_REV over using git
RUN if test ! -z "$GIT_REV"; then \
  echo "ECS_VERSION=\"$GIT_REV dev\"" > /app/ecs/ecs/version.py; \
  echo "ECS_GIT_REV=\"$GIT_REV\"" >> /app/ecs/ecs/version.py; \
else \
  ECS_VERSION="$(git branch -v | grep '^\*' | sed -re 's/^\* +([a-z0-9,_-]+) +([0-9a-f]+) +(.{,27}).*/\1 \2 \3/g')"; \
  ECS_GIT_REV="$(git rev-parse HEAD)"; \
  if test -z "$ECS_GIT_REV"; then \
      ECS_VERSION='development'; \
      ECS_GIT_REV='badbadbadbadbadbadbadbadbadbadbadbadbad0'; \
  fi; \
  echo "ECS_VERSION=\"$ECS_VERSION\"" > /app/ecs/ecs/version.py; \
  echo "ECS_GIT_REV=\"$ECS_GIT_REV\"" >> /app/ecs/ecs/version.py; \
fi

VOLUME ["/app/ecs-storage-vault"]
EXPOSE 5000
ENTRYPOINT ["/app/ecs/scripts/docker-entrypoint.sh"]
CMD ["web"]
