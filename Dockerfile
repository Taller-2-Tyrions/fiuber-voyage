FROM node:16
RUN mkdir /opt/app
WORKDIR /opt/app
COPY app.js package.json package-lock.json ./
RUN npm install
ENTRYPOINT [ "node", "app.js" ]
# Exponer el puerto 3010
EXPOSE 3010
