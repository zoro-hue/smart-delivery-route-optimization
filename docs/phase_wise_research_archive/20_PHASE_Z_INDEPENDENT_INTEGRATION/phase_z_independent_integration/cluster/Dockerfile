FROM bitnami/spark:3.5.0

USER root
RUN install_packages python3-pip python3-numpy python3-pandas

COPY spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf

USER 1001

