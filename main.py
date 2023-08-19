from core.heater import Heater
from utils import clear_files
from constants import LOW_BALANCES_FILE, TX_ERRORS_FILE


def main():
    clear_files([LOW_BALANCES_FILE, TX_ERRORS_FILE])
    heater = Heater()
    heater.warmup()


if __name__ == "__main__":
    main()
