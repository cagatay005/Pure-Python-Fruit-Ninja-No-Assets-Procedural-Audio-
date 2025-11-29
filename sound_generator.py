import wave
import math
import struct
import random
import os

def create_sound(filename, duration, freq_start, freq_end, volume=0.5, noise=False):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1) 
        wav_file.setsampwidth(2) 
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            
            # Sesin sönümlenmesi (Fade out)
            envelope = 1.0 - (i / n_samples) 
            
            if noise:
                # Gürültü (Squish ve Boom için)
                value = random.uniform(-1, 1)
            else:
                # Ton değişimi (Throw ve Miss için)
                freq = freq_start + (freq_end - freq_start) * (i / n_samples)
                value = math.sin(2 * math.pi * freq * t)
            
            # Sesi genlikle çarp ve 16-bit tamsayıya çevir
            sample = int(value * volume * envelope * 32767)
            wav_file.writeframes(struct.pack('h', sample))
            
    print(f"{filename} oluşturuldu.")

# --- Sesleri Üret ---
print("Ses dosyaları oluşturuluyor...")

# 1. Throw (Fırlatma): İnceleşen bir "vıın" sesi
create_sound("throw.wav", duration=0.3, freq_start=400, freq_end=800, volume=0.3)

# 2. Squish (Kesme): Kısa bir gürültü (hışırtı)
create_sound("squish.wav", duration=0.2, freq_start=0, freq_end=0, volume=0.6, noise=True)

# 3. Boom (Bomba): Kalın ve uzun bir gürültü
create_sound("boom.wav", duration=0.8, freq_start=0, freq_end=0, volume=0.8, noise=True)

# 4. Miss (Kaçırma): Kalınlaşan üzgün bir ses
create_sound("miss.wav", duration=0.4, freq_start=300, freq_end=150, volume=0.4)

print("Tamamlandı! Şimdi oyununu çalıştırabilirsin.")
