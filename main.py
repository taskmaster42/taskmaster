from taskmasterd import run
from taskmasterctl.server_http import Myserver
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        server = Myserver()
        run(server)
    except Exception as e:
        server.stop_server()
        logger.warning(e)