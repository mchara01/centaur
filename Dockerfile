FROM ubuntu:20.04

LABEL name=Centaur
LABEL src="https://github.com/mchara01/thesis_test.git"
LABEL creator="Marcos-Antonios Charalambous"

ENV LANG C.UTF-8

# Install Python and other dependencies
RUN apt-get -y update && apt-get -y install python3.8 python3-pip curl git wget cowsay figlet

# Install Golang by downloading its image
COPY --from=golang:1.17 /usr/local/go/ /usr/local/go/
ENV PATH="/usr/local/go/bin:$PATH"

WORKDIR .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY go-src/go.mod ./
RUN go mod download && go mod verify
COPY . ./centaur


#CMD ["./run_tool.sh"]
CMD ["/bin/bash"]
