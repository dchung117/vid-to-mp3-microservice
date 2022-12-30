#!/bin/bash

# Update apt
sudo apt update
sudo apt upgrade

# Install docker
if ! [ -x "$(command -v docker)" ];
then curl -fsSL https://get.docker.com -o get-docker.sh
	sudo sh get-docker.sh
	sudo usermod -aG docker $USER && newgrp docker # give sudo privileges to USER
	rm get-docker.sh
else echo "Docker already installed."
fi

# Install kubernetes
if ! [ -x "$(command -v kubectl)" ];
then curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
	curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256" # check sum file
	echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
	sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
	kubectl version --client --output=yaml  # test installation
else echo "Kubectl already installed."
fi

# Install minikube
if ! [ -x "$(command -v minikube)" ];
then curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
	sudo install minikube-linux-amd64 /usr/local/bin/minikube
else
	echo "Minikube already installed."
fi

# Install k9s
if ! [ -x "$(command -v k9s)" ];
then curl -sS https://webinstall.dev/k9s | bash
else echo "K9s already installed."
fi

# Install python3.10
sudo apt install python3.10
#OLD_VERSION="$(python3 --version | grep '^Python 3\.')"
#echo $OLD_VERSION

#IFS="."
#read -ra arr <<< "$OLD_VERSION"
#sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.${arr[1]} 1 # add old version to alternative list
#sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2 # add new version
#sudo update-alternatives --config python3
#sudo rm /usr/bin/python3 # remove old symlink
#sudo ln -s python 3.10 /usr/bin/python3 # update symlink to python3.10
python3 --version
# Install MySQL
if ! [ -x "$(command -v mysql)" ]
then sudo snap install mysql-shell
else echo "MySQL already installed."
fi
