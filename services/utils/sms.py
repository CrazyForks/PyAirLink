import logging

from smspdudecoder.fields import SMSDeliver
from smspdudecoder.codecs import UCS2
from smspdudecoder.elements import Number, TypeOfAddress


logger = logging.getLogger("PyAirLink")


def parse_pdu(pdu):
    """
    简单解析 PDU 格式短信
    """
    try:
        sms_data = SMSDeliver.decode(pdu)
        return sms_data
    except Exception as e:
        logger.error(f"PDU parsing failed: {e}")
        raise e


def encode_pdu(destination_number, message):
    if len(message) > 70:
        raise ValueError("Message too long")

    # 假设使用默认SMSC
    smsc_len = "00"

    # First Octet: SMS-SUBMIT，一般为0x11或0x01，如果是11需要做别的改动
    first_octet = "01"

    # TP-MR(消息参考号)，可用固定值或计数器
    tp_mr = "00"

    # TypeOfAddress编码
    toa = TypeOfAddress.encode({'ton': 'international', 'npi': 'isdn'})  # 若号码有+号则国际，否则可改'ton'

    # 编码号码
    # 先去掉+号
    dest_num = destination_number[1:] if destination_number.startswith('+') else destination_number
    encoded_number = Number.encode(dest_num)
    # 号码长度(十进制转两位十六进制)
    num_len = f"{len(dest_num):02X}"

    # TP-PID = 00（普通SMS）
    tp_pid = "00"

    # TP-DCS = 08 (UCS2编码)
    tp_dcs = "08"

    # 编码短信内容为UCS2
    ucs2_data = UCS2.encode(message)
    ucs2_len = f"{len(ucs2_data) // 2:02X}"

    # 拼接PDU：SMSC + FirstOctet + TP-MR + DA-Length + TOA + DA-Number + TP-PID + TP-DCS + TP-UDL + TP-UD
    pdu = (
            smsc_len +  # SMSC为空
            first_octet +
            tp_mr +
            num_len + toa + encoded_number +
            tp_pid + tp_dcs +
            ucs2_len + ucs2_data
    )

    # 计算AT+CMGS中的长度
    # 长度 = PDU的字节数(不包括SMSC长度字节本身)
    pdu_length = (len(pdu) // 2) - 1

    return pdu, pdu_length


if __name__ == "__main__":
    pass
