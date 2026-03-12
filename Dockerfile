FROM node:25.8.1-slim AS frontend
COPY ./client /app/client
RUN  cd /app/client &&\
     npm install &&\
     npm run build

FROM python:3.14-slim AS backend
WORKDIR /app
COPY ./pyproject.toml ./uv.lock ./main.py /app/
COPY ./api /app/api
RUN  pip install uv &&\
     uv build --wheel

FROM python:3.14-slim
WORKDIR /app
COPY --from=frontend /app/client/dist /app/client/dist
COPY --from=backend /app/dist/balance_coop-*-py3-none-any.whl /tmp
COPY logo.jpg /app/
RUN  pip install uv &&\
     uv pip install --system /tmp/balance_coop-*-py3-none-any.whl &&\
     rm /tmp/balance_coop-*-py3-none-any.whl
CMD  ["balance-coop"]
