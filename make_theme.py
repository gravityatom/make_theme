#!/usr/bin/env python3

import sys
import getopt
import argparse
import yaml
import os.path
import subprocess
import shutil
import re
import logging
import getpass

def process_args():
   parser = argparse.ArgumentParser(description='Themify this system')

   parser.add_argument('--theme', type=str, help='Theme name')
   parser.add_argument('--undo', action='store_true', 
                       help='Undo the specified --theme')
   parser.add_argument('--list', action='store_true', 
                       help='List available themes')
   parser.add_argument('--v', action='store_true', 
                       help='Verbose mode, typically for debugging')

   return parser
   #return parser.parse_args()


def list_themes():
    """ This function lists the themes based on the existence
        of directories in the themes directories
    """

    logger.info(f"[list_themes()] Listing themes")

    theme_dir = './themes'
    print(f"\nSupported themes:")
    for theme_dir, dirs, files in os.walk(theme_dir):


        counter = 1
        for subdir in dirs:
            logger.info(os.path.join(theme_dir, subdir))
            print(f"{counter}. {subdir}")
            counter += 1

    ## Print an extra new line to seperate from command prompt
    print("\n")

def set_customizations(theme_conf):
    """This function is the procudure for setting
    the customizations. It calls the specific functions
    to implement the settings"""

    set_hostname(theme_conf["hostname"])

    set_background(theme_conf['background_image'])

    create_admins(theme_conf['admins'])

    create_users(theme_conf['users'])

    set_login_user(theme_conf['default_user'])

    install_software(theme_conf['software'])

    #wconfigure_services()

    create_readme(theme_conf)

def undo_theme(theme_conf):

    logger.info(f"[undo_theme()] hostname: {script_conf['default_hostname']}")
    set_hostname(script_conf['default_hostname'])

    undo_background()

    set_login_user(script_conf['default_user'])
    delete_users(theme_conf['users'])

    delete_admins(theme_conf['admins'])

    delete_software(theme_conf['software'])





def delete_users(users):
    logger.info(f"[delete_users()]")

    for userid in users:

        logger.info(f"[delete_users()] userid: {userid}")

        #cmd_deluser = '/usr/sbin/deluser --force --remove-all-files ' + userid
        cmd_deluser = '/usr/sbin/deluser ' + userid
        logger.info(f"[create_admins()] cmd_deluser: {cmd_deluser}")

        returned_value = subprocess.call(cmd_deluser, shell=True)


def delete_admins(admins):
    logger.info(f"[delete_admins()]")

    for userid in admins:

        logger.info(f"[delete_admins()] userid: {userid}")

        cmd_deluser = '/usr/sbin/deluser ' + userid + 'sudo'
        logger.info(f"[delete_admins()] Remove sudo access for {userid}")

        returned_value = subprocess.call(cmd_deluser, shell=True)

        #cmd_deluser = '/usr/sbin/deluser --force --remove-all-files ' + userid
        cmd_deluser = '/usr/sbin/deluser ' + userid
        logger.info(f"[delete_admins()] cmd_deluser: {cmd_deluser}")

        returned_value = subprocess.call(cmd_deluser, shell=True)


def delete_software(software_list):
    """ DElete the software """

    logger.info(f"[delete_software()]")
    for sw in software_list:

        logger.info(f"[delete_software()] sw: {sw}")

        cmd_sw_remove = "/usr/bin/apt remove -y " + sw
        logger.info(f"[delete_software()] cmd_sw_remove: {cmd_sw_remove}")

        returned_value = subprocess.call(cmd_sw_remove, shell=True)



