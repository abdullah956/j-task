# Use Node 18 alpine base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Install serve to serve the built application
RUN npm install -g serve

# Expose port 5173
EXPOSE 5173

# Command to serve the application
CMD ["serve", "-s", "dist", "-l", "5173"]
