1. Cubesat contains both the navigation software (navAlpha3) and arucotracklib.py .

2. In order to run navigation, be sure that the SimPlat server is running first, as well as know the IP address for SimPlat. Make sure to make the changes to the IP address if necessary to line in line 17 , 18 in navAlpha3.py.

3. To run the SimPlat server, locate csCodeV5.py on SimPlat. Run via command line by using "python3 csCodeV5.py"

3. Once the SimPlat server is running, execute the navAlpha3 file on CubeSat via command line by entering ” python3 navAlpha3.py “. If both were successfully executed, you will get a print statement from the SimPlat noting a connection has been made with the CubeSat. 

4. CubeSat will start searching for its target and execute the needed commands to reach its destination.