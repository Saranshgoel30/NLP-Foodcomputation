FROM node:18-alpine

WORKDIR /app

# Build argument for API URL (Next.js needs this at build time)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy application code
COPY app ./app
COPY components ./components
COPY next.config.js tsconfig.json tailwind.config.ts postcss.config.js ./

# Build the Next.js application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
