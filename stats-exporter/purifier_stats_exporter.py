from miio.airpurifier import AirPurifier, OperationMode
from prometheus_client import start_http_server, Enum, Gauge
import time
import logging
import argparse

LOG_LEVELS = {
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARN,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}


def parse_app_args():
    parser = argparse.ArgumentParser(description='Periodically query device for stats and expose them over http')

    parser.add_argument("-p", "--port",
                        type=int,
                        default=8080,
                        help="port over which stats will be exposed via http")
    parser.add_argument("-i", "--interval",
                        type=int,
                        default=5,
                        help="interval between device queries in seconds")
    parser.add_argument("--log",
                        choices=LOG_LEVELS.keys(),
                        dest="log_level",
                        default="INFO",
                        help="logging level")
    parser.add_argument("--ip",
                        required=True,
                        help="ip of purifier that will be queried for stats")
    parser.add_argument("--token",
                        required=True,
                        help="access token for purifier")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_app_args()
    print(f"Parsed args from command line={args}")

    server_port = args.port
    purifier_ip = args.ip
    purifier_access_token = args.token
    purifier_access_interval_seconds = args.interval
    log_level = LOG_LEVELS.get(args.log_level.upper(), logging.INFO)

    print(f"Setting up logger with level={logging.getLevelName(log_level)}")
    logging.basicConfig(format="%(asctime)s [%(levelname)s][%(name)s] %(message)s", level=log_level)
    log = logging.getLogger('stats.exporter')

    log.info("Starting metrics server at port=%s", server_port)
    start_http_server(server_port)

    log.info("Setting up connection with purifier at ip=%s", purifier_ip)
    purifier = AirPurifier(ip=purifier_ip, token=purifier_access_token)

    log.info("Configuring metrics to export")
    power = Enum("power_state", "Power state", namespace="purifier", states=["on", "off"])
    temperature = Gauge("air_temperature_celsius", "Air temperature", namespace="purifier")
    air_quality = Gauge("air_quality", "Air quality", namespace="purifier")
    air_humidity = Gauge("air_humidity_ratio", "Air humidity", namespace="purifier")
    mode = Enum("operation_mode", "Active mode of device", namespace="purifier",
                states=[mode.value for mode in OperationMode])
    env_illuminance = Gauge("env_illuminance_lux", "Environment illuminance", namespace="purifier")
    motor_speed = Gauge("motor_speed_rpm", "Motor speed", namespace="purifier")

    log.info("Exporter has started, device status will be updated every %s seconds",
             purifier_access_interval_seconds)

    while True:
        status = purifier.status()

        log.debug("Got device status : %s", status)

        power.state(status.power)
        temperature.set(status.temperature)
        air_quality.set(status.aqi)
        air_humidity.set(status.humidity)
        mode.state(status.mode.value)
        env_illuminance.set(status.illuminance)
        motor_speed.set(status.motor_speed)

        time.sleep(purifier_access_interval_seconds)
