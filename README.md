# Automatic Tournament Layout

Select playing members in a tournament from 6 to 32 players. An automatic tournament will be generated and you can manage the various stages of it. With 9 or more players, the tournament will turn into a two-player team tournament

## Pre-requisites

1. Install [Anaconda](https://www.anaconda.com/docs/getting-started/anaconda/install)

1. Create a fresh `conda` environment and activate it:

    ```bash
    conda create -y --name tournament
    conda activate tournament
    ```
1. Install required packages:

    ```bash
    conda install -y pip
    pip install -r requirements.txt
    ```

1. **(Optional)** If using WLS on Windows, you need to install an extra package to serve the website:

    ```bash
    sudo add-apt-repository -y ppa:wslutilities/wslu
    sudo apt update -y
    sudo apt install -y wslu
    ```

## Host the webserver

Simply run the following command:

```bash
bash serve.sh
```

Now the website can be viewed at [localhost](http://127.0.0.1:1337).