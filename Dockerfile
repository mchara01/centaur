# syntax=docker/dockerfile:1

FROM ubuntu:20.04

LABEL name=Centaur
LABEL src="https://github.com/mchara01/centaur.git"
LABEL creator="Marcos-Antonios Charalambous"

ENV LANG C.UTF-8

# Install Python and other dependencies
RUN apt update -y  && apt install -y python3.8 python3-pip git cowsay figlet \
  vim curl unzip zip sudo sqlite3 wget jq cloc \

# Install Golang by downloading its image
COPY --from=golang:1.17 /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:$PATH"

WORKDIR .

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install golang dependencies
COPY go.mod ./
RUN go mod download && go mod verify

# Copy codebase into Centaur directory
COPY . ./centaur

#CMD ["./run_tool.sh"]
CMD ["/bin/bash"]
