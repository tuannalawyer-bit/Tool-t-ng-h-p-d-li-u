# -*- coding: utf-8 -*-
import sys, glob, extract_msg, asyncio, os, re
sys.stdout.reconfigure(encoding='utf-8')

files = glob.glob(r'D:\TĐMB\chay tool\*MB07930*.msg')
print('Found files:', len(files))

for f in files:
    msg = extract_msg.Message(f)
    print('\nFile:', f.split('\\')[-1][:80])
    print('Subject:', msg.subject)
    print('Attachments:')
    for a in msg.attachments:
        fn = a.longFilename or a.shortFilename or ''
        size = len(a.data) if a.data else 0
        print(f'  - {fn} ({size} bytes)')
        if fn.lower().endswith(('.png', '.jpg', '.jpeg')) and a.data:
            temp = os.path.join(r'D:\TĐMB\chay tool', '_temp_test_' + fn)
            with open(temp, 'wb') as out:
                out.write(a.data)

            async def do_ocr(path):
                from winrt.windows.media.ocr import OcrEngine
                from winrt.windows.graphics.imaging import BitmapDecoder
                from winrt.windows.storage import StorageFile
                from winrt.windows.globalization import Language
                try:
                    file = await StorageFile.get_file_from_path_async(path)
                    stream = await file.open_async(0)
                    decoder = await BitmapDecoder.create_async(stream)
                    bitmap = await decoder.get_software_bitmap_async()
                    lang = Language('vi')
                    if not OcrEngine.is_language_supported(lang):
                        lang = Language('en-US')
                    engine = OcrEngine.try_create_from_language(lang)
                    result = await engine.recognize_async(bitmap)
                    return result.text
                except Exception as e:
                    return f'ERROR: {e}'

            text = asyncio.run(do_ocr(temp))
            print(f'  OCR result: {repr(text)}')
            # Test regex matching
            flat = ' '.join(text.split())
            print(f'  OCR flat: {repr(flat)}')
            prices_strict = re.findall(r'(?<!\d)([1-9]\d{0,2}(?:[.,]\d{3}){2,})(?!\d)', flat)
            print(f'  Prices (strict): {prices_strict}')
            prices_loose = re.findall(r'(\d+[\s.,]\d{3}[\s.,]\d{3})', flat)
            print(f'  Prices (loose): {prices_loose}')
            try:
                os.remove(temp)
            except:
                pass
    msg.close()
