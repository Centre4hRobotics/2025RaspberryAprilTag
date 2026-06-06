#!/bin/bash

topname="$(dirname $0)/.."

help() {
    echo "$(basename "$(dirname $0)/..")" Setup Usage
    echo "--help (-h, -?)     : Open this help menu."
    echo ""
    echo "One of the following must be selected."
    echo "--runtime (default) : Create the environment required for running this software only."
    echo "--testing           : Create the environment required for running unit tests and other testing software only."
    echo "--develop           : Create the environment required for running, testing, and developing this software."
    echo "--clear             : Erases the environment."

}

create_venv() {
    venv_dir="$topname/.venv"
    python3 -m venv --system-site-packages $venv_dir
    echo "Created Python virtual environment at $venv_dir"
}

install_package() {
    $topname/.venv/bin/python3 -m pip install $1
    echo "Installed package $1"
}

install_robotpy() {
    .venv/bin/python3 -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy
    .venv/bin/python3 -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-cscore
    .venv/bin/python3 -m pip install --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2026/simple robotpy-apriltag
}

create_service() {
    sed "s|@location@|$topname|" "$topname/setup/vision.service.template" | sudo tee /etc/systemd/system > /dev/null
    sudo systemctl daemon-reload
    sudo systemctl enable vision.service
    sudo systemctl start vision.service
}

while getopts ":h?-:" opt; do
    case "$opt" in
        h|\?)
            help
            exit 0
            ;;
        -)
            case "$OPTARG" in
                runtime|-runtime)
                    echo "Creating runtime environment!"
                    sudo apt install -y python3-picamera2 --no-install-recommends
                    create_venv
                    install_package opencv-contrib-python-headless
                    install_package matplotlib
                    create_service
                    exit 0
                    ;;
                testing|-testing)
                    echo "Creating testing environment!"
                    create_venv
                    install_package pytest
                    install_package opencv-contrib-python-headless
                    exit 0
                    ;;
                develop|-develop)
                    echo "Creating development environment!"
                    create_venv
                    install_package pytest
                    install_package opencv-contrib-python-headless
                    install_package matplotlib
                    exit 0
                    ;;
                help|-help)
                    help
                    exit 0
                    ;;
                clear|-clear)
                    echo "Erasing the environment!"
                    rm -rf "$topname/.venv/"
                    exit 0
                    ;;
                *)
                    echo "Unknown option --$OPTARG! Run $(basename $0) --help for usage!"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Unknown option $opt! Run $(basename $0) --help for usage!"
            exit 1
            ;;
    esac
done

echo "Creating runtime environment!"
sudo apt install -y python3-picamera2 --no-install-recommends
create_venv
install_package opencv-contrib-python-headless
install_package matplotlib
create_service
