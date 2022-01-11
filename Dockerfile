FROM python:3.10-alpine AS build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-alpine
WORKDIR /src
COPY --from=build /root/.local /root/.local
COPY . /src
CMD python main.py