def create_readme(theme_conf):
    logger.info(f"[create_readme()] ")

    readme_tmpl_file = "themes/" + args.theme + "/readme.tmpl.html"
    logger.info(f"[create_readme()] Reading {readme_tmpl_file}")

    # Open the readme_tmpl_file
    tmpl = open(readme_tmpl_file, "rt")

    #read file contents to string
    tmpl_content = tmpl.read()

    ## Generate admin list
    admin_list = ''
    for userid in theme_conf['admins']:
        admin_list =  admin_list + userid + ': ' + \
            theme_conf['admins'][userid]['password'] + "\n"

    ## Generate user list
    user_list = ''
    for userid in theme_conf['users']:
        user_list =  user_list + userid + ': ' + \
            theme_conf['users'][userid]['password'] + "\n"


    #replace all occurrences of the required string
    tmpl_content = tmpl_content.replace('TMPL_ADMINS', admin_list)

    tmpl_content = tmpl_content.replace('TMPL_USERS', user_list)

    tmpl_content = tmpl_content.replace('TMPL_COMPANY', \
        theme_conf['readme']['company'])

    tmpl_content = tmpl_content.replace('TMPL_SERVICES', \
        theme_conf['readme']['services'])

    tmpl_content = tmpl_content.replace('TMPL_HOSTNAME', \
        theme_conf['hostname'])

    #close the input file
    tmpl.close()

    user_desktop_readme_file =  "/home/" + theme_conf['default_user'] + \
                   "/Desktop/README.html"

    readme_file =  "themes/" + args.theme + "/README.html"

    logger.info(f"[create_readme()] Writing README to {readme_file}")

    ## Create the user Desktop directory if it does not exist
    user_desktop_dir = '/home/' + theme_conf['default_user'] + '/Desktop'
    desktop_exists = os.path.exists(user_desktop_dir)

    if desktop_exists is False:
        # Create a new directory because it does not exist
        os.makedirs(user_desktop_dir)
        logger.info("The desktop directory ({user_desktop_dir}) created!")


    # Open the readme file for writing
    readme_out = open(readme_file, "wt")

    # Save the tmp_content to the file
    readme_out.write(tmpl_content)

    #close the file
    readme_out.close()

    # Copy the generated README to the defualt users home directory
    logger.info(f"[create_readme()] Copying README from {readme_file} "
                f"to {user_desktop_readme_file}")

    shutil.copyfile(readme_file, user_desktop_readme_file)

    cmd_chown = "/usr/bin/chown " + theme_conf['default_user'] + \
                ' ' + user_desktop_readme_file

    logger.info(f"[create_readme()] cmd_chown: {cmd_chown}")

    returned_value = subprocess.call(cmd_chown, shell=True)




def set_hostname(new_hostname):
    """ Set the hostname using hostnamectl"""

    logger.info(f"[set_hostname()] hostname: {new_hostname}")

    cmd = "/usr/bin/hostnamectl set-hostname " + new_hostname

    returned_value = subprocess.call(cmd, shell=True)


def install_software(software_list):
    """ Install the software """

    logger.info(f"[install_software()]")
    for sw in software_list:

        logger.info(f"[install_software()] sw: {sw}")

        cmd_sw_install = "DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -y " + sw
        logger.info(f"[install_software()] cmd_sw_install: {cmd_sw_install}")

        returned_value = subprocess.call(cmd_sw_install, shell=True)

def undo_background():
    """ Reset the background to the default Ubuntu wallpaper """

    logger.info(f"[undo_background()] Reseting wallpaper to the default")
    logger.info(f"[undo_background()] Copying " 
                f"{script_conf['default_bg']}.mktheme " 
                f"to {script_conf['default_bg']}")

    shutil.copyfile(script_conf['default_bg'] + '.mktheme', 
                    script_conf['default_bg'])


