# Dockerfile

FROM --platform=linux/amd64 python:3.12.2-slim


ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN apt-get update && apt-get install -y wget gnupg2 curl unzip

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# Install Node.js and npm
#RUN apt-get install -y curl \
    #&& curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    #&& apt-get install -y nodejs

RUN apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs





# Install axe-core
RUN npm install axe-core
#####

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit secrets file
COPY .streamlit/secrets.toml /root/.streamlit/secrets.toml

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME World

###
ENV DOCKER_ENV true
####

# Run streamlit.py when the container launches
CMD ["streamlit", "run", "web_accessibility_checker.py"]
