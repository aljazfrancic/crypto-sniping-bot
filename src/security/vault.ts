import { encrypt, decrypt } from 'crypto-js';
import * as keytar from 'keytar';

const SERVICE_NAME = 'crypto-sniper';

export class CredentialVault {
  static async store(key: string, value: string): Promise<void> {
    const encrypted = encrypt(value, process.env.ENCRYPTION_KEY!).toString();
    await keytar.setPassword(SERVICE_NAME, key, encrypted);
  }

  static async retrieve(key: string): Promise<string | null> {
    const encrypted = await keytar.getPassword(SERVICE_NAME, key);
    if (!encrypted) return null;
    return decrypt(encrypted, process.env.ENCRYPTION_KEY!).toString(CryptoJS.enc.Utf8);
  }
}