def set_background(background_image):
    """ Set the background associated with the theme
        TODO: Implement the correct way to set/update the backgroud
              image for all users
    """
    logger.info(f"[set_background()] background_image: {background_image}")

    ## Path to bg image from the themes directory
    bg_path = os.getcwd() + '/themes/' + args.theme + '/' + background_image

    bg_usr_share_path = '/usr/share/backgrounds/' + background_image

    ## Copy them background image to /usr/share/backgrounds
    logger.info(f"[set_background()] Copying {bg_path} to {bg_usr_share_path}")

    shutil.copyfile(bg_path, bg_usr_share_path)

    default_bg_backup_exists = os.path.exists(script_conf['default_bg'] + \
                                              ".mktheme")

    if default_bg_backup_exists is False:
        ## Make a backup copy of the default ubuntu bg 
        logger.info(f"[set_backgroud()] No backup copy of default "
                    f"ubuntu bg exists")

        shutil.copyfile(script_conf['default_bg'], 
                        script_conf['default_bg'] + '.mktheme')

        logger.info(f"[set_backgroud()] making a backup copy of " 
                    f"{script_conf['default_bg']}")


    ## Override the default_bg with the theme bg
    logger.info(f"[set_background()] Copying {bg_usr_share_path} to " 
                f" {script_conf['default_bg']}")

    shutil.copyfile(bg_usr_share_path, script_conf['default_bg'])

    ## Update the /etc/skel/.bashrc to include the gsettings command
    ## to set the background

    ## Create backup copy 
    skel_bashrc = '/etc/skel/.bashrc'

    skel_bashrc_backup_exists = os.path.exists(skel_bashrc + ".mktheme")

    if skel_bashrc_backup_exists is False:
        ## Make a backup copy of the default ubuntu bg 
        logger.info(f"[set_backgroud()] No backup copy of {skel_bashrc}")

        shutil.copyfile(skel_bashrc, skel_bashrc + '.mktheme')

        logger.info(f"[set_backgroud()] making a backup copy of {skel_bashrc}") 

    # Open the readme_tmpl_file
    skel = open(skel_bashrc, "r")

    #read file contents to string
    bashrc_content = skel.read()
    skel.close()

    gsettings_content = "\n#Set background image\n" + \
                     "gsettings set org.gnome.desktop.background " + \
                     "picture-uri file://" + script_conf['default_bg']

    logger.info(f"[set_backgroud()] gsettings_content: {gsettings_content}")

    bashrc_content = bashrc_content + gsettings_content

    # Open the skel_bashrc file for writing
    skel_bashrc_out = open(skel_bashrc, "w")

    # Save the bashrc_content to the file
    skel_bashrc_out.write(bashrc_content)

    #close the file
    skel_bashrc_out.close()

    logger.info(f"[set_backgroud()] Updated {skel_bashrc}")



def create_admins(admins):
    """ Create admin users accounts """

    logger.info(f"[create_admins()]")

    user_pwfile = '/tmp/adminuserpw.txt';
    pwfile      = open(user_pwfile, "w")

    for userid in admins:

        logger.info(f"[create_admins()] userid: {userid}")

        cmd_adduser = '/usr/sbin/adduser --gecos "' + admins[userid]['name'] + \
                      '" --disabled-password ' + userid

        logger.info(f"[create_admins()] cmd_adduser: {cmd_adduser}")

        returned_value = subprocess.call(cmd_adduser, shell=True)

        cmd_usermod = '/usr/sbin/usermod -aG sudo ' + userid

        logger.info(f"[create_admins()] cmd_usermod: {cmd_usermod}")

        returned_value = subprocess.call(cmd_usermod, shell=True)

        pwfile.write(userid + ":" + admins[userid]['password'] + "\n")


    pwfile.close()

    cmd_chpasswd = "/usr/sbin/chpasswd < " + user_pwfile
    logger.info(f"[create_admins()] cmd_chpaswd: {cmd_chpasswd}")

    returned_value = subprocess.call(cmd_chpasswd, shell=True)

