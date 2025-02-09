# SSH Honeypot

A modular, graphic-based honeypot to capture ip addresses, usernames, passwords, and commands from various protocols (SSH & HTTP supported right now). Written in Python and for educational purposes only.

# Install

**1) Clone repository.**

**2) Permissions.**

Ensure `main.py` has proper permisions. (`chmod 755 main.py`)

**3) Keygen.**

Create a new folder `static`. 

`mkdir static`

Move into directory.

`cd static`

An RSA key must be generated for the SSH server host key. The SSH host key provides proper identification for the SSH server. Ensure the key is titled `server.key` and resides in the same relative directory to the main program.

`ssh-keygen -t rsa -b 2048 -f server.key`

# Usage

The app requires a bind IP address (`-a`) and network port to listen on (`-p`). Use `0.0.0.0` to listen on all network interfaces. The protocol type must also be defined.

```
-a / --address: Bind address.
-p / --port: Port.
-s / --ssh OR -wh / --http: Declare honeypot type.
```

Example: `python3 main.py -a 0.0.0.0 -p 2224 --ssh`

**Optional Arguments**

A username (`-u`) and password (`-w`) can be specified to authenticate the SSH server. The default configuration will accept all usernames and passwords.

```
-u / --username: Username.
-w / --password: Password.
-t / --tarpit: For SSH-based honeypots, -t can be used to trap sessions inside the shell, by sending a 'endless' SSH banner.
```

Example: `python3 main.py -a 0.0.0.0 -p 22 --ssh -u admin -w admin --tarpit`

# Honeypot Types
This honeypot was written with modularity in mind to support future honeypot types (Telnet, HTTPS, SMTP, etc). As of right now there are two honeypot types supported.

## SSH
The project started out with only supported SSH. Use the following instructions above to provision an SSH-based honeypot which emulates a basic shell.

💡 `-t / --tarpit`: A tarpit is a security mechanism designed to slow down or delay the attempts of an attacker trying to brute-force login credentials. Leveraging Python's time module, a very long SSH-banner is sent to a connecting shell session. The only way to get out of the session is by closing the terminal. 

## HTTP
Using Python Flask as a basic template to provision a simple web service, the app impersonates a default WordPress `wp-admin` login page. Username / password pairs are collected.

There are default credentials accepted, `admin` and `password`. Username and password can be changed using the `-u / --username: Username.
-w / --password: Password` arguments.

The web-based honeypot runs on port 4000 by default. This can be changed using the `-p / --port` flag option.

## TLDR; commands to test the module

```
# generate server ssh key
ssh-keygen -t rsa -b 2048 -f server.key

# if running ssh:
python3 main.py -a 127.0.0.1 -p 2224 -u hi -pw hi --ssh

ssh -p 2223 username@127.0.0.1

# if running http
python3 main.py -a 127.0.0.1 -p 2224 --http

# proceed to the link in the terminal and login
```
