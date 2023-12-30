from env import config
from Shuake import Shuake


if __name__ == '__main__':
    shuake = Shuake()
    shuake.setup(config.CHROME_DRIVER_PATH)
    shuake.run_shuake()