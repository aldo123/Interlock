import serial
import serial.tools.list_ports
import threading
import time
import json
import os


class RS232Reader:

    def __init__(self):

        self.ser = None
        self.running = False
        self.callback = None

        self.port = "COM1"
        self.baudrate = 9600
        self.bytesize = 8
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE

        self.json_file = None
        self.section = None
        self.last_connect_attempt = 0

    # =====================================================
    # LOAD CONFIG
    # =====================================================
    def load_config(
        self,
        json_file,
        section
    ):

        try:

            self.json_file = json_file
            self.section = section

            json_path = os.path.join(
                os.path.dirname(__file__),
                json_file
            )

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            config = data.get(
                section,
                {}
            )

            self.port = config.get(
                "COM Port",
                "COM1"
            )

            self.baudrate = int(
                config.get(
                    "Baud Rate",
                    "9600"
                )
            )

            self.bytesize = int(
                config.get(
                    "Data Bits",
                    "8"
                )
            )

            parity = str(
                config.get(
                    "Parity",
                    "None"
                )
            ).upper()

            parity_map = {
                "NONE": serial.PARITY_NONE,
                "EVEN": serial.PARITY_EVEN,
                "ODD": serial.PARITY_ODD,
                "MARK": serial.PARITY_MARK,
                "SPACE": serial.PARITY_SPACE
            }

            self.parity = parity_map.get(
                parity,
                serial.PARITY_NONE
            )

            stop_bits = str(
                config.get(
                    "Stop Bits",
                    "1"
                )
            )

            if stop_bits == "2":

                self.stopbits = serial.STOPBITS_TWO

            elif stop_bits == "1.5":

                self.stopbits = serial.STOPBITS_ONE_POINT_FIVE

            else:

                self.stopbits = serial.STOPBITS_ONE

            print(
                f"RS232 Loaded : "
                f"{self.port}, "
                f"{self.baudrate}, "
                f"{self.bytesize}, "
                f"{parity}, "
                f"{stop_bits}"
            )

            return True

        except Exception as e:

            print(
                "Load Config Error:",
                e
            )

            return False

    # =====================================================
    # AVAILABLE PORTS
    # =====================================================
    @staticmethod
    def get_available_ports():

        ports = []

        try:

            for port in serial.tools.list_ports.comports():

                ports.append(
                    port.device
                )

        except:
            pass

        return ports

    # =====================================================
    # PORT EXISTS
    # =====================================================
    def port_exists(self):

        try:

            for port in serial.tools.list_ports.comports():

                if port.device == self.port:

                    return True

            return False

        except:

            return False

    # =====================================================
    # CONNECT
    # =====================================================
    def connect(
        self,
        json_file=None,
        section=None
    ):

        if self.is_connected():

            return True

        try:

            if json_file and section:

                self.load_config(
                    json_file,
                    section
                )

            if not self.port_exists():

                print(
                    f"{self.port} not found"
                )

                return False

            if self.ser:

                try:
                    self.ser.close()
                except:
                    pass

                self.ser = None
            
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=0.2,
                write_timeout=0.2
            )

            print(
                f"Connected : {self.port}"
            )

            return True

        except Exception as e:

            try:

                if self.ser:

                    self.ser.close()

            except:
                pass

            self.ser = None

            print(
                "Connect Error:",
                e
            )

            return False

    # =====================================================
    # DISCONNECT
    # =====================================================
    def disconnect(self):

        self.running = False

        try:

            if (
                self.ser
                and
                self.ser.is_open
            ):
                self.ser.close()

        except:
            pass

        self.ser = None

    # =====================================================
    # SEND
    # =====================================================
    def send(
        self,
        data
    ):

        try:

            if (
                self.ser
                and
                self.ser.is_open
            ):

                if isinstance(
                    data,
                    str
                ):
                    data = data.encode()

                self.ser.write(data)

        except Exception as e:

            print(
                "Send Error:",
                e
            )

    # =====================================================
    # START LISTENER
    # =====================================================
    def start(
        self,
        callback=None
    ):

        self.callback = callback

        if not self.is_connected():

            return

        self.running = True

        threading.Thread(
            target=self._listen,
            daemon=True
        ).start()

    # =====================================================
    # LISTENER
    # =====================================================
    def _listen(self):

        buffer = ""

        while self.running:

            try:

                if (
                    self.ser
                    and
                    self.ser.in_waiting
                ):

                    char = self.ser.read(
                        1
                    ).decode(
                        errors="ignore"
                    )

                    if char in [
                        "\r",
                        "\n"
                    ]:

                        if buffer.strip():

                            data = buffer.strip()

                            if self.callback:

                                self.callback(
                                    data
                                )

                            buffer = ""

                    else:

                        buffer += char

                else:

                    time.sleep(
                        0.01
                    )

            except Exception as e:

                print(
                    "Read Error:",
                    e
                )

                self.disconnect()

                break

    # =====================================================
    # STATUS
    # =====================================================
    def is_connected(self):

        try:

            return (
                self.ser is not None
                and
                self.ser.is_open
            )

        except:

            return False
    
    

    # =====================================================
    # GET PORT
    # =====================================================
    def get_port(self):

        return self.port
    
    # =====================================================
    # PORT AVAILABLE
    # =====================================================
    def port_available(self):

        try:

            ports = serial.tools.list_ports.comports()

            for p in ports:

                if p.device == self.port:

                    return True

            return False

        except:

            return False


    # =====================================================
    # VALIDATE CONNECTION
    # =====================================================
    def validate_connection(self):

        try:

            if self.ser is None:
                return False

            if not self.ser.is_open:

                self.disconnect()
                return False

            if not self.port_available():

                print(
                    f"{self.port} removed"
                )

                self.disconnect()
                return False

            return True

        except Exception as e:

            print(
                "Validate Error:",
                e
            )

            self.disconnect()
            return False