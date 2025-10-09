FROM node:20-bullseye AS builder
WORKDIR /app

COPY package.json package-lock.json* yarn.lock* .npmrc* ./
RUN npm ci
COPY . .
RUN npm run build
