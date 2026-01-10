import logging
import logging.config
import os
from src.config.app_properties import AppProperties


def configure_logging(log_dir: str = AppProperties.LOG_DIR, log_filename: str = AppProperties.LOG_FILE_NAME, app_prefix: str = 'src'):
    """
    Configures logging for the application.
    :param log_dir:
    :param log_filename:
    :param app_prefix:
    :return:
    """

    # 1. Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # 2. Configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },

        'handlers': {
            'file_handler': {
                'class': 'logging.FileHandler',
                'level': 'INFO',    # The file handler captures INFO and above
                'formatter': 'standard',
                'filename': os.path.join(log_dir, log_filename),
                'mode': 'a',
                'encoding': 'utf-8'
            },
        },

        'loggers': {
            # Root logger
            '': {
                'handlers': ['file_handler'],
                'level': 'WARNING',     # External libs log only WARNING and above
                'propagate': False
            },

            # App logger
            # Overwrite the Root level for everything that starts with "src"
            app_prefix: {
                'handlers': ["file_handler"],
                'level': 'INFO',        # My app logs INFO and above
                'propagate': False
            }
        }
    }

    logging.config.dictConfig(logging_config)