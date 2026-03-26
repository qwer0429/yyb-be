from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import os

# 加密密钥（应与前端保持一致）
# 处理为 16 字节（128位）
SECRET_KEY_RAW = os.environ.get('CRYPTO_KEY', 'yyb-secret-key-2024')
SECRET_KEY = SECRET_KEY_RAW.ljust(16, '0')[:16].encode('utf-8')


def decrypt(encrypted_text: str) -> str:
    """
    AES 解密（与前端 CryptoJS 兼容）
    使用 ECB 模式，Pkcs7 填充
    :param encrypted_text: 加密后的 base64 字符串
    :return: 解密后的原文
    """
    try:
        # Base64 解码
        encrypted_bytes = base64.b64decode(encrypted_text)
        
        # 创建 AES 解密器（ECB 模式）
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
        
        # 解密并去除 Pkcs7 填充
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {str(e)}")
        raise ValueError("解密失败")


def decrypt_password(encrypted_password: str) -> str:
    """
    解密密码（用于登录/注册）
    :param encrypted_password: 加密后的密码
    :return: 明文密码
    """
    return decrypt(encrypted_password)
