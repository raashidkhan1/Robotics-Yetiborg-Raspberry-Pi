# Yetiborgs based on Raspberry Pi Robotics play tag

---

# Connecting to the robot
1. Set up a mobile hotspot with networkname `lmlrobotics` and password `Staratio10!`. Turn it on
2. Put a battery in the Yetiborg
3. Connect your pc to the same network.
4. In a command prompt, run
    * Windows: `ssh pi@yeti05` (or the name of your YetiBorg if you are using a different one)
    * Mac `ssh pi@yeti05.local`
   
   if this doesn't work try restarting DNS with `sudo killall -HUP mDNSResponder`
      
5. When prompted for a password, type `raspberry` and press Enter.
6. Activate the virtualenv - test-env by 
    `source ./test-env/bin/activate`
7. Run `cd robotics`
8. If this is your first time, generate a personal access token from GitHub: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
9. Run `git pull` to get the latest code. If asked to log in to GitHub, enter your username and use the token when asked for a password. Note: for some reason it can take a while before your are prompted for your username and token, such that it seems as if nothing happens. No clue why this is or how it can be fixed.
10. Run `python3 main.py` to run the main script. The following arguments can be passed:
    *  `-a <arg>` or `--agent <arg>`: the agent to use. Possible values are "tag". Default is "tag".
    *  `-v <arg>` or `--vision <arg>`: whether to show plots on the client side. Possible values are "True" and "False". Default is "False". See 'Showing visuals on the client side' below to see how to enable this feature.

# Shutting down the robot.
It is never said to us directly, but some old Yetiborg instructions found [here](https://liacs.leidenuniv.nl/~bakkerem2/robotics/Robotics_YetiBorg_Racing_2020.pdf) ask to shut down the yetiborg before taking out the battery after use. To do so, run the command `sudo shutdown -h now`. The robot will disconnect. Only then remove the battery to prevent corrupting the SD-Card. To reboot, use `sudo reboot`.

# Manual control
1. Complete steps 1-5 in the section 'Connecting to the robot'.
2. Run `ifconfig` and copy the IP address shown for **wlan0** after **inet**
3. In your browser, go to `http://<ip>`, where `<ip>` is said IP address.
4. Run `cd yetiborgv2`
5. Run `sudo ./yeti2Web.py`
6. The web interface now loads and shows the video stream and control buttons. It appears that the 'reverse' option is broken.

# Changing the Yetiborg's network settings
One can change the network name and password that the Yetiborg looks for when connect to the battery. The defaults are the networkname `lmlrobotics` and password `Staratio10!` mentioned above. Once connected, you can change these to - for example - your home wifi network using the steps below. Always change them back to the defaults when you take the robot somewhere!
1. Complete steps 1-5 in the section 'Connecting to the robot'.
2. Run `sudo raspi-config`
3. In the menu, select 'Network Options', then 'Wi-fi'. Enter your network's name and subsequently the password.

# Important: Enabling remote configuration on the yetiborg before using the remote led communication functionality
Follow [these steps](https://gpiozero.readthedocs.io/en/stable/remote_gpio.html#preparing-the-raspberry-pi) for configuring the yetiborg before using the remote communication and install PiGPIO.

# Enabling visuals on the client side
The Yetiborg does not have a display, so function calls like `cv2.imshow(image)` do not work. For development purposes, however, it is nice to be able to see images taken by the robot on your computer. To do this, X11 forwarding has to be enabled. See [this tutorial](https://techsphinx.com/raspberry-pi/enable-x11-forwarding-on-raspberry-pi/?utm_source=rss&utm_medium=rss&utm_campaign=enable-x11-forwarding-on-raspberry-pi) for an explanation on how to this. The section 'Setup X11 Forwarding on Raspberry Pi' can be ignored; they have already been taken care of. Once the setup is complete, running `main.py --vision True` will enable showing the visuals. Note that the `BaseAgent` class has a `show_image` method to show the most recently captured image. For windows: don't forget to start Xming (or alternative) before using PuTTY).

# Accessing picamera docs
The Yetiborg uses the `picamera` package, which **only** words on raspberry pi systems. Your IDE thus won't recognize picamera in the source code and trying to install it with `pip install picamera` yields an error. You can fix this on Windows and Unix based systems using the steps [here](https://github.com/waveform80/picamera/issues/539#issuecomment-476651665). Of course, you won't be able to run the code on your device, but you will have access to the documentation.


# Update Python on the YetiBorg
Our code assumes Python 3.9. Installing it one a Raspberry Pi Zero can be a plague, so here's the steps. All the `make` commands take long times, so be sure to do something else in the meantime.
1. Follow the steps [here](https://help.dreamhost.com/hc/en-us/articles/360001435926-Installing-OpenSSL-locally-under-your-username) to install OpenSSL (required for pip, if you don't do this you won't be able to install any packages). You may want to skip the `make test` in step 9 to save time, and should omit the line `export LC_ALL="en_US.UTF-8"` in step 12. Use `pi` as username in steps 8 and 12. Yes, the `.bash_profile` is empty before step 12 - create it using `sudo nano .bash_profile`.
2. install Python 3.9.13 using [these steps](https://raspberrytips.com/install-latest-python-raspberry-pi/) BUT instead of `./configure --enable-optimizations`, run `./configure --enable-optimizations --with-openssl=/home/pi/openssl`. After the `sudo make altinstall` command, run `python3 -m ssl` and if nothing outputs, things went alright. Now you can create a virtualenv `env` in the root directory and install the requirements.
If python3.9 -m ssl still throws module import error, try [these steps](https://techglimpse.com/install-python-openssl-support-tutorial)
