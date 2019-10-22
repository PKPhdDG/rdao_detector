FROM alpine

COPY purize_c.sh /usr/bin

ENTRYPOINT purize_c.sh