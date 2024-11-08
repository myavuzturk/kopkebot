from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import logging

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7678768797:AAExapIItMRvFtYz-cX4SkL_86Cutfs29SE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Merhaba! IRIS Bot\'una hoş geldiniz!\n'
        'Tamamlanan talep sayısını öğrenmek için /aktif komutunu kullanabilirsiniz.'
    )

async def aktif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Talep sayısı kontrol ediliyor...")
    
    try:
        # Chrome ayarları
        chrome_options = Options()
        #chrome_options.add_argument('--headless')  # Arka planda çalışması için
        
        # Chrome'u başlat
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Login sayfasına git
            await update.message.reply_text("Login sayfasına giriliyor...")
            driver.get("https://iris.digiturk.com.tr/login")
            time.sleep(3)
            
            # Login işlemi
            await update.message.reply_text("Giriş yapılıyor...")
            bayi_kodu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "dealerCode"))
            )
            kullanici_kodu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "userCode"))
            )
            sifre = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            
            bayi_kodu.send_keys("67259814")
            kullanici_kodu.send_keys("ASLI")
            sifre.send_keys("25ASLI06")
            
            giris_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiButton-contained"))
            )
            giris_button.click()
            time.sleep(3)
            
            # Talep yönetimi sayfasına git
            await update.message.reply_text("Talep yönetimi sayfasına yönlendiriliyor...")
            driver.get("https://iris.digiturk.com.tr/main/RequisitionManagement")
            time.sleep(3)
            
            # Filtreleme işlemleri
            await update.message.reply_text("Filtreleme yapılıyor...")
            
            # Filtreleme dropdown'ını bul ve tıkla
            filtreleme_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "filterType"))
            )
            
            # Dropdown'ı aç
            filtreleme_button = driver.find_element(By.CSS_SELECTOR, "button[class*='MuiIconButton-root']")
            filtreleme_button.click()
            time.sleep(2)  # Dropdown'ın açılması için bekle
            
            # Tamamlananlar'ı seç
            filtreleme_input.clear()
            filtreleme_input.send_keys("Tamamlananlar")
            time.sleep(1)
            
            # Enter tuşuna bas (seçimi onaylamak için)
            filtreleme_input.send_keys(Keys.ENTER)
            time.sleep(1)
            
            # Listele butonuna tıkla
            await update.message.reply_text("Liste güncelleniyor...")
            listele_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "newIspBtn"))
            )
            listele_button.click()
            
            # İlk kayıt sayısını al
            try:
                ilk_kayit = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.MuiTypography-caption"))
                ).text
            except:
                ilk_kayit = "0"  # Eğer ilk kayıt bulunamazsa
            
            await update.message.reply_text("Filtreleme sonuçları bekleniyor...")
            
            # Kayıt sayısı değişene kadar bekle
            max_bekleme = 30  # maksimum 30 saniye bekle
            baslangic = time.time()
            
            while True:
                current_time = time.time()
                if current_time - baslangic > max_bekleme:
                    await update.message.reply_text("Filtreleme zaman aşımına uğradı, tekrar deneyin.")
                    raise TimeoutError("Filtreleme zaman aşımına uğradı")
                
                try:
                    # Güncel kayıt sayısını kontrol et
                    guncel_kayit = driver.find_element(By.CSS_SELECTOR, "span.MuiTypography-caption").text
                    
                    # Eğer kayıt sayısı değiştiyse ve geçerli bir değerse, filtreleme tamamlanmıştır
                    if guncel_kayit != ilk_kayit and "of" in guncel_kayit:
                        break
                except:
                    pass  # Element bulunamazsa devam et
                    
                time.sleep(1)  # 1 saniye bekle ve tekrar kontrol et
            
            # Yüklemenin tamamen bitmesi için biraz daha bekle
            time.sleep(2)
            
            # Toplam kayıt sayısını al
            await update.message.reply_text("Kayıt sayısı alınıyor...")
            kayit_sayisi = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.MuiTypography-caption"))
            ).text
            
            # "1-5 of 505" formatından sadece son sayıyı al
            toplam_sayi = kayit_sayisi.split("of")[-1].strip()
            await update.message.reply_text(f"Tamamlanan talep sayısı: {toplam_sayi}")
            
        finally:
            driver.quit()
            
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")
        if 'driver' in locals():
            driver.quit()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Exception while handling an update: {context.error}")
    if update:
        await update.message.reply_text("Bir hata oluştu, lütfen tekrar deneyin.")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Komut işleyicileri
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("aktif", aktif))
        
        # Hata işleyici
        application.add_error_handler(error_handler)
        
        print("Bot başlatılıyor...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"Bot başlatılırken hata oluştu: {e}")

if __name__ == '__main__':
    main()