def set_login_user(userid):
    """ Set the default login user """

    custom_login_file = "/etc/gdm3/custom.conf"
    logger.info(f"[set_login_user()] Updating {custom_login_file}"
                f"for userid: {userid}")

    ## Determine current custom settings
    login_file = open(custom_login_file, "rt")

    ## Look for 
    ##  AutomaticLoginEnable = true
    ## AutomaticLogin = user1

    new_login_content = ''
    for line in login_file:
        logger.info(f"[set_login_user()] line: {line}")

        if (re.match(r'AutomaticLoginEnable\s+=', line)):
            logger.info(f"[set_login_user()] matched AutomaticLoginEnable")

            new_login_content = new_login_content + \
                                "AutomaticLoginEnable = true\n"

        elif (re.match(r'AutomaticLogin\s+=', line)): 
            logger.info(f"[set_login_user()] matched AutomaticLogin")
            new_login_content = new_login_content + "AutomaticLogin = " + \
                                userid + "\n"

        else:
            new_login_content = new_login_content + line

    login_file.close()

    backup_file_exists = os.path.exists(custom_login_file + ".mktheme")

    if backup_file_exists is False:
        ## Make a backup copy of the current 
        logger.info(f"[set_login_user()] making a backup copy of ",
                    f" {custom_login_file}")

        shutil.copyfile(custom_login_file, custom_login_file + '.mktheme')

    #open the input file in write mode
    login_file_out = open(custom_login_file, "wt")

    #overrite the input file with the resulting data
    login_file_out.write(new_login_content)

    #close the file
    login_file_out.close()



def create_users(users):
    """ Create users accounts """

    logger.info(f"[create_users()]")

    user_pwfile = '/tmp/userpw.txt';
    pwfile      = open(user_pwfile, "w")

    for userid in users:

        logger.info(f"[create_users()] userid: {userid}")

        cmd_adduser = '/usr/sbin/adduser --gecos "' + users[userid]['name'] + \
                      '" --disabled-password ' + userid

        logger.info(f"[create_users()] cmd_adduser: {cmd_adduser}")

        returned_value = subprocess.call(cmd_adduser, shell=True)

        pwfile.write(userid + ":" + users[userid]['password'] + "\n")


    pwfile.close()

    cmd_chpasswd = "/usr/sbin/chpasswd < " + user_pwfile
    logger.info(f"[create_admins()] cmd_chpaswd: {cmd_chpasswd}")

    returned_value = subprocess.call(cmd_chpasswd, shell=True)

if __name__ == "__main__":

    # Check that script is running as root
    if (getpass.getuser() != 'root'):
        print("ERROR: You must run script as root or using sudo\n")
        exit()

    ## Load the script configuration file
    script_conf_file = './conf/mk_theme.yml'
    script_conf      = ''

    try:
      with open(script_conf_file) as f:
        script_conf = yaml.load(f, Loader=yaml.FullLoader)

    except FileNotFoundError:
      print(f"ERROR: Unable to load {script_conf_file}")
      exit()


    ## Setup the loggined
    logging.basicConfig(filename=script_conf['log_file'],
                        format='%(asctime)s, %(message)s',
                        filemode='w')

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ## Parse the command line options
    parser = process_args()
    args   = parser.parse_args()

    logger.info(f"Processing command line options")

    if (args.list):
        list_themes()
        exit()

    if not args.theme:
        ## Not theme specified, display the help and exit
        parser.print_help()
        exit()


    logger.info(f"Processing theme: {args.theme}")

    theme_conf_file = "themes/" + args.theme + "/theme.yml"

    logger.info(f"Processing theme_conf: {theme_conf_file}")

    if not os.path.exists(theme_conf_file):
        logger.error(f"ERROR: theme_conf was not found!")
        print(f"ERROR: theme_conf was not found!\n")
        exit()


    ## Load the application yaml configuration file
    with open(theme_conf_file) as f:
        theme_conf = yaml.load(f, Loader=yaml.FullLoader)

        logger.info(theme_conf)

    if (args.undo):
        undo_theme(theme_conf)
    else:
        ## Procedure to set the customization imtes
        set_customizations(theme_conf)






