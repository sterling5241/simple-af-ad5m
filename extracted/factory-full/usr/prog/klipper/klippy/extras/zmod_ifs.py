# (C) 2025 ghzserg https://github.com/ghzserg/zmod/
import json
import serial
import re
import time
import threading
import logging

# Параметры порта
PORT = '/dev/ttyS4'
BAUDRATE = 115200
PARITY = 'N'
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 0.2
HOST_REPORT_TIME = 0.2

STATUS_READY = 5

class zmod_ifs:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        self.query_adc = self.printer.lookup_object('query_adc')
        self.filament_sensor = self.printer.lookup_object('temperature_sensor filamentValue')
        self.language = 'en'
        self.zmod = self.printer.lookup_object('zmod', None)
        if self.zmod is not None:
            self.language = self.zmod.get_lang()
        self.ifs_data = IfsData()
        self._command = "F13"
        self.command_lock = threading.Lock()
        self.response_condition = threading.Condition()
        self.pending_responses = {}
        self.command_counter = 0
        self.stop_thread = False
        self.sensor_thread = threading.Thread(target=self._sensor_reader)
        self.sensor_thread.daemon = True
        self.sensor_thread.start()

        # Регистрация событий
        self.printer.register_event_handler("klippy:disconnect", self.handle_disconnect)
        self.printer.register_event_handler("klippy:shutdown", self.handle_shutdown)

        # Регистрация команд G-кода
        self.gcode.register_command('IFS_INSERT', self.cmd_IFS_INSERT, desc=self.cmd_IFS_INSERT_help)
        self.gcode.register_command('IFS_STATUS', self.cmd_IFS_STATUS, desc=self.cmd_IFS_STATUS_help)
        self.gcode.register_command('IFS_SENSOR', self.cmd_IFS_SENSOR, desc=self.cmd_IFS_SENSOR_help)
        self.gcode.register_command('IFS_F23', self.cmd_IFS_F23)
        self.gcode.register_command('IFS_F24', self.cmd_IFS_F24)

    def handle_disconnect(self):
        logging.info("Printer disconnected. Stopping sensor thread.")
        self.close()

    def handle_shutdown(self):
        logging.info("Printer shutdown. Stopping sensor thread.")
        self.close()

    def close(self):
        self.stop_thread = True
        with self.response_condition:
            self.response_condition.notify_all()
        time.sleep(0.1)  # Даем время сработать notify_all
        if self.sensor_thread.is_alive():
            self.sensor_thread.join(timeout=2.0)

    def _respond_info(self, msg):
        self.reactor.register_async_callback(
            lambda e: self.gcode.respond_info(msg))

    def _error(self, msg):
        self.reactor.register_async_callback(
            lambda e: raise self.gcode.error(msg))

    def getlang(self):
        if self.zmod is None:
            self.language = 'en'
            self.zmod = self.printer.lookup_object('zmod', None)
            if self.zmod is not None:
                self.language = self.zmod.get_lang()

    def get_extruder_sensor(self):
        value, timestamp = self.query_adc.adc["temperature_sensor filamentValue"].get_last_value()
        result = True
        if value > 0.3:
            result = (value >= 0.72)
        return result

    def get_ifs_sensor(self):
        return self.ifs_data.get_stall()

    def send_command_and_wait(self, command, timeout=15.0):
        with self.command_lock:
            self.command_counter += 1
            command_id = self.command_counter
        with self.response_condition:
            self.pending_responses[command_id] = None
            self.set_command(f"{command}#{command_id}")
        with self.response_condition:
            waited = self.response_condition.wait(timeout)
            if not waited or self.pending_responses[command_id] is None:
                with self.command_lock:
                    del self.pending_responses[command_id]
                return None
            response = self.pending_responses[command_id]
            with self.command_lock:
                del self.pending_responses[command_id]
            return response

    def get_command(self):
        with self.command_lock:
            return self._command

    def set_command(self, new_command):
        with self.command_lock:
            self._command = f"{new_command}"

    def wait_for_state(self, target_state=STATUS_READY, timeout=10):
        start_time = time.time()
        while not self.stop_thread:
            self.ifs_data.state_zero()
            response = self.send_command_and_wait("F13")
            self.gcode.respond_info(f"F13 > {response}")
            current_values = self.ifs_data.get_values()
            state = current_values['State']
            self.gcode.respond_info(f"State > {state} ? {target_state}")
            if current_values['State'] == target_state:
                return True
            if time.time() - start_time > timeout:
                raise self.gcode.error("Timeout waiting for IFS state")
                return False
        return False

    def _insert(self, prutok):
        self.gcode.respond_info(f"AutoInsert {prutok}")
        if not self.wait_for_state():
            return
        response = self.send_command_and_wait(f"F24 C{prutok}")
        self.gcode.respond_info(f"F24 C{prutok} > {response}")
        if not self.wait_for_state():
            return
        response = self.send_command_and_wait(f"F10 C{prutok} L600 S1200")
        self.gcode.respond_info(f"F10 C{prutok} L600 S1200 > {response}")
        if not self.wait_for_state():
            return
        response = self.send_command_and_wait(f"F23 C3{prutok}")
        self.gcode.respond_info(f"F23 C{prutok} > {response}")

    cmd_IFS_INSERT_help = "Manually trigger filament insertion"
    def cmd_IFS_INSERT(self, gcmd):
        prutok = gcmd.get_int('PRUTOK', 1)
        self._insert(prutok)

    def cmd_IFS_F23(self, gcmd):
        prutok = gcmd.get_int('PRUTOK', 1)
        response = self.send_command_and_wait(f"F23 C{prutok}")
        self.gcode.respond_info(f"F23 C{prutok} > {response}")

    def cmd_IFS_F24(self, gcmd):
        prutok = gcmd.get_int('PRUTOK', 1)
        response = self.send_command_and_wait(f"F24 C{prutok}")
        self.gcode.respond_info(f"F24 C{prutok} > {response}")

    cmd_IFS_STATUS_help = "Get current IFS status"
    def cmd_IFS_STATUS(self, gcmd):
        values = self.ifs_data.get_values()
        gcmd.respond_info(json.dumps(values))

    cmd_IFS_SENSOR_help = "Get current IFS SENSOR"
    def cmd_IFS_SENSOR(self, gcmd):
        gcmd.respond_info(str(self.get_ifs_sensor()))

    def _sensor_reader(self):
        ser = None
        while not self.stop_thread:
            try:
                ser = serial.Serial(
                    port=PORT,
                    baudrate=BAUDRATE,
                    parity=PARITY,
                    stopbits=STOPBITS,
                    bytesize=BYTESIZE,
                    timeout=TIMEOUT
                )
                while not self.stop_thread:
                    self.ifs_data.state_zero()

                    current_command = self.get_command()
                    command_id = -1
                    if '#' in current_command:
                        command, command_id = current_command.split('#', 1)
                        command_id = int(command_id)
                    else:
                        command = current_command

                    ser.write(command.encode())
                    ser.write(b'\r\n')
                    time.sleep(0.2)
                    ser.write(b'\xFF')

                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    #self._respond_info(f"IN: {response}")
                    if not response:
                        logging.warning("Empty response from device. Possible disconnect.")
                        self.set_command("F13")
                        break

                    if command_id == -1:
                        self.ifs_data.update_from_string(response)
                        current_values = self.ifs_data.get_values()

                        #self._respond_info(response)
                        #self._respond_info(json.dumps(current_values))

                        # Безопасная обработка события вставки
                        if current_values['NeedInsert']:
                            self.reactor.register_async_callback(
                                lambda e, p=current_values['Insert']: self._insert(p))
                    else:
                        #self._respond_info(f"! {command} -> {response}")
                        with self.response_condition:
                            self.pending_responses[command_id] = response
                            self.response_condition.notify_all()
                        self.set_command("F13")
                    time.sleep(HOST_REPORT_TIME)
            except serial.SerialException as e:
                logging.warning("Serial communication error: %s", e)
                self._respond_info(f"IFS sensor error: {str(e)}")
            except Exception as e:
                logging.exception("IFS: Error data")
                self._error(f"IFS sensor error: {str(e)}")
            finally:
                if ser and hasattr(ser, 'is_open') and ser.is_open:
                    try:
                        ser.close()
                        logging.info(f"{PORT} closed")
                    except Exception as e:
                        logging.warning("Error closing serial port: %s", e)
                time.sleep(0.5)

    def __del__(self):
        self.stop_thread = True
        with self.response_condition:
            self.response_condition.notify_all()
        if self.sensor_thread.is_alive():
            self.sensor_thread.join(timeout=1.0)


