#!/bin/bash

echo_red() {
    echo -e "\e[1;31m[$1]\e[0m $2"
}

echo_green() {
    echo -e "\e[1;32m[$1]\e[0m $2"
}

echo_cyan() {
    echo -e "\e[1;34m[$1]\e[0m $2"
}

echo_blue() {
    echo -e "\e[1;36m[$1]\e[0m $2"
}