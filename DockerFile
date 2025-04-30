# Use Dart official image
FROM dart:stable

# Set working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN dart pub get

# Set environment variable for the token (Render will provide this)
ENV TOKEN=${TOKEN}

# Start the bot
CMD ["dart", "run"]
