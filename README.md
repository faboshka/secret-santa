# Secret Santa

The `secret-santa` package is a _Secret Santa_ 🎅🎄 game which randomly assigns and notifies people to whom they should give a gift using _Twilio_'s messaging API.

[![Test Workflow on Main](https://github.com/FawziAS/secret-santa/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/FawziAS/secret-santa/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://github.com/astral-sh/ruff)

<details>
  <summary>Table of Contents</summary>

- [Secret Santa](#secret-santa)
  - [Why?](#why)
    - [But WHY is it over-engineered?](#but-why-is-it-over-engineered)
  - [Usage](#usage)
    - [Prerequisites](#prerequisites)
    - [Configs and Environment Needed](#configs-and-environment-needed)
    - [Installing the Dependencies](#installing-the-dependencies)
    - [Running](#running)
  - [Future Plans](#future-plans)
  - [Contributing](#contributing)
    - [So... How can I contribute?](#so-how-can-i-contribute)
  - [License](#license)
  - [Who](#who)
</details>

## Why?

My friends and I wanted to have a _Secret Santa_ party in our group, but didn't have the time to meet and draw names, so we wrote this code to have it draw the names and send each participant the name of whom he should give a gift to.

### But WHY is it over-engineered?

I was bored. **_Truly bored!_**  
And I know this could be written in one file - with a handful of code lines, but I wanted to try a few things out such as `poetry`, `mkdocs`, `Google style docstrings`, etc.  
=> This is the result.

## Usage

### Prerequisites

To be able to install the project's dependencies, you need to have:

* [_Python_](https://www.python.org/) (>= _3.10.0_)
* [_Poetry_](https://python-poetry.org/) (>= _1.0.0_)
* [_Twilio_](https://www.twilio.com/) account with an active phone number

A few notes:
* This package has not been tested with older version of _python_, but one of the things that would probably break in older version is the use of `|` (for [Union type hinting](https://python.org/dev/peps/pep-0604/)) without importing it from `futures`.
* This package is using `poetry` as its build system, but that could be changed to `pip` by changing the `[build-system]` section to `requires = ["setuptools ~= 58.0", "cython ~= 0.29.0"]` and running the command below from the root of the project:
  ```bash
  python -m pip install .
  ```
  * Source: [`pyproject.toml` page at pip's documentation](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/)
* This code uses an alphanumeric sender ID, i.e. showing the sender as _SecretSanta_, but this isn't supported in every country (please check Twilio 's [Alphanumeric Sender ID for Twilio Programmable SMS](https://support.twilio.com/hc/en-us/articles/223181348-Alphanumeric-Sender-ID-for-Twilio-Programmable-SMS#h_01F4SJZWGMP5RVAJ254VX63A26) before running the code with your configurations.)


### Configs and Environment Needed

To run this package, you need to have:
* The _Twilio_ environment variables set / added to a `.env` file to be passed to the program through the command line with the `--env-path` arguments.
  * The environment variables needed are: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_NUMBER` which could be added to a `.env` file like this:
    ```env
    TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID_HERE"
    TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN_HERE"
    TWILIO_NUMBER="YOUR_TWILIO_NUMBER_HERE"
    ```
    * In case the `--env-path` argument was not provided, the code will try to search for a `.env` file at the project root. **_Please note:_** The code will not throw an error if no environment file has been passed / if the file does not exist, but it will validate the existence of the three environment variables mentioned above (i.e. the environment variables needed could be set from the commandline / on the system beforehand.)
* A list of the participants in a _JSON_ format file, to be passed to the program using the `--participants-path` argument, with each player having a `full_name`, `phone_number`, and optionally a `nickname` as such:
  ```json
  [
    {
      "full_name": "Name 1",
      "phone_number": "+123456789",
      "nickname": "N1"
    },
    {
      "full_name": "Name 2",
      "phone_number": "+987654321"
    },
    ...
  ]
  ```
  * In case the `--participants-path` argument was not provided, the code will try to look for a `participants.json` file at the project root.
  * The file needs to have at least three participants.
  * The code will **_NOT_** check for same numbers. (this may be added later)
  * The code will determine two players' data the same if they have their three fields are the same.

### Installing the Dependencies

To install the dependencies with poetry installed, all you need to do is run:

```bash
poetry install
```

### Running

To run the _Secret Santa_ package / module, all you need to do after setting it up is run:

```bash
python secret_santa
```

with the appropriate arguments.

To see all the supported command-line arguments, run `python secret_santa --help`.

<details>
  <summary>The command-line arguments supported</summary>
  
  ```console
  ❯ python secret_santa --help
   ____                     _      ____              _
  / ___|  ___  ___ _ __ ___| |_   / ___|  __ _ _ __ | |_ __ _
  \___ \ / _ \/ __| '__/ _ \ __|  \___ \ / _` | '_ \| __/ _` |
   ___) |  __/ (__| | |  __/ |_    ___) | (_| | | | | || (_| |
  |____/ \___|\___|_|  \___|\__|  |____/ \__,_|_| |_|\__\__,_|
  
  
  usage: secret_santa [-h] [--env-path ENV_PATH] [--participants-path PARTICIPANTS_PATH] [--show-arrangement] [--dry-run] [-log {critical,error,warn,warning,info,debug}]
  
  Welcome to the Secret Santa Organizer, in which each participant gets one other participant assigned, to whom he should bring a gift!
  
  options:
    -h, --help            show this help message and exit
    --env-path ENV_PATH   path to the .env file containing the required secrets
                          If omitted - will try to load the "{project_root}/.env".
                          --> Note: No error will be raised in case --env-path is not provided and no "{project_root}/.env" exists.
    --participants-path PARTICIPANTS_PATH
                          path to the "Secret Santa" participants JSON
                          If omitted - will try to load "{project_root}/participants.json".
    --show-arrangement    show the final arrangement (participant -> receiver)
                          --> Note: The --show-arrangement is shown as logged INFO, which means setting the logger any higher will not show the arrangements as expected.
                          --> Personal Request: Please keep it fun and use this only for development-testing purposes / if you're a non-participating admin.
    --dry-run             run the program without actually sending the message
    -log {critical,error,warn,warning,info,debug}, --logging-level {critical,error,warn,warning,info,debug}
                          set the main logging level of the program loggers (Defaults to "info")
  
  Merry Christmas! and have lots of fun :)
```
</details>

**_Note:_** The program could alternatively be run as a module:

```bash
python -m secret_santa
```

## Future Plans

I can think of some things to add, such as:

* Additional command-line arguments, including but not limited to:
  * `--check-participants` to validate no two participants are the same (by phone number)
  * `--custom-message` to allow for customizing the message to be sent to the user's liking.
* Wait for some time, check the _message status_ if it was still queued, and resend it in case it failed to send / wasn't delivered.
* Allow for more messaging methods other than Twilio (including but not limited to: Email messaging, another SMS service, etc.)
* ~~Add unit / functional testing.~~ Done :)

If ever comes a time in which I'll be in a similar state to the one I was in writing this code, I may add these, but I don't see myself doing a lot with this package in the near future, however, if you like it and would like to add something, feel free to contribute.

## Contributing

You could contribute code to the repository in many ways:

1. _Bug Reports_: If you encounter a bug running the code, feel free to submit an issue.
2. _Bug Fixes_: If there's a bug you encountered and would like to fix, or saw an issue you could fix, you're more than welcome fix it.
3. _Feature Code_: If there's a feature that is , and you would like to code, you're also welcome.
    * In case you want to add a new feature, it would be advisable to raise the feature in an issue to be discussed beforehand.
4. _Optimization_: If you see an opportunity to improve the code and decide to code it, I want to thank you for making the code better.

### So... How can I contribute?

1. Fork it.
2. Create your feature branch, running the command `git checkout -b my-new-feature`.
3. Make sure the tests pass as expected, and add some tests covering your changes.
4. Document all functions and methods by the [`Google style docstrings`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
5. Commit your changes, `git commit -m "Added some feature"`.
6. Push to the branch `git push origin my-new-feature`.
7. Create a new Pull Request, merging from your `my-new-feature` to the `main` branch with a descriptive description of the changes made.

## License

In the spirit of Christmas, I decided publish this code under the [Unlicense License](./LICENSE), to whomever may find it useful / want to use it (if someone ever will 😊.)

---

## Who

The `secret-santa` project was originally developed by [Fawzi Abo Shkara](https://github.com/faboshka/).
