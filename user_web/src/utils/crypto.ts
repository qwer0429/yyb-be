import CryptoJS from 'crypto-js'

// 加密密钥（应与后端保持一致）
const SECRET_KEY = import.meta.env.VITE_CRYPTO_KEY || 'yyb-secret-key-2024'

/**
 * AES 加密（与后端兼容的实现）
 * 使用 ECB 模式，Pkcs7 填充
 * @param text 要加密的文本
 * @returns 加密后的 base64 字符串
 */
export function encrypt(text: string): string {
  try {
    // 将密钥处理为 16 字节（128位）
    const key = CryptoJS.enc.Utf8.parse(SECRET_KEY.padEnd(16, '0').slice(0, 16))
    
    const encrypted = CryptoJS.AES.encrypt(text, key, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7,
      iv: CryptoJS.enc.Utf8.parse('') // ECB 模式不需要 IV
    })
    
    return encrypted.toString()
  } catch (error) {
    console.error('加密失败:', error)
    throw new Error('加密失败')
  }
}

/**
 * AES 解密
 * @param encryptedText 加密后的 base64 字符串
 * @returns 解密后的原文
 */
export function decrypt(encryptedText: string): string {
  try {
    const key = CryptoJS.enc.Utf8.parse(SECRET_KEY.padEnd(16, '0').slice(0, 16))
    
    const decrypted = CryptoJS.AES.decrypt(encryptedText, key, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7,
      iv: CryptoJS.enc.Utf8.parse('')
    })
    
    return decrypted.toString(CryptoJS.enc.Utf8)
  } catch (error) {
    console.error('解密失败:', error)
    throw new Error('解密失败')
  }
}

/**
 * 加密密码（用于登录/注册传输）
 * @param password 明文密码
 * @returns 加密后的密码
 */
export function encryptPassword(password: string): string {
  return encrypt(password)
}
