#!/bin/bash

# Update apt
sudo apt-get update && apt-get install -y

# Install docker
if ! [ -x "$(command -v docker)" ];
then curl -fsSL https://get.docker.com -o get-docker.sh
	sudo sh get-docker.sh
	rm get-docker.sh
else echo "Docker already installed."
sudo usermod -aG docker $USER # give sudo privileges to USER
fi


# Install kubernetes
if ! [ -x "$(command -v kubectl)" ];
then curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
	curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256" # check sum file
	echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
	sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
	kubectl version --client --output=yaml  # test installation
	rm kubectl
	rm kubectl.sha256
else echo "Kubectl already installed."
fi

# Install minikube
if ! [ -x "$(command -v minikube)" ];
then curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	sudo install minikube-linux-amd64 /usr/local/bin/minikube
	rm minikube-linux-amd64
else
	echo "Minikube already installed."
fi
minikube start

# Install k9s
if ! [ -x "$(command -v k9s)" ];
then curl -sS https://webinstall.dev/k9s | bash
else echo "K9s already installed."
fi

# Install python3.10
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install python3.10 -y
OLD_VERSION="$(python3 --version | grep '^Python 3\.')"
echo $OLD_VERSION

# IFS="."
read -ra arr <<< "$OLD_VERSION"
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.${arr[1]} 1 # add old version to alternative list
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2 # add new version
sudo update-alternatives --config python3
sudo ln -s python 3.10 /usr/bin/python3 # update symlink to python3.10
python3 --version

# Install python venv
sudo apt install python3.10-venv -y

# Install MySQL
if ! [ -x "$(command -v mysql)" ]
then sudo apt install mysql-server -y
	sudo apt install mysql-client-core-8.0 -y
else echo "MySQL already installed."
fi

# Install mysqlclient dependencies
sudo apt install python3.10-dev default-libmysqlclient-dev build-essential -y

# Initialize auth service SQL db
cd python/src/auth
sudo mysql -u root < init.sql
