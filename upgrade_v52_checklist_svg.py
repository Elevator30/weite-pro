import re

with open('威特电梯厂检调试记录单v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取script里的JS
scripts = re.findall(r'(<script[^>]*>)(.*?)(</script>)', content, re.DOTALL)
js_start = content.find('<script')  # 第一个script标签位置

# 找到buildCheckItemsHTML函数的起始和结束
def find_function_end(js, start):
    """用大括号深度计算找到函数结束位置"""
    depth = 0
    found = False
    for i in range(start, len(js)):
        if js[i] == '{':
            depth += 1
            found = True
        elif js[i] == '}':
            depth -= 1
            if found and depth == 0:
                return i + 1
    return -1

# 在完整HTML中找到函数
func_start_marker = 'function buildCheckItemsHTML(task, project, dateStr, pageNum) {'
func_start = content.find(func_start_marker)
print(f'函数起始位置: {func_start}')

# 找到函数结束
js_part = content[func_start:]
func_end_rel = find_function_end(js_part, js_part.find('{'))
func_end = func_start + func_end_rel
print(f'函数结束位置: {func_end}')
print(f'函数长度: {func_end - func_start}')

# 新的buildCheckItemsHTML函数 - SVG底图方案
new_func = '''function buildCheckItemsHTML(task, project, dateStr, pageNum) {
  // SVG底图方案：每栏独立SVG底图 + 绝对定位文字
  // 分类标题横向排列（灰色背景行），序号全局连续，行高固定
  var logoBase64 = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAASABIAAD/4QCMRXhpZgAATU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAABIAAAAAQAAAEgAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAADragAwAEAAAAAQAABFkAAAAA/+0AOFBob3Rvc2hvcCAzLjAAOEJJTQQEAAAAAAAAOEJJTQQlAAAAAAAQ1B2M2Y8AsgTpgAmY7PhCfv/AABEIBFkOtgMBIgACEQEDEQH/xAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2wBDAAICAgICAgQCAgQGBAQEBggGBgYGCAoICAgICAoMCgoKCgoKDAwMDAwMDAwODg4ODg4QEBAQEBISEhISEhISEhL/2wBDAQMDAwUEBQgBAgTDQsNExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExP/3QAEAOz/2gAMAwEAAhEDEQA/AP38ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0P38ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAP/0f38ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACikzS0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFJjnNLQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAB0ooooAKKKKACiiigAooooAKKKKACiiigAoopOAKAFpAc0d6WgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKQ80tAB0o60UgyOKAFooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooo60AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUHigAooooAKKKKACikzgc0vWgAooooAKKKKACiiigAopM84paACikJxS0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRSEZFAC0UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUgz3paKAEOe1GecUtFABRRRQAUUdaKACiikJxQAvWimjj8adQAlAOaO9LQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAdaKKKACiiigBMYHFLRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB//0v38ooooAKKKKACiiigAooooAKKaTSg5ouAYwOKM84paTHOaAFopucUnPSlcB+aKbS44waYC0UnPFANAC0UUUAFFFFABSZBo5o4FAC0Ugx2pN1FwHUU3d6U2lcCSkOe1IOnPalGcc0wADFB6cUY70meOKAHZzRTT0pc8cUgFoopBTAOc0DpTe9O6UkAtFFFMAooooAKKKKADrRSE4FAOaAFoopmTigB2Oc0tNwetHPU0gHUUnSlpgFFITiloAKKKKACiik60ALRSHpQOnNAC0U3mlzQAtFITiloAKKKKACiiigAooooAKKKKACik570ue1ABRSZ5xQc9aAFopAc0tABRRSHPagBaKKTk+1AC0nTmlpM84oAWikNGcDmgBaKKKACkzzilpARQAo5ophPOaXcaVwHUUhPGRQPU0wFx3ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKQ8ClooATPGaWkzmjB9aAFopM0tABRRSZoAXrRRSHrQAtFFFABRRR1oAKKKKACikB4zQDmgBaKQnBpaACkxzmjmkwaQBz6Uoozxmkz1oAdRSd6WmAUZ7UUUAFFJjjFABoAWikGaWgAooooAKQ9aWm4JpMB1FJwKTPamA6img9qUUALRRRQAUgzjmlpMigBaKQHNLQAUUUmcjigBaKKKACiiigAooooAKKKKACiiigBO9LRTe3FADqQnAoyDR1FACcClBHQUgBBpBSAfRSEjpQOnFMBelFFICOgoAWiiigAopMiloAKKKKACiiigAooooAKOtIeBTckUrgOAxQfSm55p2RRcABpaaOlL0HNAC0nBoJxSd+KdwHUUgORS0AFFJnnFLQAUUUUAFFFFABRRRQAUUUUAFFFFABRSGl60AFFFFABRRTeRQA6ik/WloAKKKKACiiigAooooAKKKKACiiigApDjpS0UAFFFFABSZzS0gFAC9aKQmgevrQAtFFFABRRSHPagBaKKKACiik6UALRRRQAUUUUAFFFFABRRRQAhz2pCeeKdRQAmRSBvWg4OKBgZxSAdRSZ5xS0wDrTdozQevHegk0gHU3/AHaCMcigc8GgBc54NLR0opgFFFFACc0EUZ5xRnjNABzilppJp1ABRRRQAUUUgOaADPOKWkyOtLQAUUmecUA8ZoABnvSnjmkzzikyc4pXAdRSc9KWmAgzjmloooAKKKTtQAtFIORRjBoAWikxS0AFFFFABRR1ooAKKKKACik70EgUALRTSc9KXvQAtFID2NLQAUdKKZ35oAcMY4oGDzSE+lLSAWiiimAUUgz3paACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiigc0AFFFFABRRRQAUdaKKAEGe9LRRQAUUUhOKAFoppNIDilcB/SikyM4pDwc0XAdRTd1OpgFIM5paKACiiigAooooAKKKaeuKAF7Ue1IMnmlGe9IAHpS0hz2pCfxoAXI6UtNp2cUAGO9FJkUZBpgLRRRQAUUgPOKOnNAC038KA3rQR6UgF+tHNJznNL15pgLRSdBS0AFFIOOKWgAooooAKKjpe1K4DsGgUnHWlB4zTAWjPaiigAopDS0AFFFFABRRRQAUUh9KAKAFooooAKKTODSg5oAKKQHNLQAn0puSadQcd6TABnvRzmgdKQ8nFADqKKKYBRRRQAUUUUAFFITgUtABRRRQAUlLRQAhNB6ZFGOc0hHIFIBtL0IpTgdqQHBpAOwKQ8DFLRjNUAAcUtITgUc0ALRSdKWgAooooAKKKKACiiigAooooAKKKSgBaKKKACiiigAooooAKKKKACiiigApM84pCTmlHIpALRTSeKUZxzTAWiiigApO/NLSfWgBaKbzS5NAC0UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH//0/38ooooAKKKKACiiigApOlLQRmgBCMigDApaTPFAAeRRzS0mc0AJgUDrTqTHGKVgFooopgN+anUUUAFFFFABTTTqKADrSEc0tFADeO9HHNB4PNJ2JNIAGKD7UlLgetIBKUEikpe1CAUgmjoaBnFO6U7AFFFNPpTAMnjtS9aTr+FOpAJzmlo60UwDpRSZFLQAUU0E5waXIFFwFppznjtTqTr0oYBkHikzxxTaKVwHE8UmTQTQOtK4BnpTvrSYHWkxj2pgLnBFOpgOKduFABwRk0Z4zSE9qQk96LgOPI4ozmm5GOaSi4D+c0A54puec0ufzouAYGKdUdOB9aEwFJxSbqTrzS5FAAenNKTik6jIoAwMUAKCDS5xSEZpuOtAD6KTHQ0tMAopKWgAooooAKKKKAEAwaDmjvQM96ADHGKAMUvSkHNAATiloppJoAXPOKWkGcc0tABSYFLSE9qAAjvSds0oz3oIzSAOM8UZGcU0daXA60AOpCR0pDk9qUDAoAMAc0hAp1FMBB7UtFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFJS0AFFFFABRRRQAUhxjmlooAQdKU88Ugz3pM4GaQDqKbu9KdTAKTgigHNLQAmKWiigAoopD0oAWjpRRQA3B7Uoz3pcdqKAGk9qF60hGKMmkA+imrmlOccUwDrwaTB7UdqUZpAGOc0tFFMAopDnHFLQAhANNPXFPpv8XFJgKD2paaeDRnPAouA6imlvSkyelFwH0U3rzQc54ouA6kxkc0DB5paYCcflS0maWgBOc0c0tFADeTRtNLkYzS0rANAxzSjpzQc9qWgA603mgj0pRnvQAH1pvTig9aPekwHYFB6U3OKf1pgJx+dLSZxxS0wCiiigAooooAKKKKACiiigAooooAKTA6UtFACdRRjFLRQAzBFKDzg0cnrS0gE46mlB4petMwaAFHJyKUDFMpwJoQDqQdKWimAm0UtFFABRQeKKACiiigApM0tNx6UAL1pCAKXpS0AM7Gkp2M9KQjFSwEpefypRwOaTPNACkGloB7UtUgGg9qXnNJjmgDP4UgFxzmlpOe1LTAKKaD1NOoAKKTHOaWgBAc0tFFABRR0ooAKKKTnFAB3pcd6aPUU6gAooooATp1pMknApSM0YFIBOo+lKM0tNHAo2AdRSdaXpTAKKKQEGgBaKKTGOlAATzS0Y70mRQAtFFFABSDpS0UAFFFFABRRRQAUUUUAIRk0EgUtJgUAAz3paQZ70tABRRRQAUhOKWigAopDz0o6CgBaKTI6Uc0ALRRRQAUUUUAFFFHWgBuB070lLjHNHJ6UmAAjFOpoX1pegoARqMcZoBzSjpRuAhxwBRg0Cl6UALRRRTAKKKMZoATg80DjrS0mBQAdTmlo60UAFFFJnnFAATikHNAHbNLgdKQBjjFITzg0vIpD2oATrzSZpwowM4pAOpp64oyRxSk0wFopob1p1MAooooAKOtFFABRRRQAUUUUAFFFFABRRRQAhOBQTigjIoHSkAnU0pGaCBijGaADAoAxS0daYCY5zRj1paTHOaAFpp4FO60hGaAAY7UtIBij3NAC0mRQaZSbAkpOhoo69aYADmlz2oooAKKTHORRx+VAC0UUUAFHPaiigAooooAKKKKACiiigAooooAKKKKACikPSloAKKKKACiiigApOc0tFABRRRQAU089KdTDxwKTAXgDFNpwGaQjFIAPHPelJyKQjjNGCM0AA9afnNMBxSjoaaAXPNHUUA0E4FAC0U3JzinUwCikFHOaAFopCM0tABSZB4paTGKAFpo9KXPOKB1NABgdaXGaOM0daAG4ANLgUtHtSsAUnU5paKYCY5zQcY5oJxScmkAuBS0hI6Ue9MAzzilopAaADg8GlpDgUc4oAU0UmexpCM9KAHUUmBnNAJzQAhHej+QpDjtR0NIB+c0UzpQDii4D+lFMyaUZNFwHUgz3pOo5owaLgOooopgFFFFACEZoHAoPSm7h1NIB9HSkGO1KelMBMg8UhxjFNpD0qbgPOF5pc+tMxmii4D+vNJ25oycUDGcCmAg604jNIR0owcUeQDqKTNL1pgFFFFABRRSUAGAaTJzinUnekAE4paQjNIM/QUALnilpMg0tMBAQaCOc0tFABTcYpSM0HpSYB2paQDFGOMCmAY5zS0lLQAUUUUAIBiloooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooATI60d6MCloAKKKKACjrRTeelACikJ7Gg9hSdKQAOtOBzSDOOKUDFCAWiiimA0E5p1NBxSjkUgFooopgFFFFABRRRQAUUUUAFFFFABRRRQB/9T9/KKKKACiiigAooooAKTmlppJFACnpTR/KnA5puATgUgHDrS0gGKOc0AAoyBxQRmkwT1oAXrzmloopgFFFFABRRRQAUUUUAFIPfrS0hoATkU2nEkDmjOelSAmM0ck07vmlp2AZgmgjtTulL70WAaOopQQaWkwBQAuO9FFFMBMd6WijpQAdKQdOaTdSnkUgEA70ZNKM9KOPzoAbz+dLj1pvSnDI7UkA2lyRQetBB6mgBKKKKQC5oOO1AGaAPWmAoPGBQetIRg0uRjFPyAbRRR35qQFNBGBzS5oyKoBBjvQBmk96XOOBSASiiikAdKKXGc0ewpgJRRRSAKUZz60Z70ZNMBd1Gc5oODS9uKYCA+tLn1pnSilcB/FLTBxzTh600wA0AnoaWjpTAKbjBpcim8nmkwFHrS5HWm9sUYoAccd6QHmhaDigB3Smn60daCO9DAM9aBk0dT9KOgzQA6mYI5pdxozng0ALkYzQOeaMAUtMBgGaXB7U6m7vSlYA3etHOaTIzmnE4FAARmlpu6gEk0XAdRRRTAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACkyDS0dKACikAxS0AFNOOtOpuO9JgJjnFKe1L6ZoJxQAtJzRmm9TRcB3NLRSE4pgBzjilpMgUA8ZoAOnJo+lBPFN7UgFHJzS44xSdRSg5oAQD1pAM5pW9KAfWgAzign0oPNA4zQADNOpM8ZpN1ABk5xSk4petFMBMimk5oAJp23iluA0DNLgjmhT2pSBRYAxmm7TSjrinUbgMz2pKUjFJSAcOlJg0u6lBFMAHApaaeDmgN60XAdSZGcUuc01vWi4BupTjpTRjvS5yaLgKBignFAz3pCKAFyKCaQD1pcCjUBaBzRSEZ6UwEPrQPWk6mn0vMBpFJk9aXPJpc0AAx2paQDFLTAKKKKACiiigAooooAKKKKACiikJxQAtJnnFLSZFAC0UUUAFNHJzTqKADOKaORinUUAFFFFABRSEdqAe1AC0UmecUdKAFooozmgAoopMCgBaKT60tABQOaaMgU6gBpHpTacRnkUuBSsAgOBzRjPIpcCgADpQAuO9FFFMAooooAaRzkUdRihj2oWl1AUUHpRntS0wEGOlLSDFLQAUUUUAFFFFABTSe1OppBJpMBR0paavenU0AUU0jvS4Oc0ALSZOcUtJnPSgBCeKTmlIAGaTHGalgAOKXJPSk707HOaaATGeaXHrQeelAI6CgBaKQDmlpgFNIFOooAKKOlFABRRR1oAKKKKACiiigAoopOc0AGQDS0hweDRwOKAFpMc5paKACkGe9LRQAUUhOKAc0ALRRRQAUUdKKACiiigAooooAKQ+lLSAAUAAzS0UhGaADIxmlphGKM4pXAdjuKAD1NGPWlpgFFJkCk3UXAd1opu6nZzQAUUUhOKAAjNLSAg0uc0AFM707Ipp5PFJgPpD1FIKXHOaAG9aOaU4xijuCaADdSkUmACKUnFHqAgPrSgg0mRQQBQgFxzmm96cDmjHegBD1p1JnnFLTAKb+tA9Kd0oAaD606jHeigAooBzRQAUUUntQAtFHSigAooooAKKTPOKWgApPxpaKACikyKAc0ALRSUvWgAoopOc0AJyDikPt2pxB6ilpWAYc9TSjBpCc0q+tIBT7Um6nUw5zzTYC5yadTAcU4kChMAzzilpgz2p2McUIBaKKKYBRSHjmloAKKKKACiiigAooooAKBzRRQAUUUUAFFFFABRRSDkUALRRR0oAKKTGeaTGBQA6ikGaMk0AIeaXHGDQTilpANPHSjrzTqYRihgKRk8UmOcU7rzSAYHNFgAj0pfalop2AT2petFFACY4xS0UUAFIDmlpOBQAtFIDmgnAoADS0U0gk0AKcdaBnvQPegDFIBDkGnfSik6c0wDg8Ug5OadR0oAKKKKAEIzTcc4pd1AznNIBcCgkCkPBzRjPWgBQc0tNz2FBJFFwF4zS03OadTQBTBkcU/pSdeaAFo60UUAJgmm4xThTTnvSYCUUuKXbSsAAZFKBzmkGRTqYBjtSHjmlo60wCiiigAppPanUdaAGZPSl4I20N1pBxzSAXoM9qTORSUuec0XATAJo4PFKcdqbjuKWgD8A9KOAaZk4wOtAzj1pgOHSlzxSEYowaQDsimUvQ07kinuAgz0p1IOBzQeOaYC0UUh96ADpzS0naloAKQjNLRQAUdaKKAEwDzS0UUAFFFFACZFLTSM9KACKQDulNHJzTqbwDQwHUU0HJp1MAooooAKKKKACiiigAooooAKKKKACiiigAoopDntQAtFIB3NLQAUU3txS55waAFooooAKKKKACiiigAooooASloooAKTgUtNI70AL9KTJ6GhfSnUgE5paKKYCYGc0tFFACDPeloooAKKKKACiiigAooooAKKKKACiiigD//V/fyiiigAooooAKKKKACkNLSEZoAQ9PpSdDSkmm1LAeOlLTB1pRmmmAppaaetAIouA6ijIopgFFFFABRRRQAUUUUAFJwOaWkNAC0Ugz3paACiiigBOvWlpDwKWgAooooAKKKKACiiigBD6UY4xR3oxxigBGptSdaaV5pNAIBmlOaQdacT6UkA09afSdvSlpoBpBJo2ml5zR1FFgGY7UoOKKSp2AUnNJRRTAKKKKQD8CkIFKOnFMqmAoOKD1pOnNLzSASn4GMimg4oJ7CgBd1IRxkUlFFwCilwcZoIxQA0jvS0UZ70gFAzQRig5707PFNANHTNAGaM9hThjtTAMcYpAD1p1IeOaYC0nWgEGjOKADAFJjAwKOSaU57UgEPWgZHFABzRkigAOc02nZBoAzS3AAKU4xQTijHGKYB1FJt9Kd0op2AaBS4Gc0tFFgCiikIzQAtFFNJzgUAKBijANB6cUAYFIBNtOxikIzSAY5NADqKSlpgFFFFABRRRQAUUUUAFFFFACZGcUtIfWg5xxQAtFIM96U8c0AFFFFACGgHtS0UAFIeeKWigBMdqDzxS0Z7UAIM96XrRRQAnagcClooATtS0UgOaADAoxS0UAIBiloooAb9aMHrTqKVgEwKCM0Zx1oBzTAMAUtIM96buNAC5B4pcA0gPakJNIBcelJ0PNHNKeRQA6kyKB0oAxTACB1NA9qDjHNAI6UgADAoyOlJkg802i4DmPam07qKAOeaQDaKXHOKX7vNABjNGOKMk0opgGAOaXOKQ57UYFMBCM80LQOpox3FIB1JuFJhqUDFACbvWndaKKYBSZApaTAoAAQaDx0pOBSikAYzyaQjBzTqKYBRRRQAUUUUAFFFFABRRRQAUU3+KndaAENAPGaWm7eaAHUUUUAFFFFACYApaKKACiiigApMc5paKACmkHrTqKAEzjrQDRS0AFFFFABRRRQAUUUUAJkGlpAMGloAKKKKAEJxQKWigAopAe1LQAgpaKKAExzmkxinUUWAacAYpe2aWkPA4pAIDgUppN1LwRQAA5FLRRTAKKKKAGnjpSZNJThUgGTmjdQTzkUDnNMA3U6m4Ap1CAQ5xxSAEGlGO1LQAh6UYFLnFFMBCOOKWmk0AmlcBBwaCADSUoGaQD6KbgCgD1p3AdRRRTAKKKKACiiigAooooAKKKKACmnqKdRQAYzRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRSZGcUALRRRQAUUUUAFFFFADQQeDRt9KXHOaWlYBhGKBjvS5HcUhpAAGaM0me9FADuMUuOKaOhpRnHNNAGfWjgnFIDil46ikAhGKXHQikJzQDii4C4HejjjFJS4waYDqTp0ppz3oBIouAdTzS9DxQG9aQmkAYNIBmlzxikoYC/SlHSm049OKAA+1OooqgEzziloooATvS9aKKACiiigBO1IMnrSZ5zS/w0gHdKKaOtOpoAo60U0ZNADqKKQjIoAWikBzS0AJgGloooAQDFLRTQcHBoAdRSHkUtABRRRQAUUUUANIzQBxg06ilYApOo5oxnrScjpQAdOlJ9aAec0HFIBx4HFA6UnLUA+tMB1Jn1pOc806mAUU3oc0vXmgBaKKKACiiigAooooAKQjvS0UAJk0A5paTgUAAz3o5zSMO9KD2pALRRSYwOKYC0UgPOKM84oAXpRRRQAUUU3GTk0AOpMd6MAUtABRRRQAUUUUAFFFFABRRRQAUUUUAFMPWn0hGaTAb24pQTnFLjtSbaAA80ooAApaAG55pc5FGBnNLTAQDFLRRQAmecUtN/ip1ABRRRQA0D1p1J9aWgAooooAjop5x3phOakBwGOTTqTOMUtUAUUUUAFFFFABSGlooATtQOBS0UAFFFFABRRSEZFAC0UgpPmoAXOKWiigBuMZzSdTzTj0pmMUgDrRSg4pOtIApRz1oApKAFwO9L24ptLk0IB2O5paZk04Z700wDApaKTtxTAWk7cUnIoxxmkA6ikByKOc0wFooooAKKKKACiiigBAMUtJmgUALRSE4oGe9ACDg806m7vSlFJABz2oxnrS9aTPNMBaOlFJnnFAC0UUUAFFFFABRSHOOKQdAaAHUUHmkBzQAtN706igAopD1paACiiigAooooATvR15pelN3UXAcOaTIpN1LweaAFooooAKKKKACiiigAooooAKbjnFOpOD+NAC0UgGKWgAooooAKKKKACkNLRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/1v38ooooAKKKKACiiigAooooAac4oPIyKdRQBHTx0pMUdDS2AdTSKTPejJNFwFA706kJxSbvWjYA3etOpPwpaaAKKKKACijPaigAoopDwKAFpDntTcmn5FIBBkdaD0oOO9IeenagABzwaBkHFICRS5oAd0opAc0tMAooooAKKKQ8HigAxzmlpMetLQAUmRnFLTQM8mgAyM0bqNvpRgDrS1AXINJzuo206gApM4o57Uh5NAC8GmkDtT6bjANDAbRS80Ac0gADNBGKU8HNKenFOwDRnrRjNGTRmkAlPFHQU0HFPYAGO9GeMUlFK4BS59KSlAzQAZNGc0lFABRRRSAXJ54pdxpvSnbvWmA2ngYFGB1oyKaAWim5zxSYNFwHYFBGaQAilGe9ABx0oJxS9KbjmgB3bmiiimAm0UAYpaTIoATPrR6U4HNIcDmkAtFFFMBMgUtJ3paACiijIoAKKKKACiiigAooooAKKKKADrRRRQAUUnejmgBaKTIHFLQAUUUgoAWiikI5zQAtHWgcUUAHWikxzmloAKKKOlABRRRQAUdaQZ70tAB0ooooAKKKKAENKBiiigBMAUtFB5oAKTIpaQjIoAWjpTQccGlJ4zQAtJkDimg44pcg0rgKOlHAoGO1GAaAFpMijj8qX3pgFGcUUYzQAmRS0m0UYFACE54oA70o6c0tKwCdaTg06kwDTAOg5pc96Q9KAc0AJn0oPBzS4FHPFKwC0mcUvSk9qYC9aTpgCjpxS0AFJzmlooAKKKOlACZGcUZ5xSYyaAKQB97rTulJz1paYDSCaUdKCM0h7UgHUhOKTJ6UvBouAtFJjnNLTAKKKKACiiigAooprUALweaWk6UtABRRRQAneloooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigApCaWkIzQAA5paKQDFAC0Z70UmBQAtFJgUYFAC0UnApaACkxkU3Jp3OaQC0hpaQmmAtJ3xSc9KTknilcB20UgOODQDzSnGKADOaWm5weKXIoAWiikAxTATHpSjHakOc4FKBil1ATGeRTulFFMBDyKQ4AxTqaQSaTAToaUHk0pGaQcc0AL3paQ/Sk3U7gOpCOKO3FNyaVwFB7UnINGDRmkAuTSgikz60DBpgOopoyDzTqYBSZGcUvWk4IoAWikwBzS0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUY70UAFFFFABRRRQAUUU0+tADqKbkmjmlcBRnNLRRTAaTTacVpOfyqWAD1pKKKAHAgU6m5Ap3WqQCEZpMU6kOKTAaBmlwKQDNJ2zSAcMijJoGelGDTATJox3oIxQOaQCUoGTQetGec0ABHPFO4HFNzzmn00AhHpQB3paaAQaAHHpSDpzR14oPFMBaKOtFABRRRQAUUUUABGaTpwKCcUtACbRSHkUpzS0rAN5pTgClopgJkdKWmDjrRk0rgOwBzS9abk0oz3oAWikwDS9KYBRRRQAUUUUAFFFNyR1oAXp70tFFABRRRQAU04FOpMCgAxxim4NKcilHIpAICOlHDUg5NP6UIBMjOKM+lIRS4AoAWiiimAUY70UUAJS0UdKACkJ5paaBQAuecUAYpaTIoAWkyKMil6UAMpRjtS5BowBSAWiikPFMAxzmlpoPrTqEAUYzRRQAUmOc0tFABRRRQAUUUUAFFFFABSZNLSZ5xQAtFJ3oJxQAtFJ1paACiiigBu30pRyKXntRQAUmAeaXpRQAUdaKKACikHU0UALRRnNFABRRRQAUUmRS0AFFFFABjNJgYxS0UAFIDxSbqAM8mlcB1FFFMAooooAKKKKACiiigA60nTmlooAO3FNOcUoGKCR3pAA6UEUZ4yKaDzQAoBp1NPBzQCSaAF74pGPajpk0Yz0oAQY707GBTe9OyKEA0EignNKcCk4xSASilPXikoAUetKCAKb70uCaAHAg0tNxjmndaoAppOKdSYFAC0mRnFJjqKNtIBxOKTIpMHpRt9aNQFyDS0m0UAYpgLTSaKXPOKQCEc0nenZ7UAYosAhxS5AFBGaZ1oAKdjsO1AFGMUrAAGDTqbk06mgCikJ7Ckye9O4DqQ0hyeKU8ikAtITikBzxTqYCDNIc5yKdTc460gDJoznpSg5pM5PFAC5NLTTk0vNMBP4qUnFGB1paQBRRRTAKKKKACiiigBCMikBPpTqKACiikJxQAtFIDkUtABRR0ooAKKKKAEIzS0UUAFFFFABRRRQAUhOKWigAooooAKKKKACiiigAooooAKKKKACiiigD/9f9/KKKKACiiigAooooAKKKKACjrRRQA35elKORSY9KOR1pAOx2po9qdSEjoaYDSc0D1p2BRyBgUgFooopgFFFFACYBo9qM9qAMUALRRRQAnHSkwM4p1MzikwA9acMdqbz+dA60AKAM06mkZ6UuOMUALSDjrQM96WmAUUUUAFFFFABRRRQAUUUmaAEJINHXrS0tIBu2l6Uc5paAEGaWiimAhz1oz60tNYd6AHUUUdaAEIyKaMninZ5xSdOlJgLgdKTbRk0uRRoA3HOKSlI5pQAetIBBjvTsDpTcc4owRzTAPekpSMUlIApeo+lJQDg0AFFKevFBxnigAAzS7abUnWhAM+tO2im/pQCaEAuB3oGT7UuMjmlpoBOnFLSEZoFMBcd6Tml60UAJzmloo60AITim9eadjnNJikADilPXFIcH6UuO9AAKWkGMcUvSmAUUUUAFFFFABRRRQAUUdaKACiiigAooooAKKKTNAC0HiiigBDntSniikPSgABzScjmkAPWnH0pALRSAYpaYBRSc54paACikHpS0AFFFFABRRRQAUUUUAFFFFAAOaKKKAEOe1LRRQAUUhz2paACkJwaWkPHNADSc0c0fhRzUgH4UlL60nSgAp2SaAvrQOKAEBNOBzS0U7AFFGO9FMAoopCKAFooooAKKKKACmnjmnUdaACm89TSnHU0yk2BJSd80YpaYCZ4zQDmjIPFAGKQBjnNLRTW9aYCgYpaQcDFBFACEUoz3paKVgE60H1paKYDOTQTz0p2BSMO9IBATSjgUg68U4AfnQgFoopuSDTAdRRSDPegBaKKKACmkU6igBMcYpelJjHNGcGkAtFFFMBByOaWiigAooooAKKTHOaQEmgBQc0tJ25paACiiigAooooAKKKKACiiigAooooAKKKOlABRRRQAUmaWkBoAWiiigBDjNLSdaOoxQAtFFFACE4FJjvTqKLANOaAad1pOtADepp2BS4xRSsA3bS4FLRTsAgx2paKKAExzmg9KWjrQA0deKXoOaQDvRk9OtIBMmlye1JzTwc0AIM45paKKYBRRSE4oAMUtHWkJNAAc44pMClBzQRml5gIRxgUgzS4A96TAoAUE5paTuKdQAmRS03jpTqYBRRRQAUUUUAFFFFABRRRQAgzjmloooAKKKKACiiigAooooAKKKKACiiigAooooAKKOlFABTCT3p2QeKAMCkwF6UUmcUE8ZpgLRRRQA0k0DJFOopAMIwKUAdaM9qUCgBuOM0oFOoosAUm0UtFMBMdxS0UUANJwaM4FGD1NLjjmkA3Jo5FBGKSkAuOM0AZpRjHNL9aLAJkDpTqaKU46VSAXpRRRQAUhpaKACiiigAooooAKTNLRQAUUUUAFFFIc44oAWiiigBh5NJTtvpRjtU2Ab0pQcmge9OGOooSAM84paTvS1QBRRRQAUUUUAFFFFABRSY5zR+tAC0UmeMiloAKKKKADrR0opCOMUALRSAYpaACiiigAooooAKKKKACiiigAooooAKTgCjaKXrQA3bQeTQeOKdSAQDFIexpSecUYzQAdqbkmn0UAJgUtIRmlpgFFIDmloAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAQDFLR0ooAKKKKAEIzS9KBxSE4oAWim4B6U6gA6UmeM0HPagZ70gGgZ60+iimAUYxSZpQc0AFFN7inUAFFFFABRR7UUAFJwaXPakyM4oAMYFBANIT6U6kAgHGKXGKTI6UhJoADmkAzR1pQMHNLcBScU3Jpx5FNxg802AAZowaMmgHFIAFGOcUc04HIosAY5zSbuKBSH1PWmAoOTTqaMUpPHFCAXrRSDpS0wAHNFIMdqWgA6UU0iloAMc5paKKACiiigA60gGDSHnpRnGKQCnjml603qaXFABmkB5pQAKMCgAGOopaaOtOpgIeOaWiigBvYE0uQeKDnHFIADSAORR70uBSEUAA9aN1IOaMGkAZINL25pcEdKTNMBtLjvTj0oAwKLALSA5pOadTAQdOaBilpoHrQA6k7etIQSad0oAKKKKACiiigAooooAKKKKACiiigAoopMUALRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAf/Q/fyiiigAooooAKKKKACiikzzigBaKKKACjrRRQAUhwOaWk6UAJTsCkGO1NOc0tgH9KKZk04HNFwFpoJzg0oOaQg5oYCmjNBGabg0APopB0paYCGkA9adRRYBpb0oUd6d1pAMUrALRRRTAKKKKACiiigAooooATPOKWiigAooooAMd6Q57UtFACUtFFABRSZFLQAUhz2petFABRSdRSA84NFwFzS0Y70UAFNIxzTutN20mA2nDvSgYo9xQkAzrTlHekNOXpSQCbvWm9acR3pAM0PsAlFKBmg4HFACUUv1oAzQAq06jpSYPrVANOafSYHWjOKQAelLTRgDnvSjHagBaKTPOKBnvTAWiiigAooooAKMd6KKACikOe1LQAUUUUAFFFFABRRRQAUUUUAFFJzR1oAM5paTFLQAhGaWm7qAc0rgOpOBzS0daYB1ooooAKbjmnU0jvQwA5zijFG6gjPIpAOpMcU3JzindBzRcA+tGMDigHIoJwKAEDetLmm47UoGDQgFyfSloopgFN5PQ06mjpxQAoGKWm/NSk4pALRSdRxTck8UwH0UgGKWgApDwKWigBoPrSn2pDwOKXIpAJgnrTaXcadwaW4CDpSZNL04o20wEPpRg0/pRRYBBnvS0UUwCmYNPoosAdKKKKAE5paaM55p1ACE4paKKACiiigAooooAbupB1p2BTeO1IBe3HNG6kPHFHJ5pXAB1pOlFOAoAUHNIT2pScUmPWmAmTThnvS0Z7UwCiiigAooooAKKKKAGdDS9cClJ9Kbk9aWwD6KM96QHNMBcd6KKKACiiigAooooAaetLjnNLRRYAo6UZxSbhQAtJ1FJupQc0XAWijrSZFABnHFIRjkUEd6QcmkwF5oBp1FFgCiijOKYCDPelpAQaM9qAFoopAc0ALRR0pp55oAGpQcikxj3p3SkAUUUUwG4zzTqQntRnHWkADPelopDTAWio+tSDpSTAKT2paQ9RTAAAKCcUucU3cM0gFyfSlpAcilpgFIelFB6UAJzmnUg96XpQgGnJNOppOad1pIAooopgFFFFADSMmlpaQc0AHFIODSDPan0twCiiimAUhHNLRQAUgpaKACkAxS0UAFJmlooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKTApaKACkJxS0daAE69aCOMUtFACdBxSc/jTqOlABSc96WigAooooAKKKKACkxS0UAMIxSVJ1pu01NgG04AEU2njPehANIwaSnkjoaMCnYBlP9SKBjtS0JAJkGlpMClpgIM96WiigApM84ozk4paACiimnrigBRjoKToeKTBApQOKQC54yaWk7UZGcUwFppPAoPWkIGMikwFBNKelJjHNA6UIBQOMUY5oHApaYBSGgnApAT3pAOo9qKKYBRRRQAUU0k5xS9RQAtHWikIyKAFooooAbzmjJ706k4pAAOaMignFJgHpQAZzxTqQACk20AOopu2l6ZNMBaKaCaXPOKAF60gGKWigAz2ooooAKKTGeaAMUALRSE80tADdtGDTqQUrALRRRjNMApOc0tFADfmpeaWigBMilpMCl60AGe1FJjnNLQAUUUUAFFFFABRRRQAhNLRRQAUUUUAFFFHWgAooooAKKKKACiikJAoAWimk4o3UXAdRRnNIaAFooooAKKKTmgAB7GlpvQ56U6hAIPWjGaWigBPoaWiigBCM0c4paKAG4JpOcU4nFNNJgGTT6ap7UFvSgB1FHWimAgz3paCM0nOaACgDFLRQAmBRn1paKAEA7mgnFBOKMjpQA0nNBpTjNOwKVgGdqSlNAx3pAJSk5oz0pKAFPQUu30pCO4p3amAgyTmlJxSZNOxmgBMcUm30pegoHIoAMUAYpaKYBR0oooATrzS0UnU0ALRRRQAUUUUAJxS9aKbxQAoGKM0EA0AAUgEpMelOIzS0WAQCjrS0nTJpgL0ooooAKKKSgBMHFGCaXPalpAMOAKUE0h60q+lCAdTOacTim5yaGAucilApOMUoI6CgAAxQRmlpMjOKYC0UdaKACiikzzigBaKKKACiiigAooooAKKKKACiiigAoo6UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB/9H9/KKKKACiiigAooooAKTHOaWigApBnvS0UAFIM0gyTTqACkz2oJxR70ALSEelAOaWgBMcYpvTinE4pMZ5pMBaWiimAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRSZFL1oATHOaO9IaBg9aQC8EUE4FIF9aUjNAB14oAApelIDmmAhz2oGadRSsAU3dQT2oyB0oACMjjvSAGl3UuRRoAgApScClpp4OaAEJzRnFJR0pALk0lKcnmgHFACClIxQcUuMmgBM8Yp2RSbRRt9KeoCk033pQvrTsdqAG4GKUDFI2cUg5PNAC455p2O9FFMAoopO9ABjnNLSCloAKKKKACiiigAooooAKKKKACiiigA60UUUAFFFFABRSDPeloAaR6UoGKWigAooooAKBxRRntQAzJp2aWikAmBSbfWnUhz2oAQg5yKXGRQM45paAGnFKTxQABQQKAG9aUcHBpcDOaCM0WAXpTcg0dOB1p1MBuOKbTifSkzzmpYDsn0pMmnUVQDc9qXIpPqKMZpALkUZoAxS0wEpaKKACmse1OooAYMY5o5HNPphGKTAOpGafTQARSkZoQDeSaXn1o20hpALt9aUDFA6UtOwBRRRTAKaR6U6kPWkwEAxml57UtFMApMc5paQZ70ALRSHNLQA3FIOafSZPpSsAmBTMUtFIA96KUdaSgBSOaTpThnOadTsAzk07mgnFLQAnNLRRTAKKKTPagBetFFFABRRRQAUmRnFLSYBoAMDOaWiigAooooAKKKKACiiigAooooAQ9KZUlJik0AynL60vXrS0JAFJgUtFMAooooAKKKKACjGaKKAEyBQDmjjNLQAmecUZwcUhwelIBzSAf1oo6UUwEz60tFFADD1pw6UhB60Ke1LqAvA5ppOTTiM0zGKGAoJ7UE80lPzSAbg0vzUZxS55xTATHrSEYp9Nx60WAQkmgDNOwKaRikAo44oOM0mCeaMGgBeRxS5BpAfWhaYBk0Z9aUEGk2+lAC4BGKAMUAYpaYCDFLRRQAUUUUAIc9qM9jS0YzQA09eOtL04owKCKQC0UnTrS0wCiiigAooooAKKKTPrQAtFFFABSE4paKACkOe1LRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAdKB0oooAKT3paCM0AFFNJINKaVwFpBS5ppPpTAdSZzQDmloAKKKQnFAC0UUUAFFFFABRRRQAUUUUAFFFFABRRRQAUhBpaQHIoATGOaUHNL1o6UANxk5oxxg06k570rAIF9aXFKOeaKdgCiiigApDwOKWmliO1AARxRupeopaQBSUtFMBCcUmfSnU3AHNIBP0o4/GlGDR0pAAwOtGR2pCMUAE0ALupSQKQAg0p4FMABzSjnmmg9qXJzigAPShelLRTAQH1pabweRTqAEPSgEGlpMZFAC0U3BHSjb60gHUnOaAMUGmAmTTqQZ70tABTcD1ozzSkA0twDApelFFMApuDnNOooAKKKKACiiigBDwKTcadScDmkAA5paTIFB6UwDI6UtMwaXODikAhz3pQKXApaLAJnsaWk680tMAooooAKKKKACkBpaKAEzS9aKOlAB0o603Pel3ClcBaQ57UDPelpgFFFFABRRRQAUUUUAFIM96WigAo6UUUAFFFFABRRRQAU08HNOooAQetLTc4NL1FIAx6UtN56U7pQgEBzS0gx2paYCZoFLRQAUgGKCM0tABRRRQAUUUUAIQaBwOaWkPPFADTweKcDmk20uBSAbgilA5p1N9zRYAHU0pOKWimAUUgzmloAKKKKACiiigBCM0HPalooAZyacOlLRSsAw9eKMGlIxyKTikAnSlwcZpSMc02gB2expc0ynjpTTAWkIzS0UwCikAxRj1oAWkHvS0UAFFJmgHIoAWik680tABRRRQAUUUUAIRmk2+lOoosAzBpdvpRk9KdnNIBqntTqKKYBRRRQAUUUUAFIcd6WigBoGDTqQDFAOaAA4PFGM80hx1oxxikAZOcUpHFHOaWgBgHNKR6Uox2paLAN5x60EcUfxUpOKAEX9adSZ4zQM45pgA44pDnOadSDPegBMmjJpT0oxikAY5zS0UUwDpRRRQAUUUUAFFFFABRRRQAUUUUAAGO9FHSigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/0v38ooooAKKKKACiiigAooooAKOlFFADd1KCKBijGaQCdead1opM8ZNMBaKQHNITzRcAI9KdTetOpAFFFFMAopM84paACkzSHnigdaQDqKKKYBRRRQAUUUUAFFFFABRRRntQAUUUUAFFHSjrQAUUUUAFFFFACDrR06UAYpaAEppGBSse1JmkwHDPelpmTnNPoQBRTWo5NFwHUUUUwCiiigBMCk/ipSQKBzzSAOp+lNPWnHA5pvJoYCUUuOnvSUgCnZGabSgZoAOnvS9TxTaKLgOIyaQjFJS5J4oAfRTQKdVAFJgUtIDmgAIzS0UUAFFGe9JkUALRSZFGecUALRRSA5FAC0UUUAFFFFABRRRQAhpAccGnUmB1pALRRSHOOKYC0UgOaWgBCO9ABFAJ9KMikAtFHWimAUUUUAFFIRmloAKKKKACiikyKAFpM84pCSKXrzQAtFHSigApuD1p1NJ7UmAhFG00Z4xSk4NLQBtOWkznrSUASZ7U0ntQM0uBTABjtQTzijIHFAwaAFooopgFFFFABRRRQAUUUmKAA9KQHHBoAIp3WkAmQaZTwAKZSYBTskc0hxnil4xxQAo6UvWmgZ5NO6U0AU3JA5p1FMApCcUtIRmgA6jijmk+70pcikAtNwR0o3UbqLgNpwo3UA4pAANIetKTmkGO9AATxilwMZo4FOpoAzmikAxQeRTAWigdKKACkPIpaTINAC80UUmAaAFooooAKKQ0tABRRRQAUUUUAFFFIDxk0ALSDPelooAKKKKACiiigAopCQKMg0ANxzinY4xS0UrANGadRRTAKKQnFLQAUdKaTzR14NK4C5BpaKMimAUUUUAJgUHgUA8Zo46UgEDetOpMA0mDQA6iiimAUh9qDntS0ANWnUUUANIzRtpT7UY9aVgEAyKTBo5FKMnmgBRnvSEHORSHIpwz3oAbk0ck0+iiwDBwaD6inEDqaTIxiiwCE5o5FKMCl680WAQUpOKCcUdRQADJpabkijvk0XAdRRRTAKKQnFLntQAUdKKKAEzmloooAKZyDTj0pOtIB1FISBRnNMBaKQHNLQAUUmecUtABRRRQAUUUUAFFFFABRRRQAUUUUAFFFRSSJEhlkICqMkn2oASWSOFDJKwVV6knH61zWn+NvBurXrabpWq2lxcqcGKOZGcEf7IJP6V+L/7bP7X2r+MteufhV8ObprfSLRjHeXEZ+adxwUUjkKD1I61+a+n3d/o99Hqmi3MtrdQvuSWN2DAg5ByD614WKzyFGfJBXP2Ph7wdx2Z4JY2tUVNyV4prV+p/XnRX58fsRftYH4z6K3gTxxKq+JdNTO4nH2mIYAcD+8P4gPrX6D162HxEK8FUpvQ/Ls3ynEZVip4HGRtKL/phRRRW55oUUUUAFFHSigAooooAQjNNwafRSsAzoKcDkUHGOaTrjFACnkUvSiimA0jPXpS4BFLSUAN5Bp9JgUvSkgCiiimAUUUUAFFFFABRRRQAUU3dTqAEPSkWnUUAFFFJigBaKKKACikOe1L0oAKKaCSadQAUUUUAFFFFABRRRQAUU05zxTqAAcUUZxRQADnmiimE5pbAOyKOtJtoyB0oAQ5oxmgnJowTSAcRmgDjFGOMU3OKYC5FBb0owDzRgUAKDmlpBjtS0wG5Bp1JkDiloAOtR0/cKXIpWAOtIDmlopgFFGRRQAUU1qBk0XAXvS0mDS0AIT2paTntRkZxQAtFIKWgAooooAKKKKACiiigBpHem9akPSo8YqWA4GjIzmkHJpePWmAuRSZNLkUA5oABjtQTjikByadTAb3zTqKKACiiigAooooAKKQ0EZoAWikwfWgZ70ALTf4qdRQAUUUUAFFFFABRRRQAUUUgz3oAWiii';

  function escHtml(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // id->item映射
  var itemMap = {};
  if (typeof checkItems !== 'undefined') {
    checkItems.forEach(function(it) { itemMap[it.id] = it; });
  }
  var hiddenIds = (typeof hiddenCheckIds !== 'undefined') ? hiddenCheckIds : [];
  function isVisible(id) { return hiddenIds.indexOf(id) === -1; }

  // 获取结论显示
  function getResult(id) {
    var val = task.checkResults ? task.checkResults[id] : '';
    if (val === undefined || val === null || val === '') return '';
    if (val === '符合' || val === '√') return '√';
    if (val === '不符合' || val === '×') return '×';
    if (val === '不适用' || val === '/') return '/';
    return val;
  }

  // 配置
  var rowH = 16;          // 数据行行高
  var titleH = 20;        // 分类标题行高
  var headerH = 18;       // 表头行高
  var seqW = 22;          // 序号列宽
  var resultW = 28;       // 结论列宽
  var contentW = 0;       // 检查内容列宽（动态计算）
  var fontSize = 8;       // 正文字号
  var titleFontSize = 8;  // 标题字号

  // 生成范围ID数组
  function rangeIds(start, end) {
    var a = [];
    for (var i = start; i <= end; i++) a.push(i);
    return a;
  }

  // 生成一栏的SVG底图 + 文字层
  function buildColumnSvg(groups, colWidth) {
    contentW = colWidth - seqW - resultW;
    
    // 计算所有可见项，确定总高度
    var allItems = [];
    var groupInfos = []; // 每个分类的起始行索引和结束行索引
    var totalDataRows = 0;
    
    for (var g = 0; g < groups.length; g++) {
      var grp = groups[g];
      var startIdx = allItems.length;
      for (var i = 0; i < grp.ids.length; i++) {
        if (isVisible(grp.ids[i])) {
          allItems.push({id: grp.ids[i], groupIdx: g});
        }
      }
      groupInfos.push({
        label: grp.label,
        special: grp.special,
        startIdx: startIdx,
        count: allItems.length - startIdx
      });
    }
    
    // 计算总高度
    var totalH = 0;
    var rowY = []; // 每行的y坐标（数据行顶部）
    var groupY = []; // 每个分类标题的y坐标
    
    for (var g = 0; g < groupInfos.length; g++) {
      var gi = groupInfos[g];
      groupY.push(totalH);
      totalH += titleH;  // 分类标题行
      totalH += headerH; // 表头行（序|检查内容|结论）
      
      for (var r = 0; r < gi.count; r++) {
        rowY.push(totalH);
        totalH += rowH;
      }
    }
    
    var totalW = colWidth;
    
    // 生成SVG底图
    var svg = '<svg width="' + totalW + '" height="' + totalH + '" xmlns="http://www.w3.org/2000/svg" style="display:block;">';
    
    // 外框
    svg += '<rect x="0.5" y="0.5" width="' + (totalW-1) + '" height="' + (totalH-1) + '" fill="none" stroke="#000" stroke-width="1"/>';
    
    // 竖线：序号列右边界、内容列右边界
    svg += '<line x1="' + seqW + '" y1="0" x2="' + seqW + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    svg += '<line x1="' + (seqW + contentW) + '" y1="0" x2="' + (seqW + contentW) + '" y2="' + totalH + '" stroke="#000" stroke-width="1"/>';
    
    // 绘制每个分类
    var dataRowIdx = 0;
    for (var g = 0; g < groupInfos.length; g++) {
      var gi = groupInfos[g];
      var gy = groupY[g];
      
      // 分类标题灰色背景
      svg += '<rect x="0" y="' + gy + '" width="' + totalW + '" height="' + titleH + '" fill="#e8e8e8"/>';
      // 分类标题底部线
      svg += '<line x1="0" y1="' + (gy + titleH) + '" x2="' + totalW + '" y2="' + (gy + titleH) + '" stroke="#000" stroke-width="1"/>';
      
      // 表头行浅灰背景
      var hy = gy + titleH;
      svg += '<rect x="0" y="' + hy + '" width="' + totalW + '" height="' + headerH + '" fill="#f5f5f5"/>';
      // 表头底部线
      svg += '<line x1="0" y1="' + (hy + headerH) + '" x2="' + totalW + '" y2="' + (hy + headerH) + '" stroke="#000" stroke-width="1"/>';
      
      // 数据行横线
      for (var r = 0; r < gi.count; r++) {
        var ry = rowY[dataRowIdx + r] + rowH;
        svg += '<line x1="0" y1="' + ry + '" x2="' + totalW + '" y2="' + ry + '" stroke="#000" stroke-width="1"/>';
      }
      
      dataRowIdx += gi.count;
    }
    
    svg += '</svg>';
    
    // 生成文字层（绝对定位div）
    var textLayer = '<div style="position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;">';
    
    // 分类标题文字
    for (var g = 0; g < groupInfos.length; g++) {
      var gi = groupInfos[g];
      var gy = groupY[g];
      textLayer += '<div style="position:absolute;top:' + gy + 'px;left:0;right:0;height:' + titleH + 'px;line-height:' + titleH + 'px;font-size:' + titleFontSize + 'px;font-weight:bold;padding:0 4px;box-sizing:border-box;overflow:hidden;white-space:nowrap;">';
      textLayer += escHtml(gi.label);
      textLayer += '</div>';
    }
    
    // 表头文字
    for (var g = 0; g < groupInfos.length; g++) {
      var gi = groupInfos[g];
      var hy = groupY[g] + titleH;
      var contentLabel = gi.special === 'tech' ? '型号编号' : '检查内容';
      
      textLayer += '<div style="position:absolute;top:' + hy + 'px;left:0;width:' + seqW + 'px;height:' + headerH + 'px;line-height:' + headerH + 'px;font-size:' + fontSize + 'px;font-weight:bold;text-align:center;">序</div>';
      textLayer += '<div style="position:absolute;top:' + hy + 'px;left:' + seqW + 'px;width:' + contentW + 'px;height:' + headerH + 'px;line-height:' + headerH + 'px;font-size:' + fontSize + 'px;font-weight:bold;text-align:center;">' + contentLabel + '</div>';
      textLayer += '<div style="position:absolute;top:' + hy + 'px;left:' + (seqW + contentW) + 'px;width:' + resultW + 'px;height:' + headerH + 'px;line-height:' + headerH + 'px;font-size:' + fontSize + 'px;font-weight:bold;text-align:center;">结论</div>';
    }
    
    // 数据行文字
    var seq = 0; // 全局连续序号
    dataRowIdx = 0;
    for (var g = 0; g < groupInfos.length; g++) {
      var gi = groupInfos[g];
      
      for (var r = 0; r < gi.count; r++) {
        var ry = rowY[dataRowIdx];
        var item = allItems[dataRowIdx];
        seq++;
        
        var it = itemMap[item.id];
        var name = it ? (it.name || it.modelNo || '') : '';
        var result = getResult(item.id);
        
        // 序号
        textLayer += '<div style="position:absolute;top:' + ry + 'px;left:0;width:' + seqW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;font-size:' + fontSize + 'px;text-align:center;">' + seq + '</div>';
        // 检查内容/型号编号
        textLayer += '<div style="position:absolute;top:' + ry + 'px;left:' + seqW + 'px;width:' + contentW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;font-size:' + fontSize + 'px;padding:0 2px;box-sizing:border-box;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">' + escHtml(name) + '</div>';
        // 结论
        textLayer += '<div style="position:absolute;top:' + ry + 'px;left:' + (seqW + contentW) + 'px;width:' + resultW + 'px;height:' + rowH + 'px;line-height:' + rowH + 'px;font-size:' + fontSize + 'px;text-align:center;">' + escHtml(result) + '</div>';
        
        dataRowIdx++;
      }
    }
    
    textLayer += '</div>';
    
    return '<div style="position:relative;width:100%;">' + svg + textLayer + '</div>';
  }

  // 页面配置
  var pageConfig;
  if (pageNum === 1) {
    pageConfig = {
      col1: [
        {label: '技术资料与铭牌（可识别标志）的一致性检查', ids: rangeIds(1,12), special: 'tech'},
        {label: '机器空间及通道', ids: rangeIds(13,21)},
        {label: '机房电气设备与标识', ids: rangeIds(22,36)}
      ],
      col2: [
        {label: '功能检查', ids: rangeIds(37,68)},
        {label: '安全开关', ids: rangeIds(69,74)}
      ],
      col3: [
        {label: '试验', ids: rangeIds(75,99)},
        {label: '驱动主机、承重及导向', ids: rangeIds(100,112)}
      ]
    };
  } else {
    pageConfig = {
      col1: [
        {label: '层门与轿门', ids: rangeIds(113,137)},
        {label: '导轨及固定支架', ids: rangeIds(138,142)},
        {label: '悬挂与补偿装置', ids: rangeIds(143,151)}
      ],
      col2: [
        {label: '轿顶设备', ids: rangeIds(152,166)},
        {label: '轿顶护栏', ids: rangeIds(167,171)},
        {label: '轿厢与对重', ids: rangeIds(172,179)},
        {label: '轿底部件', ids: rangeIds(180,190)}
      ],
      col3: [
        {label: '限速器与夹绳器', ids: rangeIds(191,199)},
        {label: '井道部件及空间', ids: rangeIds(200,211)},
        {label: '底坑设备', ids: rangeIds(212,219)},
        {label: '感官检查', ids: rangeIds(220,229)}
      ]
    };
  }

  // 计算每栏宽度
  var colWidth = 250; // 每栏宽度px
  
  // 构建页面
  var h = '';
  h += '<div style="font-family:Arial,sans-serif;font-size:9px;position:relative;padding:8px;box-sizing:border-box;width:100%;">';
  
  // 页眉
  h += '<div style="position:relative;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #000;overflow:hidden;">';
  h += '<div style="float:left;width:20%;"><img src="' + logoBase64 + '" style="height:22px;width:auto;"></div>';
  h += '<div style="float:left;width:60%;text-align:center;font-size:14px;font-weight:bold;line-height:22px;">厂检调试记录单</div>';
  h += '<div style="float:right;width:20%;text-align:right;font-size:9px;line-height:22px;">产品编号：' + escHtml(task.prodNo || task.productNo || '') + '</div>';
  h += '</div>';
  
  // 三栏布局 - float独立，高度自适
  h += '<div style="overflow:hidden;">';
  h += '<div style="float:left;width:33.33%;padding-right:4px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col1, colWidth) + '</div>';
  h += '<div style="float:left;width:33.33%;padding:0 2px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col2, colWidth) + '</div>';
  h += '<div style="float:left;width:33.34%;padding-left:4px;box-sizing:border-box;">' + buildColumnSvg(pageConfig.col3, colWidth) + '</div>';
  h += '</div>';
  
  // 结论说明
  h += '<div style="margin-top:6px;font-size:7px;color:#333;">结论选项中，符合打"√"，不符合打"×"，不适用打"/"，或写入测量值。</div>';
  
  // 页码
  h += '<div style="text-align:center;font-size:8px;margin-top:4px;">— ' + pageNum + ' —</div>';
  
  h += '</div>';
  
  return h;
}'''

# 替换原函数
new_content = content[:func_start] + new_func + content[func_end:]

with open('威特电梯厂检调试记录单v2.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'替换完成，新文件大小: {len(new_content)}')
print(f'原函数长度: {func_end - func_start}')
print(f'新函数长度: {len(new_func)}')
