#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# Configuration Names for SAS - python List
# This is the list of allowed configuration definitions that can be used. The definition are defined below.
# if there is more than one name in the list, and cfgname= is not specified in SASsession(), then the user
# will be prompted to choose which configuration to use.
#
# The various options for the different access methods can be specified on the SASsession() i.e.:
# sas = SASsession(cfgname='default', options='-fullstimer', user='me')
#
# Based upon the lock_down configuration option below, you may or may not be able to override option
# that are defined already. Any necessary option (like user, pw for IOM or HTTP) that are not defined will be 
# prompted for at run time. To dissallow overrides of as OPTION, when you don't have a value, simply
# specify options=''. This way it's specified so it can't be overridden, even though you don't have any
# specific value you want applied.
# 
#SAS_config_names = ['default', 'ssh', 'iomlinux', 'iomwin', 'winlocal', 'winiomlinux', 'winiomwin', 'httpsviya', 'httpviya', 'iomcom']
#

SAS_config_names=['ssh']

# Configuration options for saspy - python Dict
# valid key are:
# 
# 'lock_down' - True | False. True = Prevent runtime overrides of SAS_Config values below
#
# 'verbose'   - True | False. True = Allow print statements for debug type messages
#
SAS_config_options = {'lock_down': False,
                      'verbose'  : True
                     }


# Configuration Definitions
#
# For STDIO and STDIO over SSH access methods
# These need path to SASHome and optional startup options - python Dict
# The default path to the sas start up script is: /opt/sasinside/SASHome/SASFoundation/9.4/sas
# A usual install path is: /opt/sasinside/SASHome
#
# Since python uses utf-8, running SAS with encoding=utf-8 is the expected use case. By default Unix SAS runs in Latin1 (iso-8859-1),
# which does not work well as utf-8. So, transcoding has been implemented in the python layer. The 'encoding' option can be specified to match
# the SAS session encoding (see https://docs.python.org/3.5/library/codecs.html#standard-encodings for python encoding values). latin1 is appropriate
# for the default Unix SAS session encoding
#                                                                                                         
# valid keys are:
# 'saspath'  - [REQUIRED] path to SAS startup script i.e.: /opt/sasinside/SASHome/SASFoundation/9.4/sas
# 'options'  - SAS options to include in the start up command line - Python List
# 'encoding' - This is the python encoding value that matches the SAS session encoding your SAS session is using 
#
# For passwordless ssh connection, the following are also reuqired:
# 'ssh'     - [REQUIRED] the ssh command to run
# 'host'    - [REQUIRED] the host to connect to
#
# Additional valid keys for ssh:
# 'port'    - [integer] the remote ssh port
# 'tunnel'  - [integer] local port to open via reverse tunnel, if remote host cannot otherwise reach this client
#
# default  = {'saspath'  : '/opt/sasinside/SASHome/SASFoundation/9.4/bin/sas_u8'
#             }

ssh      = {
            'ssh'     : '/usr/bin/ssh',
            'host'    : 'odum@irss-dls-buildbox.irss.unc.edu', 
            'port'    : 10808,
            'tunnel'  : 9912,
            'rtunnel' : 9911,
            'encoding': 'latin1',
            'saspath' : '/opt/sasinside/SASHome/SASFoundation/9.4/bin/sas_en',
            'options' : ["-fullstimer"]
            }

# # Configuration options for SAS output. By default output is HTML 5.0 (using "ods html5" statement) but certain templates might not work 
# # properly with HTML 5.0 so it can also be set to HTML 4.0 instead (using "ods html" statement). This option will only work when using IOM
# # in local mode. Note that HTML 4.0 will generate images separately which clutters the workspace and if you download the notebook as HTML, 
# # the HTML file will need to be put in the same folder as the images for them to appear.
# # valid key are:

# # 'output' = ['html5', 'html']

# # SAS_output_options = {'output' : 'html5'}

