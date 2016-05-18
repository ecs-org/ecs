FROM ubuntu:xenial

# locale setup
ENV LANG en_US.UTF-8
RUN printf %b "LANG=en_US.UTF-8\nLANGUAGE=en_US:en\nLC_MESSAGES=POSIX\n" > /etc/default/locale
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales

# create user+home, copy source, chown, chmod
ENV HOME /app
RUN adduser --disabled-password --gecos ",,," --home "/app" app
COPY . /app/ecs
RUN chown -R app:app /app
RUN chmod +x /app/ecs/scripts/*.sh

# symlink entrypoints
RUN for a in docker-entrypoint.sh start; do \
      ln -s /app/ecs/scripts/docker-entrypoint.sh /$a; \
    done

# install system dependencies, do not upgrade packages
RUN cd /app/ecs; ./scripts/install-os-deps.sh --no-upgrade

# create supervisord conf files
RUN prefix=/app/ecs/conf/supervisord.conf; \
    scdir=/app/ecs/conf/supervisor.conf.d; \
    cat $prefix $scdir/web.conf > $HOME/supervisord-web.conf; \
    cat $prefix $scdir/web.conf $scdir/celery.conf $scdir/smtpd.conf > $HOME/supervisord-combined.conf

# configure nginx
RUN ln -sf /app/ecs/conf/nginx.conf /etc/nginx/nginx.conf && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# install user dependencies
WORKDIR /app/ecs
USER app
RUN ./scripts/install-user-deps.sh /app/env
RUN ./scripts/create-dirs.sh /app

# compile/compress/collect/create translations, javascript, static files
RUN . /app/env/bin/activate; \
    ./manage.py compilemessages && \
    ./manage.py collectstatic --noinput && \
    ./manage.py compress -f

# create version.py file but do not abort if not successful
RUN ./scripts/create-version-file.sh /app/ecs /app/ecs/ecs/version.py || true

VOLUME ["/app/ecs-storage-vault"]
EXPOSE 5000

USER root
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["simple"]
