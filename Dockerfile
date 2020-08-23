FROM python:3.8

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD Makefile Pipfile Pipfile.lock /usr/src/app/
COPY . /usr/src/app
RUN make setup
CMD ["python", "-m", "scripts.create_indexes"]