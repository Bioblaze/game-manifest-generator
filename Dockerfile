# Use the latest steamcmd image as the base
FROM python:3.8-slim

# Maintainer information
LABEL maintainer="Randolph William Aarseth II <randolph@divine.games>"
LABEL homepage="https://divine.games/"
LABEL repository="https://github.com/Bioblaze/game-manifest-generator"

# License information
LABEL license="MIT"

# Credits
LABEL credits="This Dockerfile was created by Randolph William Aarseth II, with contributions from the community."

LABEL "com.github.actions.name"="game-manifest-generator"
LABEL "com.github.actions.description"="Generate Manifest Files for proper File downloading"
LABEL "com.github.actions.icon"="loader"
LABEL "com.github.actions.color"="blue"


# Copy the required files into the container
COPY generate_manifest.sh .
COPY manifest_creator.py .

USER root

# For Debian/Ubuntu based containers
RUN apt-get update && \
    apt-get install -y python && \
    rm -rf /var/lib/apt/lists/*

# Make sure your scripts are executable
RUN chmod +x generate_manifest.sh
RUN chmod +x manifest_creator.py

# Set the entrypoint to your deployment script
ENTRYPOINT ["./generate_manifest.sh"]
