FROM node:20-bullseye

WORKDIR /app

# Install all dependencies including devDependencies
COPY package.json package-lock.json* yarn.lock* .npmrc* ./
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000
ENV PORT=3000

# Run Next.js dev server with hot reload
CMD ["npm", "run", "dev"]
