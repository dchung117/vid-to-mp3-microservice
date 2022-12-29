#!/bin/bash

# Update apt
sudo apt update

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

# todo: install/upgrade python to 3.10, install mysql
