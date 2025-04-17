# Automatic Tournament Layout

Select playing members in a tournament from 6 to 32 players. An automatic tournament will be generated and you can manage the various stages of it. With 9 or more players, the tournament will turn into a two-player team tournament

## Host the webserver

1. Install `npm` from the [official website](https://nodejs.org/en/download). At the moment, you can do it on Ubuntu like this:

    ```bash
    # Download and install nvm:
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

    # in lieu of restarting the shell
    \. "$HOME/.nvm/nvm.sh"

    # Download and install Node.js:
    nvm install 22

    # Verify the Node.js version:
    node -v # Should print "v22.14.0".
    nvm current # Should print "v22.14.0".

    # Verify npm version:
    npm -v # Should print "10.9.2".
    ```

1. Run the following command:

    ```bash
    bash serve.sh
    ```

    Now the website can be viewed at [localhost](http://127.0.0.1:1337)