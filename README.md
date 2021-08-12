# CAM-AI Server

#### CAM-AI reads security cameras and adds artificial intelligence: No more false alarms!

This is an installation tutorial for a development system of the CAM-AI Server on a PC running Debian Linux. Other configurations are probably possible, but might need some testing and modifications. Here we go:

1. ####  Creating a new user

   It is recommended to create a special user for operating the camera server. In our example this users name will be cam_ai :

   **If the sudo-utility is not yet installed** on your target system, you can install it by doing:

   `su`

   `apt update`

   `apt install sudo`

   `sbin/adduser cam_ai`

   `sbin/usermod -aG sudo cam_ai`

   `exit`

   You will be asked for all kind of information for the new user. The only thing you need to provide is a valid password (2 times), you can skip the rest by hitting return a couple of times. 

   **If the sudo utility is already installed** and your present user has sudo privileges, this part is easier:

   `sudo adduser cam_ai`

   `sudo usermod -aG sudo cam_ai`

   After that, you have to login as the new user. 

   **If you are installing the server on the machine you are typing on**, this goes like:

   `su cam_ai`

   `cd ~`

   If you are logged into your target system via SSH, do this:

   `ssh cam_ai@[name_or_ip]`

   Replace the bracket with name or IP of the target machine. 

   

2. #### Installing a database server

   Because most of the non-volatile information and configuration is stored in a SQL-database, you need to install a database server. If you already have installed a recent version of MariaDB on your target system, you can skip this section.
   

3. Creating a database

