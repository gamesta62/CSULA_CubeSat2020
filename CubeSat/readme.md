{\rtf1\ansi\ansicpg1252\cocoartf2512
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;\red199\green200\blue201;\red26\green28\blue31;}
{\*\expandedcolortbl;;\cssrgb\c81961\c82353\c82745;\cssrgb\c13333\c14510\c16078;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs30 \cf2 \cb3 \expnd0\expndtw0\kerning0
1. Cubesat\'a0contains both the navigation software (navAlpha3) and arucotracklib.py .\
\
2. In order to run navigation, be sure that the SimPlat server is running first, as well as know the IP address for SimPlat.\'a0Make sure to make the changes to the IP address if\'a0necessary to line in line 17 , 18 in navAlpha3.py.\
\
3. To run the SimPlat server, locate csCodeV5.py on SimPlat. Run via command line by using "python3 csCodeV5.py"\
\
3. Once the SimPlat server is running, execute the navAlpha3 file on CubeSat via command line by entering \'94 python3 navAlpha3.py \'93. If\'a0both were successfully executed, you will get a print statement from the SimPlat noting a connection has been made with the CubeSat.\'a0\
\
4. CubeSat will start searching for its target and execute the needed commands to reach its destination.}