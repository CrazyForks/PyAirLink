class ATCommands:
    @staticmethod
    def _send(command):
        """Private method to format command with carriage return and newline, then encode."""
        return (command + "\r\n").encode()

    @staticmethod
    def base(command):
        """ . """
        return ATCommands._send(command)

    @staticmethod
    def at():
        """ AT test command. """
        return ATCommands._send("AT")

    @staticmethod
    def cpin(pin=None):
        """ Check PIN status or enter a PIN. """
        command = "AT+CPIN"
        if pin is not None:
            command += f"={pin}"
        elif pin is None:
            command += "?"
        return ATCommands._send(command)

    @staticmethod
    def cmgf(mode=0):
        """ Set SMS message format. Mode 0 for PDU mode, 1 for text mode. """
        return ATCommands._send(f"AT+CMGF={mode}")

    @staticmethod
    def cscs(charset='UCS2'):
        """ Set TE character set, e.g., "UCS2" or "GSM". """
        return ATCommands._send(f'AT+CSCS="{charset}"')

    @staticmethod
    def cnmi(mode=2, mt=2, bm=0, ds=0, bfr=0):
        """ New SMS message indications. """
        return ATCommands._send(f"AT+CNMI={mode},{mt},{bm},{ds},{bfr}")

    @staticmethod
    def cgatt(attach=None):
        """ GPRS Attach or Detach. Query or set the attachment status. """
        command = "AT+CGATT"
        if attach is not None:
            command += f"={attach}"
        else:
            command += "?"
        return ATCommands._send(command)

    @staticmethod
    def cmgs(to):
        """ Prepare for sending a message. The command must be followed by the PDU and Ctrl-Z. """
        return ATCommands._send(f"AT+CMGS={to}")

    @staticmethod
    def reset():
        """ restart module """
        return ATCommands._send(f"AT+RESET")


if __name__ == "__main__":
    # Example Usage:
    print(ATCommands.at())
    print(ATCommands.cpin())
    print(ATCommands.cmgf(0))
    print(ATCommands.cscs("UCS2"))
    print(ATCommands.cnmi(2, 2, 0, 0, 0))
    print(ATCommands.cgatt())
    print(ATCommands.cmgs("+1234567890"))
