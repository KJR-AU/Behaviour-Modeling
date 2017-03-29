import sys
from behave import *


#
# Support for '@requires-jython' tag on scenarios or features
#
# Since Flying Logic is running the scripts under jython some scripts may take advantage of it.
# For example to build custom dialogs, to run those tests it requires the test automation is also run under jython.
#
# To get jython to play nice with PyCharm
#
# 1. Install to directory eg "~/jython2.7.0" following their instructions
# 2. Open PyCharm and Create a new project interpreter:
#               PyCharm menu -> Preferences
#                   "Project: project-name" -> "Project Interpreter"
#                       [...] -> Add Local
#                           point at "~jython2.7.0/bin/jython"
# 3. Install dependencies, i.e. gherkin-official, behave, pprint, etc.
#
# Note with behave 1.2.5 I also needed to edit junit reporter because jython's sys.version_info is incompatible.
# Replaced property "sys.version_info.major" with to use index sys.version_info[0]
#
#     # See near line 57 of ~/jython2.7.0/Lib/site-packages/behave/reporter/junit.py
#     if sys.version_info[0] == 3:
#         ElementTree._serialize_xml = \
#             ElementTree._serialize['xml'] = _serialize_xml3
#     elif sys.version_info[0] == 2:
#         ElementTree._serialize_xml = \
#             ElementTree._serialize['xml'] = _serialize_xml2
#
def before_scenario(context, scenario):
    if ('requires-jython' in scenario.tags or
                'requires-jython' in scenario.feature.tags):
        # test to see if Jython is present
        try:
            from java.lang import System
        except ImportError as e:
            print ("WARNING: Jython not present; skipping tests marked with requires-jython.\n")
            scenario.skip()
