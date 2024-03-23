FROM python:3.11-slim-bookworm
ENV USER=sccity
ENV GROUPNAME=$USER
ENV UID=1435
ENV GID=1435
WORKDIR /app
RUN addgroup \
    --gid "$GID" \
    "$GROUPNAME" \
&&  adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --ingroup "$GROUPNAME" \
    --no-create-home \
    --uid "$UID" \
    $USER
RUN apt-get update \
  && apt-get install -y \
    procps \
    nano
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN mkdir logs
RUN chown -R sccity:sccity /app && chmod -R 775 /app
RUN chmod a+x start.sh
USER sccity
CMD ["./start.sh"]