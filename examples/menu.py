import nuke

#set up basic logging to debug DagNabbit
import logging
FORMAT = logging.Formatter('%(messages)s')
logging.basicConfig(level=logging.INFO)
logging.basicConfig(format=FORMAT)
