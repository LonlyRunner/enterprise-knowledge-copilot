import logging


logger = logging.getLogger(__name__)


class HumanApproval:


    async def approve(
        self,
        content,
    ):

        logger.info("Human approval requested: %s", content)

        return True