class IfsData:
    def __init__(self):
        self.lock = threading.Lock()
        self.Port1 = False      # Загрузка порта 1
        self.Port2 = False      # Загрузка порта 2
        self.Port3 = False      # Загрузка порта 3
        self.Port4 = False      # Загрузка порта 4
        self.Chan = 0           # Текущий активный порт
        self.Insert = 0         # В каком порту появился филамент
        self.Stall = 0          # Скорость движения нити
        self.State = 0          # Состояние IFS
        self.NeedInsert = False # Нужно ли вставлять пруток

    def state_zero(self):
        with self.lock:
            self.State = 0

    def update_from_string(self, data_str):
        silk_state = 0
        chan = 0
        insert = 0
        stall = 0
        state = 0

        state_match = re.search(r'FFS_state:\s*(\d+)', data_str)
        if state_match:
            state = int(state_match.group(1))

        silk_match = re.search(r'silk_state:\s*(\d+)', data_str)
        if silk_match:
            silk_state = int(silk_match.group(1))
        port1 = (silk_state >> 0) & 1 == 1
        port2 = (silk_state >> 1) & 1 == 1
        port3 = (silk_state >> 2) & 1 == 1
        port4 = (silk_state >> 3) & 1 == 1

        chan_match = re.search(r'chan:\s*(\d+)', data_str)
        if chan_match:
            chan = int(chan_match.group(1))

        insert_match = re.search(r'ffs_channels_insert:\s*(\d+)', data_str)
        if insert_match:
            insert = int(insert_match.group(1))
            insert = insert.bit_length()

        stall_match = re.search(r'stall_state:\s*(\d+)', data_str)
        if stall_match:
            stall = int(stall_match.group(1))

        with self.lock:
            self.Port1 = port1
            self.Port2 = port2
            self.Port3 = port3
            self.Port4 = port4
            self.State = state
            self.Chan = chan
            self.NeedInsert = insert != 0 and insert != self.Insert and state == STATUS_READY
            self.Insert = insert
            self.Stall = stall

    def get_stall(self):
        with self.lock:
            return self.Stall != 0

    def get_values(self):
        with self.lock:
            return {
                'State':  self.State,
                'Port1':  self.Port1,
                'Port2':  self.Port2,
                'Port3':  self.Port3,
                'Port4':  self.Port4,
                'Chan':   self.Chan,
                'Insert': self.Insert,
                'NeedInsert': self.NeedInsert,
                'Stall':  self.Stall
            }


def load_config(config):
    return zmod_ifs(config)
