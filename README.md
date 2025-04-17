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
    conda install pip
    pip install -r requirements.txt
    ```

## Host the webserver

Simply run the following command:

```bash
python index.py
```

Now the website can be viewed at [localhost](http://127.0.0.1:1337).