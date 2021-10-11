# CAM-AI Server

#### CAM-AI reads security cameras and adds artificial intelligence: No more false alarms!

This is an installation tutorial for a development system of the CAM-AI Server on a RaspBerry Pi 4 with 4 GB of memory and Debian 11 64bit (get it at https://raspi.debian.net/tested-images/). Other configurations are probably possible, but might need some testing and modifications. Raspberry Pi OS does not work. Here we go:

1. ####  Creating a new user

   It is recommended to create a special user for operating the camera server. In our example this users name will be cam_ai :

   **If the sudo-utility is not yet installed** on your target system, you can install it by doing:

   Log in as root.

   `apt update`

   `apt install sudo`

   `/usr/sbin/adduser cam_ai`

   `/usr/sbin/usermod -aG sudo cam_ai`

   You will be asked for all kind of information for the new user. The only thing you need to provide is a valid password (2 times), you can skip the rest by hitting return a couple of times. 

   `exit`

   **If the sudo utility is already installed** and your present user has sudo privileges, this part is easier:

   `sudo adduser cam_ai`

   `sudo usermod -aG sudo cam_ai`

   After that, you have to login as the new user. 

   **If you are installing the server on the machine you are typing on**, this goes like:

   `su cam_ai`

   `cd ~`

   **If you are installing on a remote target system via SSH**, do this:

   `exit`

   `ssh cam_ai@[name_or_ip]`

   Replace the bracket with name or IP of the target machine. 

   

2. #### Installing a database server

   Because most of the non-volatile information and configuration is stored in a SQL-database, you need to install a database server. **If you already have installed a recent version of MariaDB** on your target system, you can skip this section.

   Here are the steps to install the server:

   `sudo apt update`

   `sudo apt install mariadb-server`

   `sudo mysql_secure_installation` 

   The Secure-Installation-Tool will ask you to set the database password. Do that and accept the default for all the other questions.

   

3. #### Creating an db user

   We need a special CAM-AI-User for the database:

   `sudo mysql`

   `grant all on *.* to 'CAM-AI'@'localhost' identified by 'SelectAPassword' with grant option;`

   `flush privileges;`

   `exit`

   

4. #### Cloning this repository from Github 

   If needed, install GIT:

   `sudo apt install git`

   Then do the cloning:

   `git clone https://github.com/ludgerh/cam-ai-server`

   

5. #### Create the database in the local server

   Log in as the new user. You will need the password you defined in Section 3:

   `mysql -u CAM-AI -p`

   Then create the database:

   ``create database `C-SERVER`;``

   `exit`

   Import the initial data:

   `mysql -u CAM-AI -p "C-SERVER" < ~/cam-ai-server/sql/new.sql`

   

6. #### Create your private password file

   `cp ~/cam-ai-server/c_server/passwords.py.example ~/cam-ai-server/c_server/passwords.py`

   `nano ~/cam-ai-server/c_server/passwords.py`

   Modify the two variables db_password and security_key. The easiest way to get a valid Django Security Key is usinfg the generator on https://djecrety.ir/ .

   Save and close Nano.

   

7. #### Create an Python environment

   On Raspi-Debian you have to install Python first:

   `sudo apt install python3`

   `sudo apt install python3-dev`

   Change to the project folder:

   `cd ~/cam-ai-server`

   Install the virtual environment tool, create an environment and update PIP:

   `sudo apt install python3-venv`

   `python3 -m venv env`

   `source env/bin/activate`

   `pip install --upgrade pip`

   

8. #### Fill the environment with all needed libraries

   `pip install django`

   `pip install channels`

   `pip install mysqlclient`

   `pip install pillow`

   `pip install opencv-contrib-python`

   `pip install requests`

   `sudo apt install ffmpeg` 

   `pip install ffmpeg-python`

   `pip install multitimer`

   `pip install shapely`

   

9. #### Start the server

   `nano ~/cam-ai-server/c_server/settings.py`

   Find the variable ALLOWED_HOSTS and add your hosts domain or IP address to the bracket.

   Find the variable STATIC_ROOT and replace the old value by "~/cam-ai-server/c_server/static/"

   Save and close Nano.

   `mkdir ~/cam-ai-server/c_client/static/nogit`

   `cd ~/cam-ai-server/c_client/static/nogit`

   `wget -r https://static.cam-ai.de/static.zip`

   `unzip static.cam-ai.de/static.zip`

   `rm -R static.cam-ai.de`

   `cd ~/cam-ai-server`

   `mkdir ~/cam-ai-server/log`

   After that you should be able to start the server. Replace the IP with the actual address of your server host.

   `python manage.py runserver [ip]:8000`

   

10. 

