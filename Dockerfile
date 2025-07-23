FROM python:3.12-slim

COPY dist/taggivm-0.0.1-py3-none-any.whl /taggivm/
WORKDIR /taggivm

# RUN apt-get -y update && apt-get install -y sqlite3

RUN pip install taggivm-0.0.1-py3-none-any.whl

CMD ["bash"]
# ENTRYPOINT ["bash"]
# ENTRYPOINT ["taggivm"]
# CMD ["scan"]