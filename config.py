# путь до файла с приватниками
private_keys_file = "data/private_keys.txt"

# количество ETH для бриджа, [от, до] (выбирается рандомное с округлением до 3-х знаков)
amount_range = [0.006, 0.006]

# время между бриджами, [от, до] (выбирается рандомное число)
sleep_time = [10, 30]

# максимальная цена газа в Gwei, при которой будет проводиться бридж
gas_threshold = 20

# диапазон времени задержки между проверками текущей цены газа в секундах
gas_delay_range = [10, 15]

eth_rpc = "https://rpc.ankr.com/eth"