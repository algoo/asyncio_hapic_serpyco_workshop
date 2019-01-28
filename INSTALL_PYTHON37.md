# Install python 3.7 on debian like system

    sudo apt update
    sudo apt install build-essential wget
    sudo apt install libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev
    sudo apt install libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev

    cd /tmp
    wget https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tgz
    tar xvf Python-3.7.1.tgz
    cd Python-3.7.1
    ./configure --enable-optimizations
    make -j8
    sudo make altinstall
