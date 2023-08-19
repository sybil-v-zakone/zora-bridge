from core.heater import Heater
from utils import clear_files
from config import low_balances_file, tx_errors_file


def main():
    clear_files([low_balances_file, tx_errors_file])
    heater = Heater()
    heater.warmup()


if __name__ == "__main__":
    main()
